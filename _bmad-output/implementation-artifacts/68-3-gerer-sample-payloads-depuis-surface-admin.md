# Story 68.3: Permettre la gestion admin des sample payloads depuis la surface de contrôle

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin platform operator,
I want créer, modifier, dupliquer et supprimer des sample payloads depuis l'interface admin,
so that la preview runtime soit maintenable sans passage par la base ou des fixtures cachées.

## Acceptance Criteria

1. L'admin peut créer un sample payload depuis l'UI avec validation guidée.
2. L'admin peut modifier et dupliquer un sample payload existant.
3. L'admin peut désactiver ou supprimer un sample payload obsolète.
4. La sélection des samples reste simple et ciblée par feature/locale.

## Tasks / Subtasks

- [x] Task 1: Exposer le CRUD admin des sample payloads (AC: 1, 2, 3)
  - [x] Créer les endpoints et schémas nécessaires.
  - [x] Encadrer permissions et validation.
- [x] Task 2: Intégrer les écrans/formulaires admin (AC: 1, 2, 3, 4)
  - [x] Ajouter la liste, le détail, la duplication et la suppression.
  - [x] Rendre la navigation compatible avec la zone `Données d'exemple`.
- [x] Task 3: Tester UX et auditabilité (AC: 3, 4)
  - [x] Vérifier les listes filtrées.
  - [x] Vérifier le comportement des samples par défaut ou recommandés.

### Review Findings

- [x] [Review][Decision] Duplication / changement de cible : choix produit **autoriser** le changement de feature dans les filtres et **réinitialiser les champs payload** (chart/JSON) quand la feature change pendant qu’une modale est ouverte — implémenté (`defaultPayloadFields`, ref `payloadBaselineFeatureRef`, texte d’aide modale). Le POST continue d’utiliser `mgmtFeature` / `mgmtLocale` ; le formulaire reste cohérent après changement de cible.

- [x] [Review][Patch] Renforcer les garde-fous hors domaine `natal` [frontend/src/pages/admin/AdminSamplePayloadsAdmin.tsx] — Exemples JSON par feature (`SUGGESTED_GENERIC_PAYLOAD_BY_FEATURE`), texte d’aide structuré, bouton « Insérer l’exemple suggéré », styles `AdminSamplePayloadsAdmin.css`.

- [x] [Review][Patch] Isoler les messages d’erreur par contexte (liste vs modale édition vs modale suppression) [frontend/src/pages/admin/AdminSamplePayloadsAdmin.tsx] — États `listActionError`, `editorError`, `deleteError` avec affichage conditionnel (liste masquée si modale ouverte / suppression).

- [x] [Review][Defer] Double chargement catalogue sur l’onglet « Échantillons runtime » (requête facettes déjà couverte par le catalogue prompts + requête dans `AdminSamplePayloadsAdmin`) [frontend/src/pages/admin/AdminSamplePayloadsAdmin.tsx] — deferred, optimisation réseau / perf ultérieure.

## Dev Notes

### Technical Requirements

- Garder un formulaire guidé et borné.
- Éviter un éditeur JSON totalement libre sans garde-fous minimaux.
- La duplication doit être préférée à l'écrasement direct des payloads de référence.

### Architecture Compliance

- Rester dans le domaine admin existant.
- Ne pas créer une surface indépendante qui contourne le catalogue canonique et la vue detail.

### File Structure Requirements

- Backend admin LLM.
- Frontend admin prompts.
- Tests backend + frontend.

### Testing Requirements

- CRUD happy path.
- Validation refus des payloads invalides.
- Filtrage feature/locale.
- Non-régression sur la runtime preview.
- E2E Playwright : flux « Données d’exemple → onglet Échantillons runtime » avec mocks réseau (`e2e/admin-prompts-sample-payload-cta.spec.ts`).

### Previous Story Intelligence

- `68.1` et `68.2` posent déjà le contrat et la consommation des sample payloads.
- Cette story ajoute la maintenabilité opérateur autour de ces objets.

### Project Structure Notes

- Respecter les patterns de formulaires React existants du repo.

### References

- [epics-admin-llm-preview-execution.md](C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics-admin-llm-preview-execution.md)
- [AdminPromptsPage.tsx](C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx)

## Dev Agent Record

### Agent Model Used

Auto (Cursor agent)

### Implementation Plan

- Réutiliser le CRUD backend existant, compléter les tests manquants sur `include_inactive`.
- Étendre `adminPrompts.ts` et brancher un panneau admin dédié sous l’onglet prompts LLM.
- Formulaire guidé natal + repli JSON complet pour contournement des réponses masquées.

### Debug Log References

- Source backlog: `epics-admin-llm-preview-execution.md`

### Completion Notes List

- Story file created from BMAD backlog.
- CRUD HTTP déjà présent côté backend (`admin_llm_sample_payloads.py`) : validation, admin obligatoire, audit. Ajout d’un test d’intégration `include_inactive` pour l’auditabilité des payloads désactivés.
- Front : onglet « Échantillons runtime » + composant `AdminSamplePayloadsAdmin` (liste filtrée feature/locale, case « Afficher les inactifs », création/édition avec formulaire guidé natal `chart_json` + extras JSON, mode JSON complet si `chart_json` non objet côté API, duplication via relecture + création, désactivation rapide, suppression confirmée). Lien depuis la zone « Données d’exemple » du détail catalogue vers l’onglet avec préremplissage feature/locale.
- API client : `listAdminLlmSamplePayloads` supporte `include_inactive`, fonctions get/create/update/delete + mutations React Query et invalidation des previews résolues.
- Seed catalogue → onglet samples : le seed parent n’est plus consommé immédiatement par l’enfant (évite perte du couple feature/locale sous React Strict Mode) ; réinitialisation du seed à la sortie de l’onglet « Échantillons runtime ». Garde-fou effets d’auto-sélection feature/locale quand un seed explicite est fourni (évite la course avec la première locale alphabétique, ex. `en-US`).
- Test E2E Playwright : navigation depuis le bouton sous « Données d’exemple », onglet actif, région de gestion visible, selects `chat` / `fr-FR`.

### File List

- `_bmad-output/implementation-artifacts/68-3-gerer-sample-payloads-depuis-surface-admin.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/planning-artifacts/epics-admin-llm-preview-execution.md`
- `backend/tests/integration/test_admin_llm_sample_payloads.py`
- `frontend/e2e/admin-prompts-sample-payload-cta.spec.ts`
- `frontend/src/api/adminPrompts.ts`
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/pages/admin/AdminSamplePayloadsAdmin.tsx`
- `frontend/src/pages/admin/AdminSamplePayloadsAdmin.css`
- `frontend/src/tests/AdminSamplePayloadsAdmin.test.tsx`

### Change Log

- 2026-04-17 : Implémentation gestion admin sample payloads (UI + tests + liste inactifs).
- 2026-04-17 : E2E Playwright flux Données d’exemple → Échantillons runtime ; correctifs seed / auto-sélection locale sous Strict Mode ; docs artefacts epic 68.3.
- 2026-04-17 : Revue code — décision « réinitialiser le payload si la feature (filtre) change » appliquée dans `AdminSamplePayloadsAdmin.tsx`.
- 2026-04-17 : Code review (2ᵉ passe, périmètre `origin/main...HEAD` story 68-3) — pas de nouveau finding bloquant ; les 2 `[Review][Patch]` ouverts restent pertinents ; suggestion mineure hors scope : envisager le même reset si seule la **locale** filtre change pendant l’édition.
- 2026-04-17 : Fermeture des 2 `[Review][Patch]` — erreurs isolées + garde-fous payload hors `natal` (exemples + aide + insertion) ; test Vitest associé.
