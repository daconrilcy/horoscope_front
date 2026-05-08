# CS-109 - No Legacy / DRY guardrails

## Canonical paths

- Route tree: `frontend/src/app/routes.tsx`.
- Page ownership registry: `frontend/src/tests/page-architecture-allowlist.ts`.
- Architecture guards: `frontend/src/tests/page-architecture-guards.test.ts`.
- Billing callback defaults: `backend/app/core/config.py`.

## Forbidden

- `frontend/src/pages/HomePage.tsx`.
- `HomePage` route, export, wrapper, alias, shim, fallback or re-export.
- `/billing` compatibility retry route for checkout cancel.
- `PrivacyPolicyPage`, `BillingSuccessPage`, or `BillingCancelPage` as active `needs-user-decision`.
- `TestimonialsSection` as active `dead/unmounted-page-candidate`.
- Audit/current evidence claiming `F-201` is still active blocked after CS-109.
- Wildcard or folder-wide page architecture exception.

## Required negative evidence

- Zero active `HomePage` reference under route tree, page barrel and allowlist.
- `HomePage.tsx` absent from `frontend/src/pages`.
- No active stale blocker wording in audit 1914 or final evidence after CS-109.
- Page architecture tests pass.
