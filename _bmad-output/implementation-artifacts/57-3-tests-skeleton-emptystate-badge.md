# Story 57.3: Tests Skeleton, EmptyState, Badge/IconBadge — composants d'état et micro-UI

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux des tests unitaires complets pour `Skeleton`, `EmptyState` et `Badge`/`IconBadge`,
afin de garantir la stabilité de ces composants d'état et micro-UI utilisés partout dans l'application.

## Acceptance Criteria

1. `Skeleton.test.tsx` couvre : rendu du nombre correct d'éléments, variants (ligne, bloc, cercle).
2. `EmptyState.test.tsx` couvre : rendu avec et sans bouton d'action, icône, titre, message.
3. `Badge.test.tsx` et `IconBadge.test.tsx` couvrent : variants de couleur, rendu du contenu, tailles.
4. Tous les tests passent avec `npm run test`.
5. Les tests utilisent `@testing-library/react` et `vitest` uniquement.

## Tasks / Subtasks

- [ ] Tâche 1 : Lire les composants à tester (AC: 1, 2, 3)
  - [ ] Lire `frontend/src/components/ui/Skeleton/Skeleton.tsx`
  - [ ] Lire `frontend/src/components/ui/EmptyState/EmptyState.tsx`
  - [ ] Lire `frontend/src/components/ui/Badge/Badge.tsx`
  - [ ] Lire `frontend/src/components/ui/Badge/IconBadge.tsx` si séparé
  - [ ] Identifier l'API de props de chaque composant

- [ ] Tâche 2 : Écrire tests Skeleton (AC: 1)
  - [ ] Test : Skeleton rend sans crash
  - [ ] Test : Skeleton avec `count={3}` rend 3 éléments
  - [ ] Test : Skeleton de type 'line' a la bonne classe/attribut aria
  - [ ] Test : Skeleton a le bon rôle ARIA (`aria-busy`, `aria-label="Chargement"` ou similaire)

- [ ] Tâche 3 : Écrire tests EmptyState (AC: 2)
  - [ ] Test : rendu avec titre et message
  - [ ] Test : bouton d'action non rendu si `onAction` absent
  - [ ] Test : bouton d'action rendu si `onAction` fourni
  - [ ] Test : click sur le bouton déclenche `onAction`
  - [ ] Test : icône rendue si prop `icon` fournie

- [ ] Tâche 4 : Écrire tests Badge et IconBadge (AC: 3)
  - [ ] Test : Badge rend son contenu texte
  - [ ] Test : Badge avec `variant="success"` a la bonne classe CSS
  - [ ] Test : Badge avec `variant="danger"` a la bonne classe CSS
  - [ ] Test : IconBadge rend l'icône et le label
  - [ ] Test : IconBadge accessible (aria-label ou texte visible)

- [ ] Tâche 5 : Validation finale de l'Epic 57 (AC: 4)
  - [ ] `npm run test`
  - [ ] Tous les tests de l'Epic 57 (57.1, 57.2, 57.3) passent ensemble

## Dev Notes

### Contexte technique

**Prérequis** : Stories 57.1 et 57.2 `done` — patterns de test établis.

**Skeleton et accessibilité** : Les squelettes de chargement doivent être accessibles. Tester que le composant annonce l'état de chargement aux lecteurs d'écran :
```tsx
it('is accessible during loading', () => {
  render(<Skeleton />)
  // Vérifier aria-busy ou aria-label
  expect(screen.getByRole('status')).toBeInTheDocument()
  // ou
  expect(screen.getByLabelText(/chargement/i)).toBeInTheDocument()
})
```

**EmptyState** : Ce composant est utilisé dans plusieurs pages pour les listes vides. Tester qu'il est flexible :
```tsx
it('renders without action button when no onAction provided', () => {
  render(<EmptyState title="Aucun résultat" message="Essayez une autre recherche" />)
  expect(screen.queryByRole('button')).not.toBeInTheDocument()
})

it('renders action button when onAction provided', () => {
  const onAction = vi.fn()
  render(<EmptyState title="Aucun résultat" message="..." onAction={onAction} actionLabel="Créer" />)
  expect(screen.getByRole('button', { name: 'Créer' })).toBeInTheDocument()
})
```

**Badge** : Les variants sont probablement appliqués via des classes CSS. Ne pas tester la couleur visuelle — tester la classe :
```tsx
it('applies correct CSS class for success variant', () => {
  render(<Badge variant="success">Actif</Badge>)
  expect(screen.getByText('Actif').closest('[class*="badge"]')).toHaveClass('badge--success')
  // ou selon la convention de nommage du projet
})
```

**Bilan Epic 57** : Après cette story, documenter dans les Completion Notes le nombre total de tests ajoutés, les composants couverts, et tout pattern de test établi pour référence future.

### References

- [Source: frontend/src/components/ui/Skeleton/Skeleton.tsx]
- [Source: frontend/src/components/ui/EmptyState/EmptyState.tsx]
- [Source: frontend/src/components/ui/Badge/]
- [Source: frontend/vitest.config.ts]
- [Source: _bmad-output/implementation-artifacts/57-1-tests-button-field-select.md]
- [Source: _bmad-output/implementation-artifacts/57-2-tests-form-modal-card.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
