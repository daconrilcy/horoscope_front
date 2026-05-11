# Risk Matrix - frontend-landing-page

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | High | Landing CSS and all landing sections | High | Medium | P1 |
| F-002 | Medium | High | Landing visual UI in light/dark | High | Medium | P1 |
| F-003 | Medium | Medium | Hero first viewport | Medium | Low | P2 |
| F-004 | Medium | Medium | Landing head/SEO behavior | Medium | Low | P2 |
| F-005 | Info | Low | Guardrails only | Low | Low | P3 |

## Priority

1. SC-001: close F-001 first by creating a finite landing CSS ownership map.
2. SC-002: close F-002 after SC-001 by tuning light/dark values against the mapped semantic roles and screenshot/contrast evidence.
3. SC-003: close F-003 by simplifying or guarding the hero runtime loop.
4. SC-004: close F-004 separately to keep SEO/head behavior out of the visual refactor.
