# Experimental Setup {#sec:setup}

All parameters are declared in `manuscript/config.yaml` and loaded by
`src/thunderball/manuscript_variables.py`; no numeric result is hand-authored
in prose.

## Dive parameters

| Parameter | Value |
|---|---|
| Working depth | {{CONFIG_RECOVERY_DEPTH_M}} m |
| Cylinder capacity | {{CONFIG_CYLINDER_CAPACITY_L}} L |
| Fill pressure | {{CONFIG_FILL_PRESSURE_BAR}} bar |
| SAC rate | {{CONFIG_SAC_LMIN}} L/min |

## Convoy parameters

| Parameter | Value |
|---|---|
| Escort bearings (deg) | {{CONFIG_ESCORT_BEARINGS}} |
| Detection half-angle | {{CONFIG_HALF_ANGLE_DEG}}° |
| Coverage target | {{CONFIG_COVERAGE_TARGET}} |

## Submersible parameters

| Parameter | Value |
|---|---|
| Battery energy | {{CONFIG_ENERGY_KWH}} kWh |
| Drag coefficient | {{CONFIG_DRAG_COEFF}} |
| Hotel load | {{CONFIG_HOTEL_KW}} kW |

## Sonar parameters

| Parameter | Value |
|---|---|
| Frequency | {{CONFIG_SONAR_F_KHZ}} kHz |
| Source level | {{CONFIG_SONAR_SL_DB}} dB |
| Ambient noise | {{CONFIG_SONAR_NL_DB}} dB |
| Directivity index | {{CONFIG_SONAR_DI_DB}} dB |

## Navigation parameters

| Parameter | Value |
|---|---|
| Return-leg track | {{CONFIG_NAV_TRACK_DEG}}° |
| Own speed | {{CONFIG_NAV_SPEED_KNOTS}} kn |
| Current set | {{CONFIG_CURRENT_SET_DEG}}° |
| Current drift | {{CONFIG_CURRENT_DRIFT_KNOTS}} kn |
| Recovery radius | {{CONFIG_RECOVERY_RADIUS_NM}} nm |

## Interdiction parameters

| Parameter | Value |
|---|---|
| Threat course | {{CONFIG_THREAT_COURSE_DEG}}° |
| Threat speed | {{CONFIG_THREAT_SPEED_KNOTS}} kn |
| Screen radius | {{CONFIG_SCREEN_RADIUS_NM}} nm |
| Escort reaction time | {{CONFIG_ESCORT_REACTION_H}} h |

## Environment

- Package version: {{MISSION_VERSION}}
- Python: {{PYTHON_VERSION}}
- Manuscript date (from `config.yaml`, not the clock): {{GENERATION_TIMESTAMP}}

The mission runs under a fixed seed ({{CONFIG_KEYWORDS}} include deterministic
mission software); the six domain modules are pure functions of these
parameters.
