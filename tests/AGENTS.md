# tests/ — agent guidance

The reader's view is [README.md](README.md); the doctrine is
[`docs/testing_philosophy.md`](../docs/testing_philosophy.md); the repository-wide rules are in
[the root guide](../AGENTS.md). This file is the short version an agent needs here.

## Run it

```bash
python -m pytest tests/ -q --cov=src --cov-fail-under=90
```

Run from the repository root at `c066bfa` on **2026-11-03**, this passed in full and reached the 90%
floor. Prefer `python -m pytest` over the `pytest` console script: a relocated `.venv` can leave a
console script that runs a different environment's pytest and exits zero, which reads as a gate that
passed when it never ran. The counts and coverage are regenerated into
[`docs/_generated/COUNTS.md`](../docs/_generated/COUNTS.md); regenerate that file after a test change
instead of quoting a figure here or anywhere else in prose.

A worktree cut outside the vault has no `.venv` and no sibling `../bond-api` checkout, which
`[tool.uv.sources]` needs. Run it with an interpreter that already exists, from the parent repository:
`<canonical copy>/.venv/bin/python -m pytest tests/`. No `PYTHONPATH` is needed; `pyproject.toml` sets
`pythonpath = [".", "src"]`.

**Dated:** as of 2026-11-03 the vendoring change replaces that path dependency with a
`vendor/bond-api` directory, after which an ordinary `uv sync` in a worktree should resolve locally.
Re-check this paragraph if that change has landed here.

## Rules

- **Zero mocks.** No `unittest.mock`, `MagicMock`, `@patch` or `create_autospec` anywhere in this
  directory; `grep -rn "unittest.mock\|MagicMock\|@patch\|create_autospec" tests/` returns nothing.
  A deterministic stand-in is a real subclass with real coefficients, computed against.
- **NaN is rejected, not tolerated.** `test_nan_rejection.py` is a negative-control suite over every
  domain module that accepts floats; a new module that silently propagates NaN belongs in it.
- **Determinism is proved by rerunning**, not by comparing recorded output — the generator runs twice
  and its bytes are compared.
- **The CLIs are exercised in real subprocesses** (`test_scripts_smoke.py`), which is also where the
  pure-core import probe lives: it fails if a capability module starts importing `bond_api`.
- **Manuscript tokens are generated, never typed twice.** A token that is generated but not
  referenced, and a reference with no token, both fail — `test_manuscript_variables.py`.
- **A measured figure in prose is treated as decayed already.** The package's own V1 gate
  (`test_manuscript_lint.py`) scans the root guide, the root `README.md` and `docs/*.md` for exactly
  that. Folder-level guides sit outside its scan, so the discipline has to be kept by hand: keep
  counts out of here and point at [`docs/_generated/COUNTS.md`](../docs/_generated/COUNTS.md).

## What is absent here

No CI: the repository has no `.github/` directory, so nothing runs this suite unless a person or a lane
invokes it. No coverage badge, no scheduled run, and no recorded baseline other than
`docs/_generated/COUNTS.md`.
