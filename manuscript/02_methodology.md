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
bounded root-find on the imbalance `f(v) = R k v^3 - E v + R H`.

## Passive sonar detection

Detection modelling in `src/thunderball/sonar_detection.py` uses the passive
sonar equation. **Thorp absorption** gives the frequency-dependent seawater
attenuation (`alpha(f) = 0.11 f²/(1+f²) + 44 f²/(4100+f²) + 2.75e-4 f² + 0.003`
dB/km), and **transmission loss** combines spherical spreading with
absorption: `TL(r) = 20 log10(r) + alpha(f) r` (@fig:sonar). The **signal
excess** `SE = SL - TL - (NL - DI) - DT` is the detection margin; the
**detection range** is where `SE` crosses zero, located by bounded bisection.

## Set-and-drift navigation

Navigation in `src/thunderball/current_navigation.py` works in the
east/north plane with the current expressed as a set/drift vector. Own
velocity and current are vector-added to give ground velocity, and dead
reckoning integrates it over time. **Course to steer** solves the classic
vector triangle: the current's component perpendicular to the desired track
is cancelled by a component of own velocity, `theta = asin(-c_perp / v)`,
giving the heading that makes good the track. **Cross-track error** is the
signed perpendicular distance off the track line, and the drift distance over
the dive's bottom time is checked against the recovery radius
(@fig:drift).

## Convoy interdiction

Interdiction in `src/thunderball/interdiction_analysis.py` layers relative
motion over the static screen. The **closest point of approach** between a
threat track and the convoy follows from relative position and velocity:
`t_cpa = max(0, -dot(rel_pos, rel_vel) / |rel_vel|²)` and
`d_cpa = |rel_pos + rel_vel t_cpa|`, with closing speed derived from the same
dot product. The **screen penetration time** is the chord across the largest
gap (`2 r sin(gap/2)`) divided by the interceptor's speed. The **interdiction
status** combines these: `breached` when the CPA is inside the minimum
separation, `held` when escorts react before the threat closes or crosses the
gap, and `penetrated` otherwise.
