"""Mission phase CLI: execute — run the DISCO VOLANTE mission.

Thin orchestrator: plans and executes the mission, printing the provenanced
outcome results.
"""

from __future__ import annotations

from thunderball.mission import PROVIDER


def main() -> int:
    """Plan and execute the mission, printing the outcome."""
    brief = PROVIDER.brief()
    plan = PROVIDER.plan(brief)
    outcome = PROVIDER.execute(plan)
    print(f"success={outcome.success}")
    for key, value in outcome.results.items():
        print(f"{key}={value}")
    prov = outcome.provenance
    print(
        f"provenance: version={prov.package_version} seed={prov.seed} hash={prov.input_hash}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
