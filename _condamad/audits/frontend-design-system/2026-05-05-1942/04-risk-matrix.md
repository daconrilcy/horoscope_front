# Risk Matrix - frontend-design-system

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Info | Low | Low | Low | Low | Keep existing guardrails active. |
| F-002 | Medium | High | Medium | High | Low | Fix `visual-smoke.test.tsx` before the next frontend story relies on full-suite green. |
| F-003 | Medium | Medium | Medium | Medium | Medium | Reduce fallback allowlist in bounded batches with exact registry updates. |
| F-004 | Medium | Medium | Medium | Medium | Medium | Move removable inline styles to CSS and preserve dynamic bridges only. |
| F-005 | Medium | High | Medium | Medium | High | Continue phased hardcoded-value migration by coherent product surface. |
| F-006 | Medium | Medium | Medium | Medium | Medium | Retire legacy selectors and compatibility aliases only with canonical replacements. |

## Top Risks

1. `F-002`: the full Vitest suite is currently red, so CI or local validation cannot be treated as clean until the visual smoke guard is realigned.
2. `F-003`: fallback debt is now smaller but still an active alternate-value surface.
3. `F-005`: broad hardcoded value debt remains the largest long-term maintainability cost.

## Guardrail Mapping

| Guardrail | Findings |
|---|---|
| RG-044 | F-001, F-006 |
| RG-045 | F-001, F-005 |
| RG-046 | F-001, F-002, F-005 |
| RG-047 | F-001, F-004 |
| RG-048 | F-001, F-003 |
| RG-049 | F-001, F-006 |
| RG-050 | F-001, F-002, F-003, F-004, F-005, F-006 |
