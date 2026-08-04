"""Figure-rendering CLI: write all DISCO VOLANTE concept figures.

Thin orchestrator: calls
:func:`thunderball.figures.render_all_figures` and prints the written paths.
"""

from __future__ import annotations

from thunderball.figures import FIGURES_OUT, render_all_figures


def main() -> int:
    """Render every concept figure and print the paths."""
    paths = render_all_figures(figures_out=FIGURES_OUT)
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
