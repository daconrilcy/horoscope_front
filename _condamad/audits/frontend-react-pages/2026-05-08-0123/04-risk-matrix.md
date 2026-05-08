<!-- Matrice des risques de l'audit CONDAMAD des pages React du frontend. -->

# Risk Matrix - frontend-react-pages

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | High | High | High | High | P1 |
| F-002 | High | High | High | High | Medium | P1 |
| F-003 | Medium | High | Medium | Medium | Medium | P2 |
| F-004 | Medium | Medium | Medium | Medium | Low | P2 |
| F-005 | Medium | Medium | Medium | Medium | Low | P2 after user decision |
| F-006 | Medium | High | Medium | Medium | Low | P1 guardrail |

## Risk Notes

- `F-001` and `F-002` should be treated as architecture risks, not style cleanup.
- `F-005` is intentionally classified as `needs-user-decision` because route aliases may be public product contracts.
- Existing design-system guardrails reduce CSS drift risk but do not materially reduce the React page ownership risk found here.
