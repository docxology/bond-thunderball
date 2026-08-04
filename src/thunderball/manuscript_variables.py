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
from .current_navigation import assess_navigation
from .dive_planner import BuhlmannModel, compute_ndl, cylinder_gas_volume
from .interdiction_analysis import assess_interdiction
from .sonar_detection import detection_range_nm
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
    sonar = _section(mission, "sonar")
    navigation = _section(mission, "navigation")
    interdiction = _section(mission, "interdiction")

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

    f_khz = float(sonar["f_khz"])
    sl_db = float(sonar["sl_db"])
    nl_db = float(sonar["nl_db"])
    di_db = float(sonar["di_db"])
    dt_db = float(sonar["dt_db"])
    max_range_nm = float(sonar["max_range_nm"])

    track_deg = float(navigation["track_deg"])
    nav_speed = float(navigation["speed_knots"])
    set_deg = float(navigation["current_set_deg"])
    drift_knots = float(navigation["current_drift_knots"])
    recovery_radius = float(navigation["recovery_radius_nm"])

    convoy_course = float(interdiction["convoy_course_deg"])
    convoy_speed = float(interdiction["convoy_speed_knots"])
    threat_pos_list = interdiction["threat_position"]
    threat_position = (
        float(threat_pos_list[0]),
        float(threat_pos_list[1]),
    )
    threat_course = float(interdiction["threat_course_deg"])
    threat_speed = float(interdiction["threat_speed_knots"])
    screen_radius = float(interdiction["screen_radius_nm"])
    min_separation = float(interdiction["min_separation_nm"])
    reaction_h = float(interdiction["reaction_time_h"])

    # Deterministic derived results — the same math the mission executes.
    model = BuhlmannModel()
    ndl = compute_ndl(depth_m, model=model)
    gas_volume = cylinder_gas_volume(cylinder_capacity_l, fill_pressure_bar)
    air_duration = gas_volume / (sac_lmin * (1.013 + 0.1 * depth_m))
    convoy = assess_convoy(bearings, half_angle)
    min_escorts = min_escorts_for_coverage(coverage_target, half_angle)
    v_opt = optimal_range_speed(energy_kwh, drag, hotel_kw)
    opt_range = range_nm(energy_kwh, v_opt, drag, hotel_kw)

    sonar_range = detection_range_nm(sl_db, nl_db, di_db, f_khz, dt_db, max_range_nm)

    bottom_hours = air_duration / 60.0
    nav = assess_navigation(
        desired_track_deg=track_deg,
        speed_knots=nav_speed,
        set_deg=set_deg,
        drift_knots=drift_knots,
        duration_h=bottom_hours,
        recovery_radius_nm=recovery_radius,
    )

    interdiction_result = assess_interdiction(
        own_position=(0.0, 0.0),
        own_course_deg=convoy_course,
        own_speed_knots=convoy_speed,
        threat_position=threat_position,
        threat_course_deg=threat_course,
        threat_speed_knots=threat_speed,
        gap_deg=convoy.largest_gap_deg,
        screen_radius_nm=screen_radius,
        min_separation_nm=min_separation,
        reaction_time_h=reaction_h,
    )

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
        "CONFIG_SONAR_F_KHZ": _fmt(f_khz, 1),
        "CONFIG_SONAR_SL_DB": _fmt(sl_db, 0),
        "CONFIG_SONAR_NL_DB": _fmt(nl_db, 0),
        "CONFIG_SONAR_DI_DB": _fmt(di_db, 0),
        "CONFIG_NAV_TRACK_DEG": _fmt(track_deg, 0),
        "CONFIG_NAV_SPEED_KNOTS": _fmt(nav_speed, 1),
        "CONFIG_CURRENT_SET_DEG": _fmt(set_deg, 0),
        "CONFIG_CURRENT_DRIFT_KNOTS": _fmt(drift_knots, 2),
        "CONFIG_RECOVERY_RADIUS_NM": _fmt(recovery_radius, 1),
        "CONFIG_THREAT_COURSE_DEG": _fmt(threat_course, 0),
        "CONFIG_THREAT_SPEED_KNOTS": _fmt(threat_speed, 1),
        "CONFIG_SCREEN_RADIUS_NM": _fmt(screen_radius, 1),
        "CONFIG_ESCORT_REACTION_H": _fmt(reaction_h, 2),
        "RESULT_NDL_MINUTES": _fmt(ndl, 2),
        "RESULT_AIR_DURATION_MIN": _fmt(air_duration, 2),
        "RESULT_LARGEST_GAP_DEG": _fmt(convoy.largest_gap_deg, 2),
        "RESULT_COVERAGE": _fmt(convoy.coverage, 4),
        "RESULT_CONVOY_SCORE": _fmt(convoy.score, 4),
        "RESULT_CONVOY_STATUS": convoy.status.label,
        "RESULT_MIN_ESCORTS_90PCT": str(min_escorts),
        "RESULT_OPTIMAL_SPEED_KNOTS": _fmt(v_opt, 3),
        "RESULT_OPTIMAL_RANGE_NM": _fmt(opt_range, 2),
        "RESULT_SONAR_RANGE_NM": _fmt(sonar_range, 2),
        "RESULT_NAV_DRIFT_NM": _fmt(nav.drift_nm, 3),
        "RESULT_NAV_HEADING_DEG": _fmt(nav.heading_to_steer_deg, 2),
        "RESULT_NAV_GROUND_SPEED_KNOTS": _fmt(nav.ground_speed_knots, 3),
        "RESULT_NAV_WITHIN_RECOVERY": "yes" if not nav.drift_exceeds_recovery else "no",
        "RESULT_CPA_DIST_NM": _fmt(interdiction_result.d_cpa_nm, 3),
        "RESULT_CPA_TIME_H": _fmt(interdiction_result.t_cpa_h, 4),
        "RESULT_CLOSING_KNOTS": _fmt(interdiction_result.closing_knots, 2),
        "RESULT_PENETRATION_H": _fmt(interdiction_result.penetration_time_h, 4),
        "RESULT_INTERDICTION_STATUS": interdiction_result.status,
        "PYTHON_VERSION": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "GENERATION_TIMESTAMP": stamp,
    }
