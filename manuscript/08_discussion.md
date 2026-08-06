# Discussion and Uncertainty {#sec:discussion}

Every number in @sec:results is the deterministic output of a closed-form or
bounded-iteration model over explicit parameters in `manuscript/config.yaml`.
That determinism gives the package its reproducibility, but it also means the
precision of a token — two or three decimal places — is **not** accuracy. Each
of the six models rests on idealising assumptions, and where those assumptions
break is where the uncertainty actually lives. This section states that
honestly for each capability.

## The central finding is robust, not borderline

The headline result — that **decompression, not gas, binds the flagship dive**
— is the single most consequential number in the package, and it is also the
most robust one. The no-decompression limit of {{RESULT_NDL_MINUTES}} minutes
and the air-supply limit of {{RESULT_AIR_DURATION_MIN}} minutes are not close:
the air budget outlasts the no-stop obligation by more than a factor of two at
the working depth of {{CONFIG_RECOVERY_DEPTH_M}} m, so the conclusion that the
team surfaces on its decompression obligation survives a wide swath of
parameter error and is not a borderline tie. The suite deliberately pins the
limit against an independent published band [@usnavydiving2016] precisely
because a transposed M-value or a depth-evaluated ceiling could silently
invert this call (see @sec:results).

## Dive planning uncertainty

The ZH-L16A model is air-only and single-dive, and it treats every diver
identically: it takes one {{CONFIG_SAC_LMIN}} L/min SAC rate, no gradient
factors, no repetitive-dive residual nitrogen, and no human physiological
variation. Real no-stop limits vary substantially across divers, workloads,
thermal stress, and ascent profiles; a representative model cannot claim
those. An operational planner would add conservatism (safety/gradient factors)
well beyond what a bare M-value line provides.

## Convoy-screen uncertainty

The screen model is angular and static: escorts sit at fixed bearings, each
watching an idealised circular arc of the configured half-angle; the flagship
screen reports {{RESULT_UNCOVERED_SECTOR_DEG}} degrees of genuinely unwatched
perimeter. A real escort's detection is probabilistic, range-limited, and
environment-dependent, so a computed zero-degree uncovered sector is a
statement about the *model geometry*, not about the physical certainty that no
threat slips through. The integrity score's sigmoid knee at a nominal 60° and
the configurable hard sector ceiling are design choices, not physical
constants.

## Submersible-logistics uncertainty

The cubic speed-power drag law plus a constant hotel load is a first-order
propulsion idealisation. The analytic optimal speed
({{RESULT_OPTIMAL_SPEED_KNOTS}} knots, from @sec:methodology) is a true
extremum of that idealised curve but inherits the uncertainty of the drag
coefficient and hotel load, which in reality vary with loading, fouling,
temperature, and depth. Battery energy likewise derates with age and cold that
the constant {{CONFIG_ENERGY_KWH}} kWh figure does not capture.

## Passive-sonar uncertainty

The sonar model is a single-path, spherical-spreading-plus-absorption range
equation. It yields a *range* ({{RESULT_SONAR_RANGE_NM}} nm), not a
probability of detection: there is no multipath, convergence-zone, bottom or
surface interaction, and no fluctuation term. Real detection is inherently
probabilistic, and its strongest driver — ambient noise
({{CONFIG_SONAR_NL_DB}} dB) — is among the most variable inputs in the
scenario, so the computed range should be read as a representative figure
under the stated quieting, not a guaranteed acquisition distance.

## Navigation uncertainty

Set-and-drift is modelled as a single uniform current vector. Real currents
shear with depth, vary over time, and interact with weather; the course to
steer and the drift figure ({{RESULT_NAV_DRIFT_NM}} nm, from @sec:results)
hold exactly under the assumed constant current and degrade continuously as
that assumption is violated. Any error between the assumed and actual
set/drift translates directly into cross-track error on the return leg.

## Interdiction uncertainty

The interdiction verdict tracks a single threat under constant velocity.
{{RESULT_INTERDICTION_STATUS}} is a race against a nominal escort reaction
time ({{CONFIG_ESCORT_REACTION_H}} h); reaction time is operationally the most
uncertain quantity in the chain, so the categorical verdict should be read as
a sensitivity to that one number rather than a fixed outcome. The infinite
time-to-minimum-separation of a threat whose CPA lies outside the limit is a
"never under constant velocity", not an absolute guarantee.

## What would reduce these uncertainties

Each open item in the package backlog (`TODO.md`, *Extension*) is exactly the
modelling refinement that would shrink the corresponding uncertainty here:
gradient factors and mixed gas for the dive model, a probabilistic (Marcum)
detection layer for sonar, a depth-sheared or time-varying current for
navigation, and multi-track association for interdiction. They are out of
scope for this deterministic, six-capability mission package, which is sized to
demonstrate the BOND mission protocol rather than to plan a live operation.
