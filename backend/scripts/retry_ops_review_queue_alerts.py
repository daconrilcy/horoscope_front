from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _ensure_backend_root_on_path() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))


def _positive_int(raw_value: str) -> int:
    parsed = int(raw_value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("--limit must be greater than 0")
    return parsed


def main() -> int:
    _ensure_backend_root_on_path()

    parser = argparse.ArgumentParser(
        description="Retry failed SLA alert deliveries for canonical entitlement mutations."
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=_positive_int)
    parser.add_argument("--alert-event-id", type=int, dest="alert_event_id")
    args = parser.parse_args()

    from app.infra.db.session import SessionLocal
    from app.services.canonical_entitlement_alert_retry_service import (
        AlertEventNotFoundError,
        AlertEventNotRetryableError,
        CanonicalEntitlementAlertRetryService,
    )

    try:
        with SessionLocal() as db:
            result = CanonicalEntitlementAlertRetryService.retry_failed_alerts(
                db,
                dry_run=args.dry_run,
                limit=args.limit,
                alert_event_id=args.alert_event_id,
            )

            if not args.dry_run:
                db.commit()

            print(
                f"[OK] retried={result.retried_count} "
                f"sent={result.sent_count} "
                f"failed={result.failed_count} "
                f"candidates={result.candidate_count}"
            )
            return 1 if result.failed_count > 0 else 0
    except AlertEventNotFoundError as exc:
        print(f"[ERROR] {exc}")
        return 2
    except AlertEventNotRetryableError as exc:
        print(f"[ERROR] {exc}")
        return 2
    except Exception as exc:
        try:
            db.rollback()
        except Exception:
            pass
        print(f"[CRITICAL] Unexpected error: {exc}")
        import traceback

        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
