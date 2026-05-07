<!-- Matrice de risques pour l'audit frontend design-system apres refactors. -->

# Risk Matrix - frontend-design-system

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Info | Low | Low | Low | Low | Monitor |
| F-002 | Medium | High | High | Medium | Medium | P1 |
| F-003 | Info | Low | Low | Low | Low | Monitor |
| F-004 | Low | Medium | Medium | Low | Medium | P3 |

## Rationale

- `F-001`: guardrails are active and validated; residual risk is future drift if they are skipped.
- `F-002`: 68 candidate files still contain local visual or typography literals, so duplicate ownership can continue to grow if migrations stop.
- `F-003`: previously open legacy and compatibility surfaces are closed by targeted scans and guard tests.
- `F-004`: build passes, but Vite still warns that the main chunk is above 500 kB.

## Guardrail Mapping

- `F-001`: `RG-044` through `RG-060`.
- `F-002`: `RG-044`, `RG-045`, `RG-046`, `RG-050`, `RG-055`, `RG-056`, `RG-058`, `RG-059`.
- `F-003`: `RG-049`, `RG-051`, `RG-052`, `RG-053`, `RG-054`, `RG-057`, `RG-060`.
- `F-004`: no direct design-system guardrail; performance follow-up only.
