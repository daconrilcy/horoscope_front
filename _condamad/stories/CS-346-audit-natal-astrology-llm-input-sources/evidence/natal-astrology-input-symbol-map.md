<!-- Commentaire global: carte des symboles sources pour l'audit CS-346. -->

# Natal Astrology Input Symbol Map

| Symbol | Owner file | Role | Evidence |
|---|---|---|---|
| `LLMAstrologyInputV1Builder` | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | Canonical LLM input assembly | E-004, E-005 |
| `PROMPT_INFLUENCING_BLOCKS` | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | Hash block source | E-004 |
| `LLM_ASTROLOGY_INPUT_DATA_ROLES` | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | Prompt/backend role source | E-004, E-012 |
| `build_llm_input_hash_material` | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | Prompt-visible hash material | E-004, E-011 |
| `StructuredFactsV1Builder` | `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py` | Facts source | E-007 |
| `AINarrativeInputBuilder` | `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` | Signal source builder | E-006 |
| `AINarrativeInputContract` | `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` | Signal contract | E-006 |
| `ClientInterpretationProjectionV1Builder` | `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` | Shaping source | E-007 |
| `compute_projection_hash` | `backend/app/domain/astrology/projections/projection_hash.py` | Canonical SHA-256 helper | E-007, E-011 |
| `_build_llm_astrology_input_v1` | `backend/app/services/llm_generation/natal/interpretation_service.py` | Runtime assembly branch | E-008, E-010 |
| `AIEngineAdapter.generate_natal_interpretation` | `backend/app/domain/llm/runtime/adapter.py` | Runtime handoff branch | E-009, E-010 |
| `_prompt_visible_llm_astrology_input` | `backend/app/domain/llm/runtime/gateway.py` | Prompt payload filter | E-009, E-012 |
