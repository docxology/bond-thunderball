# src/ — the package, and the only place the mathematics lives

`src/thunderball/` is the installable package: the domain mathematics of the *Thunderball* (1965)
mission — codename **DIS VOLANTE** — plus the three modules that turn it into manuscript tokens and
figures. Every other directory either calls into it (`scripts/`), describes it (`docs/`,
`manuscript/`) or tests it (`tests/`).

## The six capabilities

One module per capability, pure and stdlib-only, so each can be read and tested alone:

| Module | What it computes |
| --- | --- |
| `dive_planner.py` | Air budget and Bühlmann ZH-L16A decompression: 16 compartments, the M-value line, the no-decompression limit taken against the *surface* ascent ceiling, a bounded deco schedule, and `plan_dive` for the assembled plan and gas budget |
| `convoy_integrity.py` | Escort-screen gap detection, pointwise and aggregate coverage, an integrity score and status against a hard sector ceiling, minimum uniform screen size |
| `submersible_logistics.py` | Cubic drag plus hotel-load power: endurance, range, analytic optimal cruise, the range inverse |
| `sonar_detection.py` | Thorp absorption, transmission loss, signal excess, detection range |
| `current_navigation.py` | Set-and-drift dead reckoning, course to steer, cross-track error, drift limits |
| `interdiction_analysis.py` | CPA geometry, screen penetration time, interdiction status |

Three modules sit around them:

- `mission.py` — the only module in this package that imports `bond_api`. It implements the frozen
  `MissionProvider` (`PROVIDER`, `GADGETS`, `_register_film_gadgets`) and holds no mathematics of its
  own.
- `manuscript_variables.py` — hydrates the manuscript's `{{TOKEN}}` variables from
  `manuscript/config.yaml` and the demo inputs, through the domain core.
- `figures.py` — renders the five concept figures into `output/figures/`.

## How to read it

`mission.py` first, to see where the package meets the suite protocol and where the boundary crossing
is; then any one of the six capability modules, which read top to bottom as the mathematics they
implement.

## What holds this directory together

- **Purity is enforced rather than intended.** The six capability modules import neither
  `infrastructure.*` nor `bond_api`. A subprocess probe in `tests/test_scripts_smoke.py` fails if one
  of them starts to.
- **Determinism is structural.** Seed 7, no wall-clock, and the only timestamp
  (`GENERATION_TIMESTAMP`) comes from the committed `paper.date` in `manuscript/config.yaml`, so
  regeneration is byte-identical with no flag.
- **One home per formula.** `mission.execute()` and `generate_variables()` both route the dive numbers
  through `plan_dive`, so the manuscript cannot drift from the mission.
- **Manuscript metrics are injected, never typed twice.** A hand-authored figure in prose is a defect.

## What is not here

No tests (`tests/`), no command-line entry points (`scripts/`), no prose (`manuscript/`, `docs/`).
The full layer contract and the verification recipe are in [the root guide](../AGENTS.md); the
module-by-module design is in [`docs/architecture.md`](../docs/architecture.md). Neither is restated
here.
