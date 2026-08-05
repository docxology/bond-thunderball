"""Passive sonar detection model for the DISCO VOLANTE underwater recovery.

Pure domain logic — no infrastructure imports. Implements the standard
passive-sonar range equation over a deterministic scenario:

* **Thorp absorption** — the classical frequency-dependent seawater
  attenuation coefficient (dB/km).
* **Transmission loss** — spherical spreading plus absorption, in nautical
  miles.
* **Signal excess** — ``SL - TL - (NL - DI) - DT``; the passive sonar
  equation's detection margin.
* **Detection range** — the range at which signal excess crosses zero,
  located by bounded bisection (no generic solver).
* **Detection verdict** — a deterministic binary classification from the
  signal-excess sign.

All arithmetic is deterministic math over explicit floats; there is no
randomness and no wall-clock dependence.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = [
    "SonarResult",
    "assess_detection",
    "detection_range_nm",
    "detection_verdict",
    "signal_excess",
    "thorp_absorption",
    "transmission_loss",
]

#: Nautical miles per kilometre (1.852 km per nm).
KM_PER_NM = 1.852
#: Default detection threshold (dB) — the passive sonar equation's DT term.
DEFAULT_DT_DB = 10.0


@dataclass(frozen=True)
class SonarResult:
    """A deterministic passive-sonar detection assessment."""

    range_nm: float
    signal_excess_db: float
    verdict: str


def thorp_absorption(f_khz: float) -> float:
    """Seawater absorption coefficient (dB/km) at ``f_khz`` (Thorp, 1967).

    The standard low-frequency Thorp formula:
    ``alpha = 0.11 f²/(1+f²) + 44 f²/(4100+f²) + 2.75e-4 f² + 0.003``.
    """
    _require_positive(f_khz, "f_khz")
    f2 = f_khz * f_khz
    return float(
        0.11 * f2 / (1.0 + f2) + 44.0 * f2 / (4100.0 + f2) + 2.75e-4 * f2 + 0.003
    )


def transmission_loss(range_nm: float, f_khz: float) -> float:
    """Spherical-spreading + absorption loss (dB) at ``range_nm`` (nm)."""
    _require_positive(range_nm, "range_nm")
    _require_positive(f_khz, "f_khz")
    r_km = range_nm * KM_PER_NM
    return float(20.0 * math.log10(r_km) + thorp_absorption(f_khz) * r_km)


def signal_excess(
    sl_db: float,
    tl_db: float,
    nl_db: float,
    di_db: float,
    dt_db: float = DEFAULT_DT_DB,
) -> float:
    """Passive sonar signal excess (dB): ``SL - TL - (NL - DI) - DT``."""
    return float(sl_db - tl_db - (nl_db - di_db) - dt_db)


def detection_range_nm(
    sl_db: float,
    nl_db: float,
    di_db: float,
    f_khz: float,
    dt_db: float = DEFAULT_DT_DB,
    max_range_nm: float = 120.0,
    min_range_nm: float = 0.01,
) -> float:
    """Range (nm) at which the passive-sonar signal excess crosses zero.

    Args:
        sl_db: Source level (dB re 1 µPa @ 1 m).
        nl_db: Ambient noise level (dB re 1 µPa).
        di_db: Directivity index (dB).
        f_khz: Frequency (kHz) driving Thorp absorption.
        dt_db: Detection threshold (dB).
        max_range_nm: Upper bound of the bisection window.
        min_range_nm: Lower bound; detection closer than this reports 0 nm.

    Returns:
        The detection range: ``max_range_nm`` when the target is still
        detectable at the window edge, ``0.0`` when the detection budget is
        non-positive or the signal never clears the threshold at ``min_range``,
        otherwise the zero-crossing range.

    Raises:
        ValueError: If a positive numeric argument is non-positive.
    """
    _require_positive(sl_db, "sl_db")
    _require_positive(nl_db, "nl_db")
    _require_nonneg(di_db, "di_db")
    _require_positive(f_khz, "f_khz")
    _require_positive(max_range_nm, "max_range_nm")
    budget = sl_db - (nl_db - di_db) - dt_db
    if budget <= 0.0:
        return 0.0
    if transmission_loss(min_range_nm, f_khz) >= budget:
        return 0.0
    if transmission_loss(max_range_nm, f_khz) <= budget:
        return max_range_nm
    lo, hi = min_range_nm, max_range_nm
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if transmission_loss(mid, f_khz) < budget:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def detection_verdict(signal_excess_db: float) -> str:
    """Deterministic binary detection verdict from the signal-excess sign."""
    return "detected" if signal_excess_db >= 0.0 else "not_detected"


def assess_detection(
    sl_db: float,
    nl_db: float,
    di_db: float,
    f_khz: float,
    range_nm: float,
    dt_db: float = DEFAULT_DT_DB,
    max_range_nm: float = 120.0,
) -> SonarResult:
    """Full passive-sonar assessment at ``range_nm`` for the given scenario."""
    tl = transmission_loss(range_nm, f_khz)
    se = signal_excess(sl_db, tl, nl_db, di_db, dt_db)
    return SonarResult(
        range_nm=detection_range_nm(sl_db, nl_db, di_db, f_khz, dt_db, max_range_nm),
        signal_excess_db=se,
        verdict=detection_verdict(se),
    )


def _require_positive(value: float, label: str) -> None:
    if not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{label} must be a positive number")


def _require_nonneg(value: float, label: str) -> None:
    if not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{label} must be a non-negative number")
