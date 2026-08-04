"""Full-mission CLI: run all five stages of the DISCO VOLANTE mission.

Thin orchestrator: drives the provider through
:func:`bond_api.protocol.run_mission` and prints a stage-by-stage trace plus
the final outcome.
"""

from __future__ import annotations

from bond_api.protocol import ReconRequest, run_mission

from thunderball.mission import PROVIDER

DEFAULT_GOAL = "plan the underwater recovery mission for DISCO VOLANTE"


def main() -> int:
    """Run the full mission and print its trace."""
    print("== DISCO VOLANTE: brief ==")
    print(PROVIDER.brief())
    print("== recon ==")
    for finding in PROVIDER.recon(ReconRequest(goal=DEFAULT_GOAL)).findings:
        print(f"  [{finding.label}] {finding.detail}")
    debrief = run_mission(PROVIDER, ReconRequest(goal=DEFAULT_GOAL))
    print("== outcome ==")
    outcome = debrief.outcome
    print(f"  success={outcome.success}")
    for key, value in outcome.results.items():
        print(f"  {key}={value}")
    print("== lessons ==")
    for lesson in debrief.lessons:
        print(f"  - {lesson}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
