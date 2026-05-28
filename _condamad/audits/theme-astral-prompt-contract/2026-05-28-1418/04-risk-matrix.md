# Risk Matrix

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Info | Low | Provider runtime only; no current contract defect proven. | Low because builder, gateway, persistence, examples, and scans are guarded. | Medium; requires provider smoke or eval environment. | None for audit-only scope. |

## Residual Non-Finding Risks

| Risk | Evidence | Decision |
|---|---|---|
| Old carrier tokens still exist in non-theme flows. | E-011 | Out of domain; current theme astral tests prove they do not replace `theme_astral_llm_input_v1`. |
| Real provider quality is not evaluated by backend tests. | E-013, E-014 | Accepted for this scope; full backend tests prove local contract behavior, not provider-side qualitative interpretation. |
