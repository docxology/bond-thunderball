"""Shared sys.path bootstrap for the thunderball CLI scripts.

Running ``python scripts/<name>.py`` directly from the package root does not
put ``src/`` on ``sys.path``; this helper inserts the project root's ``src/``
so the scripts can ``import thunderball``. Kept intentionally tiny — all
business logic lives in ``src/``.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
