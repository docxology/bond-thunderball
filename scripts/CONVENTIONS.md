# CONVENTIONS — scripts/

- One thin CLI per file, named for its mission phase (`<phase>.py`).
- `_bootstrap.py` is the single sys.path bootstrap; do not inline path
  manipulation in each script.
- Import order: `import _bootstrap  # noqa: E402` then stdlib, then
  `bond_api`, then `thunderball`. Ruff will enforce formatting.
- Deterministic stdout: scripts print computed values only (no wall-clock, no
  RNG) so smoke tests can assert stable output.
- Use `raise SystemExit(main())`; `main()` returns an int exit code.
