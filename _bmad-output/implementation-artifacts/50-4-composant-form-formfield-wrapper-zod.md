# Story 50.4: Créer le wrapper <Form> + <FormField> avec intégration Zod

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux des composants `<Form>` et `<FormField>` qui intègrent la validation Zod et l'affichage d'erreurs,
afin de ne plus dupliquer la logique de gestion de formulaire dans chaque page.

## Acceptance Criteria

1. Le composant `frontend/src/components/ui/Form/Form.tsx` existe avec `<Form>` et `<FormField>` exportés via `frontend/src/components/ui/index.ts`.
2. `<Form>` accepte un schema Zod via prop `schema` et expose les méthodes `react-hook-form` aux enfants via Context.
3. `<FormField>` encapsule `<Field>` (story 50.2) et se connecte automatiquement à `react-hook-form` pour afficher les erreurs Zod.
4. Un hook `useFormContext()` réexporté permet aux composants enfants d'accéder au contexte du formulaire.
5. La prop `onSubmit` de `<Form>` reçoit les données validées par Zod (type-safe).
6. Les messages d'erreur Zod sont affichés via `<FormField>` sans code supplémentaire dans le composant consommateur.
7. La factory `createFormSchema(t: TranslationType)` est documentée comme pattern pour externaliser les messages d'erreur en i18n.
8. Un test couvre : soumission valide, soumission invalide avec affichage d'erreurs, état loading pendant la soumission.

## Tasks / Subtasks

- [ ] Tâche 1 : Vérifier les dépendances existantes (AC: 2)
  - [ ] Vérifier si `react-hook-form` et `zod` sont dans `frontend/package.json`
  - [ ] Vérifier si `@hookform/resolvers` est installé (nécessaire pour intégration Zod)
  - [ ] Si manquant : ajouter via `npm install` — documenter dans les notes de complétion

- [ ] Tâche 2 : Créer la structure de fichiers (AC: 1)
  - [ ] `frontend/src/components/ui/Form/Form.tsx`
  - [ ] `frontend/src/components/ui/Form/FormField.tsx`
  - [ ] `frontend/src/components/ui/Form/Form.test.tsx`
  - [ ] `frontend/src/components/ui/Form/index.ts`
  - [ ] Ajouter `export * from './Form'` dans `frontend/src/components/ui/index.ts`

- [ ] Tâche 3 : Implémenter `<Form>` (AC: 2, 4, 5)
  - [ ] `Form` utilise `useForm` de react-hook-form avec `zodResolver`
  - [ ] Context React exposant `formState`, `register`, `control`, `handleSubmit`
  - [ ] Prop `onSubmit: (data: z.infer<typeof schema>) => void | Promise<void>`
  - [ ] Prop `loading?: boolean` pour désactiver le formulaire pendant la soumission
  - [ ] Rendu d'un `<form>` HTML natif avec `onSubmit={handleSubmit(onSubmit)}`

- [ ] Tâche 4 : Implémenter `<FormField>` (AC: 3, 6)
  - [ ] `FormField` consomme le context Form et utilise `Controller` de react-hook-form
  - [ ] Prop `name: string` (nom du champ Zod)
  - [ ] Prop `as?: 'input' | 'select'` (défaut: 'input')
  - [ ] Passe automatiquement `error={fieldState.error?.message}` à `<Field>` ou `<Select>`
  - [ ] Transmet toutes les autres props à `<Field>` via spread

- [ ] Tâche 5 : Documenter le pattern `createFormSchema` (AC: 7)
  - [ ] Ajouter commentaire JSDoc dans Form.tsx expliquant le pattern
  - [ ] Exemple montrant comment passer les traductions i18n au schema Zod

- [ ] Tâche 6 : Écrire les tests (AC: 8)
  - [ ] Soumission valide : `onSubmit` appelé avec les données correctes
  - [ ] Soumission invalide : messages d'erreur visibles dans le DOM
  - [ ] État loading : champs désactivés
  - [ ] Reset du formulaire après soumission réussie (si applicable)

## Dev Notes

### Contexte technique

**Prérequis** : Stories 50.1 (`<Button>`) et 50.2 (`<Field>`) doivent être `done`.

**Bibliothèques actuelles** : Vérifier `frontend/package.json`. Dans les formulaires existants (SignInForm, SignUpForm), des imports `zod` sont présents — confirmer si `react-hook-form` et `@hookform/resolvers` sont déjà installés.

Si `react-hook-form` n'est PAS installé : c'est une dépendance de production à ajouter. Ne pas implémenter un gestionnaire de formulaire maison.

### Interface TypeScript

```typescript
import { z } from 'zod'
import { UseFormReturn } from 'react-hook-form'

interface FormProps<TSchema extends z.ZodType> {
  schema: TSchema
  onSubmit: (data: z.infer<TSchema>) => void | Promise<void>
  loading?: boolean
  children: React.ReactNode
  className?: string
}

interface FormFieldProps {
  name: string
  label?: string
  hint?: string
  type?: React.HTMLInputTypeAttribute
  placeholder?: string
  // + autres props de Field
}
```

### Pattern actuel dans SignInForm.tsx (à remplacer ultérieurement)

```typescript
// Actuellement dans SignInForm.tsx
const schema = z.object({
  email: z.string().email("Adresse e-mail invalide."),  // ← message hardcodé
  password: z.string().min(1, "Le mot de passe est requis.")
})
const { register, handleSubmit, formState: { errors } } = useForm({ resolver: zodResolver(schema) })
```

**Pattern cible** (utilisant Form + FormField, avec i18n) :
```typescript
// Futur — dans l'Epic 52 (i18n)
const schema = (t: AuthTranslations) => z.object({
  email: z.string().email(t.emailInvalid),
  password: z.string().min(1, t.passwordRequired)
})

// Dans le composant
<Form schema={schema(t)} onSubmit={handleSignIn} loading={isLoading}>
  <FormField name="email" type="email" label={t.emailLabel} />
  <FormField name="password" type="password" label={t.passwordLabel} />
  <Button type="submit" variant="primary" loading={isLoading}>{t.submitButton}</Button>
</Form>
```

### Context React

```typescript
const FormContext = createContext<UseFormReturn<any> | null>(null)

export function useFormContext() {
  const ctx = useContext(FormContext)
  if (!ctx) throw new Error('useFormContext must be used inside <Form>')
  return ctx
}
```

### Gestion des erreurs API (erreurs hors-formulaire)

Le composant `<Form>` ne gère que les erreurs de validation Zod. Les erreurs retournées par l'API (ex: "Email déjà utilisé") sont gérées dans le composant parent avec `setError` de react-hook-form et affichées via un `<FormField>` ou une alerte séparée. **Ne pas intégrer la gestion d'erreurs API dans `<Form>`** — trop spécifique.

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Créer | `frontend/src/components/ui/Form/Form.tsx` |
| Créer | `frontend/src/components/ui/Form/FormField.tsx` |
| Créer | `frontend/src/components/ui/Form/Form.test.tsx` |
| Créer | `frontend/src/components/ui/Form/index.ts` |
| Modifier | `frontend/src/components/ui/index.ts` |
| Potentiellement | `frontend/package.json` (si react-hook-form manquant) |

### Project Structure Notes

- Ne pas modifier SignInForm, SignUpForm ou BirthProfilePage dans cette story
- Les composants Form existants continueront à fonctionner avec leur ancien code
- La migration vers `<Form>` + `<FormField>` est prévue pour l'Epic 52 (i18n)

### References

- [Source: frontend/src/components/SignInForm.tsx]
- [Source: frontend/src/components/SignUpForm.tsx]
- [Source: frontend/package.json]
- [Source: frontend/src/components/ui/Field/Field.tsx] (story 50.2)
- [Source: frontend/src/styles/design-tokens.css]
- [Source: _bmad-output/planning-artifacts/epic-50-bibliotheque-composants-ui-primitifs.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
