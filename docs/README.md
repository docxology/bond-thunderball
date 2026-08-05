# docs — Thunderball (DISCO VOLANTE)

Agent-facing documentation hub for the `thunderball` BOND film package. Every
document here is a working rule for agents and developers in this package, not
background reading.

| File | Purpose |
|---|---|
| `README.md` | This navigation index |
| `AGENTS.md` | What this `docs/` tree is and the order to read it in |
| `agent_instructions.md` | Read-first hard rules, common pitfalls, verification checklist |
| `architecture.md` | Layer boundaries, module-by-module inventory of `src/`, the frozen `MissionProvider` surface, forbidden patterns, mission lifecycle |
| `testing_philosophy.md` | Zero-mock policy, the "green is not proof" rules, test-file inventory, determinism and coverage mechanics |
| `_generated/COUNTS.md` | Live test count and measured coverage (regenerated output — never hand-authored) |

## Where everything else lives

| Concern | Path |
|---|---|
| Package overview, concept mapping, quick start | `../README.md` |
| Build/test/verify commands and the layer contract | `../AGENTS.md` |
| Remaining work | `../TODO.md` |
| Mission parameters and paper metadata | `../manuscript/config.yaml` |
| Manuscript sections and bibliography | `../manuscript/` |
| Script conventions | `../scripts/AGENTS.md`, `../scripts/CONVENTIONS.md` |

## The one-paragraph version

Six pure domain modules under `src/thunderball/` compute the underwater
recovery problem — dive planning, convoy integrity, submersible logistics,
passive sonar, set-and-drift navigation, and convoy interdiction. A thin
`mission.py` adapter exposes them through the frozen `bond_api`
`MissionProvider` protocol. `manuscript_variables.py` and `figures.py` turn the
same domain calls into the manuscript's tokens and figures, so the prose cannot
drift from the code. Nothing is mocked, nothing is random, and every number in
the manuscript is computed.
