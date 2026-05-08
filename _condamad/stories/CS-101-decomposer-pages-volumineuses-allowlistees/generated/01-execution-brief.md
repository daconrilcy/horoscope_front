<!-- Brief d'execution CONDAMAD genere pour CS-101. -->

# CS-101 Execution Brief

Objective: close `PAGE_SIZE_EXCEPTIONS` outside `AdminPromptsPage.tsx` without changing runtime behavior.

Boundaries:

- Touch only CS-101 page-size target pages, canonical extracted owners, `page-architecture-allowlist.ts`, and CS-101 evidence.
- Do not change backend, API contracts, pricing, quotas, rights, routes, or visual CSS.
- Do not increase `maxLines`, add wildcard exceptions, or create compatibility wrappers.

Done:

- Before and after inventories exist.
- Target page entries outside AdminPrompts are removed from `PAGE_SIZE_EXCEPTIONS`.
- Target page route files are at or below 700 lines.
- `npm run lint`, `npm run test -- page-architecture`, and targeted page tests pass or are explicitly blocked.
