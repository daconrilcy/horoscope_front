# Story 51.1: Créer RootLayout et AuthLayout — fond, providers et isolation des pages auth

Status: done

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
6. `AppShell.tsx` coexiste avec les nouveaux layouts (modifié pour centraliser le fond dans RootLayout).
7. Les tests existants relatifs aux routes auth passent sans modification.

## Tasks / Subtasks

- [x] Tâche 1 : Créer `frontend/src/layouts/` (AC: 1)
  - [x] Créer le dossier `frontend/src/layouts/`
  - [x] Créer `frontend/src/layouts/index.ts` (barrel export)

- [x] Tâche 2 : Créer `RootLayout.tsx` (AC: 1, 4)
  - [x] Lire `AppShell.tsx` pour identifier les éléments de fond (StarfieldBackground, app-bg, app-bg-container)
  - [x] `RootLayout` rend : `<div className="app-shell app-bg"><StarfieldBackground /><div className="app-bg-container"><Outlet /></div></div>`
  - [x] Exporter depuis `frontend/src/layouts/index.ts`

- [x] Tâche 3 : Créer `AuthLayout.tsx` (AC: 2, 5)
  - [x] `AuthLayout` rend un conteneur centré : `<div className="auth-layout"><Outlet /></div>`
  - [x] Ajouter dans `App.css` ou `frontend/src/layouts/AuthLayout.css` les styles `.auth-layout`
  - [x] Styles : `display: flex`, `align-items: center`, `justify-content: center`, `min-height: 100vh`, `padding: var(--space-6)`
  - [x] Conteneur interne : `max-width: 480px`, `width: 100%`

- [x] Tâche 4 : Mettre à jour `routes.tsx` (AC: 3, 4, 5)
  - [x] Créer un groupe de routes auth wrappé par `<RootLayout>` → `<AuthLayout>`
  - [x] Déplacer `/login` et `/register` dans ce groupe
  - [x] La route racine `<AuthGuard><AppShell />` reste inchangée

- [x] Tâche 5 : Validation (AC: 6, 7)
  - [x] Vérifier que `/login` et `/register` affichent le fond premium + contenu centré
  - [x] Vérifier que les pages authentifiées restent inchangées
  - [x] Exécuter `npm run test` — tous les tests passent

## Dev Notes

### Contexte technique

...

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List
- Création de `RootLayout` pour centraliser le fond `StarfieldBackground`.
- Création de `AuthLayout` pour centrer les pages d'authentification.
- Mise à jour de `AppShell` pour retirer le fond désormais géré par `RootLayout`.
- Restructuration de `routes.tsx` pour intégrer les nouveaux layouts.
- Validation via `npm run test` : 1079 tests réussis.

### File List
- `frontend/src/layouts/RootLayout.tsx`
- `frontend/src/layouts/AuthLayout.tsx`
- `frontend/src/layouts/AuthLayout.css`
- `frontend/src/layouts/index.ts`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/app/routes.tsx`
