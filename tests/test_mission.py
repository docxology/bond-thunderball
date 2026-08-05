"""Tests for the thunderball BOND-API MissionProvider adapter."""

from __future__ import annotations

from bond_api.protocol import (
    MissionBrief,
    MissionOutcome,
    MissionPlan,
    ReconReport,
    ReconRequest,
    run_mission,
)
from bond_api.registry import GadgetRegistry, MissionRegistry

from thunderball.mission import (
    GADGETS,
    PROVIDER,
    _register_film_gadgets,
)


def test_provider_identity() -> None:
    assert PROVIDER.film == "thunderball"
    assert PROVIDER.brief().codename == "DISCO VOLANTE"


def test_brief_is_protocol_brief() -> None:
    brief = PROVIDER.brief()
    assert isinstance(brief, MissionBrief)
    assert brief.objectives
    assert all(asset.kind and asset.name for asset in brief.assets)
    assert any(c.kind == "determinism" for c in brief.constraints)


def test_recon_returns_findings() -> None:
    report = PROVIDER.recon(ReconRequest(goal="verify the screen"))
    assert isinstance(report, ReconReport)
    assert {f.label for f in report.findings} == {
        "goal",
        "dive",
        "convoy",
        "logistics",
        "sonar",
        "navigation",
        "interdiction",
    }


def test_plan_has_six_steps() -> None:
    plan = PROVIDER.plan(PROVIDER.brief())
    assert isinstance(plan, MissionPlan)
    assert [s.name for s in plan.steps] == [
        "dive",
        "convoy",
        "logistics",
        "sonar",
        "navigation",
        "interdiction",
    ]


def test_execute_is_successful_and_provenanced() -> None:
    outcome = PROVIDER.execute(PROVIDER.plan(PROVIDER.brief()))
    assert isinstance(outcome, MissionOutcome)
    assert outcome.success is True
    assert outcome.provenance.seed == 7
    assert outcome.provenance.input_hash
    assert outcome.results["convoy_status"] == "ok"
    assert outcome.results["min_escorts_90pct"] == 6
    assert outcome.results["interdiction_status"] == "held"
    assert outcome.results["sonar_detection_range_nm"] > 0.0
    assert outcome.results["nav_drift_exceeds_recovery"] is False


def test_execute_dive_results_agree_with_the_domain_core() -> None:
    """The adapter must not re-derive dive numbers; it must report plan_dive()."""
    from thunderball.dive_planner import plan_dive
    from thunderball.mission import (
        CYLINDER_CAPACITY_L,
        FILL_PRESSURE_BAR,
        RECOVERY_DEPTH_M,
        SAC_RATE_LMIN,
    )

    results = PROVIDER.execute(PROVIDER.plan(PROVIDER.brief())).results
    dive = plan_dive(
        depth_m=RECOVERY_DEPTH_M,
        cylinder_capacity_l=CYLINDER_CAPACITY_L,
        fill_pressure_bar=FILL_PRESSURE_BAR,
        sac_rate_lmin=SAC_RATE_LMIN,
    )
    assert results["ndl_minutes"] == round(dive.ndl_minutes, 2)
    assert results["dive_bottom_minutes"] == round(dive.bottom_minutes, 2)
    assert results["dive_gas_required_l"] == round(dive.total_gas_required_l(), 1)
    assert results["dive_gas_margin_l"] == round(dive.gas_margin_l(), 1)
    assert results["dive_binding_constraint"] == "deco"
    assert results["dive_deco_stops"] == len(dive.deco_stops)
    # The gas budget must actually fit the cylinder for the flagship profile.
    assert results["dive_gas_margin_l"] > 0.0


def test_coverage_target_constant_drives_min_escorts() -> None:
    """min_escorts_90pct must follow COVERAGE_TARGET, not a stray literal."""
    from thunderball.convoy_integrity import min_escorts_for_coverage
    from thunderball.mission import COVERAGE_TARGET, HALF_ANGLE_DEG

    results = PROVIDER.execute(PROVIDER.plan(PROVIDER.brief())).results
    assert results["min_escorts_90pct"] == min_escorts_for_coverage(
        COVERAGE_TARGET, HALF_ANGLE_DEG
    )
    # Both arguments must be load-bearing, not coincidentally equal: a looser
    # target needs strictly fewer escorts, a narrower arc strictly more.
    assert min_escorts_for_coverage(0.8, HALF_ANGLE_DEG) < results["min_escorts_90pct"]
    assert (
        min_escorts_for_coverage(COVERAGE_TARGET, HALF_ANGLE_DEG / 2.0)
        > results["min_escorts_90pct"]
    )


def test_debrief_records_lessons() -> None:
    outcome = PROVIDER.execute(PROVIDER.plan(PROVIDER.brief()))
    debrief = PROVIDER.debrief(outcome)
    assert len(debrief.lessons) == 6
    assert all(lesson for lesson in debrief.lessons)


def test_run_mission_full_flow() -> None:
    debrief = run_mission(PROVIDER, ReconRequest(goal="recover the bombs"))
    assert debrief.outcome.success is True


def test_provider_satisfies_discovery_protocol() -> None:
    from bond_api.protocol import MissionProvider as Protocol

    assert isinstance(PROVIDER, Protocol)


def test_provider_is_discoverable_by_slug() -> None:
    # The real discovery loader must find `thunderball.mission`.
    from bond_api.discovery import load_provider

    provider = load_provider("thunderball", search_paths=["src"])
    assert provider.film == "thunderball"
    assert provider.brief().codename == "DISCO VOLANTE"


def test_provider_registers_in_mission_registry() -> None:
    registry = MissionRegistry()
    registry.register(PROVIDER)
    assert "thunderball" in registry
    assert registry.lookup("thunderball").film == "thunderball"


def test_gadget_registration_hook() -> None:
    registry = GadgetRegistry()
    _register_film_gadgets(registry)
    assert registry.contains("thunderball", "compute_ndl")
    assert registry.contains("thunderball", "optimal_range_speed")
    assert registry.films() == ("thunderball",)
    # Re-registration is idempotent.
    _register_film_gadgets(registry)
    assert registry.contains("thunderball", "compute_ndl")


def test_gadgets_are_domain_callables() -> None:
    assert callable(GADGETS["compute_ndl"])
    assert callable(GADGETS["min_escorts_for_coverage"])
    assert callable(GADGETS["optimal_range_speed"])
    assert callable(GADGETS["detection_range_nm"])
    assert callable(GADGETS["course_to_steer"])
    assert callable(GADGETS["closest_point_of_approach"])
    assert len(GADGETS) == 6


def test_execute_is_deterministic() -> None:
    r1 = PROVIDER.execute(PROVIDER.plan(PROVIDER.brief())).results
    r2 = PROVIDER.execute(PROVIDER.plan(PROVIDER.brief())).results
    assert r1 == r2
