# Implementation Plan

## Current findings

- `public/email.py` owns token decoding and direct SQL update.
- `EmailService` already owns unsubscribe token generation and marketing email decisions, so it is the canonical service target.
- The SQL allowlist currently contains seven `public/email.py` rows: SQLAlchemy import, Session import, UserModel import, get_db_session import, dependency injection, `db.execute`, and `db.commit`.
- RG-006 and RG-008 apply.

## Selected approach

1. Capture OpenAPI and SQL before snapshots.
2. Add `EmailService.mark_user_unsubscribed(db, user_id)` in `backend/app/services/email/service.py`.
3. Change route dependency from DB session to a service callable, preserving tests through FastAPI dependency override.
4. Remove stale allowlist rows for `app/api/v1/routers/public/email.py`.
5. Persist after snapshots and final evidence.

## Files to modify

- `backend/app/api/v1/routers/public/email.py`
- `backend/app/services/email/service.py`
- `backend/tests/integration/test_email_unsubscribe.py`
- `backend/app/tests/unit/test_api_router_architecture.py`
- `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md`
- Story evidence files under `_condamad/stories/reduce-api-sql-boundary-debt-public-email/`

## Tests to add or update

- Add/adjust integration proof that the route delegates via overrideable service dependency and still persists.
- Add/adjust architecture guard for `public/email.py` forbidden SQL/session symbols if existing exact allowlist guard is not sufficient.

## No Legacy stance

- No route deletion.
- No compatibility wrapper.
- No duplicate unsubscribe persistence path.
- Stale SQL allowlist rows are deleted, not repointed.

## Rollback strategy

Revert only this story’s changed files if validations expose an unsafe behavior change.
