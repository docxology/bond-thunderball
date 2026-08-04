# Thunderball — DISCO VOLANTE Mission Software

**film:** Thunderball (1965) · **mission codename:** DISCO VOLANTE

A BOND-suite film package: deterministic special-agent mission software for
the underwater recovery of two hijacked NATO nuclear bombs. It implements
six pure domain capabilities and exposes them through the frozen
`bond_api` `MissionProvider` protocol.

## Concepts

| Module | Concept | What it computes |
|---|---|---|
| `src/thunderball/dive_planner.py` | Dive planning | Air budget (SAC × depth pressure), Bühlmann ZH-L16A 16-compartment decompression, no-decompression limits, deco stops |
| `src/thunderball/convoy_integrity.py` | NATO convoy integrity | Escort-screen angular gaps, largest-gap detection, coverage fraction, integrity score + status |
| `src/thunderball/submersible_logistics.py` | Submersible logistics | Cubic speed–power drag + hotel load, endurance, range, optimal cruise speed, mission energy |
| `src/thunderball/sonar_detection.py` | Passive sonar | Thorp absorption, transmission loss, signal excess, detection range + verdict |
| `src/thunderball/current_navigation.py` | Set-and-drift navigation | Current vectors, dead reckoning, course to steer, cross-track error, drift limits |
| `src/thunderball/interdiction_analysis.py` | Convoy interdiction | Closest point of approach (CPA/TCPA), screen penetration time, interdiction status |

`src/thunderball/mission.py` is a thin adapter wrapping these in the frozen
BOND-API `MissionProvider` (`brief` / `recon` / `plan` / `execute` / `debrief`),
and registers its domain callables as `GadgetRegistry` gadgets. The domain
modules are standalone and never import infrastructure or `bond_api`.

## Quick start

```bash
# Install (binds the bond-api path dependency)
uv sync --extra dev

# Run the full five-stage mission
uv run python scripts/run_mission.py

# Per-phase CLIs
uv run python scripts/brief.py
uv run python scripts/recon.py
uv run python scripts/plan.py
uv run python scripts/execute.py
uv run python scripts/debrief.py

# Render concept figures + hydrate manuscript tokens
uv run python scripts/render_figures.py
uv run python scripts/z_generate_manuscript_variables.py
```

## Verification

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
```

Coverage and test counts are tracked in `docs/_generated/COUNTS.md`.

## Layout

- `src/thunderball/` — six pure domain modules + `mission.py` protocol adapter + figures + manuscript variables
- `scripts/` — thin mission CLIs
- `tests/` — real-computation tests (no mocks), one file per concept plus mission/manuscript/figures/smoke
- `manuscript/` — DISCO VOLANTE manuscript (tokens computed from `config.yaml`)
- `output/` — regenerable artifacts (git-ignored)

This is a **local-only** working tree; there is no remote.
