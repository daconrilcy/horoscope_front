<!-- Matrice des risques de l'audit frontend design-system. -->

# Risk Matrix - frontend-design-system

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Info | Low | Low | Low | Low | Monitor |
| F-002 | Medium | High | High | Medium | Medium | P1 |
| F-003 | Info | Low | Low | Low | Low | Monitor |
| F-004 | Low | Medium | Medium | Low | Medium | P3 |

## Top Risks

1. F-002 is the only active design-system implementation risk. It is broad but should be reduced through small, cluster-based stories.
2. F-004 should not be mixed into token cleanup; code-splitting needs a performance/routing audit first.

## Guardrail Mapping

- F-001: `RG-044` through `RG-057`.
- F-002: `RG-044`, `RG-045`, `RG-046`, `RG-047`, `RG-048`, `RG-050`, plus `RG-055`/`RG-056` when relevant.
- F-003: `RG-051`, `RG-052`, `RG-053`, `RG-054`, `RG-057`.
- F-004: no current regression guardrail; performance follow-up should define one if implemented.
