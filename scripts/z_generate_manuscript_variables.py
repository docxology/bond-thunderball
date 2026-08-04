"""Manuscript-variable hydration CLI for the DISCO VOLANTE manuscript.

Thin orchestrator: computes the ``{{TOKEN}} -> value`` map via
:func:`thunderball.manuscript_variables.generate_variables`, writes it to
``output/data/manuscript_variables.json``, and renders the concept figures.
Supports ``--allow-draft`` (unused fallback kept for CLI parity with the
BOND suite convention) and ``--now`` to pin ``GENERATION_TIMESTAMP``.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from thunderball.figures import FIGURES_OUT, render_all_figures
from thunderball.manuscript_variables import generate_variables

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_OUT = PROJECT_ROOT / "output" / "data"


def main(argv: list[str] | None = None) -> int:
    """Hydrate the token map to JSON and render figures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-draft",
        action="store_true",
        help="accepted for BOND CLI parity; results are always computed",
    )
    parser.add_argument(
        "--now",
        default=None,
        help="ISO timestamp override for GENERATION_TIMESTAMP (determinism)",
    )
    args = parser.parse_args(argv)

    now = None
    if args.now:
        now = datetime.fromisoformat(args.now.replace("Z", "+00:00"))

    variables = generate_variables(project_root=PROJECT_ROOT, now=now)
    DATA_OUT.mkdir(parents=True, exist_ok=True)
    json_path = DATA_OUT / "manuscript_variables.json"
    json_path.write_text(
        json.dumps(variables, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    render_all_figures(figures_out=str(PROJECT_ROOT / FIGURES_OUT))
    print(f"wrote {json_path} ({len(variables)} tokens)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
