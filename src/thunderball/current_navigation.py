"""Set-and-drift underwater navigation for the DISCO VOLANTE assault divers.

Pure domain logic — no infrastructure imports. Implements deterministic
dead-reckoning navigation in a moving (current-carrying) water column:

* **Drift vector** — current expressed as an east/north velocity (knots)
  from a set (direction the current flows *toward*, degrees true) and drift
  rate.
* **Ground velocity / dead reckoning** — own speed and heading vector-added
  to the current; integrated over time to a position (nautical miles).
* **Course to steer** — the heading that makes good a desired track despite
  set and drift (the classical vector-triangle solution; raises when the
  current's cross-track component exceeds own speed).
* **Cross-track error** — signed perpendicular distance off the intended
  track line.
* **Drift over a dive** — how far a diver is swept during the planned bottom
  time, and whether it exceeds a recovery radius.

All headings are degrees true, angles measured clockwise from north.
All arithmetic is deterministic; no randomness.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = [
    "NavAssessment",
    "course_to_steer",
    "cross_track_error",
    "dead_reckon",
    "drift_distance",
    "drift_exceeds_limit",
    "drift_vector",
    "ground_speed",
    "ground_velocity",
]

#: East/north coordinate tuple (nautical miles, or knots for velocities).
Position = tuple[float, float]


@dataclass(frozen=True)
class NavAssessment:
    """Dead-reckoned navigation assessment for a dive."""

    end_east_nm: float
    end_north_nm: float
    drift_nm: float
    drift_exceeds_recovery: bool
    heading_to_steer_deg: float
    ground_speed_knots: float


def drift_vector(set_deg: float, drift_knots: float) -> tuple[float, float]:
    """Current velocity ``(east_kn, north_kn)`` from set (deg) and drift (kn).

    ``set`` is the direction the current flows toward; components follow the
    usual north-up navigation convention ``(sin, cos)``.
    """
    _require_nonneg(drift_knots, "drift_knots")
    rad = math.radians(set_deg % 360.0)
    return (drift_knots * math.sin(rad), drift_knots * math.cos(rad))


def ground_velocity(
    heading_deg: float,
    speed_knots: float,
    set_deg: float,
    drift_knots: float,
) -> tuple[float, float]:
    """Ground velocity (east, north) knots: own motion plus the current."""
    _require_positive(speed_knots, "speed_knots")
    rad = math.radians(heading_deg % 360.0)
    own_e = speed_knots * math.sin(rad)
    own_n = speed_knots * math.cos(rad)
    cur_e, cur_n = drift_vector(set_deg, drift_knots)
    return (own_e + cur_e, own_n + cur_n)


def dead_reckon(
    start_east_nm: float,
    start_north_nm: float,
    heading_deg: float,
    speed_knots: float,
    duration_h: float,
    set_deg: float,
    drift_knots: float,
) -> tuple[float, float]:
    """Dead-reckoned position after ``duration_h`` under set and drift."""
    _require_nonneg(duration_h, "duration_h")
    ve, vn = ground_velocity(heading_deg, speed_knots, set_deg, drift_knots)
    return (start_east_nm + ve * duration_h, start_north_nm + vn * duration_h)


def course_to_steer(
    desired_track_deg: float,
    speed_knots: float,
    set_deg: float,
    drift_knots: float,
) -> float:
    """Heading (deg) that makes good ``desired_track_deg`` under set and drift.

    The current's component perpendicular to the desired track must be
    cancelled by a component of own velocity: ``v·sin(theta) = -c_perp`` with
    ``theta = asin(-c_perp / v)``.

    Raises:
        ValueError: If the current's cross-track component exceeds own speed
            (the track is not achievable).
    """
    _require_positive(speed_knots, "speed_knots")
    rad = math.radians(desired_track_deg % 360.0)
    # Left-perpendicular of the track unit vector; the current's component
    # along it must be cancelled by own velocity.
    p_e, p_n = math.cos(rad), -math.sin(rad)
    cur_e, cur_n = drift_vector(set_deg, drift_knots)
    c_perp = cur_e * p_e + cur_n * p_n
    ratio = -c_perp / speed_knots
    if abs(ratio) > 1.0:
        raise ValueError(
            "current cross-track component exceeds own speed; track not achievable"
        )
    theta_deg = math.degrees(math.asin(ratio))
    return float((desired_track_deg + theta_deg) % 360.0)


def ground_speed(
    desired_track_deg: float,
    speed_knots: float,
    set_deg: float,
    drift_knots: float,
) -> float:
    """Speed made good along the desired track after course-to-steer (knots)."""
    rad = math.radians(desired_track_deg % 360.0)
    u_e, u_n = math.sin(rad), math.cos(rad)
    heading = course_to_steer(desired_track_deg, speed_knots, set_deg, drift_knots)
    heading_rad = math.radians(heading % 360.0)
    theta = heading_rad - rad
    along_own = speed_knots * math.cos(theta)
    cur_e, cur_n = drift_vector(set_deg, drift_knots)
    along_current = cur_e * u_e + cur_n * u_n
    return float(along_own + along_current)


def cross_track_error(
    position_east_nm: float,
    position_north_nm: float,
    start_east_nm: float,
    start_north_nm: float,
    track_deg: float,
) -> float:
    """Signed perpendicular distance (nm) of the position off the track line.

    Positive when the position lies to the left of the track direction.
    """
    rad = math.radians(track_deg % 360.0)
    # Left-hand perpendicular of the track unit vector.
    p_e, p_n = -math.cos(rad), math.sin(rad)
    d_e = position_east_nm - start_east_nm
    d_n = position_north_nm - start_north_nm
    return float(d_e * p_e + d_n * p_n)


def drift_distance(drift_knots: float, duration_h: float) -> float:
    """Distance (nm) the current sweeps a stationary diver in ``duration_h``."""
    _require_nonneg(drift_knots, "drift_knots")
    _require_nonneg(duration_h, "duration_h")
    return float(drift_knots * duration_h)


def drift_exceeds_limit(limit_nm: float, drift_knots: float, duration_h: float) -> bool:
    """True when the current drift over ``duration_h`` exceeds ``limit_nm``."""
    _require_nonneg(limit_nm, "limit_nm")
    return drift_distance(drift_knots, duration_h) > limit_nm


def assess_navigation(
    desired_track_deg: float,
    speed_knots: float,
    set_deg: float,
    drift_knots: float,
    duration_h: float,
    recovery_radius_nm: float,
    start_east_nm: float = 0.0,
    start_north_nm: float = 0.0,
) -> NavAssessment:
    """Full navigation assessment: DR position, drift, and steer solution."""
    _require_positive(speed_knots, "speed_knots")
    _require_positive(recovery_radius_nm, "recovery_radius_nm")
    end_e, end_n = dead_reckon(
        start_east_nm,
        start_north_nm,
        desired_track_deg,
        speed_knots,
        duration_h,
        set_deg,
        drift_knots,
    )
    swept = drift_distance(drift_knots, duration_h)
    heading = course_to_steer(desired_track_deg, speed_knots, set_deg, drift_knots)
    gs = ground_speed(desired_track_deg, speed_knots, set_deg, drift_knots)
    return NavAssessment(
        end_east_nm=end_e,
        end_north_nm=end_n,
        drift_nm=swept,
        drift_exceeds_recovery=drift_exceeds_limit(
            recovery_radius_nm, drift_knots, duration_h
        ),
        heading_to_steer_deg=heading,
        ground_speed_knots=gs,
    )


def _require_positive(value: float, label: str) -> None:
    if not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{label} must be a positive number")


def _require_nonneg(value: float, label: str) -> None:
    if not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{label} must be a non-negative number")
