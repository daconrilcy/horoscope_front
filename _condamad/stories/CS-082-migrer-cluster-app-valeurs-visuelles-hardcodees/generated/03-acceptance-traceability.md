<!-- Traceabilite AC vers preuves pour CS-082. -->

# Acceptance Traceability

| AC | Status | Code evidence | Validation evidence |
|---|---|---|---|
| AC1 | PASS | `hardcoded-values-before.md`, `hardcoded-values-after.md` bornent `App.css`. | Scans `rg` cibles sur `src/App.css`. |
| AC2 | PASS | Decisions finales dans `hardcoded-values-after.md`. | Scan des livrables de preuve sans statut limite. |
| AC3 | PASS | `--app-*` dans `App.css`; registre `token-namespace-registry.md`. | `npm run test -- theme-tokens design-system` inclus dans la suite ciblee. |
| AC4 | PASS | Aucune allowlist elargie; garde `css-fallback` intacte. | `npm run test -- css-fallback inline-style legacy-style`. |
| AC5 | PASS | Aucun changement React; surfaces rendues couvertes par smoke. | `npm run test -- visual-smoke design-system`. |
| AC6 | PASS | Test `bloque le retour des literals App migres par CS-082`. | `npm run test -- design-system`. |
| AC7 | PASS | `generated/10-final-evidence.md` sans statut limite. | Scan cible des preuves finales. |

