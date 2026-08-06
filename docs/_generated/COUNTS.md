# COUNTS.md — Thunderball (DISCO VOLANTE)

Live, regenerated metrics for this package. These are generated output — do
not hardcode them elsewhere; regenerate after any test change with

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

## Test suite

- Test count: **210**
- Line + branch coverage on `src/`: **100.00%** (gate: 90%)
- Failures: **0** · Skipped: **0** · Mock-framework uses: **0**

## Coverage by module

| Module | Stmts | Branch | Cover |
|---|---|---|---|
| `src/thunderball/convoy_integrity.py` | 132 | 60 | 100.00% |
| `src/thunderball/current_navigation.py` | 76 | 6 | 100.00% |
| `src/thunderball/dive_planner.py` | 144 | 38 | 100.00% |
| `src/thunderball/figures.py` | 115 | 2 | 100.00% |
| `src/thunderball/interdiction_analysis.py` | 80 | 16 | 100.00% |
| `src/thunderball/manuscript_variables.py` | 95 | 10 | 100.00% |
| `src/thunderball/mission.py` | 77 | 0 | 100.00% |
| `src/thunderball/sonar_detection.py` | 54 | 14 | 100.00% |
| `src/thunderball/submersible_logistics.py` | 74 | 16 | 100.00% |
| **TOTAL** | **847** | **162** | **100.00%** |

`src/thunderball/__init__.py` is excluded by `[tool.coverage.run] omit` — it is
a re-export facade with no logic, and its exports are exercised through the
per-module tests.

## Tests per file

| Test file | Tests |
|---|---|
| `test_convoy_integrity.py` | 29 |
| `test_current_navigation.py` | 20 |
| `test_dive_planner.py` | 29 |
| `test_figures.py` | 12 |
| `test_interdiction_analysis.py` | 22 |
| `test_manuscript_lint.py` | 3 |
| `test_manuscript_variables.py` | 14 |
| `test_mission.py` | 16 |
| `test_nan_rejection.py` | 11 |
| `test_regeneration_determinism.py` | 10 |
| `test_scripts_smoke.py` | 10 |
| `test_sonar_detection.py` | 19 |
| `test_submersible_logistics.py` | 15 |

## Manuscript tokens

- Generated tokens: **55**
- Referenced in prose but not generated: **0** (gated by
  `test_all_manuscript_tokens_are_generated`)
- Generated but never referenced: **0** (gated by
  `test_no_generated_token_is_orphaned`)
- Crossref labels referenced but never defined: **0** (gated by
  `test_manuscript_crossref_labels_resolve`)
- Citation keys absent from `references.bib`: **0** (gated by
  `test_manuscript_citation_keys_resolve`)
- Measured metric decaying in agent-facing prose: **0** (gated by
  `test_no_measured_metric_decays_in_agent_facing_prose`)

Measured on Python 3.14.6, macOS (darwin), 2026-08-06.
