"""Regeneration determinism: the persisted artifacts must not move with time.

The package claims regeneration is byte-identical. The manuscript-token tests
pin ``now`` to a fixed value, which proves the *math* is deterministic but says
nothing about the default path a person or a build actually runs — that path
once read ``datetime.now()`` and rewrote a different ``GENERATION_TIMESTAMP``
into ``output/data/manuscript_variables.json`` on every invocation.

So these tests run the real CLI, with no clock override, twice, separated by
more than one clock tick, and compare the written bytes. Reintroducing a wall
clock anywhere in the generated artifacts turns them red.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from thunderball.manuscript_variables import (
    generate_variables,
    generation_timestamp,
    load_mission_config,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GENERATOR = PROJECT_ROOT / "scripts" / "z_generate_manuscript_variables.py"
OUTPUT_ROOT = PROJECT_ROOT / "output"

#: Longer than the one-second resolution of an ISO stamp, so a wall-clock
#: value is guaranteed to differ between the two runs below.
TICK_S = 1.05


def _run_generator() -> None:
    """Run the real hydration CLI exactly as a person or build would."""
    result = subprocess.run(
        [sys.executable, str(GENERATOR)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def _artifact_digests() -> dict[str, str]:
    """SHA-256 of every persisted artifact under ``output/``."""
    digests: dict[str, str] = {}
    for path in sorted(OUTPUT_ROOT.rglob("*")):
        if path.is_file():
            key = str(path.relative_to(OUTPUT_ROOT))
            digests[key] = hashlib.sha256(path.read_bytes()).hexdigest()
    return digests


def test_regenerating_twice_writes_identical_bytes() -> None:
    """Two full regenerations more than a clock tick apart must agree."""
    _run_generator()
    first = _artifact_digests()
    time.sleep(TICK_S)
    _run_generator()
    second = _artifact_digests()

    # Guard the guard: a comparison over an empty output tree is vacuous.
    assert "data/manuscript_variables.json" in first
    assert len([k for k in first if k.endswith(".png")]) == 5
    assert first == second


def test_generated_json_carries_no_wall_clock_stamp() -> None:
    """The stamp that lands on disk is the committed date, not today's."""
    _run_generator()
    written = (OUTPUT_ROOT / "data" / "manuscript_variables.json").read_text(
        encoding="utf-8"
    )
    config = load_mission_config(PROJECT_ROOT)
    expected = generation_timestamp(config["paper"])
    assert f'"{expected}"' in written
    # And it is not merely coincident with the moment of the run.
    now_second = datetime.now(timezone.utc).isoformat(timespec="seconds")
    assert expected != now_second


def test_generate_variables_defaults_to_committed_config_date() -> None:
    """No-argument generation is pinned to ``paper.date``."""
    config = load_mission_config(PROJECT_ROOT)
    variables = generate_variables(project_root=PROJECT_ROOT)
    assert variables["GENERATION_TIMESTAMP"] == "2026-08-04T00:00:00+00:00"
    assert variables["GENERATION_TIMESTAMP"].startswith(config["paper"]["date"])


def test_generation_timestamp_honours_explicit_override() -> None:
    pinned = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert generation_timestamp({"date": "2026-08-04"}, pinned) == (
        "2026-01-01T00:00:00+00:00"
    )


def test_generation_timestamp_accepts_full_iso_datetime() -> None:
    assert generation_timestamp({"date": "2026-08-04T09:30:00Z"}) == (
        "2026-08-04T09:30:00+00:00"
    )


@pytest.mark.parametrize("bad", [None, "", "   ", 20260804])
def test_generation_timestamp_requires_a_committed_date(bad: object) -> None:
    with pytest.raises(ValueError, match="paper.date is required"):
        generation_timestamp({"date": bad} if bad is not None else {})


def test_generation_timestamp_rejects_unparseable_date() -> None:
    with pytest.raises(ValueError, match="not an ISO date"):
        generation_timestamp({"date": "the fourth of August"})
