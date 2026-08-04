"""Mission phase CLI: brief — print the DISCO VOLANTE mission brief.

Thin orchestrator: delegates to the provider and prints the frozen
:class:`~bond_api.protocol.MissionBrief`.
"""

from __future__ import annotations

from thunderball.mission import PROVIDER


def main() -> int:
    """Print the mission brief and return ``0``."""
    print(PROVIDER.brief())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
