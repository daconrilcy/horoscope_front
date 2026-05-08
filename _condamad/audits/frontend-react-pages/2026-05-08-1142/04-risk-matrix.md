<!-- Matrice de risque pour l'audit CONDAMAD des pages React frontend. -->

# Risk Matrix - frontend-react-pages

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | High | High | Medium | High | P1 |
| F-002 | Medium | Medium | Medium | Medium | Medium | P2 |
| F-003 | Medium | Medium | Medium | Medium | Low | P2 |

## Risk Notes

- `F-001` remains the highest residual architecture risk because the page still has an explicit remaining-slice map from CS-096.
- `F-002` is controlled by `RG-064`, but the exact allowlist means page-size debt is still present.
- `F-003` is lower effort because the canonical helper owner and tests already exist.
