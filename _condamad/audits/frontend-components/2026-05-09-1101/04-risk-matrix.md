<!-- Matrice de risques de l'audit CONDAMAD frontend components apres CS-120. -->

# Risk Matrix - frontend-components

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Info | Low | Components, feature owners, route/layout owners | Low: scans, runtime targeted tests, architecture guards, and lint pass | None | Low |
| F-002 | Info | Low | Component architecture guard suite | Low: empty exact allowlists and passing guards block reintroduction | None | Low |
| F-003 | Info | Low | Old component owner paths and config/docs references | Low: old-path scans pass; one canonical feature config reference is classified | None | Low |

## Residual Risk

- Full frontend test suite and browser E2E were not run for this bounded closure audit.
- Risk is limited by targeted route/page/layout/panel/UI tests, component architecture and usage guards, design-system/visual-smoke guards, and TypeScript lint passing.
