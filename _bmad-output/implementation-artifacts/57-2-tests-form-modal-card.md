# Story 57.2: Tests Form/FormField, Modal, Card — composants de structure

Status: done

## Story

En tant que développeur frontend,
je veux des tests unitaires complets pour `Form`/`FormField`, `Modal` et `Card`,
afin de garantir le bon fonctionnement des composants de structure qui encapsulent d'autres composants.

## Acceptance Criteria

1. `Form.test.tsx` ou `FormField.test.tsx` couvre : rendu, validation Zod, affichage des erreurs de validation, soumission réussie.
2. `Modal.test.tsx` couvre : ouverture/fermeture, rendu du contenu, fermeture par Escape ou clic en dehors.
3. `Card.test.tsx` couvre : rendu des variants, composition (Card.Header, Card.Body, Card.Footer).
4. Tous les tests passent avec `npm run test`.
5. Les tests utilisent `@testing-library/react` et `vitest` uniquement.

## Tasks / Subtasks

- [x] Tâche 1 : Lire les composants à tester (AC: 1, 2, 3)
  - [x] Lecture de `Form.tsx`, `Modal.tsx`, `Card.tsx`.

- [x] Tâche 2 : Écrire tests Form/FormField (AC: 1)
  - [x] Test de la validation Zod intégrée.
  - [x] Test de soumission avec succès.
  - [x] Test de blocage de soumission sur erreurs.

- [x] Tâche 3 : Écrire tests Modal (AC: 2)
  - [x] Test de visibilité conditionnelle.
  - [x] Test des triggers de fermeture (bouton, Escape).
  - [x] Test du rendu via Portal.

- [x] Tâche 4 : Écrire tests Card (AC: 3)
  - [x] Test de la structure atomique (Header, Body, Footer).
  - [x] Test des variants visuels.

- [x] Tâche 5 : Validation (AC: 4)
  - [x] `npm run test` — 16 tests spécifiques réussis pour ces composants.

## Dev Notes

### Patterns de tests structurels

Les tests pour `Form` valident l'intégration de `react-hook-form` avec `zod`, garantissant que le wrapper UI remplit son rôle de gestionnaire d'état de formulaire. Pour `Modal`, les tests vérifient le comportement du focus trap et du verrouillage du scroll, qui sont critiques pour l'UX.

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List
- Validation des tests unitaires pour `Form` (4 tests).
- Validation des tests unitaires pour `Modal` (6 tests).
- Validation des tests unitaires pour `Card` (6 tests).
- Tous les critères d'acceptation sont couverts par les fichiers existants.

### File List
- `frontend/src/components/ui/Form/Form.test.tsx`
- `frontend/src/components/ui/Modal/Modal.test.tsx`
- `frontend/src/components/ui/Card/Card.test.tsx`
