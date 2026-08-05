# AGENTS.md — scripts/

Thin orchestrators only. Rules:

1. **No business logic** in scripts. Delegate to `src/thunderball/`. If a
   script needs a number, the number is computed in `src/` and imported.
2. **No `sys.path` manipulation.** `uv sync --extra dev` installs this package
   editable into `.venv`, so `import thunderball` resolves for anything run
   under `uv run`. A hand-rolled bootstrap module used to live here; it was
   imported by nothing and is gone. Do not reintroduce one — `mypy src/
   scripts/` cannot resolve a bare sibling import and will fail the gate.
3. **argv shaping** is fine; do not add parameter validation logic here.
4. Return an exit code (`0` on success); use `raise SystemExit(main())`.
5. Every script is exercised by `tests/test_scripts_smoke.py` via
   `sys.executable` from the project root, and the assertions there are
   unconditional — a script that silently writes nothing fails.

`z_generate_manuscript_variables.py` is the only script with a `z_` prefix
(runs last, mirrors the BOND CLI `--allow-draft`/`--now` conventions).
