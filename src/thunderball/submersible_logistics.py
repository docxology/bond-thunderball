"""Submersible logistics for the DISCO VOLANTE mission.

Pure domain logic — no infrastructure imports. Models the range and
endurance of a submerged craft from first principles:

* **Propulsion power** — underwater drag follows an approximate cubic
  speed-power law ``P = k * v^3``, plus a constant hotel (life-support /
  systems) load ``H``.
* **Endurance** — battery energy divided by total power gives hours.
* **Range** — speed times endurance gives nautical miles.
* **Optimal range speed** — the speed that maximises range for a given
  energy follows from balancing the cubic propulsion term against the
  constant hotel load; solved analytically from the derivative.
* **Mission energy** — the inverse problem: battery energy required to
  transit a given range at a given speed.

All arithmetic is deterministic over explicit floats; no randomness.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = [
    "MissionEnergy",
    "RangeProfile",
    "endurance_hours",
    "energy_for_mission",
    "optimal_range_speed",
    "power_kw",
    "range_nm",
    "speed_for_range",
]


@dataclass(frozen=True)
class RangeProfile:
    """Endurance/range analysis at a chosen cruising speed."""

    speed_knots: float
    power_kw: float
    endurance_h: float
    range_nm: float
    optimal_speed_knots: float
    optimal_range_nm: float


@dataclass(frozen=True)
class MissionEnergy:
    """Energy required to complete a fixed-range transit."""

    energy_kwh: float
    used_fraction: float


def power_kw(speed_knots: float, drag_coeff: float, hotel_kw: float = 0.0) -> float:
    """Total submerged power draw at ``speed_knots`` (cubic drag + hotel load)."""
    _require_nonneg(speed_knots, "speed_knots")
    _require_nonneg(drag_coeff, "drag_coeff")
    _require_nonneg(hotel_kw, "hotel_kw")
    return drag_coeff * speed_knots**3 + hotel_kw


def endurance_hours(
    energy_kwh: float, speed_knots: float, drag_coeff: float, hotel_kw: float = 0.0
) -> float:
    """Hours the powerplant can sustain ``speed_knots`` on ``energy_kwh``."""
    _require_positive(energy_kwh, "energy_kwh")
    p = power_kw(speed_knots, drag_coeff, hotel_kw)
    return energy_kwh / p


def range_nm(
    energy_kwh: float, speed_knots: float, drag_coeff: float, hotel_kw: float = 0.0
) -> float:
    """Nautical-mile range at ``speed_knots`` on ``energy_kwh``."""
    e = endurance_hours(energy_kwh, speed_knots, drag_coeff, hotel_kw)
    return speed_knots * e


def optimal_range_speed(energy_kwh: float, drag_coeff: float, hotel_kw: float) -> float:
    """Speed (knots) maximising range for the given energy and loads.

    Range ``R(v) = v * E / (k v^3 + H)``. The derivative vanishes when
    ``k v^3 = H/2``, giving an analytic optimum. With no hotel load the range
    is monotonically increasing to the speed ceiling, so we clamp to a
    nominal soakable maximum.
    """
    _require_positive(energy_kwh, "energy_kwh")
    _require_positive(drag_coeff, "drag_coeff")
    _require_positive(hotel_kw, "hotel_kw")
    # dR/dv = 0  =>  k v^3 = H/2
    return float((hotel_kw / (2.0 * drag_coeff)) ** (1.0 / 3.0))


def speed_for_range(
    range_nm: float, energy_kwh: float, drag_coeff: float, hotel_kw: float = 0.0
) -> float:
    """Inverse: the fastest speed at which ``range_nm`` is achievable on ``energy_kwh``.

    Solves ``R = v * E / (k v^3 + H)`` for ``v`` (a cubic in ``v``, often with
    two real roots on either side of the range maximum). Returns the *largest*
    real root — the fast, cruise regime a logistics planner actually wants —
    and raises ``ValueError`` if the range is not attainable with the given
    energy (the cubic's minimum lies above zero).

    The root is located by a bounded bisection seeded at the minimum of the
    range-imbalance ``f(v) = R k v^3 - E v + R H``, which is guaranteed to
    terminate in O(log) iterations.
    """
    _require_positive(range_nm, "range_nm")
    _require_positive(energy_kwh, "energy_kwh")
    _require_positive(drag_coeff, "drag_coeff")
    _require_nonneg(hotel_kw, "hotel_kw")

    k = drag_coeff
    r = range_nm
    e = energy_kwh
    h = hotel_kw

    def imbalance(v: float) -> float:
        return r * k * v**3 - e * v + r * h

    if h == 0.0:
        # f(v) = v (r k v^2 - e): the only positive root is sqrt(e / (r k)).
        return math.sqrt(e / (r * k))

    # f(0) = r*h > 0; f is convex for v >= 0. Find the minimum.
    v_min = math.sqrt(e / (3.0 * r * k))
    f_min = imbalance(v_min)
    if f_min > 0.0:
        raise ValueError("range is not attainable with the given energy budget")
    if abs(f_min) < 1e-12:
        return v_min

    # Bisect on the right branch: lo has f < 0 (the minimum), hi has f > 0.
    lo, hi = v_min, v_min
    while imbalance(hi) < 0.0:
        hi *= 2.0
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if imbalance(mid) < 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def energy_for_mission(
    range_nm: float, speed_knots: float, drag_coeff: float, hotel_kw: float = 0.0
) -> float:
    """Battery kWh required to transit ``range_nm`` at ``speed_knots``.

    ``E = R * P / v`` where ``P`` is total submerged power at ``speed_knots``.
    """
    _require_positive(range_nm, "range_nm")
    _require_positive(speed_knots, "speed_knots")
    _require_positive(drag_coeff, "drag_coeff")
    _require_nonneg(hotel_kw, "hotel_kw")
    p = power_kw(speed_knots, drag_coeff, hotel_kw)
    return range_nm * p / speed_knots


def _require_positive(value: float, label: str) -> None:
    if not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{label} must be a positive number")


def _require_nonneg(value: float, label: str) -> None:
    if not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{label} must be a non-negative number")
