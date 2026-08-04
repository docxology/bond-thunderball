"""Mission phase CLI: debrief — summarise the DISCO VOLANTE mission.

Thin orchestrator: plans, executes, and debriefs the mission, printing the
outcome summary and lessons learned.
"""

from __future__ import annotations

from thunderball.mission import PROVIDER


def main() -> int:
    """Run the full mission and print the debrief."""
    brief = PROVIDER.brief()
    plan = PROVIDER.plan(brief)
    outcome = PROVIDER.execute(plan)
    debrief = PROVIDER.debrief(outcome)
    print(f"mission success={debrief.outcome.success}")
    print("lessons:")
    for lesson in debrief.lessons:
        print(f"  - {lesson}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
