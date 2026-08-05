# Scope and Related Work {#sec:scope}

## Scope

DISCO VOLANTE covers six planning problems drawn from *Thunderball* (1965):
dive planning under a Bühlmann ZH-L16A decompression model, convoy-screen
integrity, submersible range and endurance, passive-sonar detection,
set-and-drift navigation, and dynamic convoy interdiction. Each is a
deliberately small, fully-tested, deterministic core, sized to demonstrate the
BOND mission protocol rather than to plan a real operation.

The package makes no claim to full naval mission planning. In particular it
omits:

* **Mixed gas.** The decompression model is air-only: no trimix or nitrox
  compartment sets, no gradient factors, no repetitive-dive residual nitrogen,
  and no ascent-rate violation penalties. It is representative, not a certified
  dive computer, and nothing here should be used to plan a real dive.
* **Ocean physics.** The sonar model is a single-path range equation over
  spherical spreading and Thorp absorption: no sound-speed profile, no
  multipath or convergence-zone structure, no bottom or surface scattering, and
  no probabilistic fluctuation term — so it yields a range, not a probability
  of detection. The current field is a single uniform set-and-drift vector,
  with no tidal variation, depth shear, or weather.
* **Multi-target tactics.** Convoy metrics are angular (gaps, coverage,
  integrity score) plus a single CPA-tracked threat. There is no sensor fusion,
  no multi-track association, no weapon-target assignment, and no wargaming of
  escort manoeuvre.
* **Teams.** One diver, one submersible, one threat track — no buddy pairs, no
  team gas-sharing, no formation logistics.

## Related work

* **Decompression modelling** — Bühlmann's ZH-L16 family is the classical
  dissolved-gas framework and the direct source of the coefficient tables and
  the tolerated-ambient-pressure formulation used here [@buehlmann1984]. The
  *US Navy Diving Manual* is the standard operational reference against which
  no-stop limits are conventionally sanity-checked [@usnavydiving2016]; the
  test suite pins this package's limits inside bands around those published
  air limits rather than against its own arithmetic. The manual's limits come
  from the Navy's own EL/VVAL-18 model lineage, not from ZH-L16A, so the check
  is a cross-model agreement test and not a lookup of the model under test. Modern dive computers add gradient factors
  and bubble-model variants that this package intentionally omits.
* **Underwater acoustics** — Urick is the standard treatment of the sonar
  equation, transmission loss, and detection threshold [@urick1983]; the
  frequency-dependent absorption coefficient is Thorp's [@thorp1967].
* **Marine hydrodynamics** — the cubic speed–power drag law is the standard
  first-order model for submerged resistance and propulsive power
  [@newman1977]; the constant hotel-load term is the minimal extension needed
  for an interior range optimum to exist at all.
* **Navigation and collision geometry** — set-and-drift, the current vector
  triangle, and course-to-steer follow Bowditch [@bowditch2002]. Relative-motion
  CPA/TCPA geometry is the basis of collision-avoidance practice, for which
  Cockcroft and Lameijer is the standard practitioner treatment
  [@cockcroft2011].
* **Perimeter screening** — coverage and gap analysis of a defended perimeter
  is standard in convoy-defence and sensor-placement studies; the angular
  metric here is a reduced, deterministic form of it.

As a BOND suite film, this package's primary relation is to the frozen
`bond_api` protocol [@bondapi2026], shared across the film packages, and to
the suite _orchestrator_, which drives any `MissionProvider` through the
five-stage lifecycle.
