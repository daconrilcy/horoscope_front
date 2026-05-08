<!-- Matrice de risques de l'audit CONDAMAD sur les layouts frontend. -->

# Risk Matrix - frontend-layouts

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | High | High | High | Medium | P1 |
| F-002 | High | High | Medium | High | Low | P1 |
| F-003 | High | Medium | Medium | Medium | Low | P2 |
| F-004 | Medium | High | Medium | High | Low | P1 |
| F-005 | High | Medium | Medium | High | Medium | P1 |

## Scoring

- Probability, blast radius, regression risk, effort, and priority use qualitative values.
- Priority values are ordered from P1 to P3.

## Priority Order

1. F-001: master layout convergence, because all other layout ownership depends on it.
2. F-002: landing bypass removal, because it is an active duplicate responsibility.
3. F-005: page file ownership inventory, because it determines whether "all pages" is actually exhaustive.
4. F-003: auth route ownership, because it may need a product decision on public chrome.
5. F-004: guards, ideally implemented with the same change set so the hierarchy cannot drift again.
