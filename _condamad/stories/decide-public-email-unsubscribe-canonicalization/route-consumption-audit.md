# Route Consumption Audit

## Summary

`GET /api/email/unsubscribe` is `external-active`.

The repository still generates this public URL in outbound email flows, and emails already sent before this story may contain the historical URL outside repository control. Deletion or migration therefore requires a future explicit user decision and a bounded transition plan.

## Classification table

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `/api/email/unsubscribe` | public HTTP route | external-active | `EmailService.get_unsubscribe_link`, onboarding email templates through `unsubscribe_url`, integration tests, OpenAPI, already-sent emails outside repository control | none selected | needs-user-decision | `rg` consumer scan; OpenAPI/runtime snapshots; prior removal audit | Breaking links in emails already sent if removed or migrated without transition |
| `EmailService.get_unsubscribe_link` | link generator | canonical-active | onboarding email tasks | none selected | keep | `backend/app/services/email/service.py` generates `/api/email/unsubscribe?token=` | New outbound emails keep using the public historical route |
| `backend/app/api/v1/routers/public/email.py::unsubscribe` | runtime handler | canonical-active for selected decision | FastAPI route registered through `API_ROUTE_MOUNT_EXCEPTIONS` with `/api` prefix | none selected | keep | runtime route inventory shows one `GET /api/email/unsubscribe` owner | Handler still contains route-level DB work, outside this story scope |
| `backend/tests/integration/test_email_unsubscribe.py` | integration tests | test_guard_expected_hit | validates public URL success/error behavior | none selected | keep | targeted integration test | Tests intentionally preserve governed public behavior while the target decision is pending |

## Public route hardening

- The route remains a public `GET` endpoint to preserve already-sent email links.
- Responses include `Cache-Control: no-store` to avoid caching token-bearing requests.
- A signed token for an absent user preserves the existing `400` contract while the target decision remains pending.
- Invalid or expired tokens still fail with `400`.
- The unexpected-error log entry uses a stable event name and does not interpolate the token or query string.

## Scan evidence

Command:

```powershell
rg -n "api/email/unsubscribe|/email/unsubscribe|get_unsubscribe_link|unsubscribe_url" backend frontend _condamad
```

Classification:

- `backend/app/services/email/service.py`: active canonical link generator and active consumers for template variables.
- `backend/app/templates/emails/*.html`: active template consumption through `unsubscribe_url`.
- `backend/tests/integration/test_email_unsubscribe.py`: expected behavior tests.
- `backend/app/api/route_exceptions.py`: exact exception register.
- `_condamad/**`: historical audit/story evidence.

Duplicate handler scan:

```powershell
rg -n "def unsubscribe|/unsubscribe|api/email/unsubscribe" backend/app
```

Result classification:

- one handler: `backend/app/api/v1/routers/public/email.py::unsubscribe`;
- one route exception entry: `backend/app/api/route_exceptions.py`;
- one link generator: `backend/app/services/email/service.py`.
