"""Tests for the convoy-interdiction domain (CPA geometry + screen verdict)."""

from __future__ import annotations

import math

import pytest

from thunderball.interdiction_analysis import (
    assess_interdiction,
    closest_point_of_approach,
    interdiction_status,
    screen_penetration_time,
    time_to_minimum_separation,
)


def test_cpa_crossing_tracks() -> None:
    # Threat at (5, -2) heading 270 (west) at 20 kn; convoy at (0,0) heading
    # 045 at 12 kn. CPA must be finite, in the future, and positive distance.
    cpa = closest_point_of_approach((0.0, 0.0), 45.0, 12.0, (5.0, -2.0), 270.0, 20.0)
    assert cpa.t_cpa_h > 0.0
    assert cpa.d_cpa_nm > 0.0
    assert cpa.closing_knots > 0.0  # the threat is closing


def test_cpa_parallel_tracks_stationary_relative_motion() -> None:
    # Identical courses and speeds: relative velocity zero; CPA = initial
    # separation, t = 0.
    cpa = closest_point_of_approach((0.0, 0.0), 90.0, 10.0, (3.0, 4.0), 90.0, 10.0)
    assert cpa.t_cpa_h == 0.0
    assert cpa.d_cpa_nm == pytest.approx(5.0)
    assert cpa.closing_knots == pytest.approx(0.0)


def test_cpa_diverging_threat_clamps_to_now() -> None:
    # Threat already past its CPA (t < 0) is clamped to t = 0.
    cpa = closest_point_of_approach((0.0, 0.0), 0.0, 10.0, (0.0, 10.0), 0.0, 20.0)
    assert cpa.t_cpa_h == 0.0
    assert cpa.d_cpa_nm == pytest.approx(10.0)


def test_cpa_validates_speeds() -> None:
    with pytest.raises(ValueError):
        closest_point_of_approach((0.0, 0.0), 45.0, 0.0, (5.0, -2.0), 270.0, 20.0)
    with pytest.raises(ValueError):
        closest_point_of_approach((0.0, 0.0), 45.0, 12.0, (5.0, -2.0), 270.0, 0.0)


def test_screen_penetration_time_chord_formula() -> None:
    # 90-degree gap at radius 2 nm: chord = 2*2*sin(45°) = 2.828 nm.
    chord = 2.0 * 2.0 * math.sin(math.radians(90.0) / 2.0)
    assert screen_penetration_time(90.0, 2.0, 10.0) == pytest.approx(chord / 10.0)


def test_screen_penetration_time_scale() -> None:
    # A wider gap or a faster interceptor crosses faster.
    assert screen_penetration_time(45.0, 2.0, 20.0) < screen_penetration_time(
        90.0, 2.0, 20.0
    )
    assert screen_penetration_time(45.0, 2.0, 30.0) < screen_penetration_time(
        45.0, 2.0, 10.0
    )


def test_screen_penetration_time_validates() -> None:
    with pytest.raises(ValueError):
        screen_penetration_time(0.0, 2.0, 10.0)
    with pytest.raises(ValueError):
        screen_penetration_time(45.0, 0.0, 10.0)
    with pytest.raises(ValueError):
        screen_penetration_time(45.0, 2.0, 0.0)


def test_time_to_minimum_separation() -> None:
    t = time_to_minimum_separation(5.0, 10.0, 1.0)
    assert t == pytest.approx(0.4)


def test_time_to_minimum_separation_infinite_when_diverging() -> None:
    assert time_to_minimum_separation(5.0, -2.0, 1.0) == math.inf
    assert time_to_minimum_separation(0.5, 10.0, 1.0) == math.inf  # already inside


def test_time_to_minimum_separation_validates() -> None:
    with pytest.raises(ValueError):
        time_to_minimum_separation(-1.0, 10.0, 1.0)
    with pytest.raises(ValueError):
        time_to_minimum_separation(5.0, 10.0, 0.0)


def test_interdiction_status_breached() -> None:
    assert interdiction_status(0.5, 20.0, 1.0, 0.05, 0.1) == "breached"


def test_interdiction_status_held_when_escorts_react_in_time() -> None:
    # d_cpa 3.34, closing 23.3 → t_minsep = (3.34-1.0)/23.3 ≈ 0.10 h >
    # reaction 0.05 → escorts respond first.
    assert interdiction_status(3.34, 23.3, 1.0, 0.05, 0.08) == "held"


def test_interdiction_status_held_when_diverging() -> None:
    assert interdiction_status(5.0, -1.0, 1.0, 0.05, 0.1) == "held"


def test_interdiction_status_penetrated_when_gap_crossed_first() -> None:
    # Gap crossing (0.01 h) is much faster than escort reaction (0.5 h) and
    # the threat still closes before escorts respond.
    assert interdiction_status(3.34, 23.3, 1.0, 0.5, 0.01) == "penetrated"


def test_interdiction_status_validates() -> None:
    with pytest.raises(ValueError):
        interdiction_status(-0.1, 20.0, 1.0, 0.05, 0.1)
    with pytest.raises(ValueError):
        interdiction_status(3.34, 23.3, 0.0, 0.05, 0.1)
    with pytest.raises(ValueError):
        interdiction_status(3.34, 23.3, 1.0, -0.05, 0.1)
    with pytest.raises(ValueError):
        interdiction_status(3.34, 23.3, 1.0, 0.05, 0.0)


def test_assess_interdiction_canonical_held() -> None:
    result = assess_interdiction(
        own_position=(0.0, 0.0),
        own_course_deg=45.0,
        own_speed_knots=12.0,
        threat_position=(5.0, -2.0),
        threat_course_deg=270.0,
        threat_speed_knots=20.0,
        gap_deg=45.0,
        screen_radius_nm=2.0,
        min_separation_nm=1.0,
        reaction_time_h=0.05,
    )
    assert result.status == "held"
    assert result.d_cpa_nm > 1.0
    assert result.penetration_time_h > 0.0
    assert result.t_cpa_h > 0.0


def test_assess_interdiction_penetrates_slow_reaction() -> None:
    result = assess_interdiction(
        own_position=(0.0, 0.0),
        own_course_deg=45.0,
        own_speed_knots=12.0,
        threat_position=(5.0, -2.0),
        threat_course_deg=270.0,
        threat_speed_knots=20.0,
        gap_deg=45.0,
        screen_radius_nm=2.0,
        min_separation_nm=1.0,
        reaction_time_h=1.0,
    )
    assert result.status == "penetrated"


def test_assess_interdiction_breached_close_threat() -> None:
    result = assess_interdiction(
        own_position=(0.0, 0.0),
        own_course_deg=45.0,
        own_speed_knots=12.0,
        threat_position=(0.5, 0.0),
        threat_course_deg=270.0,
        threat_speed_knots=20.0,
        gap_deg=45.0,
        screen_radius_nm=2.0,
        min_separation_nm=1.0,
        reaction_time_h=0.05,
    )
    assert result.status == "breached"
