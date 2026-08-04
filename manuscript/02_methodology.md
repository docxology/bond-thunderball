# Methodology {#sec:methodology}

## Dive planning

Dive planning in `src/thunderball/dive_planner.py` rests on two pieces of
physics. First, absolute ambient pressure rises by one bar every ten metres:
`P(d) = P_surf + d/10`. Breathing demand at depth scales with this pressure,
so a diver with a surface air consumption (SAC) rate of
{{CONFIG_SAC_LMIN}} L/min uses `SAC * P(d)` litres per minute at depth. A
cylinder of {{CONFIG_CYLINDER_CAPACITY_L}} L filled to
{{CONFIG_FILL_PRESSURE_BAR}} bar therefore holds
`{{CONFIG_CYLINDER_CAPACITY_L}} * {{CONFIG_FILL_PRESSURE_BAR}}` litres of
free gas, and the bottom time follows by dividing usable volume by the
at-depth demand.

Second, inert-gas loading is modelled with the **Bühlmann ZH-L16A** tissue
model: sixteen compartments, each with a nitrogen half-time and an M-value
line `M = a*P + b`. A compartment's inert-gas pressure approaches the
alveolar pressure `P_alv = f_N2 (P - pH2O)` exponentially on its half-time.
The no-decompression limit at a depth is the largest bottom time for which
every compartment stays under its M-value at that ambient pressure
(@fig:ndl). When a dive exceeds it, `plan_decompression` emits ascending stop
holds that discharge the controlling tissue.

## Convoy integrity

Convoy analysis in `src/thunderball/convoy_integrity.py` treats the escort
screen as a set of bearing angles around the protected formation. Between
consecutive escorts there is an uncovered **angular gap**; the largest gap is
the weakest sector a hostile interceptor can exploit. Each escort defends an
arc of `2 * half_angle` around its bearing, and **coverage fraction** is the
unioned defended arc divided by 360° (@fig:convoy).

The **integrity score** combines a sigmoid gap penalty with coverage:

```
score = 1 / (1 + exp((gap - 60) / 12))  *  (0.5 + 0.5 * coverage)
```

Scores above 0.7 are rated `ok`, between 0.4 and 0.7 `marginal`, and below
0.4 `breached`. `min_escorts_for_coverage` returns the smallest uniform screen
that reaches a coverage target.

## Submersible logistics

Submersible logistics in `src/thunderball/submersible_logistics.py` models
underwater propulsion with a cubic speed-power law plus a constant hotel
load: `P(v) = k v^3 + H`. Endurance is `E / P(v)`, and range is
`v * E / P(v)` (@fig:range). The speed that maximises range balances the
cubic drag term against the hotel load; because `R(v)` rises then falls, the
optimum is found from the derivative vanishing at `k v^3 = H/2`. The inverse
problem — energy required to transit a given range — inverts the cubic via a
closed-form root.
