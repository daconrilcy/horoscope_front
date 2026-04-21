# Audit backend generation de prompts LLM (post-story 70-14)

Date: 2026-04-20  
Perimetre: `backend/` (fichiers de production et scripts ops; tests exclus du classement principal)

## Objectif

Etablir un etat post-story 70-14 des fichiers backend lies au process de generation de prompts LLM, avec:
- leur statut d usage (`actif`, `actif-legacy`, `incertain`, `obsolete`),
- leur fonction dans le flux global,
- la distinction entre chemins canoniques et implementations encore transitoires.

## Flux global (etat observe)

1. Les endpoints metier (chat/guidance/natal/predictions) appellent des services metier.
2. Les services metier passent par `app.services.ai_engine_adapter`.
3. L adapter construit une requete `LLMExecutionRequest` et appelle `app.llm_orchestration.gateway.LLMGateway`.
4. Le gateway resout prompt/version/assembly/persona/profil puis execute via provider.
5. Les endpoints admin LLM pilotent catalogue prompts, assemblies, releases, payloads et observabilite.
6. Les scripts `app/ops/llm/*` et wrappers `backend/scripts/*` couvrent bootstrap et evidences release.

## Inventaire des fichiers lies au process prompt LLM

## A. Entree API et bootstrap application

- `backend/app/main.py` - **actif** - Monte les routers admin LLM, declenche le reseed dev conditionnel (`app.ops.llm.bootstrap.*`), et lance la validation de coherence LLM au demarrage.
- `backend/app/startup/llm_coherence_validation.py` - **actif** - Validation de coherence configuration LLM au startup.
- `backend/app/api/v1/routers/ops_monitoring_llm.py` - **actif** - Exposition des endpoints OPS de suivi LLM.

## B. Endpoints admin LLM (namespace canonique 70-14)

- `backend/app/api/v1/routers/admin/llm/prompts.py` - **actif-legacy** - Point d entree canonique, mais wrapper transitoire qui re-exporte `admin_llm`.
- `backend/app/api/v1/routers/admin/llm/assemblies.py` - **actif-legacy** - Wrapper vers le router historique assemblies.
- `backend/app/api/v1/routers/admin/llm/releases.py` - **actif-legacy** - Wrapper vers le router historique releases.
- `backend/app/api/v1/routers/admin/llm/sample_payloads.py` - **actif-legacy** - Wrapper vers le router historique sample payloads.
- `backend/app/api/v1/routers/admin/llm/consumption.py` - **actif-legacy** - Wrapper vers le router historique consumption.
- `backend/app/api/v1/routers/admin/llm/observability.py` - **actif-legacy** - Wrapper vers le router historique observability.
- `backend/app/api/v1/routers/admin/llm/__init__.py` - **actif** - Regroupe les exports du namespace admin LLM.

## C. Endpoints admin LLM historiques (implementation principale actuelle)

- `backend/app/api/v1/routers/admin_llm.py` - **actif** - Implementation principale du catalogue prompt, publish/rollback, execute-sample, replay, governance et audit admin.
- `backend/app/api/v1/routers/admin_llm_assembly.py` - **actif** - Gestion admin des assemblies.
- `backend/app/api/v1/routers/admin_llm_release.py` - **actif** - Gestion lifecycle releases LLM.
- `backend/app/api/v1/routers/admin_llm_sample_payloads.py` - **actif** - CRUD payloads d echantillon pour execution manuelle/replay.
- `backend/app/api/v1/routers/admin_llm_consumption.py` - **actif** - API consommation canonique.
- `backend/app/api/v1/routers/admin_llm_error_codes.py` - **actif** - Codes d erreurs structures pour surfaces admin LLM.

## D. Couche application et services metier declencheurs

- `backend/app/application/llm/ai_engine_adapter.py` - **actif-legacy** - Chemin canonique 70-14, mais re-export transitoire de l implementation historique.
- `backend/app/services/ai_engine_adapter.py` - **actif** - Adaptateur principal runtime metier -> gateway LLM.
- `backend/app/services/guidance_service.py` - **actif** - Cas guidance (delegation vers adapter).
- `backend/app/services/chat_guidance_service.py` - **actif** - Cas chat astrologique (delegation vers adapter).
- `backend/app/services/natal_interpretation_service_v2.py` - **actif** - Cas natal v2 (generation + persistance).
- `backend/app/services/natal_interpretation_service.py` - **actif-legacy** - Chemin legacy encore present pour compatibilite de transition.
- `backend/app/prediction/public_projection.py` - **actif** - Flux horoscope quotidien qui declenche la narration via adapter.

## E. Domaine canonique 70-14 (majoritairement wrappers transitoires)

- `backend/app/domain/llm/runtime/gateway.py` - **actif-legacy** - Point d entree canonique, wrapper de `app.llm_orchestration.gateway`.
- `backend/app/domain/llm/runtime/composition.py` - **actif-legacy** - Wrapper vers injecteurs/mappers historiques (`llm_orchestration.services.*`).
- `backend/app/domain/llm/runtime/validation.py` - **actif-legacy** - Wrapper vers validation historique.
- `backend/app/domain/llm/runtime/fallback.py` - **actif-legacy** - Wrapper vers gouvernance fallback historique.
- `backend/app/domain/llm/runtime/provider_runtime_manager.py` - **actif-legacy** - Wrapper vers runtime manager historique.
- `backend/app/domain/llm/configuration/prompt_versions.py` - **actif-legacy** - Wrapper vers lookup version active historique.
- `backend/app/domain/llm/configuration/assemblies.py` - **actif-legacy** - Wrapper vers registres/resolution assemblies historiques.
- `backend/app/domain/llm/configuration/execution_profiles.py` - **actif-legacy** - Wrapper vers registre de profils historique.
- `backend/app/domain/llm/prompting/renderer.py` - **actif-legacy** - Wrapper vers renderer historique.
- `backend/app/domain/llm/prompting/personas.py` - **actif-legacy** - Wrapper vers composeur persona historique.
- `backend/app/domain/llm/prompting/context.py` - **actif-legacy** - Wrapper vers contexte prompt historique.
- `backend/app/domain/llm/prompting/validation.py` - **actif-legacy** - Wrapper vers validation prompt historique.
- `backend/app/domain/llm/governance/governance.py` - **actif-legacy** - Wrapper vers registres governance/residual historiques.
- `backend/app/domain/llm/legacy/bridge.py` - **actif** - Point unique nominal -> legacy (regle 70-14).

## F. Noyau d implementation effectif actuel (llm_orchestration/prompts/prediction)

- `backend/app/llm_orchestration/gateway.py` - **actif** - Orchestrateur runtime principal (resolution, rendu, provider call, fallback, validation, telemetrie).
- `backend/app/llm_orchestration/models.py` - **actif** - Contrats de requete/reponse et erreurs du pipeline.
- `backend/app/llm_orchestration/prompt_version_lookup.py` - **actif** - Lookup runtime read-only de la version `published`.
- `backend/app/llm_orchestration/services/prompt_renderer.py` - **actif** - Rendu template avec gouvernance placeholders.
- `backend/app/llm_orchestration/services/assembly_resolver.py` - **actif** - Resolution assembly target et composition du prompt final.
- `backend/app/llm_orchestration/services/assembly_registry.py` - **actif** - Lecture/configuration assemblies publiees.
- `backend/app/llm_orchestration/services/assembly_admin_service.py` - **actif** - Logique admin assemblies.
- `backend/app/llm_orchestration/services/execution_profile_registry.py` - **actif** - Selection des profils d execution.
- `backend/app/llm_orchestration/services/provider_parameter_mapper.py` - **actif** - Mapping parametres runtime -> provider.
- `backend/app/llm_orchestration/services/context_quality_injector.py` - **actif** - Injection de garde-fous selon qualite de contexte.
- `backend/app/llm_orchestration/services/length_budget_injector.py` - **actif** - Injection contraintes longueur/taille.
- `backend/app/llm_orchestration/services/observability_service.py` - **actif** - Enregistrement telemetrie et purge logs.
- `backend/app/llm_orchestration/services/release_service.py` - **actif** - Build/validate/activation snapshots releases.
- `backend/app/llm_orchestration/services/golden_regression_service.py` - **actif** - Verification golden regression.
- `backend/app/llm_orchestration/services/replay_service.py` - **actif** - Replay de calls LLM pour diagnostic.
- `backend/app/llm_orchestration/services/prompt_registry_v2.py` - **actif** - Gestion lifecycle prompt versions cote admin.
- `backend/app/llm_orchestration/providers/provider_runtime_manager.py` - **actif** - Pilotage runtime provider/fallback.
- `backend/app/llm_orchestration/providers/responses_client.py` - **actif-legacy** - Client provider historique (progressivement converge vers infrastructure).
- `backend/app/llm_orchestration/prompt_governance_registry.py` - **actif** - Registre gouvernance placeholders.
- `backend/app/llm_orchestration/legacy_residual_registry.py` - **actif-legacy** - Registre residus legacy de transition.
- `backend/app/llm_orchestration/legacy_prompt_runtime.py` - **actif-legacy** - Mappings legacy et fonctions de compatibilite.
- `backend/app/prompts/common_context.py` - **actif** - Construction contexte commun/qualifie injecte dans prompts.
- `backend/app/prompts/catalog.py` - **actif-legacy** - Catalogue historique encore present pour compat/tests.
- `backend/app/prediction/astrologer_prompt_builder.py` - **actif** - Construction de prompt narratif astrologique.
- `backend/app/prediction/llm_narrator.py` - **obsolète** - Module marque deprecie au profit de l adapter/gateway (conserve pour compat/tests).

## G. Infrastructure DB, repositories et providers

- `backend/app/infrastructure/db/repositories/llm/prompting_repository.py` - **actif** - Point central de lectures persistantes LLM (prompts/use-cases/releases/payloads).
- `backend/app/infrastructure/db/models/llm_prompt.py` - **actif** - Modeles `llm_use_case_configs` et `llm_prompt_versions`.
- `backend/app/infrastructure/db/models/llm_assembly.py` - **actif** - Modeles assemblies.
- `backend/app/infrastructure/db/models/llm_execution_profile.py` - **actif** - Modeles profils execution.
- `backend/app/infrastructure/db/models/llm_persona.py` - **actif** - Modeles personas.
- `backend/app/infrastructure/db/models/llm_output_schema.py` - **actif** - Modeles schemas de sortie.
- `backend/app/infrastructure/db/models/llm_release.py` - **actif** - Modeles snapshots releases.
- `backend/app/infrastructure/db/models/llm_sample_payload.py` - **actif** - Modeles payloads sample.
- `backend/app/infrastructure/db/models/llm_observability.py` - **actif** - Modeles logs/observabilite.
- `backend/app/infrastructure/db/models/llm_canonical_consumption.py` - **actif** - Modeles consommation canonique.
- `backend/app/infrastructure/providers/llm/openai_responses_client.py` - **actif-legacy** - Chemin canonique introduit mais encore adosse aux composants historiques.

## H. Ops LLM (scripts canoniques 70-14)

- `backend/app/ops/llm/bootstrap/seed_29_prompts.py` - **actif** - Seed natal historique (appele au bootstrap dev conditionnel).
- `backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py` - **actif** - Seed natal v3.
- `backend/app/ops/llm/bootstrap/seed_30_14_chat_prompt.py` - **actif** - Seed prompt chat astrologer.
- `backend/app/ops/llm/release/build_release_candidate.py` - **actif** - Generation artefact candidate + validation snapshot.
- `backend/app/ops/llm/release/build_release_readiness_report.py` - **actif** - Rapport readiness go/no-go.
- `backend/app/ops/llm/release/build_qualification_evidence.py` - **actif** - Evidence qualification.
- `backend/app/ops/llm/release/build_golden_evidence.py` - **actif** - Evidence golden regression.
- `backend/app/ops/llm/release/build_smoke_evidence.py` - **actif** - Evidence smoke.
- `backend/app/ops/llm/TRANSITION_WRAPPERS.md` - **actif** - Registre des wrappers transitoires et criteres de sortie.

## I. Wrappers de compatibilite dans backend/scripts

- `backend/scripts/build_llm_release_candidate.py` - **actif-legacy** - Wrapper vers `app.ops.llm.release.build_release_candidate`.
- `backend/scripts/build_llm_release_readiness_report.py` - **actif-legacy** - Wrapper vers script ops canonique.
- `backend/scripts/build_llm_qualification_evidence.py` - **actif-legacy** - Wrapper vers script ops canonique.
- `backend/scripts/build_llm_golden_evidence.py` - **actif-legacy** - Wrapper vers script ops canonique.
- `backend/scripts/build_llm_smoke_evidence.py` - **actif-legacy** - Wrapper vers script ops canonique.

## Synthese des statuts

- **actif**: pipeline nominal fonctionne via ces fichiers; requis en prod/dev nominal.
- **actif-legacy**: encore execute/importe, mais principalement pour transition de chemins et compatibilite outillage.
- **incertain**: non retenu dans cette liste principale faute de preuve d execution reguliere post-70.14.
- **obsolete**: composant explicitement deprecie ou non cible du runtime nominal.

Repartition observee (sur cet inventaire):
- `actif`: majoritaire sur le coeur runtime et la persistence.
- `actif-legacy`: concentre sur wrappers canoniques 70-14 et wrappers `backend/scripts`.
- `obsolete`: `prediction/llm_narrator.py`.

## Conclusion

Le backend est fonctionnel et mieux structure apres la story 70-14, mais reste en phase de transition: les chemins canoniques `api/application/domain/infrastructure/ops` sont bien en place, tandis qu une partie de l implementation reste centralisee dans `llm_orchestration` et exposee via wrappers.  
Le risque principal n est pas une rupture fonctionnelle immediate, mais la confusion de maintenance tant que les wrappers `actif-legacy` ne sont pas progressivement remplaces par des implementations directement hebergees dans les namespaces canoniques.
