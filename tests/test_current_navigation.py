"""Tests for the set-and-drift underwater navigation domain."""

from __future__ import annotations

import math

import pytest

from thunderball.current_navigation import (
    assess_navigation,
    course_to_steer,
    cross_track_error,
    dead_reckon,
    drift_distance,
    drift_exceeds_limit,
    drift_vector,
    ground_speed,
    ground_velocity,
)


def test_drift_vector_east_and_north() -> None:
    e, n = drift_vector(90.0, 0.8)
    assert e == pytest.approx(0.8)
    assert n == pytest.approx(0.0, abs=1e-12)
    e, n = drift_vector(0.0, 0.8)
    assert e == pytest.approx(0.0, abs=1e-12)
    assert n == pytest.approx(0.8)


def test_drift_vector_southeast() -> None:
    e, n = drift_vector(135.0, 1.0)
    assert e == pytest.approx(math.sqrt(0.5))
    assert n == pytest.approx(-math.sqrt(0.5))


def test_drift_vector_rejects_negative_drift() -> None:
    with pytest.raises(ValueError):
        drift_vector(90.0, -0.1)


def test_ground_velocity_adds_current() -> None:
    # Heading 000 at 4 kn with a 0.8 kn east current.
    e, n = ground_velocity(0.0, 4.0, 90.0, 0.8)
    assert e == pytest.approx(0.8)
    assert n == pytest.approx(4.0)


def test_ground_velocity_rejects_bad_speed() -> None:
    with pytest.raises(ValueError):
        ground_velocity(0.0, 0.0, 90.0, 0.8)


def test_dead_reckon_no_current_is_own_motion() -> None:
    e, n = dead_reckon(0.0, 0.0, 0.0, 4.0, 1.0, 90.0, 0.0)
    assert e == pytest.approx(0.0, abs=1e-9)
    assert n == pytest.approx(4.0)


def test_dead_reckon_with_current() -> None:
    e, n = dead_reckon(0.0, 0.0, 0.0, 4.0, 0.5, 90.0, 0.8)
    assert e == pytest.approx(0.4)
    assert n == pytest.approx(2.0)


def test_dead_reckon_rejects_negative_duration() -> None:
    with pytest.raises(ValueError):
        dead_reckon(0.0, 0.0, 0.0, 4.0, -1.0, 90.0, 0.8)


def test_course_to_steer_no_current_is_track() -> None:
    assert course_to_steer(45.0, 4.0, 0.0, 0.0) == pytest.approx(45.0)


def test_course_to_steer_corrects_for_east_current() -> None:
    # A 0.8 kn east current on a north track (000) forces a port correction.
    heading = course_to_steer(0.0, 4.0, 90.0, 0.8)
    assert heading == pytest.approx((-math.degrees(math.asin(0.8 / 4.0))) % 360.0)


def test_course_to_steer_makes_good_the_track() -> None:
    # After steering, the ground velocity direction must equal the track.
    track = 315.0
    heading = course_to_steer(track, 4.0, 90.0, 0.8)
    gs_e, gs_n = ground_velocity(heading, 4.0, 90.0, 0.8)
    ground_track = math.degrees(math.atan2(gs_e, gs_n)) % 360.0
    assert ground_track == pytest.approx(track, abs=1e-6)


def test_course_to_steer_raises_when_track_unachievable() -> None:
    # A 2.0 kn current across a 1.5 kn boat cannot be cancelled.
    with pytest.raises(ValueError):
        course_to_steer(0.0, 1.5, 90.0, 2.0)


def test_course_to_steer_rejects_bad_speed() -> None:
    with pytest.raises(ValueError):
        course_to_steer(0.0, 0.0, 90.0, 0.8)


def test_ground_speed_is_positive_and_below_own_speed_plus_current() -> None:
    gs = ground_speed(315.0, 4.0, 90.0, 0.8)
    assert gs > 0.0
    assert gs < 4.0 + 0.8


def test_cross_track_error_on_track_is_zero() -> None:
    # Position exactly along the track from the start.
    cte = cross_track_error(1.0, 1.0, 0.0, 0.0, 45.0)
    assert cte == pytest.approx(0.0, abs=1e-9)


def test_cross_track_error_sign_left_positive() -> None:
    # East of a north track (000) is to the right → negative.
    cte = cross_track_error(0.5, 1.0, 0.0, 0.0, 0.0)
    assert cte == pytest.approx(-0.5)


def test_drift_distance_and_limit() -> None:
    assert drift_distance(0.8, 0.5) == pytest.approx(0.4)
    assert drift_exceeds_limit(0.5, 0.8, 0.5) is False
    assert drift_exceeds_limit(0.3, 0.8, 0.5) is True


def test_drift_rejects_bad_args() -> None:
    with pytest.raises(ValueError):
        drift_distance(-0.8, 0.5)
    with pytest.raises(ValueError):
        drift_distance(0.8, -0.5)
    with pytest.raises(ValueError):
        drift_exceeds_limit(-1.0, 0.8, 0.5)


def test_assess_navigation_canonical() -> None:
    nav = assess_navigation(315.0, 4.0, 90.0, 0.8, 0.413, 1.0)
    assert nav.drift_nm == pytest.approx(0.8 * 0.413)
    assert nav.drift_exceeds_recovery is False
    assert nav.heading_to_steer_deg != 315.0  # a real correction exists
    assert nav.ground_speed_knots > 0.0
    assert nav.end_north_nm > 0.0  # heading north-west on the return leg


def test_assess_navigation_raises_on_bad_args() -> None:
    with pytest.raises(ValueError):
        assess_navigation(315.0, 0.0, 90.0, 0.8, 0.4, 1.0)
    with pytest.raises(ValueError):
        assess_navigation(315.0, 4.0, 90.0, 0.8, 0.4, 0.0)
