"""Tests for the dive-planning domain: air budget and Bühlmann ZH-L16A deco."""

from __future__ import annotations

import pytest

from thunderball.dive_planner import (
    BuhlmannModel,
    alveolar_pressure,
    ambient_pressure,
    bottom_time_from_air,
    buhlmann_mvalue,
    compute_ndl,
    cylinder_gas_volume,
    plan_decompression,
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


def test_buhlmann_mvalue_line() -> None:
    # M = a*P + b for compartment 1 at surface.
    assert buhlmann_mvalue(1.013, 1.2599, 0.5050) == pytest.approx(
        1.2599 * 1.013 + 0.5050
    )


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
    # NDL strictly shrinks as depth increases and remains a finite value even
    # at great depth (a ZH-L16A model without gradient factors yields a large,
    # conservative no-stop time but still monotonic in depth).
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
