<!-- Matrice de risque pour l'audit frontend design-system. -->

# Risk Matrix - frontend-design-system

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Info | Low | Frontend design-system guardrails | Low | Low | P4 |
| F-002 | Info | Low | CSS fallback policy | Low | Low | P4 |
| F-003 | Info | Low | TSX inline-style policy | Low | Low | P4 |
| F-004 | Medium | High | Broad frontend CSS/TSX product surfaces | Medium | High | P2 |
| F-005 | Medium | Medium | Astrologer card styles and legacy-style guard coverage | Medium | Low | P1 |
| F-006 | Medium | Medium | Consultation i18n user-facing labels | Medium | Low | P1 |
| F-007 | Low | Medium | Frontend bundle performance | Low | Medium | P3 |

## Top Risks

1. `F-005`: the guard currently passes while an alias-named selector remains unclassified, so alias debt can survive under a green legacy-style suite.
2. `F-006`: user-visible `(Legacy)` consultation labels require a product decision before implementation.
3. `F-004`: the remaining hardcoded-value surface is broad enough that a single cleanup story would carry unnecessary regression risk.

## Guardrail Mapping

| Guardrail | Findings |
|---|---|
| RG-044 | F-001, F-004 |
| RG-045 | F-001, F-004 |
| RG-046 | F-001, F-004 |
| RG-047 | F-001, F-003 |
| RG-048 | F-001, F-002 |
| RG-049 | F-001, F-005, F-006 |
| RG-050 | F-001, F-002, F-003, F-004, F-005, F-006 |
