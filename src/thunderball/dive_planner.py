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
    "plan_dive",
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
    """The planned dive: air budget, NDL, and the decompression schedule.

    Attributes:
        depth_m: Working depth (metres).
        bottom_minutes: Planned bottom time — the binding limit of air and NDL.
        air_volume_l: Free gas volume available in the cylinder (litres at
            surface pressure).
        sac_rate_lmin: Surface air consumption rate (L/min).
        ndl_minutes: No-decompression limit at ``depth_m``.
        deco_stops: Decompression schedule for the flown profile, deepest first.
        within_air: ``True`` when the gas budget was not the binding limit.
        within_ndl: ``True`` when decompression was not the binding limit.
    """

    depth_m: float
    bottom_minutes: float
    air_volume_l: float
    sac_rate_lmin: float
    ndl_minutes: float
    deco_stops: tuple[DecoStop, ...] = field(default_factory=tuple)
    within_air: bool = True
    within_ndl: bool = True

    def bottom_gas_required_l(self) -> float:
        """Gas consumed on the bottom (litres): ``SAC * P_amb(depth) * time``."""
        return self.sac_rate_lmin * ambient_pressure(self.depth_m) * self.bottom_minutes

    def total_gas_required_l(self) -> float:
        """Gas needed for the bottom phase plus every decompression stop (litres).

        Each stop is charged at its own ambient pressure — a 6 m hold costs
        roughly 1.6x the surface SAC volume, not 1x — so the total is a real
        gas budget rather than a surface-rate approximation.
        """
        deco = sum(
            self.sac_rate_lmin * ambient_pressure(stop.depth_m) * stop.minutes
            for stop in self.deco_stops
        )
        return self.bottom_gas_required_l() + deco

    def gas_margin_l(self) -> float:
        """Cylinder gas left over after the planned dive (negative if short)."""
        return self.air_volume_l - self.total_gas_required_l()

    def binding_constraint(self) -> str:
        """Which limit actually bounds the dive: ``air``, ``deco``, or ``none``.

        ``none`` means the planned bottom time was shorter than both limits —
        the diver surfaced on the plan, not on a constraint.
        """
        if not self.within_air:
            return "air"
        if not self.within_ndl:
            return "deco"
        air_minutes = bottom_time_from_air(
            self.air_volume_l, self.sac_rate_lmin, self.depth_m
        )
        if self.bottom_minutes >= min(air_minutes, self.ndl_minutes):
            return "air" if air_minutes <= self.ndl_minutes else "deco"
        return "none"


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
    """Bühlmann tolerated tissue tension (bar) at ambient pressure ``p_amb``.

    Bühlmann states the constraint as a tolerated *ambient* pressure,
    ``P_amb_tol = (P_tissue - a) * b``. Inverted for the tolerated tissue
    tension at a given ambient pressure, the M-value line is

    ``M(P) = P / b + a``

    with ``a`` the surfacing intercept and ``1/b`` the slope. This is *not*
    ``a*P + b``: transposing the two coefficients collapses the fast
    compartments' surfacing limits — compartment 1 tolerates 3.27 bar at the
    surface, not 1.78 bar — which in turn inflates every no-stop limit.

    Raises:
        ValueError: If ``b`` is not positive.
    """
    _require_positive(b, "b")
    return p_amb / b + a


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

    def tissue_pressures_after_profile(
        self,
        profile: list[tuple[float, float]],
        surface_pressure: float = STANDARD_SURFACE_PRESSURE,
    ) -> list[float]:
        """Inert-gas tissue pressures after a ``(depth_m, minutes)`` profile.

        Args:
            profile: Ordered ``(depth_m, minutes)`` holds as executed.
            surface_pressure: Ambient surface pressure (bar).

        Returns:
            One inert-gas pressure (bar) per compartment, in compartment order.
        """
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

        "No-decompression" means a *direct ascent to the surface* stays legal,
        so every compartment is tested against its M-value at the **surface**
        ambient pressure — the ceiling the diver must clear on the way up — not
        against the M-value at depth. Testing at depth is the classic error: at
        40 m the ambient pressure is five times the surface value, so every
        M-value is inflated with it and almost no bottom time is ever rejected.

        Returns ``0.0`` if the depth is already beyond its no-stop limit — a
        stop is obligatory on arrival, before any bottom time accrues. The
        stock ZH-L16A table never trips this at any depth (its lowest surfacing
        ceiling, 1.28 bar in compartment 16, still exceeds the 0.75 bar of a
        surface-saturated diver), so the guard exists for subclasses that
        override ``a_coeff``/``b_coeff`` with a stricter table.

        The limit is located by 60 rounds of bisection on bottom minutes over
        ``[0, 600]``, so the result is deterministic to well under a second.
        """
        _require_positive(depth_m, "depth_m")
        p_amb = ambient_pressure(depth_m, surface_pressure)
        # The ascent ceiling: what each compartment may hold on surfacing.
        mvalues = [
            buhlmann_mvalue(surface_pressure, a, b)
            for a, b in zip(self.a_coeff, self.b_coeff)
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
    # isfinite() rejects NaN (silent-propagating) and +/-inf (no finite
    # physical positive), so a bad argument cannot leak a degenerate result
    # downstream instead of failing loudly.
    if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{label} must be a positive finite number")


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
    tissues = model.tissue_pressures_after_profile(list(profile), surface_pressure)

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


def plan_dive(
    depth_m: float,
    cylinder_capacity_l: float,
    fill_pressure_bar: float,
    sac_rate_lmin: float,
    requested_bottom_minutes: float | None = None,
    reserve_fraction: float = 0.0,
    model: BuhlmannModel | None = None,
    surface_pressure: float = STANDARD_SURFACE_PRESSURE,
) -> DivePlan:
    """Assemble the full :class:`DivePlan` for a single-depth recovery dive.

    This is the single place the air budget and the ZH-L16A model are
    combined, so the mission adapter and the manuscript token generator cannot
    drift apart by re-deriving ambient pressure or the gas budget by hand.

    With no ``requested_bottom_minutes`` the planner flies the longest safe
    dive: ``min(air_limit, ndl)``. Both ``within_air`` and ``within_ndl`` are
    then necessarily ``True`` — use :meth:`DivePlan.binding_constraint` to see
    *which* limit bound. Passing an explicit request makes those flags
    load-bearing: a request longer than either limit clears the corresponding
    flag, and the decompression schedule is planned for the requested (unsafe)
    profile so the caller can see the obligation it incurs.

    Args:
        depth_m: Working depth (metres).
        cylinder_capacity_l: Cylinder water capacity (litres).
        fill_pressure_bar: Cylinder fill pressure (bar).
        sac_rate_lmin: Surface air consumption rate (L/min).
        requested_bottom_minutes: Bottom time the diver intends to fly. When
            ``None`` (default) the planner uses ``min(air_limit, ndl)``.
        reserve_fraction: Gas fraction held back as reserve, in ``[0, 1)``.
        model: Decompression model (default ZH-L16A).
        surface_pressure: Ambient surface pressure (bar).

    Returns:
        A :class:`DivePlan` for the flown profile, with the decompression
        schedule the profile actually requires.

    Raises:
        ValueError: If ``requested_bottom_minutes`` is negative, or any
            positive-only parameter is non-positive.
    """
    model = model or BuhlmannModel()
    gas_volume_l = cylinder_gas_volume(cylinder_capacity_l, fill_pressure_bar)
    air_minutes = bottom_time_from_air(
        gas_volume_l, sac_rate_lmin, depth_m, reserve_fraction=reserve_fraction
    )
    ndl = model.ndl_minutes(depth_m, surface_pressure=surface_pressure)
    if requested_bottom_minutes is None:
        bottom_minutes = min(air_minutes, ndl)
    elif requested_bottom_minutes < 0.0:
        raise ValueError("requested_bottom_minutes must be >= 0")
    else:
        bottom_minutes = requested_bottom_minutes
    stops = plan_decompression(
        [(depth_m, bottom_minutes)],
        surface_pressure=surface_pressure,
        model=model,
    )
    return DivePlan(
        depth_m=depth_m,
        bottom_minutes=bottom_minutes,
        air_volume_l=gas_volume_l,
        sac_rate_lmin=sac_rate_lmin,
        ndl_minutes=ndl,
        deco_stops=stops,
        within_air=bottom_minutes <= air_minutes,
        within_ndl=bottom_minutes <= ndl,
    )
