<!-- Matrice de risques de l'audit CONDAMAD frontend-layouts post-CS-109. -->

# Risk Matrix - frontend-layouts post-CS-109

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-301 | Medium | Medium | Medium | Medium | Low | P1 |
| F-302 | Medium | Medium | Medium | Medium | Medium | P2 |
| F-303 | Low | High | Low | Low | Low | P2 |

## Risk Notes

- F-301 is the highest practical risk because it can affect rendered layout spacing while the current validation suite remains green.
- F-302 is controlled by exact allowlists, so it is not an unbounded drift, but it remains an active exception inside the audited layout domain.
- F-303 is governance-only; runtime closure remains intact.
