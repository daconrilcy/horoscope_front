# Execution Brief

- Story key: `decide-public-email-unsubscribe-canonicalization`
- Objective: classify the public historical route `GET /api/email/unsubscribe` and persist the target decision.
- Selected path: because generated email links and already-sent emails make the route `external-active`, keep runtime behavior unchanged and record `needs-user-decision` until explicit permanence, migration, or deletion approval exists.
- Boundaries: only `backend/app/api`, targeted email tests, and this story evidence may change.
- Non-goals: no unsubscribe business logic change, no new canonical route, no redirect, no wrapper, no hidden allowlist, no frontend change without a concrete consumer.
- Preflight required: read `AGENTS.md`, story, regression guardrails, current route exception register, public email router, email service, unsubscribe integration tests, and API router architecture tests.
- Completion definition: decision record, consumption audit, before/after OpenAPI and runtime snapshots, exact route exception metadata, architecture guard, integration behavior test, lint, and final evidence.
- Halt condition: do not remove or migrate `/api/email/unsubscribe` without explicit user approval because the route is externally active.
