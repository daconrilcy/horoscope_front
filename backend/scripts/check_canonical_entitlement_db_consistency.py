# backend/scripts/check_canonical_entitlement_db_consistency.py
import sys
from pathlib import Path


def _ensure_backend_root_on_path() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))


def main() -> int:
    _ensure_backend_root_on_path()
    from app.infra.db.session import SessionLocal
    from app.services.canonical_entitlement.shared.db_consistency_validator import (
        CanonicalEntitlementDbConsistencyError,
        CanonicalEntitlementDbConsistencyValidator,
    )

    try:
        with SessionLocal() as db:
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
