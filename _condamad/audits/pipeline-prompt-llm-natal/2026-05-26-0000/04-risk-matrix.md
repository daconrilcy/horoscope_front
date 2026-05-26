# Risk Matrix - Pipeline Prompt LLM Natal

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | High | Natal LLM interpretation quality | Prompt remains based on public/legacy projection while recent canonical facts are ignored. | Medium | P1 |
| F-002 | Medium | High | Gateway message composition | Future work may assume runtime-only fields are visible to the provider. | Low | P2 |
| F-003 | Medium | Medium | LLM evidence grounding | Validation evidence may be mistaken for generation-time constraints. | Medium | P2 |
| F-004 | Medium | Medium | Natal compatibility branches | Legacy/fallback behavior can grow without exact ownership. | Medium | P2 |

