"""Thunderball — DISCO VOLANTE MissionProvider (BOND-API protocol adapter).

This module is the thin adapter between the frozen
:class:`bond_api.protocol.MissionProvider` contract and the pure domain core
in :mod:`thunderball.dive_planner`, :mod:`thunderball.convoy_integrity`,
:mod:`thunderball.submersible_logistics`, :mod:`thunderball.sonar_detection`,
:mod:`thunderball.current_navigation`, and
:mod:`thunderball.interdiction_analysis`.

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
from .current_navigation import assess_navigation, course_to_steer
from .dive_planner import BuhlmannModel, bottom_time_from_air, compute_ndl, plan_dive
from .interdiction_analysis import assess_interdiction, closest_point_of_approach
from .sonar_detection import detection_range_nm
from .submersible_logistics import optimal_range_speed, range_nm

__all__ = ["GADGETS", "PROVIDER", "MissionProvider"]

#: Fixed deterministic seed for the whole mission (no randomness anywhere).
SEED = 7

#: Recon/plan parameters for the flagship profile — a deep-water recovery
#: dive, screen layout, and threat track representative of the 1965
#: underwater assault.
CYLINDER_CAPACITY_L = 12.0
FILL_PRESSURE_BAR = 207.0
SAC_RATE_LMIN = 20.0
RECOVERY_DEPTH_M = 40.0
ESCORT_BEARINGS = (0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0)
HALF_ANGLE_DEG = 30.0
#: Perimeter-coverage target used to size a uniform reinforcement screen.
COVERAGE_TARGET = 0.9
SUBMERSIBLE_DRAG = 0.035
SUBMERSIBLE_HOTEL_KW = 2.0
SUBMERSIBLE_ENERGY_KWH = 400.0

# Passive-sonar scenario (source/noise levels, detection threshold).
SONAR_F_KHZ = 10.0
SONAR_SL_DB = 150.0
SONAR_NL_DB = 75.0
SONAR_DI_DB = 15.0
SONAR_DT_DB = 10.0
SONAR_MAX_RANGE_NM = 120.0

# Set-and-drift navigation scenario.
NAV_TRACK_DEG = 315.0
NAV_SPEED_KNOTS = 4.0
CURRENT_SET_DEG = 90.0
CURRENT_DRIFT_KNOTS = 0.8
RECOVERY_RADIUS_NM = 1.0

# Interdiction scenario: threat track relative to the convoy's own course.
CONVOY_COURSE_DEG = 45.0
CONVOY_SPEED_KNOTS = 12.0
THREAT_POSITION = (5.0, -2.0)
THREAT_COURSE_DEG = 270.0
THREAT_SPEED_KNOTS = 20.0
SCREEN_RADIUS_NM = 2.0
MIN_SEPARATION_NM = 1.0
ESCORT_REACTION_H = 0.05

#: Gadgets this film registers with the BOND-API GadgetRegistry — the domain
#: callables a coordinator can invoke by name.
GADGETS: dict[str, object] = {
    "closest_point_of_approach": closest_point_of_approach,
    "compute_ndl": compute_ndl,
    "course_to_steer": course_to_steer,
    "detection_range_nm": detection_range_nm,
    "min_escorts_for_coverage": min_escorts_for_coverage,
    "optimal_range_speed": optimal_range_speed,
}


class MissionProvider:
    """Deterministic :class:`~bond_api.protocol.MissionProvider` for THUNDERBALL.

    Drives the six domain capabilities — dive planning, convoy integrity,
    submersible logistics, passive sonar detection, set-and-drift navigation,
    and convoy interdiction — through the five lifecycle stages and returns a
    fully-provenanced, reproducible outcome.
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
                "confirm passive-sonar detection of the recovery site",
                "steer the return leg against the prevailing current",
                "interdict closing threat tracks before they reach the screen",
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
                Asset(
                    kind="hydrophone",
                    name="passive_sonar",
                    payload={"f_khz": SONAR_F_KHZ, "di_db": SONAR_DI_DB},
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
        """Survey the request against the six controllable domains."""
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
                Finding(
                    label="sonar",
                    detail="Thorp absorption and passive-sonar range equation available",
                ),
                Finding(
                    label="navigation",
                    detail="set-and-drift vector triangle and dead-reckoning available",
                ),
                Finding(
                    label="interdiction",
                    detail="CPA geometry and screen-penetration model available",
                ),
            )
        )

    def plan(self, brief: MissionBrief) -> MissionPlan:
        """Plan the deterministic six-step mission."""
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
                Step(
                    name="sonar",
                    action="assess_detection",
                    params={
                        "f_khz": SONAR_F_KHZ,
                        "sl_db": SONAR_SL_DB,
                        "nl_db": SONAR_NL_DB,
                        "di_db": SONAR_DI_DB,
                        "dt_db": SONAR_DT_DB,
                        "max_range_nm": SONAR_MAX_RANGE_NM,
                    },
                ),
                Step(
                    name="navigation",
                    action="assess_current",
                    params={
                        "track_deg": NAV_TRACK_DEG,
                        "speed_knots": NAV_SPEED_KNOTS,
                        "set_deg": CURRENT_SET_DEG,
                        "drift_knots": CURRENT_DRIFT_KNOTS,
                        "recovery_radius_nm": RECOVERY_RADIUS_NM,
                    },
                ),
                Step(
                    name="interdiction",
                    action="assess_threat",
                    params={
                        "convoy_course_deg": CONVOY_COURSE_DEG,
                        "convoy_speed_knots": CONVOY_SPEED_KNOTS,
                        "threat_position": tuple(THREAT_POSITION),
                        "threat_course_deg": THREAT_COURSE_DEG,
                        "threat_speed_knots": THREAT_SPEED_KNOTS,
                        "screen_radius_nm": SCREEN_RADIUS_NM,
                        "min_separation_nm": MIN_SEPARATION_NM,
                        "reaction_time_h": ESCORT_REACTION_H,
                    },
                ),
            )
        )

    def execute(self, plan: MissionPlan) -> MissionOutcome:
        """Run the plan through the domain core and return a provenanced result."""
        dive_params = plan.steps[0].params
        convoy_params = plan.steps[1].params
        logistics_params = plan.steps[2].params
        sonar_params = plan.steps[3].params
        nav_params = plan.steps[4].params
        interdiction_params = plan.steps[5].params

        model = BuhlmannModel()
        dive = plan_dive(
            depth_m=dive_params["depth_m"],
            cylinder_capacity_l=dive_params["cylinder_capacity_l"],
            fill_pressure_bar=dive_params["fill_bar"],
            sac_rate_lmin=dive_params["sac_lmin"],
            model=model,
        )
        ndl = dive.ndl_minutes
        # Gas-limited bottom time, before the NDL cap: the same helper plan_dive
        # uses internally, so the adapter cannot drift from the domain core.
        gas_duration_min = bottom_time_from_air(
            dive.air_volume_l, dive_params["sac_lmin"], dive_params["depth_m"]
        )

        convoy = assess_convoy(
            tuple(convoy_params["bearings"]), convoy_params["half_angle_deg"]
        )
        min_escorts = min_escorts_for_coverage(
            COVERAGE_TARGET, convoy_params["half_angle_deg"]
        )

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

        sonar_range = detection_range_nm(
            sonar_params["sl_db"],
            sonar_params["nl_db"],
            sonar_params["di_db"],
            sonar_params["f_khz"],
            sonar_params["dt_db"],
            sonar_params["max_range_nm"],
        )

        # Navigation: the team is in the water for the dive's *planned* bottom
        # time — min(air limit, NDL) as reported by plan_dive — not for the
        # air-budget limit it never gets to fly. Using gas_duration_min here
        # would overstate the drift whenever decompression binds first.
        bottom_hours = dive.bottom_minutes / 60.0
        nav = assess_navigation(
            desired_track_deg=nav_params["track_deg"],
            speed_knots=nav_params["speed_knots"],
            set_deg=nav_params["set_deg"],
            drift_knots=nav_params["drift_knots"],
            duration_h=bottom_hours,
            recovery_radius_nm=nav_params["recovery_radius_nm"],
        )

        interdiction = assess_interdiction(
            own_position=(0.0, 0.0),
            own_course_deg=interdiction_params["convoy_course_deg"],
            own_speed_knots=interdiction_params["convoy_speed_knots"],
            threat_position=tuple(interdiction_params["threat_position"]),
            threat_course_deg=interdiction_params["threat_course_deg"],
            threat_speed_knots=interdiction_params["threat_speed_knots"],
            gap_deg=convoy.largest_gap_deg,
            screen_radius_nm=interdiction_params["screen_radius_nm"],
            min_separation_nm=interdiction_params["min_separation_nm"],
            reaction_time_h=interdiction_params["reaction_time_h"],
        )

        success = (
            convoy.status.label == "ok"
            and gas_duration_min > 0.0
            and opt_range > 0.0
            and sonar_range > 0.0
            and not nav.drift_exceeds_recovery
            and interdiction.status == "held"
        )
        return MissionOutcome(
            success=success,
            results={
                "ndl_minutes": round(ndl, 2),
                "air_duration_min": round(gas_duration_min, 2),
                "dive_bottom_minutes": round(dive.bottom_minutes, 2),
                "dive_binding_constraint": dive.binding_constraint(),
                "dive_gas_required_l": round(dive.total_gas_required_l(), 1),
                "dive_gas_margin_l": round(dive.gas_margin_l(), 1),
                "dive_deco_stops": len(dive.deco_stops),
                "convoy_largest_gap_deg": round(convoy.largest_gap_deg, 2),
                "convoy_uncovered_sector_deg": round(convoy.uncovered_sector_deg, 2),
                "convoy_coverage": round(convoy.coverage, 4),
                "convoy_score": round(convoy.score, 4),
                "convoy_status": convoy.status.label,
                "min_escorts_90pct": min_escorts,
                "optimal_speed_knots": round(v_opt, 3),
                "optimal_range_nm": round(opt_range, 2),
                "sonar_detection_range_nm": round(sonar_range, 2),
                "nav_drift_nm": round(nav.drift_nm, 3),
                "nav_drift_exceeds_recovery": nav.drift_exceeds_recovery,
                "nav_heading_to_steer_deg": round(nav.heading_to_steer_deg, 2),
                "nav_ground_speed_knots": round(nav.ground_speed_knots, 3),
                "interdiction_cpa_nm": round(interdiction.d_cpa_nm, 3),
                "interdiction_t_cpa_h": round(interdiction.t_cpa_h, 4),
                "interdiction_closing_knots": round(interdiction.closing_knots, 2),
                "interdiction_penetration_h": round(interdiction.penetration_time_h, 4),
                "interdiction_status": interdiction.status,
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
                "passive detection range collapses as ambient noise rises",
                "set and drift force a course correction on every return leg",
                "the screen holds only while escorts react faster than the gap is crossed",
            ),
        )


PROVIDER: MissionProvider = MissionProvider()


def _register_film_gadgets(registry: GadgetRegistry) -> GadgetRegistry:
    """Register this film's gadgets with any BOND-API gadget registry."""
    registry.register(PROVIDER.film, GADGETS)
    return registry
