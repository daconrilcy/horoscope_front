# Acceptance Traceability - CS-079

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Le cluster est borne uniquement aux composants UI selectionnes. | Migration limitee a `frontend/src/components/ui/**`, avec un consommateur direct `frontend/src/components/ShortcutsSection.tsx` pour supprimer `var(--primary)`. | `hardcoded-values-before.md`, `git diff --stat -- frontend`. | PASS |
| AC2 | Toutes les valeurs ont une decision finale. | `hardcoded-values-after.md` classe les valeurs en `migrated`, `registered-semantic-owner` ou one-off final. | `rg -n "TODO|PASS with limitation|legacy" hardcoded-values-after.md` - zero hit attendu. | PASS |
| AC3 | Les valeurs repetees migrent vers owners canoniques non legacy. | Tokens ajoutes dans `frontend/src/styles/design-tokens.css`; roles documentes dans `frontend/src/styles/typography-roles.md`; CSS UI consomme ces tokens. | `npm run test -- theme-tokens design-system` via commande combinee story. | PASS |
| AC4 | Aucun fallback CSS ou namespace non canonique n'est introduit. | `Skeleton.tsx` utilise `var(--space-2)` sans fallback; aucun namespace hors registres canoniques. | `npm run test -- css-fallback legacy-style`; scan No Legacy zero hit. | PASS |
| AC5 | Les primitives UI restent couvertes par les guards frontend. | `frontend/src/tests/design-system-guards.test.ts` ajoute le guard CS-079. | `npm run test -- design-system visual-smoke` via commande combinee story. | PASS |
| AC6 | Les literals migres ne peuvent pas revenir silencieusement. | Guard CS-079 et scans exacts des literals migres. | Scan exact des literals migres - zero hit; `npm run lint`. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
