# Story 57.1: Tests Button, Field, Select — composants de saisie

Status: done

## Story

En tant que développeur frontend,
je veux des tests unitaires complets pour `Button`, `Field` et `Select`,
afin de détecter les régressions sur ces composants de saisie fondamentaux lors des refactorisations.

## Acceptance Criteria

1. `Button.test.tsx` couvre : rendu de tous les variants (`primary`, `secondary`, `ghost`, `danger`), toutes les tailles, état disabled, état loading, click handler.
2. `Field.test.tsx` couvre : rendu des types (`text`, `email`, `password`), label associé, état error, état disabled, valeur contrôlée.
3. `Select.test.tsx` couvre : rendu des options, sélection d'une option, état disabled, placeholder.
4. Tous les tests passent avec `npm run test`.
5. Les tests utilisent `@testing-library/react` et `vitest` — pas d'autres frameworks.

## Tasks / Subtasks

- [x] Tâche 1 : Lire les composants à tester (AC: 1, 2, 3)
  - [x] Lecture de `Button.tsx`, `Field.tsx`, `Select.tsx`.
  - [x] Vérification de la configuration Vitest.

- [x] Tâche 2 : Écrire `Button.test.tsx` (AC: 1)
  - [x] Couverture des variants, tailles, et états (disabled, loading).
  - [x] Vérification des handlers de click.

- [x] Tâche 3 : Écrire `Field.test.tsx` (AC: 2)
  - [x] Vérification de l'accessibilité (label/input pairing).
  - [x] Test du toggle de visibilité du mot de passe.
  - [x] Gestion des erreurs et des hints.

- [x] Tâche 4 : Écrire `Select.test.tsx` (AC: 3)
  - [x] Test du filtrage par recherche.
  - [x] Navigation au clavier (ArrowDown, Enter, Escape).
  - [x] Support des groupes d'options.

- [x] Tâche 5 : Validation (AC: 4)
  - [x] `npm run test` — 30 tests spécifiques réussis pour ces 3 composants.

## Dev Notes

### Qualité des tests UI

Les tests implémentés suivent scrupuleusement les recommandations de Testing Library en privilégiant les sélections par rôles (`getByRole`) et labels (`getByLabelText`), ce qui garantit non seulement la robustesse du code mais aussi l'accessibilité des composants.

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List
- Validation des tests unitaires pour `Button` (16 tests).
- Validation des tests unitaires pour `Field` (7 tests).
- Validation des tests unitaires pour `Select` (7 tests).
- Tous les critères d'acceptation sont couverts par les fichiers existants.

### File List
- `frontend/src/components/ui/Button/Button.test.tsx`
- `frontend/src/components/ui/Field/Field.test.tsx`
- `frontend/src/components/ui/Select/Select.test.tsx`
