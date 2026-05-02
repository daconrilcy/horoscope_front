# Story Candidates - prompt-generation - 2026-05-02-1452

## SC-001 - Converger les exceptions fallback prompt restantes

- Candidate ID: SC-001
- Source finding: F-001
- Suggested story title: Classifier et converger les exceptions `PROMPT_FALLBACK_CONFIGS` restantes
- Suggested archetype: architecture-guard-hardening
- Primary domain: `backend/app/domain/llm/prompting`
- Required contracts: No Legacy / DRY, Runtime Source of Truth, Allowlist Exception, Reintroduction Guard, Persistent Evidence
- Draft objective: reduire `PROMPT_FALLBACK_CONFIGS` aux fixtures synthetiques ou a une exception bootstrap strictement non-prod, puis migrer ou supprimer les prompts fallback restants qui correspondent a des use cases canoniques.
- Must include: inventaire cle par cle (`natal_interpretation_short`, `guidance_daily`, `guidance_weekly`, `event_guidance`, `natal_long_free`, `astrologer_selection_help`, `test_natal`, `test_guidance`); decision `fixture`, `bootstrap-non-prod`, `migrate-to-assembly`, `delete`, ou `needs-user-decision`; test qui prouve qu'aucune cle canonique ne peut etre ajoutee sans decision; preuve gateway production `missing_assembly` conservee.
- Validation hints: `pytest -q tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_llm_legacy_extinction.py tests/llm_orchestration/test_assembly_resolution.py`; scan `rg -n "PROMPT_FALLBACK_CONFIGS|build_fallback_use_case_config" app tests`.
- Blockers:
  - definir si `natal_interpretation_short`, `guidance_daily`, `guidance_weekly` et `event_guidance` doivent encore avoir un bootstrap prompt hors assembly.

## SC-002 - Corriger les chemins de validation des stories prompt-generation

- Candidate ID: SC-002
- Source finding: F-002
- Suggested story title: Aligner les validation plans des stories prompt-generation avec les chemins collectes
- Suggested archetype: test-guard-hardening
- Primary domain: `_condamad/stories`
- Required contracts: Persistent Evidence, Reintroduction Guard
- Draft objective: corriger les commandes de validation des stories livrees pour qu'elles pointent vers les fichiers de tests reels et restent executables sans correction manuelle.
- Must include: correction des chemins `tests/llm_orchestration/test_seed_horoscope_narrator_assembly.py` vers `app/tests/unit/test_seed_horoscope_narrator_assembly.py`; correction des chemins `tests/unit/test_guidance_service.py` et `tests/unit/test_consultation_generation_service.py` vers `app/tests/unit/...`; verification que les commandes de chaque story prompt-generation collectent au moins un test.
- Validation hints: relancer les commandes de validation ciblees dans le venv; optionnellement ajouter un script read-only qui parse les blocs `Validation Plan` et verifie l'existence des chemins.
- Blockers:
  - aucun blocker produit; decider si les stories `ready-for-dev` doivent aussi passer `completed` quand l'evidence existe.
