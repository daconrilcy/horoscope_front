# Risk Matrix

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Medium | High | Medium | Medium | Low | P1 |
| F-002 | Info | Medium | Low | Low | Medium | P3 |
| F-003 | Info | Low | Low | Low | High | P4 |

## Notes

- F-001 has low implementation effort because it is expected to touch examples and validation only, but it blocks final closure because examples are part of the audited contract.
- F-002 remains a deliberate non-interactive limitation.
- F-003 should not become a story unless the product requires real production-table coverage for every interpretive family.
