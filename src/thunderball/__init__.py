"""Thunderball (1965) — mission codename DISCO VOLANTE.

BOND-suite film package: special-agent mission software built around six
pure domain capabilities used in the underwater recovery of two hijacked
NATO nuclear bombs:

* :mod:`thunderball.dive_planner` — scuba dive planning: air budget and
  Bühlmann ZH-L16A decompression.
* :mod:`thunderball.convoy_integrity` — NATO convoy screen analysis: gap
  detection, escort coverage, and the integrity score.
* :mod:`thunderball.submersible_logistics` — submersible range/endurance and
  optimal-speed analysis for the eponymous craft.
* :mod:`thunderball.sonar_detection` — passive sonar detection: Thorp
  absorption, transmission loss, signal excess, detection range.
* :mod:`thunderball.current_navigation` — set-and-drift underwater
  navigation: dead reckoning, course to steer, cross-track error, drift.
* :mod:`thunderball.interdiction_analysis` — convoy interdiction: closest
  point of approach, screen penetration time, interdiction status.

The protocol adapter :mod:`thunderball.mission` exposes the BOND-API
:class:`~bond_api.protocol.MissionProvider` that coordinators discover by
slug. The domain modules themselves are standalone (stdlib only) and never
import bond-api, keeping them usable in isolation.
"""

from __future__ import annotations

#: Public package identity (manuscript / provenance use this).
__version__ = "0.1.0"

# NOTE: the `mission` adapter is intentionally NOT imported here. It is the
# only module that imports bond_api; keeping it lazy means `import thunderball`
# (and any pure module) works even when the bond-api path dependency is
# unavailable. Discovery imports `thunderball.mission` explicitly.
from .convoy_integrity import (
    ConvoyStatus,
    IntegrityResult,
    assess_convoy,
    coverage_fraction,
    integrity_score,
    integrity_status,
    largest_gap,
    largest_uncovered_sector,
    min_escorts_for_coverage,
)
from .current_navigation import (
    NavAssessment,
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
from .dive_planner import (
    BuhlmannModel,
    DecoStop,
    DivePlan,
    alveolar_pressure,
    ambient_pressure,
    bottom_time_from_air,
    buhlmann_mvalue,
    compute_ndl,
    cylinder_gas_volume,
    plan_decompression,
    tissue_pressure_after,
)
from .interdiction_analysis import (
    CPAResult,
    InterdictionAssessment,
    assess_interdiction,
    closest_point_of_approach,
    interdiction_status,
    screen_penetration_time,
    time_to_minimum_separation,
)
from .sonar_detection import (
    SonarResult,
    assess_detection,
    detection_range_nm,
    detection_verdict,
    signal_excess,
    thorp_absorption,
    transmission_loss,
)
from .submersible_logistics import (
    MissionEnergy,
    RangeProfile,
    endurance_hours,
    energy_for_mission,
    optimal_range_speed,
    power_kw,
    range_nm,
    speed_for_range,
)

__all__ = [
    "BuhlmannModel",
    "CPAResult",
    "ConvoyStatus",
    "DecoStop",
    "DivePlan",
    "IntegrityResult",
    "InterdictionAssessment",
    "MissionEnergy",
    "NavAssessment",
    "RangeProfile",
    "SonarResult",
    "alveolar_pressure",
    "ambient_pressure",
    "assess_convoy",
    "assess_detection",
    "assess_interdiction",
    "assess_navigation",
    "bottom_time_from_air",
    "buhlmann_mvalue",
    "closest_point_of_approach",
    "compute_ndl",
    "course_to_steer",
    "coverage_fraction",
    "cross_track_error",
    "cylinder_gas_volume",
    "dead_reckon",
    "detection_range_nm",
    "detection_verdict",
    "drift_distance",
    "drift_exceeds_limit",
    "drift_vector",
    "endurance_hours",
    "energy_for_mission",
    "ground_speed",
    "ground_velocity",
    "integrity_score",
    "integrity_status",
    "interdiction_status",
    "largest_gap",
    "largest_uncovered_sector",
    "min_escorts_for_coverage",
    "optimal_range_speed",
    "plan_decompression",
    "power_kw",
    "range_nm",
    "screen_penetration_time",
    "signal_excess",
    "speed_for_range",
    "thorp_absorption",
    "time_to_minimum_separation",
    "tissue_pressure_after",
    "transmission_loss",
]
