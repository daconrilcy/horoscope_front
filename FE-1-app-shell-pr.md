# PR: FE-1 — App Shell & Routage

**Titre**: FE-1 — App Shell & Routage (Robuste & Scalable)

## Portée & Alignement

Implémente l'**architecture de routage robuste et scalable** avec providers globaux optimisés, layouts public/privé, protection des routes avec gestion de l'hydratation, et code splitting pour les pages privées.

## Endpoints utilisés

Cette PR ne modifie pas les endpoints utilisés. Elle prépare l'infrastructure pour les futures intégrations backend.

## Contraintes respectées

- ✅ Data Router (createBrowserRouter + RouterProvider) au lieu de BrowserRouter
- ✅ QueryClient configuré avec options "safe by default" (retry NetworkError uniquement, staleTime 30s)
- ✅ ReactQueryDevtools monté uniquement en dev
- ✅ Toaster (sonner) monté une fois avec richColors/position, helpers toastSuccess/toastError
- ✅ ErrorBoundary global avec resetKeys sur pathname
- ✅ RouteGuard attend hydratation du store avant décision
- ✅ RouteGuard redirige vers /login si pas de JWT après hydratation
- ✅ RouteGuard évite boucles de redirection (ne redirige pas si déjà sur /login)
- ✅ RouteGuard mémorise redirectAfterLogin
- ✅ PublicLayout pour routes publiques avec Outlet et navigation
- ✅ PrivateLayout pour routes privées avec Outlet et navigation
- ✅ Code splitting (lazy) pour pages /app (Dashboard)
- ✅ ScrollRestoration fonctionne
- ✅ Routes centralisées dans src/shared/config/routes.ts
- ✅ Hook useTitle pour document.title par page

## Tests (local-only)

- **Unit/int** :
  - `src/shared/hooks/useTitle.test.ts` → Tests pour useTitle
  - `src/app/layouts/PublicLayout.test.tsx` → Tests pour PublicLayout (Outlet, navigation)
  - `src/app/layouts/PrivateLayout.test.tsx` → Tests pour PrivateLayout (Outlet, navigation, logout)
  - `src/stores/authStore.test.ts` → Tests pour hydratation _hasHydrated
  - `src/app/router.test.tsx` → Tests pour route 404
- **Commandes** : `npm run dev`, `npm run test`, `npm run lint`

## Vérifications

- [x] Check-list **Quality Gates Frontend** entièrement cochée
- [x] Tous les tests unitaires passent
- [x] TypeScript strict : `npx tsc --noEmit` → **0 erreur** (sauf erreurs préexistantes dans client.test.ts)
- [x] Lint : quelques warnings mineurs (principalement dans les tests mocks)
- [x] Architecture conforme au plan

## Détails techniques

### Providers globaux

- **QueryClientProvider** : Configuré avec retry uniquement sur NetworkError (max 2), staleTime 30s
- **ReactQueryDevtools** : Monté uniquement en dev (import.meta.env.DEV)
- **Toaster (sonner)** : Monté avec richColors et position top-right
- **Helpers toast** : `toast.success()`, `toast.error()`, `toast.info()`, `toast.warning()`
- **ErrorBoundary** : Global avec resetKeys sur pathname pour reset automatique

### Data Router

- **Migration** : De BrowserRouter vers createBrowserRouter + RouterProvider
- **Avantages** : Prêt pour loaders/actions/errorElements futurs sans refacto
- **Structure** : AppShell → PublicLayout/PrivateLayout → Pages

### RouteGuard amélioré

- **Hydratation** : Attend `_hasHydrated` avant de décider (évite redirections intempestives)
- **Token** : Lit depuis store (mémoire), pas directement localStorage
- **RedirectAfterLogin** : Mémorise dans sessionStorage via RouteGuard

### Layouts

- **PublicLayout** : Navigation avec liens Accueil, Connexion, Inscription
- **PrivateLayout** : Navigation avec lien Dashboard et bouton Déconnexion
- **Outlet** : Utilisé pour afficher le contenu des pages enfants

### Code splitting

- **Dashboard** : Lazy loaded avec React.lazy() + Suspense
- **Fallback** : PageLoader simple pendant le chargement

### Routes

- **Centralisées** : Toutes les routes dans `src/shared/config/routes.ts`
- **Types** : `PublicRoute` et `PrivateRoute` pour type safety

## Captures des pages de base

Les pages suivantes ont été créées (placeholders) :

- ✅ **HomePage** (`/`) : Page d'accueil avec liens vers Login/Signup
- ✅ **LoginPage** (`/login`) : Formulaire de connexion (placeholder)
- ✅ **SignupPage** (`/signup`) : Formulaire d'inscription (placeholder)
- ✅ **DashboardPage** (`/app/dashboard`) : Tableau de bord (placeholder, lazy loaded)
- ✅ **TermsOfServicePage** (`/legal/tos`) : Conditions d'utilisation (placeholder)
- ✅ **PrivacyPolicyPage** (`/legal/privacy`) : Politique de confidentialité (placeholder)
- ✅ **NotFoundPage** (`*`) : Page 404 avec lien retour accueil

## Checklist DoD (Definition of Done)

### Fonctionnel
- [x] QueryClientProvider actif avec config "safe by default"
- [x] ReactQueryDevtools monté uniquement en dev
- [x] Toaster (sonner) monté et fonctionnel
- [x] ErrorBoundary global avec resetKeys
- [x] Data Router (createBrowserRouter + RouterProvider)
- [x] PublicLayout pour routes publiques avec Outlet et nav
- [x] PrivateLayout pour routes privées avec Outlet et nav
- [x] RouteGuard avec hydratation
- [x] RouteGuard redirige vers /login si pas de JWT
- [x] RouteGuard évite boucles de redirection
- [x] RouteGuard mémorise redirectAfterLogin
- [x] Route 404 affiche NotFound
- [x] ScrollRestoration fonctionne
- [x] Code splitting (lazy) pour Dashboard
- [x] Routes centralisées dans routes.ts
- [x] Hook useTitle pour document.title

### Technique
- [x] Tous les tests passent
- [x] Lint OK (warnings mineurs acceptés dans tests)
- [x] TypeScript strict OK (erreurs préexistantes acceptées)
- [x] Architecture conforme au plan
- [x] Code review ready

### Documentation
- [x] Issue créée (FE-1-app-shell-issue.md)
- [x] PR créée (FE-1-app-shell-pr.md)
- [x] Code commenté

## Notes

- Les erreurs de lint restantes sont principalement dans les tests (mocks), non bloquantes
- Les erreurs TypeScript dans `client.test.ts` sont préexistantes (concernant `global.fetch` dans tests)
- L'architecture respecte le découplage UI/routing via layouts
- Le router est prêt pour les loaders/actions/errorElements futurs sans refacto
- Les pages sont des placeholders qui seront implémentées dans les PRs futures

## Prochaines étapes

- Implémentation de l'authentification réelle (login/signup)
- Intégration backend pour les features (horoscope, chat, account)
- Ajout de loaders/actions dans le Data Router
- Amélioration des layouts (style, responsive)
- Tests E2E pour les flows critiques

