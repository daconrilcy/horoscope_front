# Decision Record

## Decision

- Decision: `needs-user-decision`
- Route: `GET /api/email/unsubscribe`
- Effective owner: `backend/app/api/route_exceptions.py` for exception metadata and `backend/app/api/v1/routers/public/email.py` for runtime handling.
- Date: 2026-04-28

## Rationale

`/api/email/unsubscribe` is externally active. The backend currently generates unsubscribe links with this URL, and already-sent emails can contain the route outside repository control. Removing it, replacing it, or redirecting it without a bounded migration decision would risk breaking unsubscribe links.

## User decision

No explicit user approval was provided to make the route permanent, delete it, or migrate it. Under the story rules, this blocks a permanent target decision, deletion, and migration.

The runtime route is kept unchanged only as a governed external-active surface while that explicit decision is pending.

## Allowed differences

- OpenAPI before/after: no route path difference expected.
- Runtime route before/after: no route path difference expected.
- Code: route exception decision text may change from migration-pending language to an explicit `needs-user-decision` blocker.
- Security hardening: the existing `GET` route remains public and compatible, responses use `Cache-Control: no-store`, and application error logging avoids including token or query-string details. Existing tested success/error status codes are preserved while the target decision remains pending.

## Risk

The route remains outside `/v1` by deliberate governed exception while a target decision is pending. The risk is controlled by the exact `API_ROUTE_MOUNT_EXCEPTIONS` entry and the architecture guard that fails if non-v1 API routes grow silently.

The route remains public because email unsubscribe links must work without an authenticated web session. The accepted residual risk is token possession: anyone with the signed URL can unsubscribe the target account from marketing emails until token expiry.

## Future migration conditions

A future story may select `migrate-with-bounded-compatibility` only after explicit user approval and a migration plan covering:

- newly generated links;
- already-sent emails;
- route retirement or bounded compatibility;
- OpenAPI and runtime snapshots;
- negative guards against unbounded wrappers, aliases, redirects, or fallbacks.
