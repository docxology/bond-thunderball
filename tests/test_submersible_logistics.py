"""Tests for the submersible-logistics domain: power, endurance, range, energy."""

from __future__ import annotations

import math

import pytest

from thunderball.submersible_logistics import (
    endurance_hours,
    energy_for_mission,
    optimal_range_speed,
    power_kw,
    range_nm,
    speed_for_range,
)


def test_power_kw_cubic_at_zero_speed_is_hotel() -> None:
    assert power_kw(0.0, 0.035, hotel_kw=2.0) == pytest.approx(2.0)


def test_power_kw_cubic_law() -> None:
    # P = k v^3 + H; doubling speed multiplies the drag term by 8.
    p1 = power_kw(10.0, 0.035, hotel_kw=0.0)
    p2 = power_kw(20.0, 0.035, hotel_kw=0.0)
    assert p2 == pytest.approx(8.0 * p1)


def test_power_kw_rejects_negative() -> None:
    with pytest.raises(ValueError):
        power_kw(-1.0, 0.035, hotel_kw=2.0)


def test_endurance_hours() -> None:
    # 400 kWh at a constant 10 kW draw lasts 40 h.
    e = endurance_hours(400.0, 5.0, 0.035, hotel_kw=2.0)
    p = power_kw(5.0, 0.035, hotel_kw=2.0)
    assert e == pytest.approx(400.0 / p)


def test_endurance_rejects_nonpositive_energy() -> None:
    with pytest.raises(ValueError):
        endurance_hours(0.0, 5.0, 0.035)


def test_range_is_speed_times_endurance() -> None:
    r = range_nm(400.0, 5.0, 0.035, hotel_kw=2.0)
    e = endurance_hours(400.0, 5.0, 0.035, hotel_kw=2.0)
    assert r == pytest.approx(5.0 * e)


def test_optimal_range_speed_balances_hotel_and_drag() -> None:
    # Analytic optimum: k v^3 = H/2.
    v = optimal_range_speed(400.0, 0.035, 2.0)
    assert v == pytest.approx((2.0 / (2.0 * 0.035)) ** (1.0 / 3.0))


def test_optimal_range_speed_rejects_nonpositive() -> None:
    with pytest.raises(ValueError):
        optimal_range_speed(0.0, 0.035, 2.0)
    with pytest.raises(ValueError):
        optimal_range_speed(400.0, 0.0, 2.0)


def test_energy_for_mission_inverse_consistency() -> None:
    # Energy required for a range at a speed, then recovering that range from
    # the energy, must round-trip to the same speed.
    speed = 5.0
    energy = energy_for_mission(100.0, speed, 0.035, hotel_kw=2.0)
    recovered = speed_for_range(100.0, energy, 0.035, hotel_kw=2.0)
    assert recovered == pytest.approx(speed, rel=1e-3)


def test_speed_for_range_rejects_unattainable() -> None:
    # A huge range on a tiny energy budget is not physically attainable.
    with pytest.raises(ValueError):
        speed_for_range(100000.0, 1.0, 0.035, hotel_kw=2.0)


def test_range_profile_dataclass() -> None:
    from thunderball.submersible_logistics import RangeProfile

    p = RangeProfile(
        speed_knots=5.0,
        power_kw=6.375,
        endurance_h=10.0,
        range_nm=50.0,
        optimal_speed_knots=3.0,
        optimal_range_nm=100.0,
    )
    assert p.speed_knots == 5.0
    assert p.range_nm == 50.0


def test_speed_for_range_with_no_hotel_load_uses_the_closed_form() -> None:
    """With H = 0 the cubic degenerates and the root is sqrt(E / (R k))."""
    from thunderball.submersible_logistics import speed_for_range

    v = speed_for_range(100.0, 400.0, 0.035, hotel_kw=0.0)
    assert v == pytest.approx(math.sqrt(400.0 / (100.0 * 0.035)))
    # Round-trip: the returned speed really does deliver the requested range.
    assert range_nm(400.0, v, 0.035, 0.0) == pytest.approx(100.0)


def test_optimal_range_speed_requires_a_hotel_load() -> None:
    """Without a hotel load range decreases monotonically — no interior
    optimum exists, so the function must refuse rather than invent one."""
    from thunderball.submersible_logistics import optimal_range_speed

    with pytest.raises(ValueError, match="hotel_kw"):
        optimal_range_speed(400.0, 0.035, 0.0)
    # Confirm the premise: with H = 0, range really does fall with speed.
    assert range_nm(400.0, 2.0, 0.035, 0.0) > range_nm(400.0, 8.0, 0.035, 0.0)


def test_optimal_range_speed_is_the_true_maximum() -> None:
    """External check: a dense sweep must not beat the analytic optimum."""
    from thunderball.submersible_logistics import optimal_range_speed

    v_opt = optimal_range_speed(400.0, 0.035, 2.0)
    best = range_nm(400.0, v_opt, 0.035, 2.0)
    for i in range(1, 400):
        v = i * 0.05
        assert range_nm(400.0, v, 0.035, 2.0) <= best + 1e-9


def test_speed_for_range_at_the_exact_range_maximum() -> None:
    """When the requested range is exactly the achievable maximum the cubic's
    minimum touches zero and the single (double) root is that minimum."""
    from thunderball.submersible_logistics import optimal_range_speed, speed_for_range

    energy, drag, hotel = 400.0, 0.035, 2.0
    v_best = optimal_range_speed(energy, drag, hotel)
    r_max = range_nm(energy, v_best, drag, hotel)
    v = speed_for_range(r_max, energy, drag, hotel)
    assert v == pytest.approx(v_best, rel=1e-6)
    assert range_nm(energy, v, drag, hotel) == pytest.approx(r_max, rel=1e-6)
    # One nautical mile beyond the maximum is genuinely unreachable.
    with pytest.raises(ValueError, match="not attainable"):
        speed_for_range(r_max + 1.0, energy, drag, hotel)
