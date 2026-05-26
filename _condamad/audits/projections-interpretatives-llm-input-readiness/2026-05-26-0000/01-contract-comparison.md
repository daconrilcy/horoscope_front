# Contract Comparison

| contract | producer | consumer | main fields | hash / provenance | current-llm-use | readiness |
|---|---|---|---|---|---|---|
| `structured_facts_v1` | `StructuredFactsV1Builder` in `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py` | Projection endpoint, downstream client builders, tests | `structural_facts`, `interpretive_signals`, `dominants`, `missing_data`, `excluded_surfaces`, `hash_input` | `canonical_hash_input_json`, `source_versions`, hashable `hash_input` | available-not-injected | ready as factual source; partial as prompt contract |
| `beginner_summary_v1` | `BeginnerSummaryV1Builder` | Projection endpoint, B2C clients, tests | `allowed_fields`, `state`, `summary_items`, `display_messages`, `disclaimer_codes`, `excluded_surfaces` | stable `canonical_json`; source projection is `structured_facts_v1` | product-only | not ready as canonical LLM input |
| `client_interpretation_projection_v1` | `ClientInterpretationProjectionV1Builder` | Projection endpoint, B2C clients, tests | `plan`, `llm_input_selection`, `editorial_depth_profile`, `frontend_visibility_rules`, `sections`, `support_elements`, `audit_input` | stable `canonical_json`; source projection is `structured_facts_v1`; no prompt hash owner | product-only | partial; useful for plan/context limits, not factual prompt source |
| `AINarrativeInputContract` | `AINarrativeInputBuilder` and dataclasses in `ai_narrative_input_contracts.py` | Tests today; future scoring/narration owner by contract intent | `structural_facts`, `interpretive_signals`, `readiness_flags`, `source_versions`, `masking_policy`, `public_projection_links`, `debug_context` | source versions, persisted projection identity can carry `projection_hash`; masking policy explicit | available-not-injected | ready as recommended-target, pending architecture decision and pipeline wiring |
| `narrative_answer_audit_v1` | `UserNatalInterpretationModel`, `_apply_narrative_answer_audit`, rejected answer workflow | Persistence, audit/rejection tests | `projection_hash`, `llm_input_hash`, `prompt_version`, `provider`, `model`, `grounding_status`, `evidence_refs` | SHA-256-like hash checks and source proof validation | audit-only | ready as audit trail, not LLM input |

## Producer / Consumer Notes

- `ProjectionEndpointService` builds `structured_facts_v1` first, then dispatches to `beginner_summary_v1` or `client_interpretation_projection_v1`; this proves product projection ownership, not prompt injection.
- `AINarrativeInputBuilder` reuses `ChartInterpretationInputBuilder`; it does not consume provider, gateway or prompt files.
- `_apply_narrative_answer_audit` computes audit hashes from the persisted answer payload and LLM input identity; this is post-generation evidence, not pre-generation context.

