# Risk Matrix - AI Traceability Audit

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | Medium | Backend persistence, admin audit reads, rejected answer workflow | High: row IDs or request IDs could become accidental answer IDs | Medium | P1 |
| F-002 | High | High | Narrative audit integrity, grounding, rejected-answer traceability | High: generated rows could remain unauditable after migration | Medium | P1 |
| F-003 | Medium | Medium | LLM prompt/provenance storage, observability joins, future migrations | Medium: duplicate provenance storage could diverge from call logs | Medium | P2 |
| F-004 | Medium | Medium | Prompt retention, privacy, replay, migration backfill | Medium: retention choice could overstore prompts or understore audit proof | Medium | P2 |
| F-005 | Medium | Medium | Tests, architecture guards, DB migration safety | Medium: future storage can drift without field completeness checks | Low | P2 |

## Migration And Duplication Risks

- Existing persisted answer rows under `user_natal_interpretations` will need backfill rules for `answer_id`, hashes, grounding status and possible prompt evidence references.
- Existing LLM call logs expire after their configured retention window, while persisted interpretations can survive longer; joining audit rows to call logs must handle missing historical logs.
- `input_hash` in LLM observability is not automatically equivalent to CS-259 `llm_input_hash`; the implementation must either prove equivalence or store a separate canonical hash.
- Provider provenance is split between `llm_call_logs.model` and `llm_call_log_operational_metadata.executed_provider`; duplicating those fields without source routing can create drift.
- Full prompt retention has privacy risk because rendered prompts can include variable user context; `prompt_ref` plus payload snapshot needs an explicit retention and encryption policy.
