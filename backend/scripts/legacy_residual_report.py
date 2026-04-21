"""Rapport texte du registre legacy résiduel (Story 66.40 AC11)."""

from __future__ import annotations

import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))


def main() -> int:
    from app.domain.llm.governance.legacy_residual_registry import render_maintenance_report

    print(render_maintenance_report(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
