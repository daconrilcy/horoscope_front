# Couverture source CS-371

- Brief source: `_story_briefs/cs-371-generer-exemples-json-theme-astral-llm-v1-par-plan.md`.
- Synthese: `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`.
- Builder: `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`.
- Tests: `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` et `backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`.
- Source gap: le runtime `ChartInterpretationInputRuntimeData` ne porte pas de champs naissance detailles; l'exemple encode le scenario dans `chart_id` et le documente dans `intermediate-data.json`.
