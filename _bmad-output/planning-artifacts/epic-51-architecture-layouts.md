# Epic 51: Créer une architecture de layouts composables et hiérarchisés

Status: split-into-stories

## Contexte

L'Epic 16 a posé une première structure routing/layouts avec React Router. L'`AppShell.tsx` actuel gère tout dans un seul composant monolithique : il inclut `<Header>`, `<Sidebar>`, `<BottomNav>` et un `<main>` sans slots. Les pages gèrent elles-mêmes leur propre padding, max-width et structure interne de manière incohérente.

Problèmes identifiés :
- `AppShell.tsx` mélange la structure de navigation et la mise en page du contenu
- Aucun `AuthLayout` — les pages SignIn/SignUp partagent le même shell que les pages authentifiées
- Le Chat utilise une mise en page deux colonnes gérée localement dans `ChatPage.tsx`
- Le wizard de consultation gère sa barre de progression localement dans `ConsultationWizardPage.tsx`
- `SettingsPage.tsx` gère ses onglets localement avec `SettingsTabs.tsx` sans layout dédié
- `AdminPage.tsx` gère son layout séparément via `AdminPage.css`
- Chaque page recalcule son propre `max-width`, `padding`, `margin: 0 auto`

Cette situation rend difficile de changer la structure visuelle d'une catégorie de pages sans toucher chaque page individuellement.

## Objectif Produit

Créer une hiérarchie de layouts composables qui :

1. Sépare clairement la navigation globale (AppLayout) de la mise en page du contenu (PageLayout)
2. Isole les pages d'authentification dans un AuthLayout sans navigation
3. Fournit des layouts spécialisés réutilisables pour Chat, Wizard, Settings et Admin
4. Centralise les décisions de max-width, padding et grille dans les layouts — les pages ne gèrent plus ça
5. Consomme les tokens CSS de l'Epic 49

## Non-objectifs

- Ne pas refondre le routing lui-même (`router.tsx`, `routes.tsx`) sauf ajustements mineurs pour brancher les nouveaux layouts
- Ne pas modifier la logique métier des pages (données, hooks, API calls)
- Ne pas migrer le contenu visuel des pages vers les composants UI de l'Epic 50 dans cet epic

## Diagnostic Technique

### Structure actuelle

```
AppShell.tsx               ← monolithique : Header + Sidebar + BottomNav + <main>
  └── <main className="app-shell-main panel">
        └── <Outlet />     ← toutes les pages atterrissent ici
```

Pages avec layout local :
- `ChatPage.tsx` : deux colonnes (liste + conversation)
- `ConsultationWizardPage.tsx` : barre de progression
- `SettingsPage.tsx` : onglets via `SettingsTabs.tsx`
- `AdminPage.tsx` : layout admin via `AdminPage.css`
- Pages auth (`HomePage.tsx`) : passent par AppShell alors qu'elles n'ont pas besoin de navigation

### Structure cible

```
RootLayout                 ← fond, thème, providers globaux
  ├── AuthLayout           ← centré, sans navigation (SignIn, SignUp, HomePage?)
  └── AppLayout            ← AppShell refactorisé (Header + Sidebar + BottomNav)
        └── PageLayout     ← container centré, max-width, slots header/main/aside
              ├── (standard pages : Dashboard, Horoscope, NatalChart, Astrologers...)
              ├── TwoColumnLayout    ← Chat (liste + conversation)
              ├── WizardLayout       ← ConsultationWizard
              ├── SettingsLayout     ← onglets + sous-pages
              └── AdminLayout        ← panneau admin
```

### Emplacement des layouts

Tous les layouts iront dans `frontend/src/layouts/` — dossier à créer.

## Principe de mise en oeuvre

- Créer les nouveaux layouts dans `frontend/src/layouts/`
- Refactoriser `AppShell.tsx` en `AppLayout` sans le supprimer (renommer ou exporter depuis AppShell)
- Mettre à jour `routes.tsx` pour utiliser les nouveaux layouts comme wrappers de routes
- Ne pas modifier les composants `<Header>`, `<Sidebar>`, `<BottomNav>` — ils restent inchangés

## Découpage en stories

### Chapitre 1 — Fondation

- 51.1 Créer `RootLayout` et `AuthLayout` — fond, providers et isolation des pages auth

### Chapitre 2 — Layout principal

- 51.2 Refactoriser `AppShell` → `AppLayout` + créer `PageLayout` avec slots

### Chapitre 3 — Layouts spécialisés

- 51.3 Créer `TwoColumnLayout` (Chat) et `WizardLayout` (ConsultationWizard)
- 51.4 Créer `SettingsLayout` et `AdminLayout`

### Chapitre 4 — Migration

- 51.5 Migrer toutes les pages vers les nouveaux layouts et valider la non-régression

## Risques et mitigations

### Risque 1 : Régression de routing

Mitigation :
- Modifier `routes.tsx` de manière chirurgicale, route par route
- Tester chaque route après migration
- `AppShell.tsx` n'est pas supprimé avant que toutes les pages soient migrées

### Risque 2 : Perte des guards d'authentification

Mitigation :
- `AuthGuard`, `RoleGuard`, `RootRedirect` dans `app/guards/` ne sont pas modifiés
- Les layouts ne gèrent pas l'authentification — les guards restent dans `routes.tsx`

### Risque 3 : CSS de layout dupliqué entre AppShell et AppLayout

Mitigation :
- AppShell est refactorisé (pas remplacé) — les classes CSS existantes restent valides
- Les nouveaux layouts utilisent les mêmes classes CSS que l'AppShell actuel

## Ordre recommandé d'implémentation

- 51.1 → 51.2 → 51.3 → 51.4 → 51.5

## Références

- [Source: frontend/src/components/AppShell.tsx]
- [Source: frontend/src/components/layout/Header.tsx]
- [Source: frontend/src/components/layout/Sidebar.tsx]
- [Source: frontend/src/components/layout/BottomNav.tsx]
- [Source: frontend/src/components/layout/EnterpriseLayout.tsx]
- [Source: frontend/src/app/router.tsx]
- [Source: frontend/src/app/routes.tsx]
- [Source: frontend/src/app/guards/]
- [Source: frontend/src/pages/ChatPage.tsx]
- [Source: frontend/src/pages/ConsultationWizardPage.tsx]
- [Source: frontend/src/pages/SettingsPage.tsx]
- [Source: frontend/src/pages/AdminPage.tsx]
- [Source: frontend/src/App.css] (classes .app-shell-*)
- [Source: _bmad-output/planning-artifacts/epics.md]
