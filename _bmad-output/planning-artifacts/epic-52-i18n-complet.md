# Epic 52: Compléter et unifier le système i18n — zéro texte en dur dans les composants

Status: split-into-stories

## Contexte

Le système i18n existant (10 fichiers dans `frontend/src/i18n/`) couvre bien les domaines métier (astrologie, prédictions, consultations, settings, admin). Cependant plusieurs zones du produit restent avec des textes hardcodés en français :

- `SignInForm.tsx` et `SignUpForm.tsx` : tous les labels, erreurs Zod, messages API, boutons et liens
- `Header.tsx` : "Se déconnecter", "Utilisateur"
- `HeroHoroscopeCard.tsx` : "Lire en 2 min", "Version détaillée"
- `ui/nav.ts` : tous les labels de navigation ("Aujourd'hui", "Chat", "Thème", "Consultations"...)
- Panneaux B2B (`B2BAstrologyPanel`, `B2BBillingPanel`, etc.) : titres et messages d'erreur
- Les messages d'erreur Zod dans `SignInForm` et `SignUpForm` sont hardcodés directement dans les schemas

Problèmes structurels identifiés :
- **Duplication du pattern de détection de langue** : `const { lang } = useAstrologyLabels()` ou `const lang = detectLang()` répété dans 15+ composants
- **Deux types identiques** : `AstrologyLang` (dans `i18n/astrology.ts`) et `SupportedLocale` (dans `i18n/dashboard.tsx`) représentent la même chose — `"fr" | "en" | "es"` — sans être unifiés
- **Aucun hook `useTranslation`** centralisé — chaque composant accède aux traductions différemment

## Objectif Produit

Créer un système i18n exhaustif qui :

1. Couvre 100% des textes visibles du produit (zéro string en dur dans les composants)
2. Unifie `AstrologyLang` / `SupportedLocale` en un seul type partagé
3. Fournit un hook `useTranslation(namespace)` simple qui remplace le pattern dupliqué dans 15+ composants
4. Externalise les messages d'erreur Zod vers les fichiers i18n via des factory functions
5. Couvre les 3 langues : français (défaut), anglais, espagnol

## Non-objectifs

- Ne pas introduire une librairie i18n externe (react-i18next, i18next, etc.) — le système custom existant est suffisant
- Ne pas changer la détection automatique de la langue (basée sur `navigator.language` ou localStorage)
- Ne pas traduire le contenu astrologique dynamique (textes générés par LLM) — uniquement les textes UI statiques
- Ne pas migrer les textes i18n déjà en place dans les 10 fichiers existants

## Diagnostic Technique

### Types actuels à unifier

```typescript
// i18n/astrology.ts
export type AstrologyLang = "fr" | "en" | "es"

// i18n/dashboard.tsx
export type SupportedLocale = "fr" | "en" | "es"
```

Ces deux types sont identiques. Le type canonique sera `AppLocale` défini dans `i18n/types.ts` et réexporté par les fichiers existants.

### Pattern de détection de langue actuel (15+ occurrences)

```typescript
// Variante 1 — avec hook
const { lang } = useAstrologyLabels()
const t = translateDashboardPage(lang)

// Variante 2 — avec fonction utilitaire
const lang = detectLang()
const t = settingsTranslations.page[lang]
```

### Nouveau pattern cible

```typescript
const t = useTranslation('dashboard')   // retourne DashboardPageTranslation
const t = useTranslation('auth')        // retourne AuthTranslation
const t = useTranslation('common')      // retourne CommonTranslation
```

## Découpage en stories

### Chapitre 1 — Nouveaux fichiers i18n

- 52.1 Créer `i18n/auth.ts` — SignInForm, SignUpForm : labels, erreurs, boutons
- 52.2 Créer `i18n/common.ts` — textes transversaux : Header, états vides, actions génériques
- 52.3 Créer `i18n/navigation.ts` — labels de navigation (`ui/nav.ts`)

### Chapitre 2 — Infrastructure i18n

- 52.4 Créer `i18n/types.ts` + hook `useTranslation(namespace)` centralisé

### Chapitre 3 — Externalisation des erreurs de formulaire

- 52.5 Migrer les schemas Zod de SignInForm et SignUpForm vers des factory functions i18n

### Chapitre 4 — Migration des composants

- 52.6 Migrer Header, HeroHoroscopeCard, panneaux B2B/Admin vers les nouvelles clés i18n

## Risques et mitigations

### Risque 1 : Régression linguistique (texte manquant ou clé absente)

Mitigation :
- TypeScript strict sur les types de traduction — une clé manquante est une erreur de compilation
- Tester EN et ES après chaque story

### Risque 2 : Renommage cassant de `AstrologyLang` / `SupportedLocale`

Mitigation :
- Créer `AppLocale` comme nouveau type canonique dans `i18n/types.ts`
- `AstrologyLang` et `SupportedLocale` deviennent des alias : `export type AstrologyLang = AppLocale`
- Migration progressive story par story

### Risque 3 : Hook `useTranslation` trop couplé au système actuel

Mitigation :
- Le hook est un wrapper léger autour du système existant — pas de refonte
- Si un namespace n'a pas de fichier i18n, le hook échoue à la compilation (type-safe)

## Ordre recommandé d'implémentation

52.1 → 52.2 → 52.3 → 52.4 → 52.5 → 52.6

## Références

- [Source: frontend/src/i18n/]
- [Source: frontend/src/i18n/astrology.ts] (AstrologyLang, detectLang, useAstrologyLabels)
- [Source: frontend/src/i18n/dashboard.tsx] (SupportedLocale, pattern existant)
- [Source: frontend/src/components/SignInForm.tsx]
- [Source: frontend/src/components/SignUpForm.tsx]
- [Source: frontend/src/components/layout/Header.tsx]
- [Source: frontend/src/components/HeroHoroscopeCard.tsx]
- [Source: frontend/src/ui/nav.ts]
- [Source: _bmad-output/planning-artifacts/epics.md]
