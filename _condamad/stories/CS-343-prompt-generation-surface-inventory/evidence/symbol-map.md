# CS-343 Symbol Map

## AST Evidence

Collected after activating `.venv` with `python -S -B -c` AST parsing.

| Path | Key symbols |
|---|---|
| `backend/app/domain/llm/runtime/gateway.py` | `_prompt_visible_llm_astrology_input`, `_without_prompt_excluded_keys`, `LLMGateway`, `build_user_payload`, `compose_chat_messages`, `compose_structured_messages`, `_resolve_plan`, `_build_messages`, `_call_provider`, `_validate_and_normalize`, `execute_request` |
| `backend/app/domain/llm/configuration/assembly_resolver.py` | `PlanRule`, `validate_placeholders`, `build_assembly_preview`, `resolve_assembly`, `assemble_developer_prompt` |
| `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | `CanonicalOutputSchemaDefinition`, `CanonicalUseCaseContract`, `list_canonical_use_case_contracts`, `list_modern_natal_use_case_contracts`, `get_canonical_use_case_contract` |
| `backend/app/domain/llm/prompting/prompt_renderer.py` | `PromptRenderer`, `render`, `extract_placeholders`, `resolve_quality_block`, `replace` |
| `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | `LLMAstrologyInputV1Builder`, `build_llm_input_hash_material`, `_facts_block`, `_signals_block`, `_limits_block`, `_evidence_block`, `_shaping_block`, `_provenance_block`, `build` |
| `backend/app/services/llm_generation/natal/interpretation_service.py` | `_build_llm_astrology_input_v1`, `_apply_narrative_answer_audit`, `_llm_input_hash_for_audit`, `_evidence_refs_for_audit`, `NatalInterpretationService`, `interpret`, `_generate_free_short` |
