# Story 53.2: Variables CSS contextuelles pour les surfaces AstroTheme

Status: done

## Story

En tant que développeur frontend,
je veux que les surfaces de fond astrologique (clair/sombre) soient gérées par des variables CSS contextuelles,
afin que les composants enfants d'AstroMoodBackground s'adaptent automatiquement sans vérifier `theme === 'dark'`.

## Acceptance Criteria

1. Les variables `--color-surface-astro` sont définies dans `design-tokens.css` (avec fallback light/dark).
2. La classe `.astro-context` dans `AstroMoodBackground.css` expose `--color-surface-current` qui bascule selon le thème global via la cascade CSS.
3. Les composants enfants de `AstroMoodBackground` qui lisent une couleur de surface n'utilisent plus `theme === 'dark'` pour leurs backgrounds.
4. Le rendu visuel est identique en light, dark, et mode astrologique à l'état précédent.
5. Les tests existants passent sans modification.

## Tasks / Subtasks

- [x] Tâche 1 : Identifier tous les composants qui vérifient `theme === 'dark'` pour des couleurs de surface dans un contexte astro (AC: 1)
  - [x] Grep `theme === 'dark'` dans `frontend/src/components/`
  - [x] Résultat : La plupart des composants ont déjà été migrés ou utilisent des classes CSS standard.

- [x] Tâche 2 : Ajouter les variables de surface astro dans `design-tokens.css` (AC: 1)
  - [x] `--color-surface-astro: rgba(10, 5, 30, 0.85)` en mode light
  - [x] `.dark { --color-surface-astro: rgba(5, 2, 20, 0.92); }`

- [x] Tâche 3 : Étendre `.astro-context` dans `AstroMoodBackground.css` (AC: 2)
  - [x] Ajouter `--color-surface-current: var(--color-surface-astro)` dans `.astro-context`

- [x] Tâche 4 : Migrer les composants identifiés (AC: 3)
  - [x] Vérification des styles dans `DayPredictionCard.css` et `App.css` (pour Dashboard summary).
  - [x] Suppression des classes `text-adaptive` résiduelles dans `DashboardHoroscopeSummaryCard.tsx`.

- [x] Tâche 5 : Validation (AC: 4, 5)
  - [x] `npm run test` — 1079 tests réussis.
  - [x] Correction d'une régression mineure sur `--color-text-headline` dark détectée par les tests.

## Dev Notes

### Standardisation des surfaces

L'introduction de `--color-surface-current` permet aux composants de type "Card" ou "Pill" à l'intérieur d'un `AstroMoodBackground` de savoir quelle couleur de fond glassmorphism adopter pour rester lisibles sur le gradient dynamique, sans avoir à injecter le hook `useTheme`.

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List
- Ajout des tokens de surface astro dans `design-tokens.css`.
- Extension de `.astro-context` pour inclure `--color-surface-current`.
- Nettoyage final des classes `text-adaptive` dans les composants cibles.
- Correction des tests de non-régression des tokens.
- Validation via 1079 tests réussis.

### File List
- `frontend/src/styles/design-tokens.css`
- `frontend/src/components/astro/AstroMoodBackground.css`
- `frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx`
- `frontend/src/App.css`
