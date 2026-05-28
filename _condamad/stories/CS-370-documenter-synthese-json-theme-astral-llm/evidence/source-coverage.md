<!-- Commentaire global: cette preuve liste les sources inspectees pour documenter la structure JSON theme astral LLM. -->

# Source coverage CS-370

## Sources inspectees

- Brief source: `_story_briefs/cs-370-documenter-synthese-nouvelle-structure-json-theme-astral-llm.md`.
- Story cible et tracker: `_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/00-story.md`, `_condamad/stories/story-status.md`.
- Architecture: `_condamad/architecture/theme-astral-prompt-contract/2026-05-28-1217/archi-theme-astral-prompt-contract-v1.md`.
- Audits: `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1152/`, `2026-05-28-1203/`, `2026-05-28-1409/`, `2026-05-28-1418/`.
- Stories amont: CS-363, CS-364, CS-365, CS-366, CS-367, CS-368, CS-369.
- Documentation existante: `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`, `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md`.
- Backend owners: `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`, `backend/app/domain/llm/configuration/theme_astral_contracts.py`, `backend/app/domain/astrology/interpretation/interpretation_material_builder.py`, `backend/app/domain/astrology/interpretation/interpretation_material_contracts.py`.
- Tests evidence: `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`, `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`, `backend/tests/integration/astrology/test_theme_astral_interpretation_material_input.py`.

## Statuts amont observes

- CS-364: `done`; persistence et contrats versionnes documentes dans le tracker canonique.
- CS-365: `done`; builder `interpretation_material` present.
- CS-366: `done` dans `_condamad/stories/story-status.md`; le code et les tests du builder provider existent dans le workspace.
- CS-367: `done`; bigbang et tests de handoff existent.
- CS-368 et CS-369: `done`; les audits correspondants existent et restent sources de verification, pas owners runtime.

## Gaps et decisions de redaction

- Les sources d'audit et d'architecture existent; aucun blocker de chemin absent.
- CS-371 n'est referencee que comme owner des exemples complets; aucun payload complet n'a ete genere dans CS-370.
- Les etiquettes commerciales sont traitees comme entrees backend uniquement; le document de synthese evite de les presenter comme donnees LLM-visibles.
- Aucun code applicatif, test backend, migration ou frontend n'a ete modifie.
