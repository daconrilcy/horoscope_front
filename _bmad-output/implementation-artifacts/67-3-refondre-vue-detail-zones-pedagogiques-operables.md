# Story 67.3: Refondre la vue detail en zones pédagogiques et opérables

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin ops / release operator,
I want une vue detail structurée en zones distinctes et lisibles,
so that je puisse comprendre rapidement le prompt sans parser un JSON brut.

## Acceptance Criteria

1. La vue detail est organisée au minimum en `Construction logique`, `Prompts`, `Données d'exemple`, `Retour LLM`.
2. La zone `Prompts` sépare `assembled prompt`, `post injectors prompt`, `rendered prompt`, `system hard policy`, `developer content`, `persona block`.
3. La zone placeholders affiche nom, statut, source de résolution, classification et niveau de redaction.
4. Les états vide, erreur et preview partielle ont des messages de premier rang compréhensibles.

## Tasks / Subtasks

- [x] Task 1: Recomposer la hiérarchie de la page admin detail (AC: 1, 2, 4)
  - [x] Définir l'ordre visuel et la navigation entre zones.
  - [x] Préparer les sections futures `Données d'exemple` et `Retour LLM` sans dépendance bloquante.
- [x] Task 2: Rationaliser l'affichage des blocs de prompt (AC: 2, 3)
  - [x] Uniformiser les titres et sous-titres.
  - [x] Rendre les placeholders compréhensibles sans lecture JSON brute.
- [x] Task 3: Ajouter les tests d'affichage et de structure (AC: 1, 2, 3, 4)
  - [x] Tester les sections obligatoires.
  - [x] Tester les états vides/erreurs/preview partielle.

### Review Findings

- [x] [Review][Patch] Le message d'erreur reste formulé comme une prévisualisation même en mode `live_execution` [frontend/src/pages/admin/AdminPromptsPage.tsx:854]
- [x] [Review][Patch] Une valeur d'aperçu vide mais autorisée est affichée comme `redacted` au lieu de sa vraie valeur [frontend/src/pages/admin/AdminPromptsPage.tsx:817]

## Dev Notes

### Technical Requirements

- Cette story est surtout frontend, mais peut nécessiter de légers ajustements de schéma API si certaines métadonnées manquent.
- Garder la séparation claire entre inspection du pipeline et futures actions runtime/exécution.

### Architecture Compliance

- Réutiliser la vue detail resolved livrée en 66.46 comme base.
- Préparer les emplacements pour les stories 68.x et 69.x sans créer de dépendance sur des endpoints encore absents.

### File Structure Requirements

- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- éventuellement un composant d'aide ou de section dédié si cela améliore la lisibilité.

### Testing Requirements

- Vérifier que les 4 zones existent dans le rendu.
- Vérifier que la zone `Retour LLM` peut exister vide tant que l'exécution n'est pas disponible.
- Vérifier l'absence de régression sur le contenu déjà livré en 66.46.

### Previous Story Intelligence

- `67.1` fixe la sémantique de preview.
- `67.2` ajoute la visualisation logique.
- Cette story doit les intégrer dans une composition opérable unique.

### Project Structure Notes

- Pas de style inline.
- Préserver la cohérence visuelle de l'admin existant.

### References

- [66-46-vue-detail-resolved-prompt-assembly.md](C:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-46-vue-detail-resolved-prompt-assembly.md)
- [AdminPromptsPage.tsx](C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx)
- [AdminPromptsPage.css](C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Source backlog: `epics-admin-llm-preview-execution.md`

### Completion Notes List

- Story file created from BMAD backlog.
- Vue détail restructurée en zones pédagogiques opérables avec séparation explicite des blocs prompts et placeholders lisibles.
- États de premier rang ajoutés pour preview partielle, erreur de rendu et zone Retour LLM vide en attente des stories 69.x.
- Tests Vitest renforcés sur structure des zones et états UX (vide/erreur/preview partielle), sans régression des scénarios existants.

### File List

- `_bmad-output/implementation-artifacts/67-3-refondre-vue-detail-zones-pedagogiques-operables.md`
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/tests/AdminPromptsPage.test.tsx`

## Change Log

- 2026-04-17: Implémentation complète de la story 67.3 (refonte vue détail, placeholders pédagogiques, états UX, tests et lint verts).
