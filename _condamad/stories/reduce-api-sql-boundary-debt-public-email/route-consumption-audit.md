# Route Consumption Audit

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `/api/email/unsubscribe` | Public HTTP route | external-active | Liens email générés par `EmailService.get_unsubscribe_link` et clients email déjà envoyés | None in this story | keep | OpenAPI before/after contains `/api/email/unsubscribe`; integration tests pass. | Deleting or moving the route would break existing unsubscribe links. |
| Direct SQL in `backend/app/api/v1/routers/public/email.py` | API persistence debt | dead after extraction | No consumer after route delegates to `EmailService.mark_user_unsubscribed` | `backend/app/services/email/service.py` | delete | Negative route scan has no SQL/session hits; exact allowlist guard passes. | None identified. |
