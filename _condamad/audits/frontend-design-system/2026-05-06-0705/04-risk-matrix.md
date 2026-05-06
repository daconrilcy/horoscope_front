# Risk Matrix - frontend-design-system

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Info | Low | Low | Low | Low | Low |
| F-002 | Medium | Medium | Low | Medium | Low | Medium |
| F-003 | Medium | Medium | Medium | Medium | Medium | Medium |
| F-004 | Medium | High | High | Medium | High | Medium |
| F-005 | Medium | Medium | Medium | Medium | Medium | Medium |
| F-006 | Info | Medium | Low | Low | Medium | Low |
| F-007 | Info | Low | Low | Low | Low | Low |

## Top Risks

1. `F-004`: large visual-literal surface keeps token convergence incomplete and makes future style changes expensive.
2. `F-005`: admin prompt legacy selectors remain consumed by runtime markup, so deletion requires a bounded migration.
3. `F-003`: inline style exceptions are guarded but still need clear API decisions for `Badge` and `Skeleton`.
