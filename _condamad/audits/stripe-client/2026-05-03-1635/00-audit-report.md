# Audit Report - stripe-client

## Audit Metadata

- Audit folder: `_condamad/audits/stripe-client/2026-05-03-1635`
- Date: 2026-05-03
- Skill: `condamad-domain-auditor`
- Mode: read-only application audit; audit artifacts only
- Target domain: `stripe-client`
- Primary archetype: `service-boundary-audit`
- Supporting archetypes: `test-guard-coverage-audit`, `legacy-surface-audit`, `contract-shape-audit`

## Target Boundary

In scope:

- Stripe SDK client ownership and version configuration.
- Stripe webhook dispatch, event registry, user resolution, and idempotency retry outcome.
- Public webhook route contract only where needed to prove service outcome mapping.
- Local webhook docs and PowerShell listener parity.
- Targeted tests and static scans for No Legacy / DRY / dependency direction.

Out of scope:

- Full billing product behavior outside Stripe client/webhook integration.
- Frontend billing UI.
- Live Stripe account configuration.
- Production Stripe Dashboard webhook endpoint settings beyond local config/docs evidence.

## Applicable Guardrails

- `RG-004` - API errors stay centralized.
- `RG-005` - API must not own business logic.
- `RG-006` - non-API layers must not import `app.api`.
- `RG-023` - root scripts must remain owned.
- `RG-024` - local Stripe listener stays opt-in and PowerShell-oriented for local dev.

## Executive Result

No new actionable finding.

The previous Stripe implementation findings from `_condamad/audits/stripe-implementation/2026-05-03-1003` are resolved or guarded in the audited target:

- F-001 retry semantics: resolved by retryable HTTP 500 for signed processing failure.
- F-002 Stripe API version: resolved with explicit `2026-04-22.dahlia` version usage.
- F-003 supported webhook event ownership: resolved with canonical registry and parity tests.
- F-006 infra ownership: resolved with `app.infra.stripe.client` and legacy-path guard.

## Finding Summary

| ID | Severity | Summary | Status |
|---|---|---|---|
| F-001 | Info | Signed webhook failure semantics are now retryable. | Resolved / guarded |
| F-002 | Info | Stripe API version default is current and explicit. | Resolved / guarded |
| F-003 | Info | Supported webhook events have one service-owned registry. | Resolved / guarded |
| F-004 | Info | Stripe client ownership respects service/infra boundaries. | Resolved / guarded |
| F-005 | Info | Legacy payment surfaces remain absent. | No issue detected |

## Evidence Highlights

- E-004 proves the SDK client is owned by `backend/app/infra/stripe/client.py` and guarded by `test_stripe_client.py`.
- E-005 proves runtime dispatch and user resolution consume `stripe_webhook_events.py`.
- E-006 proves signed processing failure maps to HTTP 500 and retry-from-failed behavior is covered.
- E-008 and E-009 prove no API adapter or FastAPI/HTTP response dependency in the audited service/infra target.
- E-013 and E-014 prove lint and targeted tests pass.
- E-015 proves runtime OpenAPI still exposes `POST /v1/billing/stripe-webhook`.

## DRY / No Legacy Assessment

PASS.

The active runtime source of truth for supported Stripe webhook events is `backend/app/services/billing/stripe_webhook_events.py`. Docs and the PowerShell listener still contain literal event names because they are executable or human-facing assets, but tests compare those assets to the registry, so they are guarded parity surfaces rather than independent runtime owners.

The old `app.integrations.stripe_client` path is absent from active backend code and guarded by tests. Historical references remain in `_condamad` story/audit documents only.

## Dependency Direction Assessment

PASS.

Scans found no `app.api` imports and no FastAPI/HTTP response types in `backend/app/services/billing` or `backend/app/infra/stripe`. The API router remains the HTTP adapter that maps service outcomes to HTTP responses.

## Security / Policy Assessment

PASS for the audited target.

Webhook signature rejection and missing-secret handling remain covered by integration tests. Targeted scans found no active legacy Stripe payment APIs, raw card collection surfaces, or live Stripe secret patterns in audited code/docs/scripts.

## Validation Summary

Commands were executed with the Python venv activated before Python-based lint/tests/runtime checks.

- `ruff check app/infra/stripe/client.py app/services/billing/stripe_webhook_events.py app/services/billing/stripe_webhook_service.py app/tests/unit/test_stripe_client.py app/tests/unit/test_stripe_webhook_service.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/integration/test_stripe_webhook_api.py` - PASS.
- `pytest -q app/tests/unit/test_stripe_client.py app/tests/unit/test_stripe_webhook_service.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/integration/test_stripe_webhook_api.py` - PASS, 43 tests.
- Runtime OpenAPI assertion for `/v1/billing/stripe-webhook` - PASS.
- Targeted boundary and legacy scans - PASS.

## Story Candidate Summary

No new story candidates.

The only follow-up worth considering later is a dedicated regression guardrail that names `backend/app/services/billing/stripe_webhook_events.py` as the canonical owner if future stories change supported Stripe event behavior.
