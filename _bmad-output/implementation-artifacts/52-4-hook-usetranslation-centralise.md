# Story 52.4: Créer i18n/types.ts + hook useTranslation(namespace) centralisé

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux un type `AppLocale` unifié et un hook `useTranslation(namespace)` centralisé,
afin de remplacer le pattern dupliqué `const { lang } = useAstrologyLabels()` présent dans 15+ composants par une seule ligne.

## Acceptance Criteria

1. Le fichier `frontend/src/i18n/types.ts` existe avec `AppLocale = "fr" | "en" | "es"` comme type canonique.
2. `AstrologyLang` dans `i18n/astrology.ts` et `SupportedLocale` dans `i18n/dashboard.tsx` deviennent des alias de `AppLocale` — rétrocompatibilité totale.
3. Le hook `useTranslation` est exporté depuis `frontend/src/i18n/index.ts` et supporte les namespaces : `'auth'`, `'common'`, `'navigation'`, `'dashboard'`, `'settings'`, `'admin'`, `'astrology'`, `'predictions'`, `'consultations'`, `'natalChart'`, `'birthProfile'`, `'astrologers'`, `'insights'`.
4. `useTranslation('dashboard')` retourne le type `DashboardPageTranslation` — TypeScript valide sans cast.
5. Les composants qui utilisaient `const { lang } = useAstrologyLabels(); const t = translateX(lang)` sont migrés vers `const t = useTranslation('namespace')`.
6. `detectLang()` continue de fonctionner — il est réexporté depuis `i18n/index.ts` pour les contextes hors-hook (schemas Zod, etc.).
7. Tous les tests existants passent.

## Tasks / Subtasks

- [ ] Tâche 1 : Créer `frontend/src/i18n/types.ts` (AC: 1)
  - [ ] `export type AppLocale = "fr" | "en" | "es"`
  - [ ] `export const DEFAULT_LOCALE: AppLocale = "fr"`
  - [ ] `export const SUPPORTED_LOCALES: AppLocale[] = ["fr", "en", "es"]`

- [ ] Tâche 2 : Créer les alias dans les fichiers existants (AC: 2)
  - [ ] Dans `i18n/astrology.ts` : ajouter `import type { AppLocale } from './types'` et `export type AstrologyLang = AppLocale`
  - [ ] Dans `i18n/dashboard.tsx` : même alias pour `SupportedLocale`
  - [ ] Vérifier que les imports downstream ne cassent pas (TypeScript compile)

- [ ] Tâche 3 : Créer `frontend/src/i18n/index.ts` — barrel + hook (AC: 3, 4, 6)
  - [ ] Réexporter tous les fichiers i18n (auth, common, navigation, dashboard, settings, etc.)
  - [ ] Réexporter `detectLang` et `AppLocale`
  - [ ] Implémenter `useTranslation<N extends TranslationNamespace>(namespace: N)`
  - [ ] Mapper chaque namespace vers sa fonction de traduction et son type de retour

- [ ] Tâche 4 : Migrer les composants avec pattern `useAstrologyLabels` + translate (AC: 5)
  - [ ] Grep `useAstrologyLabels` dans tout `frontend/src/`
  - [ ] Pour chaque occurrence : remplacer par `useTranslation(namespace)` approprié
  - [ ] Priorité : composants de pages (DashboardPage, DailyHoroscopePage, etc.)

- [ ] Tâche 5 : Migrer les composants avec pattern `detectLang` + translate (AC: 5)
  - [ ] Grep `detectLang` dans tout `frontend/src/components/` et `frontend/src/pages/`
  - [ ] Remplacer par `useTranslation` dans les composants React (contexte hook valide)
  - [ ] Garder `detectLang` dans les contextes non-React (schemas Zod, fonctions pures)

- [ ] Tâche 6 : Validation (AC: 7)
  - [ ] TypeScript compile sans erreurs (`npm run build`)
  - [ ] `npm run test`
  - [ ] Vérifier quelques pages en FR et EN

## Dev Notes

### Contexte technique

**Prérequis** : Stories 52.1, 52.2, 52.3 doivent être `done` (les fichiers i18n référencés dans le hook doivent exister).

### Implémentation du hook `useTranslation`

Le hook détecte la langue via `useAstrologyLabels()` (qui est un hook React existant basé sur l'état ou le contexte) et appelle la fonction de traduction appropriée :

```typescript
// i18n/index.ts

import { useAstrologyLabels } from "./astrology"
import { authTranslations, type AuthTranslation } from "./auth"
import { commonTranslations, type CommonTranslation } from "./common"
import { navigationTranslations, type NavigationTranslation } from "./navigation"
import { translateDashboardPage, type DashboardPageTranslation } from "./dashboard"
// ... autres imports

type TranslationMap = {
  auth: AuthTranslation
  common: CommonTranslation
  navigation: NavigationTranslation
  dashboard: DashboardPageTranslation
  settings: SettingsTranslation
  admin: AdminTranslation
  // etc.
}

export type TranslationNamespace = keyof TranslationMap

const translationFunctions: {
  [K in TranslationNamespace]: (lang: AppLocale) => TranslationMap[K]
} = {
  auth: authTranslations,
  common: commonTranslations,
  navigation: navigationTranslations,
  dashboard: translateDashboardPage,
  // etc.
}

export function useTranslation<N extends TranslationNamespace>(namespace: N): TranslationMap[N] {
  const { lang } = useAstrologyLabels()
  return translationFunctions[namespace](lang) as TranslationMap[N]
}
```

### Nommage des fonctions de traduction existantes

Vérifier les noms exacts des fonctions exportées dans chaque fichier i18n existant :
- `dashboard.tsx` → `translateDashboardPage(lang)`
- `settings.ts` → `settingsTranslations.page[lang]` (pattern différent — à vérifier)
- `admin.ts` → `adminTranslations.page[lang]` (pattern différent — à vérifier)

Si certains fichiers i18n utilisent un pattern objet (`.page[lang]`) au lieu d'une fonction, créer un wrapper dans `i18n/index.ts` :

```typescript
const translationFunctions = {
  settings: (lang: AppLocale) => settingsTranslations.page[lang],
  admin: (lang: AppLocale) => adminTranslations.page[lang],
  // etc.
}
```

### Grep pour identifier les composants à migrer

```bash
# Composants avec useAstrologyLabels
grep -rn "useAstrologyLabels" frontend/src/components/ frontend/src/pages/

# Composants avec detectLang
grep -rn "detectLang" frontend/src/components/ frontend/src/pages/
```

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Créer | `frontend/src/i18n/types.ts` |
| Créer | `frontend/src/i18n/index.ts` |
| Modifier | `frontend/src/i18n/astrology.ts` (alias AstrologyLang) |
| Modifier | `frontend/src/i18n/dashboard.tsx` (alias SupportedLocale) |
| Modifier | 15+ composants (migration pattern → useTranslation) |

### Project Structure Notes

- `i18n/index.ts` est le nouveau point d'entrée central : `import { useTranslation } from '../i18n'`
- Les imports directs vers les fichiers i18n spécifiques (`import { authTranslations } from '../i18n/auth'`) restent valides — pas de migration forcée
- Ne pas rendre les imports directs obsolètes — uniquement proposer `useTranslation` comme alternative plus simple

### References

- [Source: frontend/src/i18n/astrology.ts] (useAstrologyLabels, detectLang, AstrologyLang)
- [Source: frontend/src/i18n/dashboard.tsx] (SupportedLocale)
- [Source: frontend/src/i18n/settings.ts]
- [Source: frontend/src/i18n/admin.ts]
- [Source: frontend/src/pages/SettingsPage.tsx] (exemple de composant à migrer)
- [Source: frontend/src/pages/AdminPage.tsx] (exemple de composant à migrer)
- [Source: _bmad-output/planning-artifacts/epic-52-i18n-complet.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
