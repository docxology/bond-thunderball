"""Tests for the dive-planning domain: air budget and Bühlmann ZH-L16A deco."""

from __future__ import annotations

import pytest

from thunderball.dive_planner import (
    BuhlmannModel,
    DecoStop,
    DivePlan,
    alveolar_pressure,
    ambient_pressure,
    bottom_time_from_air,
    buhlmann_mvalue,
    compute_ndl,
    cylinder_gas_volume,
    plan_decompression,
    plan_dive,
    tissue_pressure_after,
)


def test_ambient_pressure_surface_and_depth() -> None:
    assert ambient_pressure(0.0) == pytest.approx(1.013)
    assert ambient_pressure(10.0) == pytest.approx(2.013)
    assert ambient_pressure(40.0) == pytest.approx(5.013)


def test_alveolar_pressure_is_n2_fraction_of_ambient_minus_vapour() -> None:
    assert alveolar_pressure(5.013) == pytest.approx(0.79 * (5.013 - 0.0627))


def test_cylinder_gas_volume() -> None:
    assert cylinder_gas_volume(12.0, 207.0) == pytest.approx(2484.0)


def test_cylinder_gas_volume_rejects_nonpositive() -> None:
    with pytest.raises(ValueError):
        cylinder_gas_volume(0.0, 207.0)
    with pytest.raises(ValueError):
        cylinder_gas_volume(12.0, 0.0)


def test_bottom_time_scales_down_with_depth() -> None:
    shallow = bottom_time_from_air(2484.0, 20.0, 10.0)
    deep = bottom_time_from_air(2484.0, 20.0, 40.0)
    assert shallow > deep


def test_bottom_time_reserve_reduces_duration() -> None:
    full = bottom_time_from_air(2484.0, 20.0, 40.0)
    reserved = bottom_time_from_air(2484.0, 20.0, 40.0, reserve_fraction=0.25)
    assert reserved == pytest.approx(0.75 * full)


def test_bottom_time_rejects_bad_reserve() -> None:
    with pytest.raises(ValueError):
        bottom_time_from_air(2484.0, 20.0, 40.0, reserve_fraction=1.0)
    with pytest.raises(ValueError):
        bottom_time_from_air(2484.0, 20.0, 40.0, reserve_fraction=-0.1)


def test_buhlmann_mvalue_matches_published_surfacing_limits() -> None:
    """Pin the M-value line to Buehlmann's own published surfacing ceilings.

    These are external anchors, not a restatement of the implementation: the
    ZH-L16A fastest compartment tolerates ~3.27 bar of inert-gas tension at the
    surface and the slowest ~1.28 bar. The transposed form ``a*P + b`` gives
    1.78 bar and 1.20 bar respectively and fails this test.
    """
    assert buhlmann_mvalue(1.013, 1.2599, 0.5050) == pytest.approx(3.2658, abs=1e-3)
    assert buhlmann_mvalue(1.013, 0.2327, 0.9653) == pytest.approx(1.2821, abs=1e-3)
    # The line is increasing in ambient pressure with slope 1/b.
    at_10m = buhlmann_mvalue(2.013, 1.2599, 0.5050)
    assert at_10m > buhlmann_mvalue(1.013, 1.2599, 0.5050)
    assert (at_10m - buhlmann_mvalue(1.013, 1.2599, 0.5050)) == pytest.approx(
        1.0 / 0.5050, abs=1e-6
    )


def test_buhlmann_mvalue_rejects_zero_slope_coefficient() -> None:
    with pytest.raises(ValueError, match="b must be"):
        buhlmann_mvalue(1.013, 1.0, 0.0)


def test_ndl_matches_published_zhl16a_no_stop_times() -> None:
    """The no-stop limits must land in the published ZH-L16A air-table bands.

    This is the test that catches an M-value or ascent-ceiling transposition:
    evaluating M-values at the bottom ambient pressure instead of the surface
    inflates the 40 m limit from ~9 min to ~163 min, which sails past every
    monotonicity or positivity check but is wrong by a factor of eighteen.
    """
    model = BuhlmannModel()
    assert 50.0 < compute_ndl(18.0, model=model) < 80.0
    assert 15.0 < compute_ndl(30.0, model=model) < 25.0
    assert 7.0 < compute_ndl(40.0, model=model) < 12.0
    assert 3.0 < compute_ndl(60.0, model=model) < 7.0


def test_tissue_pressure_after_minutes_zero_unchanged() -> None:
    assert tissue_pressure_after(0.7, 1.5, 4.0, 0.0) == pytest.approx(0.7)


def test_tissue_pressure_after_rejects_negative_time() -> None:
    with pytest.raises(ValueError):
        tissue_pressure_after(0.7, 1.5, 4.0, -1.0)


def test_tissue_pressure_after_tends_to_alveolar() -> None:
    # After many half-lives the tissue approaches the alveolar pressure.
    result = tissue_pressure_after(0.7, 1.5, 4.0, 400.0)
    assert result == pytest.approx(1.5, abs=1e-9)


def test_ndl_decreases_with_depth() -> None:
    model = BuhlmannModel()
    shallow_ndl = compute_ndl(12.0, model=model)
    deep_ndl = compute_ndl(40.0, model=model)
    assert shallow_ndl > deep_ndl
    assert deep_ndl > 0.0


def test_ndl_rejects_nonpositive_depth() -> None:
    model = BuhlmannModel()
    with pytest.raises(ValueError):
        compute_ndl(-5.0, model=model)


def test_ndl_monotonic_decreases_to_extreme_depth() -> None:
    # NDL strictly shrinks as depth increases and stays positive even at
    # extreme depth: the ascent ceiling is fixed at the surface, so deeper
    # dives saturate toward it faster but never instantaneously.
    model = BuhlmannModel()
    ndl_10 = compute_ndl(10.0, model=model)
    ndl_200 = compute_ndl(200.0, model=model)
    assert 0.0 < ndl_200 < ndl_10


def test_model_has_sixteen_compartments() -> None:
    model = BuhlmannModel()
    assert len(model.half_time) == 16
    assert len(model.a_coeff) == 16
    assert len(model.b_coeff) == 16
    assert model.half_time[0] == 4.0


def test_deep_long_dive_requires_deco_stops() -> None:
    # A dive beyond the NDL must produce ascending stops.
    model = BuhlmannModel()
    profile = [(30.0, 100.0)]
    stops = plan_decompression(profile, model=model)
    assert len(stops) > 0
    depths = [stop.depth_m for stop in stops]
    assert depths == sorted(depths, reverse=True)  # deepest first


def test_shallow_short_dive_is_no_stop() -> None:
    model = BuhlmannModel()
    stops = plan_decompression([(10.0, 20.0)], model=model)
    assert stops == ()


def test_plan_decompression_math_consistency() -> None:
    """Moderate dives yield a coherent, bounded deco schedule: ascending stops
    with positive hold times that do not hit the degenerate cap."""
    model = BuhlmannModel()
    stops = plan_decompression([(25.0, 120.0)], model=model)
    assert len(stops) > 0
    depths = [stop.depth_m for stop in stops]
    assert depths == sorted(depths, reverse=True)
    for stop in stops:
        assert stop.depth_m >= 0.0
        assert stop.minutes > 0.0
    # A sensible no-stop-by-demerit schedule totals well under the cap.
    assert sum(stop.minutes for stop in stops) < 600.0


def test_tissue_pressures_after_profile_loads_every_compartment() -> None:
    """A deep hold must raise every compartment above surface saturation, and
    fast compartments must load further than slow ones."""
    model = BuhlmannModel()
    surface = model.initial_tissue_pressure()
    tissues = model.tissue_pressures_after_profile([(40.0, 30.0)])
    assert len(tissues) == len(model.half_time)
    assert all(t > surface for t in tissues)
    # Compartment 1 (4 min half-time) loads far faster than compartment 16.
    assert tissues[0] > tissues[-1]


def test_ndl_returns_zero_when_the_model_forbids_any_bottom_time() -> None:
    """The zero-NDL guard is reachable: a pathologically conservative table
    whose M-values sit below surface saturation requires a stop on arrival."""

    class ImpossibleTable(BuhlmannModel):
        # M(P) = P/b + a, so a large b and zero a give a surfacing ceiling far
        # below the 0.75 bar tension of a surface-saturated diver. Physically
        # absurd, deliberately: it proves the guard is not dead code.
        a_coeff = (0.0,) * 16
        b_coeff = (10.0,) * 16

    strict = ImpossibleTable()
    ceiling = buhlmann_mvalue(1.013, 0.0, 10.0)
    assert strict.initial_tissue_pressure() > ceiling  # the table is truly stricter
    assert strict.ndl_minutes(40.0) == 0.0
    assert compute_ndl(40.0, model=strict) == 0.0
    # The stock table, by contrast, always allows some bottom time.
    assert compute_ndl(40.0, model=BuhlmannModel()) > 0.0


def test_plan_decompression_instant_ascent_branch() -> None:
    """``ascent_rate_m_min=0`` disables the ascent-loading contribution; the
    resulting schedule is no longer than the rate-limited one."""
    model = BuhlmannModel()
    timed = plan_decompression([(30.0, 90.0)], ascent_rate_m_min=9.0, model=model)
    instant = plan_decompression([(30.0, 90.0)], ascent_rate_m_min=0.0, model=model)
    assert sum(s.minutes for s in instant) <= sum(s.minutes for s in timed)
    assert all(s.minutes > 0.0 for s in instant)


def test_plan_dive_default_flies_the_binding_limit() -> None:
    plan = plan_dive(
        depth_m=40.0,
        cylinder_capacity_l=12.0,
        fill_pressure_bar=207.0,
        sac_rate_lmin=20.0,
    )
    air_limit = bottom_time_from_air(12.0 * 207.0, 20.0, 40.0)
    assert plan.bottom_minutes == pytest.approx(min(air_limit, plan.ndl_minutes))
    assert plan.within_air is True
    assert plan.within_ndl is True
    # Decompression binds first at 40 m: the NDL (~9 min) runs out well before
    # the 12 L / 207 bar cylinder does (~25 min).
    assert plan.ndl_minutes < air_limit
    assert plan.binding_constraint() == "deco"
    # Flying exactly the NDL is by definition a no-stop dive.
    assert plan.deco_stops == ()


def test_plan_dive_flags_are_load_bearing_when_a_time_is_requested() -> None:
    """An over-long request must clear the flags and incur a real obligation."""
    plan = plan_dive(
        depth_m=40.0,
        cylinder_capacity_l=12.0,
        fill_pressure_bar=207.0,
        sac_rate_lmin=20.0,
        requested_bottom_minutes=400.0,
    )
    assert plan.within_air is False
    assert plan.within_ndl is False
    assert plan.binding_constraint() == "air"  # the first violated limit wins
    assert plan.deco_stops != ()
    assert plan.gas_margin_l() < 0.0


def test_plan_dive_short_request_is_bound_by_neither_limit() -> None:
    plan = plan_dive(
        depth_m=40.0,
        cylinder_capacity_l=12.0,
        fill_pressure_bar=207.0,
        sac_rate_lmin=20.0,
        requested_bottom_minutes=5.0,
    )
    assert plan.binding_constraint() == "none"
    assert plan.gas_margin_l() > 0.0


def test_plan_dive_rejects_a_negative_request() -> None:
    with pytest.raises(ValueError, match="requested_bottom_minutes"):
        plan_dive(
            depth_m=40.0,
            cylinder_capacity_l=12.0,
            fill_pressure_bar=207.0,
            sac_rate_lmin=20.0,
            requested_bottom_minutes=-1.0,
        )


def test_deco_stop_gas_is_charged_at_stop_pressure_not_surface_rate() -> None:
    """A 6 m hold costs ~1.6x the surface SAC volume, not 1x."""
    plan = DivePlan(
        depth_m=30.0,
        bottom_minutes=10.0,
        air_volume_l=2484.0,
        sac_rate_lmin=20.0,
        ndl_minutes=20.0,
        deco_stops=(DecoStop(depth_m=6.0, minutes=10.0),),
    )
    bottom = 20.0 * ambient_pressure(30.0) * 10.0
    deco = 20.0 * ambient_pressure(6.0) * 10.0
    assert plan.bottom_gas_required_l() == pytest.approx(bottom)
    assert plan.total_gas_required_l() == pytest.approx(bottom + deco)
    assert deco == pytest.approx(20.0 * 1.613 * 10.0)
    # A surface-rate approximation would understate the deco leg by >60%.
    assert deco > 1.6 * (20.0 * 10.0)
    assert plan.gas_margin_l() == pytest.approx(2484.0 - bottom - deco)


def test_binding_constraint_reports_deco_when_only_the_ndl_is_exceeded() -> None:
    """A request inside the gas budget but past the NDL must name deco."""
    plan = plan_dive(
        depth_m=40.0,
        cylinder_capacity_l=12.0,
        fill_pressure_bar=207.0,
        sac_rate_lmin=20.0,
        requested_bottom_minutes=15.0,
    )
    air_limit = bottom_time_from_air(12.0 * 207.0, 20.0, 40.0)
    assert plan.ndl_minutes < 15.0 < air_limit  # the premise the test relies on
    assert plan.within_air is True
    assert plan.within_ndl is False
    assert plan.binding_constraint() == "deco"
    assert plan.deco_stops != ()
