"""Thunderball — DISCO VOLANTE MissionProvider (BOND-API protocol adapter).

This module is the thin adapter between the frozen
:class:`bond_api.protocol.MissionProvider` contract and the pure domain core
in :mod:`thunderball.dive_planner`, :mod:`thunderball.convoy_integrity`, and
:mod:`thunderball.submersible_logistics`.

It is deliberately a *thin* adapter: no business logic lives here. Each
lifecycle stage delegates to the domain modules and wraps their outputs in
the frozen BOND-API dataclasses. The domain core imports nothing from
``bond_api``; only this adapter (and the package facade) does, so the core
remains usable in isolation if the path dependency is ever unavailable.
"""

from __future__ import annotations

from bond_api.protocol import (
    Asset,
    Constraint,
    Debrief,
    Finding,
    MissionBrief,
    MissionOutcome,
    MissionPlan,
    Provenance,
    ReconReport,
    ReconRequest,
    Step,
)
from bond_api.registry import GadgetRegistry

from . import __version__ as _PACKAGE_VERSION
from .convoy_integrity import assess_convoy, min_escorts_for_coverage
from .dive_planner import BuhlmannModel, compute_ndl, cylinder_gas_volume
from .submersible_logistics import optimal_range_speed, range_nm

__all__ = ["GADGETS", "PROVIDER", "MissionProvider"]

#: Fixed deterministic seed for the whole mission (no randomness anywhere).
SEED = 7

#: Recon/plan parameters for the flagship profile — a deep-water recovery
#: dive and screen layout representative of the 1965 underwater assault.
CYLINDER_CAPACITY_L = 12.0
FILL_PRESSURE_BAR = 207.0
SAC_RATE_LMIN = 20.0
RECOVERY_DEPTH_M = 40.0
ESCORT_BEARINGS = (0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0)
HALF_ANGLE_DEG = 30.0
SUBMERSIBLE_DRAG = 0.035
SUBMERSIBLE_HOTEL_KW = 2.0
SUBMERSIBLE_ENERGY_KWH = 400.0

#: Gadgets this film registers with the BOND-API GadgetRegistry — the domain
#: callables a coordinator can invoke by name.
GADGETS: dict[str, object] = {
    "compute_ndl": compute_ndl,
    "min_escorts_for_coverage": min_escorts_for_coverage,
    "optimal_range_speed": optimal_range_speed,
}


class MissionProvider:
    """Deterministic :class:`~bond_api.protocol.MissionProvider` for THUNDERBALL.

    Drives the three domain capabilities — dive planning, convoy integrity,
    and submersible logistics — through the five lifecycle stages and returns
    a fully-provenanced, reproducible outcome.
    """

    film = "thunderball"

    def brief(self) -> MissionBrief:
        """Declare the DISCO VOLANTE mission and its objectives."""
        return MissionBrief(
            film=self.film,
            codename="DISCO VOLANTE",
            objectives=(
                "plan the underwater recovery dive",
                "verify the NATO escort screen holds",
                "confirm submersible range to reach the recovery site",
            ),
            assets=(
                Asset(
                    kind="dive_rig",
                    name="cylinder",
                    payload={
                        "capacity_l": CYLINDER_CAPACITY_L,
                        "fill_bar": FILL_PRESSURE_BAR,
                    },
                ),
                Asset(
                    kind="screen",
                    name="escort_bearings",
                    payload=tuple(ESCORT_BEARINGS),
                ),
                Asset(
                    kind="powerplant",
                    name="submersible_battery",
                    payload={"energy_kwh": SUBMERSIBLE_ENERGY_KWH},
                ),
            ),
            constraints=(
                Constraint(
                    kind="determinism",
                    detail="fixed seed 7, no random draws, no wall-clock in results",
                ),
                Constraint(
                    kind="safety",
                    detail="preserve a deco-stop margin on all planned dives",
                ),
            ),
        )

    def recon(self, request: ReconRequest) -> ReconReport:
        """Survey the request against the three controllable domains."""
        return ReconReport(
            findings=(
                Finding(label="goal", detail=request.goal),
                Finding(
                    label="dive",
                    detail="Bühlmann ZH-L16A model available; 16 compartments",
                ),
                Finding(
                    label="convoy",
                    detail="angular-gap and coverage-fraction metrics available",
                ),
                Finding(
                    label="logistics",
                    detail="cubic speed-power model with hotel load available",
                ),
            )
        )

    def plan(self, brief: MissionBrief) -> MissionPlan:
        """Plan the deterministic three-step mission."""
        return MissionPlan(
            steps=(
                Step(
                    name="dive",
                    action="plan_dive",
                    params={
                        "depth_m": RECOVERY_DEPTH_M,
                        "cylinder_capacity_l": CYLINDER_CAPACITY_L,
                        "fill_bar": FILL_PRESSURE_BAR,
                        "sac_lmin": SAC_RATE_LMIN,
                    },
                ),
                Step(
                    name="convoy",
                    action="assess_screen",
                    params={
                        "bearings": tuple(ESCORT_BEARINGS),
                        "half_angle_deg": HALF_ANGLE_DEG,
                    },
                ),
                Step(
                    name="logistics",
                    action="evaluate_range",
                    params={
                        "energy_kwh": SUBMERSIBLE_ENERGY_KWH,
                        "drag": SUBMERSIBLE_DRAG,
                        "hotel_kw": SUBMERSIBLE_HOTEL_KW,
                    },
                ),
            )
        )

    def execute(self, plan: MissionPlan) -> MissionOutcome:
        """Run the plan through the domain core and return a provenanced result."""
        dive_params = plan.steps[0].params
        convoy_params = plan.steps[1].params
        logistics_params = plan.steps[2].params

        model = BuhlmannModel()
        ndl = compute_ndl(dive_params["depth_m"], model=model)
        gas_volume = cylinder_gas_volume(
            dive_params["cylinder_capacity_l"], dive_params["fill_bar"]
        )
        gas_duration_min = gas_volume / (
            dive_params["sac_lmin"] * (1.013 + 0.1 * dive_params["depth_m"])
        )

        convoy = assess_convoy(
            tuple(convoy_params["bearings"]), convoy_params["half_angle_deg"]
        )
        min_escorts = min_escorts_for_coverage(0.9, convoy_params["half_angle_deg"])

        v_opt = optimal_range_speed(
            logistics_params["energy_kwh"],
            logistics_params["drag"],
            logistics_params["hotel_kw"],
        )
        opt_range = range_nm(
            logistics_params["energy_kwh"],
            v_opt,
            logistics_params["drag"],
            logistics_params["hotel_kw"],
        )

        success = (
            convoy.status.label == "ok" and gas_duration_min > 0.0 and opt_range > 0.0
        )
        return MissionOutcome(
            success=success,
            results={
                "ndl_minutes": round(ndl, 2),
                "air_duration_min": round(gas_duration_min, 2),
                "convoy_largest_gap_deg": round(convoy.largest_gap_deg, 2),
                "convoy_coverage": round(convoy.coverage, 4),
                "convoy_score": round(convoy.score, 4),
                "convoy_status": convoy.status.label,
                "min_escorts_90pct": min_escorts,
                "optimal_speed_knots": round(v_opt, 3),
                "optimal_range_nm": round(opt_range, 2),
                "steps_completed": len(plan.steps),
            },
            provenance=Provenance(
                package_version=_PACKAGE_VERSION,
                seed=SEED,
                input_hash="thunderball-disco-volante-recovery",
                wall_time_s=0.0,
            ),
        )

    def debrief(self, outcome: MissionOutcome) -> Debrief:
        """Summarise the mission and record standing lessons."""
        return Debrief(
            outcome=outcome,
            lessons=(
                "deco-stop margin is mandatory beneath maximum working depth",
                "a convoy screen is only as strong as its largest angular gap",
                "range is maximised by balancing the cubic drag law against hotel load",
            ),
        )


PROVIDER: MissionProvider = MissionProvider()


def _register_film_gadgets(registry: GadgetRegistry) -> GadgetRegistry:
    """Register this film's gadgets with any BOND-API gadget registry."""
    registry.register(PROVIDER.film, GADGETS)
    return registry
