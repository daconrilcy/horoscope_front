# Story 52.5: Migrer les schemas Zod vers des factory functions avec messages i18n

Status: done

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

- [x] Tâche 1 : Compléter `i18n/auth.ts` avec la section validation (AC: 1)
  - [x] Ajout de l'interface `validation` dans `AuthTranslation`.
  - [x] Remplissage des traductions pour FR, EN, ES.

- [x] Tâche 2 : Créer `createSignInSchema` dans SignInForm.tsx (AC: 2)
  - [x] Implémentation de la factory function.
  - [x] Utilisation de `useMemo` pour la stabilité du schéma.

- [x] Tâche 3 : Créer `createSignUpSchema` dans SignUpForm.tsx (AC: 3)
  - [x] Implémentation de la factory function.
  - [x] Utilisation de `useMemo` pour la stabilité du schéma.

- [x] Tâche 4 : Mettre à jour le hook `useForm` dans les deux composants (AC: 4, 5)
  - [x] Intégration du schéma dynamique dans `zodResolver`.

- [x] Tâche 5 : Validation (AC: 6)
  - [x] `npm run test` — 1079 tests réussis.

## Dev Notes

### Stabilité des schémas Zod

L'utilisation de `useMemo` pour instancier le schéma Zod est cruciale. Sans cela, le schéma serait recréé à chaque rendu du composant, ce qui forcerait `react-hook-form` à réinitialiser son état interne (et potentiellement perdre le focus de l'input en cours de saisie) car la référence du resolver changerait.

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List
- Extension de `i18n/auth.ts` avec les messages de validation.
- Migration de `SignInForm` vers un schéma i18n dynamique.
- Migration de `SignUpForm` vers un schéma i18n dynamique.
- Utilisation de `useMemo` pour garantir la performance et la stabilité du formulaire.
- Validation via 1079 tests réussis.

### File List
- `frontend/src/i18n/auth.ts`
- `frontend/src/components/SignInForm.tsx`
- `frontend/src/components/SignUpForm.tsx`
