"""Mission phase CLI: recon — run reconnaissance for DISCO VOLANTE.

Thin orchestrator: sends a :class:`~bond_api.protocol.ReconRequest` to the
provider and prints the resulting findings.
"""

from __future__ import annotations

import sys

from bond_api.protocol import ReconRequest

from thunderball.mission import PROVIDER

DEFAULT_GOAL = "plan the underwater recovery mission for DISCO VOLANTE"


def main(argv: list[str] | None = None) -> int:
    """Run recon with an optional overridden goal."""
    args = argv if argv is not None else sys.argv[1:]
    goal = args[0] if args else DEFAULT_GOAL
    report = PROVIDER.recon(ReconRequest(goal=goal))
    for finding in report.findings:
        print(f"[{finding.label}] {finding.detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
