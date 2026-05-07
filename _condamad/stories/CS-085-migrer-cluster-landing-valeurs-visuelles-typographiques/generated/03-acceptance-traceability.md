# Acceptance Traceability - CS-085

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Le cluster est borne aux CSS landing. | Baseline before/after limite a `LandingLayout.css` et `pages/landing/**/*.css`. | `hardcoded-values-before.md`, `hardcoded-values-after.md`, `npm run test -- design-system`, scans path. | PASS |
| AC2 | Chaque literal landing selectionne a une decision finale. | Owners ou classifications finales documentees. | after artifact, `npm run test -- design-system`, limitation scan. | PASS |
| AC3 | Les valeurs repetables utilisent un owner documente. | CSS migre vers tokens globaux, `--premium-*`, `--landing-*` ou roles typographiques; registres mis a jour. | `npm run test -- theme-tokens design-system`, diff registres. | PASS |
| AC4 | Aucune exception landing large n'est creee. | Allowlists conservees exactes ou non modifiees. | `npm run test -- css-fallback inline-style legacy-style`, fallback scan. | PASS |
| AC5 | Les rendus landing restent couverts. | Tests de rendu existants conserves et guards executes. | `npm run test -- visual-smoke App FaqSection design-system`, `npm run build`. | PASS |
| AC6 | Les literals migres ne reviennent pas. | Guard anti-retour design-system ajoute ou ajuste. | `npm run test -- design-system theme-tokens`, scans exacts after. | PASS |
| AC7 | La contrainte No Legacy est respectee. | Aucun alias, shim, compat, fallback ou migration-only actif dans les fichiers touches. | `npm run test -- legacy-style`, scan vocabulaire interdit. | PASS |
| AC8 | Aucune AC n'est acceptee avec limitation. | Evidence finale sans limitation active. | `generated/10-final-evidence.md`, scan des artefacts generes. | PASS |
