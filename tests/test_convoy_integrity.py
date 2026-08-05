"""Tests for the convoy-integrity domain: gaps, coverage, and score."""

from __future__ import annotations

import pytest

from thunderball.convoy_integrity import (
    assess_convoy,
    coverage_fraction,
    integrity_score,
    integrity_status,
    largest_gap,
    min_escorts_for_coverage,
)


def test_angular_gaps_two_escorts() -> None:
    from thunderball.convoy_integrity import angular_gaps

    gaps = angular_gaps((0.0, 180.0))
    assert gaps == pytest.approx((180.0, 180.0))


def test_angular_gaps_wraps_full_circle() -> None:
    from thunderball.convoy_integrity import angular_gaps

    # Escorts at 0 and 350: gaps are 350 and 10 (wrapping).
    gaps = angular_gaps((0.0, 350.0))
    assert gaps == pytest.approx((350.0, 10.0))


def test_angular_gaps_empty() -> None:
    from thunderball.convoy_integrity import angular_gaps

    assert angular_gaps(()) == ()


def test_largest_gap_detects_weak_sector() -> None:
    gap, start, end = largest_gap((0.0, 60.0, 120.0, 240.0, 300.0, 350.0))
    assert gap == pytest.approx(120.0)
    assert start == pytest.approx(120.0)
    assert end == pytest.approx(240.0)


def test_largest_gap_empty_returns_full_circle() -> None:
    gap, _, _ = largest_gap(())
    assert gap == pytest.approx(360.0)


def test_coverage_fraction_single_escort() -> None:
    # One escort with half-angle 30 covers 60° of 360°.
    assert coverage_fraction((0.0,), 30.0) == pytest.approx(60.0 / 360.0)


def test_coverage_fraction_full_screen() -> None:
    # 8 evenly spaced escorts with half-angle 30 fully cover the circle.
    bearings = tuple(45.0 * i for i in range(8))
    assert coverage_fraction(bearings, 30.0) == pytest.approx(1.0)


def test_coverage_fraction_wraps_seam() -> None:
    # An escort straddling 0/360 still contributes its full arc.
    covered = coverage_fraction((350.0,), 30.0)
    assert covered == pytest.approx(60.0 / 360.0)


def test_coverage_empty() -> None:
    assert coverage_fraction((), 30.0) == 0.0


def test_integrity_score_small_gap_high_coverage_is_green() -> None:
    score = integrity_score(45.0, 1.0)
    assert score >= 0.7
    assert integrity_status(score).label == "ok"


def test_integrity_score_large_gap_is_bad() -> None:
    score = integrity_score(150.0, 0.9)
    assert score < 0.4
    assert integrity_status(score).label == "breached"


def test_integrity_status_boundaries() -> None:
    assert integrity_status(0.8).label == "ok"
    assert integrity_status(0.5).label == "marginal"
    assert integrity_status(0.2).label == "breached"


def test_assess_convoy_ok_screen() -> None:
    result = assess_convoy(tuple(45.0 * i for i in range(8)), 30.0)
    assert result.status.label == "ok"
    assert result.coverage == pytest.approx(1.0)
    assert result.largest_gap_deg == pytest.approx(45.0)
    assert result.score >= 0.7


def test_assess_convoy_breached_screen() -> None:
    result = assess_convoy((0.0, 60.0, 120.0, 240.0, 300.0, 350.0), 30.0)
    assert result.status.label == "breached"
    assert result.largest_gap_deg == pytest.approx(120.0)


def test_min_escorts_for_coverage_target() -> None:
    count = min_escorts_for_coverage(0.9, 30.0)
    assert count == 6


def test_min_escorts_rejects_bad_target() -> None:
    with pytest.raises(ValueError):
        min_escorts_for_coverage(0.0, 30.0)
    with pytest.raises(ValueError):
        min_escorts_for_coverage(1.5, 30.0)
    with pytest.raises(ValueError):
        min_escorts_for_coverage(0.9, 200.0)


def test_min_escorts_unreachable_raises() -> None:
    # A half-angle so small the target is unreachable within the cap.
    with pytest.raises(ValueError):
        min_escorts_for_coverage(1.0, 0.1, max_escorts=8)


def test_is_bearing_covered_respects_the_arc_and_the_seam() -> None:
    from thunderball.convoy_integrity import is_bearing_covered

    screen = (0.0, 90.0)
    # Inside compartment 0's +/-30 deg arc, including across the 0/360 seam.
    assert is_bearing_covered(0.0, screen, 30.0)
    assert is_bearing_covered(29.9, screen, 30.0)
    assert is_bearing_covered(350.0, screen, 30.0)
    assert is_bearing_covered(330.0, screen, 30.0)
    # Outside every arc.
    assert not is_bearing_covered(45.0, screen, 30.0)
    assert not is_bearing_covered(180.0, screen, 30.0)
    # Boundary is inclusive.
    assert is_bearing_covered(30.0, screen, 30.0)
    assert not is_bearing_covered(30.001, screen, 30.0)


def test_is_bearing_covered_agrees_with_coverage_fraction() -> None:
    """Sweeping the pointwise predicate must reproduce the aggregate fraction."""
    from thunderball.convoy_integrity import is_bearing_covered

    screen = (0.0, 45.0, 90.0, 200.0)
    samples = [i * 0.1 for i in range(3600)]
    hits = sum(1 for t in samples if is_bearing_covered(t, screen, 25.0))
    assert hits / len(samples) == pytest.approx(
        coverage_fraction(screen, 25.0), abs=2e-3
    )


def test_is_bearing_covered_on_an_empty_screen() -> None:
    from thunderball.convoy_integrity import is_bearing_covered

    assert not is_bearing_covered(10.0, (), 30.0)


def test_marginal_ceiling_downgrades_an_otherwise_ok_screen() -> None:
    """The sector ceiling must actually change the verdict, not just the text."""
    screen = (0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0)
    default = assess_convoy(screen, 30.0)
    assert default.largest_gap_deg == pytest.approx(45.0)
    assert default.status.label == "ok"
    # A ceiling below the actual 45 deg gap must downgrade the same screen.
    strict = assess_convoy(screen, 30.0, marginal_under_deg=40.0)
    assert strict.status.label == "marginal"
    assert "reaches" in strict.status.detail
    # The continuous score is untouched — only the categorical verdict moves.
    assert strict.score == pytest.approx(default.score)


def test_marginal_ceiling_can_only_downgrade_never_upgrade() -> None:
    """A wide ceiling must not rescue a screen the score already condemned."""
    breached = assess_convoy((0.0, 10.0), 30.0, marginal_under_deg=1000.0)
    assert breached.status.label == "breached"
    assert breached.largest_gap_deg == pytest.approx(350.0)
