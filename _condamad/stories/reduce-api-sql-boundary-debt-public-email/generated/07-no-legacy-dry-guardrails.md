# No Legacy / DRY Guardrails

## Canonical ownership

- HTTP token parsing and response mapping: `backend/app/api/v1/routers/public/email.py`.
- Unsubscribe persistence: `backend/app/services/email/service.py`.
- Route exception metadata: `backend/app/api/route_exceptions.py`, unchanged.
- SQL debt register: `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md`.

## Forbidden in this story

- New endpoint, redirect, wrapper, alias, fallback or re-export for unsubscribe.
- `sqlalchemy`, `sqlalchemy.orm.Session`, `UserModel` or `get_db_session` in `backend/app/api/v1/routers/public/email.py`.
- `db.execute`, `db.commit`, `db.rollback`, `db.add`, `db.flush`, `db.refresh`, `db.get`, `db.scalar`, `db.scalars` in the route handler.
- Any service import of `app.api`.
- Leaving stale `public/email.py` rows in the router SQL allowlist.

## Required negative evidence

- Scan route file for forbidden SQL/session symbols.
- Run exact SQL allowlist architecture guard.
- Scan allowlist for `app/api/v1/routers/public/email.py`.
- Classify any `legacy|compat|shim|fallback|deprecated|alias` hits in the touched scope.

## Allowed exceptions

- The public runtime path `/api/email/unsubscribe` remains active because it is external-active and explicitly out of scope for deletion.
- Existing unrelated SQL debt in other API routers remains governed by RG-008.

## Review checklist

- One persistence implementation exists for public email unsubscribe.
- The route delegates persistence and does not own DB/session concerns.
- No compatibility path was added.
- Tests prove behavior and guards prove non-reintroduction.
