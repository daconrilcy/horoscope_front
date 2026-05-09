# Acceptance Traceability — CS-121

| AC | Requirement | Expected code impact | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Baseline des variables App specifiques. | `app-css-standardization-before.md` | Audit baseline + artefact before | PASS |
| AC2 | `App.css` contient les primitives generiques. | `frontend/src/App.css` | `npm run test -- design-system ...` + `rg` primitives | PASS |
| AC3 | Les primitives evitent les noms de domaine interdits. | `frontend/src/tests/design-system-guards.test.ts` | `npm run test -- design-system` | PASS |
| AC4 | Registres tokens/typographie documentes. | `token-namespace-registry.md`, `typography-roles.md` | `npm run test -- theme-tokens design-system` | PASS |
| AC5 | Aucune exception large ou alias. | `design-system-allowlist.ts`, `App.css` | `rg -n "OLD|legacy|alias|compat|compatibility|shim|migration-only" src/App.css`: zero hit | PASS |
