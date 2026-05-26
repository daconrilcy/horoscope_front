# Recommendations

## Architecture Recommendation

recommended-target: `AINarrativeInputContract`.

Use `structured_facts_v1` as the stable factual substrate and `AINarrativeInputContract` as the future canonical LLM input boundary. Keep `client_interpretation_projection_v1` and `beginner_summary_v1` as B2C projection outputs only. Keep `narrative_answer_audit_v1` as post-generation audit/provenance storage only.

## Limits

- Do not inject `client_interpretation_projection_v1` wholesale into prompts.
- Do not treat `llm_input_selection` as factuel; it is shaping editorial / product policy.
- Do not inject `frontend_visibility_rules`, `display_messages`, `support_elements` or provider/model audit metadata.
- Do not use `readiness_flags` as proof that the runtime prompt already consumes the contract.
- Do not store or expose prompt payloads or provider responses in `narrative_answer_audit_v1`.

## Next Story Candidates

1. Decide canonical natal LLM input contract around `AINarrativeInputContract` before any prompt migration.
2. Add a guard or architecture decision that prevents B2C projection shaping from becoming prompt facts by inertia.

## Guardrail Position

No update to `_condamad/stories/regression-guardrails.md` is justified by this audit alone. A durable global invariant should be added only when a future implementation story changes LLM input wiring or prompt assembly.

