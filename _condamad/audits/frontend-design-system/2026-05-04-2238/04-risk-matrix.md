# Risk Matrix - frontend-design-system

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | High | All frontend styling | High | Medium | P0 |
| F-002 | High | High | Shared pages, landing, admin, dashboard, prediction UI | High | High | P0 |
| F-003 | Medium | High | Text hierarchy across all pages | Medium | Medium | P1 |
| F-004 | Medium | Medium | Components using TSX inline styles | Medium | Medium | P1 |
| F-005 | Medium | High | Token migration and theme reliability | Medium | Medium | P1 |
| F-006 | Medium | Medium | Large legacy CSS and compatibility selectors | Medium | Medium | P2 |
| F-007 | Low | High | CI and future frontend changes | Medium | Low | P1 |

## Notes

- `F-001` and `F-002` are the highest leverage risks because they define whether later cleanup can be deterministic.
- `F-007` is Low severity as an isolated gap, but should be implemented early once the canonical contract and allowlists exist.
