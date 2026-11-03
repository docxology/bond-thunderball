# src/ — agent guidance

`src/thunderball/`, the installable package. The reader's view is [README.md](README.md); this file is
what to know before editing here. The repository-wide contract, the guardrails and the build recipe
live in [the root guide](../AGENTS.md) — read that first, then
[`docs/agent_instructions.md`](../docs/agent_instructions.md) and
[`docs/architecture.md`](../docs/architecture.md). This file does not restate them.

## Rules that hold inside this directory

1. **Domain purity.** The six capability modules (`dive_planner`, `convoy_integrity`,
   `submersible_logistics`, `sonar_detection`, `current_navigation`, `interdiction_analysis`) stay
   stdlib-only: no `infrastructure.*`, no `bond_api`. `mission.py` is the single boundary crossing.
2. **`mission.py` holds no mathematics.** It adapts the frozen protocol to the core; a formula it
   computes itself is misplaced, because the same numbers also reach the manuscript through
   `manuscript_variables.py`.
3. **Determinism is structural.** No `datetime`, wall-clock, unseeded RNG or temporary-path
   dependence in generated artifacts; `GENERATION_TIMESTAMP` comes from the committed `paper.date`.
   `tests/test_regeneration_determinism.py` holds this by running the real generator twice.
4. **Stay out of the frozen protocol.** `MissionProvider`, `PROVIDER`, `GADGETS` and
   `_register_film_gadgets` keep their names and signatures — bond-cli, the coordinator reconcile and
   the orchestrator consume them across packages. Adding a key to `execute()`'s `results` dict is
   additive and safe.
5. **Orchestration belongs in `scripts/`, not here.** A phase CLI that computes something is
   misplaced; a pure module that bootstraps `sys.path` is too.

## Check before you commit

```bash
python -m pytest tests/ -q --cov=src --cov-fail-under=90
```

Run from the repository root at `c066bfa` on **2026-11-03**, this passed in full and reached the
floor. The counts and coverage it produced are regenerated into
[`docs/_generated/COUNTS.md`](../docs/_generated/COUNTS.md) and are deliberately not repeated here:
this package treats a measured figure in prose as a figure that has already decayed, and a count in
two places is the second one that goes wrong. The floor is a gate, not a target
(`[tool.coverage.report] fail_under` in `pyproject.toml`).

The repository's own guardrail greps, run at the same head rather than quoted:

| Command | Result |
| --- | --- |
| `grep -rn "unittest.mock\|MagicMock\|@patch\|create_autospec" tests/` | no match |
| `grep -rnE "^(from\|import) infrastructure" src/thunderball/` | no match |
| `grep -rnE "^(from\|import) bond_api" src/thunderball/` | only `mission.py:19` and `mission.py:32` |

## Running the suite from a worktree

`[tool.uv.sources]` pins `bond-api = { path = "../bond-api" }`, so `uv sync` resolves it from a sibling
suite checkout — present beside this repository inside the vault, absent from a worktree cut
elsewhere. A worktree has no `.venv`, so invoke an interpreter that already exists, from the parent
repository: `<canonical copy>/.venv/bin/python -m pytest tests/`. No other setting is needed, because
`pyproject.toml` sets `pythonpath = [".", "src"]`.

**Dated, and the first thing to re-check:** as of 2026-11-03 the vendoring change in this suite
replaces that path dependency with a `vendor/bond-api` directory, at which point an ordinary
`uv sync` in a worktree should resolve locally. The sentence above describes the head it was measured
at, before that change landed.

## What this directory does not have

No tests, no CI, and nothing that verifies this package except whoever runs the command above: the
repository carries no `.github/` directory. `.venv/`, `output/` and `src/*.egg-info/` are ignored
local or generated state, not sources.
