# Reproducibility {#sec:reproducibility}

DISCO VOLANTE is deterministic by construction:

* **Fixed seed** — no random draws anywhere; results are pure functions of the
  config parameters.
* **No wall-clock dependence** — `GENERATION_TIMESTAMP` is the only timestamp,
  and it is read from the committed `paper.date` in `manuscript/config.yaml`,
  never from the clock. Regenerating the artifacts on any later day rewrites
  the same bytes with no flag; `--now` exists only to pin a different value
  deliberately. The one environment-derived token is `PYTHON_VERSION`, so the
  byte-identical claim holds for a fixed interpreter.
* **Computed tokens** — every `{{RESULT_*}}` value in this manuscript is
  recomputed from `src/` domain math, never hand-authored.
* **Provenance** — every `MissionOutcome` carries a fixed input hash and seed,
  so an outcome can be audited without re-running the film.

The concept figures (`output/figures/ndl_curve.png`, `convoy_screen.png`,
`submersible_range.png`, `transmission_loss.png`, `drift_geometry.png`) are
regenerated deterministically. The claim is bound, not asserted:
`tests/test_regeneration_determinism.py` runs the hydration CLI twice, more
than a clock tick apart, and compares every written byte of the token JSON and
all five PNGs.

## Test suite

The package gates on line+branch coverage of `src/` at or above 90%. The
suite covers the dive planner, convoy integrity, submersible logistics,
passive sonar, current navigation, convoy interdiction, the mission protocol
adapter, manuscript-token hydration, figure generation, and subprocess smoke
tests of the mission CLIs. All tests use real computation and real protocol
types — there are no mocks. Live counts are regenerated into
`docs/_generated/COUNTS.md`; this manuscript quotes the gate, not a figure
that would go stale.

## External anchors

Reproducing a number is not the same as it being right, so the constants that
carry a physical claim are pinned against published values rather than against
the implementation's own arithmetic:

* Bühlmann surfacing ceilings — 3.27 bar for the fastest compartment, 1.28 bar
  for the slowest [@buehlmann1984].
* No-decompression limits at 18, 30, 40 and 60 m, asserted to fall inside
  bands bracketing the *U.S. Navy Diving Manual*'s published air
  no-decompression limits of 60, 20, 10 and 5 minutes at those depths
  [@usnavydiving2016]. The Navy manual publishes limits from its own
  EL/VVAL-18 model lineage, not Bühlmann tables, so this anchor is a
  cross-model agreement check — a ZH-L16A implementation landing inside a band
  around an independently derived operational limit — and not a comparison of
  ZH-L16A against itself.
* The analytic optimal-range speed, cross-checked against a dense numerical
  sweep of the range curve.
* The pointwise coverage predicate, cross-checked against the aggregate
  coverage fraction over a 3600-sample sweep of the compass.

A test that only restates the formula under test cannot catch a transposed
formula. These anchors can.
