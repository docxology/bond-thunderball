"""Shared pytest configuration for the thunderball package.

* Pins ``MPLBACKEND=Agg`` so matplotlib figure tests never open a display.
* Ensures ``src/`` is importable even when pytest is invoked in an unusual
  working directory (the project ``pyproject.toml`` already sets
  ``pythonpath = [".", "src"]``; this makes it robust regardless).

No mock imports anywhere — all tests use real computation and real data.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
