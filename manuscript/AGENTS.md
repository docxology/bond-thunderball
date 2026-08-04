# AGENTS.md — manuscript/

Repository-wide agent rules live in `../docs/agent_instructions.md`. This file
covers manuscript-specific editing for the Thunderball (DISCO VOLANTE)
package.

## `{{VARIABLE}}` token protocol

1. Numeric values that come from analysis **must** use `{{VARIABLE_NAME}}`.
2. Add each new token's key/value in
   `src/thunderball/manuscript_variables.py::generate_variables()`.
3. The live cross-reference test
   `tests/test_manuscript_variables.py::test_all_manuscript_tokens_are_generated`
   scans `manuscript/[0-9]*.md` and fails if any `{{TOKEN}}` lacks a generated
   value. Reference/guide files (README.md, AGENTS.md, SYNTAX.md) legitimately
   contain literal `{{TOKEN}}` placeholders and are excluded from the scan.
4. Verify: read `output/data/manuscript_variables.json` after running
   `scripts/z_generate_manuscript_variables.py`.

## Figure protocol

All figures use Pandoc-crossref `{#fig:label}`; reference with `[@fig:label]`
or `@fig:label` in `03_results.md`. See the table in `README.md` for the
five concept figures.

## Config

`config.yaml` is the single source of truth for the dive / convoy /
submersible parameters and the `paper:` metadata. `generate_variables()`
reads it (with `--now` override for determinism).
