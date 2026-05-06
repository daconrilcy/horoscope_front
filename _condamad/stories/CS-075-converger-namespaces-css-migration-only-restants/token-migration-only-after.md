# After Evidence - CS-075

Date: 2026-05-06

## Decision

--settings-*, --profile-* et --astro-* reclasses semantic-extension; --default_dropshadow supprime; prose du registre rendue deterministe.

## Files

frontend/src/styles/token-namespace-registry.md; frontend/src/tests/design-system-guards.test.ts

## Scans

rg -- --default_dropshadow src: zero-hit; registry targeted legacy vocabulary: zero-hit

## Classification

- Decision: implemented without compatibility shim, alias, silent fallback, or duplicate active path.
- Remaining differences: none outside the story-declared allowed differences.
