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

## Environment

- Package version: {{MISSION_VERSION}}
- Python: {{PYTHON_VERSION}}
- Generated: {{GENERATION_TIMESTAMP}}

The mission runs under a fixed seed ({{CONFIG_KEYWORDS}} include deterministic
mission software); the three domain modules are pure functions of these
parameters.
