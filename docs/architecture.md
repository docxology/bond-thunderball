# Architecture — Thunderball (DISCO VOLANTE)

## Layers and dependency direction

```
tests/  ->  src/thunderball/     scripts/  ->  src/thunderball/ + bond_api
                                      ^
src/thunderball/domain core        (imports only domain; no bond_api)
          ^
src/thunderball/mission.py  <-->  bond_api (frozen protocol, GadgetRegistry)
```

The dependency arrow is one-directional and strict:

* **Domain core** — `dive_planner.py`, `convoy_integrity.py`,
  `submersible_logistics.py`, `sonar_detection.py`, `current_navigation.py`,
  `interdiction_analysis.py`. Pure math, stdlib only. No `infrastructure.*`,
  no `bond_api`. These are the load-bearing, testable primitives.
* **Mission adapter** (`mission.py`) — the only module that imports
  `bond_api`. Wraps domain outputs in the frozen protocol dataclasses and
  exposes `MissionProvider` (film slug `thunderball`) at module top level for
  discovery, plus `PROVIDER`, `GADGETS`, and `_register_film_gadgets`.
* **Orchestration** (`manuscript_variables.py`, `figures.py`) — may import the
  domain core plus `yaml` / `matplotlib`. Compute tokens and figures.
* **scripts/** — thin CLIs: `sys.path` bootstrap via `_bootstrap.py`, then
  delegate to the domain/mission/figures. No math here.

## Forbidden patterns

| Pattern | Why |
|---|---|
| `import infrastructure` in domain core | breaks the standalone/pure contract |
| `import bond_api` in domain core | couples pure math to the protocol |
| Business logic in `scripts/` | impossible to unit-test at 90% coverage |
| Mocks in `tests/` | tests can pass while the math is wrong |
| Hardcoded metrics in manuscript prose | token drift |

## Mission lifecycle (five stages)

`brief()` declares the mission → `recon(request)` surveys → `plan(brief)`
produces steps → `execute(plan)` runs the domain core with provenance →
`debrief(outcome)` summarises. `run_mission` in `bond_api.protocol` drives all
five. The plan carries six deterministic steps (dive, convoy, logistics,
sonar, navigation, interdiction) whose results all land in the outcome dict.
Everything is deterministic.

## Adding a new capability (algorithm)

1. Add the pure function(s) to the matching domain module (or a new pure
   module).
2. Add real-computation tests (no mocks); keep `--cov-fail-under=90` green.
3. If the mission should surface it: expose it in `mission.py` (step +
   result) and add a gadget if a coordinator should invoke it by name.
4. Compute any new manuscript token in `manuscript_variables.py` and reference
   it in prose; add a figure if visualisation is warranted.

## Discovery contract

`src/thunderball/mission.py` must expose `MissionProvider` at module top
level under a stable name, and `PROVIDER` is the shared instance. The
`bond_api` loader imports `<slug>.mission` (here `thunderball.mission`) and
finds it. Downstream fleet tooling consumes the module-level `GADGETS` map
and `_register_film_gadgets` hook — keep their shape stable.
