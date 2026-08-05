"""Convoy interdiction analysis for the DISCO VOLANTE NATO recovery.

Pure domain logic — no infrastructure imports. Adds the dynamic layer over
the static escort-screen assessment (``convoy_integrity``): given a threat
track and the convoy's own course, it computes

* **Closest point of approach (CPA)** — relative-motion geometry between the
  threat and the convoy: time-to-CPA, CPA distance, closing speed, and the
  relative-speed magnitude the range profile is swept at.
* **Screen penetration time** — how long an interceptor takes to cross the
  straight-line chord subtended by the widest *spacing* between adjacent
  escorts (``convoy_integrity.largest_gap``), at the screen radius.
* **Time to minimum separation** — when the threat's range first falls to the
  minimum-separation limit, from the constant-velocity range profile
  ``range(t)² = d_cpa² + v_rel² (t - t_cpa)²``. Infinite when the CPA never
  comes inside the limit.
* **Interdiction status** — a deterministic rule combining that time, escort
  reaction time, and penetration time: ``breached`` (the threat reaches
  minimum separation before escorts react), ``penetrated`` (the gap chord is
  crossed before escorts react), or ``held``.

All arithmetic is deterministic math over explicit floats; no randomness.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = [
    "CPAResult",
    "InterdictionAssessment",
    "closest_point_of_approach",
    "interdiction_status",
    "screen_penetration_time",
    "time_to_minimum_separation",
]

#: Relative-motion geometry below which tracks are considered stationary.
_EPS_REL_VEL = 1e-12


@dataclass(frozen=True)
class CPAResult:
    """Closest-point-of-approach geometry between two tracks."""

    t_cpa_h: float
    d_cpa_nm: float
    #: Radial rate at which the separation is shrinking *now* (negative when
    #: the tracks are diverging).
    closing_knots: float
    #: Magnitude of the relative-velocity vector — constant over the track, and
    #: the speed at which the range profile sweeps through its hyperbola.
    relative_speed_knots: float


@dataclass(frozen=True)
class InterdictionAssessment:
    """A combined threat assessment: CPA geometry plus the screen verdict."""

    d_cpa_nm: float
    t_cpa_h: float
    closing_knots: float
    penetration_time_h: float
    time_to_min_sep_h: float
    status: str


def _velocity(course_deg: float, speed_knots: float) -> tuple[float, float]:
    rad = math.radians(course_deg % 360.0)
    return (speed_knots * math.sin(rad), speed_knots * math.cos(rad))


def closest_point_of_approach(
    own_position: tuple[float, float],
    own_course_deg: float,
    own_speed_knots: float,
    threat_position: tuple[float, float],
    threat_course_deg: float,
    threat_speed_knots: float,
) -> CPAResult:
    """CPA geometry between ``threat`` and ``own`` in relative motion.

    ``t_cpa`` is clamped to the future (``>= 0``); when relative motion is
    (near-)zero the CPA distance is the initial separation with ``t=0``.
    ``closing_knots`` is the rate at which the separation decreases (negative
    when the tracks are diverging).
    """
    _require_positive(own_speed_knots, "own_speed_knots")
    _require_positive(threat_speed_knots, "threat_speed_knots")
    own_v = _velocity(own_course_deg, own_speed_knots)
    threat_v = _velocity(threat_course_deg, threat_speed_knots)
    rel_pos = (
        threat_position[0] - own_position[0],
        threat_position[1] - own_position[1],
    )
    rel_vel = (threat_v[0] - own_v[0], threat_v[1] - own_v[1])
    sep2 = rel_vel[0] * rel_vel[0] + rel_vel[1] * rel_vel[1]
    initial_sep = math.hypot(rel_pos[0], rel_pos[1])
    if sep2 < _EPS_REL_VEL:
        return CPAResult(
            t_cpa_h=0.0,
            d_cpa_nm=initial_sep,
            closing_knots=0.0,
            relative_speed_knots=0.0,
        )
    dot = rel_pos[0] * rel_vel[0] + rel_pos[1] * rel_vel[1]
    t_cpa = max(0.0, -dot / sep2)
    cpa_e = rel_pos[0] + t_cpa * rel_vel[0]
    cpa_n = rel_pos[1] + t_cpa * rel_vel[1]
    d_cpa = math.hypot(cpa_e, cpa_n)
    closing = -dot / initial_sep if initial_sep > 0.0 else 0.0
    return CPAResult(
        t_cpa_h=t_cpa,
        d_cpa_nm=d_cpa,
        closing_knots=closing,
        relative_speed_knots=math.sqrt(sep2),
    )


def screen_penetration_time(
    gap_deg: float, screen_radius_nm: float, speed_knots: float
) -> float:
    """Hours for an interceptor at ``speed_knots`` to cross the gap's chord.

    ``gap_deg`` is an angular sector of a screen at ``screen_radius_nm``, whose
    straight-line chord is ``2 r sin(gap/2)``. Callers pass the widest escort
    *spacing* (``convoy_integrity.largest_gap``), so this is the transit across
    the sector between two adjacent escorts — not across an unwatched arc.
    """
    _require_positive(gap_deg, "gap_deg")
    _require_positive(screen_radius_nm, "screen_radius_nm")
    _require_positive(speed_knots, "speed_knots")
    chord = 2.0 * screen_radius_nm * math.sin(math.radians(gap_deg) / 2.0)
    return float(chord / speed_knots)


def time_to_minimum_separation(
    d_cpa_nm: float,
    t_cpa_h: float,
    relative_speed_knots: float,
    min_separation_nm: float,
) -> float:
    """Hours until the threat's range *first* falls to ``min_separation_nm``.

    Under constant relative velocity the range profile is the hyperbola
    ``range(t)² = d_cpa² + v_rel² (t - t_cpa)²``, so the range reaches ``R`` at
    ``t = t_cpa ± sqrt(R² - d_cpa²) / v_rel`` and the first (earlier) root is
    the answer.

    Returns ``inf`` when ``d_cpa_nm >= min_separation_nm``: the whole point of
    the CPA is that it is the smallest range the threat ever achieves, so a CPA
    outside the limit means the limit is never reached. Returns ``0.0`` when
    the threat is inside the limit already (the earlier root is in the past).
    """
    _require_nonneg(d_cpa_nm, "d_cpa_nm")
    _require_nonneg(t_cpa_h, "t_cpa_h")
    _require_nonneg(relative_speed_knots, "relative_speed_knots")
    _require_positive(min_separation_nm, "min_separation_nm")
    if d_cpa_nm >= min_separation_nm:
        return math.inf
    if relative_speed_knots <= 0.0:
        # Zero relative motion with a CPA inside the limit: already there.
        return 0.0
    half_chord_h = (
        math.sqrt(min_separation_nm * min_separation_nm - d_cpa_nm * d_cpa_nm)
        / relative_speed_knots
    )
    return max(0.0, t_cpa_h - half_chord_h)


def interdiction_status(
    time_to_min_sep_h: float,
    penetration_time_h: float,
    reaction_time_h: float,
    closing_knots: float,
) -> str:
    """Deterministic convoy-screen verdict, as a race against escort reaction.

    The verdict is a function of three times, not of the CPA distance directly:
    ``time_to_min_sep_h`` (from :func:`time_to_minimum_separation`, ``inf``
    when the threat never comes inside the limit), ``penetration_time_h``, and
    the escorts' ``reaction_time_h``. Rules, in order:

    * ``breached`` — the threat reaches minimum separation before escorts
      react. A CPA outside the limit gives ``inf`` here, which never wins this
      comparison, so no distant track can be scored as a breach.
    * ``held`` — a diverging threat (``closing_knots <= 0``); the screen is not
      under pressure.
    * ``penetrated`` — the gap chord is crossed before escorts can respond.
    * ``held`` — otherwise: escorts get there first.

    Returns one of ``"held"``, ``"penetrated"``, ``"breached"``.
    """
    _require_nonneg(time_to_min_sep_h, "time_to_min_sep_h")
    _require_nonneg(reaction_time_h, "reaction_time_h")
    _require_positive(penetration_time_h, "penetration_time_h")
    if time_to_min_sep_h < reaction_time_h:
        return "breached"
    if closing_knots <= 0.0:
        # Diverging threat: the screen is not threatened.
        return "held"
    if penetration_time_h < reaction_time_h:
        return "penetrated"
    return "held"


def assess_interdiction(
    own_position: tuple[float, float],
    own_course_deg: float,
    own_speed_knots: float,
    threat_position: tuple[float, float],
    threat_course_deg: float,
    threat_speed_knots: float,
    gap_deg: float,
    screen_radius_nm: float,
    min_separation_nm: float,
    reaction_time_h: float,
) -> InterdictionAssessment:
    """Full interdiction assessment: CPA geometry plus the screen verdict."""
    cpa = closest_point_of_approach(
        own_position,
        own_course_deg,
        own_speed_knots,
        threat_position,
        threat_course_deg,
        threat_speed_knots,
    )
    penetration = screen_penetration_time(gap_deg, screen_radius_nm, threat_speed_knots)
    to_min_sep = time_to_minimum_separation(
        cpa.d_cpa_nm,
        cpa.t_cpa_h,
        cpa.relative_speed_knots,
        min_separation_nm,
    )
    status = interdiction_status(
        to_min_sep,
        penetration,
        reaction_time_h,
        cpa.closing_knots,
    )
    return InterdictionAssessment(
        d_cpa_nm=cpa.d_cpa_nm,
        t_cpa_h=cpa.t_cpa_h,
        closing_knots=cpa.closing_knots,
        penetration_time_h=penetration,
        time_to_min_sep_h=to_min_sep,
        status=status,
    )


def _require_positive(value: float, label: str) -> None:
    if not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{label} must be a positive number")


def _require_nonneg(value: float, label: str) -> None:
    if not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{label} must be a non-negative number")
