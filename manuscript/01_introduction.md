# Introduction

*Thunderball* (1965) is the film in which SPECTRE hijacks two NATO nuclear
bombs and the operation reaches its climax in an underwater battle around the
legendary submersible yacht, *Disco Volante*. The **DISCO VOLANTE** mission
software package implements the quantitative planning problems that underwrite
such a recovery: how deep and how long a diver can work, whether the escort
screen protecting the high-value asset holds, how far the submersible
powerplant can carry an assault team, whether passive sonar can localise the
recovery site, how the prevailing current displaces the dive team, and whether
closing threat tracks can be interdicted before they reach the screen.

Six pure domain modules provide these capabilities:

* `src/thunderball/dive_planner.py` — air-budget and Bühlmann ZH-L16A
  decompression planning.
* `src/thunderball/convoy_integrity.py` — convoy-screen gap detection, escort
  coverage, and an integrity score.
* `src/thunderball/submersible_logistics.py` — power, endurance, range, and
  optimal-cruise analysis.
* `src/thunderball/sonar_detection.py` — Thorp absorption, transmission loss,
  signal excess, and detection range.
* `src/thunderball/current_navigation.py` — set-and-drift dead reckoning,
  course-to-steer, and cross-track error.
* `src/thunderball/interdiction_analysis.py` — closest-point-of-approach
  geometry and screen-penetration verdicts.

The package is a BOND-suite film: a thin `src/thunderball/mission.py` adapter
exposes these capabilities through the frozen `bond_api` `MissionProvider`
protocol, so the *orchestrator* can discover and drive the mission
deterministically. The domain modules themselves are standalone and never
import infrastructure.

This manuscript documents the mathematical models (@sec:methodology), the
computed results (@sec:results), and the reproducibility guarantees
(@sec:reproducibility) of the mission software.
