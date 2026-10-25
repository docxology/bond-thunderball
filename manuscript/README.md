# Manuscript — Thunderball (DISCO VOLANTE)

This directory holds the DISCO VOLANTE manuscript. Repository-wide agent
rules for this package live in `docs/agent_instructions.md`; this file covers
manuscript-specific editing (tokens, figures, cross-references).

## Files

| File | Role |
|---|---|
| `00_abstract.md` … `08_discussion.md`, `99_references.md` | manuscript sections |
| `config.yaml` | paper metadata + `mission:` parameters (source of truth for tokens) |
| `config.yaml.example` | reference copy of the config schema |
| `layer_contract.yaml` | layer-boundary validation |
| `references.bib` | BibTeX bibliography |
| `preamble.md` | LaTeX preamble injections |
| `SYNTAX.md` | token / figure / cross-reference syntax |
| `README.md`, `AGENTS.md` | this guide |

## `{{TOKEN}}` protocol

Every numeric result in prose is a `{{TOKEN}}` computed by
`src/thunderball/manuscript_variables.py::generate_variables()` from
`config.yaml` + the domain math. Never hardcode a metric. When adding a token,
add it to `generate_variables()` and update
`tests/test_manuscript_variables.py::test_all_manuscript_tokens_are_generated`
(the live cross-reference gate over `[0-9]*.md` sections).

## Figure protocol

Figures are rendered by `src/thunderball/figures.py` into `output/figures/`:

| Label | File |
|---|---|
| `{#fig:ndl}` | `output/figures/ndl_curve.png` |
| `{#fig:convoy}` | `output/figures/convoy_screen.png` |
| `{#fig:range}` | `output/figures/submersible_range.png` |
| `{#fig:sonar}` | `output/figures/transmission_loss.png` |
| `{#fig:drift}` | `output/figures/drift_geometry.png` |

Reference figures via Pandoc-crossref (`[@fig:ndl]`, `@fig:range`), never with
hardcoded numbers.

## Rendering

`scripts/z_generate_manuscript_variables.py` writes
`output/data/manuscript_variables.json` and renders the figures.
