# No Legacy / DRY Guardrails - CS-108

## Canonical owners

- Page ownership registry: `frontend/src/tests/page-architecture-allowlist.ts`.
- Runtime route source of truth: `frontend/src/app/routes.tsx`.
- Guard suite: `frontend/src/tests/page-architecture-guards.test.ts`.
- Historical inventory: `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md`.

## Forbidden patterns

- Route, redirect, alias, shim, wrapper or fallback for privacy/billing callbacks without sourced decision.
- Wildcard or folder-wide exception for `frontend/src/pages/**`.
- `owner: "A definir"` or equivalent anonymous owner for residual decisions.
- Physical deletion of `HomePage.tsx` or `TestimonialsSection.tsx` in this story.
- `PASS with limitation`, `TODO`, `migration-only`, `legacy`, `shim`, `alias` or hidden residual work as closure evidence.

## Required negative evidence

- Scan route table and allowlist for the five residual symbols.
- Run `npm run test -- page-architecture layout`.
- Scan final evidence and after artifacts for forbidden closure vocabulary.
- Review `git diff --stat` to confirm no page deletion or route addition.

## Exceptions

No compatibility exception is authorized.

## Review checklist

- The five residual files are still exhaustively covered.
- Any retained blocker has owner, reason and expiry/next artifact.
- No route was introduced for blocked privacy/billing pages.
- No dead candidate was deleted silently.
- Guards fail on anonymous or stale classifications.
