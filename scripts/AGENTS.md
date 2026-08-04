# AGENTS.md — scripts/

Thin orchestrators only. Rules:

1. **No business logic** in scripts. Delegate to `src/thunderball/`.
2. **Bootstrap first**: `import _bootstrap  # noqa: E402` inserts `src/` on
   `sys.path`. Deep monorepo paths bypass the root ruff per-file-ignore
   patterns, so the `# noqa: E402` on the bootstrap import is required.
3. **argv shaping** is fine; do not add parameter validation logic here.
4. Return an exit code (`0` on success); use `raise SystemExit(main())`.
5. Every script is exercised by `tests/test_scripts_smoke.py` via
   `sys.executable` from the project root.

`z_generate_manuscript_variables.py` is the only script with a `z_` prefix
(runs last, mirrors the BOND CLI `--allow-draft`/`--now` conventions).
