# Risk Matrix

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | High | B2C projection docs and dependent builders | High: dependent stories can duplicate or invent disclaimer ownership | Medium | P1 |
| F-002 | High | Medium | Guidance responses and LLM output boundary | High: LLM-authored legal/product wording can reappear silently | Medium | P1 |
| F-003 | Medium | High | Degraded/no-time projection states | Medium: inconsistent limitation wording across plans | Low | P2 |
| F-004 | Info | Low | API/OpenAPI neutrality | Low: current runtime is neutral, but future CS-284 work must preserve it | Low | P3 |
