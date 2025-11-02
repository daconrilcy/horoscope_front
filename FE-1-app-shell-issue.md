# Issue: FE-1 — App Shell & Routage

## Objectif

Mettre en place l'architecture de routage robuste et scalable avec providers globaux optimisés, layouts public/privé, protection des routes avec gestion de l'hydratation, et code splitting pour les pages privées.

## Tâches

### 1.1 — Providers (React Query, Router, Toaster)

- [x] Installer `@tanstack/react-query`, `@tanstack/react-query-devtools` et `sonner`
- [x] Configurer `QueryClient` avec options "safe by default" :
  - `retry: (failureCount, error) => isNetworkError(error) && failureCount < 2`
  - `staleTime: 30_000` (30s) pour limiter le flicker
- [x] Intégrer `QueryClientProvider` dans `AppProviders.tsx`
- [x] Monter `ReactQueryDevtools` uniquement en dev
- [x] Intégrer `Toaster` de sonner avec `richColors` et `position` définis
- [x] Créer helpers `toastSuccess` et `toastError` pour unifier les usages
- [x] Maintenir `<React.StrictMode>` dans `main.tsx`

### 1.2 — Router + Routes protégées (Data Router)

- [x] Migrer vers Data Router : `createBrowserRouter` + `RouterProvider` (au lieu de BrowserRouter)
- [x] Créer `PublicLayout` dans `src/app/layouts/PublicLayout.tsx` avec `<Outlet/>` et barre de navigation
- [x] Créer `PrivateLayout` dans `src/app/layouts/PrivateLayout.tsx` avec `<Outlet/>` et barre de navigation
- [x] Créer les pages basiques :
  - `src/pages/home/index.tsx`
  - `src/pages/login/index.tsx`
  - `src/pages/signup/index.tsx`
  - `src/pages/app/dashboard/index.tsx` (avec code splitting lazy)
  - `src/pages/legal/tos/index.tsx` (placeholder)
  - `src/pages/legal/privacy/index.tsx` (placeholder)
  - `src/pages/NotFound/index.tsx` (404)
- [x] Créer `src/shared/config/routes.ts` pour centraliser les chemins
- [x] Implémenter `ScrollRestoration` (composant personnalisé)
- [x] Mettre à jour `router.tsx` pour utiliser createBrowserRouter avec layouts et lazy loading

### 1.3 — RouteGuard amélioré

- [x] Améliorer `RouteGuard` pour attendre l'hydratation du store Zustand
- [x] Ajouter état `_hasHydrated` dans `authStore` pour détecter fin d'hydratation
- [x] Utiliser token depuis store (mémoire) uniquement
- [x] Éviter boucles de redirection : ne pas re-naviguer si déjà sur `/login`
- [x] Mémoriser `redirectAfterLogin` (déjà dans sessionStorage via AppProviders)

### 1.4 — ErrorBoundary amélioré

- [x] Positionner ErrorBoundary global autour de l'app dans AppProviders
- [x] Ajouter support `resetKeys` pour reset automatique en changeant de page
- [x] Afficher `request_id` si disponible (préparé pour intégration future)

### 1.5 — Helpers et conventions

- [x] Créer hook `useTitle(title: string)` pour mettre à jour `document.title`
- [x] Utiliser `useTitle` dans toutes les pages
- [x] Centraliser toutes les routes dans `src/shared/config/routes.ts`

## Routes

### Routes publiques

- `/` — Page d'accueil
- `/login` — Page de connexion
- `/signup` — Page d'inscription
- `/legal/tos` — Conditions d'utilisation (placeholder)
- `/legal/privacy` — Politique de confidentialité (placeholder)
- `*` (404) — Page non trouvée

### Routes privées (nécessitent JWT)

- `/app/dashboard` — Tableau de bord (lazy loaded)
- `/app/horoscope` — À venir
- `/app/chat` — À venir
- `/app/account` — À venir

**Note** : Toutes les routes `/app/*` sont protégées par `RouteGuard` et redirigent vers `/login` si pas de JWT.

## Découpage des layouts

### PublicLayout
- Utilisé pour toutes les routes publiques (`/`, `/login`, `/signup`, `/legal/*`)
- Inclut une barre de navigation simple avec liens vers Accueil, Connexion, Inscription
- Utilise `<Outlet/>` pour afficher le contenu des pages enfants

### PrivateLayout
- Utilisé pour toutes les routes privées (`/app/*`)
- Inclut une barre de navigation avec lien Dashboard et bouton Déconnexion
- Utilise `<Outlet/>` pour afficher le contenu des pages enfants

## Scope de la PR

Cette PR se concentre uniquement sur :
- ✅ Architecture de routage (Data Router)
- ✅ Providers globaux (React Query, Toaster)
- ✅ Layouts public/privé
- ✅ Pages basiques (placeholders)
- ✅ Protection des routes avec gestion d'hydratation
- ✅ Code splitting pour pages privées

**Exclut** :
- ❌ Client HTTP (déjà implémenté dans FE-0.4)
- ❌ Paywall (déjà implémenté dans FE-0.4)
- ❌ Authentification réelle (login/signup) — sera dans une PR future
- ❌ Intégration backend — sera dans des PRs futures

## Critères d'acceptation

- [x] QueryClientProvider actif avec config "safe by default" (retry NetworkError uniquement, staleTime 30s)
- [x] ReactQueryDevtools monté uniquement en dev
- [x] Toaster (sonner) monté une fois avec richColors/position, helpers toastSuccess/toastError
- [x] React.StrictMode maintenu dans main.tsx
- [x] ErrorBoundary global avec resetKeys sur pathname
- [x] Data Router (createBrowserRouter + RouterProvider) au lieu de BrowserRouter
- [x] PublicLayout pour routes publiques (/, /login, /signup, /legal/*) avec Outlet et nav
- [x] PrivateLayout pour routes privées (/app/*) avec Outlet et nav
- [x] RouteGuard :
  - Attend hydratation du store avant décision
  - Redirige vers /login si pas de JWT après hydratation
  - Ne redirige pas si déjà sur /login
  - Mémorise redirectAfterLogin
- [x] Route * (404) affiche NotFound
- [x] ScrollRestoration fonctionne
- [x] Code splitting (lazy) pour pages /app (au moins Dashboard)
- [x] Routes centralisées dans src/shared/config/routes.ts
- [x] Hook useTitle pour document.title par page
- [x] Tous les tests passent (guard/hydratation, layouts, navigation, 404, providers, toaster)
- [x] Lint/typecheck OK

## Livrables

- Providers globaux optimisés (React Query + Toaster + helpers)
- Data Router avec layouts public/privé fonctionnels
- RouteGuard robuste avec gestion hydratation
- Pages basiques créées avec code splitting
- ErrorBoundary amélioré avec reset automatique
- Tests couvrant tous les cas critiques
- Architecture scalable prête pour les features futures

## Labels

`feature`, `routing`, `providers`, `layout`, `milestone-fe-1`

