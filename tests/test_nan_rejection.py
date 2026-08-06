"""Negative-control tests: NaN must never silently propagate through the domain.

Every domain module that validates its numeric inputs now rejects NaN at the
``_require_*`` chokepoint (and rejects non-finite values for quantities that
must be finite positive). These tests pin that hardening so a future edit
cannot quietly let a NaN or +/-inf slip back into the arithmetic and produce a
"looks fine but isn't" result — e.g. a dive with NaN bottom time or a sonar
range of NaN that never raises.

The one deliberate exception is documented in ``interdiction_analysis.py``:
``time_to_minimum_separation`` legally returns +inf to mean "the limit is
never reached", and ``interdiction_status`` must keep accepting it. That
path is pinned too, so hardening the validator cannot regress it.
"""

from __future__ import annotations

import math

import pytest

import thunderball.current_navigation as cn
import thunderball.dive_planner as dp
import thunderball.interdiction_analysis as ia
import thunderball.sonar_detection as sd
import thunderball.submersible_logistics as sl


# --- dive_planner ---
def test_dive_buhlmann_mvalue_rejects_nan_and_inf():
    with pytest.raises(ValueError, match="b"):
        dp.buhlmann_mvalue(1.0, 1.0, math.nan)
    with pytest.raises(ValueError, match="b"):
        dp.buhlmann_mvalue(1.0, 1.0, math.inf)


def test_dive_bottom_time_from_air_rejects_nan():
    with pytest.raises(ValueError, match="gas_volume_l"):
        dp.bottom_time_from_air(math.nan, 20.0, 40.0)


# --- submersible_logistics ---
def test_submersible_power_rejects_nan_speed():
    with pytest.raises(ValueError, match="speed_knots"):
        sl.power_kw(math.nan, 1.0, 0.0)


def test_submersible_optimal_speed_rejects_inf():
    # Positive validators reject a non-finite argument.
    with pytest.raises(ValueError, match="energy_kwh"):
        sl.optimal_range_speed(math.inf, 0.035, 2.0)


def test_submersible_endurance_rejects_nan_energy():
    with pytest.raises(ValueError, match="energy_kwh"):
        sl.endurance_hours(math.nan, 5.0, 0.035, 2.0)


# --- sonar_detection ---
def test_sonar_thorp_absorption_rejects_nan_and_inf():
    with pytest.raises(ValueError, match="f_khz"):
        sd.thorp_absorption(math.nan)
    with pytest.raises(ValueError, match="f_khz"):
        sd.thorp_absorption(math.inf)


# --- current_navigation ---
def test_navigation_drift_distance_rejects_nan():
    with pytest.raises(ValueError, match="drift_knots"):
        cn.drift_distance(math.nan, 1.0)


def test_navigation_drift_exceeds_rejects_nan_limit():
    with pytest.raises(ValueError, match="limit_nm"):
        cn.drift_exceeds_limit(math.nan, 0.5, 1.0)


# --- interdiction_analysis ---
def test_interdiction_min_sep_rejects_nan():
    # Non-negative validators must still reject NaN...
    with pytest.raises(ValueError, match="min_separation_nm"):
        ia.time_to_minimum_separation(0.5, 0.0, 6.0, math.nan)


def test_interdiction_penetration_rejects_inf():
    # ...and positive validators reject non-finite.
    with pytest.raises(ValueError, match="speed_knots"):
        ia.screen_penetration_time(45.0, 2.0, math.inf)


def test_interdiction_status_accepts_inf_min_sep():
    """Regression: inf is a legal ``time_to_min_sep_h`` (never reached) and the
    NaN-hardened non-negative validator must not reject it."""
    assert ia.interdiction_status(math.inf, 1.0, 1.0, -5.0) == "held"
