# Story 52.5: Migrer les schemas Zod vers des factory functions avec messages i18n

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux que les messages d'erreur des schemas Zod soient extraits des schemas et fournis via les fichiers i18n,
afin que les messages de validation s'affichent dans la langue de l'utilisateur.

## Acceptance Criteria

1. `i18n/auth.ts` est complété avec une section `validation` contenant les messages d'erreur Zod pour SignInForm et SignUpForm en FR, EN, ES.
2. `SignInForm.tsx` utilise une factory function `createSignInSchema(t: AuthTranslation)` qui reçoit les traductions et produit le schema Zod avec des messages localisés.
3. `SignUpForm.tsx` utilise une factory function `createSignUpSchema(t: AuthTranslation)` de la même manière.
4. Aucun message d'erreur Zod hardcodé ne subsiste dans les deux composants.
5. Les messages de validation s'affichent en FR par défaut, EN si la langue est EN, ES si ES.
6. Les tests de validation existants (soumission d'email invalide, mot de passe vide) passent dans les 3 langues.

## Tasks / Subtasks

- [ ] Tâche 1 : Compléter `i18n/auth.ts` avec la section validation (AC: 1)
  - [ ] Ajouter `validation` dans `AuthTranslation` :
    ```typescript
    validation: {
      emailInvalid: string
      passwordRequired: string
      passwordTooShort: string
      emailRequired: string
    }
    ```
  - [ ] Remplir FR, EN, ES pour ces messages

- [ ] Tâche 2 : Créer `createSignInSchema` dans SignInForm.tsx ou dans un fichier dédié (AC: 2)
  - [ ] Factory function qui reçoit `t: AuthTranslation` (ou `t: AuthTranslation['validation']`)
  - [ ] Retourne le schema Zod avec `z.string().email(t.validation.emailInvalid)` etc.
  - [ ] Appeler avec `createSignInSchema(authTranslations(lang))` dans le composant

- [ ] Tâche 3 : Créer `createSignUpSchema` dans SignUpForm.tsx (AC: 3)
  - [ ] Même pattern que createSignInSchema
  - [ ] Couvre : email invalide, email requis, mot de passe trop court (min 8 caractères)

- [ ] Tâche 4 : Mettre à jour le hook `useForm` dans les deux composants (AC: 4, 5)
  - [ ] Le schema est maintenant créé avec `useMemo(() => createSignXSchema(t), [t])` ou calculé à la volée
  - [ ] Vérifier que le schema est stable (pas recréé à chaque render) pour éviter la perte du focus

- [ ] Tâche 5 : Écrire les tests de validation multilingue (AC: 6)
  - [ ] Tester que `createSignInSchema(authTranslations('en'))` produit des messages en anglais
  - [ ] Tester que `createSignInSchema(authTranslations('fr'))` produit des messages en français

## Dev Notes

### Contexte technique

**Prérequis** : Story 52.1 `done` (auth.ts existant avec les traductions de base).

**react-hook-form + zodResolver** sont déjà utilisés dans SignInForm et SignUpForm. Le pattern de factory function est compatible.

### Problème de stabilité du schema

Si `createSignInSchema(t)` est appelé directement dans le composant :
```typescript
// ⚠️ Problème : schema recréé à chaque render
const schema = createSignInSchema(t)
const { register } = useForm({ resolver: zodResolver(schema) })
```

Solution avec `useMemo` :
```typescript
// ✅ Schema stable
const schema = useMemo(() => createSignInSchema(t), [t])
const { register } = useForm({ resolver: zodResolver(schema) })
```

Ou encore mieux — la langue ne change pas mid-session, donc calculer le schema une seule fois :
```typescript
// ✅ Alternatif — calculé une fois hors du composant (si lang est stable)
const lang = detectLang()
const t = authTranslations(lang)
const schema = createSignInSchema(t)  // en dehors du composant React
```

### Messages d'erreur Zod actuels à migrer

**SignInForm.tsx** :
```typescript
// Avant
z.string().email("Adresse e-mail invalide.")
z.string().min(1, "Le mot de passe est requis.")

// Après
z.string().email(t.validation.emailInvalid)
z.string().min(1, t.validation.passwordRequired)
```

**SignUpForm.tsx** (attendu) :
```typescript
// Avant
z.string().email("Adresse e-mail invalide.")
z.string().min(8, "Le mot de passe doit contenir au moins 8 caractères.")

// Après
z.string().email(t.validation.emailInvalid)
z.string().min(8, t.validation.passwordTooShort)
```

### Structure de la factory function

```typescript
// Dans SignInForm.tsx ou src/schemas/auth.ts
import { z } from "zod"
import type { AuthTranslation } from "../i18n/auth"

export function createSignInSchema(t: AuthTranslation) {
  return z.object({
    email: z.string().email(t.validation.emailInvalid),
    password: z.string().min(1, t.validation.passwordRequired),
  })
}
export type SignInFormData = z.infer<ReturnType<typeof createSignInSchema>>
```

### Emplacement des factory functions

**Option A** : Directement dans `SignInForm.tsx` et `SignUpForm.tsx` (simple, proche du composant)
**Option B** : Dans un fichier `frontend/src/schemas/auth.ts` (séparation des responsabilités)

**Recommandation** : Option A pour l'instant — YAGNI. Si d'autres composants utilisent ces schemas, extraire en Option B.

### Section `validation` dans `AuthTranslation`

```typescript
// Ajout dans i18n/auth.ts
validation: {
  emailInvalid: string       // "Adresse e-mail invalide."
  emailRequired: string      // "L'adresse e-mail est requise."
  passwordRequired: string   // "Le mot de passe est requis."
  passwordTooShort: string   // "Le mot de passe doit contenir au moins 8 caractères."
}
```

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Modifier | `frontend/src/i18n/auth.ts` (ajouter section validation) |
| Modifier | `frontend/src/components/SignInForm.tsx` |
| Modifier | `frontend/src/components/SignUpForm.tsx` |

### References

- [Source: frontend/src/components/SignInForm.tsx]
- [Source: frontend/src/components/SignUpForm.tsx]
- [Source: frontend/src/i18n/auth.ts] (créé en story 52.1)
- [Source: _bmad-output/planning-artifacts/epic-52-i18n-complet.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
