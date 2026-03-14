# Epic 50: Créer la bibliothèque de composants UI primitifs réutilisables

Status: split-into-stories

## Contexte

L'Epic 49 a centralisé tous les design tokens CSS. Le codebase frontend ne possède cependant aucun composant UI partagé : chaque page et chaque section reconstruisent leurs propres boutons, champs, formulaires et cartes avec du HTML brut et des classes CSS locales.

Conséquences actuelles :
- Les boutons existent sous des formes disparates : `.hero-card__cta`, `button-ghost`, boutons inline dans les forms — sans cohérence visuelle ni comportement unifié
- Les `<input>` sont du HTML nu avec des classes CSS variables selon le contexte (BirthProfilePage, SignInForm, SignUpForm)
- `TimezoneSelect` est un composant select searchable non réutilisable, câblé uniquement sur les fuseaux horaires
- La logique de validation Zod est dupliquée avec des messages d'erreur hardcodés dans chaque formulaire
- `DeleteAccountModal` est le seul composant modal du produit mais non généralisé
- Le pattern `<div badge><Icon /></div><div content>...</div>` est répété identiquement dans `ShortcutCard` et `MiniInsightCard`
- Les squelettes de chargement sont des `<div style={{ width: "80%" }} />` hardcodés

Cette situation rend tout changement visuel transversal (ex: nouveau style de bouton, nouveau radius sur les inputs) nécessite de toucher 10+ fichiers.

## Objectif Produit

Créer une bibliothèque de composants UI primitifs qui :

1. Couvre tous les patterns UI répétés (bouton, input, select, form, modal, card, skeleton, badge)
2. Consomme exclusivement les design tokens de l'Epic 49
3. Expose une API de props simple et typée TypeScript
4. Permet de modifier l'apparence de tous les boutons du produit en changeant un seul fichier
5. Sert de fondation pour les Epics suivants (layouts, i18n, refactoring des pages)

## Non-objectifs

- Ne pas installer de librairie de composants externe (pas de shadcn/ui, MUI, Radix)
- Ne pas migrer les pages existantes vers les nouveaux composants dans cet epic (migration en Epic 51+)
- Ne pas créer de Storybook ou de documentation interactive
- Ne pas créer de composants spécifiques à un seul écran (ex: `AstroMoodBackground` reste dans components/astro)

## Diagnostic Technique

### Composants à créer

**Button** : remplace `.hero-card__cta`, les boutons de forms (SignIn, SignUp), les boutons admin — aucun composant `<Button>` partagé n'existe actuellement.

**Input / Field** : les `<input>` dans SignInForm, SignUpForm, BirthProfilePage sont du HTML nu sans abstraction de label/erreur/état.

**Select searchable** : `TimezoneSelect.tsx` + `TimezoneSelect.css` existent mais sont câblés uniquement sur les fuseaux horaires. À généraliser.

**Form + FormField** : la logique affichage-erreur-Zod est dupliquée dans chaque formulaire. Aucun wrapper Form partagé.

**Modal / Dialog** : `DeleteAccountModal.tsx` est le seul modal du produit, non généralisé.

**Card** : HeroHoroscopeCard, MiniInsightCard, ShortcutCard partagent le pattern glassmorphism (traité en 49.4) mais pas les props de composition.

**Skeleton** : inline `<div style={{ width: "80%", marginBottom: "0.5rem" }}/>` répété dans DashboardHoroscopeSummaryCard et possiblement ailleurs.

**Badge / IconBadge** : pattern `<div style={{ background: badgeColor }}><Icon /></div>` répété dans ShortcutCard et MiniInsightCard.

### Emplacement des composants

Tous les composants primitifs iront dans `frontend/src/components/ui/` avec un barrel export `frontend/src/components/ui/index.ts`.

## Principe de mise en oeuvre

- Créer chaque composant dans son propre dossier `frontend/src/components/ui/{ComponentName}/`
- Fichiers par composant : `{ComponentName}.tsx` + `{ComponentName}.css` + `{ComponentName}.test.tsx`
- Barrel export dans `frontend/src/components/ui/index.ts`
- Chaque composant consomme uniquement les tokens de `design-tokens.css`
- Ne pas migrer les pages dans cet epic — uniquement créer et tester les composants

## Découpage en stories

### Chapitre 1 — Actions et saisie

- 50.1 Créer le composant `<Button>` avec variants, tailles et états
- 50.2 Créer le composant `<Input>` / `<Field>` avec types, états et validation
- 50.3 Généraliser `TimezoneSelect` en composant `<Select>` searchable réutilisable

### Chapitre 2 — Formulaires

- 50.4 Créer le wrapper `<Form>` + `<FormField>` avec intégration Zod

### Chapitre 3 — Overlays et conteneurs

- 50.5 Créer le composant `<Modal>` / `<Dialog>` générique
- 50.6 Créer le composant `<Card>` avec variants et slots de composition

### Chapitre 4 — États et micro-composants

- 50.7 Créer les composants `<Skeleton>` et `<EmptyState>`
- 50.8 Créer les composants `<Badge>` et `<IconBadge>`

## Risques et mitigations

### Risque 1 : Sur-ingénierie des APIs de composants

Mitigation :
- Commencer par le minimum nécessaire pour les usages actuels du codebase
- Ne pas créer de props pour des cas hypothétiques futurs
- Chaque prop doit avoir au moins 2 usages concrets identifiés dans le code existant

### Risque 2 : Régression sur les composants existants

Mitigation :
- Ne pas modifier les composants existants dans cet epic
- Les nouveaux composants coexistent avec l'ancien code jusqu'à la migration (Epic 51+)

### Risque 3 : Incohérence visuelle entre nouveaux et anciens composants

Mitigation :
- Les nouveaux composants utilisent les mêmes tokens que les composants existants
- Review visuelle après chaque story

### Risque 4 : Duplication du composant Select

Mitigation :
- Le nouveau composant `<Select>` générique doit absorber TimezoneSelect sans le supprimer immédiatement
- TimezoneSelect sera migré vers `<Select>` dans l'Epic 51+

## Ordre recommandé d'implémentation

- 50.1 → 50.2 → 50.3 → 50.4 → 50.5 → 50.6 → 50.7 → 50.8

Les stories 50.1 et 50.2 sont des prérequis pour 50.4 (FormField utilise Button et Input).

## Références

- [Source: frontend/src/components/SignInForm.tsx]
- [Source: frontend/src/components/SignUpForm.tsx]
- [Source: frontend/src/components/TimezoneSelect.tsx]
- [Source: frontend/src/components/TimezoneSelect.css]
- [Source: frontend/src/components/settings/DeleteAccountModal.tsx]
- [Source: frontend/src/components/MiniInsightCard.tsx]
- [Source: frontend/src/components/ShortcutCard.tsx]
- [Source: frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx]
- [Source: frontend/src/styles/design-tokens.css] (Epic 49)
- [Source: frontend/src/styles/utilities.css] (Epic 49)
- [Source: _bmad-output/planning-artifacts/epic-49-design-tokens-css-centralises.md]
- [Source: _bmad-output/planning-artifacts/epics.md]
