<!-- Matrice de risques du nouvel audit frontend design-system. -->

# Risk Matrix - frontend-design-system

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Info | Low | Low | Low | Low | Monitor |
| F-002 | Medium | High | High | Medium | Medium | P1 |
| F-003 | Info | Low | Low | Low | Low | Monitor |
| F-004 | Low | Medium | Medium | Low | Medium | P3 |

## Rationale

- `F-002` remains the only implementation story candidate because it is the active DRY/design-system ownership risk.
- `F-004` is intentionally separated from design-system work because it is a bundle performance concern, not a token or No Legacy defect.
