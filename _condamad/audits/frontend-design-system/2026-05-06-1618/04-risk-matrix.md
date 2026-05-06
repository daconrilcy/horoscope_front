<!-- Matrice de risques de l'audit frontend design-system apres refactors. -->

# Risk Matrix - frontend-design-system

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Info | Low | Frontend guard suite | Low | Low | Monitor |
| F-002 | Medium | High | 101 frontend application files | High | Medium | P1 |
| F-003 | Medium | Medium | Five frontend runtime/i18n compatibility files | Medium | Medium | P2 |
| F-004 | Low | Medium | Production bundle | Medium | High | P3 |

## Top Risks

- `F-002`: the main remaining design-system risk is broad local literal ownership across 101 candidate files. This should continue as cluster-scoped stories, not a repository-wide refactor.
- `F-003`: compatibility remnants are fewer than before, but they need classification so `RG-053` is enforceable as a concrete guard instead of a broad text scan.
