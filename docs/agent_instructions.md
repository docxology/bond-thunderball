# Agent Instructions — Thunderball (DISCO VOLANTE)

Read this before modifying any file in this package. It encodes the hard rules
and the verification checklist. This is a BOND-suite film package; the
suite-level guardrails apply on top of everything here.

## Read-first protocol

1. Read this file (always).
2. Read `docs/architecture.md` before touching any `src/` or `scripts/`
   boundary — it names every module and what each one computes.
3. Read `docs/testing_philosophy.md` before writing or modifying any test. Its
   "Green is not proof" section describes a real defect this package shipped
   for two phases; do not reintroduce that class of test.
4. Consult `src/thunderball/mission.py` and the frozen protocol
   (`bond-api/src/bond_api/protocol.py`) before changing the adapter. The
   protocol is frozen — do not invent types.

## Hard rules

1. **No mocks.** No `unittest.mock`, `MagicMock`, `@patch`, or
   `create_autospec` anywhere in `tests/`. Real computation, real protocol
   types.
2. **Deterministic.** Fixed seed (7); no untracked randomness; no wall-clock in
   results. The only timestamp is `GENERATION_TIMESTAMP`, overridable via
   `--now`.
3. **Thin orchestrators.** Business logic lives in `src/thunderball/`. Scripts
   shape argv, delegate, print, and return an exit code. They contain no math
   and no `sys.path` manipulation.
4. **Domain purity.** The six concept modules (`dive_planner.py`,
   `convoy_integrity.py`, `submersible_logistics.py`, `sonar_detection.py`,
   `current_navigation.py`, `interdiction_analysis.py`) are stdlib-only and
   import neither `infrastructure.*` nor `bond_api`. Only `mission.py` adapts
   to the protocol.
5. **One copy of every formula.** If the adapter or the token generator needs a
   domain quantity, it calls the domain function. Both `mission.execute()` and
   `manuscript_variables.generate_variables()` go through `plan_dive` for the
   dive numbers — that is what stops the manuscript drifting from the mission.
6. **Computed manuscript tokens.** Every numeric result in prose is a token
   computed in `manuscript_variables.py`. Never hardcode a metric in prose. The
   cross-reference is checked in both directions.
7. **Type hints + docstrings** on all public functions. If a docstring states a
   formula, a raised exception, or a default's provenance, it must be true — a
   wrong docstring is a defect, not a cosmetic issue.
8. **Coverage gate.** `uv run pytest tests/ --cov=src --cov-fail-under=90`.

## Common pitfalls

- Run `uv sync --extra dev` on a fresh clone: `bond_api` is a local path
  dependency and this package must be installed editable for `scripts/` to
  import it. The domain core is deliberately importable without `bond_api`.
- Do **not** add a `sys.path` bootstrap module to `scripts/`. One existed, was
  imported by nothing, and `mypy src/ scripts/` cannot resolve a bare sibling
  import — it will fail the gate.
- When adding a manuscript token, add it to `generate_variables()` **and**
  reference it in prose. An orphan token fails the cross-reference check just
  as an ungenerated one does.
- When adding a figure, wire it through `render_all_figures()` and reference it
  in `03_results.md` with a `{#fig:label}`. Do not pin a figure default to a
  literal that shadows a mission parameter — compute it.
- Keep the adapter's public shape stable (`MissionProvider`, `PROVIDER`,
  `GADGETS`, `_register_film_gadgets`): bond-cli, the coordinator reconcile,
  and the orchestrator all consume it. Adding a key to `execute()`'s `results`
  dict is additive and safe.
- Do not use a bare `assert` in `src/` as a runtime check. It is stripped under
  `python -O`, and in practice such asserts are true by construction. Raise, or
  delete.

## Verification checklist (run before submitting a change)

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90 -q
grep -rn "unittest.mock\|MagicMock\|@patch\|create_autospec" tests/ || echo Clean
grep -rnE "^(from|import) infrastructure" src/thunderball/ || echo Clean
grep -rnE "^(from|import) bond_api" src/thunderball/ | grep -v "mission.py" \
  || echo "Clean — only mission.py imports bond_api"
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
uv run python scripts/z_generate_manuscript_variables.py --now 2026-01-01T00:00:00+00:00
git status --short
```

Then update `docs/_generated/COUNTS.md` from the numbers you just measured —
never from memory.
