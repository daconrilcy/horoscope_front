# Story 50.2: Créer le composant <Input> / <Field> avec types, états et validation

Status: done

## Story

En tant que développeur frontend,
je veux un composant `<Field>` partagé encapsulant `<label>` + `<input>` + message d'erreur/hint,
afin que tous les champs de saisie du produit aient un comportement, des états visuels et une accessibilité uniformes.

## Acceptance Criteria

1. Le composant `frontend/src/components/ui/Field/Field.tsx` existe et est exporté via `frontend/src/components/ui/index.ts`.
2. Les types `text`, `email`, `password`, `date`, `time`, `search` sont supportés via la prop `type`.
3. L'état `error` affiche un message d'erreur en dessous du champ avec l'icône et la couleur `--color-error`.
4. L'état `disabled` désactive le champ visuellement et fonctionnellement.
5. Les props `label`, `hint` (texte d'aide), `leftIcon` et `rightIcon` sont supportées.
6. La prop `password` gère le toggle show/hide avec un bouton icône intégré dans le champ.
7. Le composant est accessible : `<label>` lié par `htmlFor`/`id`, `aria-describedby` pour le message d'erreur, `aria-invalid="true"` en état erreur.
8. Tous les styles utilisent les tokens CSS de `design-tokens.css`.
9. Un fichier de tests `Field.test.tsx` couvre le rendu, l'état erreur, le toggle password et l'accessibilité.

## Tasks / Subtasks

- [x] Tâche 1 : Créer la structure de fichiers (AC: 1)
  - [x] `frontend/src/components/ui/Field/Field.tsx`
  - [x] `frontend/src/components/ui/Field/Field.css`
  - [x] `frontend/src/components/ui/Field/Field.test.tsx`
  - [x] `frontend/src/components/ui/Field/index.ts`
  - [x] Ajouter `export * from './Field'` dans `frontend/src/components/ui/index.ts`

- [x] Tâche 2 : Implémenter le composant (AC: 2, 3, 4, 5, 6, 7)
  - [x] Interface TypeScript `FieldProps`
  - [x] Génération automatique d'un `id` unique si non fourni (pour lier label/input)
  - [x] Label rendu si prop `label` fournie
  - [x] Hint rendu en gris sous le champ si prop `hint` fournie
  - [x] Message d'erreur rendu en rouge si prop `error` fournie
  - [x] Toggle show/hide pour `type="password"` (icône Eye/EyeOff de Lucide)
  - [x] `leftIcon` et `rightIcon` positionnés avec `padding-left`/`padding-right` adjusté sur l'input

- [x] Tâche 3 : Créer `Field.css` (AC: 8)
  - [x] `.field` : wrapper flex-column, gap `--space-1`
  - [x] `.field__label` : font-size `--font-size-sm`, color `--color-text-secondary`
  - [x] `.field__input-wrapper` : position relative (pour les icônes)
  - [x] `.field__input` : width 100%, padding, border-radius `--radius-md`, border, background, color, focus ring
  - [x] `.field__input--error` : border-color `--color-error`
  - [x] `.field__input--has-left-icon` : padding-left augmenté
  - [x] `.field__icon-left`, `.field__icon-right` : positionnement absolu centré verticalement
  - [x] `.field__error` : color `--color-error`, font-size `--font-size-sm`
  - [x] `.field__hint` : color `--color-text-muted`, font-size `--font-size-sm`
  - [x] Focus ring visible : `outline: 2px solid var(--color-primary)`, `outline-offset: 2px`

- [x] Tâche 4 : Écrire les tests (AC: 9)
  - [x] Rendu avec label et input liés (`htmlFor` = `id`)
  - [x] Message d'erreur visible quand prop `error` fournie + `aria-invalid="true"`
  - [x] Toggle password : icône visible, click change `type` entre `password` et `text`
  - [x] `aria-describedby` pointe vers le message d'erreur

## Dev Notes

### Contexte technique

**Prérequis** : Epic 49 `done`. Story 50.1 (`<Button>`) peut être en cours en parallèle.

**Icônes** : Le projet utilise Lucide React, importé via `frontend/src/ui/icons.tsx`. Utiliser `Eye` et `EyeOff` de Lucide pour le toggle password. Ne pas installer une nouvelle librairie d'icônes.

### Interface TypeScript

```typescript
interface FieldProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'id'> {
  label?: string
  hint?: string
  error?: string
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  // id est auto-généré si non fourni
  id?: string
}
```

### Usages actuels dans le codebase (référence pour l'API)

**SignInForm.tsx** — à migrer ultérieurement (Epic 52+) :
```tsx
// Actuellement
<label>Adresse e-mail</label>
<input type="email" ... />
{errors.email && <span className="chat-error">{errors.email}</span>}

// Après migration
<Field type="email" label={t.emailLabel} error={errors.email?.message} />
```

**BirthProfilePage.tsx** — inputs date, time, text :
```tsx
<Field type="date" label={t.birthDateLabel} />
<Field type="time" label={t.birthTimeLabel} hint={t.birthTimeHint} />
```

### Génération d'ID unique

```typescript
import { useId } from 'react' // React 18+ built-in

function Field({ id: providedId, label, ...props }: FieldProps) {
  const generatedId = useId()
  const id = providedId ?? generatedId
  // ...
}
```

### Styles — tokens utilisés

```css
.field__input {
  background: var(--color-bg-surface);
  border: 1px solid var(--color-glass-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-md);
  padding: var(--space-3) var(--space-4);
  transition: border-color var(--duration-fast);
}
.field__input:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
  border-color: var(--color-primary);
}
.field__input--error {
  border-color: var(--color-error);
}
```

### Toggle password

```typescript
const [showPassword, setShowPassword] = useState(false)
const inputType = type === 'password' ? (showPassword ? 'text' : 'password') : type
```

Le bouton toggle doit être de type `type="button"` pour éviter la soumission de formulaire accidentelle. Accessibilité : `aria-label="Afficher/Masquer le mot de passe"`.

### Classe CSS d'erreur existante

Le projet utilise `.chat-error` dans `App.css` pour afficher les erreurs de formulaire. Le nouveau composant `Field` créera sa propre classe `.field__error` plus générique — ne pas modifier `.chat-error` dans cette story.

### Fichiers à créer

| Action | Fichier |
|--------|---------|
| Créer | `frontend/src/components/ui/Field/Field.tsx` |
| Créer | `frontend/src/components/ui/Field/Field.css` |
| Créer | `frontend/src/components/ui/Field/Field.test.tsx` |
| Créer | `frontend/src/components/ui/Field/index.ts` |
| Modifier | `frontend/src/components/ui/index.ts` (ajouter export) |

### Project Structure Notes

- Lucide icons : `import { Eye, EyeOff } from 'lucide-react'` — déjà une dépendance du projet
- Ne pas importer depuis `frontend/src/ui/icons.tsx` si les icônes spécifiques ne sont pas dans le barrel export — importer directement depuis `lucide-react`
- `useId()` est disponible nativement dans React 18+ (le projet est en React 19)

### References

- [Source: frontend/src/components/SignInForm.tsx]
- [Source: frontend/src/components/SignUpForm.tsx]
- [Source: frontend/src/pages/BirthProfilePage.tsx]
- [Source: frontend/src/ui/icons.tsx]
- [Source: frontend/src/App.css] (`.chat-error` existant)
- [Source: frontend/src/styles/design-tokens.css]
- [Source: _bmad-output/planning-artifacts/epic-50-bibliotheque-composants-ui-primitifs.md]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

### Completion Notes List

- Composant `<Field>` implémenté avec support pour labels, hints, erreurs et icônes.
- Gestion intégrée du toggle de visibilité pour les champs de type `password`.
- Accessibilité complète avec `useId`, `aria-describedby` et `aria-invalid`.
- Utilisation systématique des design tokens pour le styling.
- 7 tests unitaires couvrant les fonctionnalités clés.

### Change Log

- 2026-03-14 : Implémentation complète du composant Field.

### File List

| Action | Fichier |
|--------|---------|
| Créé | `frontend/src/components/ui/Field/Field.tsx` |
| Créé | `frontend/src/components/ui/Field/Field.css` |
| Créé | `frontend/src/components/ui/Field/Field.test.tsx` |
| Créé | `frontend/src/components/ui/Field/index.ts` |
| Modifié | `frontend/src/components/ui/index.ts` |
