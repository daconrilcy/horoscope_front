# Sequence - Pipeline Prompt LLM Natal

1. `/users` legacy compatibility calls `NatalInterpretationService.interpret_chart`.
2. `interpret_chart` calls `interpret` with `level="complete"` and `variant_code="free_short"`.
3. `interpret` computes degraded mode and translation labels.
4. `interpret` calls `build_chart_json`, then `build_enriched_evidence_catalog`.
5. `interpret` builds astral-point interpretations and serializes `astro_context`.
6. Branch selection:
   - `complete + free_short` -> `_generate_free_short` -> `natal_long_free`.
   - `complete + module` -> `MODULE_TO_USE_CASE_KEY[module]`.
   - `complete` -> `natal_interpretation`.
   - `short` -> `natal_interpretation_short`.
7. The service resolves entitlement plan.
8. The service builds `NatalExecutionInput`.
9. `AIEngineAdapter.generate_natal_interpretation` maps input to `LLMExecutionRequest`.
10. `LLMGateway.execute_request` resolves execution plan and prompt.
11. `_build_messages` merges `ExecutionContext.extra_context`.
12. `_build_messages` sets `chart_json_in_prompt` from `{{chart_json}} in plan.rendered_developer_prompt`.
13. `build_user_payload` emits the user data block.
14. If `chart_json_in_prompt=false`, the user data block contains `Technical Data: {chart_json}`.
15. If `chart_json_in_prompt=true`, the user data block omits `Technical Data`; `chart_json` is expected to be rendered in the developer prompt placeholder path.
16. Provider response is validated; `evidence_catalog` participates in output validation, not message construction.

