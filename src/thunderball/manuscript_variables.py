"""Manuscript ``{{TOKEN}}`` generation for the DISCO VOLANTE manuscript.

Every ``{{TOKEN}}`` in the manuscript prose is generated here — never
hand-authored in prose. Values come either straight from
``manuscript/config.yaml`` or are derived deterministically by re-running the
pure domain modules over those parameters (the exact same computation the
mission adapter performs), so the prose can never drift from the code.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .convoy_integrity import assess_convoy, min_escorts_for_coverage
from .dive_planner import BuhlmannModel, compute_ndl, cylinder_gas_volume
from .submersible_logistics import optimal_range_speed, range_nm

#: Manuscript config path, relative to the project root.
CONFIG_RELATIVE = Path("manuscript") / "config.yaml"


def load_mission_config(project_root: str | Path | None = None) -> dict[str, Any]:
    """Load and return the manuscript ``config.yaml`` contents.

    Args:
        project_root: Project root; defaults to the package root (parent of
            ``src/``).

    Returns:
        The parsed config mapping.

    Raises:
        FileNotFoundError: If ``config.yaml`` is missing.
        ValueError: If the file does not contain a mapping.
    """
    root = (
        Path(project_root)
        if project_root is not None
        else Path(__file__).resolve().parents[2]
    )
    config_path = root / CONFIG_RELATIVE
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise TypeError("config.yaml must contain a mapping")
    return config


def _section(config: dict[str, Any], name: str) -> dict[str, Any]:
    value = config.get(name)
    if not isinstance(value, dict):
        raise TypeError(f"config.yaml {name} section must be a mapping")
    return value


def _fmt(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}"


def generate_variables(
    config: dict[str, Any] | None = None,
    project_root: str | Path | None = None,
    now: datetime | None = None,
) -> dict[str, str]:
    """Compute the full ``{{TOKEN}} -> value`` map for the manuscript.

    Args:
        config: Pre-loaded config; defaults to :func:`load_mission_config`.
        project_root: Root used to locate ``manuscript/config.yaml``.
        now: Clock override for ``GENERATION_TIMESTAMP`` (tests pass a fixed
            value so the map is fully deterministic).

    Returns:
        Mapping of token name to rendered string value.
    """
    loaded = config if config is not None else load_mission_config(project_root)
    paper = _section(loaded, "paper")
    mission = _section(loaded, "mission")
    recovery = _section(mission, "recovery")
    screen = _section(mission, "screen")
    submersible = _section(mission, "submersible")

    depth_m = float(recovery["depth_m"])
    cylinder_capacity_l = float(recovery["cylinder_capacity_l"])
    fill_pressure_bar = float(recovery["fill_pressure_bar"])
    sac_lmin = float(recovery["sac_rate_lmin"])
    bearings = tuple(float(b) for b in screen["escort_bearings"])
    half_angle = float(screen["half_angle_deg"])
    coverage_target = float(screen["coverage_target"])
    drag = float(submersible["drag_coeff"])
    hotel_kw = float(submersible["hotel_kw"])
    energy_kwh = float(submersible["energy_kwh"])

    # Deterministic derived results — the same math the mission executes.
    model = BuhlmannModel()
    ndl = compute_ndl(depth_m, model=model)
    gas_volume = cylinder_gas_volume(cylinder_capacity_l, fill_pressure_bar)
    air_duration = gas_volume / (sac_lmin * (1.013 + 0.1 * depth_m))
    convoy = assess_convoy(bearings, half_angle)
    min_escorts = min_escorts_for_coverage(coverage_target, half_angle)
    v_opt = optimal_range_speed(energy_kwh, drag, hotel_kw)
    opt_range = range_nm(energy_kwh, v_opt, drag, hotel_kw)

    stamp = (now or datetime.now(timezone.utc)).isoformat(timespec="seconds")
    return {
        "MISSION_IDENTITY": str(paper.get("title", "thunderball")),
        "MISSION_CODENAME": str(mission.get("codename", "DISCO VOLANTE")),
        "MISSION_VERSION": str(paper.get("version", "0.1.0")),
        "CONFIG_KEYWORDS": ", ".join(str(k) for k in loaded.get("keywords", [])),
        "CONFIG_RECOVERY_DEPTH_M": _fmt(depth_m, 0),
        "CONFIG_CYLINDER_CAPACITY_L": _fmt(cylinder_capacity_l, 0),
        "CONFIG_FILL_PRESSURE_BAR": _fmt(fill_pressure_bar, 0),
        "CONFIG_SAC_LMIN": _fmt(sac_lmin, 1),
        "CONFIG_ESCORT_BEARINGS": ", ".join(_fmt(b, 0) for b in bearings),
        "CONFIG_HALF_ANGLE_DEG": _fmt(half_angle, 0),
        "CONFIG_COVERAGE_TARGET": _fmt(coverage_target, 2),
        "CONFIG_DRAG_COEFF": _fmt(drag, 3),
        "CONFIG_HOTEL_KW": _fmt(hotel_kw, 1),
        "CONFIG_ENERGY_KWH": _fmt(energy_kwh, 0),
        "RESULT_NDL_MINUTES": _fmt(ndl, 2),
        "RESULT_AIR_DURATION_MIN": _fmt(air_duration, 2),
        "RESULT_LARGEST_GAP_DEG": _fmt(convoy.largest_gap_deg, 2),
        "RESULT_COVERAGE": _fmt(convoy.coverage, 4),
        "RESULT_CONVOY_SCORE": _fmt(convoy.score, 4),
        "RESULT_CONVOY_STATUS": convoy.status.label,
        "RESULT_MIN_ESCORTS_90PCT": str(min_escorts),
        "RESULT_OPTIMAL_SPEED_KNOTS": _fmt(v_opt, 3),
        "RESULT_OPTIMAL_RANGE_NM": _fmt(opt_range, 2),
        "PYTHON_VERSION": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "GENERATION_TIMESTAMP": stamp,
    }
