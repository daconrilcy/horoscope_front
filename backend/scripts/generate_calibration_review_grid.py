"""Wrapper CLI pour generer une grille de revue calibration."""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_backend_root_on_path() -> None:
    """Ajoute la racine backend pour executer le script sans installation editable."""
    backend_root = Path(__file__).resolve().parents[1]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))


def main() -> int:
    """Execute la generation via le service canonique."""
    _ensure_backend_root_on_path()

    from app.services.calibration.generate_review_grid import main as service_main

    return service_main()


if __name__ == "__main__":
    sys.exit(main())
