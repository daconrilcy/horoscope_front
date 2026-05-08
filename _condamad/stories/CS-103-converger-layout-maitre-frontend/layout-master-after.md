# CS-103 - Inventaire layout maitre apres

- `RootLayout` est monte comme route racine unique dans `frontend/src/app/routes.tsx`.
- La branche application/admin est un enfant de `RootLayout` et conserve `AuthGuard`, `AppLayout`, `AdminGuard`, `RoleGuard` et les chemins existants.
- `RootLayout` est l'unique owner de `StarfieldBackground`, `.app-shell app-bg` et `.app-bg-container`.
- `RootLayout` applique `.app-bg-container--admin` selon `useLocation()` pour preserver le comportement admin existant.
- `AppLayout` conserve uniquement le shell secondaire: `Header`, `Sidebar`, `BottomNav`, `PageErrorBoundary` et `Outlet`.
- Exceptions restantes: aucune exception maitre active. Les gaps audit initialement phases sont fermes par `CS-104`, `CS-105`, `CS-106` et `CS-107`.
- Guard: `frontend/src/tests/page-architecture-guards.test.ts` echoue si `RootLayout` n'est plus monte ou si `AppLayout` reprend le fond maitre.
