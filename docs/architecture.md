# Architecture — Thunderball (DISCO VOLANTE)

## Layers and dependency direction

```
tests/  ->  src/thunderball/          scripts/  ->  src/thunderball/ + bond_api
                    ^                                        |
   domain core (pure, stdlib only)  <----------------------- +
                    ^
   mission.py  <-->  bond_api (frozen protocol, GadgetRegistry)
```

The dependency arrow is one-directional and strict. Nothing in the domain core
imports the layer above it, and nothing outside `mission.py` imports
`bond_api`.

## Module-by-module

### Domain core — pure math, stdlib only

No `infrastructure.*`, no `bond_api`, no `yaml`, no `matplotlib`. These are the
load-bearing, independently testable primitives.

| Module | What it computes |
|---|---|
| `dive_planner.py` | Saltwater ambient pressure and alveolar inert-gas partial pressure; cylinder free-gas volume; gas-limited bottom time from a SAC rate; the Bühlmann ZH-L16A 16-compartment tissue model (`BuhlmannModel`) with half-times and `(a, b)` coefficients; the M-value line `M(P) = P/b + a`; exponential per-compartment loading over an arbitrary `(depth, minutes)` profile; the no-decompression limit by bisection against the **surface** ascent ceiling; a bounded deterministic decompression schedule (`plan_decompression`); and `plan_dive`, which assembles a full `DivePlan` — bottom time, binding constraint, deco stops, and a gas budget that charges each stop at its own ambient pressure. |
| `convoy_integrity.py` | Angular spacings between escort bearings around the circle and the widest such spacing (`largest_gap`, bearings only — it reads no half-angle); the widest genuinely unwatched arc with its start/end bearings (`largest_uncovered_sector`, which does read the half-angle and returns 0 when the arcs overlap all the way round); unioned escort-arc coverage fraction; the pointwise `is_bearing_covered` predicate (circle-distance, seam-safe); a sigmoid gap penalty combined with coverage into a 0–1 `integrity_score`; the `ok`/`marginal`/`breached` status with a hard sector ceiling layered over it; and `min_escorts_for_coverage`, the smallest uniform screen reaching a coverage target. |
| `submersible_logistics.py` | Submerged power from a cubic speed–drag law plus a constant hotel load; endurance and range from a battery budget; the analytic optimal-range speed (`k v³ = H/2`); the inverse `speed_for_range` (bounded bisection on the range-imbalance cubic, with a closed form when there is no hotel load); and `energy_for_mission`. |
| `sonar_detection.py` | Thorp frequency-dependent seawater absorption; transmission loss as spherical spreading plus absorption; passive-sonar signal excess `SL − TL − (NL − DI) − DT`; detection range as the signal-excess zero crossing by bounded bisection; a binary detection verdict; and `assess_detection`, the combined result. |
| `current_navigation.py` | The current set/drift vector in east/north components; ground velocity as own motion plus current; dead reckoning over a duration; course-to-steer from the vector triangle (raising when the cross-track component exceeds own speed); speed made good along the track; signed cross-track error; drift distance and a recovery-radius limit check; and `assess_navigation`, the combined result. |
| `interdiction_analysis.py` | Closest point of approach in relative motion (time-to-CPA clamped to the future, CPA distance, closing rate, relative-speed magnitude); screen-penetration time as the chord across the widest inter-escort spacing; time to minimum separation from the range profile `range(t)² = d_cpa² + v_rel²(t - t_cpa)²`, infinite when the CPA never comes inside the limit; the `held`/`penetrated`/`breached` verdict as a race between that time, the penetration time, and the escort reaction time; and `assess_interdiction`, the combined assessment. |

### Protocol adapter — `mission.py`

The **only** module importing `bond_api`. It holds the flagship scenario
constants, wraps domain outputs in the frozen protocol dataclasses, and exposes
four names that downstream fleet tooling consumes:

- `MissionProvider` — the class implementing `brief` / `recon` / `plan` /
  `execute` / `debrief`, with `film = "thunderball"`.
- `PROVIDER` — the shared module-level instance the slug loader finds.
- `GADGETS` — the name → callable map a coordinator invokes by name.
- `_register_film_gadgets(registry)` — the `GadgetRegistry` hook.

**Their public shape is frozen.** `bond-cli`, the coordinator reconcile pass,
and the orchestrator import them across every film package. Deepen *inside* the
package — add domain modules, enrich `execute()`'s `results` dict — but never
rename or re-signature these four.

`execute()` contains no math of its own. Every number it reports comes from a
domain call; the dive figures come from `plan_dive`, which is also what the
manuscript token generator calls, so the two cannot drift.

### Orchestration

| Module | Role |
|---|---|
| `manuscript_variables.py` | Loads `manuscript/config.yaml`, re-runs the same domain calls the mission makes, and returns the full token → string map (live count in `docs/_generated/COUNTS.md`; do not restate it here). May import `yaml`. |
| `figures.py` | Renders the five concept figures with matplotlib into `output/figures/`. Every curve is evaluated from the domain math; figure defaults standing in for mission parameters are computed (see `_flagship_bottom_hours`), not pinned to literals. |

### scripts/

Thin CLIs, one per mission phase plus figures and token hydration. They shape
argv, delegate, print, and return an exit code. No math, and no `sys.path`
manipulation — `uv sync --extra dev` installs this package editable, which is
what makes `import thunderball` resolve.

## Forbidden patterns

| Pattern | Why |
|---|---|
| `import infrastructure` in the domain core | breaks the standalone/pure contract |
| `import bond_api` outside `mission.py` | couples pure math to the protocol |
| Business logic in `scripts/` | untestable at the coverage gate |
| `sys.path` manipulation in `scripts/` | `mypy src/ scripts/` cannot resolve a bare sibling import |
| Mocks in `tests/` | a test can pass while the math is wrong |
| Hardcoded metrics in manuscript prose | token drift |
| Re-deriving a domain quantity in an adapter | two copies of a formula drift silently — call the domain function |
| `assert` in `src/` as a runtime check | stripped under `python -O`, and usually true by construction |

## Mission lifecycle (five stages)

`brief()` declares the mission → `recon(request)` surveys the six domains →
`plan(brief)` emits six deterministic steps → `execute(plan)` runs the domain
core and returns a provenanced `MissionOutcome` → `debrief(outcome)` summarises
with standing lessons. `bond_api.protocol.run_mission` drives all five.
`execute()` is byte-identical across runs; the only timestamp anywhere in the
package is `GENERATION_TIMESTAMP`, overridable via `--now`.

## Adding a new capability

1. Add the pure function(s) to the matching domain module, or a new pure module
   if the concept is genuinely separate.
2. Add real-computation tests. Where a physical claim is involved, anchor the
   test to a published value, not to a restatement of your own formula.
3. If the mission should surface it: add a step in `plan()` and a result in
   `execute()`. Adding a `results` key is additive and safe; changing the four
   frozen names is not.
4. Register a gadget if a coordinator should invoke it by name.
5. Compute any new manuscript token in `manuscript_variables.py` and reference
   it in prose — the cross-reference gate is checked in both directions
   (`test_all_manuscript_tokens_are_generated` forward,
   `test_no_generated_token_is_orphaned` reverse), so an unused token is as
   much a failure as an ungenerated one.
6. Add a figure if visualisation is warranted, and wire it into
   `render_all_figures()`.

## Discovery contract

`bond_api.discovery.load_provider("thunderball", ...)` imports
`thunderball.mission` and looks for `MissionProvider` at module top level;
`PROVIDER` is the shared instance. The domain core is deliberately importable
without `bond_api` — `tests/test_scripts_smoke.py` asserts in a subprocess that
`import thunderball` does not pull `bond_api` into `sys.modules`.
