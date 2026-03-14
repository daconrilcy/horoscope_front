# Story 57.2: Tests Form/FormField, Modal, Card — composants de structure

Status: ready-for-dev

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

- [ ] Tâche 1 : Lire les composants à tester (AC: 1, 2, 3)
  - [ ] Lire `frontend/src/components/ui/Form/` (ou fichier Form)
  - [ ] Lire `frontend/src/components/ui/Modal/Modal.tsx`
  - [ ] Lire `frontend/src/components/ui/Card/Card.tsx`
  - [ ] Identifier l'API de props de chaque composant

- [ ] Tâche 2 : Écrire tests Form/FormField (AC: 1)
  - [ ] Test : FormField rend le Field avec le label correct
  - [ ] Test : FormField affiche l'erreur Zod quand la validation échoue
  - [ ] Test : soumission de Form appelle le handler avec les données correctes
  - [ ] Test : soumission avec données invalides n'appelle pas le handler

- [ ] Tâche 3 : Écrire tests Modal (AC: 2)
  - [ ] Test : Modal n'est pas rendu quand `isOpen=false`
  - [ ] Test : Modal est rendu quand `isOpen=true`
  - [ ] Test : clic sur le bouton de fermeture déclenche `onClose`
  - [ ] Test : touche Escape déclenche `onClose`
  - [ ] Test : le contenu passé en children est rendu dans la modal

- [ ] Tâche 4 : Écrire tests Card (AC: 3)
  - [ ] Test : Card rend ses enfants
  - [ ] Test : Card.Header rend le titre
  - [ ] Test : Card.Body rend le contenu
  - [ ] Test : Card avec variant applique la bonne classe CSS

- [ ] Tâche 5 : Validation (AC: 4)
  - [ ] `npm run test`

## Dev Notes

### Contexte technique

**Prérequis** : Story 57.1 `done` — les patterns de test sont établis.

**Form avec react-hook-form** : Le composant `Form` utilise probablement `react-hook-form`. Pour les tests, utiliser `userEvent` de `@testing-library/user-event` pour la saisie de formulaire (plus réaliste que `fireEvent`).

```tsx
import userEvent from '@testing-library/user-event'

it('submits form with valid data', async () => {
  const onSubmit = vi.fn()
  render(<Form onSubmit={onSubmit} schema={mySchema}>...</Form>)

  await userEvent.type(screen.getByLabelText('Email'), 'test@example.com')
  await userEvent.click(screen.getByRole('button', { name: 'Soumettre' }))

  await waitFor(() => expect(onSubmit).toHaveBeenCalled())
})
```

**Modal et portals** : Si Modal utilise `createPortal`, s'assurer que le test setup inclut un div `#modal-root` ou que `document.body` est utilisé. Vérifier dans `vitest.config.ts` l'environnement DOM (jsdom).

**Card compound components** : Si Card utilise le pattern dot-notation (Card.Header, etc.), tester la composition :
```tsx
render(
  <Card>
    <Card.Header>Titre</Card.Header>
    <Card.Body>Contenu</Card.Body>
  </Card>
)
expect(screen.getByText('Titre')).toBeInTheDocument()
expect(screen.getByText('Contenu')).toBeInTheDocument()
```

**`@testing-library/user-event`** : Vérifier qu'il est installé. Si non, utiliser `fireEvent` de `@testing-library/react` comme fallback.

### References

- [Source: frontend/src/components/ui/Form/]
- [Source: frontend/src/components/ui/Modal/Modal.tsx]
- [Source: frontend/src/components/ui/Card/Card.tsx]
- [Source: frontend/vitest.config.ts]
- [Source: _bmad-output/implementation-artifacts/57-1-tests-button-field-select.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
