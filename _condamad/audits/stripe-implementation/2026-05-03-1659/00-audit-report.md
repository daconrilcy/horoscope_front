# Audit Report - stripe-implementation

## Audit Metadata

- Audit folder: `_condamad/audits/stripe-implementation/2026-05-03-1659`
- Date: 2026-05-03
- Skill: `condamad-domain-auditor`
- Mode: read-only application audit; audit artifacts only
- Target domain: `stripe-implementation`
- Primary archetype: `service-boundary-audit`
- Supporting archetypes: `api-adapter-boundary-audit`, `legacy-surface-audit`, `contract-shape-audit`, `test-guard-coverage-audit`, `observability-audit`

## Target Boundary

In scope:

- Stripe public billing API routes.
- Stripe admin actions in API routers.
- Stripe checkout, customer portal, profile sync, webhook, and idempotency services.
- Infra Stripe client and startup portal validation.
- Local Stripe docs/scripts and ownership guardrails.
- Targeted Stripe test inventory, runtime OpenAPI inventory, dependency scans, No Legacy scans, and security scans.

Out of scope:

- Frontend billing UI implementation.
- Live Stripe account/Dashboard configuration.
- B2B billing not backed by Stripe.
- Full repository-wide persistence refactor beyond Stripe billing evidence.

## Applicable Guardrails

- `RG-004` - API error envelopes stay centralized.
- `RG-005` - API must not own business logic or persistence behavior.
- `RG-006` - non-API layers must not import `app.api`.
- `RG-023` - root scripts must remain owned.
- `RG-024` - Stripe local listener stays opt-in via local dev stack.

## Executive Result

The earlier Stripe correction stories are implemented and guarded, but the broader Stripe implementation still has one active high-severity boundary violation and one medium robustness gap.

## Finding Summary

| ID | Severity | Summary | Story candidate |
|---|---|---|---|
| F-001 | High | Admin forced subscription refresh directly owns Stripe SDK orchestration in an API route. | yes |
| F-002 | Medium | Stripe external calls lack an app-owned timeout/retry policy. | yes |
| F-003 | Medium | Stripe billing persistence remains service-coupled; target architecture needs user decision. | needs-user-decision |
| F-004 | Info | Previous Stripe correction stories are resolved or guarded. | no |
| F-005 | Info | Core Stripe security and No Legacy controls are present. | no |

## Evidence Highlights

- E-005 proves runtime OpenAPI exposes public Stripe billing routes and admin Stripe-related routes.
- E-006 and E-007 prove `refresh_subscription` owns direct Stripe SDK orchestration in the API router.
- E-008 and E-009 prove services/infra do not import API adapters or FastAPI HTTP types.
- E-011 proves no explicit timeout/retry policy exists in the audited Stripe client/call-site surface.
- E-013 and E-014 prove the previous event registry and Stripe API version corrections remain present.
- E-017 and E-018 prove targeted lint and 153 targeted tests pass.

## DRY / No Legacy Assessment

Mostly PASS, with one active ownership drift.

The canonical webhook event registry and infra Stripe client are now guarded. The old `app.integrations.stripe_client` path is not active. Local Stripe development is owned by `scripts/stripe-listen-webhook.ps1` and opt-in through `scripts/start-dev-stack.ps1 -WithStripe`.

The exception is admin forced subscription refresh: it creates a second active Stripe use-case owner in the API router by directly calling the SDK and assembling profile-sync payloads.

## Dependency Direction Assessment

Partial PASS.

Services and infra pass dependency scans against `app.api` imports and HTTP response types. The API adapter boundary does not fully pass because `backend/app/api/v1/routers/admin/users.py` performs direct Stripe SDK orchestration instead of delegating that use case to the service layer.

## Runtime Contract Assessment

PASS for previously corrected public Stripe flows.

Targeted tests cover checkout, portal sessions, subscription update/cancel flows, subscription upgrade, webhook signature/error/idempotency behavior, local webhook docs/script parity, startup portal validation, and admin Stripe actions.

The runtime OpenAPI route inventory includes:

- `/v1/billing/stripe-checkout-session`
- `/v1/billing/stripe-customer-portal-session`
- `/v1/billing/stripe-customer-portal-subscription-update-session`
- `/v1/billing/stripe-customer-portal-subscription-cancel-session`
- `/v1/billing/stripe-subscription-reactivate`
- `/v1/billing/stripe-subscription-upgrade`
- `/v1/billing/stripe-webhook`
- `/v1/admin/users/{user_id}/refresh-subscription`
- `/v1/admin/users/{user_id}/reveal-stripe-id`
- `/v1/admin/logs/stripe`

## Security / Robustness Assessment

Security scans pass for the audited source: no live Stripe secrets, raw card collection, Card Element, Charges, Sources, or Tokens were found.

Robustness remains incomplete because the app does not declare central timeout/retry behavior for Stripe external calls. That is not a failing test today, but it is operationally relevant for payment-provider availability and should be made explicit.

## Validation Summary

Commands were executed with the Python venv activated before Python-based lint/tests/runtime checks.

- Targeted `ruff check`: PASS.
- Targeted Stripe pytest suite: PASS, `153 passed`.
- Runtime OpenAPI inventory: PASS.
- Service/infra dependency scans: PASS.
- Secret and legacy payment API scans: PASS.

## Story Candidate Summary

- `SC-001`: Move admin Stripe subscription refresh behind a billing service boundary.
- `SC-002`: Define a central Stripe timeout and retry policy.

One additional item, F-003, requires user decision before becoming a story because the repository currently tolerates direct SQLAlchemy access inside billing services.
