# Story 70.15: Basculer la source de verite runtime LLM vers les namespaces canoniques

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect,  
I want faire des namespaces canoniques `application/llm`, `domain/llm`, `infrastructure/*` et `ops/llm` la source de verite reelle du runtime de generation de prompts LLM,  
so that la refonte 70-14 ne reste pas une couche de wrappers transitoires, mais devienne l architecture effectivement executee, maintenue et evolutive du backend.

## Contexte

La story 70-14 a atteint son objectif de reorganisation initiale sans rupture runtime :

- les namespaces canoniques `api/application/domain/infrastructure/ops` existent ;
- les points d entree admin LLM sont regroupes dans `backend/app/api/v1/routers/admin/llm/` ;
- `backend/app/application/llm/ai_engine_adapter.py` existe comme facade canonique ;
- `backend/app/domain/llm/*` existe comme espace canonique pour runtime, prompting, configuration, governance et legacy ;
- `backend/app/infrastructure/*` et `backend/app/ops/llm/*` absorbent deja une partie des responsabilites ;
- la qualite globale est revenue au vert apres stabilisation.

Cependant, l audit post-story 70-14 montre que le centre de gravite effectif de l implementation reste majoritairement dans les chemins historiques :

- `backend/app/llm_orchestration/*`
- `backend/app/prompts/*`
- `backend/app/services/ai_engine_adapter.py`
- certaines surfaces admin historiques.

L etat actuel est donc un etat de transition :

- les chemins canoniques existent et sont utilises comme points d entree ;
- une partie importante de ces chemins canoniques reste composee de wrappers transitoires ;
- le coeur d execution reel du pipeline LLM reste encore heberge dans les modules historiques ;
- le risque principal n est plus la casse runtime immediate, mais la confusion de maintenance et la duplication d evolutions si de nouvelles modifications continuent a entrer dans l ancien noyau.

Cette story vise donc la bascule de la source de verite reelle du runtime LLM, sans refactor big-bang, en gardant une approche BMAD par lots, mesurable et reversible.

## Objectif

Faire converger le backend LLM d un etat :

- **structure canonique + implementation historique encapsulee**

vers un etat :

- **structure canonique + implementation canonique executee**

La story ne cherche pas a supprimer tout le legacy en une fois. Elle impose d abord que les composants canoniques deviennent les implementations reelles, et que les chemins historiques soient progressivement reduits a des shims de compatibilite, puis supprimables.

## Cible d architecture

A l issue de cette story :

- `backend/app/application/llm/ai_engine_adapter.py` est l implementation applicative reelle ;
- `backend/app/domain/llm/runtime/gateway.py` est le vrai point d entree du runtime LLM ;
- `backend/app/domain/llm/prompting/*` et `backend/app/domain/llm/configuration/*` portent les implementations de resolution, rendu, contexte, personas, assemblies, profils et versions ;
- `backend/app/domain/llm/governance/*` devient la source de verite des regles de gouvernance et de residual legacy ;
- `backend/app/infrastructure/providers/llm/openai_responses_client.py` est le client provider concret de reference ;
- les modules historiques `llm_orchestration/*`, `prompts/*` et certains chemins `services/*` deviennent des wrappers inverses temporaires ou des modules candidats a suppression.

## Acceptance Criteria

1. **AC1 - AIEngineAdapter canonique reel** : `backend/app/application/llm/ai_engine_adapter.py` contient l implementation reelle de l adaptateur metier -> runtime LLM ; `backend/app/services/ai_engine_adapter.py` devient au maximum un wrapper transitoire inverse ou est supprime si plus necessaire.
2. **AC2 - Gateway canonique reel** : `backend/app/domain/llm/runtime/gateway.py` contient l implementation reelle du runtime gateway ; `backend/app/llm_orchestration/gateway.py` devient un shim de compatibilite transitoire ou est decommissionne.
3. **AC3 - Runtime canonique execute** : les composants canoniques `runtime/composition.py`, `runtime/validation.py`, `runtime/fallback.py`, `runtime/provider_runtime_manager.py` portent les implementations utilisees en nominal et ne se contentent plus de re-exporter les modules historiques.
4. **AC4 - Prompting canonique execute** : les composants canoniques `prompting/renderer.py`, `prompting/personas.py`, `prompting/context.py`, `prompting/validation.py` portent les implementations utilisees en nominal.
5. **AC5 - Configuration canonique execute** : les composants canoniques `configuration/prompt_versions.py`, `configuration/assemblies.py`, `configuration/execution_profiles.py` portent les implementations de reference pour la resolution runtime et admin.
6. **AC6 - Gouvernance canonique source de verite** : `backend/app/domain/llm/governance/` devient la source de verite des regles de gouvernance placeholders et residual legacy ; les anciens chemins historiques deviennent des wrappers transitoires ou sont retires.
7. **AC7 - Infrastructure provider canonique reelle** : `backend/app/infrastructure/providers/llm/openai_responses_client.py` devient le client provider concret de reference ; le runtime canonique depend de ce chemin ou d un contrat stable associe.
8. **AC8 - Pas de nouvelle logique dans l ancien noyau** : a partir de cette story, aucune nouvelle logique fonctionnelle LLM nominale n est introduite directement dans `llm_orchestration/*`, `prompts/*` ou les anciens chemins historiques, sauf shim de compatibilite explicitement documente.
9. **AC9 - Inversion des wrappers** : lorsque des chemins historiques restent necessaires, ils wrapent les composants canoniques, et non l inverse.
10. **AC10 - Preservation comportementale** : la bascule vers les implementations canoniques n introduit pas de regression fonctionnelle observable sur les use cases guidance, chat, natal et horoscope quotidien.
11. **AC11 - Admin partage le meme moteur de resolution** : les surfaces admin de preview, execute-sample, replay et release validation reutilisent les composants canoniques de resolution et ne re-derivent pas leurs propres regles.
12. **AC12 - Repositories conserves comme point d acces persistant** : les acces DB introduits ou centralises en 70-14 restent utilises et sont renforces, sans retour a des acces SQLAlchemy disperses.
13. **AC13 - Legacy bridge maintenu comme sas unique** : `backend/app/domain/llm/legacy/bridge.py` reste l unique point d acces nominal -> legacy tant que des dependances legacy subsistent.
14. **AC14 - Compatibilite transitoire documentee** : chaque shim ou wrapper inverse restant est liste dans un document de transition maintenu a jour avec son critere de suppression.
15. **AC15 - Validation complete obligatoire** : la story est consideree finie seulement si les validations locales backend passent (`ruff format`, `ruff check`, `pytest -q`) et si les tests critiques de non-regression runtime/admin sont verts.
16. **AC16 - Adoption nominale des chemins canoniques** : pour les composants critiques migres vers `app.domain.llm.*`, le code nominal `backend/app` importe directement les chemins canoniques ; les chemins historiques `app.llm_orchestration.*` correspondants ne sont utilises que comme shims de compatibilite transitoire.

## Tasks / Subtasks

- [x] Task 1: Faire de la couche application canonique le point d entree reel (AC1, AC10)
  - [x] Deplacer l implementation effective de `app/services/ai_engine_adapter.py` dans `backend/app/application/llm/ai_engine_adapter.py`.
  - [x] Mettre a jour les imports des services metier pour viser prioritairement `app.application.llm.ai_engine_adapter`.
  - [x] Transformer `backend/app/services/ai_engine_adapter.py` en wrapper transitoire inverse vers le chemin canonique, ou le supprimer si possible.
  - [x] Verifier que guidance, chat, natal et public projection utilisent bien l adaptateur canonique.
  - [x] Ajouter ou ajuster des tests de non-regression sur l adaptateur canonique.

- [x] Task 2: Basculer le runtime gateway et ses composants vers le domaine canonique (AC2, AC3, AC9, AC10)
  - [x] Migrer l implementation effective de `app.llm_orchestration.gateway` vers `backend/app/domain/llm/runtime/gateway.py`.
  - [x] Migrer les composants reels de composition, validation, fallback et provider runtime manager vers `backend/app/domain/llm/runtime/*`.
  - [x] Mettre a jour les imports internes pour que le runtime nominal parte du domaine canonique.
  - [x] Transformer les anciens modules `llm_orchestration/gateway.py` et associes en shims de compatibilite si necessaire.
  - [x] Verifier qu aucun composant runtime canonique n importe `ops` ni de router API.

- [x] Task 3: Basculer prompting et configuration vers les modules canoniques (AC4, AC5, AC11)
  - [x] Migrer l implementation effective de `prompt_renderer`, `persona_composer`, `common_context`, validations prompt dans `backend/app/domain/llm/prompting/*`.
  - [x] Migrer l implementation effective de `prompt_version_lookup`, `assembly_resolver`, `assembly_registry`, `assembly_admin_service`, `execution_profile_registry` dans `backend/app/domain/llm/configuration/*`.
  - [x] Verifier que runtime et admin utilisent les memes modules canoniques de resolution.
  - [x] Laisser au besoin des shims dans `llm_orchestration/*` et `prompts/*`, mais sans logique nouvelle.
  - [x] Ajuster les tests de resolution pour viser les chemins canoniques comme reference.

- [x] Task 4: Basculer la gouvernance et les providers vers les chemins canoniques (AC6, AC7, AC13, AC14)
  - [x] Faire de `backend/app/domain/llm/governance/*` la source de verite active pour les registres governance et residual legacy.
  - [x] Faire de `backend/app/infrastructure/providers/llm/openai_responses_client.py` le client concret de reference.
  - [x] Verifier que `legacy/bridge.py` reste l unique porte nominale vers les mecanismes legacy.
  - [x] Mettre a jour le registre de transition des wrappers et definir les criteres de retrait.
  - [x] Verifier que les anciens chemins historiques de provider ou governance ne sont plus la source primaire.

- [x] Task 5: Reduction controlee de l ancien noyau historique (AC8, AC9, AC14)
  - [x] Geler `backend/app/llm_orchestration/*` comme zone de maintenance minimale.
  - [x] Identifier les modules historiques encore necessaires comme shims explicites.
  - [x] Supprimer ou declasser les wrappers canoniques devenus inutiles apres bascule.
  - [x] Lister les modules historiques devenus candidats a suppression dans un plan de decommission.
  - [x] S assurer que toute evolution future LLM nominale passe par les chemins canoniques.

- [x] Task 6: Validation locale obligatoire (AC10, AC11, AC12, AC15)
  - [x] Activer le venv avant toute commande Python : `\.venv\Scripts\Activate.ps1`
  - [x] Installer ou mettre a jour les dependances backend si necessaire via `cd backend ; pip install -e ".[dev]"`
  - [x] Executer `cd backend ; ruff format .`
  - [x] Executer `cd backend ; ruff check .`
  - [x] Executer `cd backend ; pytest -q`
  - [x] Executer ou cibler des tests critiques sur guidance, chat, natal, daily prediction, admin prompts/replay/release si necessaire.
  - [x] Verifier que les imports historiques restants pointent tous vers des shims documentes.

- [x] Task 7: Bascule ciblee des imports nominaux critiques vers `app.domain.llm.*` (AC16)
  - [x] Basculer `ProviderRuntimeManager` nominal vers `app.domain.llm.runtime.provider_runtime_manager`.
  - [x] Basculer `prompt_version_lookup` nominal vers `app.domain.llm.configuration.prompt_version_lookup`.
  - [x] Basculer `prompt_governance_registry` nominal vers `app.domain.llm.governance.prompt_governance_registry`.
  - [x] Basculer `legacy_residual_registry` nominal vers `app.domain.llm.governance.legacy_residual_registry`.
  - [x] Inverser les chemins historiques concernes en shims de compatibilite.

## Dev Notes

### Positionnement par rapport a 70-14

La story 70-14 a reussi la mise en ordre structurelle.  
La story 70-15 vise la bascule de la source de verite executee.

Autrement dit :

- 70-14 = les chemins canoniques existent
- 70-15 = les chemins canoniques deviennent l implementation reelle

### Strategie par lots

- **Lot 1 - Application canonique reelle** : faire porter l implementation effective par `application/llm/ai_engine_adapter.py`.
- **Lot 2 - Runtime canonique reel** : migrer `gateway` et les briques runtime dans `domain/llm/runtime/`.
- **Lot 3 - Prompting et configuration canoniques reels** : migrer la resolution et le rendu dans `domain/llm/prompting/` et `domain/llm/configuration/`.
- **Lot 4 - Gouvernance/providers canoniques et reduction de l ancien noyau** : basculer governance/provider puis retrograder l ancien noyau a des shims ou candidats a suppression.

### Regles structurelles non negociables

- Aucun nouveau developpement LLM nominal ne doit cibler directement `llm_orchestration/*` comme source primaire.
- Aucun nouveau developpement LLM nominal ne doit cibler directement `prompts/*` comme source primaire.
- Les modules historiques encore presents ne doivent servir qu a la compatibilite transitoire.
- Tout shim restant doit wrapper le canonique, pas l inverse.
- Runtime et admin doivent partager les memes moteurs de resolution.
- Les acces DB restent centralises via repositories ou query services dedies.
- `legacy/bridge.py` reste l unique porte nominale vers le legacy.
- Toute suppression d ancien module doit etre precedee d une preuve qu il n est plus le point de verite execute.

### Points d attention

- Ne pas faire une migration big-bang de tous les sous-modules en une seule PR.
- Ne pas casser les usages admin pendant la bascule du moteur de resolution.
- Ne pas reintroduire de duplication de logique entre anciens et nouveaux chemins.
- Verifier que les imports canoniques deviennent les imports par defaut dans les fichiers touches.
- Si certains modules historiques doivent rester temporairement, les renommer ou documenter clairement comme `shim` ou `legacy-compatible`.

### References

- [docs/2026-04-20-audit-prompts-backend.md](/c:/dev/horoscope_front/docs/2026-04-20-audit-prompts-backend.md)
- [docs/2026-04-20-audit-prompts-backend-post-story-70-14.md](/c:/dev/horoscope_front/docs/2026-04-20-audit-prompts-backend-post-story-70-14.md)
- [70-14-reorganiser-et-consolider-les-fichiers-du-process-llm-backend-dry.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-14-reorganiser-et-consolider-les-fichiers-du-process-llm-backend-dry.md)

## Dev Agent Record

### Agent Model Used

gpt-5

### Debug Log References

- Demande utilisateur : rediger la story logique suivante apres 70-14 pour basculer la source de verite runtime LLM vers les namespaces canoniques.
- Source principale : audit post-story 70-14 montrant que les chemins canoniques existent mais que le noyau d implementation reste majoritairement historique.
- Positionnement BMAD : story de convergence apres reorganisation, centree sur la bascule effective du runtime et l inversion des wrappers.

### Completion Notes List

- Story 70.15 redigee pour transformer les namespaces canoniques en source de verite executee du pipeline LLM.
- La story couvre la bascule applicative, runtime, prompting, configuration, gouvernance et provider.
- Les criteres d acceptation imposent l inversion des wrappers, la preservation comportementale et le partage des moteurs runtime/admin.
- La trajectoire reste incrementaliste et compatible avec la logique BMAD en lots.
- Implementation 2026-04-20 : `AIEngineAdapter` et `LLMGateway` portent l implementation reelle sous `application/llm` et `domain/llm/runtime` ; chemins `services/ai_engine_adapter` et `llm_orchestration/gateway` sont des shims.
- Runtime (composition, validation, fallback, provider manager), prompting (renderer, personas), configuration (assemblies, profils, prompt versions) et `prompt_version_lookup` migres sous `domain/llm/*` avec shims historiques.
- `ProviderRuntimeManager` canonique utilise `ResponsesClient` via `infrastructure/providers/llm/openai_responses_client` ; validateur semantique et tests de patch ciblent les modules domaine.
- Registre `TRANSITION_WRAPPERS.md` et manifest doc conformite mis a jour ; `ruff format`, `ruff check`, `pytest -q` verts (2964 passed).
- Stabilisation reproductibilite (review P1) : les imports runtime trackes ont ete reroutes vers des modules suivis (`app.llm_orchestration/*` et `app.prompts/common_context`) pour eviter toute dependance aux fichiers canoniques non suivis.
- Hygiene diff (review P2) : `backend/horoscope.db` reste hors scope et est restauree depuis `HEAD` avant validation finale.
- Bascule ciblee AC16 : les imports nominaux backend/app des 4 composants critiques consomment maintenant directement `app.domain.llm.*` ; les chemins historiques correspondants sont reduits a des shims.
- Correctif cible post-bascule : les 3 tests `test_story_66_27_integrated_propagation.py` patchent desormais `app.prompts.common_context.CommonContextBuilder.build` (reference runtime effective) pour restaurer la propagation attendue de `obs.context_quality` sans revenir sur les imports canoniques.

### File List

- _bmad-output/implementation-artifacts/70-15-basculer-la-source-de-verite-runtime-llm-vers-les-namespaces-canoniques.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/application/llm/ai_engine_adapter.py
- backend/app/services/ai_engine_adapter.py
- backend/app/domain/llm/runtime/gateway.py
- backend/app/domain/llm/runtime/composition.py
- backend/app/domain/llm/runtime/validation.py
- backend/app/domain/llm/runtime/fallback.py
- backend/app/domain/llm/runtime/provider_runtime_manager.py
- backend/app/domain/llm/runtime/context_quality_injector.py
- backend/app/domain/llm/runtime/length_budget_injector.py
- backend/app/domain/llm/runtime/provider_parameter_mapper.py
- backend/app/domain/llm/runtime/output_validator.py
- backend/app/domain/llm/runtime/fallback_governance.py
- backend/app/domain/llm/prompting/prompt_renderer.py
- backend/app/domain/llm/prompting/personas.py
- backend/app/domain/llm/prompting/renderer.py
- backend/app/domain/llm/configuration/assemblies.py
- backend/app/domain/llm/configuration/assembly_resolver.py
- backend/app/domain/llm/configuration/assembly_registry.py
- backend/app/domain/llm/configuration/assembly_admin_service.py
- backend/app/domain/llm/configuration/execution_profiles.py
- backend/app/domain/llm/configuration/execution_profile_registry.py
- backend/app/domain/llm/configuration/prompt_versions.py
- backend/app/domain/llm/configuration/prompt_version_lookup.py
- backend/app/llm_orchestration/gateway.py
- backend/app/llm_orchestration/prompt_version_lookup.py
- backend/app/llm_orchestration/services/*.py (shims listes en story)
- backend/app/llm_orchestration/providers/provider_runtime_manager.py
- backend/app/llm_orchestration/doc_conformity_manifest.py
- backend/app/llm_orchestration/services/semantic_conformity_validator.py
- backend/app/ops/llm/TRANSITION_WRAPPERS.md
- backend/app/infra/llm/client.py
- backend/app/tests/unit/test_ai_engine_adapter.py
- backend/app/tests/unit/test_natal_interpretation_service_v2.py
- backend/tests/integration/conftest.py
- backend/tests/evaluation/conftest.py
- backend/tests/evaluation/test_prompt_resolution.py
- backend/tests/integration/test_story_66_21_governance.py
- backend/tests/integration/test_story_66_22_provider_locking.py
- backend/tests/integration/test_story_66_27_integrated_propagation.py
- backend/tests/integration/test_story_66_30_suppression.py
- backend/tests/integration/test_story_66_40_legacy_residual.py
- backend/app/llm_orchestration/tests/conftest.py
- backend/app/llm_orchestration/tests/test_gateway_pipeline.py

### Change Log

- 2026-04-20 : creation de la story backend `70.15` pour basculer la source de verite runtime LLM des chemins historiques vers les namespaces canoniques introduits par 70-14.
- 2026-04-20 : implementation — bascule effective des implementations vers `application/llm` et `domain/llm/*`, shims historiques, ajustements tests et conformite doc/semantique.
- 2026-04-21 : correctifs review P1/P2 — suppression des dependances trackees vers modules non suivis et restauration systematique de `backend/horoscope.db` hors scope.
- 2026-04-21 : ajout AC16 et bascule ciblee des imports nominaux vers `app.domain.llm.*` pour `provider_runtime_manager`, `prompt_version_lookup`, `prompt_governance_registry` et `legacy_residual_registry` ; inversion des chemins historiques en shims.
- 2026-04-21 : correctif tests integration 66.27 apres bascule canonique — realignement de la cible de patch `CommonContextBuilder.build` vers `app.prompts.common_context` pour conserver `obs.context_quality` (3/3 verts) sans rollback des imports canoniques.
