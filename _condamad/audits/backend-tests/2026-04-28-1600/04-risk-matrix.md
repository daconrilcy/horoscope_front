# Risk Matrix - backend-tests

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | High | Backend CI and LLM architecture guards | High: retained tests can be invisible to default runs | Medium | P0 |
| F-002 | High | High | Whole backend test organization | High: new tests can land in wrong roots and duplicate patterns | Medium | P1 |
| F-003 | High | Medium | DB-backed unit and integration tests | High: global DB rewiring can hide isolation defects | High | P1 |
| F-004 | Medium | High | Regression and No Legacy guard suites | Medium: unsafe deletion could regress protected legacy removals | Medium | P2 |
| F-005 | Medium | Medium | Test helper maintenance | Medium: hidden coupling breaks unrelated tests during cleanup | Low | P2 |
| F-006 | Medium | High | Seed validation coverage | Low: one facade test gives false confidence for a narrow rule | Low | P2 |
| F-007 | Low | Medium | Ops/docs/script governance | Low: mostly ownership confusion unless CI relies on backend pytest for ops checks | Medium | P3 |
