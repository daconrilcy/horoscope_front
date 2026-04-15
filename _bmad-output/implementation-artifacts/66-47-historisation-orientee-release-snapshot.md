# Story 66.47: Historisation orientee release snapshot

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin ops / release manager,
I want consulter l'historique des configurations LLM par snapshot de release et non plus par simple version de prompt,
so that la gouvernance admin suive la vraie unite runtime de changement, d'activation, de rollback et de preuve de readiness.

## Contexte

Les stories 66.32 et 66.44 ont deplace la verite runtime du cote des snapshots de release :

- un snapshot actif fige le manifest des assemblies, execution profiles et output contracts
- l'activation et le rollback se font par bascule de snapshot
- `manifest.release_health` historise les etats de sante de release
- qualification, golden regression et smoke sont corrigees sur le snapshot et sur le `manifest_entry_id`

En parallele, l'admin historique de `/admin/prompts` continue de raconter surtout :

- l'historique des versions de `LlmPromptVersionModel`
- des diffs entre deux textes de prompt
- un rollback cible d'une version de prompt

Cette lecture n'est plus suffisante pour exploiter le pipeline 66 :

- une release peut changer une assembly, un execution profile ou un output contract sans que le diff texte d'un prompt unique suffise a l'expliquer
- le rollback nominal s'opere au niveau snapshot, pas par republishing manuel d'un prompt
- `release_health.status` et sa timeline font partie de la verite ops
- les preuves `qualification`, `golden`, `smoke`, `readiness` doivent etre corrigees a la meme unite de lecture

Le depot contient deja les fondations techniques :

- [backend/app/api/v1/routers/admin_llm_release.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm_release.py) expose create/validate/activate/rollback/evaluate health
- [backend/app/infra/db/models/llm_release.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_release.py) porte les snapshots et la release active
- [backend/app/llm_orchestration/services/release_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/release_service.py) porte `manifest`, `release_health`, activation et rollback
- [backend/tests/integration/test_llm_release.py](/c:/dev/horoscope_front/backend/tests/integration/test_llm_release.py) couvre deja plusieurs cas de release health, smoke et rollback

Le manque restant est une vue admin d'historisation orientee snapshot qui permette de comprendre :

- quelles activations et quels rollbacks ont eu lieu
- quels artefacts ont reellement change entre deux snapshots
- quelle etait la sante de release a chaque etape
- quelles preuves de readiness etaient presentes ou absentes

Cette story ferme ce manque sans reintroduire une lecture `prompt version first`.

## Glossaire UI canonique

- `SnapshotTimelineItem` : evenement affiche dans la timeline admin
- `SnapshotDiffEntry` : projection diff d'une entree de manifest entre deux snapshots
- `ProofSummary` : resume structure d'une preuve corrigee
- `current_status` : statut courant d'un snapshot
- `status_history` : historique append-only de transitions de statut

## Scope et permissions

- Scope de la story : **lecture seule + navigation croisee**. Aucune nouvelle action operatoire de create/validate/activate/rollback n'est requise par 66.47.
- Lecture de la timeline snapshot : accessible aux profils admin autorises a consulter la gouvernance/release LLM.
- Affichage des preuves detaillees : reserve au meme profil de lecture ; toute donnee sensible reste redacted.
- Les actions operatoires restent sur les endpoints et vues existants ; la presente story se concentre sur la lecture historique et l'investigation.

## Acceptance Criteria

1. **Given** l'admin consulte l'historique LLM depuis l'espace admin  
   **When** la page ou l'onglet d'historisation se charge  
   **Then** l'unite principale d'historique est le `release snapshot`  
   **And** non la simple derniere version de prompt ou de persona.

2. **Given** qu'au moins deux snapshots existent  
   **When** l'admin selectionne deux snapshots a comparer  
   **Then** un diff lisible affiche les changements sur `assembly`, `execution profile` et `output contract`  
   **And** ce diff est projete par `manifest_entry_id`  
   **And** chaque `SnapshotDiffEntry` est classe au moins en `added`, `removed`, `changed` ou `unchanged`  
   **And** ce diff ne se limite pas a un diff texte brut de prompt.

3. **Given** qu'un snapshot a ete active puis potentiellement remplace ou rollbacke  
   **When** l'admin consulte la timeline  
   **Then** les evenements affiches suivent une taxonomie UI canonique explicite :
   **And** `created`
   **And** `validated`
   **And** `activated`
   **And** `monitoring`
   **And** `degraded`
   **And** `rollback_recommended`
   **And** `rolled_back`
   **And** tout evenement backend supplementaire est mappe explicitement a cette taxonomie ou a un type documente, jamais via un "ou equivalent stable" implicite.

4. **Given** que `manifest.release_health.status` est disponible  
   **When** la timeline et le detail snapshot sont affiches  
   **Then** le statut de release health est visible  
   **And** l'UI distingue explicitement `current_status` et `status_history`
   **And** `status_history` expose timestamp et cause de transition si disponible.

5. **Given** qu'une qualification, une golden regression, un smoke ou une readiness evidence existent pour un snapshot  
   **When** l'admin consulte le detail de ce snapshot  
   **Then** ces preuves sont visibles via un resume structure :
   **And** `qualification_status`
   **And** `golden_status`
   **And** `smoke_status`
   **And** `readiness_status`
   **And** chaque preuve expose son verdict, sa date et son `manifest_entry_id` si pertinent.

6. **Given** qu'une preuve attendue est absente  
   **When** le snapshot est consulte  
   **Then** l'absence est visible explicitement  
   **And** n'est pas interpretee comme une preuve implicite de succes.

7. **Given** qu'une preuve est affichee comme valide dans l'UI  
   **When** l'admin consulte le detail du snapshot  
   **Then** cette preuve est marquee valide seulement si elle est corrigee au `snapshot_id`  
   **And** au `manifest_entry_id` quand cette dimension est requise  
   **And** une preuve fraiche mais non corrigee est visible comme `uncorrelated` ou equivalent stable, pas comme `valid`.

8. **Given** qu'un rollback a eu lieu  
   **When** l'admin consulte le diff entre le snapshot rollbacke et le snapshot restaure  
   **Then** il peut identifier quel snapshot a ete quitte, lequel a ete restaure et quels artefacts nominalement gouvernes differaient.

9. **Given** que l'historique doit servir l'ops et pas seulement la lecture technique  
   **When** la page est affichee  
   **Then** les colonnes, badges et filtres privilegient les dimensions `snapshot version`, `current_status`, `activated_at`, `release_health_status`, `manifest_entry_count`, `qualification_status`, `golden_status`, `smoke_status`, `readiness_status`
   **And** aucun filtre generique `proofs` n'est utilise seul sans decomposition.

10. **Given** la cohabitation avec les stories 66.45 et 66.46  
   **When** l'admin navigue depuis le catalogue ou le detail assembly  
   **Then** il peut ouvrir la timeline snapshot ou le diff entre snapshots sans changer de langage mental.

11. **Given** qu'un admin consulte la timeline ou un diff snapshot  
    **When** il souhaite investiguer une entree impactee  
    **Then** il peut naviguer du snapshot ou du diff vers :
    **And** la ligne concernee du catalogue 66.45
    **And** le detail `ResolvedAssemblyView` 66.46 de l'entree `manifest_entry_id`.

12. **Given** qu'une action admin de rollback snapshot est deja supportee backend  
    **When** la vue d'historisation affiche les evenements  
    **Then** elle montre le rollback comme transition de snapshot gouvernee  
    **And** non comme un simple rollback de prompt isole.

13. **Given** des cas non nominaux existent  
    **When** aucun snapshot n'est disponible, qu'un diff est impossible, qu'une preuve est absente, qu'une manifest entry est orpheline ou qu'une correlation est invalide  
    **Then** l'UI expose un etat vide ou erreur de premier rang avec libelle stable  
    **And** ne remplace pas silencieusement ce cas par une lecture simplifiee.

## Tasks / Subtasks

- [ ] Task 1: Auditer la surface release existante et definir la projection historique cible (AC: 1, 3, 4, 5, 6, 8, 10)
  - [ ] Lire [backend/app/api/v1/routers/admin_llm_release.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm_release.py), [backend/app/llm_orchestration/services/release_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/release_service.py) et [backend/app/infra/db/models/llm_release.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_release.py)
  - [ ] Definir le schema d'une vue historique orientee snapshot incluant metadata, release health et preuves corrigees
  - [ ] Decider si la vue vit dans `/admin/prompts`, `/admin/llm/releases` ou comme onglet de gouvernance LLM partage

- [ ] Task 2: Exposer une API admin de timeline et de diff snapshot (AC: 1, 2, 3, 4, 5, 6, 7, 8, 10)
  - [ ] Ajouter un endpoint liste/timeline des snapshots avec `status`, `created_at`, `activated_at`, `release_health.status`, compte d'entrees de manifest et resume des preuves
  - [ ] Ajouter un endpoint de diff entre deux snapshots restituant les changements sur assemblies, execution profiles et output contracts
  - [ ] Projeter chaque diff par `manifest_entry_id` avec categorie `added/removed/changed/unchanged`
  - [ ] Rendre visible le lien `from_snapshot_id` -> `to_snapshot_id` pour les activations et rollbacks
  - [ ] Exposer des objets API partages : `SnapshotTimelineItem`, `SnapshotDiffEntry`, `ProofSummary`

- [ ] Task 3: Construire la vue frontend de timeline snapshot (AC: 1, 3, 4, 5, 6, 8, 9, 10)
  - [ ] Ajouter un ecran ou onglet de timeline des snapshots avec filtres de statut et recherche par version
  - [ ] Afficher la chronologie des activations, degrades et rollbacks
  - [ ] Afficher distinctement `current_status` et `status_history`
  - [ ] Afficher dans un panneau detail les preuves qualification/golden/smoke/readiness
  - [ ] Permettre la navigation retour vers 66.45 et 66.46

- [ ] Task 4: Construire le diff de snapshots (AC: 2, 7, 9)
  - [ ] Permettre la selection de deux snapshots
  - [ ] Afficher les changements d'assembly, d'execution profile et d'output contract par `manifest_entry_id`
  - [ ] Garder les diffs textuels de prompt comme vue secondaire optionnelle, jamais comme axe principal

- [ ] Task 5: Tester la gouvernance historique (AC: 2, 3, 4, 5, 6, 7, 10)
  - [ ] Ajouter des tests backend sur la timeline des snapshots et le diff d'artefacts
  - [ ] Ajouter des tests frontend sur l'affichage de `release_health.status` et des preuves
  - [ ] Ajouter un test couvrant un rollback visible en timeline

- [ ] Task 6: Verification locale obligatoire
  - [ ] Si du code Python est modifie, activer le venv avec `.\.venv\Scripts\Activate.ps1`, puis executer `cd backend`, `ruff format .`, `ruff check .`, `pytest -q`
  - [ ] Executer aussi les tests frontend cibles lies a la timeline release si le frontend est modifie

## Dev Notes

### Diagnostic exact a preserver

- L'historique par version de prompt n'est plus la bonne unite d'exploitation du pipeline nominal
- La verite runtime d'un changement de comportement passe par snapshot + manifest entries + release health
- Le diff attendu doit d'abord porter sur les artefacts gouvernes : assembly, execution profile, output contract
- Les preuves `qualification`, `golden`, `smoke` et `readiness` ne sont pas decoratives ; elles doivent etre visibles comme parties constitutives de la lecture ops du snapshot
- Une timeline utile doit raconter l'activation et le rollback de releases, pas seulement l'edition de contenu

### Ce que le dev ne doit pas faire

- Ne pas construire une "timeline des prompts" rebaptisee snapshot
- Ne pas reduire le diff snapshot a un diff de champs JSON illisible sans projection par artefact
- Ne pas cacher l'absence de preuves derriere des badges implicites
- Ne pas dupliquer la logique de `ReleaseService` dans le frontend
- Ne pas oublier les liens de navigation depuis 66.45 et 66.46

### Fichiers a inspecter en priorite

- [backend/app/api/v1/routers/admin_llm_release.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm_release.py)
- [backend/app/infra/db/models/llm_release.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_release.py)
- [backend/app/llm_orchestration/services/release_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/release_service.py)
- [backend/tests/integration/test_llm_release.py](/c:/dev/horoscope_front/backend/tests/integration/test_llm_release.py)
- [frontend/src/pages/admin/AdminPromptsPage.tsx](/c:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx)
- [frontend/src/pages/AdminPage.tsx](/c:/dev/horoscope_front/frontend/src/pages/AdminPage.tsx)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [docs/llm-prod-release-step-by-step.md](/c:/dev/horoscope_front/docs/llm-prod-release-step-by-step.md)
- [docs/llm-release-runbook.md](/c:/dev/horoscope_front/docs/llm-release-runbook.md)
- [docs/llm-go-no-go-formal.md](/c:/dev/horoscope_front/docs/llm-go-no-go-formal.md)

### Previous Story Intelligence

- **65.16** a ancre historiquement `/admin/prompts` sur les versions de prompt. 66.47 doit depasser cette lecture sans perdre la tracabilite utile
- **66.32** a introduit le snapshot actif, l'activation atomique et le rollback par snapshot
- **66.44** a ajoute `release_health` et la gouvernance continue qualification/golden/smoke/rollback
- **66.45** fournit la vue catalogue canonique ; **66.46** fournit le detail assembly resolu. 66.47 ferme la boucle temporelle en montrant comment ces artefacts ont evolue par release

### Testing Requirements

- Ajouter un test backend de liste/timeline de snapshots avec `release_health.status`
- Ajouter un test backend de diff entre deux snapshots sur les artefacts gouvernes
- Ajouter un test backend couvrant l'affichage/correlation de `manifest_entry_id` et des preuves
- Ajouter un test backend du mapping canonique des evenements timeline backend -> UI
- Ajouter un test backend de preuve `uncorrelated` non consideree comme valide
- Ajouter un test frontend d'affichage des badges `release_health` et d'une timeline contenant activation puis rollback
- Ajouter un test frontend de navigation snapshot -> catalogue -> detail assembly

### Project Structure Notes

- Story backend + frontend admin + documentation de gouvernance/release si necessaire
- Reutiliser les modeles et services de release existants ; la story vise une projection admin, pas un nouveau moteur de release
- Aucun style inline ; reutiliser les tokens et patterns CSS admin
- Introduire si possible des schemas partages `SnapshotTimelineItem`, `SnapshotDiffEntry`, `ProofSummary`

### References

- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [docs/llm-prod-release-step-by-step.md](/c:/dev/horoscope_front/docs/llm-prod-release-step-by-step.md)
- [docs/llm-release-runbook.md](/c:/dev/horoscope_front/docs/llm-release-runbook.md)
- [docs/llm-go-no-go-formal.md](/c:/dev/horoscope_front/docs/llm-go-no-go-formal.md)
- [backend/app/api/v1/routers/admin_llm_release.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm_release.py)
- [backend/app/infra/db/models/llm_release.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_release.py)
- [backend/app/llm_orchestration/services/release_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/release_service.py)
- [backend/tests/integration/test_llm_release.py](/c:/dev/horoscope_front/backend/tests/integration/test_llm_release.py)
- [66-32-versionnement-atomique-et-rollback-sur-des-artefacts-de-prompting.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-32-versionnement-atomique-et-rollback-sur-des-artefacts-de-prompting.md)
- [66-44-gate-production-continue-par-snapshot.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-44-gate-production-continue-par-snapshot.md)
- [66-45-vue-catalogue-canonique-prompts-actifs.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-45-vue-catalogue-canonique-prompts-actifs.md)
- [66-46-vue-detail-resolved-prompt-assembly.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-46-vue-detail-resolved-prompt-assembly.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- Story creee pour faire porter l'historisation admin sur la bonne unite runtime : le release snapshot
- La vue cible privilegie timeline, release health, preuves corrigees et diff d'artefacts gouvernes
- Elle complete le bloc 1 de realignement admin sur la verite runtime du pipeline canonique

### File List

- `_bmad-output/implementation-artifacts/66-47-historisation-orientee-release-snapshot.md`
