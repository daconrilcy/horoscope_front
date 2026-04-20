# Audit backend generation de prompts LLM

Date: 2026-04-20
Perimetre: `backend/`
Auteur: Agent Codex

## Objectif

Identifier les fichiers backend impliques dans le process de generation de prompt LLM, verifier leur statut d'usage (actif, legacy, incertain, obsolete), et preciser la fonction de chacun pour preparer une restructuration propre.

## Methode de verification

- Recherche des fichiers candidats par mots-cles (`prompt`, `llm`, `assembly`, `persona`, `fallback`, `release`, `seed`).
- Verification des references entrantes/sortantes (imports, appels de fonctions, `include_router`, scripts seed/build).
- Lecture ciblee des fichiers coeur pour qualifier la responsabilite reelle.
- Classement par statut:
  - `actif`: utilise dans le runtime/API principale.
  - `actif-legacy`: toujours appele pour compatibilite/fallback, mais non voie cible.
  - `incertain`: usage ponctuel/outillage, pas de preuve forte en runtime nominal.
  - `obsolete-probable`: deprecie, backup, ou non relie au flux principal.

## Flux actuel (vision synthese)

1. Les routes API (`guidance`, `chat`, `natal`, `predictions`) deleguent aux services metier.
2. Les services metier passent par `AIEngineAdapter`.
3. `AIEngineAdapter` construit une `LLMExecutionRequest` et appelle `LLMGateway`.
4. `LLMGateway` resout prompt/version/assembly/persona/contexte, puis execute via provider runtime.
5. Les surfaces admin (`admin_llm*`) pilotent prompt versions, assemblies, payloads et releases.
6. Les scripts `seed_*` et `build_llm_*` alimentent/migrent/qualifient la couche prompt en dehors du runtime request.

## Inventaire detaille: fichiers pertinents, statut et fonction

### A) Orchestration coeur (`backend/app/llm_orchestration`)

- `backend/app/llm_orchestration/gateway.py`  
  Statut: `actif`  
  Fonction: point d'entree principal de l'orchestration LLM (composition messages, resolution config/prompt, execution provider, fallback, validation sortie).  
  Preuves: instancie via `AIEngineAdapter`, utilise en admin replay/eval.

- `backend/app/llm_orchestration/prompt_version_lookup.py`  
  Statut: `actif`  
  Fonction: lookup runtime read-only de la version `published` d'un prompt (evite le registre admin).  
  Preuves: importe par `gateway.py` et utilise dans chemins runtime.

- `backend/app/llm_orchestration/services/prompt_renderer.py`  
  Statut: `actif`  
  Fonction: rendu des templates `{{placeholder}}` avec gouvernance/allowlist, gestion required/optional/fallback.  
  Preuves: importe dans `gateway.py`, `assembly_resolver.py`, `admin_llm.py`.

- `backend/app/llm_orchestration/services/prompt_registry_v2.py`  
  Statut: `actif` (surface admin)  
  Fonction: publication, rollback, historique, cache TTL de prompt versions.  
  Preuves: utilise par `admin_llm.py`; documentation interne indique scope admin/history.

- `backend/app/llm_orchestration/services/assembly_resolver.py`  
  Statut: `actif`  
  Fonction: resolution d'une assembly (feature/subfeature/plan/locale), composition persona/plan-rules et preview.  
  Preuves: appels depuis `gateway.py` et `admin_llm.py`.

- `backend/app/llm_orchestration/services/assembly_registry.py`  
  Statut: `actif`  
  Fonction: acces/selection d'assembly config publiees pour le runtime.  
  Preuves: consomme par `gateway.py` et routes admin assembly.

- `backend/app/llm_orchestration/services/assembly_admin_service.py`  
  Statut: `actif`  
  Fonction: logique metier admin pour CRUD/validation des assemblies.  
  Preuves: utilise par les surfaces admin assembly.

- `backend/app/llm_orchestration/services/persona_composer.py`  
  Statut: `actif`  
  Fonction: transformation d'une persona DB en bloc prompt injecte.  
  Preuves: utilise dans `gateway.py`, `assembly_resolver.py`, `admin_llm.py`.

- `backend/app/llm_orchestration/services/context_quality_injector.py`  
  Statut: `actif`  
  Fonction: injection des contraintes/ajustements selon qualite du contexte (`full/partial/minimal`).  
  Preuves: references runtime + tests story 66.x.

- `backend/app/llm_orchestration/services/length_budget_injector.py`  
  Statut: `actif`  
  Fonction: applique des contraintes de longueur selon plan/profil.  
  Preuves: references dans pipeline et tests story.

- `backend/app/llm_orchestration/services/output_validator.py`  
  Statut: `actif`  
  Fonction: validation contractuelle de sortie LLM (schema, erreurs, resultats).  
  Preuves: importe par `gateway.py`, tests unitaires/integration dedies.

- `backend/app/llm_orchestration/services/fallback_governance.py`  
  Statut: `actif`  
  Fonction: gouvernance/trace des fallback types (nominal/non nominal).  
  Preuves: appele par `gateway.py`, `common_context.py`, `llm_narrator.py`.

- `backend/app/llm_orchestration/services/execution_profile_registry.py`  
  Statut: `actif`  
  Fonction: resolution des profils d'execution (mode, parametres, contraintes).  
  Preuves: branche dans pipeline assembly/gateway.

- `backend/app/llm_orchestration/services/provider_parameter_mapper.py`  
  Statut: `actif`  
  Fonction: mapping des parametres d'execution vers le format provider.  
  Preuves: utilise en admin execute sample + pipeline provider.

- `backend/app/llm_orchestration/providers/responses_client.py`  
  Statut: `actif`  
  Fonction: client provider (Responses API), appel effectif au modele.  
  Preuves: instancie par `LLMGateway`.

- `backend/app/llm_orchestration/providers/provider_runtime_manager.py`  
  Statut: `actif`  
  Fonction: orchestration runtime provider (routing, mode nominal/fallback).  
  Preuves: utilise par `gateway.py`.

- `backend/app/llm_orchestration/prompt_governance_registry.py`  
  Statut: `actif`  
  Fonction: registre de gouvernance placeholders/regles de prompt.  
  Preuves: importe dans `prompt_renderer.py` et tests story.

- `backend/app/llm_orchestration/data/prompt_governance_registry.json`  
  Statut: `actif`  
  Fonction: donnees de gouvernance versionnees consommees par le registre.

- `backend/app/llm_orchestration/legacy_prompt_runtime.py`  
  Statut: `actif-legacy`  
  Fonction: mapping legacy use-cases/model/schema/max_tokens et wrappers de compatibilite.  
  Preuves: importe par `gateway.py`, `prompts/catalog.py`, `prompts/common_context.py`.

- `backend/app/llm_orchestration/legacy_residual_registry.py`  
  Statut: `actif-legacy`  
  Fonction: suivi des residus legacy et exceptions de convergence.  
  Preuves: branche au flux de gouvernance fallback.

- `backend/app/llm_orchestration/data/legacy_residual_registry.json`  
  Statut: `actif-legacy`  
  Fonction: configuration des residus legacy.

- `backend/app/llm_orchestration/models.py`  
  Statut: `actif`  
  Fonction: modeles contractuels de l'orchestration (`LLMExecutionRequest`, `GatewayResult`, erreurs, flags).

- `backend/app/llm_orchestration/schemas.py`  
  Statut: `actif`  
  Fonction: schemas associes aux objets d'orchestration/admin.

- `backend/app/llm_orchestration/services/observability_service.py`  
  Statut: `actif`  
  Fonction: logs/telemetrie LLM (log_call, governance events, purge).

- `backend/app/llm_orchestration/services/release_service.py`  
  Statut: `actif`  
  Fonction: construction/validation/activation des snapshots de release LLM.

- `backend/app/llm_orchestration/services/golden_regression_service.py`  
  Statut: `actif`  
  Fonction: verification golden regression dans la boucle de release.

- `backend/app/llm_orchestration/services/replay_service.py`  
  Statut: `actif`  
  Fonction: replay d'appels LLM depuis logs/admin pour diagnostic.

### B) Prompts et contexte (`backend/app/prompts`, `backend/app/prediction`)

- `backend/app/prompts/catalog.py`  
  Statut: `actif-legacy`  
  Fonction: catalogue central derive de `legacy_prompt_runtime`, principalement wrapper de compatibilite/tests/admin.

- `backend/app/prompts/common_context.py`  
  Statut: `actif`  
  Fonction: construction du contexte commun qualifie (`PromptCommonContext`, `QualifiedContext`) pour prompts.

- `backend/app/prompts/validators.py`  
  Statut: `actif`  
  Fonction: validation du contenu des prompts et regles d'architecture.

- `backend/app/prediction/astrologer_prompt_builder.py`  
  Statut: `actif`  
  Fonction: generation de base prompt narratif horoscope/journalier.

- `backend/app/prediction/llm_narrator.py`  
  Statut: `obsolete-probable` (encore present pour compat/tests)  
  Fonction: ancien narrateur direct provider, marque explicitement deprecie au profit de `AIEngineAdapter.generate_horoscope_narration()`.  
  Preuves: docstring deprecation + usages observes surtout en tests.

- `backend/app/prediction/public_projection.py`  
  Statut: `actif`  
  Fonction: flux daily qui appelle la narration via `AIEngineAdapter.generate_horoscope_narration`.

### C) Services metier qui declenchent la generation

- `backend/app/services/ai_engine_adapter.py`  
  Statut: `actif`  
  Fonction: adaptateur principal des use-cases metier vers `LLMGateway`; expose `generate_chat_reply`, `generate_guidance`, `generate_natal_interpretation`, `generate_horoscope_narration`.

- `backend/app/services/natal_interpretation_service_v2.py`  
  Statut: `actif`  
  Fonction: service natal v2; orchestre demande et persistance autour du resultat gateway.

- `backend/app/services/guidance_service.py`  
  Statut: `actif`  
  Fonction: logique guidance; appelle `AIEngineAdapter.generate_guidance`.

- `backend/app/services/chat_guidance_service.py`  
  Statut: `actif`  
  Fonction: logique conversationnelle chat; appelle `AIEngineAdapter.generate_chat_reply`.

- `backend/app/services/llm_ops_monitoring_service.py`  
  Statut: `actif`  
  Fonction: agrats/monitoring LLM pour surfaces ops/admin.

- `backend/app/services/natal_interpretation_service.py`  
  Statut: `actif-legacy`  
  Fonction: ancienne couche natal encore utilisee sur certains endpoints (coexistence avec v2).

- `backend/app/services/chat_guidance_service.py.orig`  
  Statut: `obsolete-probable`  
  Fonction: fichier backup non nominal, non destine au runtime.

### D) Routes API connectees au process prompt

- `backend/app/api/v1/routers/admin_llm.py`  
  Statut: `actif`  
  Fonction: surface admin principale (catalog, publish/rollback, execute-sample, personas, contrats, logs).

- `backend/app/api/v1/routers/admin_llm_assembly.py`  
  Statut: `actif`  
  Fonction: gestion admin des assemblies et previews.

- `backend/app/api/v1/routers/admin_llm_sample_payloads.py`  
  Statut: `actif`  
  Fonction: gestion des payloads d'echantillon pour tests manuels/admin.

- `backend/app/api/v1/routers/admin_llm_release.py`  
  Statut: `actif`  
  Fonction: pilotage release snapshots LLM.

- `backend/app/api/v1/routers/admin_llm_consumption.py`  
  Statut: `actif`  
  Fonction: exposition consommation canonique LLM.

- `backend/app/api/v1/routers/admin_ai.py`  
  Statut: `actif`  
  Fonction: surfaces admin AI connexes (pilotage/observabilite).

- `backend/app/api/v1/routers/predictions.py`  
  Statut: `actif`  
  Fonction: endpoint predictions/daily, injecte contexte et declenche generation narrative.

- `backend/app/api/v1/routers/natal_interpretation.py`  
  Statut: `actif`  
  Fonction: endpoints natal relies aux services d'interpretation LLM.

- `backend/app/api/v1/routers/guidance.py`  
  Statut: `actif`  
  Fonction: endpoint guidance -> service guidance -> adapter -> gateway.

- `backend/app/api/v1/routers/chat.py`  
  Statut: `actif`  
  Fonction: endpoint chat astrologique -> chat guidance service.

- `backend/app/api/v1/routers/ops_monitoring_llm.py`  
  Statut: `actif`  
  Fonction: endpoints ops de monitoring LLM.

- `backend/app/main.py`  
  Statut: `actif`  
  Fonction: montage des routers LLM/admin et bootstrap seed prompts en conditions ciblees.

### E) Modeles DB support du process prompt

- `backend/app/infra/db/models/llm_prompt.py`  
  Statut: `actif`  
  Fonction: tables `llm_use_case_configs` et `llm_prompt_versions` (coeur des prompts versionnes).

- `backend/app/infra/db/models/llm_assembly.py`  
  Statut: `actif`  
  Fonction: table `llm_assembly_configs` pour les combinaisons feature/subfeature/plan/locale.

- `backend/app/infra/db/models/llm_persona.py`  
  Statut: `actif`  
  Fonction: stockage des personas injectables.

- `backend/app/infra/db/models/llm_output_schema.py`  
  Statut: `actif`  
  Fonction: schemas de sortie contractuels par use-case/release.

- `backend/app/infra/db/models/llm_execution_profile.py`  
  Statut: `actif`  
  Fonction: profils d'execution LLM (parametres runtime).

- `backend/app/infra/db/models/llm_observability.py`  
  Statut: `actif`  
  Fonction: logs/appels LLM et traces d'observabilite.

- `backend/app/infra/db/models/llm_release.py`  
  Statut: `actif`  
  Fonction: snapshots de release LLM + pointeur release active.

- `backend/app/infra/db/models/llm_sample_payload.py`  
  Statut: `actif`  
  Fonction: payloads sample pour admin execute/replay.

- `backend/app/infra/db/models/llm_canonical_consumption.py`  
  Statut: `actif`  
  Fonction: stockage des metriques de consommation canonique.

- `backend/app/infra/db/models/token_usage_log.py`  
  Statut: `actif`  
  Fonction: journalisation usage tokens reliee aux appels LLM.

### F) Scripts backend lies au cycle prompt

- `backend/scripts/seed_29_prompts.py`  
  Statut: `actif` (bootstrap conditionnel)  
  Fonction: seed historique prompts; appele dans `main.py` en mode conditionnel.

- `backend/scripts/seed_30_8_v3_prompts.py`  
  Statut: `actif` (bootstrap/migration)  
  Fonction: seed prompts v3 natal + lint + publication.

- `backend/scripts/seed_30_14_chat_prompt.py`  
  Statut: `actif` (bootstrap/migration)  
  Fonction: seed prompt chat astrologer.

- `backend/scripts/seed_30_3_gpt5_prompts.py`  
  Statut: `incertain`  
  Fonction: seed/migration GPT-5; pas de preuve forte d'appel runtime direct.

- `backend/scripts/seed_30_15_chat_naturalite.py`  
  Statut: `incertain`  
  Fonction: ajustements qualitatifs chat prompt; plutot outillage ponctuel.

- `backend/scripts/seed_66_15_assembly_convergence.py`  
  Statut: `incertain`  
  Fonction: convergence assemblies story 66.15; typiquement migration.

- `backend/scripts/seed_66_20_convergence.py`  
  Statut: `incertain`  
  Fonction: convergence taxonomie/story 66.20; typiquement migration.

- `backend/scripts/build_llm_release_candidate.py`  
  Statut: `actif` (ops/release)  
  Fonction: construit + valide un snapshot release candidate.

- `backend/scripts/build_llm_release_readiness_report.py`  
  Statut: `actif` (ops/release)  
  Fonction: rapport readiness go/no-go pour release LLM.

- `backend/scripts/build_llm_qualification_evidence.py`  
  Statut: `actif` (ops/release)  
  Fonction: genere artefacts de qualification.

- `backend/scripts/build_llm_golden_evidence.py`  
  Statut: `actif` (ops/release)  
  Fonction: genere evidences golden regression.

- `backend/scripts/build_llm_smoke_evidence.py`  
  Statut: `actif` (ops/release)  
  Fonction: genere evidences smoke test release.

- `backend/scripts/update_all_prompts_59_5.py`  
  Statut: `incertain`  
  Fonction: script one-shot de migration historique (ajout common header).

- `backend/scripts/update_guidance_prompts_59_4.py`  
  Statut: `incertain`  
  Fonction: migration one-shot guidance prompts.

- `backend/scripts/legacy_residual_report.py`  
  Statut: `actif-legacy`  
  Fonction: rapport de suivi des residus legacy.

### G) Tests backend lies au sujet (support de verification, non runtime)

Statut global de ces fichiers: `actif (tests)` sauf mention contraire.

- `backend/app/llm_orchestration/tests/test_prompt_registry_v2.py` - verifie publication/rollback/cache registry.
- `backend/app/llm_orchestration/tests/test_prompt_renderer.py` - verifie resolution placeholders/gouvernance.
- `backend/app/llm_orchestration/tests/test_llm_gateway_compose.py` - verifie composition messages gateway.
- `backend/app/llm_orchestration/tests/test_gateway_pipeline.py` - verifie pipeline complet gateway.
- `backend/app/llm_orchestration/tests/test_llm_gateway_routing.py` - verifie routage use-case feature/subfeature.
- `backend/app/llm_orchestration/tests/test_assembly_resolution.py` - verifie resolution assembly.
- `backend/app/llm_orchestration/tests/test_story_66_42_prompt_governance_registry.py` - verifie regles gouvernance.
- `backend/app/llm_orchestration/tests/test_story_66_19_narrator_migration.py` - verifie migration vers adapter/gateway.
- `backend/app/tests/integration/test_admin_llm_natal_prompts.py` - integration admin prompt lifecycle.
- `backend/tests/integration/test_admin_llm_catalog.py` - integration catalogue admin LLM.
- `backend/tests/evaluation/test_prompt_resolution.py` - evaluation de resolution prompt.
- `backend/tests/unit/prediction/test_astrologer_prompt_builder.py` - verifie builder narratif.
- `backend/tests/unit/prediction/test_llm_narrator.py` - `actif (tests-legacy)` sur composant deprecie.

## Statut global: actifs vs obsolete

### Actif (runtime ou admin principal)

La majorite du process est active et coherent autour du triplet:
- `AIEngineAdapter` -> `LLMGateway` -> services `prompt_renderer` / `assembly_*` / providers.

Les surfaces admin sont bien branchees dans `main.py`:
- `admin_llm`, `admin_llm_sample_payloads`, `admin_llm_consumption`, `admin_llm_assembly`, `admin_llm_release`.

### Actif-legacy (compatibilite preservee)

Composants encore utilises pour transition:
- `legacy_prompt_runtime.py`
- `legacy_residual_registry.py` (+ JSON)
- `prompts/catalog.py`
- une partie de `natal_interpretation_service.py`
- scripts/reporting legacy.

### Obsolete-probable

- `backend/app/prediction/llm_narrator.py` (deprecie explicitement).
- `backend/app/services/chat_guidance_service.py.orig` (backup).

### Incertain (a confirmer selon runbooks CI/ops)

Principalement scripts one-shot de migration:
- `seed_30_3_gpt5_prompts.py`
- `seed_30_15_chat_naturalite.py`
- `seed_66_15_assembly_convergence.py`
- `seed_66_20_convergence.py`
- `update_all_prompts_59_5.py`
- `update_guidance_prompts_59_4.py`

## Recommandations de restructuration (proposees)

### 1) Clarifier par couches dans `backend/app/llm_orchestration`

- Conserver `runtime/` (gateway, providers, validators, injectors).
- Extraire `admin/` (registry v2, assembly admin services, replay/eval admin).
- Isoler `legacy/` (legacy runtime + residual registries).
- Isoler `governance/` (prompt governance registry + policies + conformity validators).

### 2) Separer strictement runtime vs migration scripts

- Creer `backend/scripts/llm/migrations/` pour scripts one-shot.
- Creer `backend/scripts/llm/release/` pour scripts evidence/release candidate.
- Garder seulement un bootstrap minimal clairement documente.

### 3) Plan de decommission progressive

- Etape 1: marquer officiellement `llm_narrator.py` en removal-target avec date.
- Etape 2: verifier qu'aucun endpoint prod n'utilise encore `natal_interpretation_service.py` legacy.
- Etape 3: figer la liste des scripts migration a archiver dans `scripts/legacy/`.

### 4) Gouvernance des statuts de fichiers

- Ajouter un `README` dans `backend/app/llm_orchestration/` definissant:
  - fichiers runtime obligatoires,
  - fichiers legacy temporaires,
  - conventions de suppression.

## Points d'attention / limites de l'audit

- Audit statique (imports/appels) sans execution end-to-end complete.
- Certains scripts "incertains" peuvent etre lances hors code (CI, runbook ops manuel).
- La coexistence `v2` et legacy peut etre volontaire selon phases de migration.

## Conclusion

Le process de generation de prompt LLM backend est globalement actif et structure autour du pipeline canonique `AIEngineAdapter -> LLMGateway`.  
La dette principale n'est pas une rupture fonctionnelle, mais la cohabitation runtime + legacy + scripts one-shot. La restructuration doit prioriser la lisibilite (separation des couches) puis la decommission progressive des composants depreciés.
