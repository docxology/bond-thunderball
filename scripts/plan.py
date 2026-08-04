"""Mission phase CLI: plan — generate the DISCO VOLANTE mission plan.

Thin orchestrator: calls :meth:`provider.plan` with the provider's own brief
and prints the resulting steps.
"""

from __future__ import annotations

from thunderball.mission import PROVIDER


def main() -> int:
    """Build and print the mission plan."""
    brief = PROVIDER.brief()
    plan = PROVIDER.plan(brief)
    for step in plan.steps:
        print(f"{step.name}: {step.action} {step.params}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
