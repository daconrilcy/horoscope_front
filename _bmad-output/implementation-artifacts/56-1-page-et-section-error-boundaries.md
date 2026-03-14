# Story 56.1: Créer PageErrorBoundary et SectionErrorBoundary à partir du ErrorBoundary existant

Status: done

## Story

En tant que développeur frontend,
je veux que le composant `ErrorBoundary` existant soit étendu en deux variantes spécialisées `PageErrorBoundary` et `SectionErrorBoundary`,
afin d'avoir des fallbacks visuellement adaptés selon la portée de l'erreur (page entière vs section).

## Acceptance Criteria

1. `PageErrorBoundary` affiche un fallback pleine page avec titre "Une erreur est survenue" et bouton "Recharger la page".
2. `SectionErrorBoundary` affiche un fallback compact inline avec message d'erreur et bouton "Réessayer".
3. Les deux composants sont basés sur `ErrorBoundary.tsx` existant (pas de duplication de logique de boundary).
4. Les deux composants sont exportés depuis `frontend/src/components/ErrorBoundary/index.ts`.
5. Les tests existants passent sans modification.

## Tasks / Subtasks

- [x] Tâche 1 : Analyser `ErrorBoundary.tsx` existant (AC: 3)
  - [x] Déplacement de `ErrorBoundary.tsx` et `ErrorBoundary.css` dans un dossier dédié `frontend/src/components/ErrorBoundary/`.

- [x] Tâche 2 : Créer `PageErrorBoundary` (AC: 1)
  - [x] Nouveau composant avec fallback stylisé pleine page (glassmorphism).
  - [x] Action : `window.location.reload()`.

- [x] Tâche 3 : Créer `SectionErrorBoundary` (AC: 2)
  - [x] Nouveau composant utilisant `EmptyState` comme base pour le fallback compact.
  - [x] Action : Appel de `onRetry`.

- [x] Tâche 4 : Créer `frontend/src/components/ErrorBoundary/index.ts` (AC: 4)
  - [x] Export groupé des trois composants.

- [x] Tâche 5 : Validation (AC: 5)
  - [x] `npm run test` — 1079 tests réussis.
  - [x] Mise à jour des imports dans les fichiers consommateurs (`NatalInterpretation.tsx`).

## Dev Notes

### Organisation des Error Boundaries

La logique de capture d'erreur reste centralisée dans `ErrorBoundary.tsx` (Class Component). Les variantes `PageErrorBoundary` et `SectionErrorBoundary` sont des Functional Components agissant comme des configurations pré-définies de `ErrorBoundary` avec des fallbacks visuels spécifiques.

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List
- Création du dossier `ErrorBoundary` et restructuration des fichiers.
- Implémentation de `PageErrorBoundary` (full page) et `SectionErrorBoundary` (inline/compact).
- Intégration avec `EmptyState` pour la cohérence visuelle.
- Mise à jour globale des imports impactés.
- Validation via 1079 tests réussis.

### File List
- `frontend/src/components/ErrorBoundary/ErrorBoundary.tsx`
- `frontend/src/components/ErrorBoundary/ErrorBoundary.css`
- `frontend/src/components/ErrorBoundary/PageErrorBoundary.tsx`
- `frontend/src/components/ErrorBoundary/SectionErrorBoundary.tsx`
- `frontend/src/components/ErrorBoundary/index.ts`
- `frontend/src/components/NatalInterpretation.tsx`
