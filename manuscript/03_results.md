# Results {#sec:results}

## Dive planning results

For the flagship recovery profile (working depth {{CONFIG_RECOVERY_DEPTH_M}} m),
the Bühlmann ZH-L16A model reports a no-decompression limit of
**{{RESULT_NDL_MINUTES}} minutes**. The configured cylinder
({{CONFIG_CYLINDER_CAPACITY_L}} L at {{CONFIG_FILL_PRESSURE_BAR}} bar) and SAC
rate ({{CONFIG_SAC_LMIN}} L/min) yield an air-duration limit of
**{{RESULT_AIR_DURATION_MIN}} minutes** — the binding constraint, indicating
that gas volume, not decompression, governs the working bottom time.

![Bühlmann ZH-L16A no-decompression limit versus depth.](figures/ndl_curve.png){#fig:ndl}

## Convoy integrity results

The escort screen is placed at bearings {{CONFIG_ESCORT_BEARINGS}} degrees
with a detection half-angle of {{CONFIG_HALF_ANGLE_DEG}} degrees. The largest
uncovered sector is **{{RESULT_LARGEST_GAP_DEG}} degrees**, the total escort
coverage is **{{RESULT_COVERAGE}}**, and the resulting integrity score is
**{{RESULT_CONVOY_SCORE}}**, rated **{{RESULT_CONVOY_STATUS}}**. To reach the
{{CONFIG_COVERAGE_TARGET}} coverage target a uniform screen needs at least
**{{RESULT_MIN_ESCORTS_90PCT}} escorts**.

![Polar escort-screen coverage for the configured detection half-angle.](figures/convoy_screen.png){#fig:convoy}

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
dive's bottom time the current sweeps the team **{{RESULT_NAV_DRIFT_NM}}
nautical miles** — {{RESULT_NAV_WITHIN_RECOVERY}} within the
{{CONFIG_RECOVERY_RADIUS_NM}}-nautical-mile recovery radius (@fig:drift).

![Set-and-drift geometry over the dive bottom time.](figures/drift_geometry.png){#fig:drift}

## Interdiction results

The threat track (course {{CONFIG_THREAT_COURSE_DEG}} degrees at
{{CONFIG_THREAT_SPEED_KNOTS}} knots, closing at
**{{RESULT_CLOSING_KNOTS}} knots**) has its closest point of approach at
**{{RESULT_CPA_DIST_NM}} nautical miles** after **{{RESULT_CPA_TIME_H}}
hours**. Crossing the {{RESULT_LARGEST_GAP_DEG}}-degree screen gap at
{{CONFIG_SCREEN_RADIUS_NM}} nautical miles takes **{{RESULT_PENETRATION_H}}
hours**, against an escort reaction time of {{CONFIG_ESCORT_REACTION_H}}
hours; the screen is rated **{{RESULT_INTERDICTION_STATUS}}**.
