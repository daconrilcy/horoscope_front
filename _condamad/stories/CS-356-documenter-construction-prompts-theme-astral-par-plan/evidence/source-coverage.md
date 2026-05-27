<!-- Commentaire global: cette evidence relie les affirmations CS-356 aux sources inspectees. -->

# CS-356 source coverage

## Sources inspectees

- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`: cartographie CS-350, owners, prompt-visible/backend-only, provider handoff, validation, repair, persistence et risques.
- `_condamad/audits/prompt-generation-cartography/2026-05-27-1800/01-surface-inventory-audit.md`: inventaire des surfaces et frontieres.
- `_condamad/audits/prompt-generation-cartography/2026-05-27-1809/02-configuration-assembly-placeholder-audit.md`: assembly, placeholders, persona, plan rules.
- `_condamad/audits/prompt-generation-cartography/2026-05-27-1822/03-runtime-gateway-handoff-audit.md`: messages provider et dernier payload avant provider.
- `_condamad/audits/prompt-generation-cartography/2026-05-27-1835/04-natal-astrology-input-audit.md`: input natal moderne et separation des blocs.
- `_condamad/audits/prompt-generation-cartography/2026-05-27-1847/05-output-validation-persistence-audit.md`: validation, repair, rejet, persistence et observability.
- `_story_briefs/cs-320-definir-differenciation-llm-front-par-plan-b2c.md`: differenciation `free`, `basic`, `premium`.
- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md` et `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md`: contrat input et non-invention.
- `_condamad/stories/CS-330-*` a `_condamad/stories/CS-342-*`: frontiere evidence/provenance/prompt et guards de livraison.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`: `NATAL_LLM_ASTROLOGY_INPUT_SCHEMA` et placeholders requis.
- `backend/app/domain/llm/configuration/assembly_resolver.py`: `resolve_assembly`, `assemble_developer_prompt`, hard policy, persona et plan rules.
- `backend/app/domain/llm/prompting/prompt_renderer.py`: rendu et politique de placeholders.
- `backend/app/domain/llm/runtime/gateway.py`: `_prompt_visible_llm_astrology_input`, `_without_prompt_excluded_keys`, `compose_structured_messages`, `compose_chat_messages`, `validate_output`, repair/fallback.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`: `LLM_ASTROLOGY_INPUT_DATA_ROLES`, `PROMPT_INFLUENCING_BLOCKS`, builder et hash material.
- `backend/app/services/llm_generation/natal/interpretation_service.py`: orchestration natale et persistence audit.

## Conclusions source-alignees

- Prompt-visible natal moderne: `facts`, `signals`, `limits`, `shaping`.
- Validation-only: `evidence`, `grounding_status`, `validation_owner`.
- Audit-only: `provenance`, `projection_hash`, `llm_input_hash`, `provider_response`, `persisted_answer`, observability.
- Runtime-only / non moderne: `chart_json`, `natal_data`, metadata provider, seeds, bootstrap, tests, admin samples.
- Unknown runtime prompt text: `a extraire depuis la configuration runtime`.
- Provider calls: no real LLM provider call was performed for CS-356.
