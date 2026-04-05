# Story 65.3 : Guard admin frontend — protection des routes /admin/*

Status: ready-for-dev

## Story

En tant qu'**utilisateur non-admin**,  
je veux être redirigé hors de l'espace admin si je n'ai pas les permissions,  
afin que l'espace admin soit inaccessible à toute personne non autorisée.

## Acceptance Criteria

1. **Given** un utilisateur non authentifié tente d'accéder à `/admin` ou `/admin/*`  
   **When** la route est évaluée  
   **Then** il est redirigé vers `/login` avec le paramètre `redirect=/admin` (ou équivalent) pour revenir après connexion

2. **Given** un utilisateur authentifié avec rôle `user`, `support`, `ops` ou `enterprise_admin` tente d'accéder à `/admin/*`  
   **When** la route est évaluée  
   **Then** il est redirigé vers `/` (dashboard utilisateur) sans message d'erreur affiché

3. **Given** un utilisateur authentifié avec rôle `admin` accède à `/admin`  
   **When** la route est évaluée  
   **Then** la page admin se charge normalement

4. **Given** le composant de guard admin est rendu  
   **When** le rôle de l'utilisateur est en cours de chargement (état async)  
   **Then** un spinner de chargement est affiché — aucune redirection n'est déclenchée prématurément

## Tasks / Subtasks

- [ ] Créer le composant `AdminGuard` dans `frontend/src/components/AdminGuard.tsx` (AC: 1, 2, 3, 4)
  - [ ] Lire le rôle utilisateur depuis le contexte d'auth existant
  - [ ] Si chargement en cours → afficher spinner (AC: 4)
  - [ ] Si non authentifié → `<Navigate to="/login" state={{ redirect: location.pathname }} />`
  - [ ] Si authentifié mais rôle ≠ `"admin"` → `<Navigate to="/" replace />`
  - [ ] Si rôle `"admin"` → `<Outlet />` (ou `{children}`)
- [ ] Envelopper toutes les routes `/admin/*` dans le routeur React (`frontend/src/App.tsx` ou fichier de routes) (AC: 1, 2, 3)
  - [ ] Identifier le fichier qui définit `<Route path="/admin" element={<AdminPage />}>` — probablement `App.tsx` ou `router.tsx`
  - [ ] Envelopper avec `<AdminGuard>` ou utiliser comme `element={<AdminGuard />}` parent
- [ ] Ajouter le CSS du spinner de chargement dans `frontend/src/components/AdminGuard.css` (AC: 4)
  - [ ] Utiliser `var(--primary)` pour la couleur du spinner
  - [ ] Centrer le spinner dans la page (flex + height: 100vh)

## Dev Notes

### Contexte architectural
- **Contexte d'auth existant** : localiser dans `frontend/src/context/` ou `frontend/src/hooks/` — chercher `useAuth`, `AuthContext`, ou `useUser` — c'est là qu'on obtient `{ user, isLoading }` ou équivalent
- **Rôle dans le context** : le user object doit avoir un champ `role: string` — vérifier le type TypeScript dans `frontend/src/types/` ou `frontend/src/api/`
- **React Router v6** : utiliser `<Navigate>` pour les redirections, `useLocation()` pour capturer le path actuel, `<Outlet>` pour rendre les routes enfants
- **Pattern guard existant** : il existe probablement un `PrivateRoute` ou `RequireAuth` dans le projet — vérifier `frontend/src/components/` avant de créer `AdminGuard` pour éviter la duplication, et suivre le même pattern

### Implémentation type
```tsx
export function AdminGuard() {
  const { user, isLoading } = useAuth()  // adapter au hook réel du projet
  const location = useLocation()
  
  if (isLoading) return <div className="admin-guard-loading"><span className="spinner" /></div>
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />
  if (user.role !== "admin") return <Navigate to="/" replace />
  return <Outlet />
}
```

### CSS — aucun style inline
- Créer `frontend/src/components/AdminGuard.css` avec `.admin-guard-loading` et `.spinner`
- Importer ce CSS dans `AdminGuard.tsx`
- Variables CSS à utiliser : `var(--primary)`, `var(--bg-base)`

### Project Structure Notes
- Nouveau composant : `frontend/src/components/AdminGuard.tsx` + `AdminGuard.css`
- Modification du fichier de routing (`App.tsx` ou équivalent) — **lire ce fichier avant de modifier**
- Ne pas modifier `AdminPage.tsx` dans cette story — c'est la story 65-4 qui restructure la navigation

### References
- Contexte auth frontend : `frontend/src/context/` ou `frontend/src/hooks/useAuth.ts` [Source: architecture frontend]
- Routing React : `frontend/src/App.tsx` [Source: architecture frontend]
- Epic 65 FR65-11 : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-3`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
