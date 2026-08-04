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
**{{RESULT_OPTIMAL_RANGE_NM}} nautical-mile** best range
(@fig:range).

![Submersible range versus speed, with the optimal-range marker.](figures/submersible_range.png){#fig:range}
