# After Evidence - CS-074

Date: 2026-05-06

## Decision

HelpPage consommait --settings-card-border et --settings-card-shadow-soft; remplacement par --help-subscription-card-* et garde page-scoped.

## Files

frontend/src/pages/HelpPage.css; frontend/src/tests/design-system-guards.test.ts; frontend/src/tests/design-system-policy.ts

## Scans

rg -- --settings- src/pages/HelpPage.css: zero-hit

## Classification

- Decision: implemented without compatibility shim, alias, silent fallback, or duplicate active path.
- Remaining differences: none outside the story-declared allowed differences.
