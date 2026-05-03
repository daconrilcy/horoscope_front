# CONDAMAD Code Review

## Review target

- Story: `CS-003-centralize-supported-stripe-webhook-event-ownership`
- Source: `_condamad/stories/CS-003-centralize-supported-stripe-webhook-event-ownership/00-story.md`
- Verdict: `CLEAN`

## Inputs reviewed

- Story contract and generated capsule evidence.
- Regression guardrails registry: `_condamad/stories/regression-guardrails.md`.
- Diff for backend service, registry, unit/integration tests, docs, PowerShell listener, and story status.
- Untracked story capsule files and untracked `backend/app/services/billing/stripe_webhook_events.py`.

## Diff summary

- Added `backend/app/services/billing/stripe_webhook_events.py` as the canonical billing-owned registry.
- Refactored `StripeWebhookService.handle_event` and `_resolve_user_id` to consume registry-derived event groups.
- Updated docs, local PowerShell listener, unit tests, and integration test coverage for registry parity and `invoice.payment_succeeded` ignored behavior.
- Added CONDAMAD evidence artifacts for baseline/after parity.

## Review layers

- Diff integrity: story-scoped changes only; no generated cache, dependency, or secret changes found.
- Acceptance audit: AC1-AC5 mapped to implementation and passing targeted validation.
- Validation audit: required commands were rerun by reviewer in the activated venv where Python was involved.
- DRY / No Legacy audit: no active duplicate dispatch/resolver event tuples found; docs/script event strings are guarded by registry-importing tests.
- Guardrail audit: RG-005, RG-006, and RG-024 evidence present; API ownership was not moved, services do not import `app.api`, and Stripe local listener remains PowerShell opt-in.

## Findings

No actionable findings.

## Acceptance audit

| AC | Result | Evidence |
|---|---|---|
| AC1 | PASS | `stripe_webhook_events.py` lives under `app.services.billing`; no `app.api` imports found from service/domain/infra/core scans. |
| AC2 | PASS | `handle_event` uses `is_supported_webhook_event(event_type)` and `CHECKOUT_UPGRADE_EVENT_TYPES`; service tests pass. |
| AC3 | PASS | `_resolve_user_id` uses registry-derived resolver groups; service tests pass. |
| AC4 | PASS | PowerShell listener equals `LOCAL_LISTENER_EVENT_TYPES`; docs include all `SUPPORTED_WEBHOOK_EVENT_TYPES`; local asset tests pass. |
| AC5 | PASS | `invoice.payment_succeeded` remains absent from the registry and returns `event_ignored` in integration coverage. |

## Validation audit

Reviewer commands:

| Command | Result |
|---|---|
| `git diff --check` | PASS; line-ending warnings only. |
| `rg -n "from app\.api|import app\.api" backend/app/services backend/app/domain backend/app/infra backend/app/core` | PASS; no hits. |
| `rg -n "stripe-listen-webhook\.sh" scripts docs backend/app/tests` | PASS; no hits. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff check app/services/billing/stripe_webhook_events.py app/services/billing/stripe_webhook_service.py app/tests/unit/test_stripe_webhook_service.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/integration/test_stripe_webhook_api.py` | PASS. |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_stripe_webhook_service.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/integration/test_stripe_webhook_api.py` | PASS, 38 passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -c "from app.main import app; assert '/v1/billing/stripe-webhook' in app.openapi()['paths']"` | PASS. |
| `rg -n "subscription_schedule|checkout.session.async_payment_succeeded" backend/app/services/billing docs scripts backend/app/tests` | PASS; hits classified as registry, guarded docs/script/tests, and existing billing profile schedule handling. |

## DRY / No Legacy audit

- No compatibility wrapper, alias, re-export, or second runtime registry found.
- `handle_event` and `_resolve_user_id` no longer embed the reviewed async checkout or schedule event strings.
- Docs and script still contain human-facing event names, but parity tests import the canonical registry.
- Forbidden Bash listener path remains absent.

## Residual risks

- `git ls-files --others --exclude-standard` reports permission warnings for existing pytest artifact directories; reviewed untracked files relevant to the story were inspected.
- The docs parity guard was strengthened after review to ensure supported events are documented as supported and `invoice.payment_succeeded` remains documented as replaced/ignored, not supported.

## Verdict

`CLEAN`
