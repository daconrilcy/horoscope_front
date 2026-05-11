# Risk Matrix - frontend-landing-page - 2026-05-11-1841

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Medium | Medium | Hero first viewport CSS and screenshots | Medium | Medium | P1 |
| F-002 | Medium | Medium | Landing light/dark visual hierarchy and mobile menu | Medium | Medium | P1 |
| F-003 | Low | High | Landing visual guard tests | Low | Low | P2 |
| F-004 | Info | Low | Guardrails only | Low | Low | P3 |

## Applicable Regression Guardrails

| Guardrail | Applies to findings | Audit mapping |
|---|---|---|
| RG-083 | F-002, F-003, F-004 | Dark mode visual surfaces must remain classified and readable. |
| RG-084 | F-002, F-004 | Global background remains canonical through `--premium-app-bg`. |
| RG-085 | F-002, F-004 | Dark astral background remains the single dark global background. |
| RG-086 | F-002, F-004 | Landing must not recreate `app-bg--landing`. |
| RG-087 | F-002, F-004 | Global background remains viewport-fixed and not content-height dependent. |

## Top Residual Risks

1. The landing can look visually busy while all current tests remain green.
2. Hero simplification closed the JS loop but not the CSS motion/filter budget.
3. Mobile menu theme polish is currently the clearest visual incoherence in screenshots.
