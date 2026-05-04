"""Wrapper CLI pour generer les cas QA de prediction quotidienne."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def _ensure_backend_root_on_path() -> None:
    """Ajoute la racine backend pour executer le script sans installation editable."""
    backend_root = Path(__file__).resolve().parents[1]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))


def main() -> int:
    """Execute la generation QA et retourne un code d'erreur explicite."""
    _ensure_backend_root_on_path()

    from app.services.calibration.generate_qa_cases import generate

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    generated = generate()
    if generated < 5:
        logger.error("AC1 VIOLATION: only %s case(s) generated, minimum 5 required", generated)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
