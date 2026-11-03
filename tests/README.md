# tests/ — the suite that proves the mathematics

One module per capability, plus the protocol adapter, determinism, figure, prose-integrity and CLI
gates — and no mocks anywhere. The doctrine and its reason are in
[`docs/testing_philosophy.md`](../docs/testing_philosophy.md): a mock-based test can pass while the
algorithm is wrong, so every test here computes a real result and asserts it.

| Module | Subject |
| --- | --- |
| `test_dive_planner.py` | Air budget and Bühlmann ZH-L16A decompression |
| `test_convoy_integrity.py` | Escort-screen gaps, coverage and the integrity score |
| `test_submersible_logistics.py` | Power, endurance, range, energy |
| `test_sonar_detection.py` | The Thorp-absorption sonar model |
| `test_current_navigation.py` | Set-and-drift underwater navigation |
| `test_interdiction_analysis.py` | CPA geometry and the screen verdict |
| `test_nan_rejection.py` | Negative controls: NaN must never propagate silently through a domain module |
| `test_mission.py` | The `bond_api` `MissionProvider` adapter |
| `test_manuscript_variables.py` | `{{TOKEN}}` generation and the live cross-reference to the manuscript |
| `test_manuscript_lint.py` | Two prose-integrity gates (V1 and V4 in `TODO.md`) |
| `test_figures.py` | Figure generation and the rendering orchestrator |
| `test_regeneration_determinism.py` | The determinism claim, by running the real generator twice |
| `test_scripts_smoke.py` | The thin mission CLIs, in subprocesses |

## What the suite is for

It is the only gate this repository has: there is no `.github/` directory, so no CI runs it. What it
carries is arithmetic (the six domain modules), protocol (the adapter), determinism (the generator run
twice, compared as bytes), purity (the pure-core import probe and the CLI smoke tests, both in real
subprocesses), and prose integrity (a measured figure in agent-facing prose is treated as decayed, and
every manuscript cross-reference and citation key must resolve).

## Where to go next

`docs/testing_philosophy.md` for the doctrine; `conftest.py` for the two things every invocation
depends on (an `Agg` matplotlib backend, and `src/` on `sys.path`); `docs/_generated/COUNTS.md` for
the current counts and coverage, which are regenerated rather than quoted anywhere in prose.
