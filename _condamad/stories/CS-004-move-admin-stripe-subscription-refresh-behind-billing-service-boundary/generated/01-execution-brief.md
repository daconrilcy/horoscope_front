# Execution Brief - CS-004-move-admin-stripe-subscription-refresh-behind-billing-service-boundary

## Primary objective

Move the admin Stripe subscription forced-refresh orchestration out of the HTTP router and behind the canonical billing service boundary, while preserving `POST /v1/admin/users/{user_id}/refresh-subscription`.

## Boundaries

- In scope: one service-owned billing/admin use case, a thinner admin route, updated tests, runtime/OpenAPI proof, and an anti-regression guard against direct Stripe SDK calls from API routers.
- Out of scope: global admin router refactor, persistence model changes, Stripe API version changes, timeout/retry policy changes, frontend changes, and unrelated admin Stripe endpoints.
- Applicable guardrails: `RG-004`, `RG-005`, `RG-006`.

## Execution rules

- Read `../00-story.md` completely before editing code.
- Read all required generated capsule files before implementation.
- Run `git status --short` before and after code changes.
- Preserve unrelated user changes.
- Implement only the current story.
- Do not introduce compatibility wrappers, aliases, silent fallbacks, duplicate active paths, or legacy import routes unless explicitly required by the story.
- Record implementation and validation evidence in `10-final-evidence.md`.

## Halt conditions

- Stop if preserving the route contract requires changing status codes or response shape.
- Stop if a new dependency is required.
- Stop if billing services would need to import FastAPI or `app.api`.

## Done when

- Every AC in `03-acceptance-traceability.md` has code evidence and validation evidence.
- Commands in `06-validation-plan.md` have been run or explicitly documented as not run with reason and risk.
- `10-final-evidence.md` is complete.
