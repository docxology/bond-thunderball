# Reproducibility {#sec:reproducibility}

DISCO VOLANTE is deterministic by construction:

* **Fixed seed** — no random draws anywhere; results are pure functions of the
  config parameters.
* **No wall-clock dependence** — `GENERATION_TIMESTAMP` is the only timestamp
  and is overridable (`--now`) for byte-identical regeneration.
* **Computed tokens** — every `{{RESULT_*}}` value in this manuscript is
  recomputed from `src/` domain math, never hand-authored.
* **Provenance** — every `MissionOutcome` carries a fixed input hash and seed,
  so an outcome can be audited without re-running the film.

The concept figures (`output/figures/ndl_curve.png`, `convoy_screen.png`,
`submersible_range.png`, `transmission_loss.png`, `drift_geometry.png`) are
regenerated deterministically.

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
* No-decompression limits at 18, 30, 40 and 60 m, asserted to fall inside the
  published ZH-L16A air-table bands [@usnavydiving2016].
* The analytic optimal-range speed, cross-checked against a dense numerical
  sweep of the range curve.
* The pointwise coverage predicate, cross-checked against the aggregate
  coverage fraction over a 3600-sample sweep of the compass.

A test that only restates the formula under test cannot catch a transposed
formula. These anchors can.
