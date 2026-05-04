# Risk Matrix - backend-docs

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Medium | Medium | LLM documentation placement and backend docs ownership | Medium: non-canonical prose can continue to blur backend docs ownership if left in place | Low | P1 |
| F-002 | Medium | Medium | Entitlement historical architecture and backend docs ownership | Medium: historical prose can be mistaken for active source of truth because filename/title still say canonical | Low | P1 |
| F-003 | Info | Low | LLM generated docs and executable registry validation | Medium: cleanup could break active validation if generated/executable assets are treated as passive legacy docs | Medium | monitor |
| F-004 | Info | Low | Calibration artifact placement | Low: issue is resolved; risk is reintroduction only | Low | monitor |

## Priority

1. F-001
2. F-002
3. F-003
4. F-004
