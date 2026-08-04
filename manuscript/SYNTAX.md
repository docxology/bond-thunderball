# Manuscript SYNTAX — Thunderball (DISCO VOLANTE)

This guide documents the token, figure, and cross-reference syntax used in the
manuscript. Literal `{{TOKEN}}` strings here are illustrative placeholders,
not live tokens.

## `{{TOKEN}}` substitution

Manuscript prose uses `{{TOKEN_NAME}}`. Values are computed by
`src/thunderball/manuscript_variables.py::generate_variables()`. Prefixes:

- `CONFIG_*` — parameters read verbatim from `manuscript/config.yaml`.
- `RESULT_*` — values derived deterministically by the domain modules.
- `MISSION_*`, `PYTHON_VERSION`, `GENERATION_TIMESTAMP` — identity/environment.

## Cross-references

- Section: anchor the heading `## Methodology {#sec:methodology}`, reference
  `@sec:methodology` (narrative) or `[@sec:methodology]` (parenthetical).
- Figure: anchor with `{#fig:label}`, reference `@fig:label` /
  `[@fig:label]`.
- Citations: `[@buehlmann1984]` from `references.bib`.

## Adding a token / figure

1. Add the key to `generate_variables()` (and the domain derivation that
   backs it).
2. Update the live cross-reference test so the token resolves.
3. Reference it in a `[0-9]*.md` section; keep it out of rendered prose as a
   raw unsubstituted `{{...}}`.
