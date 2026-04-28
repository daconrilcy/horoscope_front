# No Legacy / DRY Guardrails

## Selected classification

- `/api/email/unsubscribe` is `external-active`.
- Decision is `needs-user-decision`.
- The route is not a removable legacy facade in this story because first-party email generation emits it and already-sent emails may contain it outside repository control.

## Forbidden

- Delete `/api/email/unsubscribe` without explicit user approval.
- Add a second active unsubscribe handler.
- Add a redirect, wrapper, alias, or fallback route.
- Add hidden allowlists outside `API_ROUTE_MOUNT_EXCEPTIONS`.
- Change `EmailService.get_unsubscribe_link` unless a migration decision is approved.

## Canonical ownership

- Route exception decision: `backend/app/api/route_exceptions.py`.
- Runtime handler: `backend/app/api/v1/routers/public/email.py`.
- Link generation: `backend/app/services/email/service.py`.
- Persistent decision: `_condamad/stories/decide-public-email-unsubscribe-canonicalization/decision-record.md`.

## Required evidence

- OpenAPI before/after keeps `/api/email/unsubscribe`.
- Runtime route before/after keeps one `GET /api/email/unsubscribe` owner.
- `pytest -q app/tests/unit/test_api_router_architecture.py`.
- `pytest -q tests/integration/test_email_unsubscribe.py`.
- Consumer scan and duplicate-handler scan classified in final evidence.
