# TODO — Thunderball (DISCO VOLANTE)

## Status

Phase-2 (package build) and phase-4 (deep improvement) are **complete** and
gated (pytest --cov-fail-under=90, ruff, mypy, lineage zero, git clean).
Phase-4 commit: current working tree (see `git log`).

## Built

### Pure domain core (`src/thunderball/`) — six modules
- `dive_planner.py` — air budget (SAC × ambient pressure), Bühlmann ZH-L16A
  16-compartment decompression, NDL via binary search, deterministic deco
  schedule with a bounded ascent/off-gas loop.
- `convoy_integrity.py` — angular gaps, largest-gap detection, coverage
  fraction (interval union), sigmoid integrity score + status,
  min-escorts-for-coverage.
- `submersible_logistics.py` — cubic drag + hotel-load power, endurance,
  range, analytic optimal cruise speed, robust range-inverse (bounded
  bisection on the imbalance minimum).
- `sonar_detection.py` — Thorp absorption, transmission loss (spreading +
  absorption), signal excess, detection range (bounded bisection), verdict.
- `current_navigation.py` — set-and-drift vectors, ground velocity, dead
  reckoning, course to steer (vector-triangle), cross-track error, drift
  limits, full navigation assessment.
- `interdiction_analysis.py` — CPA/TCPA relative-motion geometry, screen
  penetration time (gap chord), time-to-minimum-separation, interdiction
  status (held/penetrated/breached).

### Protocol adapter
- `src/thunderball/mission.py` — `MissionProvider` (film = `thunderball`,
  codename `DISCO VOLANTE`) implementing the frozen `bond_api` protocol;
  public shape stable (`MissionProvider`, `PROVIDER`, `GADGETS`,
  `_register_film_gadgets`). Six-step plan; six domain results in
  `execute()`. Discoverable by slug.

### Orchestration
- `src/thunderball/manuscript_variables.py` — computed `{{TOKEN}}` map from
  `manuscript/config.yaml` + domain math (deterministic, `--now` override).
- `src/thunderball/figures.py` — `ndl_curve`, `convoy_screen` (polar),
  `submersible_range`, `transmission_loss`, `drift_geometry`.
- `scripts/` — `brief.py`, `recon.py`, `plan.py`, `execute.py`, `debrief.py`,
  `run_mission.py`, `render_figures.py`, `z_generate_manuscript_variables.py`.

### Manuscript & docs
- `manuscript/` sections rewritten for the six-concept DISCO VOLANTE mission;
  `config.yaml` declares dive/convoy/submersible/sonar/navigation/interdiction
  parameters; `references.bib` cites Urick (1983), Thorp (1967),
  Bowditch (2002), Buehlmann (1984). README/AGENTS/TODO/docs/metadata updated.

## Integration points (declared)

- **`bond-api`** is a local path dependency (`[tool.uv.sources]` in
  `pyproject.toml`). Only `mission.py` imports it; the domain core remains
  importable without it.
- **Discovery**: `src/thunderball/mission.py` exposes `MissionProvider` at
  module top level (`PROVIDER`), so the orchestrator's slug-based discovery
  (`bond_api.discovery.load_provider("thunderball", ...)`) finds it.
- **Gadgets**: registered with any `bond_api.GadgetRegistry` via
  `_register_film_gadgets` (tested in `tests/test_mission.py`); module-level
  `GADGETS` dict is consumed by fleet reconcile/harvest tooling.

## Accepted limitations (documented in manuscript)

- ZH-L16A without gradient factors yields large conservative NDLs at great
  depth; the deco scheduler is deterministic and bounded (per-stop cap) and
  is representative, not a certified dive computer.
- Sonar model is a deterministic passive-sonar range equation (Thorp
  absorption, spherical spreading); no multipath, scattering, or
  probabilistic fluctuation terms.
- Convoy metrics are angular (gaps/coverage) plus a single CPA-based threat
  track; no multi-target sensor fusion.

## Next (optional)

- Bind `bond_utilities.mission_io.record_provenance_outcome` for persistent
  outcome records once that dependency ships.
- Add mixed-gas / trimix compartments and gradient factors to the deco model;
  add a Marcum-Q detection-probability layer over the sonar range equation.
