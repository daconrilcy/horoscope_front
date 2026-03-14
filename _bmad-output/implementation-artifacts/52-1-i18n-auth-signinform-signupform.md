# Story 52.1: Créer i18n/auth.ts — traductions SignInForm et SignUpForm

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux un fichier `i18n/auth.ts` centralisant tous les textes des pages d'authentification,
afin que SignInForm et SignUpForm soient entièrement traduits en FR, EN et ES sans aucune string hardcodée.

## Acceptance Criteria

1. Le fichier `frontend/src/i18n/auth.ts` existe avec les types `AuthTranslation` et les traductions FR, EN, ES.
2. `AuthTranslation` couvre : titre de page, labels email/password, placeholder, boutons submit/loading, lien vers l'autre form, messages d'erreur API (401, générique), et textes d'accompagnement.
3. Une fonction `authTranslations(lang: AppLocale): AuthTranslation` est exportée (pattern identique aux fichiers i18n existants).
4. `SignInForm.tsx` utilise `authTranslations(lang)` pour tous ses textes — aucune string en dur.
5. `SignUpForm.tsx` utilise `authTranslations(lang)` pour tous ses textes — aucune string en dur.
6. La détection de langue dans SignInForm et SignUpForm utilise `detectLang()` importée de `i18n/astrology` (pattern existant — ne pas introduire de nouveau mécanisme).
7. Les tests existants de SignInForm et SignUpForm passent sans modification.

## Tasks / Subtasks

- [ ] Tâche 1 : Lire `SignUpForm.tsx` entièrement (AC: 2)
  - [ ] Lister tous les textes hardcodés (labels, erreurs, boutons, liens)
  - [ ] Compiler la liste complète des clés nécessaires dans `AuthTranslation`

- [ ] Tâche 2 : Créer `frontend/src/i18n/auth.ts` (AC: 1, 2, 3)
  - [ ] Définir l'interface `AuthTranslation` avec toutes les clés identifiées
  - [ ] Remplir les traductions FR (copier les strings hardcodées existantes)
  - [ ] Remplir les traductions EN (traduction fidèle)
  - [ ] Remplir les traductions ES (traduction fidèle)
  - [ ] Exporter `authTranslations(lang: AppLocale): AuthTranslation`
  - [ ] Utiliser `AppLocale` si le type est défini par story 52.4, sinon utiliser `AstrologyLang` importé depuis `i18n/astrology.ts`

- [ ] Tâche 3 : Migrer `SignInForm.tsx` (AC: 4, 6)
  - [ ] Ajouter `const lang = detectLang()` et `const t = authTranslations(lang)`
  - [ ] Remplacer chaque string hardcodée par la clé `t.xxx` correspondante
  - [ ] Conserver toute la logique de formulaire (react-hook-form, zodResolver, API calls) inchangée
  - [ ] **Les messages d'erreur Zod restent hardcodés pour l'instant** — ils seront migrés en story 52.5

- [ ] Tâche 4 : Migrer `SignUpForm.tsx` (AC: 5, 6)
  - [ ] Même approche que SignInForm
  - [ ] **Les messages d'erreur Zod restent hardcodés pour l'instant**

- [ ] Tâche 5 : Validation (AC: 7)
  - [ ] `npm run test` — tous les tests passent
  - [ ] Vérifier visuellement `/login` et `/register` en FR, EN (changer `navigator.language`)

## Dev Notes

### Contexte technique

**Prérequis** : Aucun prérequis dans cet epic — cette story peut démarrer immédiatement.

**Note sur `AppLocale`** : Le type unifié `AppLocale` sera créé en story 52.4. Dans cette story, utiliser `AstrologyLang` importé de `i18n/astrology.ts` — il sera remplacé par un alias en 52.4 sans changement de code.

**`detectLang()`** est importé depuis `frontend/src/i18n/astrology.ts` dans plusieurs composants. Confirmer qu'il est bien exporté depuis ce fichier avant de l'utiliser dans SignInForm.

### Inventaire complet des strings hardcodées dans SignInForm.tsx

```
// Titre
"Connexion"                                           → t.signIn.title

// Labels
"Adresse e-mail"                                      → t.signIn.emailLabel
"Mot de passe"                                        → t.signIn.passwordLabel

// Messages d'erreur Zod (LAISSER POUR STORY 52.5)
"Adresse e-mail invalide."
"Le mot de passe est requis."

// Bouton submit
"Se connecter"                                        → t.signIn.submitButton
"Connexion en cours..."                               → t.signIn.submitLoading

// Erreurs API
"Identifiants incorrects. Veuillez réessayer."        → t.signIn.errorInvalidCredentials
"Une erreur est survenue. Veuillez réessayer."        → t.signIn.errorGeneric

// Lien vers Register
"Pas encore de compte ?"                              → t.signIn.noAccount
"Créer un compte"                                     → t.signIn.createAccount
```

### Inventaire des strings hardcodées dans SignUpForm.tsx (à lire)

```
// Attendu d'après l'analyse codebase
"Créer un compte"                                     → t.signUp.title
"Adresse e-mail"                                      → t.signUp.emailLabel
"Mot de passe"                                        → t.signUp.passwordLabel

// Messages Zod (LAISSER POUR STORY 52.5)
"Adresse e-mail invalide."
"Le mot de passe doit contenir au moins 8 caractères."

// Bouton
"Créer mon compte"                                    → t.signUp.submitButton
"Inscription en cours..."                             → t.signUp.submitLoading

// Erreurs API
"Cette adresse e-mail est déjà utilisée."             → t.signUp.errorEmailTaken
"Inscription impossible."                             → t.signUp.errorGeneric

// Lien vers Login
"Déjà un compte ?"                                    → t.signUp.alreadyHaveAccount
"Se connecter"                                        → t.signUp.signInLink
```

### Structure du fichier `i18n/auth.ts`

```typescript
import type { AstrologyLang } from "./astrology"

export interface AuthTranslation {
  signIn: {
    title: string
    emailLabel: string
    passwordLabel: string
    submitButton: string
    submitLoading: string
    errorInvalidCredentials: string
    errorGeneric: string
    noAccount: string
    createAccount: string
  }
  signUp: {
    title: string
    emailLabel: string
    passwordLabel: string
    submitButton: string
    submitLoading: string
    errorEmailTaken: string
    errorGeneric: string
    alreadyHaveAccount: string
    signInLink: string
  }
  // Messages d'erreur Zod — à ajouter en story 52.5
  // validation: { emailInvalid: string; passwordRequired: string; ... }
}

const translations: Record<AstrologyLang, AuthTranslation> = {
  fr: { ... },
  en: { ... },
  es: { ... },
}

export function authTranslations(lang: AstrologyLang = "fr"): AuthTranslation {
  return translations[lang] ?? translations.fr
}
```

### Détection de la langue dans les composants

Pattern actuel dans les autres composants (ex: `SettingsPage.tsx`) :
```typescript
import { detectLang } from "../i18n/astrology"
const lang = detectLang()
```

Utiliser ce même pattern dans SignInForm et SignUpForm. **Ne pas utiliser `useAstrologyLabels()`** dans ces composants — ils n'ont pas besoin du hook complet, juste de la langue.

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Créer | `frontend/src/i18n/auth.ts` |
| Modifier | `frontend/src/components/SignInForm.tsx` |
| Modifier | `frontend/src/components/SignUpForm.tsx` |

### Project Structure Notes

- `auth.ts` va dans `frontend/src/i18n/` — cohérent avec les 10 fichiers i18n existants
- Suivre exactement le pattern des fichiers existants : type de traduction → objet `translations` → fonction export
- Ne pas créer de système de namespaces encore — ça vient en story 52.4

### References

- [Source: frontend/src/components/SignInForm.tsx]
- [Source: frontend/src/components/SignUpForm.tsx]
- [Source: frontend/src/i18n/dashboard.tsx] (pattern à reproduire)
- [Source: frontend/src/i18n/astrology.ts] (AstrologyLang, detectLang)
- [Source: _bmad-output/planning-artifacts/epic-52-i18n-complet.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
