---
name: thunderball
description: Use when working inside the Thunderball (DISCO VOLANTE) BOND film package.
version: 0.1.0
tags: [bond, film, dive-planning, convoy-integrity, submersible-logistics]
---

# Thunderball — DISCO VOLANTE Mission Software

BOND-suite film package for the 1965 *Thunderball* underwater nuclear-recovery
operation. Three pure domain capabilities exposed through the frozen
`bond_api` `MissionProvider` protocol.

## When to use

- Building/maintaining `projects/working/bond/thunderball/`.
- Extending dive planning, convoy integrity, or submersible logistics.

## Quick reference

```bash
cd projects/working/bond/thunderball
uv sync --extra dev                       # bind bond-api path dep
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
uv run python scripts/run_mission.py       # full five-stage mission
```

## Domain modules

- `src/thunderball/dive_planner.py` — air budget + Bühlmann ZH-L16A deco.
- `src/thunderball/convoy_integrity.py` — escort gaps, coverage, integrity score.
- `src/thunderball/submersible_logistics.py` — power/endurance/range/optimal speed.

`src/thunderball/mission.py` is the only `bond_api`-importing adapter (`MissionProvider`,
slug `thunderball`). Domain modules are standalone.

## Pitfalls

- Run `uv sync --extra dev` after touching `pyproject.toml`; a fresh scaffold
  venv has no deps.
- The deco planner bounds per-stop hold time; extreme dives legitimately cap.
- Domain core must stay importable without `bond-api`.
- Add manuscript tokens to `generate_variables()` and the live cross-ref test.
- Scripts need `import _bootstrap  # noqa: E402` (deep monorepo path).
