"""NATO-style nuclear convoy integrity analysis for the DISCO VOLANTE mission.

Pure domain logic — no infrastructure imports. Given the bearing angles at
which escort vessels ("the screen") sit around a protected formation, this
module computes:

* **Angular gaps** — the uncovered sectors between consecutive escorts.
* **Largest-gap detection** — the single weakest sector and whether it
  breaches a mission threshold.
* **Escort coverage fraction** — what fraction of the 360° perimeter a set of
  escorts defends given each escort's detection half-angle.
* **Convoy integrity score** — a deterministic 0..1 readiness metric plus a
  categorical status, penalising both large gaps and thin overall coverage.

All arithmetic is deterministic over float degrees; no randomness.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = [
    "ConvoyStatus",
    "IntegrityResult",
    "angular_gaps",
    "assess_convoy",
    "coverage_fraction",
    "integrity_score",
    "integrity_status",
    "is_bearing_covered",
    "largest_gap",
    "min_escorts_for_coverage",
]

FULL_CIRCLE = 360.0


@dataclass(frozen=True)
class IntegrityResult:
    """A convoy integrity assessment: gaps, coverage, and the derived verdict."""

    bearings: tuple[float, ...]
    largest_gap_deg: float
    gap_start_deg: float
    gap_end_deg: float
    coverage: float
    score: float
    status: ConvoyStatus


@dataclass(frozen=True)
class ConvoyStatus:
    """Categorical readiness: ``ok``, ``marginal``, or ``breached``."""

    label: str
    detail: str


def angular_gaps(bearings_deg: tuple[float, ...]) -> tuple[float, ...]:
    """Covered-arc gaps (degrees) between consecutive escorts around the circle.

    Bearings are normalised to ``[0, 360)``; the gap after the last escort
    wraps back to the first. Returns one gap per escort.
    """
    if not bearings_deg:
        return ()
    normalized = sorted(b % FULL_CIRCLE for b in bearings_deg)
    gaps: list[float] = []
    for i in range(len(normalized)):
        nxt = normalized[(i + 1) % len(normalized)]
        gap = nxt - normalized[i]
        if i == len(normalized) - 1:
            gap += FULL_CIRCLE
        gaps.append(gap)
    return tuple(gaps)


def largest_gap(bearings_deg: tuple[float, ...]) -> tuple[float, float, float]:
    """Return ``(gap_deg, start_deg, end_deg)`` of the largest uncovered sector."""
    if not bearings_deg:
        return FULL_CIRCLE, 0.0, 360.0
    normalized = sorted(b % FULL_CIRCLE for b in bearings_deg)
    best_size = -1.0
    best_start = 0.0
    best_end = 0.0
    for i in range(len(normalized)):
        start = normalized[i]
        end = normalized[(i + 1) % len(normalized)]
        if i == len(normalized) - 1:
            end += FULL_CIRCLE
        size = end - start
        if size > best_size:
            best_size, best_start, best_end = size, start, end
    return best_size, best_start % FULL_CIRCLE, best_end % FULL_CIRCLE


def coverage_fraction(
    bearings_deg: tuple[float, ...], half_angle_deg: float = 30.0
) -> float:
    """Fraction of the 360° perimeter an escort screen defends.

    Each escort covers an arc of ``2 * half_angle_deg`` around its bearing;
    overlapping arcs are unioned. Returns a value in ``[0, 1]``.
    """
    if not bearings_deg:
        return 0.0
    half = abs(half_angle_deg)
    covered: list[tuple[float, float]] = []
    for bearing in bearings_deg:
        start = (bearing - half) % FULL_CIRCLE
        end = (bearing + half) % FULL_CIRCLE
        if start <= end:
            covered.append((start, end))
        else:
            # Arc crosses the 0/360 seam: represent as two intervals.
            covered.append((start, FULL_CIRCLE))
            covered.append((0.0, end))
    covered.sort()
    merged: list[tuple[float, float]] = []
    for start, end in covered:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    total = sum(end - start for start, end in merged)
    return min(1.0, total / FULL_CIRCLE)


def is_bearing_covered(
    bearing_deg: float,
    bearings_deg: tuple[float, ...],
    half_angle_deg: float = 30.0,
) -> bool:
    """Whether ``bearing_deg`` falls inside any escort's detection arc.

    The per-bearing companion to :func:`coverage_fraction`: that function
    returns the *aggregate* defended fraction, this one answers the pointwise
    question "is this bearing watched?" and so can be swept around the circle
    to draw the screen's actual coverage rosette.

    Angular distance is measured on the circle, so the 0/360 seam is handled
    without special-casing.
    """
    half = abs(half_angle_deg)
    target = bearing_deg % FULL_CIRCLE
    for escort in bearings_deg:
        delta = abs(target - escort % FULL_CIRCLE) % FULL_CIRCLE
        separation = min(delta, FULL_CIRCLE - delta)
        if separation <= half:
            return True
    return False


def integrity_score(largest_gap_deg: float, coverage: float) -> float:
    """Deterministic convoy readiness in ``[0, 1]``.

    High scores need small largest gaps and near-full coverage. The gap
    penalty is sigmoidal around a nominal ``60°`` screening threshold.
    """
    gap_penalty = 1.0 / (1.0 + math.exp((largest_gap_deg - 60.0) / 12.0))
    return max(0.0, min(1.0, gap_penalty * (0.5 + 0.5 * coverage)))


def integrity_status(score: float) -> ConvoyStatus:
    """Map a 0..1 integrity score to a categorical readiness verdict."""
    if score >= 0.7:
        return ConvoyStatus(
            label="ok", detail="escort screen preserves convoy integrity"
        )
    if score >= 0.4:
        return ConvoyStatus(
            label="marginal", detail="weak sector present; reinforce the screen"
        )
    return ConvoyStatus(
        label="breached", detail="unscreened sector permits interdiction"
    )


def assess_convoy(
    bearings_deg: tuple[float, ...],
    half_angle_deg: float = 30.0,
    marginal_under_deg: float = 75.0,
) -> IntegrityResult:
    """Full convoy integrity assessment over an escort screen.

    ``marginal_under_deg`` is a hard gap ceiling layered *over* the continuous
    score: a screen whose largest gap reaches it is downgraded from ``ok`` to
    ``marginal`` even when the sigmoid score would have passed it. It exists so
    a mission can impose a sector width narrower than the score's nominal 60°
    knee without retuning the score itself; it can only downgrade, never
    upgrade.

    Args:
        bearings_deg: Escort bearings (degrees true) around the formation.
        half_angle_deg: Each escort's detection half-angle (degrees).
        marginal_under_deg: Largest gap (degrees) at or above which an
            otherwise-``ok`` screen is downgraded to ``marginal``.

    Returns:
        The full :class:`IntegrityResult` for the screen.
    """
    gap, start, end = largest_gap(bearings_deg)
    coverage = coverage_fraction(bearings_deg, half_angle_deg)
    score = integrity_score(gap, coverage)
    status = integrity_status(score)
    if status.label == "ok" and gap >= marginal_under_deg:
        status = ConvoyStatus(
            label="marginal",
            detail=(
                f"largest gap {gap:.1f}deg reaches the "
                f"{marginal_under_deg:.0f}deg sector ceiling"
            ),
        )
    elif status.label == "ok":
        status = ConvoyStatus(
            label="ok",
            detail=(
                f"largest gap {gap:.1f}deg under the "
                f"{marginal_under_deg:.0f}deg sector ceiling"
            ),
        )
    return IntegrityResult(
        bearings=tuple(b % FULL_CIRCLE for b in bearings_deg),
        largest_gap_deg=gap,
        gap_start_deg=start,
        gap_end_deg=end,
        coverage=coverage,
        score=score,
        status=status,
    )


def min_escorts_for_coverage(
    coverage_target: float,
    half_angle_deg: float = 30.0,
    max_escorts: int = 48,
) -> int:
    """Smallest escort count that achieves ``coverage_target`` on a uniform screen.

    Escorts are placed evenly around the circle; returns the count whose
    :func:`coverage_fraction` first reaches the target.
    """
    if not 0.0 < coverage_target <= 1.0:
        raise ValueError("coverage_target must be in (0, 1]")
    if not 0.0 < half_angle_deg < 180.0:
        raise ValueError("half_angle_deg must be in (0, 180)")
    for n in range(1, max_escorts + 1):
        bearings = tuple(360.0 * i / n for i in range(n))
        if coverage_fraction(bearings, half_angle_deg) >= coverage_target:
            return n
    raise ValueError(f"coverage target unreachable with up to {max_escorts} escorts")
