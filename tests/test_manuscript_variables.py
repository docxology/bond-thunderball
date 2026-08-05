"""Tests for manuscript ``{{TOKEN}}`` generation and the live cross-reference."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

from thunderball.manuscript_variables import (
    CONFIG_RELATIVE,
    generate_variables,
    load_mission_config,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _fixed_now() -> datetime:
    return datetime(2026, 8, 4, 12, 0, 0, tzinfo=timezone.utc)


def test_load_mission_config_returns_mapping() -> None:
    config = load_mission_config(PROJECT_ROOT)
    assert isinstance(config, dict)
    assert config["mission"]["codename"] == "DISCO VOLANTE"


def test_generate_variables_has_all_core_tokens() -> None:
    variables = generate_variables(project_root=PROJECT_ROOT, now=_fixed_now())
    for token in (
        "MISSION_IDENTITY",
        "MISSION_CODENAME",
        "CONFIG_RECOVERY_DEPTH_M",
        "RESULT_NDL_MINUTES",
        "RESULT_CONVOY_STATUS",
        "RESULT_OPTIMAL_RANGE_NM",
        "RESULT_SONAR_RANGE_NM",
        "RESULT_NAV_HEADING_DEG",
        "RESULT_INTERDICTION_STATUS",
        "PYTHON_VERSION",
        "GENERATION_TIMESTAMP",
    ):
        assert token in variables
        assert variables[token]


def test_generate_variables_from_inline_config() -> None:
    config = {
        "paper": {"title": "T", "version": "1.0"},
        "keywords": ["a", "b"],
        "mission": {
            "codename": "DISCO VOLANTE",
            "recovery": {
                "depth_m": 40,
                "cylinder_capacity_l": 12,
                "fill_pressure_bar": 207,
                "sac_rate_lmin": 20,
            },
            "screen": {
                "escort_bearings": [0, 45, 90, 135, 180, 225, 270, 315],
                "half_angle_deg": 30,
                "coverage_target": 0.9,
            },
            "submersible": {"energy_kwh": 400, "drag_coeff": 0.035, "hotel_kw": 2.0},
            "sonar": {
                "f_khz": 10.0,
                "sl_db": 150.0,
                "nl_db": 75.0,
                "di_db": 15.0,
                "dt_db": 10.0,
                "max_range_nm": 120.0,
            },
            "navigation": {
                "track_deg": 315.0,
                "speed_knots": 4.0,
                "current_set_deg": 90.0,
                "current_drift_knots": 0.8,
                "recovery_radius_nm": 1.0,
            },
            "interdiction": {
                "convoy_course_deg": 45.0,
                "convoy_speed_knots": 12.0,
                "threat_position": [5.0, -2.0],
                "threat_course_deg": 270.0,
                "threat_speed_knots": 20.0,
                "screen_radius_nm": 2.0,
                "min_separation_nm": 1.0,
                "reaction_time_h": 0.05,
            },
        },
    }
    variables = generate_variables(config=config, now=_fixed_now())
    assert variables["RESULT_CONVOY_STATUS"] == "ok"
    assert variables["RESULT_MIN_ESCORTS_90PCT"] == "6"
    assert variables["RESULT_INTERDICTION_STATUS"] == "held"
    assert float(variables["RESULT_SONAR_RANGE_NM"]) > 0.0
    assert variables["RESULT_NAV_WITHIN_RECOVERY"] == "yes"


def test_generate_variables_is_deterministic() -> None:
    v1 = generate_variables(project_root=PROJECT_ROOT, now=_fixed_now())
    v2 = generate_variables(project_root=PROJECT_ROOT, now=_fixed_now())
    assert v1 == v2


def test_generate_variables_missing_section_raises() -> None:
    with pytest.raises(TypeError):
        generate_variables(config={"paper": {}})


def test_generate_variables_missing_screen_raises() -> None:
    config = {
        "paper": {"title": "T"},
        "mission": {
            "recovery": {
                "depth_m": 40,
                "cylinder_capacity_l": 12,
                "fill_pressure_bar": 207,
                "sac_rate_lmin": 20,
            }
        },
    }
    with pytest.raises(TypeError):
        generate_variables(config=config)


def test_all_manuscript_tokens_are_generated() -> None:
    """Live cross-reference gate: every {{TOKEN}} in numbered prose sections
    must have a generated value."""
    variables = generate_variables(project_root=PROJECT_ROOT, now=_fixed_now())
    manuscript = PROJECT_ROOT / "manuscript"
    token_re = re.compile(r"\{\{([A-Z_][A-Z0-9_]*)\}\}")
    found: set[str] = set()
    for section in sorted(manuscript.glob("[0-9]*.md")):
        found.update(token_re.findall(section.read_text(encoding="utf-8")))
    for token in sorted(found):
        assert token in variables, f"manuscript token {token} has no generated value"


def test_config_relative_points_to_manuscript_config() -> None:
    assert CONFIG_RELATIVE == Path("manuscript") / "config.yaml"


def test_load_mission_config_rejects_a_non_mapping_file(tmp_path) -> None:
    """A YAML file that parses to a list must raise, and the docstring's
    documented exception type must be the one actually raised."""
    manuscript = tmp_path / "manuscript"
    manuscript.mkdir()
    (manuscript / "config.yaml").write_text("- not\n- a mapping\n", encoding="utf-8")
    with pytest.raises(TypeError, match="must contain a mapping"):
        load_mission_config(tmp_path)


def test_load_mission_config_reports_a_missing_file(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        load_mission_config(tmp_path)


def test_dive_tokens_agree_with_the_domain_core() -> None:
    """The dive tokens must be plan_dive() output, not re-derived arithmetic."""
    from thunderball.dive_planner import bottom_time_from_air, plan_dive

    variables = generate_variables(project_root=PROJECT_ROOT, now=_fixed_now())
    config = load_mission_config(PROJECT_ROOT)["mission"]["recovery"]
    dive = plan_dive(
        depth_m=float(config["depth_m"]),
        cylinder_capacity_l=float(config["cylinder_capacity_l"]),
        fill_pressure_bar=float(config["fill_pressure_bar"]),
        sac_rate_lmin=float(config["sac_rate_lmin"]),
    )
    assert float(variables["RESULT_NDL_MINUTES"]) == pytest.approx(
        dive.ndl_minutes, abs=5e-3
    )
    assert float(variables["RESULT_DIVE_BOTTOM_MIN"]) == pytest.approx(
        dive.bottom_minutes, abs=5e-3
    )
    assert variables["RESULT_DIVE_BINDING_CONSTRAINT"] == dive.binding_constraint()
    assert float(variables["RESULT_AIR_DURATION_MIN"]) == pytest.approx(
        bottom_time_from_air(
            dive.air_volume_l,
            float(config["sac_rate_lmin"]),
            float(config["depth_m"]),
        ),
        abs=5e-3,
    )
    assert float(variables["RESULT_DIVE_GAS_MARGIN_L"]) > 0.0


def test_manuscript_token_gate_actually_scans_something() -> None:
    """Guard the guard: the cross-reference test is vacuous if no section file
    is read or no token is found."""
    import re

    manuscript = PROJECT_ROOT / "manuscript"
    sections = sorted(manuscript.glob("[0-9]*.md"))
    assert len(sections) >= 9, [s.name for s in sections]
    token_re = re.compile(r"\{\{([A-Z_][A-Z0-9_]*)\}\}")
    found: set[str] = set()
    for section in sections:
        found.update(token_re.findall(section.read_text(encoding="utf-8")))
    assert len(found) >= 30, sorted(found)
