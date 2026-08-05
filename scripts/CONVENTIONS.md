# CONVENTIONS — scripts/

- One thin CLI per file, named for its mission phase (`<phase>.py`).
- No `sys.path` manipulation anywhere: rely on the editable install from
  `uv sync --extra dev`. Import order is `__future__`, stdlib, `bond_api`,
  then `thunderball`; ruff enforces the formatting.
- Deterministic stdout: scripts print computed values only (no wall-clock, no
  RNG) so smoke tests can assert stable output. The one timestamp in the
  system, `GENERATION_TIMESTAMP`, is read from the committed `paper.date` in
  `manuscript/config.yaml`; `--now` overrides it but is not needed for
  byte-identical regeneration.
- Use `raise SystemExit(main())`; `main()` returns an int exit code.
- Business logic belongs in `src/thunderball/`. A script that computes
  anything a test would want to assert on is in the wrong layer.
