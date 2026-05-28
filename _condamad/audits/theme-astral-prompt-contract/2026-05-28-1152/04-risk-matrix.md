# Risk Matrix

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | High | Natal LLM output quality and contract architecture | High if future stories assume source existence equals prompt use | Medium | P0 |
| F-002 | High | Medium | Provider payload builder and gateway handoff | High if a second prompt carrier is introduced | Medium | P0 |
| F-003 | Medium | Medium | DB/reference seed ownership and material selection | Medium if selection logic is duplicated | Medium | P1 |
| F-004 | Medium | Medium | Future closure evidence and guardrails | Medium if migration cannot prove rich-source reach | Low | P1 |

## Risk Notes

No Critical risk was identified because no runtime behavior was changed and no provider call was executed. The highest risk is architectural: future enrichment must not blur DB/reference source existence with prompt-visible reachability.
