# After Evidence - CS-077

Date: 2026-05-06

## Decision

Redirects /admin/pricing, /admin/monitoring et /admin/personas supprimes; navigation monitoring routee vers /admin/logs; tests canoniques ajustes.

## Files

frontend/src/app/routes.tsx; frontend/src/ui/nav.ts; frontend/src/tests/AdminPage.test.tsx; frontend/src/tests/AdminPromptsRouting.test.tsx; frontend/src/tests/router.test.tsx

## Scans

rg Legacy redirects|/admin/pricing|/admin/monitoring|/admin/personas src: zero-hit

## Classification

- Decision: implemented without compatibility shim, alias, silent fallback, or duplicate active path.
- Remaining differences: none outside the story-declared allowed differences.
