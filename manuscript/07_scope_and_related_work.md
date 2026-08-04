# Scope and Related Work {#sec:scope}

## Scope

DISCO VOLANTE covers three planning problems from *Thunderball* (1965): dive
planning, convoy-screen integrity, and submersible logistics. It makes no
claim to full naval mission planning: it omits weather and current modelling,
multi-diver teams, mixed-gas and trimix decompression, sonar and sensor
fusion, and tactical wargaming. Each capability is a deliberately small,
well-tested, deterministic core suitable for demonstrating the BOND mission
protocol.

## Related work

* **Dive planning** — The Bühlmann ZH-L16A tissue model is the classical
  decompression framework; modern software adds gradient factors and trimix
  extensions that this package intentionally keeps simple.
* **Harbour/convoy screening** — Coverage and gap analysis of perimeter
  screens is standard in convoy-defence studies; the angular metric here is a
  reduced, deterministic form.
* **Underwater vehicles** — Cubic speed–power drag laws are the standard
  first-order model for submerged endurance and range; the hotel-load term is
  the minimal extension needed to locate a range optimum.

As a BOND suite film, this package's primary relation is to the frozen
`bond_api` protocol (shared by the 27 film packages) and the suite
_orchestrator_, which drives any `MissionProvider` through the five-stage
lifecycle.
