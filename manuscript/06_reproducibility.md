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
types — there are no mocks.
