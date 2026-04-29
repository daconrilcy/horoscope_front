"""CLI de verification de coherence des droits canoniques en base."""

import sys
from pathlib import Path

from sqlalchemy.orm import Session


def _ensure_backend_root_on_path() -> None:
    """Ajoute le dossier backend au path quand le script est lance hors package."""
    backend_root = Path(__file__).resolve().parents[1]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))


def _open_canonical_entitlement_db_session() -> Session:
    """Ouvre la session ORM utilisee par la verification CLI."""
    _ensure_backend_root_on_path()
    from app.infra.db.session import SessionLocal

    return SessionLocal()


def main() -> int:
    """Retourne un code de sortie selon le resultat de coherence DB."""
    _ensure_backend_root_on_path()
    from app.services.canonical_entitlement.shared.db_consistency_validator import (
        CanonicalEntitlementDbConsistencyError,
        CanonicalEntitlementDbConsistencyValidator,
    )

    try:
        with _open_canonical_entitlement_db_session() as db:
            CanonicalEntitlementDbConsistencyValidator.validate(db)
        print("[OK] Canonical entitlement DB is consistent.")
        return 0
    except CanonicalEntitlementDbConsistencyError as exc:
        print(f"[ERROR] {exc}")
        return 1
    except Exception as exc:
        print(f"[CRITICAL] Unexpected error: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
