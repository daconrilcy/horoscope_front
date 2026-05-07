# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Le cluster est borne a `Settings.css`. | Modifications frontend limitees a `Settings.css` et au guard `design-system-guards.test.ts`; evidence capsule ajoutee. | Baseline before/after, `git diff --stat`, `npm run test -- design-system ...`. | PASS |
| AC2 | Chaque literal Settings a une decision finale. | `hardcoded-values-after.md` classe les literals restants comme `registered-semantic-owner`, `runtime-custom-property` ou `kept-one-off-final`. | Scans `rg` cibles et test CS-084. | PASS |
| AC3 | Les valeurs repetables utilisent un owner documente. | Selecteurs Settings consomment `--settings-*`, `--type-*`, `--font-*`, `--line-height-*`, `--radius-*`. | `npm run test -- theme-tokens design-system` via suite cible. | PASS |
| AC4 | Les exceptions restent exactes. | Aucun registre elargi; `--usage-progress` reste l'unique fallback CSS en scope. | `npm run test -- css-fallback inline-style legacy-style`, scan fallback. | PASS |
| AC5 | Les rendus Settings restent couverts. | Guard design-system CS-084 et visual-smoke executes. | `npm run test -- visual-smoke design-system`. | PASS |
| AC6 | Les literals migres ne reviennent pas. | Nouveau guard retire l'owner block puis bloque les literals dans les selecteurs rendus. | `npm run test -- design-system theme-tokens`, scans exacts. | PASS |
| AC7 | La contrainte No Legacy est respectee. | Aucun vocabulaire interdit dans `Settings.css`; pas d'alias/shim/compatibilite. | `rg` zero-hit et `npm run test -- legacy-style`. | PASS |
| AC8 | Aucune AC n'est `PASS with limitation`. | Evidence finale en PASS, aucun skip obligatoire. | Validations frontend + story lint/validate en PASS. | PASS |
