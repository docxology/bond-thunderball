---
name: thunderball
description: Use when working inside the Thunderball (DISCO VOLANTE) BOND film package.
version: 0.1.0
tags: [bond, film, dive-planning, convoy-integrity, submersible-logistics, passive-sonar, navigation, interdiction]
---

# Thunderball — DISCO VOLANTE Mission Software

BOND-suite film package for the 1965 *Thunderball* underwater nuclear-recovery
operation. Six pure domain capabilities exposed through the frozen `bond_api`
`MissionProvider` protocol.

## When to use

- Building or maintaining `projects/working/bond/thunderball/`.
- Extending dive planning, convoy integrity, submersible logistics, passive
  sonar, set-and-drift navigation, or convoy interdiction.

## Quick reference

```bash
cd projects/working/bond/thunderball
uv sync --extra dev                       # bind bond-api path dep, install editable
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
uv run python scripts/run_mission.py       # full five-stage mission
```

## Domain modules

- `src/thunderball/dive_planner.py` — air budget, Bühlmann ZH-L16A deco, NDL
  against the surface ascent ceiling, `plan_dive` for the assembled plan.
- `src/thunderball/convoy_integrity.py` — escort gaps, pointwise and aggregate
  coverage, integrity score with a hard sector ceiling.
- `src/thunderball/submersible_logistics.py` — power, endurance, range, optimal
  speed, range inverse.
- `src/thunderball/sonar_detection.py` — Thorp absorption, TL, signal excess,
  detection range.
- `src/thunderball/current_navigation.py` — set-and-drift dead reckoning,
  course-to-steer, cross-track error.
- `src/thunderball/interdiction_analysis.py` — CPA/TCPA geometry, penetration
  time, held/penetrated/breached status.

`src/thunderball/mission.py` is the only `bond_api`-importing adapter
(`MissionProvider`, slug `thunderball`). Domain modules are standalone.

## Pitfalls

- Run `uv sync --extra dev` after touching `pyproject.toml`; a fresh scaffold
  venv has no deps.
- Keep the four frozen names stable: `MissionProvider`, `PROVIDER`, `GADGETS`,
  `_register_film_gadgets`. Adding a `results` key is safe; renaming is not.
- Domain core must stay importable without `bond-api` (subprocess-probed).
- Do **not** add a `sys.path` bootstrap to `scripts/` — mypy cannot resolve a
  bare sibling import and the gate fails. The editable install is what makes
  `import thunderball` work.
- Add manuscript tokens to `generate_variables()` **and** reference them in a
  numbered section; the cross-reference is checked in both directions
  (forward `test_all_manuscript_tokens_are_generated`, reverse
  `test_no_generated_token_is_orphaned`).
- Never assert a formula against a restatement of itself. Anchor physical
  claims to published values — see `docs/testing_philosophy.md`.
