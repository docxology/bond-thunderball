# Agent Instructions — Thunderball (DISCO VOLANTE)

Read this before modifying any file in this package. It encodes the hard
rules and the verification checklist. It is part of the BOND suite; the
shared guardrails are the package-level contract.

## Read-first protocol

1. Read this file (always).
2. Read `docs/architecture.md` before touching `scripts/` or `src/`
   boundaries.
3. Read `docs/testing_philosophy.md` before writing or modifying any `pytest`
   file.
4. Consult `src/thunderball/mission.py` + the frozen `bond_api` protocol
   (`bond-api/src/bond_api/protocol.py`) before changing the mission adapter —
   the protocol is frozen; do not invent types.

## Hard rules

1. **No mocks.** No `unittest.mock`, `MagicMock`, `@patch`, or
   `create_autospec` anywhere in `tests/`. Tests use real computation and
   real `bond_api` protocol types. A mock test can pass while the domain math
   is wrong; these tests prove the math.
2. **Deterministic.** Fixed seed; no untracked random reliance; no wall-clock
   in persisted results. The only timestamp is `GENERATION_TIMESTAMP`,
   overridable via `--now`.
3. **Thin orchestrators.** Business logic lives in `src/thunderball/`. Scripts
   in `scripts/` bootstrap `sys.path` and delegate; they do not contain math.
4. **Domain purity.** `dive_planner.py`, `convoy_integrity.py`,
   `submersible_logistics.py` are standalone (stdlib + numpy) and import
   neither `infrastructure.*` nor `bond_api`. Only `mission.py` adapts to the
   protocol.
5. **Computed manuscript tokens.** Every numeric result in manuscript prose
   uses `{{TOKEN}}` computed by `src/thunderball/manuscript_variables.py`.
   Never hardcode a metric in prose.
6. **Type hints + docstrings.** All public functions annotated and documented.
7. **Coverage gate.** `uv run pytest tests/ --cov=src --cov-fail-under=90`.

## Common pitfalls

- The `bond_api` path dependency must be present; run `uv sync --extra dev`
  before pytest on a fresh clone. The domain core is deliberately importable
  without it.
- Add the sys.path bootstrap (`import _bootstrap  # noqa: E402`) to any new
  top-level script.
- When adding a manuscript token, add it to `generate_variables()` and update
  the cross-reference test, or the live token gate fails.
- When adding a figure, wire it through `render_all_figures()` and reference
  it in `03_results.md` with a `{#fig:label}`.

## Verification checklist (run before submitting a change)

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90 -q
grep -r "unittest.mock\|MagicMock\|@patch\|create_autospec" tests/ || echo Clean
grep -rnE "^(from|import) infrastructure" src/thunderball/ || echo Clean
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
git status --short
```

Coverage and test counts: `docs/_generated/COUNTS.md`.
