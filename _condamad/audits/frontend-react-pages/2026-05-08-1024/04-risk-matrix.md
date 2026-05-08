<!-- Matrice des risques de l'audit de continuite des pages React frontend. -->

# Risk Matrix - frontend-react-pages

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | Medium | High | Medium | High | P1 |
| F-002 | Medium | Medium | Medium | Medium | Medium | P1 |
| F-003 | Medium | Medium | Medium | Medium | Medium | P2 |
| F-004 | Medium | Medium | Medium | Medium | Medium | P2 |

## Risk Notes

- `F-001` is the highest residual architecture risk because the guard limits growth but does not finish ownership convergence.
- `F-002` and `F-004` are good closure candidates because both have exact allowlists and zero-hit stop conditions.
- `F-003` should be done through a classification-first pass to avoid merging intentionally different display rules.
