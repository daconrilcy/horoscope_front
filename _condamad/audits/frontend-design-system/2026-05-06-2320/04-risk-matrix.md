<!-- Matrice de risque de l'audit frontend design-system apres CS-081. -->

# Risk Matrix - frontend-design-system

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Info | Low | Low | Low | Low | Monitor |
| F-002 | Medium | High | High | Medium | Medium | P1 |
| F-003 | Medium | Medium | Low | Medium | Low | P1 |
| F-004 | Low | Medium | Medium | Low | Medium | P3 |

## Top Risks

1. F-002 remains the broadest active design-system implementation risk and should be reduced through small cluster-based stories.
2. F-003 is small, but should be fixed first because it closes a No Legacy guard gap.
3. F-004 should not be mixed into token cleanup; code-splitting needs a performance/routing audit first.

## Guardrail Mapping

- F-001: `RG-044` through `RG-058`.
- F-002: `RG-044`, `RG-045`, `RG-046`, `RG-047`, `RG-048`, `RG-050`, `RG-055`, `RG-056`, `RG-058`.
- F-003: `RG-049`, `RG-050`, `RG-057`.
- F-004: no current regression guardrail; performance follow-up should define one if implemented.
