# Story 57.1: Tests Button, Field, Select — composants de saisie

Status: ready-for-dev

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

- [ ] Tâche 1 : Lire les composants à tester (AC: 1, 2, 3)
  - [ ] Lire `frontend/src/components/ui/Button/Button.tsx`
  - [ ] Lire `frontend/src/components/ui/Field/Field.tsx`
  - [ ] Lire `frontend/src/components/ui/Select/Select.tsx`
  - [ ] Lire `frontend/vitest.config.ts` pour comprendre la config de test
  - [ ] Lire un test existant pour copier le pattern (ex: `frontend/src/tests/`)

- [ ] Tâche 2 : Écrire `Button.test.tsx` (AC: 1)
  - [ ] Trouver ou créer `frontend/src/components/ui/Button/Button.test.tsx`
  - [ ] Test : rendu par défaut sans crash
  - [ ] Test : chaque variant a la bonne classe CSS
  - [ ] Test : click sur button déclenche le handler
  - [ ] Test : button disabled ne déclenche pas le handler
  - [ ] Test : button loading affiche l'état de chargement
  - [ ] Test : snapshot ou assertion sur le rendu de base

- [ ] Tâche 3 : Écrire `Field.test.tsx` (AC: 2)
  - [ ] Trouver ou créer `frontend/src/components/ui/Field/Field.test.tsx`
  - [ ] Test : rendu avec label
  - [ ] Test : label est associé au input (htmlFor / aria)
  - [ ] Test : saisie de texte déclenche onChange
  - [ ] Test : affichage du message d'erreur quand `error` fourni
  - [ ] Test : field disabled ne peut pas être modifié

- [ ] Tâche 4 : Écrire `Select.test.tsx` (AC: 3)
  - [ ] Trouver ou créer `frontend/src/components/ui/Select/Select.test.tsx`
  - [ ] Test : rendu avec les options
  - [ ] Test : sélection d'une option déclenche onChange
  - [ ] Test : placeholder affiché quand aucune valeur sélectionnée
  - [ ] Test : select disabled ne peut pas être modifié

- [ ] Tâche 5 : Validation (AC: 4)
  - [ ] `npm run test`
  - [ ] Tous les nouveaux tests passent

## Dev Notes

### Contexte technique

**Framework de test** : Vitest + `@testing-library/react`. Ne pas utiliser Jest, Enzyme, ou Playwright.

**Pattern de test existant** :
```tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { Button } from './Button'

describe('Button', () => {
  it('renders without crashing', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const onClick = vi.fn()
    render(<Button onClick={onClick}>Click</Button>)
    fireEvent.click(screen.getByRole('button'))
    expect(onClick).toHaveBeenCalledOnce()
  })

  it('does not call onClick when disabled', () => {
    const onClick = vi.fn()
    render(<Button disabled onClick={onClick}>Click</Button>)
    fireEvent.click(screen.getByRole('button'))
    expect(onClick).not.toHaveBeenCalled()
  })
})
```

**Lire les tests existants** avant d'écrire : les patterns établis dans `frontend/src/tests/` montrent comment le projet importe les composants et configure l'environnement.

**Attention** : Ne pas tester les styles visuels (ex: "la couleur est #xxx") — tester les comportements et la structure.

**Accessibilité** : Utiliser `getByRole('button')`, `getByLabelText()`, `getByRole('combobox')` plutôt que `getByTestId` — c'est la bonne pratique Testing Library.

### References

- [Source: frontend/src/components/ui/Button/Button.tsx]
- [Source: frontend/src/components/ui/Field/Field.tsx]
- [Source: frontend/src/components/ui/Select/Select.tsx]
- [Source: frontend/vitest.config.ts]
- [Source: frontend/src/tests/]
- [Source: _bmad-output/planning-artifacts/epic-57-tests-composants-ui.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
