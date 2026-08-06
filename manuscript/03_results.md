# Results {#sec:results}

## Flagship verdict summary

For the flagship recovery profile the six capabilities report the following
deterministic verdicts; each row is a live token from the engine, not a
hand-copied constant.

| Capability | Verdict |
|---|---|
| Dive — no-decompression limit | {{RESULT_NDL_MINUTES}} min |
| Dive — air-supply limit | {{RESULT_AIR_DURATION_MIN}} min |
| Dive — binding constraint | {{RESULT_DIVE_BINDING_CONSTRAINT}} |
| Dive — decompression stops | {{RESULT_DIVE_DECO_STOPS}} |
| Convoy — integrity status | {{RESULT_CONVOY_STATUS}} (score {{RESULT_CONVOY_SCORE}}) |
| Convoy — uncovered sector | {{RESULT_UNCOVERED_SECTOR_DEG}}° |
| Submersible — optimal range | {{RESULT_OPTIMAL_RANGE_NM}} nm |
| Sonar — detection range | {{RESULT_SONAR_RANGE_NM}} nm |
| Navigation — drift | {{RESULT_NAV_DRIFT_NM}} nm (within recovery: {{RESULT_NAV_WITHIN_RECOVERY}}) |
| Interdiction — status | {{RESULT_INTERDICTION_STATUS}} |


## Dive planning results

For the flagship recovery profile (working depth {{CONFIG_RECOVERY_DEPTH_M}} m),
the Bühlmann ZH-L16A model reports a no-decompression limit of
**{{RESULT_NDL_MINUTES}} minutes**. The configured cylinder
({{CONFIG_CYLINDER_CAPACITY_L}} L at {{CONFIG_FILL_PRESSURE_BAR}} bar) and SAC
rate ({{CONFIG_SAC_LMIN}} L/min) yield an air-duration limit of
**{{RESULT_AIR_DURATION_MIN}} minutes**. Decompression therefore binds first:
`plan_dive` reports a binding constraint of
**{{RESULT_DIVE_BINDING_CONSTRAINT}}** and a planned bottom time of
**{{RESULT_DIVE_BOTTOM_MIN}} minutes**, with
{{RESULT_DIVE_DECO_STOPS}} decompression stops — flying exactly the
no-decompression limit is by definition a no-stop dive. The dive consumes
**{{RESULT_DIVE_GAS_REQUIRED_L}} L** of the cylinder's free gas, leaving a
margin of **{{RESULT_DIVE_GAS_MARGIN_L}} L**: the recovery team surfaces on its
decompression obligation with gas to spare, which is the correct way round for
a working dive at this depth.

![Bühlmann ZH-L16A no-decompression limit versus depth, evaluated against the surface ascent ceiling.](figures/ndl_curve.png){#fig:ndl}

## Convoy integrity results

The escort screen is placed at bearings {{CONFIG_ESCORT_BEARINGS}} degrees
with a detection half-angle of {{CONFIG_HALF_ANGLE_DEG}} degrees. The widest
*spacing* between adjacent escorts is **{{RESULT_LARGEST_GAP_DEG}} degrees**,
but spacing is not exposure: each escort watches {{CONFIG_HALF_ANGLE_DEG}}
degrees either side of its bearing, so the arcs overlap and the largest
genuinely *uncovered* sector is **{{RESULT_UNCOVERED_SECTOR_DEG}} degrees**,
with total escort coverage **{{RESULT_COVERAGE}}**. Nothing around this screen
is unwatched. The integrity score is **{{RESULT_CONVOY_SCORE}}**, rated
**{{RESULT_CONVOY_STATUS}}**; the score is driven by the spacing rather than by
the uncovered sector, which is what keeps it sensitive to a screen thinning out
before any hole actually opens. To reach the
{{CONFIG_COVERAGE_TARGET}} coverage target a uniform screen needs at least
**{{RESULT_MIN_ESCORTS_90PCT}} escorts**.

![Polar coverage rosette for the configured screen: each of 360 sample bearings tested against the actual escort set, with the escorts marked on the rim.](figures/convoy_screen.png){#fig:convoy}

## Submersible logistics results

The submersible powerplant ({{CONFIG_ENERGY_KWH}} kWh, drag coefficient
{{CONFIG_DRAG_COEFF}}, hotel load {{CONFIG_HOTEL_KW}} kW) achieves its optimal
range at **{{RESULT_OPTIMAL_SPEED_KNOTS}} knots**, giving an
**{{RESULT_OPTIMAL_RANGE_NM}} nautical-mile** best range (@fig:range).

![Submersible range versus speed, with the optimal-range marker.](figures/submersible_range.png){#fig:range}

## Passive sonar results

At {{CONFIG_SONAR_F_KHZ}} kHz (source level {{CONFIG_SONAR_SL_DB}} dB,
ambient noise {{CONFIG_SONAR_NL_DB}} dB, directivity index
{{CONFIG_SONAR_DI_DB}} dB) the passive-sonar range equation gives a detection
range of **{{RESULT_SONAR_RANGE_NM}} nautical miles** — the range at which the
signal excess crosses zero (@fig:sonar).

![Passive-sonar transmission loss versus range, with the detection budget.](figures/transmission_loss.png){#fig:sonar}

## Navigation results

The return leg makes good a track of {{CONFIG_NAV_TRACK_DEG}} degrees at
{{CONFIG_NAV_SPEED_KNOTS}} knots against a current setting
{{CONFIG_CURRENT_SET_DEG}} degrees at {{CONFIG_CURRENT_DRIFT_KNOTS}} knots.
Course-to-steer corrects the heading to **{{RESULT_NAV_HEADING_DEG}} degrees**
with a ground speed of **{{RESULT_NAV_GROUND_SPEED_KNOTS}} knots**. Over the
planned bottom time of {{RESULT_DIVE_BOTTOM_MIN}} minutes — the time the team
is actually in the water, which is the decompression limit here and not the
longer {{RESULT_AIR_DURATION_MIN}}-minute air budget — the current sweeps the
team **{{RESULT_NAV_DRIFT_NM}} nautical miles**. Inside the
{{CONFIG_RECOVERY_RADIUS_NM}}-nautical-mile recovery radius:
**{{RESULT_NAV_WITHIN_RECOVERY}}** (@fig:drift).

![Set-and-drift geometry over the planned bottom time, computed from the dive parameters rather than pinned to a literal.](figures/drift_geometry.png){#fig:drift}

## Interdiction results

The threat track (course {{CONFIG_THREAT_COURSE_DEG}} degrees at
{{CONFIG_THREAT_SPEED_KNOTS}} knots, closing at
**{{RESULT_CLOSING_KNOTS}} knots**) has its closest point of approach at
**{{RESULT_CPA_DIST_NM}} nautical miles** after **{{RESULT_CPA_TIME_H}}
hours**. That CPA is outside the
{{CONFIG_MIN_SEPARATION_NM}}-nautical-mile minimum separation, and the CPA is
by construction the smallest range the threat ever reaches, so minimum
separation is never breached and the verdict turns on the gap crossing alone.
Crossing the {{RESULT_LARGEST_GAP_DEG}}-degree inter-escort sector at
{{CONFIG_SCREEN_RADIUS_NM}} nautical miles takes **{{RESULT_PENETRATION_H}}
hours**, against an escort reaction time of {{CONFIG_ESCORT_REACTION_H}}
hours; the screen is rated **{{RESULT_INTERDICTION_STATUS}}**.
