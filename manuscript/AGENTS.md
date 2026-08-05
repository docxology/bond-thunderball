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
   The reverse direction is enforced by
   `tests/test_manuscript_variables.py::test_no_generated_token_is_orphaned`,
   which fails on any token `generate_variables()` emits that no numbered
   section references — so keep `generate_variables()` and the prose in step.
4. Verify: read `output/data/manuscript_variables.json` after running
   `scripts/z_generate_manuscript_variables.py`.

## Figure protocol

All figures use Pandoc-crossref `{#fig:label}`; reference with `[@fig:label]`
or `@fig:label` in `03_results.md`. See the table in `README.md` for the
five concept figures.

## Config

`config.yaml` is the single source of truth for all six domains' parameters
(`recovery`, `screen`, `submersible`, `sonar`, `navigation`, `interdiction`)
and the `paper:` metadata. `generate_variables()` reads it, with a `--now`
override for determinism.

Its `paper.subtitle` and `keywords` must describe what the package actually
does; they feed `CONFIG_KEYWORDS`, which is rendered into the abstract, so a
stale keyword list becomes a false statement in the manuscript.

## Never hand-author a metric

Not in prose, not in a caption, not in a table. If a number changes when the
code changes, it is a token. This package once shipped a manuscript whose
headline conclusion — that gas, not decompression, bound the dive — was
inverted by a model defect; the numbers updated themselves when the model was
fixed, but the surrounding *claim* had to be rewritten by hand. Prefer prose
that states the comparison ("X binds before Y") over prose that restates a
value the token already carries.
