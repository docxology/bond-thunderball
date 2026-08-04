"""Subprocess smoke tests for the thin mission CLI scripts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = PROJECT_ROOT / "scripts"


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    """Run a thin CLI script with the venv python from the project root."""
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_brief_script() -> None:
    result = run_script("brief.py")
    assert result.returncode == 0
    assert "MissionBrief" in result.stdout
    assert "DISCO VOLANTE" in result.stdout


def test_recon_script_default_goal() -> None:
    result = run_script("recon.py")
    assert result.returncode == 0
    assert "[dive]" in result.stdout
    assert "[convoy]" in result.stdout


def test_recon_script_custom_goal() -> None:
    result = run_script("recon.py", "evaluate range to target")
    assert result.returncode == 0
    assert "evaluate range to target" in result.stdout


def test_plan_script() -> None:
    result = run_script("plan.py")
    assert result.returncode == 0
    assert "dive" in result.stdout
    assert "logistics" in result.stdout


def test_execute_script_reports_success() -> None:
    result = run_script("execute.py")
    assert result.returncode == 0
    assert "success=True" in result.stdout
    assert "optim" in result.stdout


def test_debrief_script_prints_lessons() -> None:
    result = run_script("debrief.py")
    assert result.returncode == 0
    assert "lessons" in result.stdout


def test_run_mission_script() -> None:
    result = run_script("run_mission.py")
    assert result.returncode == 0
    assert "success=True" in result.stdout


def test_render_figures_script_writes_output(tmp_path) -> None:
    result = run_script("render_figures.py")
    assert result.returncode == 0
    for line in result.stdout.splitlines():
        assert Path(line).exists()


def test_z_generate_manuscript_variables_writes_json(tmp_path) -> None:
    result = run_script("z_generate_manuscript_variables.py")
    assert result.returncode == 0
    json_path = PROJECT_ROOT / "output" / "data" / "manuscript_variables.json"
    if json_path.exists():
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        assert payload["MISSION_CODENAME"] == "DISCO VOLANTE"
