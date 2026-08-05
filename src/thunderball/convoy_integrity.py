"""NATO-style nuclear convoy integrity analysis for the DISCO VOLANTE mission.

Pure domain logic — no infrastructure imports. Given the bearing angles at
which escort vessels ("the screen") sit around a protected formation, this
module computes:

* **Angular gaps** — the angular *spacing* between consecutive escort
  bearings. Spacing is a property of where the escorts sit; it says nothing
  on its own about what is watched, because it does not know the detection
  half-angle.
* **Largest-gap detection** — the widest such spacing and whether it breaches
  a mission threshold.
* **Largest uncovered sector** — the widest arc that *no* escort's detection
  cone watches. This is the half-angle-aware quantity: a screen whose arcs
  overlap has a positive largest spacing and a zero largest uncovered sector.
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
    "largest_uncovered_sector",
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
    #: Widest arc no escort watches, in degrees. Zero when the detection arcs
    #: overlap all the way round — which is the usual case for a dense screen,
    #: and is *not* the same as ``largest_gap_deg``.
    uncovered_sector_deg: float
    coverage: float
    score: float
    status: ConvoyStatus


@dataclass(frozen=True)
class ConvoyStatus:
    """Categorical readiness: ``ok``, ``marginal``, or ``breached``."""

    label: str
    detail: str


def angular_gaps(bearings_deg: tuple[float, ...]) -> tuple[float, ...]:
    """Angular spacings (degrees) between consecutive escorts around the circle.

    Bearings are normalised to ``[0, 360)``; the spacing after the last escort
    wraps back to the first. Returns one spacing per escort.

    This is bearing geometry only — it does not read any detection half-angle,
    so a positive spacing does **not** imply an unwatched sector. For the arc
    that is genuinely unwatched, use :func:`largest_uncovered_sector`.
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
    """Return ``(gap_deg, start_deg, end_deg)`` of the widest escort *spacing*.

    The widest angular interval between two adjacent escort bearings. It takes
    no half-angle argument and therefore cannot say whether that interval is
    watched: with eight escorts 45° apart and a 30° half-angle the widest
    spacing is 45° while the uncovered sector is 0°. Use
    :func:`largest_uncovered_sector` for the unwatched arc.
    """
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


def _merged_cover(
    bearings_deg: tuple[float, ...], half_angle_deg: float
) -> list[tuple[float, float]]:
    """Union of the escorts' detection arcs as sorted intervals in ``[0, 360]``.

    Arcs crossing the 0/360 seam are split into two intervals, so the result is
    a disjoint, ascending cover of the compass. Single source of the union
    geometry: both :func:`coverage_fraction` and
    :func:`largest_uncovered_sector` read it, so they cannot disagree.
    """
    half = abs(half_angle_deg)
    if half >= FULL_CIRCLE / 2.0:
        return [(0.0, FULL_CIRCLE)]
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
    return merged


def coverage_fraction(
    bearings_deg: tuple[float, ...], half_angle_deg: float = 30.0
) -> float:
    """Fraction of the 360° perimeter an escort screen defends.

    Each escort covers an arc of ``2 * half_angle_deg`` around its bearing;
    overlapping arcs are unioned. Returns a value in ``[0, 1]``.
    """
    if not bearings_deg:
        return 0.0
    total = sum(
        end - start for start, end in _merged_cover(bearings_deg, half_angle_deg)
    )
    return min(1.0, total / FULL_CIRCLE)


def largest_uncovered_sector(
    bearings_deg: tuple[float, ...], half_angle_deg: float = 30.0
) -> tuple[float, float, float]:
    """Return ``(size_deg, start_deg, end_deg)`` of the widest *unwatched* arc.

    Unlike :func:`largest_gap`, this reads ``half_angle_deg``: it takes the
    union of the escorts' detection arcs and returns the widest hole in it,
    joining a hole that runs across the 0/360 seam. ``0.0`` means every bearing
    is watched by at least one escort — the arcs overlap and there is no
    uncovered sector at all, whatever the escort spacing is.

    An empty screen watches nothing, so it returns the full circle.
    """
    if not bearings_deg:
        return FULL_CIRCLE, 0.0, FULL_CIRCLE
    merged = _merged_cover(bearings_deg, half_angle_deg)
    holes: list[tuple[float, float]] = []
    prev_end = 0.0
    for start, end in merged:
        if start > prev_end:
            holes.append((prev_end, start))
        prev_end = max(prev_end, end)
    if prev_end < FULL_CIRCLE:
        holes.append((prev_end, FULL_CIRCLE))
    if not holes:
        return 0.0, 0.0, 0.0
    if len(holes) > 1 and holes[0][0] == 0.0 and holes[-1][1] == FULL_CIRCLE:
        # The first and last holes are one arc running across the 0/360 seam.
        first = holes.pop(0)
        last = holes.pop()
        holes.append((last[0], first[1] + FULL_CIRCLE))
    size, start = max((end - start, start) for start, end in holes)
    if size >= FULL_CIRCLE:
        return FULL_CIRCLE, 0.0, FULL_CIRCLE
    return size, start % FULL_CIRCLE, (start + size) % FULL_CIRCLE


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

    Reports both angular quantities, which are different things:
    ``largest_gap_deg`` is the widest *spacing* between adjacent escorts (no
    half-angle involved) and drives the score, while ``uncovered_sector_deg``
    is the widest arc no escort actually watches — ``0.0`` whenever the
    detection arcs overlap all the way round.

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
    uncovered, _, _ = largest_uncovered_sector(bearings_deg, half_angle_deg)
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
        uncovered_sector_deg=uncovered,
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
