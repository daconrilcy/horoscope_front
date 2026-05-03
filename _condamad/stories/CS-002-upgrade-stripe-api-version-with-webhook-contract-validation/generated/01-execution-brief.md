# Execution Brief - CS-002

## Primary objective

Upgrade the default Stripe API version to `2026-04-22.dahlia` while preserving the existing backend billing and webhook contracts.

## Boundaries

- Scope is limited to Stripe runtime configuration, the canonical infra client, billing/webhook compatibility tests, and upgrade evidence.
- Do not recreate `backend/app/integrations/stripe_client.py`.
- Do not add a second Stripe API version setting or per-service overrides.
- Do not change public billing endpoint response shapes or status codes.

## Required preflight

- Read `00-story.md`, `AGENTS.md`, and `_condamad/stories/regression-guardrails.md`.
- Record initial `git status --short`.
- Inspect the Stripe config, infra client, billing services, webhook service, and existing Stripe tests before editing.

## Done conditions

- AC1-AC5 have code and validation evidence.
- Baseline and after evidence artifacts are persisted under `evidence/`.
- Targeted unit/integration tests and lint pass or any limitation is documented.
- Final evidence and traceability are complete.
