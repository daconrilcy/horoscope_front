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
        description="Emit SLA alerts for canonical entitlement mutations."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Calculate candidates without writing to DB or sending webhooks",
    )
    parser.add_argument("--limit", type=_positive_int, help="Maximum number of alerts to emit")
    args = parser.parse_args()

    from app.infra.db.session import SessionLocal
    from app.services.canonical_entitlement_alert_service import CanonicalEntitlementAlertService

    try:
        with SessionLocal() as db:
            result = CanonicalEntitlementAlertService.emit_sla_alerts(
                db,
                dry_run=args.dry_run,
                limit=args.limit,
            )

            if not args.dry_run:
                db.commit()

            status = "OK" if result.failed_count == 0 else "PARTIAL"
            print(
                f"[{status}] emitted={result.emitted_count} "
                f"skipped_duplicate={result.skipped_duplicate_count} "
                f"failed={result.failed_count} "
                f"candidates={result.candidate_count}"
            )

            if result.failed_count > 0:
                return 1
            return 0

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
