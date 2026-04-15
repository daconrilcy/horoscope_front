# Story 66.45: Vue catalogue canonique des prompts actifs

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin ops / release operator,
I want consulter `/admin/prompts` comme un catalogue canonique gouverne par `feature/subfeature/plan/locale` et aligne sur le snapshot actif,
so that l'UI admin reflète enfin la verite runtime du pipeline LLM et non l'ancien modele `use_case -> prompt/persona`.

## Contexte

L'epic 65 a introduit une page `/admin/prompts` utile pour consulter l'historique des prompts, comparer des versions et rollback une version de `LlmPromptVersionModel`. Cette surface reste cependant centree sur l'ancien axe `use_case`, alors que l'epic 66 a fait converger le runtime nominal vers une chaine canonique gouvernee par :

- `feature`, `subfeature`, `plan`, `locale`
- une `PromptAssemblyConfig` resolue
- un `ExecutionProfile` resolu
- un `output_contract_ref`
- un snapshot de release actif et son `manifest_entry_id`
- des signaux d'observabilite comme `execution_path_kind`, `context_compensation_status` et `max_output_tokens_source`

Le document [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) dit explicitement que le runtime nominal ne lit plus "un prompt unique" par use case. Il lit d'abord le snapshot actif, puis l'assembly, puis le profil d'execution, puis la chaine de transformations du prompt. La route admin actuelle reste donc decalee de la verite d'execution.

Le depot contient deja les briques backend permettant de construire cette vue de gouvernance :

- [backend/app/api/v1/routers/admin_llm_assembly.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm_assembly.py) expose les assemblies, leur preview et leur publication
- [backend/app/api/v1/routers/admin_llm_release.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm_release.py) expose les snapshots, leur activation, rollback et `release_health`
- [backend/app/llm_orchestration/services/assembly_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_registry.py) priorise le snapshot actif avant les tables live
- [backend/app/llm_orchestration/services/execution_profile_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/execution_profile_registry.py) applique la meme logique pour les profils
- [backend/app/llm_orchestration/services/release_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/release_service.py) porte `active_snapshot_id`, `active_snapshot_version`, `manifest_entry_id` et `manifest.release_health`

Le trou a fermer est donc purement de gouvernance admin :

- l'ecran `/admin/prompts` doit cesser d'etre la lecture nominale de `use_case`
- la liste primaire doit devenir une table canonique `feature/subfeature/plan/locale`
- la source de verite effective doit etre visible ligne par ligne : snapshot actif si present, sinon fallback live table quand le cas existe encore
- les dimensions d'execution utiles a l'ops doivent etre lisibles sans devoir croiser plusieurs panneaux admin

Cette story ne demande pas encore le detail du prompt compose ni la timeline des snapshots. Ces sujets appartiennent aux stories suivantes 66.46 et 66.47. Ici, l'objectif est la vue catalogue canonique de premier niveau.

## Glossaire UI canonique

- `CatalogEntry` : ligne canonique du catalogue admin
- `manifest_entry_id` : identifiant nominal unique d'une ligne pour la lecture runtime admin
- `canonical_target` : quadruplet contextuel `feature/subfeature/plan/locale`
- `source_of_truth_status` : indique si la ligne est resolue depuis le snapshot actif ou depuis un fallback live explicite
- `assembly_status` : statut de la config assembly sous-jacente (`draft`, `published`, `archived` ou equivalent stable)
- `release_health_status` : statut de sante du snapshot actif (`candidate`, `qualified`, `activated`, `monitoring`, `degraded`, `rollback_recommended`, `rolled_back`)
- `catalog_visibility_status` : etat UI de visibilite d'une ligne (`visible`, `orphaned`, `stale`, `hidden_by_filter` ou equivalent stable) si necessaire pour l'admin
- `runtime_signal_status` : etat de fraicheur d'un signal runtime affiche (`fresh`, `stale`, `n/a`)

## Scope et permissions

- Scope de la story : **lecture seule + navigation croisee**. Aucune nouvelle action operatoire de release, publish ou rollback n'est dans le scope de 66.45.
- Lecture catalogue : accessible aux profils admin autorises a consulter la gouvernance LLM.
- Affichage des colonnes techniques detaillees : accessible au meme profil de lecture ; aucun champ sensible brut ne doit etre expose via cette story.
- Les actions operatoires existantes de rollback/publish restent hors de la vue principale et relevent des surfaces existantes ou des stories ulterieures.

## Acceptance Criteria

1. **Given** l'admin accede a `/admin/prompts`  
   **When** la page charge en mode catalogue  
   **Then** la vue principale est une table canonique par `feature`, `subfeature`, `plan`, `locale`, `assembly`, `execution_profile`, `output_contract`, `active_snapshot_id`, `active_snapshot_version`, `manifest_entry_id`  
   **And** la cle nominale unique d'une ligne est `manifest_entry_id`  
   **And** le quadruplet `feature/subfeature/plan/locale` est affiche comme contexte lisible de cette ligne  
   **And** aucune colonne primaire n'utilise `use_case` comme dimension nominale.

2. **Given** qu'un snapshot de release actif couvre une cible canonique  
   **When** la ligne correspondante est affichee  
   **Then** la source de verite visible est `active_snapshot`  
   **And** la ligne expose l'identifiant du snapshot actif, sa version et l'entree de manifest resolue.

3. **Given** qu'aucun snapshot actif ne couvre une cible encore visible a l'admin  
   **When** la ligne est affichee  
   **Then** la source de verite visible est `live_table_fallback` ou un libelle stable equivalent  
   **And** cette lecture de secours est explicitement marquee comme non nominale.

4. **Given** l'admin applique des filtres  
   **When** il filtre par `feature`, `subfeature`, `plan`, `locale`, `provider`, `source_of_truth_status`, `assembly_status`, `release_health_status` ou `catalog_visibility_status`  
   **Then** la table se met a jour sans perdre la lisibilite de la source de verite runtime.

5. **Given** que le terme generique `status` est ambigu pour cette UI  
   **When** la story est implementee  
   **Then** aucun filtre ou badge principal ne s'appelle uniquement `status`  
   **And** les statuts affiches sont explicitement decomposees entre `source_of_truth_status`, `assembly_status`, `release_health_status` et, si necessaire, `catalog_visibility_status`.

6. **Given** qu'une ligne dispose d'un profil d'execution resolu  
   **When** la ligne est affichee  
   **Then** le provider, le modele resolu et la reference de `execution_profile` sont visibles  
   **And** le filtre `provider` s'appuie sur cette valeur resolue, pas sur une colonne UI hardcodee.

7. **Given** que des signaux d'observabilite canoniques sont disponibles pour la cible ou son dernier chemin nominal  
   **When** la ligne est affichee  
   **Then** les champs `execution_path_kind`, `context_compensation_status` et `max_output_tokens_source` sont visibles quand disponibles  
   **And** leur source est priorisee ainsi :
   **And** valeurs deterministes portees par le snapshot ou le manifest si elles existent
   **And** sinon derniere observation qualifiee dans une fenetre de fraicheur documentee cote backend
   **And** hors de cette fenetre, le signal est explicitement marque `stale` ou `n/a`
   **And** leur absence n'est pas silencieuse.

8. **Given** que le perimetre nominal converge est gouverne par snapshot actif  
   **When** une ligne appartient a `chat`, `guidance`, `natal` ou `horoscope_daily`  
   **Then** l'UI ne presente pas `use_case` comme cle nominale de resolution  
   **And** toute information legacy eventuelle reste secondaire, contextuelle et explicitement marquee `compatibility-only`.

9. **Given** qu'une cible canonique possede plusieurs artefacts relies  
   **When** la ligne est affichee  
   **Then** l'admin peut identifier sans ambiguit de quelle assembly, quel execution profile et quel output contract depend l'execution nominale.

10. **Given** qu'un admin consulte la table depuis mobile ou desktop  
   **When** la largeur disponible change  
   **Then** la page reste exploitable via scroll horizontal ou cartes derivees  
   **And** aucun style inline n'est introduit.

11. **Given** la story 65.16 existante centre l'UI sur l'historique prompt par use case  
    **When** 66.45 est implemente  
    **Then** `/admin/prompts` adopte un pattern cible explicite :
    **And** onglet principal `Catalogue canonique`
    **And** panneau secondaire ou sous-vue `Historique legacy prompt/persona`
    **And** aucune page hybride unique ne melange a densite egale catalogue canonique et historique legacy.

12. **Given** que le catalogue peut croitre fortement en volumetrie  
    **When** l'admin consulte la table  
    **Then** le tri serveur et la pagination serveur sont obligatoires  
    **And** un ordre par defaut stable existe (`feature`, `subfeature`, `plan`, `locale`, puis `manifest_entry_id` ou equivalent backend)  
    **And** une recherche serveur par `manifest_entry_id` et par tuple canonique est disponible.

13. **Given** des etats non nominaux existent  
    **When** aucun snapshot actif, aucune ligne resolvable, un manifest entry orphelin, un profil introuvable ou un signal stale est rencontre  
    **Then** l'UI affiche un etat vide ou d'erreur de premier rang avec code ou libelle stable  
    **And** n'essaie pas de degrader silencieusement vers une presentation nominale.

## Tasks / Subtasks

- [x] Task 1: Auditer et recadrer les surfaces admin existantes (AC: 1, 4, 7, 10)
  - [x] Lire [frontend/src/pages/admin/AdminPromptsPage.tsx](/c:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx), [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py), [backend/app/api/v1/routers/admin_llm_assembly.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm_assembly.py) et [backend/app/api/v1/routers/admin_llm_release.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm_release.py)
  - [x] Lister clairement ce qui reste centre `use_case` et ce qui est deja canonique `feature/subfeature/plan/locale`
  - [x] Decider si la page `/admin/prompts` devient une page unique refondue ou un hub a onglets avec `Catalogue canonique` comme vue par defaut

- [x] Task 2: Exposer un endpoint backend de catalogue canonique (AC: 1, 2, 3, 5, 6, 8)
  - [x] Creer un endpoint admin dedie du type `GET /v1/admin/llm/catalog` ou equivalent stable
  - [x] Construire une projection backend joignant snapshot actif, manifest entries, assemblies, execution profiles, output contracts et metadata de source de verite
  - [x] Faire de `manifest_entry_id` la cle unique de `CatalogEntry`
  - [x] Retourner pour chaque ligne au minimum : `manifest_entry_id`, `feature`, `subfeature`, `plan`, `locale`, `assembly_id`, `assembly_status`, `execution_profile_id`, `output_contract_ref`, `active_snapshot_id`, `active_snapshot_version`, `provider`, `source_of_truth_status`, `release_health_status`, `catalog_visibility_status`
  - [x] Exposer explicitement la fraicheur des signaux runtime et la fenetre backend appliquee
  - [x] Ajouter `execution_path_kind`, `context_compensation_status`, `max_output_tokens_source` lorsque ces informations peuvent etre derivees du snapshot actif ou de la derniere observabilite canonique sans heuristique concurrente
  - [x] Imposer pagination serveur, tri serveur et recherche serveur

- [x] Task 3: Refondre la page frontend `/admin/prompts` autour de la table canonique (AC: 1, 4, 5, 6, 7, 9, 10)
  - [x] Remplacer la colonne primaire `use case` par une grille ou table canonique `feature/subfeature/plan/locale`
  - [x] Ajouter les filtres `feature/subfeature/plan/locale/provider/source_of_truth_status/assembly_status/release_health_status/catalog_visibility_status`
  - [x] Afficher un badge stable de source de verite `snapshot actif` vs `fallback live table`
  - [x] Implementer le pattern cible : onglet principal `Catalogue canonique`, onglet secondaire `Historique legacy`
  - [x] Ajouter pagination, tri et recherche visibles cote UI mais executes serveur

- [x] Task 4: Verrouiller les schemas et tests backend/frontend (AC: 2, 3, 4, 5, 6, 8, 10)
  - [x] Ajouter des schemas API admin dedies a la projection du catalogue canonique
  - [x] Ajouter des tests backend sur la priorite `active snapshot > live tables`
  - [x] Ajouter des tests frontend couvrant l'affichage canonique, les filtres et la disparition de `use_case` comme axe primaire

- [x] Task 5: Verification locale obligatoire
  - [x] Si du code Python est modifie, activer le venv avec `.\.venv\Scripts\Activate.ps1`, puis executer `cd backend`, `ruff format .`, `ruff check .`, `pytest -q`
  - [x] Executer aussi les tests frontend cibles lies a `AdminPromptsPage` si la page est modifiee

## Dev Notes

### Diagnostic exact a preserver

- L'UI admin actuelle de `/admin/prompts` est fonctionnelle pour l'ancien modele `prompt history / diff / rollback`, mais elle n'est plus alignee sur la verite runtime du pipeline 66
- Le runtime nominal se gouverne d'abord par snapshot actif, puis par assembly et execution profile ; la vue admin doit donc partir de ces objets
- `use_case` ne doit pas disparaitre completement du codebase : il reste une dimension de compatibilite, de golden fixtures ou de fallback legacy. En revanche, il ne doit plus etre la dimension nominale de la table principale
- Les signaux `execution_path_kind`, `context_compensation_status` et `max_output_tokens_source` sont deja des discriminants canoniques d'observabilite. Il faut les relayer, pas les recalculer arbitrairement dans l'UI
- La source `snapshot actif` vs `fallback live table` doit etre exposee explicitement. Une UI qui masque cette nuance reintroduit de l'ambiguite ops

### Ce que le dev ne doit pas faire

- Ne pas creer un second catalogue admin qui duplique la logique de resolution du runtime
- Ne pas recalculer en frontend la priorite snapshot vs tables live
- Ne pas garder `use_case` comme premiere colonne "par praticite"
- Ne pas introduire de styles inline ; reutiliser les classes CSS admin existantes et les variables de design tokens
- Ne pas casser les usages de rollback/historique deja presents ; il faut les recontextualiser, pas les supprimer aveuglement

### Fichiers a inspecter en priorite

- [frontend/src/pages/admin/AdminPromptsPage.tsx](/c:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx)
- [frontend/src/pages/admin/AdminPromptsPage.css](/c:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css)
- [frontend/src/app/routes.tsx](/c:/dev/horoscope_front/frontend/src/app/routes.tsx)
- [frontend/src/pages/AdminPage.tsx](/c:/dev/horoscope_front/frontend/src/pages/AdminPage.tsx)
- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py)
- [backend/app/api/v1/routers/admin_llm_assembly.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm_assembly.py)
- [backend/app/api/v1/routers/admin_llm_release.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm_release.py)
- [backend/app/llm_orchestration/services/assembly_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_registry.py)
- [backend/app/llm_orchestration/services/execution_profile_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/execution_profile_registry.py)
- [backend/app/llm_orchestration/services/release_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/release_service.py)
- [backend/app/infra/db/models/llm_release.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_release.py)
- [backend/app/infra/db/models/llm_assembly.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_assembly.py)
- [backend/app/infra/db/models/llm_execution_profile.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_execution_profile.py)
- [backend/app/infra/db/models/llm_observability.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_observability.py)

### Previous Story Intelligence

- **65.16** a cree la page `/admin/prompts` autour des prompts par `use_case`, diff et rollback. 66.45 doit reorienter cette page, pas reouvrir un second ecran concurrent
- **66.8** a introduit la gouvernance assembly administrable et le pattern preview/resolution par `feature/subfeature/plan`
- **66.11** a separe `ExecutionProfile` du texte de prompt ; la table admin doit refleter cette separation
- **66.17** a verrouille la responsabilite exclusive des couches ; la table admin doit donc distinguer assembly, persona, output contract et execution profile au lieu de les fusionner sous "prompt"
- **66.32** et **66.44** ont fait du snapshot actif et de `release_health` la verite runtime d'exploitation ; la vue catalogue doit partir de la release active, pas des seules tables publiees

### Testing Requirements

- Ajouter un test backend pour un catalogue avec snapshot actif resolu et presence de `manifest_entry_id`
- Ajouter un test backend pour un cas fallback live table explicitement marque
- Ajouter un test backend de decomposition correcte des statuts (`source_of_truth_status`, `assembly_status`, `release_health_status`)
- Ajouter un test backend de signal `fresh/stale/n/a` avec fenetre de fraicheur documentee
- Ajouter un test frontend prouvant que la colonne primaire `use_case` n'est plus la dimension nominale de la vue
- Ajouter un test frontend des filtres `feature/subfeature/plan/locale/provider/status`
- Ajouter un test frontend du pattern d'onglets `Catalogue canonique` / `Historique legacy`
- Ajouter un test de pagination et tri serveur
- Si la page conserve un panneau secondaire legacy, verifier que les actions diff/rollback restent accessibles

### Project Structure Notes

- Story cross-backend/front/admin uniquement
- Pas de changement de stack ni de nouvelles dependances lourdes
- Reutiliser l'API admin existante quand possible ; si un nouvel endpoint est cree, le garder borne au domaine `admin_llm`
- Introduire si possible un schema partage `CatalogEntry` reutilisable par 66.46 et 66.47

### References

- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [docs/admin-implementation-overview.md](/c:/dev/horoscope_front/docs/admin-implementation-overview.md)
- [backend/app/llm_orchestration/ARCHITECTURE.md](/c:/dev/horoscope_front/backend/app/llm_orchestration/ARCHITECTURE.md)
- [backend/app/api/v1/routers/admin_llm_assembly.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm_assembly.py)
- [backend/app/api/v1/routers/admin_llm_release.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm_release.py)
- [frontend/src/pages/admin/AdminPromptsPage.tsx](/c:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx)
- [65-16-config-prompts-llm.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/65-16-config-prompts-llm.md)
- [66-8-catalogue-administrable-composition-llm.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-8-catalogue-administrable-composition-llm.md)
- [66-11-execution-profiles-administrables.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-11-execution-profiles-administrables.md)
- [66-17-source-verite-canonique-composition.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-17-source-verite-canonique-composition.md)
- [66-32-versionnement-atomique-et-rollback-sur-des-artefacts-de-prompting.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-32-versionnement-atomique-et-rollback-sur-des-artefacts-de-prompting.md)
- [66-44-gate-production-continue-par-snapshot.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-44-gate-production-continue-par-snapshot.md)
- [epic-66-llm-orchestration-contrats-explicites.md](/c:/dev/horoscope_front/_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- 2026-04-15: Ajout endpoint `GET /v1/admin/llm/catalog` avec projection snapshot + fallback live + signaux runtime.
- 2026-04-15: Refonte `/admin/prompts` en onglets `Catalogue canonique` / `Historique legacy` / `Personas`.
- 2026-04-15: Validation locale executee (`ruff check` + `pytest` backend ciblé + `vitest` frontend ciblé).

### Completion Notes List

- Story creee pour requalifier `/admin/prompts` comme lecture canonique du pipeline runtime
- Le coeur du besoin est la projection admin de `snapshot actif > assemblies > execution profiles`, avec `use_case` relaye au rang de compatibilite
- Les stories 66.46 et 66.47 prennent en charge respectivement le detail compose et l'historisation snapshot
- Endpoint backend catalogue canonical expose avec filtres/tri/pagination/recherche et decomposition de statuts explicites.
- UI admin migree vers une table canonique, badges de source de verite et signaux runtime `fresh/stale/n/a`.
- Historique legacy conserve dans un onglet secondaire avec rollback accessible.

### File List

- `_bmad-output/implementation-artifacts/66-45-vue-catalogue-canonique-prompts-actifs.md`
- `backend/app/api/v1/routers/admin_llm.py`
- `backend/tests/integration/test_admin_llm_catalog.py`
- `frontend/src/api/adminPrompts.ts`
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/tests/AdminPromptsPage.test.tsx`

### Change Log

- 2026-04-15: Implémentation complète de la vue catalogue canonique prompts actifs (backend + frontend + tests).
