"""Dive planning for the DISCO VOLANTE underwater assault.

Pure domain logic — no infrastructure imports. Implements:

* **Air budget** — compute cylinder gas volume, breathing demand at depth,
  and bottom-time limits from surface-air-consumption (SAC) rate.
* **Ambient pressure physics** — saltwater hydrostatic pressure and alveolar
  inert-gas partial pressure.
* **Bühlmann ZH-L16A decompression model** — a real 16-compartment tissue
  model: inert-gas loading over an arbitrary depth profile, no-decompression
  limits (NDL) at a target depth, and a deterministic decompression schedule
  from ascent stops.

Everything is deterministic math over explicit floats; there is no
randomness and no wall-clock dependence.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

__all__ = [
    "BuhlmannModel",
    "DecoStop",
    "DivePlan",
    "alveolar_pressure",
    "ambient_pressure",
    "bottom_time_from_air",
    "buhlmann_mvalue",
    "compute_ndl",
    "cylinder_gas_volume",
    "plan_decompression",
    "tissue_pressure_after",
]

#: Saltwater hydrostatic pressure gain in bar per metre of depth.
BAR_PER_METRE = 0.1
#: Standard surface atmospheric pressure (bar).
STANDARD_SURFACE_PRESSURE = 1.013
#: Alveolar water-vapour partial pressure (bar), conventionally 0.0627.
WATER_VAPOUR = 0.0627
#: Fraction of nitrogen in air.
F_N2 = 0.79
#: Natural log of 2, used in half-time kinetics.
_LN2 = math.log(2.0)


@dataclass(frozen=True)
class DecoStop:
    """A single decompression stop: hold at ``depth_m`` for ``minutes``."""

    depth_m: float
    minutes: float


@dataclass(frozen=True)
class DivePlan:
    """The planned dive: air budget, NDL, and the decompression schedule."""

    depth_m: float
    bottom_minutes: float
    air_volume_l: float
    sac_rate_lmin: float
    ndl_minutes: float
    deco_stops: tuple[DecoStop, ...] = field(default_factory=tuple)
    within_air: bool = True
    within_ndl: bool = True

    def total_gas_required_l(self) -> float:
        """Cylinder gas needed for descent, bottom, and any deco stops (SAC basis)."""
        total = self.air_volume_l + sum(
            stop.minutes * self.sac_rate_lmin for stop in self.deco_stops
        )
        return total


def ambient_pressure(
    depth_m: float, surface_pressure: float = STANDARD_SURFACE_PRESSURE
) -> float:
    """Absolute ambient pressure (bar) at ``depth_m`` below the surface."""
    return surface_pressure + BAR_PER_METRE * depth_m


def alveolar_pressure(
    p_amb: float, f_n2: float = F_N2, water_vapour: float = WATER_VAPOUR
) -> float:
    """Alveolar inert-gas partial pressure given an ambient pressure (bar)."""
    return f_n2 * (p_amb - water_vapour)


def cylinder_gas_volume(capacity_l: float, fill_pressure_bar: float) -> float:
    """Free gas volume (litres at surface) in a cylinder.

    Args:
        capacity_l: Cylinder water capacity in litres.
        fill_pressure_bar: Fill pressure in bar.

    Returns:
        Available gas volume in litres at surface pressure.
    """
    _require_positive(capacity_l, "capacity_l")
    _require_positive(fill_pressure_bar, "fill_pressure_bar")
    return capacity_l * fill_pressure_bar


def bottom_time_from_air(
    gas_volume_l: float,
    sac_rate_lmin: float,
    depth_m: float,
    reserve_fraction: float = 0.0,
) -> float:
    """Bottom minutes a diver can stay at ``depth_m`` from ``gas_volume_l``.

    Breathing demand scales with ambient pressure: at depth the SAC volume
    per minute is ``sac * P_amb``. ``reserve_fraction`` (0..1) is held back
    as a safety reserve and not counted toward usable bottom time.
    """
    _require_positive(gas_volume_l, "gas_volume_l")
    _require_positive(sac_rate_lmin, "sac_rate_lmin")
    _require_positive(depth_m, "depth_m")
    if not 0.0 <= reserve_fraction < 1.0:
        raise ValueError("reserve_fraction must be in [0, 1)")
    p_amb = ambient_pressure(depth_m)
    usable = gas_volume_l * (1.0 - reserve_fraction)
    return usable / (sac_rate_lmin * p_amb)


def buhlmann_mvalue(p_amb: float, a: float, b: float) -> float:
    """Bühlmann tolerated tissue pressure for ambient pressure ``p_amb``.

    The M-value line: max tolerated inert-gas tissue tension ``M = a*P + b``.
    """
    return a * p_amb + b


def tissue_pressure_after(
    p_initial: float,
    p_alv: float,
    half_time_min: float,
    minutes: float,
) -> float:
    """Tissue inert-gas pressure after ``minutes`` at alveolar pressure ``p_alv``."""
    _require_positive(half_time_min, "half_time_min")
    if minutes < 0.0:
        raise ValueError("minutes must be >= 0")
    return p_alv + (p_initial - p_alv) * math.exp(-_LN2 * minutes / half_time_min)


class BuhlmannModel:
    """Bühlmann ZH-L16A decompression model over 16 tissue compartments.

    Each compartment ``i`` has a nitrogen half-time ``half_time[i]`` and
    M-value coefficients ``a[i]``, ``b[i]``. The model tracks the inert-gas
    tissue pressure and, on ascent, requires that no tissue exceed its
    M-value at any ambient pressure — that is what produces deco stops.
    """

    #: ZH-L16A nitrogen half-times (minutes), compartments 1..16.
    half_time: tuple[float, ...] = (
        4.0,
        8.0,
        12.5,
        18.5,
        27.0,
        38.3,
        54.3,
        77.0,
        109.0,
        146.0,
        187.0,
        239.0,
        305.0,
        390.0,
        498.0,
        635.0,
    )
    #: ZH-L16A ``a`` coefficients.
    a_coeff: tuple[float, ...] = (
        1.2599,
        1.0000,
        0.8618,
        0.7562,
        0.6667,
        0.5933,
        0.5282,
        0.4701,
        0.4187,
        0.3798,
        0.3497,
        0.3223,
        0.2971,
        0.2737,
        0.2523,
        0.2327,
    )
    #: ZH-L16A ``b`` coefficients.
    b_coeff: tuple[float, ...] = (
        0.5050,
        0.6514,
        0.7222,
        0.7825,
        0.8126,
        0.8434,
        0.8693,
        0.8910,
        0.9092,
        0.9222,
        0.9319,
        0.9403,
        0.9477,
        0.9544,
        0.9602,
        0.9653,
    )

    def __init__(self, f_n2: float = F_N2, water_vapour: float = WATER_VAPOUR) -> None:
        self.f_n2 = f_n2
        self.water_vapour = water_vapour

    def initial_tissue_pressure(
        self, surface_pressure: float = STANDARD_SURFACE_PRESSURE
    ) -> float:
        """Inert-gas tissue pressure of a fully saturated diver at the surface."""
        return alveolar_pressure(surface_pressure, self.f_n2, self.water_vapour)

    def _tone_after_dive(
        self, profile: list[tuple[float, float]], surface_pressure: float
    ) -> list[float]:
        """Simulate inert-gas loading across a ``(depth_m, minutes)`` profile."""
        tissues = [self.initial_tissue_pressure(surface_pressure)] * len(self.half_time)
        for depth_m, minutes in profile:
            p_amb = ambient_pressure(depth_m, surface_pressure)
            p_alv = alveolar_pressure(p_amb, self.f_n2, self.water_vapour)
            tissues = [
                tissue_pressure_after(t, p_alv, ht, minutes)
                for t, ht in zip(tissues, self.half_time)
            ]
        return tissues

    def ndl_minutes(
        self, depth_m: float, surface_pressure: float = STANDARD_SURFACE_PRESSURE
    ) -> float:
        """No-decompression limit: max bottom time at ``depth_m`` with no deco stop.

        Returns ``0.0`` if the depth is already beyond its no-stop limit
        (a stop is required immediately). Binary search on bottom minutes.
        """
        _require_positive(depth_m, "depth_m")
        p_amb = ambient_pressure(depth_m, surface_pressure)
        mvalues = [
            buhlmann_mvalue(p_amb, a, b) for a, b in zip(self.a_coeff, self.b_coeff)
        ]
        initial = self.initial_tissue_pressure(surface_pressure)
        p_alv = alveolar_pressure(p_amb, self.f_n2, self.water_vapour)

        def in_limit(minutes: float) -> bool:
            for t0, ht, mvalue in zip(
                [initial] * len(self.half_time), self.half_time, mvalues
            ):
                if tissue_pressure_after(t0, p_alv, ht, minutes) > mvalue:
                    return False
            return True

        if not in_limit(0.0):
            return 0.0
        lo, hi = 0.0, 600.0
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if in_limit(mid):
                lo = mid
            else:
                hi = mid
        return lo


def _require_positive(value: float, label: str) -> None:
    if not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{label} must be a positive number")


def compute_ndl(
    depth_m: float,
    model: BuhlmannModel | None = None,
    surface_pressure: float = STANDARD_SURFACE_PRESSURE,
) -> float:
    """Compute the NDL at ``depth_m`` using ``model`` (default ZH-L16A)."""
    model = model or BuhlmannModel()
    return model.ndl_minutes(depth_m, surface_pressure=surface_pressure)


def plan_decompression(
    profile: list[tuple[float, float]],
    ascent_rate_m_min: float = 9.0,
    stop_interval_m: float = 3.0,
    surface_pressure: float = STANDARD_SURFACE_PRESSURE,
    model: BuhlmannModel | None = None,
    max_stop_min: float = 600.0,
) -> tuple[DecoStop, ...]:
    """Deterministic decompression schedule for a dive ``profile``.

    Args:
        profile: ``(depth_m, minutes)`` holds as executed (descent then bottom).
        ascent_rate_m_min: Vertical ascent speed (m/min). ``0`` disables the
            ascent-time contribution (instant ascent).
        stop_interval_m: Depth spacing between candidate stops (standard 3 m).
        surface_pressure: Ambient surface pressure (bar).
        model: Decompression model (default ZH-L16A).
        max_stop_min: Capped hold per stop (minutes). Bounds the off-gas loop
            so that a degenerate stop depth whose alveolar target lies above
            its M-value cannot loop forever — the model simply ascends past it.

    Returns:
        Tuple of :class:`DecoStop` holds, deepest first, to keep every tissue
        within its M-value on ascent. Empty if the dive is no-stop.
    """
    model = model or BuhlmannModel()
    # Tissues loaded at the deepest/bottom of the profile.
    max_depth = max(d for d, _ in profile)
    tissues = model._tone_after_dive(list(profile), surface_pressure)

    stops: list[DecoStop] = []
    current_depth = max_depth
    while current_depth > 0.0:
        next_depth = max(0.0, current_depth - stop_interval_m)
        # Ascent to the next stop at the configured rate (time-dependent loading).
        if ascent_rate_m_min > 0.0:
            dt = (current_depth - next_depth) / ascent_rate_m_min
            p_alv_here = alveolar_pressure(
                ambient_pressure(current_depth, surface_pressure),
                model.f_n2,
                model.water_vapour,
            )
            tissues = [
                tissue_pressure_after(t, p_alv_here, ht, dt)
                for t, ht in zip(tissues, model.half_time)
            ]

        # Hold at `next_depth` until the controlling tissue meets its M-value.
        # The loop is bounded by ``max_stop_min``: if a stop depth cannot clear
        # the tissue (M-value below the off-gas target), we ascend past it rather
        # than hang, keeping the planner total and deterministic.
        hold = 0.0
        p_amb = ambient_pressure(next_depth, surface_pressure)
        p_alv = alveolar_pressure(p_amb, model.f_n2, model.water_vapour)
        while hold < max_stop_min and next_depth > 0.0:
            mvalues = [
                buhlmann_mvalue(p_amb, a, b)
                for a, b in zip(model.a_coeff, model.b_coeff)
            ]
            over = max((t - m for t, m in zip(tissues, mvalues) if t > m), default=0.0)
            if over <= 0.0:
                break
            tissues = [
                tissue_pressure_after(t, p_alv, ht, 1.0)
                for t, ht in zip(tissues, model.half_time)
            ]
            hold += 1.0
        if hold > 0.0 and next_depth > 0.0:
            stops.append(DecoStop(depth_m=round(next_depth, 1), minutes=hold))
        current_depth = next_depth

    return tuple(stops)
