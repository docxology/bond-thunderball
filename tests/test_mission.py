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
    assert {f.label for f in report.findings} == {"goal", "dive", "convoy", "logistics"}


def test_plan_has_three_steps() -> None:
    plan = PROVIDER.plan(PROVIDER.brief())
    assert isinstance(plan, MissionPlan)
    assert [s.name for s in plan.steps] == ["dive", "convoy", "logistics"]


def test_execute_is_successful_and_provenanced() -> None:
    outcome = PROVIDER.execute(PROVIDER.plan(PROVIDER.brief()))
    assert isinstance(outcome, MissionOutcome)
    assert outcome.success is True
    assert outcome.provenance.seed == 7
    assert outcome.provenance.input_hash
    assert outcome.results["convoy_status"] == "ok"
    assert outcome.results["min_escorts_90pct"] == 6


def test_debrief_records_lessons() -> None:
    outcome = PROVIDER.execute(PROVIDER.plan(PROVIDER.brief()))
    debrief = PROVIDER.debrief(outcome)
    assert len(debrief.lessons) == 3
    assert all(lesson for lesson in debrief.lessons)


def test_run_mission_full_flow() -> None:
    debrief = run_mission(PROVIDER, ReconRequest(goal="recover the bombs"))
    assert debrief.outcome.success is True


def test_provider_satisfies_discovery_protocol() -> None:
    from bond_api.protocol import MissionProvider as Protocol

    assert isinstance(PROVIDER, Protocol)


def test_provider_is_discoverable_by_slug(tmp_path) -> None:
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


def test_execute_is_deterministic() -> None:
    r1 = PROVIDER.execute(PROVIDER.plan(PROVIDER.brief())).results
    r2 = PROVIDER.execute(PROVIDER.plan(PROVIDER.brief())).results
    assert r1 == r2
