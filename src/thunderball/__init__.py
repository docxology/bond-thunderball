"""Thunderball (1965) — mission codename DISCO VOLANTE.

BOND-suite film package: special-agent mission software built around three
pure domain capabilities used in the underwater recovery of two hijacked
NATO nuclear bombs:

* :mod:`thunderball.dive_planner` — scuba dive planning: air budget and
  Bühlmann ZH-L16A decompression.
* :mod:`thunderball.convoy_integrity` — NATO convoy screen analysis: gap
  detection, escort coverage, and the integrity score.
* :mod:`thunderball.submersible_logistics` — submersible range/endurance and
  optimal-speed analysis for the eponymous craft.

The protocol adapter :mod:`thunderball.mission` exposes the BOND-API
:class:`~bond_api.protocol.MissionProvider` that coordinators discover by
slug. The domain modules themselves are standalone (stdlib + numpy only) and
never import bond-api, keeping them usable in isolation.
"""

from __future__ import annotations

#: Public package identity (manuscript / provenance use this).
__version__ = "0.1.0"

from . import mission
from .convoy_integrity import (
    ConvoyStatus,
    IntegrityResult,
    assess_convoy,
    coverage_fraction,
    integrity_score,
    integrity_status,
    largest_gap,
    min_escorts_for_coverage,
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
    "ConvoyStatus",
    "DecoStop",
    "DivePlan",
    "IntegrityResult",
    "MissionEnergy",
    "RangeProfile",
    "alveolar_pressure",
    "ambient_pressure",
    "assess_convoy",
    "bottom_time_from_air",
    "buhlmann_mvalue",
    "compute_ndl",
    "coverage_fraction",
    "cylinder_gas_volume",
    "endurance_hours",
    "energy_for_mission",
    "integrity_score",
    "integrity_status",
    "largest_gap",
    "min_escorts_for_coverage",
    "mission",
    "optimal_range_speed",
    "plan_decompression",
    "power_kw",
    "range_nm",
    "speed_for_range",
    "tissue_pressure_after",
]
