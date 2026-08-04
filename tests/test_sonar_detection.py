"""Tests for the passive-sonar detection domain (Thorp absorption model)."""

from __future__ import annotations

import math

import pytest

from thunderball.sonar_detection import (
    assess_detection,
    detection_range_nm,
    detection_verdict,
    signal_excess,
    thorp_absorption,
    transmission_loss,
)


def test_thorp_absorption_is_positive_and_increasing() -> None:
    a_low = thorp_absorption(1.0)
    a_high = thorp_absorption(20.0)
    assert a_low > 0.0
    assert a_high > a_low


def test_thorp_absorption_low_frequency_baseline() -> None:
    # At f -> 0 the absorption tends to the 0.003 dB/km floor.
    assert thorp_absorption(0.1) == pytest.approx(0.003, abs=0.005)


def test_thorp_absorption_rejects_nonpositive() -> None:
    with pytest.raises(ValueError):
        thorp_absorption(0.0)
    with pytest.raises(ValueError):
        thorp_absorption(-5.0)


def test_transmission_loss_at_one_nm_is_spreading_only() -> None:
    # 20 log10(1.852) — at 1 nm the absorption term is small and the
    # spreading term dominates.
    assert transmission_loss(1.0, 1.0) == pytest.approx(
        20.0 * math.log10(1.852), abs=0.2
    )


def test_transmission_loss_increases_with_range() -> None:
    assert transmission_loss(40.0, 10.0) > transmission_loss(10.0, 10.0)


def test_transmission_loss_increases_with_frequency() -> None:
    assert transmission_loss(20.0, 20.0) > transmission_loss(20.0, 2.0)


def test_transmission_loss_rejects_bad_args() -> None:
    with pytest.raises(ValueError):
        transmission_loss(0.0, 10.0)
    with pytest.raises(ValueError):
        transmission_loss(10.0, 0.0)


def test_signal_excess_formula() -> None:
    assert signal_excess(150.0, 50.0, 75.0, 15.0, 10.0) == pytest.approx(
        150 - 50 - (75 - 15) - 10
    )


def test_signal_excess_decreases_with_range() -> None:
    near = signal_excess(150.0, transmission_loss(5.0, 10.0), 75.0, 15.0, 10.0)
    far = signal_excess(150.0, transmission_loss(50.0, 10.0), 75.0, 15.0, 10.0)
    assert far < near


def test_detection_range_between_edges() -> None:
    r = detection_range_nm(150.0, 75.0, 15.0, 10.0, 10.0, 120.0)
    assert 15.0 < r < 40.0


def test_detection_range_improves_with_source_level() -> None:
    quiet = detection_range_nm(140.0, 75.0, 15.0, 10.0, 10.0, 120.0)
    loud = detection_range_nm(160.0, 75.0, 15.0, 10.0, 10.0, 120.0)
    assert loud > quiet


def test_detection_range_shrinks_with_noise() -> None:
    quiet_sea = detection_range_nm(150.0, 65.0, 15.0, 10.0, 10.0, 120.0)
    noisy_sea = detection_range_nm(150.0, 90.0, 15.0, 10.0, 10.0, 120.0)
    assert noisy_sea < quiet_sea


def test_detection_range_zero_when_budget_nonpositive() -> None:
    # NL high enough that SL - (NL - DI) - DT <= 0: never detectable.
    assert detection_range_nm(100.0, 110.0, 5.0, 10.0, 10.0, 120.0) == 0.0


def test_detection_range_zero_when_min_range_already_above_budget() -> None:
    # With the bisection window raised to 10 nm, even the near edge already
    # exceeds the detection budget (very high absorption at 100 kHz).
    assert (
        detection_range_nm(120.0, 60.0, 0.0, 100.0, 10.0, 120.0, min_range_nm=10.0)
        == 0.0
    )


def test_detection_range_clamps_to_max_when_still_detectable() -> None:
    # Extremely loud source at low frequency: still detectable at window edge.
    r = detection_range_nm(180.0, 60.0, 10.0, 1.0, 10.0, 30.0)
    assert r == pytest.approx(30.0)


def test_detection_range_validates_arguments() -> None:
    with pytest.raises(ValueError):
        detection_range_nm(0.0, 75.0, 15.0, 10.0, 10.0, 120.0)
    with pytest.raises(ValueError):
        detection_range_nm(150.0, 0.0, 15.0, 10.0, 10.0, 120.0)
    with pytest.raises(ValueError):
        detection_range_nm(150.0, 75.0, -1.0, 10.0, 10.0, 120.0)
    with pytest.raises(ValueError):
        detection_range_nm(150.0, 75.0, 15.0, 0.0, 10.0, 120.0)


def test_detection_verdict_both_branches() -> None:
    assert detection_verdict(5.0) == "detected"
    assert detection_verdict(-0.1) == "not_detected"
    assert detection_verdict(0.0) == "detected"


def test_assess_detection_canonical() -> None:
    result = assess_detection(150.0, 75.0, 15.0, 10.0, range_nm=10.0)
    assert result.verdict == "detected"
    assert result.signal_excess_db > 0.0
    assert result.range_nm > 0.0


def test_assess_detection_not_detected_at_extreme_range() -> None:
    result = assess_detection(150.0, 75.0, 15.0, 10.0, range_nm=80.0)
    assert result.verdict == "not_detected"
    assert result.signal_excess_db < 0.0
