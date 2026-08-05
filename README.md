# Thunderball — DISCO VOLANTE Mission Software

**film:** Thunderball (1965) · **mission codename:** DISCO VOLANTE

A BOND-suite film package: deterministic special-agent mission software for the
underwater recovery of two hijacked NATO nuclear bombs. Six pure domain
capabilities, exposed through the frozen `bond_api` `MissionProvider` protocol.

## Film → software mapping

*Thunderball* is the Bond film that goes underwater and stays there. SPECTRE
hijacks two NATO nuclear weapons and hides them on the seabed beneath the
submersible yacht *Disco Volante*; the climax is a diver battle over the
recovery. Every quantitative question that operation raises has a module here.

| Film problem | Module | What it computes |
|---|---|---|
| How deep, and how long, can a diver work? | `src/thunderball/dive_planner.py` | Ambient and alveolar pressure, cylinder gas volume, gas-limited bottom time from a SAC rate, the Bühlmann ZH-L16A 16-compartment tissue model, the no-decompression limit against the surface ascent ceiling, a bounded decompression schedule, and `plan_dive` — the full plan with its binding constraint and a stop-pressure gas budget |
| Does the escort screen round the warheads hold? | `src/thunderball/convoy_integrity.py` | Angular gaps between escort bearings, the largest uncovered sector, unioned arc coverage, a pointwise "is this bearing watched" predicate, a sigmoid integrity score with `ok`/`marginal`/`breached` status and a hard sector ceiling, and the minimum uniform screen for a coverage target |
| How far can the submersible carry the team? | `src/thunderball/submersible_logistics.py` | Cubic speed–drag power plus hotel load, endurance, range, the analytic optimal-range speed, the range inverse by bounded bisection, and mission energy |
| Can passive sonar localise the site? | `src/thunderball/sonar_detection.py` | Thorp absorption, transmission loss (spreading + absorption), signal excess, detection range at the zero crossing, and a detection verdict |
| How far does the current sweep the divers? | `src/thunderball/current_navigation.py` | Set-and-drift vectors, ground velocity, dead reckoning, course-to-steer from the vector triangle, speed made good, signed cross-track error, and drift against a recovery radius |
| Can a closing threat be stopped before the screen? | `src/thunderball/interdiction_analysis.py` | Closest point of approach (distance, time, closing rate), screen-penetration time across the largest gap, time to minimum separation, and a `held`/`penetrated`/`breached` verdict |

Two further modules serve the manuscript rather than the mission:

| Module | Role |
|---|---|
| `src/thunderball/manuscript_variables.py` | Computes every manuscript token from `manuscript/config.yaml` plus the same domain calls the mission makes |
| `src/thunderball/figures.py` | Renders the five concept figures into `output/figures/` |

The six domain modules are stdlib-only and never import infrastructure or
`bond_api`.

## The MissionProvider surface

`src/thunderball/mission.py` is a thin adapter — no math of its own — exposing
four names the rest of the fleet consumes. **Their shape is frozen:**

```python
class MissionProvider:          # film = "thunderball"
    def brief(self) -> MissionBrief: ...
    def recon(self, request: ReconRequest) -> ReconReport: ...
    def plan(self, brief: MissionBrief) -> MissionPlan: ...
    def execute(self, plan: MissionPlan) -> MissionOutcome: ...
    def debrief(self, outcome: MissionOutcome) -> Debrief: ...

PROVIDER: MissionProvider                    # shared instance, found by slug
GADGETS: dict[str, object]                   # 6 domain callables, by name
def _register_film_gadgets(registry: GadgetRegistry) -> GadgetRegistry: ...
```

`bond-cli`, the coordinator reconcile pass, and the orchestrator import these
across every film package. `plan()` emits six deterministic steps (dive,
convoy, logistics, sonar, navigation, interdiction) whose results all land in
the outcome, alongside a `Provenance` record carrying the package version, the
fixed seed, and an input hash.

## Quick start

```bash
uv sync --extra dev            # installs this package editable + the bond-api path dep

uv run python scripts/run_mission.py        # all five stages

uv run python scripts/brief.py              # per-phase CLIs
uv run python scripts/recon.py
uv run python scripts/plan.py
uv run python scripts/execute.py
uv run python scripts/debrief.py

uv run python scripts/render_figures.py                  # concept figures
uv run python scripts/z_generate_manuscript_variables.py # manuscript tokens + figures
```

## Verification

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
```

The gate is line + branch coverage of `src/` at or above 90%, with zero
failures, zero skips, and zero mock-framework uses. The measured figures from
the last run are recorded in
[`docs/_generated/COUNTS.md`](docs/_generated/COUNTS.md) — that file is
generated output, and it is the only place a coverage number is quoted.

## Layout

- `src/thunderball/` — six pure domain modules, the `mission.py` protocol
  adapter, plus `manuscript_variables.py` and `figures.py`
- `scripts/` — thin mission CLIs (no math, no `sys.path` manipulation)
- `tests/` — real-computation tests, no mocks: one file per concept plus
  mission, manuscript, figures, and subprocess smoke tests
- `manuscript/` — the DISCO VOLANTE manuscript; every metric is a token
  computed from `config.yaml`
- `docs/` — agent-facing rules ([index](docs/README.md))
- `output/` — regenerable artifacts (git-ignored)

## Scope note

The dive model is representative, not a certified dive planner: air only, no
gradient factors, no repetitive dives. The sonar model returns a range, not a
probability of detection. See
[`manuscript/07_scope_and_related_work.md`](manuscript/07_scope_and_related_work.md)
for the full boundary.

This is a **local-only** working tree; there is no remote.
