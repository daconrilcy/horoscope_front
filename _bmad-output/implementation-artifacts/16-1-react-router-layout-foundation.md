# Story 16.1: React Router et Layout Foundation

Status: done

## Story

As a utilisateur de l'application horoscope,
I want que l'application utilise React Router avec des URLs propres et un layout global cohérent,
So that je puisse naviguer avec back/forward, partager des liens directs, et avoir une interface structurée.

## Contexte

L'application actuelle utilise un state local dans `App.tsx` pour gérer la navigation par boutons. Cela empêche :
- Les URLs significatives (tout est sur `/`)
- Le back/forward du navigateur
- Les deep links et le partage de pages
- Une structure de layout cohérente

Cette story met en place les fondations : React Router 6+ et le nouveau AppShell.

## Scope

### In-Scope
- Installation et configuration de React Router 6+
- Création du système de routes avec définitions
- Guards d'authentification (AuthGuard) et de rôle (RoleGuard)
- Nouveau AppShell avec structure header/sidebar/main
- Navigation responsive (desktop sidebar, mobile bottom nav)
- Migration de `App.tsx` vers RouterProvider
- Redirections : `/` → `/dashboard` (auth) ou `/login` (non auth)

### Out-of-Scope
- Création des nouvelles pages (stories suivantes)
- Refonte du chat messenger (story 16.3)
- Nouvelles fonctionnalités métier

## Acceptance Criteria

### AC1: Routes fonctionnelles
**Given** un utilisateur naviguant dans l'application
**When** il change de section
**Then** l'URL change pour refléter la page courante
**And** les boutons back/forward du navigateur fonctionnent

### AC2: Protection des routes
**Given** un utilisateur non authentifié
**When** il accède à une URL protégée (ex: `/dashboard`)
**Then** il est redirigé vers `/login`
**And** après connexion, il est redirigé vers la page demandée

### AC3: Contrôle des rôles
**Given** un utilisateur sans rôle admin/ops
**When** il accède à `/admin`
**Then** il est redirigé vers `/dashboard`

### AC4: Layout responsive
**Given** un utilisateur sur desktop
**When** il consulte l'application
**Then** il voit un sidebar de navigation à gauche et le contenu à droite

**Given** un utilisateur sur mobile
**When** il consulte l'application
**Then** il voit une navigation en bas de l'écran (bottom nav)

### AC5: Rétrocompatibilité
**Given** les pages existantes (NatalChartPage, ChatPage, etc.)
**When** elles sont intégrées au nouveau router
**Then** elles fonctionnent sans régression

## Tasks

- [x] Task 1: Installer et configurer React Router (AC: #1)
  - [x] 1.1 `npm install react-router-dom@6`
  - [x] 1.2 Créer `src/app/router.tsx` avec createBrowserRouter
  - [x] 1.3 Créer `src/app/routes.tsx` avec RouteObject[]

- [x] Task 2: Créer les guards (AC: #2, #3)
  - [x] 2.1 Créer `src/app/guards/AuthGuard.tsx`
  - [x] 2.2 Créer `src/app/guards/RoleGuard.tsx`
  - [x] 2.3 Implémenter redirect avec `returnTo` query param

- [x] Task 3: Refactorer AppShell (AC: #4)
  - [x] 3.1 Créer `src/components/layout/Header.tsx`
  - [x] 3.2 Créer `src/components/layout/Sidebar.tsx`
  - [x] 3.3 Créer `src/components/layout/BottomNav.tsx`
  - [x] 3.4 Refactorer `src/components/AppShell.tsx` avec Outlet

- [x] Task 4: Migrer App.tsx (AC: #1, #5)
  - [x] 4.1 Remplacer state navigation par RouterProvider
  - [x] 4.2 Configurer routes pour pages existantes
  - [x] 4.3 Ajouter redirections `/` → `/dashboard` ou `/login`

- [x] Task 5: Tests (AC: tous)
  - [x] 5.1 Test navigation entre routes
  - [x] 5.2 Test AuthGuard redirect
  - [x] 5.3 Test RoleGuard redirect
  - [x] 5.4 Test back/forward navigation

## Dev Notes

### Structure de fichiers à créer

```
frontend/src/
├── app/
│   ├── router.tsx        # createBrowserRouter + RouterProvider
│   ├── routes.tsx        # Route definitions
│   └── guards/
│       ├── AuthGuard.tsx
│       └── RoleGuard.tsx
├── components/
│   └── layout/
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── BottomNav.tsx
```

### Routes initiales

```typescript
// routes.tsx
export const routes: RouteObject[] = [
  { path: "/login", element: <LoginPage /> },
  { path: "/register", element: <RegisterPage /> },
  {
    element: <AuthGuard><AppShell /></AuthGuard>,
    children: [
      { path: "/", element: <Navigate to="/dashboard" /> },
      { path: "/dashboard", element: <DashboardPage /> },
      { path: "/natal", element: <NatalChartPage /> },
      { path: "/chat", element: <ChatPage /> },
      { path: "/settings/*", element: <SettingsPage /> },
      // ... autres routes
      {
        path: "/admin/*",
        element: <RoleGuard roles={["ops", "admin"]}><AdminPage /></RoleGuard>
      }
    ]
  }
]
```

### AuthGuard pattern

```typescript
function AuthGuard({ children }: { children: ReactNode }) {
  const token = useAccessTokenSnapshot()
  const location = useLocation()
  
  if (!token) {
    return <Navigate to={`/login?returnTo=${location.pathname}`} replace />
  }
  return <>{children}</>
}
```

### Dépendance

```bash
npm install react-router-dom@6
```

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Frontend Architecture]
- React Router 6 docs: https://reactrouter.com/en/main

## Dev Agent Record

### Agent Model Used
Claude Opus 4.5 (Cursor)

### Debug Log References
N/A

### Completion Notes List
- React Router 6.30.3 installé et configuré avec future flags (v7_relativeSplatPath, v7_startTransition)
- Guards implémentés avec protection Open Redirect corrigée
- Layout responsive avec sidebar desktop et bottom nav mobile
- 14 tests de routing passent (navigation, AuthGuard, RoleGuard, back/forward)
- Page 404 ajoutée pour routes invalides
- Navigation items centralisés dans navItems.ts
- AdminLayout et EnterpriseLayout extraits dans des fichiers séparés

### File List

**Fichiers créés:**
- `frontend/src/app/router.tsx` - Router principal avec createBrowserRouter et future flags
- `frontend/src/app/routes.tsx` - Définitions des routes avec guards
- `frontend/src/app/guards/AuthGuard.tsx` - Guard d'authentification avec returnTo
- `frontend/src/app/guards/RoleGuard.tsx` - Guard de rôle avec loading state
- `frontend/src/app/guards/RootRedirect.tsx` - Redirection / vers dashboard ou login
- `frontend/src/app/guards/index.ts` - Barrel export des guards
- `frontend/src/components/layout/Header.tsx` - Header avec logout
- `frontend/src/components/layout/Sidebar.tsx` - Navigation sidebar desktop
- `frontend/src/components/layout/BottomNav.tsx` - Navigation mobile bottom
- `frontend/src/components/layout/AdminLayout.tsx` - Layout admin avec Outlet
- `frontend/src/components/layout/EnterpriseLayout.tsx` - Layout enterprise avec Outlet
- `frontend/src/components/layout/navItems.ts` - Configuration centralisée des items de navigation
- `frontend/src/components/layout/index.ts` - Barrel export des layouts
- `frontend/src/pages/NotFoundPage.tsx` - Page 404
- `frontend/src/tests/router.test.tsx` - Tests complets du routing (14 tests)
- `frontend/src/tests/test-utils.tsx` - Utilitaires de test avec router

**Fichiers modifiés:**
- `frontend/package.json` - Ajout react-router-dom@6.30.3
- `frontend/package-lock.json` - Lockfile mis à jour
- `frontend/src/App.tsx` - Simplifié pour utiliser AppRouter
- `frontend/src/main.tsx` - Utilise AppRouter avec providers
- `frontend/src/App.css` - Styles du layout (header, sidebar, bottom nav, admin/enterprise layouts)
- `frontend/src/components/AppShell.tsx` - Refactoré avec Outlet et composants layout
- `frontend/src/components/SignInForm.tsx` - Navigation router + fix open redirect
- `frontend/src/components/SignUpForm.tsx` - Navigation router + fix open redirect
- `frontend/src/tests/App.test.tsx` - Adapté pour router
- `frontend/src/pages/BirthProfilePage.tsx` - Migré vers useNavigate react-router-dom
- `frontend/src/pages/ChatPage.tsx` - Migré vers useParams/useNavigate (conversationId via URL)
- `frontend/src/pages/NatalChartPage.tsx` - Adapté pour compatibilité router
- `frontend/src/tests/BirthProfilePage.test.tsx` - Adapté pour environnement router
- `frontend/src/tests/ChatPage.test.tsx` - Adapté pour environnement router
- `frontend/src/tests/SignInForm.test.tsx` - Adapté pour environnement router
- `frontend/src/tests/SignUpForm.test.tsx` - Adapté pour environnement router
- `frontend/src/tests/astrology-i18n.test.ts` - Adapté pour environnement router
- `frontend/src/i18n/astrology.ts` - Ajout detectLang utilisé par ChatPage
- `nginx/nginx.conf` - Ajout fallback SPA (`try_files $uri $uri/ /index.html`) requis pour React Router en production

**Note d'implémentation (routes.tsx scope):** `routes.tsx` référence des composants créés par les stories suivantes (16-2 à 16-7 : DashboardPage, ConsultationsPage, AstrologersPage, panels admin/enterprise, etc.). Cette story a été implémentée après les stories 16-2 à 16-5 pour intégrer toutes les routes dans un seul fichier cohérent. Les composants des stories précédentes sont des prérequis fonctionnels de ce fichier.

### Change Log
| Date | Change | Author |
|------|--------|--------|
| 2026-02-22 | Implémentation complète + code review fixes | Claude Opus 4.5 |
| 2026-02-23 | Code review fixes: NotFoundPage HTML, router.tsx dead code, BottomNav rôles, Header UX, File List complétée | Claude Sonnet 4.6 |
