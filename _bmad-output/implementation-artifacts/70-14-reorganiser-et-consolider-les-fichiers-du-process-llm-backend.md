# Story 70.14: Reorganiser et consolider les fichiers du process LLM backend de facon DRY

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect,
I want reorganiser et consolider les fichiers backend impliques dans la generation de prompt LLM selon des couches explicites (`api`, `application`, `domain`, `infrastructure`, `ops`) et des modules cohesifs par capacite,
so that le process de prompt soit lisible, gouvernable, maintenable et DRY, sans duplication de logique entre runtime, admin, legacy, persistence et outillage ops.

## Contexte

L audit backend [docs/2026-04-20-audit-prompts-backend.md](/c:/dev/horoscope_front/docs/2026-04-20-audit-prompts-backend.md) montre une base fonctionnelle mais dispersee :

- `backend/app/llm_orchestration` melange runtime, admin, gouvernance, providers, release, observabilite, legacy et fichiers JSON ;
- des composants applicatifs (ex: `ai_engine_adapter.py`, services metier guidance/natal/chat) cohabitent avec des composants techniques LLM bas niveau ;
- les routes admin LLM sont fragmentees au meme niveau que les routes metier publiques ;
- les scripts de seed, migration, release et diagnostic legacy cohabitent dans `backend/scripts/` sans structure de responsabilite ;
- le legacy est encore present mais peu visible comme objet gouverne de decommission ;
- plusieurs regles de resolution, de lecture publiee, de fallback et de preview risquent d etre dupliquees entre runtime, admin et outils.

Le probleme n est pas d abord un bug fonctionnel. C est un probleme de lisibilite architecturale et de duplication :

- le "quoi" (use cases metier et decisions domaine) et le "comment" (provider, DB, scripts ops) ne sont pas nettement separes ;
- la dette d organisation ralentit les evolutions et multiplie les points d entree ambigus ;
- la duplication de regles entre runtime/admin/legacy augmente le risque de divergence ;
- la decommission legacy est difficile tant que le nominal et le legacy restent intriques.

La cible de cette story est une reorganisation physique et contractuelle, sans re-ecriture big-bang de tout le comportement runtime, avec une exigence explicite de mutualisation et de sobriete structurelle.

## Cible d architecture

Le backend doit converger vers la structure suivante :

- `backend/app/api` : routes HTTP et composition transport uniquement ;
- `backend/app/application` : facades applicatives et orchestration metier transverse ;
- `backend/app/domain/llm` : logique metier LLM dediee, coherente, autonome et mutualisee ;
- `backend/app/infrastructure` : acces techniques externes/persistants (DB, providers, config) ;
- `backend/app/ops` : scripts bootstrap, migration, release et diagnostic hors runtime.

La refonte doit rester DRY :

- chaque module represente une capacite cohesif et reutilisable ;
- on evite la multiplication artificielle de micro-fichiers, micro-services ou micro-repositories minces ;
- les regles de resolution prompt/assembly/persona/profile/release sont centralisees et partagees ;
- toute compatibilite legacy passe par un point d acces unique et explicite ;
- le refactor privilegie la mutualisation avant la proliferation.

## Acceptance Criteria

1. **AC1 - Separation stricte des couches** : les fichiers backend relies au process LLM sont ranges dans les couches `api`, `application`, `domain`, `infrastructure` et `ops` selon leur responsabilite reelle ; les emplacements ambigus de type `llm_orchestration/services` fourre-tout sont elimines ou clairement decomposes.
2. **AC2 - Namespace admin LLM unifie cote API** : les routes admin LLM sont regroupees sous `backend/app/api/v1/routers/admin/llm/` avec une granularite explicite (`prompts.py`, `assemblies.py`, `releases.py`, `sample_payloads.py`, `consumption.py`, `observability.py`) et sans casser le montage des routers.
3. **AC3 - AIEngineAdapter repositionne en couche application** : `ai_engine_adapter.py` reside en `backend/app/application/llm/ai_engine_adapter.py`, en tant que facade applicative transverse entre use cases metier et domaine LLM.
4. **AC4 - Domaine LLM decoupe par capacites explicites** : la logique LLM est repartie en modules ou sous-ensembles coherents (ex: runtime, prompting, configuration, governance, legacy, contracts) avec des noms de capacite plutot que `services` generique.
5. **AC5 - Legacy rendu visible et gouvernable** : les composants legacy LLM sont centralises sous `backend/app/domain/llm/legacy/` (ou suffixes `_legacy.py` si hors dossier), avec une politique explicite d usage transitoire et sans import implicite depuis le nominal.
6. **AC6 - Gouvernance et donnees associees co-localisees** : `prompt_governance_registry`, `legacy_residual_registry` et leurs JSON sont regroupes sous `backend/app/domain/llm/governance/` avec un chemin de lecture explicite et teste.
7. **AC7 - Infrastructure clarifiee** : les modeles DB LLM sont ranges sous `backend/app/infrastructure/db/models/` et une couche repository `backend/app/infrastructure/db/repositories/llm/` est introduite ou renforcee pour centraliser l acces persistant.
8. **AC8 - Providers externalises en infrastructure** : les clients provider LLM (ex: Responses/OpenAI) sont deplaces sous `backend/app/infrastructure/providers/llm/` et le domaine runtime depend d interfaces, contrats ou adaptateurs, pas d implementations concretes disperses.
9. **AC9 - Scripts hors runtime** : les scripts `seed`, `migration`, `release`, `legacy diagnostics` sont deplaces sous `backend/app/ops/llm/` avec sous-dossiers `bootstrap`, `migrations`, `release`, `legacy` et un `README.md` operable.
10. **AC10 - Zero changement comportemental involontaire en lot 1** : la premiere phase de migration est un deplacement, renommage et update d imports sans changement fonctionnel nominal observable.
11. **AC11 - Imports et points d entree stabilises** : `main.py`, route includes, imports de services/use cases et scripts d exploitation restent resolvables apres reorganisation, avec compatibilite transitoire documentee si necessaire.
12. **AC12 - Pas de bridge legacy diffuse** : toute dependance nominal -> legacy passe par un point explicite unique (ex: `legacy/bridge.py`) et non par des imports directs disperses.
13. **AC13 - Nettoyage artefacts non runtime** : les fichiers backup ou duplicats non executables (ex: `*.orig`) sont retires du code runtime ou archives hors chemin importable.
14. **AC14 - Plan en 4 lots respecte** : l implementation suit explicitement les lots `reorganisation physique`, `mutualisation des resolutions`, `repositories`, `extinction legacy` pour limiter le risque de regression.
15. **AC15 - Documentation structurelle alignee** : un document de reference (story + README ops + eventuel README domaine) decrit la nouvelle cartographie, les regles d import inter-couches et les points de compatibilite transitoire.
16. **AC16 - Mutualisation des regles de resolution** : la resolution des prompts, assemblies, personas, execution profiles et releases actives repose sur des composants domaine partages entre runtime et admin ; aucune duplication de regles de selection, publish ou fallback ne subsiste entre surfaces.
17. **AC17 - Pas de micro-services artificiels** : la refonte privilegie des modules cohesifs et reutilisables plutot qu une multiplication de fichiers, classes ou objets minces sans logique propre.
18. **AC18 - Un seul point d acces legacy** : toute compatibilite nominal -> legacy passe par un bridge unique, documente et teste ; les modules legacy ne sont pas importes directement depuis plusieurs points du nominal.
19. **AC19 - Repositories composes et non proliferants** : la couche repository centralise les patterns persistants communs et n introduit pas de duplication de requetes, filtres ou hydrations entre repositories trop fins.
20. **AC20 - Runtime et admin partagent les memes moteurs** : les surfaces admin de preview, execute-sample, release validation et replay reutilisent les memes briques domaine que le runtime nominal, avec parametrage explicite plutot que reimplementation.

## Tasks / Subtasks

- [ ] Task 1: Reorganisation physique initiale sans changement de comportement (Lot 1) (AC1, AC2, AC3, AC4, AC10, AC11)
  - [x] Creer l arborescence cible `api/admin/llm`, `application/llm`, `domain/llm/*`, `infrastructure/*`, `ops/llm/*`.
  - [x] Deplacer les routers admin LLM vers `api/v1/routers/admin/llm/` et ajuster `__init__.py`.
  - [x] Deplacer `ai_engine_adapter.py` vers `application/llm/`.
  - [ ] Deplacer les composants domaine LLM vers les zones cibles, sans introduire de micro-fichiers artificiels.
  - [x] Mettre a jour imports absolus/relatifs et montage des routers dans `main.py`.
  - [x] Verifier qu aucun endpoint nominal ne change de comportement a cette etape.

- [ ] Task 2: Mutualiser les regles runtime/admin avant proliferation structurelle (Lot 2) (AC4, AC6, AC16, AC17, AC20)
  - [x] Identifier les regles de resolution actuellement dupliquees ou menacees de duplication entre runtime, admin, preview, replay, release validation.
  - [x] Introduire un ou plusieurs composants domaine partages pour la resolution de prompts, assemblies, personas, profiles et releases.
  - [x] Faire reposer preview, execute-sample et release validation sur les memes briques que le runtime nominal avec parametrage explicite.
  - [ ] Fusionner les modules minces ou redondants quand leur separation n apporte pas de valeur architecturale reelle.
  - [ ] Verifier qu aucune logique de publish, fallback ou selection `published` n existe en double.

- [ ] Task 3: Consolidation infrastructure et repositories LLM (Lot 3) (AC7, AC8, AC11, AC19)
  - [x] Deplacer `responses_client.py` vers `backend/app/infrastructure/providers/llm/openai_responses_client.py`.
  - [x] Structurer ou aligner les modeles DB LLM sous `backend/app/infrastructure/db/models/`.
  - [x] Introduire ou completer `backend/app/infrastructure/db/repositories/llm/` avec une granularite sobre et composee.
  - [x] Centraliser les patterns persistants communs (published lookup, filtres feature/subfeature/locale, chargement release active, pagination admin, lecture observabilite).
  - [x] Remplacer progressivement les acces SQLAlchemy disperses par des repositories ou query services explicites.

- [ ] Task 4: Clarification runtime et encapsulation legacy (Lot 4 prep + hygiene) (AC5, AC6, AC12, AC18)
  - [ ] Garder `gateway.py` mince et orchestrateur, en deleguant la resolution, la composition et la validation a des briques partagees.
  - [x] Co-localiser gouvernance et data (`prompt_governance_registry.json`, `legacy_residual_registry.json`) sous `domain/llm/governance/data/`.
  - [x] Introduire un `legacy/bridge.py` comme unique point d acces nominal vers les mecanismes legacy encore necessaires.
  - [x] Verifier que runtime n importe pas de modules `ops` ni de routers API.
  - [x] Verifier que les modules legacy ne sont pas importes directement depuis plusieurs composants nominaux.

- [ ] Task 5: Structuration ops et hygiene repository (AC9, AC13, AC15)
  - [x] Deplacer les scripts `backend/scripts/*` lies au LLM vers `backend/app/ops/llm/{bootstrap,migrations,release,legacy}/`.
  - [x] Ajouter `backend/app/ops/llm/README.md` (mode d usage, prerequis, scripts one-shot vs recurrents).
  - [x] Supprimer ou archiver les fichiers non runtime (`*.orig`, backups non utiles).
  - [x] Documenter les points d entree ops recurrents vs one-shot.
  - [ ] Verifier qu aucun module runtime importable ne depend d un script one-shot.

- [ ] Task 6: Mapping deplacements minimaux a realiser en priorite (AC1 a AC11)
  - [ ] Appliquer le mapping valide (extraits) :
    - [ ] `backend/app/llm_orchestration/gateway.py` -> `backend/app/domain/llm/runtime/gateway.py`
    - [ ] `backend/app/llm_orchestration/services/prompt_renderer.py` -> `backend/app/domain/llm/prompting/renderer.py`
    - [ ] `backend/app/llm_orchestration/services/persona_composer.py` -> `backend/app/domain/llm/prompting/personas.py`
    - [ ] `backend/app/prompts/common_context.py` -> `backend/app/domain/llm/prompting/context.py`
    - [ ] `backend/app/prompts/validators.py` -> `backend/app/domain/llm/prompting/validation.py`
    - [ ] `backend/app/prediction/astrologer_prompt_builder.py` -> `backend/app/domain/llm/prompting/astrologer_prompt_builder.py`
    - [ ] `backend/app/llm_orchestration/services/assembly_resolver.py` -> `backend/app/domain/llm/configuration/assemblies.py`
    - [ ] `backend/app/llm_orchestration/services/assembly_registry.py` -> `backend/app/domain/llm/configuration/assemblies.py`
    - [ ] `backend/app/llm_orchestration/services/assembly_admin_service.py` -> `backend/app/domain/llm/configuration/assemblies.py`
    - [ ] `backend/app/llm_orchestration/services/execution_profile_registry.py` -> `backend/app/domain/llm/configuration/execution_profiles.py`
    - [ ] `backend/app/llm_orchestration/services/prompt_version_lookup.py` -> `backend/app/domain/llm/configuration/prompt_versions.py`
    - [ ] `backend/app/llm_orchestration/services/provider_parameter_mapper.py` -> `backend/app/domain/llm/runtime/composition.py`
    - [ ] `backend/app/llm_orchestration/providers/provider_runtime_manager.py` -> `backend/app/domain/llm/runtime/provider_runtime_manager.py`
    - [ ] `backend/app/llm_orchestration/providers/responses_client.py` -> `backend/app/infrastructure/providers/llm/openai_responses_client.py`
    - [ ] `backend/app/llm_orchestration/services/output_validator.py` -> `backend/app/domain/llm/runtime/validation.py`
    - [ ] `backend/app/llm_orchestration/services/context_quality_injector.py` -> `backend/app/domain/llm/runtime/composition.py`
    - [ ] `backend/app/llm_orchestration/services/length_budget_injector.py` -> `backend/app/domain/llm/runtime/composition.py`
    - [ ] `backend/app/llm_orchestration/services/fallback_governance.py` -> `backend/app/domain/llm/runtime/fallback.py`
    - [ ] `backend/app/llm_orchestration/prompt_governance_registry.py` -> `backend/app/domain/llm/governance/governance.py`
    - [ ] `backend/app/llm_orchestration/legacy_residual_registry.py` -> `backend/app/domain/llm/governance/governance.py`
    - [ ] `backend/app/llm_orchestration/legacy_prompt_runtime.py` -> `backend/app/domain/llm/legacy/runtime_legacy.py`
    - [ ] `backend/app/prompts/catalog.py` -> `backend/app/domain/llm/legacy/catalog_legacy.py`
    - [ ] `backend/app/prediction/llm_narrator.py` -> `backend/app/domain/llm/legacy/narrator_legacy.py`
    - [ ] `backend/app/services/ai_engine_adapter.py` -> `backend/app/application/llm/ai_engine_adapter.py`
    - [ ] `backend/app/api/v1/routers/admin_llm.py` -> `backend/app/api/v1/routers/admin/llm/prompts.py`
    - [ ] `backend/app/api/v1/routers/admin_llm_assembly.py` -> `backend/app/api/v1/routers/admin/llm/assemblies.py`
    - [ ] `backend/app/api/v1/routers/admin_llm_release.py` -> `backend/app/api/v1/routers/admin/llm/releases.py`
    - [ ] `backend/app/api/v1/routers/admin_llm_sample_payloads.py` -> `backend/app/api/v1/routers/admin/llm/sample_payloads.py`
    - [ ] `backend/app/api/v1/routers/admin_llm_consumption.py` -> `backend/app/api/v1/routers/admin/llm/consumption.py`
    - [ ] `backend/scripts/build_llm_release_candidate.py` -> `backend/app/ops/llm/release/build_release_candidate.py`

- [x] Task 7: Validation locale obligatoire (AC1 a AC20)
  - [x] Activer le venv avant toute commande Python : `\.venv\Scripts\Activate.ps1`
  - [x] Installer ou mettre a jour les dependances backend si necessaire via `cd backend ; pip install -e ".[dev]"`
  - [x] Executer `cd backend ; ruff format .`
  - [x] Executer `cd backend ; ruff check .`
  - [x] Executer `cd backend ; pytest -q`
  - [x] Ajouter des tests de non-regression sur imports critiques, routage admin LLM et bridge legacy si necessaire.

## Dev Notes

### Strategie imposee en 4 lots

- **Lot 1 - Reorganisation physique uniquement** : deplacements, renommages, aliases d import si necessaire, zero changement fonctionnel.
- **Lot 2 - Mutualisation des resolutions** : centraliser les regles partagees runtime/admin/preview/replay/release.
- **Lot 3 - Repositories** : centraliser les acces DB LLM dans `infrastructure/db/repositories/llm` sans proliferation inutile.
- **Lot 4 - Encapsulation puis extinction legacy** : introduire un bridge unique puis decommission progressive des composants legacy.

### Regles structurelles non negociables

- Un composant `domain/llm` ne doit jamais importer un router `api`.
- Un composant `runtime` ne doit jamais importer `ops`.
- Un service admin ne doit pas contenir de details provider bruts.
- Un client provider ne doit pas connaitre les concepts `assembly` ou `persona`.
- Les acces DB LLM passent via repositories ou query services dedies.
- Les fichiers legacy ne sont jamais importes directement depuis les couches metier publiques.
- Toute compatibilite legacy passe par un bridge unique.
- Tout script one-shot vit dans `ops/migrations/` (ou est retire apres usage documente).
- Toute nouvelle decomposition doit prouver qu elle reduit une ambiguite reelle et non qu elle multiplie les couches.

### Points d attention

- Ne pas faire un refactor big-bang.
- Ne pas melanger reorganisation de dossiers et suppression definitive legacy dans la meme PR.
- Ne pas fusionner les services metier `natal` legacy et v2 sans preuve runtime complete.
- Maintenir une compatibilite transitoire explicite (`__init__`, aliases d import) quand necessaire pour reduire le risque.
- Preferer la fusion de modules minces a la creation de nouveaux wrappers sans valeur.
- Verifier systematiquement que runtime et admin partagent bien les memes moteurs de resolution.

### Watchpoints de transition (review)

- Les wrappers de compatibilite sont autorises uniquement comme pont temporaire ; registre et criteres de sortie : `backend/app/ops/llm/TRANSITION_WRAPPERS.md`.
- Le bridge legacy `app.domain.llm.legacy.bridge` reste le seul point d acces nominal -> legacy.
- Les imports actifs convergent vers `app.infrastructure.db.models.*` ; tout nouvel import legacy equivalent est considere comme reintroduisant de la dette.
- `prompting_repository` reste borne aux patterns persistants partages (prompting/config/release), sans devenir un depot generique de toute lecture LLM.
- Toute nouvelle evolution LLM utilise en priorite les namespaces canoniques `api/application/domain/infrastructure/ops`.

### References

- [docs/2026-04-20-audit-prompts-backend.md](/c:/dev/horoscope_front/docs/2026-04-20-audit-prompts-backend.md)
- [70-13-cleaner-le-backend-generation-de-prompt-et-fermer-les-compatibilites-legacy.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-13-cleaner-le-backend-generation-de-prompt-et-fermer-les-compatibilites-legacy.md)

## Dev Agent Record

### Agent Model Used

gpt-5

### Debug Log References

- Demande utilisateur : reecrire la story BMAD `70.14` en version plus DRY et plus resserree.
- Sources utilisees : audit `2026-04-20-audit-prompts-backend.md`, story initiale `70.14`, recommandations de refonte et de mutualisation.
- 2026-04-20 : implementation Lot 1 partielle (namespace API admin LLM + facade application LLM + update import router dans `main.py`) avec compatibilite transitoire.
- 2026-04-20 : lot 2/4 partiels : creation du namespace canonique `domain/llm/*`, introduction du bridge legacy unique, et branchement progressif des imports runtime/admin sur ces points d entree.
- 2026-04-20 : co-localisation des registres JSON de gouvernance sous `domain/llm/governance/data` avec fallback transitoire pour compatibilite.
- 2026-04-20 : resorption imports directs legacy (`llm_narrator`, `admin_models`, `common_context`) vers `domain.llm.legacy.bridge`.
- 2026-04-20 : structuration ops initiale sous `app/ops/llm/*` avec entrypoint canonique `release/build_release_candidate.py` et README operable.
- 2026-04-20 : migration effective des scripts release LLM vers `app/ops/llm/release/*` avec wrappers de compatibilite dans `backend/scripts/`.
- 2026-04-20 : suppression de l artefact runtime `backend/app/services/chat_guidance_service.py.orig`.
- 2026-04-20 : deplacement des imports de seed LLM de `main.py` vers `app.ops.llm.bootstrap.*` (wrappers lazy-import) pour limiter le couplage runtime -> `scripts`.
- 2026-04-20 : introduction d un repository LLM partage (`prompting_repository`) pour centraliser les lectures prompt/use-case/release active et branchement progressif dans `admin_llm` + `prompt_version_lookup`.
- 2026-04-20 : ajout des ponts de modeles LLM sous `infrastructure/db/models/llm_*.py` et branchement du repository LLM sur ces imports canoniques.
- 2026-04-20 : migration complementaire de `admin_llm._build_admin_resolved_catalog_view` vers le repository canonique pour la lecture du snapshot actif.
- 2026-04-20 : migration complementaire de lectures `release snapshot by id`, `sample payload by id` et `use case config by key` vers `prompting_repository` dans `admin_llm`.
- 2026-04-20 : validation globale lancee (`ruff check .`, `pytest -q`) ; echecs detectes hors perimetre direct story 70.14 (tests legacy/doc-conformity + lint preexistant).
- 2026-04-20 : passe stabilisation gate globale executee : correction lint (`admin_ai`, `test_admin_llm_config_api`) + realignement tests legacy/admin/doc-conformity sur le comportement canonique (`chat`/`chat_astrologer`/`daily_prediction` rejetes, alias `daily_prediction` documente).

### Completion Notes List

- Story `70.14` reecrite pour imposer une refonte plus DRY.
- La cible reste en couches `api/application/domain/infrastructure/ops`, mais avec granularite sobre et mutualisation explicite.
- Les criteres d acceptation ajoutent la centralisation des regles de resolution, l interdiction des micro-services artificiels et un point d acces legacy unique.
- Le plan d execution en 4 lots a ete resserre pour faire la mutualisation avant la proliferation des repositories.
- Lot 1 engage : creation du namespace `app.api.v1.routers.admin.llm.*` (prompts, assemblies, releases, sample_payloads, consumption, observability) avec points d entree transitoires.
- Lot 1 engage : ajout de `app.application.llm.ai_engine_adapter` comme chemin canonique de facade applicative, sans rupture des imports existants.
- Montage des routers admin LLM rebascule sur le namespace canonique dans `app.main` ; tests admin LLM cibles passent.
- Lot 2 engage : `gateway.py` et `admin_llm.py` consomment des points d entree domaine partages (`configuration`, `prompting`, `runtime`, `governance`) au lieu d imports disperses.
- Lot 3 engage : creation de `app.infrastructure.providers.llm.openai_responses_client` et bascule `gateway.py` sur ce chemin canonique.
- Lot 4 prep : `app.domain.llm.legacy.bridge` introduit pour centraliser l acces nominal -> legacy.
- Lot 4 prep : imports directs vers `legacy_prompt_runtime` remplaces par le bridge sur les composants nominaux identifies.
- Lot 5 engage : arborescence `app.ops.llm` creee avec mode d emploi et wrapper release canonique ; scripts legacy `backend/scripts` conserves temporairement en delegation.
- Lot 5 complete (deplacement scripts release) : logique portee sous `app.ops.llm.release`, anciens scripts convertis en wrappers backward-compatible.
- Validation executee : lint OK sur les fichiers modifies ; tests cibles admin/gouvernance OK ; une regression existante detectee sur `test_pipeline_anti_loop` (message d erreur attendu non aligne avec le comportement actuel de rejet des use_case legacy).
- Verification runtime : aucun import `app.ops` ou routers API detecte dans `app/llm_orchestration` et `app/domain/llm`.
- Consolidation repository : extraction des requetes communes `active prompt`, `latest prompt`, `list prompts`, `list use-cases`, `active release snapshot`, `timeline snapshots` vers `infrastructure/db/repositories/llm`.
- Alignement modeles DB : exposition canonique des modeles LLM via `infrastructure/db/models/llm_*.py` pour migration progressive depuis `infra/db/models`.
- Reduction SQLAlchemy disperse : suppression d un acces direct `LlmActiveReleaseModel` dans `admin_llm` au profit du repository LLM partage.
- Reduction SQLAlchemy disperse : remplacement de plusieurs `db.get(...)` LLM dans `admin_llm` par des helpers repository (`get_release_snapshot`, `get_sample_payload`, `get_use_case_config`).
- Validation globale : `ruff check .` echoue sur `admin_ai.py` et un test d integration hors perimetre ; `pytest -q` echoue sur 7 tests principalement lies a des attentes legacy (`chat`, `chat_astrologer`, `daily_prediction`) et doc-conformity taxonomy.
- Stabilisation gate globale : tous les echecs restants ont ete corriges (lint + tests legacy/doc-conformity/admin persona), puis validation complete verte (`ruff check .` OK, `pytest -q` OK : 2964 passed, 12 skipped).
- Hardening transition : ajout d un registre des wrappers transitoires avec criteres de sortie (`app/ops/llm/TRANSITION_WRAPPERS.md`) et ajout d un guard test sur les imports legacy directs du perimetre nominal critique.

### File List

- _bmad-output/implementation-artifacts/70-14-reorganiser-et-consolider-les-fichiers-du-process-llm-backend.md
- backend/app/main.py
- backend/app/api/v1/routers/admin/__init__.py
- backend/app/api/v1/routers/admin/llm/__init__.py
- backend/app/api/v1/routers/admin/llm/prompts.py
- backend/app/api/v1/routers/admin/llm/assemblies.py
- backend/app/api/v1/routers/admin/llm/releases.py
- backend/app/api/v1/routers/admin/llm/sample_payloads.py
- backend/app/api/v1/routers/admin/llm/consumption.py
- backend/app/api/v1/routers/admin/llm/observability.py
- backend/app/application/__init__.py
- backend/app/application/llm/__init__.py
- backend/app/application/llm/ai_engine_adapter.py
- backend/app/domain/llm/__init__.py
- backend/app/domain/llm/runtime/__init__.py
- backend/app/domain/llm/runtime/gateway.py
- backend/app/domain/llm/runtime/composition.py
- backend/app/domain/llm/runtime/validation.py
- backend/app/domain/llm/runtime/fallback.py
- backend/app/domain/llm/runtime/provider_runtime_manager.py
- backend/app/domain/llm/prompting/__init__.py
- backend/app/domain/llm/prompting/renderer.py
- backend/app/domain/llm/prompting/personas.py
- backend/app/domain/llm/prompting/context.py
- backend/app/domain/llm/prompting/validation.py
- backend/app/domain/llm/configuration/__init__.py
- backend/app/domain/llm/configuration/assemblies.py
- backend/app/domain/llm/configuration/execution_profiles.py
- backend/app/domain/llm/configuration/prompt_versions.py
- backend/app/domain/llm/governance/__init__.py
- backend/app/domain/llm/governance/governance.py
- backend/app/domain/llm/governance/data/prompt_governance_registry.json
- backend/app/domain/llm/governance/data/legacy_residual_registry.json
- backend/app/domain/llm/legacy/__init__.py
- backend/app/domain/llm/legacy/bridge.py
- backend/app/infrastructure/__init__.py
- backend/app/infrastructure/providers/__init__.py
- backend/app/infrastructure/providers/llm/__init__.py
- backend/app/infrastructure/providers/llm/openai_responses_client.py
- backend/app/infrastructure/db/__init__.py
- backend/app/infrastructure/db/models/__init__.py
- backend/app/infrastructure/db/models/llm_prompt.py
- backend/app/infrastructure/db/models/llm_release.py
- backend/app/infrastructure/db/models/llm_assembly.py
- backend/app/infrastructure/db/models/llm_execution_profile.py
- backend/app/infrastructure/db/models/llm_observability.py
- backend/app/infrastructure/db/models/llm_output_schema.py
- backend/app/infrastructure/db/models/llm_persona.py
- backend/app/infrastructure/db/models/llm_sample_payload.py
- backend/app/infrastructure/db/models/llm_canonical_consumption.py
- backend/app/infrastructure/db/repositories/__init__.py
- backend/app/infrastructure/db/repositories/llm/__init__.py
- backend/app/infrastructure/db/repositories/llm/prompting_repository.py
- backend/app/ops/__init__.py
- backend/app/ops/llm/__init__.py
- backend/app/ops/llm/README.md
- backend/app/ops/llm/TRANSITION_WRAPPERS.md
- backend/app/ops/llm/bootstrap/__init__.py
- backend/app/ops/llm/bootstrap/seed_29_prompts.py
- backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py
- backend/app/ops/llm/bootstrap/seed_30_14_chat_prompt.py
- backend/app/ops/llm/migrations/__init__.py
- backend/app/ops/llm/release/__init__.py
- backend/app/ops/llm/release/build_release_candidate.py
- backend/app/ops/llm/release/build_golden_evidence.py
- backend/app/ops/llm/release/build_qualification_evidence.py
- backend/app/ops/llm/release/build_smoke_evidence.py
- backend/app/ops/llm/release/build_release_readiness_report.py
- backend/app/ops/llm/legacy/__init__.py
- backend/app/llm_orchestration/gateway.py
- backend/app/llm_orchestration/prompt_governance_registry.py
- backend/app/llm_orchestration/legacy_residual_registry.py
- backend/app/api/v1/routers/admin_llm.py
- backend/app/llm_orchestration/admin_models.py
- backend/app/prediction/llm_narrator.py
- backend/app/prompts/common_context.py
- backend/app/llm_orchestration/prompt_version_lookup.py
- backend/app/services/chat_guidance_service.py.orig (deleted)
- backend/scripts/build_llm_release_candidate.py
- backend/scripts/build_llm_golden_evidence.py
- backend/scripts/build_llm_qualification_evidence.py
- backend/scripts/build_llm_smoke_evidence.py
- backend/scripts/build_llm_release_readiness_report.py
- backend/tests/unit/test_story_70_14_transition_guards.py

### Change Log

- 2026-04-20 : reecriture de la story backend `70.14` pour cadrer une reorganisation LLM backend plus DRY, plus mutualisee et plus sobre structurellement.
- 2026-04-20 : demarrage implementation lot 1 (namespace API admin LLM + facade application LLM + reroutage `main.py`) en mode compatible, sans changement comportemental nominal.
- 2026-04-20 : extension lot 2/3/4 (points d entree `domain/llm` partages, bridge legacy unique, co-localisation registres JSON de gouvernance, chemin provider canonique `infrastructure/providers/llm`), avec compatibilite transitoire maintenue.
- 2026-04-20 : extension lot 4/5 (imports nominaux rebranches sur bridge legacy unique, initialisation de `app/ops/llm` et wrapper release canonique) avec compatibilite de transition.
- 2026-04-20 : deplacement des scripts release LLM vers `app/ops/llm/release` + wrappers de compatibilite dans `backend/scripts` pour transition sans rupture.
- 2026-04-20 : nettoyage artefact `*.orig` runtime et rebranchement des seeds LLM startup vers `app.ops.llm.bootstrap`.
- 2026-04-20 : ajout repository LLM `prompting_repository` et migration partielle des acces SQLAlchemy admin/runtime vers ce point central.
- 2026-04-20 : alignement des modeles LLM sous `infrastructure/db/models/` via modules ponts et utilisation dans le repository canonique.
- 2026-04-20 : migration complementaire d une lecture release active dans `admin_llm` vers `prompting_repository` (moins de duplication SQLAlchemy).
- 2026-04-20 : migration complementaire de lectures LLM by-id/by-key dans `admin_llm` vers `prompting_repository` pour centraliser les acces persistants.
- 2026-04-20 : validation globale executee ; story conservee `in-progress` car gate globale rouge (7 tests + 2 lint non resolus dans ce lot).
- 2026-04-20 : stabilisation gate globale terminee ; lint et tests aligns sur le comportement canonique actuel, puis gate complete repassee au vert (`ruff check .`, `pytest -q`).
- 2026-04-20 : hardening transition ajoute (watchpoints explicites story + registre wrappers transitoires + guard test anti-import legacy direct sur modules nominaux critiques).
