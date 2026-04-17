# Story 67.2: Exposer la construction logique sous forme de graphe inspectable

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin ops / prompt designer,
I want voir la chaîne logique de composition d'une cible canonique sous forme de graphe,
so that je comprenne immédiatement quelles briques et quelles données alimentent le prompt.

## Acceptance Criteria

1. La vue detail affiche une section `Construction logique` avec un graphe lisible du pipeline.
2. Le graphe relie au minimum `manifest_entry_id`, `composition_sources`, `transformation_pipeline`, `provider_messages` et `runtime inputs`.
3. Les couches `feature template`, `subfeature template`, `plan rules`, `persona block`, `hard policy`, `execution profile` sont identifiables visuellement.
4. Le graphe distingue les données système, fallbacks de registre et sample payloads.
5. Le rendu reste utilisable sur desktop et mobile sans style inline.

## Tasks / Subtasks

- [x] Task 1: Définir la projection de données pour le graphe (AC: 1, 2, 3, 4)
  - [x] Déterminer si le graphe est construit uniquement côté frontend à partir du payload resolved ou si un sous-objet backend dédié est utile.
  - [x] Minimiser la duplication de logique avec l'inspection detail existante.
- [x] Task 2: Implémenter le composant de graphe (AC: 1, 2, 3, 4, 5)
  - [x] Choisir une représentation sobre et maintenable compatible React.
  - [x] Prévoir une légende de lecture.
  - [x] Prévoir un fallback texte si le rendu graphique échoue ou devient trop dense.
- [x] Task 3: Tester lisibilité et résilience (AC: 4, 5)
  - [x] Couvrir les cas avec/sans subfeature, persona, plan rules.
  - [x] Couvrir les cas placeholders uniquement runtime.

### Review Findings

- [x] [Review][Patch] Chaîne de messages sous-modélisée dans le graphe [frontend/src/pages/admin/AdminPromptsPage.tsx:253]
- [x] [Review][Patch] Double comptage possible des catégories runtime/fallback/sample [frontend/src/pages/admin/AdminPromptsPage.tsx:174]
- [x] [Review][Patch] Couverture de tests edge cases incomplète sur la projection [frontend/src/tests/AdminPromptsPage.test.tsx:206]
- [x] [Review][Defer] Résilience limitée si payload `resolved` partiel [frontend/src/pages/admin/AdminPromptsPage.tsx:174] — deferred, pre-existing

## Dev Notes

### Technical Requirements

- Privilégier un graphe léger et déterministe.
- Une représentation Mermaid-like côté UI est acceptable si elle ne nécessite pas d'infrastructure externe fragile.
- Ne pas introduire une nouvelle dépendance lourde si le graphe peut être généré avec le stack existant.

### Architecture Compliance

- Le graphe doit refléter la chaîne réelle documentée dans `llm-prompt-generation-by-feature.md`.
- Il ne doit pas réinventer la structure du pipeline ni montrer un flux théorique divergent du gateway réel.

### File Structure Requirements

- Frontend principal: `frontend/src/pages/admin/AdminPromptsPage.tsx` et éventuellement un composant dédié dans `frontend/src/components` ou `frontend/src/pages/admin`.
- Styles dans un fichier CSS existant ou dédié.
- Tests dans `frontend/src/tests/AdminPromptsPage.test.tsx` ou fichier ciblé associé.

### Testing Requirements

- Vérifier que le graphe reflète correctement:
  - la présence/absence de persona,
  - la présence/absence de plan rules,
  - la provenance des inputs runtime.
- Vérifier qu'un fallback texte ou un état vide lisible existe.

### Previous Story Intelligence

- `66.46` a déjà structuré la vue detail en zones d'inspection.
- `67.1` clarifie la sémantique des modes de preview ; ce graphe doit réutiliser cette sémantique au lieu de l'inventer.

### Project Structure Notes

- Garder la composition visuelle pédagogique et non décorative.
- Aucun style inline; réutiliser les variables et classes admin.

### References

- [docs/llm-prompt-generation-by-feature.md](C:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [66-46-vue-detail-resolved-prompt-assembly.md](C:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-46-vue-detail-resolved-prompt-assembly.md)
- [AdminPromptsPage.tsx](C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Source backlog: `epics-admin-llm-preview-execution.md`
- Implémentation frontend: projection `buildLogicGraphProjection()` dans `frontend/src/pages/admin/AdminPromptsPage.tsx`.
- Validation: `npm run test -- AdminPromptsPage.test.tsx` (vitest) et vérification lints locale (aucune erreur).

### Completion Notes List

- Story file created from BMAD backlog.
- Graphe de construction logique ajouté dans le détail `resolved` avec nœuds/connexions couvrant `manifest_entry_id`, `composition_sources`, `transformation_pipeline`, `provider_messages` et `runtime inputs`.
- Couches métier rendues explicitement dans le graphe: `feature template`, `subfeature template`, `plan rules`, `persona block`, `hard policy`, `execution profile`.
- Distinction visuelle ajoutée via légende et styles dédiés: données système, fallback registre, sample payloads.
- Fallback texte activé automatiquement pour les graphes denses (seuil placeholders) afin de préserver la lisibilité mobile/desktop.
- Tests mis à jour: assertions du graphe inspectable + scénario de fallback dense.

### File List

- `_bmad-output/implementation-artifacts/67-2-exposer-construction-logique-graphe-inspectable.md`
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/tests/AdminPromptsPage.test.tsx`

### Change Log

- 2026-04-17: Implémentation de la story 67.2 (graphe logique inspectable, légende de lecture, fallback texte, tests associés).
