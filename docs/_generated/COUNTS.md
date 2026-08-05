# COUNTS.md — Thunderball (DISCO VOLANTE)

Live, regenerated metrics for this package. These are generated output — do
not hardcode them elsewhere; regenerate after any test change with

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

## Test suite

- Test count: **169**
- Line + branch coverage on `src/`: **100.00%** (gate: 90%)
- Failures: **0** · Skipped: **0** · Mock-framework uses: **0**

## Coverage by module

| Module | Stmts | Branch | Cover |
|---|---|---|---|
| `src/thunderball/convoy_integrity.py` | 104 | 44 | 100.00% |
| `src/thunderball/current_navigation.py` | 76 | 6 | 100.00% |
| `src/thunderball/dive_planner.py` | 144 | 38 | 100.00% |
| `src/thunderball/figures.py` | 114 | 2 | 100.00% |
| `src/thunderball/interdiction_analysis.py` | 77 | 16 | 100.00% |
| `src/thunderball/manuscript_variables.py` | 82 | 4 | 100.00% |
| `src/thunderball/mission.py` | 77 | 0 | 100.00% |
| `src/thunderball/sonar_detection.py` | 54 | 14 | 100.00% |
| `src/thunderball/submersible_logistics.py` | 74 | 16 | 100.00% |
| **TOTAL** | **802** | **140** | **100.00%** |

`src/thunderball/__init__.py` is excluded by `[tool.coverage.run] omit` — it is
a re-export facade with no logic, and its exports are exercised through the
per-module tests.

## Tests per file

| Test file | Tests |
|---|---|
| `test_convoy_integrity.py` | 22 |
| `test_current_navigation.py` | 20 |
| `test_dive_planner.py` | 29 |
| `test_figures.py` | 8 |
| `test_interdiction_analysis.py` | 19 |
| `test_manuscript_variables.py` | 12 |
| `test_mission.py` | 15 |
| `test_scripts_smoke.py` | 10 |
| `test_sonar_detection.py` | 19 |
| `test_submersible_logistics.py` | 15 |

## Manuscript tokens

- Generated tokens: **53**
- Referenced in prose but not generated: **0**
- Generated but never referenced: **0**

Measured on Python 3.14.6, macOS (darwin), 2026-08-05.
