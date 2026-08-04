# Introduction

*Thunderball* (1965) is the film in which SPECTRE hijacks two NATO nuclear
bombs and the operation reaches its climax in an underwater battle around the
legendary submersible yacht, *Disco Volante*. The **DISCO VOLANTE** mission
software package implements the three quantitative planning problems that
underwrite such a recovery: how deep and how long a diver can work, whether
the escort screen protecting the high-value asset holds, and how far the
submersible powerplant can carry an assault team.

Three pure domain modules provide these capabilities:

* `src/thunderball/dive_planner.py` — air-budget and Bühlmann ZH-L16A
  decompression planning.
* `src/thunderball/convoy_integrity.py` — convoy-screen gap detection, escort
  coverage, and an integrity score.
* `src/thunderball/submersible_logistics.py` — power, endurance, range, and
  optimal-cruise analysis.

The package is a BOND-suite film: a thin `src/thunderball/mission.py` adapter
exposes these capabilities through the frozen `bond_api` `MissionProvider`
protocol, so the *orchestrator* can discover and drive the mission
deterministically. The domain modules themselves are standalone and never
import infrastructure.

This manuscript documents the mathematical models (@sec:methodology), the
computed results (@sec:results), and the reproducibility guarantees
(@sec:reproducibility) of the mission software.
