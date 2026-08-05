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


def test_cpa_reports_the_relative_speed_magnitude() -> None:
    # Head-on: own 000 at 10 kn, threat 180 at 20 kn -> |v_rel| = 30 kn.
    cpa = closest_point_of_approach((0.0, 0.0), 0.0, 10.0, (0.0, 12.0), 180.0, 20.0)
    assert cpa.relative_speed_knots == pytest.approx(30.0)
    assert cpa.closing_knots == pytest.approx(30.0)
    assert cpa.t_cpa_h == pytest.approx(12.0 / 30.0)


def test_cpa_parallel_tracks_stationary_relative_motion() -> None:
    # Identical courses and speeds: relative velocity zero; CPA = initial
    # separation, t = 0.
    cpa = closest_point_of_approach((0.0, 0.0), 90.0, 10.0, (3.0, 4.0), 90.0, 10.0)
    assert cpa.t_cpa_h == 0.0
    assert cpa.d_cpa_nm == pytest.approx(5.0)
    assert cpa.closing_knots == pytest.approx(0.0)
    assert cpa.relative_speed_knots == pytest.approx(0.0)


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


def test_time_to_minimum_separation_matches_the_range_profile() -> None:
    """The returned time must be the instant the *real* range hits the limit.

    The oracle is the raw track geometry: step both vessels forward to the
    returned time and measure the separation directly. If the formula were the
    old margin-over-closing-rate quotient this would not land on the limit.
    """
    own = (0.0, 0.0)
    threat = (5.0, 3.0)
    cpa = closest_point_of_approach(own, 45.0, 12.0, threat, 225.0, 20.0)
    assert cpa.d_cpa_nm < 2.0  # the tracks really do come inside the limit
    t = time_to_minimum_separation(
        cpa.d_cpa_nm, cpa.t_cpa_h, cpa.relative_speed_knots, 2.0
    )
    assert 0.0 < t < cpa.t_cpa_h

    def separation_at(hours: float) -> float:
        own_e = own[0] + 12.0 * math.sin(math.radians(45.0)) * hours
        own_n = own[1] + 12.0 * math.cos(math.radians(45.0)) * hours
        thr_e = threat[0] + 20.0 * math.sin(math.radians(225.0)) * hours
        thr_n = threat[1] + 20.0 * math.cos(math.radians(225.0)) * hours
        return math.hypot(thr_e - own_e, thr_n - own_n)

    assert separation_at(t) == pytest.approx(2.0, abs=1e-9)
    # And it is the FIRST crossing: a hair earlier the threat is still outside.
    assert separation_at(t - 1e-4) > 2.0


def test_time_to_minimum_separation_is_infinite_when_the_cpa_stays_outside() -> None:
    """A CPA outside the limit means the limit is never reached — the CPA is
    by definition the smallest range the threat ever achieves."""
    assert time_to_minimum_separation(5.0, 0.4, 10.0, 1.0) == math.inf
    assert time_to_minimum_separation(1.0, 0.4, 10.0, 1.0) == math.inf


def test_time_to_minimum_separation_is_zero_when_already_inside() -> None:
    # CPA inside the limit and already in the past (t_cpa clamped to 0).
    assert time_to_minimum_separation(0.5, 0.0, 10.0, 1.0) == 0.0
    # Zero relative motion with the CPA inside the limit: there now, forever.
    assert time_to_minimum_separation(0.5, 0.0, 0.0, 1.0) == 0.0


def test_time_to_minimum_separation_validates() -> None:
    with pytest.raises(ValueError):
        time_to_minimum_separation(-1.0, 0.4, 10.0, 1.0)
    with pytest.raises(ValueError):
        time_to_minimum_separation(5.0, -0.4, 10.0, 1.0)
    with pytest.raises(ValueError):
        time_to_minimum_separation(5.0, 0.4, -10.0, 1.0)
    with pytest.raises(ValueError):
        time_to_minimum_separation(5.0, 0.4, 10.0, 0.0)


def test_interdiction_status_breached() -> None:
    # Minimum separation reached in 0.01 h, escorts need 0.05 h.
    assert interdiction_status(0.01, 0.1, 0.05, 20.0) == "breached"


def test_interdiction_status_held_when_escorts_react_in_time() -> None:
    # The threat never comes inside minimum separation (inf) and the gap chord
    # takes longer to cross than the escorts take to respond.
    assert interdiction_status(math.inf, 0.08, 0.05, 23.3) == "held"


def test_interdiction_status_held_when_diverging() -> None:
    assert interdiction_status(math.inf, 0.01, 0.05, -1.0) == "held"


def test_interdiction_status_penetrated_when_gap_crossed_first() -> None:
    # Gap crossing (0.01 h) is faster than escort reaction (0.5 h), and the
    # threat never reaches minimum separation, so this is penetration.
    assert interdiction_status(math.inf, 0.01, 0.5, 23.3) == "penetrated"


def test_interdiction_status_validates() -> None:
    with pytest.raises(ValueError):
        interdiction_status(-0.1, 0.1, 0.05, 20.0)
    with pytest.raises(ValueError):
        interdiction_status(0.1, 0.1, -0.05, 20.0)
    with pytest.raises(ValueError):
        interdiction_status(0.1, 0.0, 0.05, 20.0)


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


def test_slow_gap_crossing_holds_even_when_min_separation_is_late() -> None:
    """The penetration-time branch decides when the min-separation race is won:
    a crossing slower than the reaction time holds, a faster one penetrates."""
    assert interdiction_status(2.0, 2.0, 0.5, 100.0) == "held"
    assert interdiction_status(2.0, 0.1, 0.5, 100.0) == "penetrated"


def test_a_breach_outranks_a_penetration() -> None:
    """Both races lost: the verdict is the more severe one."""
    assert interdiction_status(0.001, 0.001, 0.5, 100.0) == "breached"
