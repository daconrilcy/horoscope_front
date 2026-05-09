# Acceptance Traceability — CS-124

| AC | Requirement | Expected code impact | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Baseline reliquats page-specific App. | `app-specificity-guard-before.md` | Artefact before | PASS |
| AC2 | Guard Vitest bloque les noms App specifiques. | `design-system-guards.test.ts` | `npm run test -- design-system` PASS | PASS |
| AC3 | Toute exception est expiree. | `design-system-allowlist.ts` | `APP_CSS_SPECIFICITY_EXCEPTIONS` vide | PASS |
| AC4 | No Legacy vocabulary absent de `App.css`. | `App.css` | Scan No Legacy zero hit | PASS |
| AC5 | Suite design-system passe. | Tests front | `npm run test -- design-system ... visual-smoke` PASS | PASS |
