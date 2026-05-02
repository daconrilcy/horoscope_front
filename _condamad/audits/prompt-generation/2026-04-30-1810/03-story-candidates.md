# Story Candidates - prompt-generation - 2026-04-30-1810

## SC-001 - Retirer le narrateur LLM legacy direct OpenAI

- Candidate ID: SC-001
- Source finding: F-001
- Suggested story title: Supprimer le chemin `LLMNarrator` hors gateway pour `horoscope_daily`
- Suggested archetype: legacy-facade-removal
- Primary domain: `backend/app/prediction`, `backend/app/services/llm_generation/horoscope_daily`
- Required contracts: No Legacy / DRY, service-boundary-audit, regression guardrail `RG-016`
- Draft objective: rendre impossible l'execution directe du narrateur legacy et garantir que la narration quotidienne passe uniquement par `AIEngineAdapter.generate_horoscope_narration`.
- BMAD 70 alignment: traiter ce sujet comme une dette residuelle post-70.15 et post-70.20. Ne pas recréer de shim `app.services.ai_engine_adapter`, ne pas replacer la narration dans l'adapter, et aligner le service quotidien avec le sous-namespace attendu par 70.21.
- Must include: scan zero-hit des instanciations nominales `LLMNarrator(`; verification absence de `chat.completions.create` hors provider canonique; tests de migration narrator conserves sur le chemin canonique; garde-fou empechant toute nouvelle classe direct-provider hors `infrastructure/providers/llm`.
- Validation hints: `rg -n "LLMNarrator\\(|chat\\.completions\\.create|openai\\.AsyncOpenAI" backend/app backend/tests`; tests `backend/tests/unit/prediction/test_llm_narrator*.py` et `backend/tests/llm_orchestration/test_narrator_migration.py`.
- Blockers: Conserver ou non les dataclasses `NarratorResult`/`NarratorAdvice` dans un module de contrat non legacy.

## SC-002 - Eteindre les prompts fallback des familles supportees

- Candidate ID: SC-002
- Source finding: F-002
- Suggested story title: Bloquer les `PROMPT_FALLBACK_CONFIGS` pour `chat`, `guidance`, `natal`, `horoscope_daily`
- Suggested archetype: architecture-guard-hardening
- Primary domain: `backend/app/domain/llm/prompting`, `backend/app/domain/llm/runtime`
- Required contracts: No Legacy / DRY, service-boundary-audit, legacy residual registry
- Draft objective: supprimer le second proprietaire de prompts pour les familles supportees et forcer assemblies/profils comme source unique.
- BMAD 70 alignment: respecter le compromis de 70.16 uniquement s'il reste necessaire: bootstrap non-prod borne, flagge et observable pour base vide, sans devenir un second runtime. L'admin 70.9-70.12 doit continuer a lire les assemblies/versioning reels.
- Must include: guard qui echoue si `PROMPT_FALLBACK_CONFIGS` contient une cle de famille supportee hors fixtures tests ou bootstrap allowliste; test `missing_assembly` sur chaque feature nominale; preuve que la prod ne bascule jamais sur ce fallback; documentation du cas bootstrap explicitement autorise si conserve.
- Validation hints: tests `test_llm_legacy_extinction.py`, `test_prompt_governance_registry.py`, `test_assembly_resolution.py`, routes/tests QA 70.16; scan `PROMPT_FALLBACK_CONFIGS`.
- Blockers: Definir si le bootstrap dev sans assembly doit rester autorise et, si oui, avec quelle allowlist stricte.

## SC-003 - Converger le prompt `horoscope_daily/narration` dans l'assembly

- Candidate ID: SC-003
- Source finding: F-003
- Suggested story title: Deplacer les consignes narratives quotidiennes hors `AstrologerPromptBuilder`
- Suggested archetype: ownership-routing-refactor
- Primary domain: `backend/app/services/llm_generation/horoscope_daily`, `backend/app/prediction`, `backend/app/domain/llm/configuration`
- Required contracts: No Legacy / DRY, service-boundary-audit, prompt governance
- Draft objective: separer payload contextuel quotidien et instructions durables; l'assembly gouvernee devient la source des consignes de format, de longueur, de style et d'interdiction.
- BMAD 70 alignment: garder l'admin 70.12 honnete: les couches `selected_components` et `runtime_artifacts` doivent montrer les vraies consignes envoyees. Respecter 70.20: ne pas compenser via `AIEngineAdapter`. Respecter 70.21: placer le code feature-specific sous `services/llm_generation/horoscope_daily` ou destination equivalente justifiee.
- Must include: `AstrologerPromptBuilder` ne doit plus contenir `Format attendu`, contraintes `daily_synthesis`, ni `Interdiction`; l'assembly `horoscope_daily/narration` porte ces regles; tests du builder verifies sur payload seulement; tests admin detail verifiant que les consignes migrées apparaissent dans les couches observables.
- Validation hints: scans cibles dans `backend/app/prediction/astrologer_prompt_builder.py`; tests `test_astrologer_prompt_builder.py`, `test_seed_horoscope_narrator_assembly.py`, `test_llm_narrator.py`, tests admin catalog/detail de 70.12, tests QA horoscope daily de 70.16.
- Blockers: Definir le niveau exact de migration des textes existants dans la seed/assembly admin.

## SC-004 - Clarifier la taxonomie LLM de la consultation specifique

- Candidate ID: SC-004
- Source finding: F-004
- Suggested story title: Decider et formaliser l'ownership prompt des consultations specifiques
- Suggested archetype: ownership-routing-refactor
- Primary domain: `backend/app/services/llm_generation/consultation_generation_service.py`, `backend/app/services/llm_generation/guidance/guidance_service.py`, `backend/app/domain/llm/governance`
- Required contracts: No Legacy / DRY, service-boundary-audit, prompt governance
- Draft objective: documenter et implementer la decision: consultations comme sous-feature de `guidance`, ou nouvelle famille/sous-feature canonique.
- BMAD 70 alignment: tenir compte de 70.16, qui a deja remis `guidance_contextual` dans le bootstrap canonique et l'admin comme famille `guidance` / consultations thematiques. Si la decision est "sous-cas guidance", la story peut etre majoritairement documentation + guard de non-divergence.
- Must include: contrat de placeholders pour `situation`, `objective`, `natal_chart_summary` et contexte tiers; tests de precheck/refusal qui prouvent qu'aucun prompt LLM n'est genere en cas de refus; guard sur templates `prompt_content`; doc explicite dans `docs/llm-prompt-generation-by-feature.md`.
- Validation hints: tests `test_consultation_*`, `test_guidance_service.py`, registry `prompt_governance_registry.json`.
- Blockers: Decision produit/architecture obligatoire avant story dev.

## BMAD 70 traceability constraints for all candidates

- Ne pas rouvrir les namespaces supprimes par 70.15: aucun import nominal `app.llm_orchestration.*`, `app.prompts.*` ou `app.domain.llm.legacy.*`.
- Reutiliser les surfaces admin existantes de 70.1-70.12: catalogue, legacy, release, consumption, editor, audit et couches observables.
- Conserver la compatibilite avec 70.10: chaque changement de prompt versionne doit rester historisable, comparable, rollbackable et auditable.
- Reutiliser les routes/tests QA de 70.16 pour prouver le pipeline execute au lieu de creer un mini-pipeline de test.
- Respecter 70.20: `AIEngineAdapter` reste une facade minimale, sans logique narrative, prompting durable ou fallback de test.
- Respecter 70.21/70.23: pas de fichier LLM residuel a plat ni de shim/alias de confort; les services feature-specifics vont dans un sous-namespace explicite.
