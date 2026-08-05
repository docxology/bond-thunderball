# Testing Philosophy — Thunderball (DISCO VOLANTE)

The test suite proves the domain math and the protocol adapter with **real
computation and real `bond_api` protocol types** — never mocks. A mock-based
test can pass while the underlying algorithm is wrong; these tests compute
results and assert their correctness, so a green suite is evidence the
implementation is right.

## Zero-mock policy

No `unittest.mock`, `MagicMock`, `@patch`, or `create_autospec` anywhere in
`tests/`. This is enforced and is part of the suite's identity. Where a
deterministic stand-in is needed — a stricter decompression table, say — it is
a *real* subclass with real coefficients, computed against; never a recording
object with a canned return value.

## Green is not proof

A test that restates the formula under test cannot fail when the formula is
wrong. This package learned that the hard way. For two phases the Bühlmann
M-value line was implemented as `a*P + b` instead of `P/b + a`, and the
no-decompression limit was evaluated against the M-value at *working depth*
rather than at the surface ascent ceiling. Every test passed. The suite checked
that the NDL was positive, that it decreased with depth, and that
`buhlmann_mvalue` returned `a*P + b` — all true of the broken model. The
reported 40 m limit was 163 minutes against a real value near 9, and the
package's headline conclusion ("gas, not decompression, binds") was inverted.

The rules that follow from that:

1. **Anchor physical claims externally.** Assert against published values —
   Bühlmann's 3.27 bar and 1.28 bar surfacing ceilings, and bands around the
   *U.S. Navy Diving Manual*'s published air no-stop limits (60/20/10/5 min at
   18/30/40/60 m) — not against the implementation's own arithmetic. Note the
   Navy limits come from its own EL/VVAL-18 lineage, not from ZH-L16A, which
   is what makes that anchor an independent check rather than a restatement.
2. **Prove a knob is consumed.** Do not assert that a parameter has a value;
   change it and assert the output moves. `min_escorts_for_coverage` is tested
   with a looser target (fewer escorts) *and* a narrower arc (more escorts), so
   both arguments are proven load-bearing. Same for the convoy sector ceiling.
3. **Cross-check one computation with a different one.** The analytic
   optimal-range speed is checked against a dense numerical sweep; the
   pointwise coverage predicate against the aggregate coverage fraction over
   3600 samples; the adapter's dive numbers against a direct `plan_dive` call.
4. **Never guard an assertion behind `if`.** A test whose assertions sit inside
   `if path.exists():` passes silently when the path is missing — exactly the
   failure it was written to catch. Assert the precondition, then the content.
5. **Assert the count before looping.** `for line in output: assert ...` is
   vacuous on empty output. Assert the expected length first.
6. **Guard the guards.** The manuscript token gate is itself tested for
   non-vacuity: at least nine section files must be found and at least thirty
   tokens extracted, or the gate is not actually gating.

## Files

| File | Covers |
|---|---|
| `test_dive_planner.py` | Ambient/alveolar pressure, cylinder volume, gas-limited bottom time, the M-value line against published surfacing ceilings, NDL against published no-stop bands, per-compartment loading, deco scheduling (rate-limited and instant-ascent), `plan_dive` across all four binding regimes, stop-pressure gas accounting |
| `test_convoy_integrity.py` | Angular spacings, largest spacing, the largest uncovered sector (cross-checked against a brute-force sweep of the pointwise predicate, and pinned apart from the spacing on the flagship screen), coverage fraction, the pointwise coverage predicate and its agreement with the aggregate, integrity score/status, the sector ceiling's downgrade-only behaviour, min escorts |
| `test_submersible_logistics.py` | Power, endurance, range, the analytic optimum against a numerical sweep, the no-hotel-load closed form, range-inverse including the exact-maximum and unattainable cases, mission energy |
| `test_sonar_detection.py` | Thorp absorption, transmission loss, signal excess, detection range, verdicts |
| `test_current_navigation.py` | Drift vectors, dead reckoning, course-to-steer, cross-track error, drift limits |
| `test_interdiction_analysis.py` | CPA/TCPA geometry, penetration time, all three verdicts including the penetration-time branch, full assessment |
| `test_mission.py` | Provider lifecycle, discovery by slug, registries, gadget registration, determinism, and agreement between the adapter's reported numbers and a direct domain call |
| `test_manuscript_variables.py` | Token computation, config error paths, agreement with the domain core, the live token cross-reference gate, and a non-vacuity check on that gate |
| `test_figures.py` | Figure generation writes valid PNGs; the convoy rosette actually varies with the screen it is given; the drift figure's default duration comes from the dive math |
| `test_scripts_smoke.py` | Subprocess runs of every thin CLI, plus a probe that importing the pure core does not pull `bond_api` into `sys.modules` |

## Determinism

* Fixed inputs everywhere; no untracked RNG; seed 7 recorded in provenance.
* Manuscript tokens are compared with a fixed `now` for `GENERATION_TIMESTAMP`.
* `execute()` results are asserted equal across two runs.
* Geometry is verified by round-trip: the steered ground velocity actually
  makes good the track; `speed_for_range` is fed back through `range_nm`.
* Figures are compared byte-for-byte where the claim is "these two code paths
  produce the same image".
* Docs and verification commands never contain the literal exemplar lineage
  string, so the lineage gate cannot self-trip.

## Coverage

Gate: `uv run pytest tests/ --cov=src --cov-fail-under=90` (line + branch).
Live counts and achieved coverage are regenerated into
`docs/_generated/COUNTS.md` — never quote a figure in prose you have not just
measured.
