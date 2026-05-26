# Risk Matrix - Configuration Prompts Placeholders Input Schema

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | High | Natal LLM configuration and future injection contract | High if prompts are changed before schema ownership | Medium | P1 |
| F-002 | Medium | High | Gateway input validation and natal runtime context | Medium because current behavior is compatibility-sensitive | Medium | P2 |
| F-003 | Medium | Medium | Prompt renderer, assembly preview, placeholder governance | Medium if new placeholders are added ad hoc | Medium | P2 |
| F-004 | Medium | Medium | Natal fallback/readiness classification | Low for supported output fallback, medium for config readiness | Low | P3 |
