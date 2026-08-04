# TODO — Thunderball (DISCO VOLANTE)

## Status

Phase-2 build of the `thunderball` BOND film package is **complete** and
gated (pytest --cov-fail-under=90, ruff, mypy, lineage zero, git clean).

## Built

### Pure domain core (`src/thunderball/`)
- `dive_planner.py` — air budget (SAC × ambient pressure), Bühlmann ZH-L16A
  16-compartment decompression, NDL via binary search, deterministic deco
  schedule with a bounded ascent/off-gas loop.
- `convoy_integrity.py` — angular gaps, largest-gap detection, coverage
  fraction (interval union), sigmoid integrity score + status,
  min-escorts-for-coverage.
- `submersible_logistics.py` — cubic drag + hotel-load power, endurance,
  range, analytic optimal cruise speed, robust range-inverse (bounded
  bisection on the imbalance minimum).

### Protocol adapter
- `src/thunderball/mission.py` — `MissionProvider` (film = `thunderball`,
  codename `DISCO VOLANTE`) implementing the frozen `bond_api` protocol;
  registers domain callables as `GadgetRegistry` gadgets via
  `_register_film_gadgets`. Discoverable by slug.

### Orchestration
- `src/thunderball/manuscript_variables.py` — computed `{{TOKEN}}` map from
  `manuscript/config.yaml` + domain math (deterministic, `--now` override).
- `src/thunderball/figures.py` — `ndl_curve`, `convoy_screen`
  (polar), `submersible_range` figures.
- `scripts/` — `brief.py`, `recon.py`, `plan.py`, `execute.py`, `debrief.py`,
  `run_mission.py`, `render_figures.py`, `z_generate_manuscript_variables.py`.

### Manuscript & docs
- `manuscript/` sections rewritten for DISCO VOLANTE; `config.yaml` declares
  mission parameters. README/AGENTS/TODO/docs rewritten for this package.

## Integration points (declared)

- **`bond-api`** is a local path dependency (`[tool.uv.sources]` in
  `pyproject.toml`). Only `mission.py` imports it; the domain core remains
  importable without it.
- **Discovery**: `src/thunderball/mission.py` exposes `MissionProvider` at
  module top level (`PROVIDER`), so the orchestrator's slug-based discovery
  (`bond_api.discovery.load_provider("thunderball", ...)`) finds it.
- **Gadgets**: registered with any `bond_api.GadgetRegistry` via
  `_register_film_gadgets` (tested in `tests/test_mission.py`).

## Accepted limitations (documented in manuscript)

- ZH-L16A without gradient factors yields large conservative NDLs at great
  depth; the deco scheduler is deterministic and bounded (per-stop cap) and
  is representative, not a certified dive computer.
- Convoy metric is angular only (no range/radar weighting); logistics uses a
  first-order cubic drag model.

## Next (optional)

- Bind `bond_utilities.mission_io.record_provenance_outcome` for persistent
  outcome records once that dependency ships.
- Add mixed-gas / trimix compartments and gradient factors to the deco model.
