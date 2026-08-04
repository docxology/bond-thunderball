# Testing Philosophy — Thunderball (DISCO VOLANTE)

The test suite proves the domain math and the protocol adapter with **real
computation and real `bond_api` protocol types** — never mocks. A mock-based
test can pass while the underlying algorithm is wrong; these tests compute
results and assert their correctness, so a green suite is evidence the
implementation is right.

## Zero-mock policy

No `unittest.mock`, `MagicMock`, `@patch`, or `create_autospec` anywhere in
`tests/`. This is enforced and is part of the suite's identity. Where a
deterministic stand-in is needed (e.g. a provider), it is a *real* class
implementing the *real* protocol.

## Files

| File | Covers |
|---|---|
| `test_dive_planner.py` | Air budget, ambient/alveolar pressure, ZH-L16A NDL, deco-stops schedule |
| `test_convoy_integrity.py` | Angular gaps, largest gap, coverage fraction, integrity score/status, min escorts |
| `test_submersible_logistics.py` | Power, endurance, range, optimal speed, range-inverse, mission energy |
| `test_sonar_detection.py` | Thorp absorption, transmission loss, signal excess, detection range, verdicts |
| `test_current_navigation.py` | Drift vectors, dead reckoning, course-to-steer, cross-track error, drift limits |
| `test_interdiction_analysis.py` | CPA/TCPA geometry, penetration time, interdiction statuses, full assessment |
| `test_mission.py` | MissionProvider lifecycle, discovery, registries, gadget registration, determinism |
| `test_manuscript_variables.py` | Token computation + live `{{TOKEN}}` cross-reference gate |
| `test_figures.py` | Figure generation writes valid PNGs |
| `test_scripts_smoke.py` | Subprocess runs of every thin CLI (`sys.executable`, `cwd=root`) |

## Deterministic tests

* Fixed inputs everywhere; no untracked RNG.
* Manuscript tokens are compared deterministically with a fixed `now` for
  `GENERATION_TIMESTAMP`.
* `execute()` results are asserted byte-identical across two runs.
* Domain geometry (CPA, course-to-steer) is verified by round-trip: the
  steered ground velocity actually makes good the track; the CPA point lies
  on the relative-motion line.
* Documents/verification commands never contain the literal lineage string, so
  the lineage gate cannot self-trip.

## Coverage

Gate: `uv run pytest tests/ --cov=src --cov-fail-under=90` (line+branch).
Live test count and achieved coverage are tracked in
`docs/_generated/COUNTS.md`.
