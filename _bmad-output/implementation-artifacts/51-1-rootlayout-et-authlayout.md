# Story 51.1: Créer RootLayout et AuthLayout — fond, providers et isolation des pages auth

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux un `RootLayout` portant le fond visuel global et un `AuthLayout` centrant les pages d'authentification,
afin que les pages `/login` et `/register` bénéficient du fond premium et d'un layout centré sans navigation.

## Acceptance Criteria

1. `frontend/src/layouts/RootLayout.tsx` existe et encapsule `StarfieldBackground` + la classe `app-bg` avec `app-bg-container`.
2. `frontend/src/layouts/AuthLayout.tsx` existe, étend visuellement `RootLayout` et centre le contenu dans un conteneur de largeur max 480px avec `<Outlet />`.
3. Les routes `/login` et `/register` dans `routes.tsx` sont wrappées par `AuthLayout`.
4. Les pages de login et register bénéficient du fond `StarfieldBackground` et du gradient premium.
5. `AuthLayout` n'affiche aucun élément de navigation (Header, Sidebar, BottomNav absents).
6. `AppShell.tsx` n'est pas modifié dans cette story — il coexiste avec les nouveaux layouts.
7. Les tests existants relatifs aux routes auth passent sans modification.

## Tasks / Subtasks

- [ ] Tâche 1 : Créer `frontend/src/layouts/` (AC: 1)
  - [ ] Créer le dossier `frontend/src/layouts/`
  - [ ] Créer `frontend/src/layouts/index.ts` (barrel export)

- [ ] Tâche 2 : Créer `RootLayout.tsx` (AC: 1, 4)
  - [ ] Lire `AppShell.tsx` pour identifier les éléments de fond (StarfieldBackground, app-bg, app-bg-container)
  - [ ] `RootLayout` rend : `<div className="app-shell app-bg"><StarfieldBackground /><div className="app-bg-container"><Outlet /></div></div>`
  - [ ] Exporter depuis `frontend/src/layouts/index.ts`

- [ ] Tâche 3 : Créer `AuthLayout.tsx` (AC: 2, 5)
  - [ ] `AuthLayout` rend un conteneur centré : `<div className="auth-layout"><Outlet /></div>`
  - [ ] Ajouter dans `App.css` ou `frontend/src/layouts/AuthLayout.css` les styles `.auth-layout`
  - [ ] Styles : `display: flex`, `align-items: center`, `justify-content: center`, `min-height: 100vh`, `padding: var(--space-6)`
  - [ ] Conteneur interne : `max-width: 480px`, `width: 100%`

- [ ] Tâche 4 : Mettre à jour `routes.tsx` (AC: 3, 4, 5)
  - [ ] Créer un groupe de routes auth wrappé par `<RootLayout>` → `<AuthLayout>`
  - [ ] Déplacer `/login` et `/register` dans ce groupe
  - [ ] La route racine `<AuthGuard><AppShell />` reste inchangée

- [ ] Tâche 5 : Validation (AC: 6, 7)
  - [ ] Vérifier que `/login` et `/register` affichent le fond premium + contenu centré
  - [ ] Vérifier que les pages authentifiées restent inchangées
  - [ ] Exécuter `npm run test` — tous les tests passent

## Dev Notes

### Contexte technique

**Prérequis** : Aucun prérequis dans les epics 49/50 — cette story est indépendante du point de vue des composants.

**ThemeProvider** applique la classe `.dark` sur `document.documentElement` (vérifié dans `ThemeProvider.tsx` ligne 58). Les classes CSS de thème fonctionnent donc correctement quelle que soit la position dans l'arbre React.

**Providers** : `AppProviders` (`state/providers.tsx`) encapsule `QueryClientProvider` + `ThemeProvider`. Il est appliqué dans `App.tsx` au-dessus du router — les layouts n'ont pas à gérer les providers.

### Structure actuelle de routes.tsx

```typescript
// Actuellement
{ path: "/login", element: <LoginPage /> },          // pas de layout
{ path: "/register", element: <RegisterPage /> },     // pas de layout
{ element: <AuthGuard><AppShell /></AuthGuard>, children: [...] }
```

### Structure cible de routes.tsx

```typescript
// Après story 51.1
{
  element: <RootLayout />,
  children: [
    {
      element: <AuthLayout />,
      children: [
        { path: "/login", element: <LoginPage /> },
        { path: "/register", element: <RegisterPage /> },
      ]
    },
    {
      element: <AuthGuard><AppShell /></AuthGuard>,
      children: [...]  // routes protégées — inchangées
    }
  ]
}
```

**Attention** : `RootRedirect` sur `/` reste hors du groupe — il redirige avant d'afficher quoi que ce soit.

### `StarfieldBackground`

Ce composant est actuellement dans `AppShell.tsx`. Quand `RootLayout` englobe les routes auth, `StarfieldBackground` sera rendu pour les pages auth **et** pour AppShell. Pour éviter un doublon dans AppShell, retirer `StarfieldBackground` de `AppShell.tsx` et laisser `RootLayout` le gérer.

**Attention** : Si `RootLayout` englobe aussi `AppShell`, retirer `StarfieldBackground` d'`AppShell`. Si `RootLayout` est un niveau parallèle à `AppShell` (auth seulement), garder `StarfieldBackground` dans `AppShell`. **Recommandation** : faire de `RootLayout` le wrapper commun des deux branches (auth + app) pour centraliser le fond.

### CSS AuthLayout

```css
/* AuthLayout.css */
.auth-layout {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100dvh;
  padding: var(--space-6);
}

.auth-layout__container {
  width: 100%;
  max-width: 480px;
}
```

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Créer | `frontend/src/layouts/RootLayout.tsx` |
| Créer | `frontend/src/layouts/AuthLayout.tsx` |
| Créer | `frontend/src/layouts/AuthLayout.css` |
| Créer | `frontend/src/layouts/index.ts` |
| Modifier | `frontend/src/app/routes.tsx` |
| Modifier | `frontend/src/components/AppShell.tsx` (retrait StarfieldBackground si RootLayout commun) |

### Project Structure Notes

- Nouveau dossier `frontend/src/layouts/` à créer — ne pas mettre les layouts dans `components/`
- `StarfieldBackground` reste dans `frontend/src/components/` — `RootLayout` l'importe de là
- `LoginPage` et `RegisterPage` restent inline dans `routes.tsx` (fonctions locales) — pas de migration dans cette story

### References

- [Source: frontend/src/components/AppShell.tsx]
- [Source: frontend/src/app/routes.tsx]
- [Source: frontend/src/state/providers.tsx]
- [Source: frontend/src/state/ThemeProvider.tsx]
- [Source: frontend/src/components/StarfieldBackground.tsx]
- [Source: frontend/src/styles/backgrounds.css] (classes app-bg, app-bg-container)
- [Source: _bmad-output/planning-artifacts/epic-51-architecture-layouts.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
