# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Le cluster est borne aux CSS admin selectionnes. | Changements limites aux CSS admin, registres/guards design-system et evidence CS-086. | `hardcoded-values-before.md`, `hardcoded-values-after.md`, `git diff --stat`, path scan admin. | PASS |
| AC2 | Chaque literal admin selectionne a une decision finale. | Mapping vers tokens globaux, roles typographiques, variables admin semantiques ou decision finale documentee. | After artifact, `npm run test -- design-system`, scans cibles. | PASS |
| AC3 | Les valeurs repetables utilisent un owner documente. | Mise a jour tokens/admin namespace/roles typographiques si necessaire. | `npm run test -- theme-tokens design-system`, diff registres. | PASS |
| AC4 | Aucune exception admin large n'est creee. | Pas d'elargissement allowlist inline/css-fallback/legacy-style. | `npm run test -- css-fallback inline-style legacy-style`, scan fallback. | PASS |
| AC5 | Les rendus admin restent couverts sans changement fonctionnel. | CSS only; garde visual-smoke maintenue. | `npm run test -- visual-smoke design-system`, `npm run build`. | PASS |
| AC6 | Les literals migres ne reviennent pas. | Guard anti-retour admin dans `design-system-guards.test.ts`. | `npm run test -- design-system theme-tokens`, scans exacts after. | PASS |
| AC7 | La contrainte No Legacy est respectee. | Aucun vocabulaire No Legacy actif non classe dans les CSS touches. | `npm run test -- legacy-style`, scan vocabulaire interdit et classification des hits metier. | PASS |
| AC8 | Aucune AC n'est acceptee avec limitation. | Evidence finale uniquement en `PASS` ou blocker explicite. | Scan story/capsule execute et hits attendus limites au texte de contrat. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
