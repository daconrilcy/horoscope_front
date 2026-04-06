# Story 65.4 : Navigation admin — menu 10 sections avec architecture de permissions conditionnelle

Status: done

## Story

En tant qu'**admin**,  
je veux un menu de navigation structuré en 10 sections avec l'infrastructure pour des permissions futures,  
afin de piloter tous les domaines du produit depuis une interface cohérente et évolutive.

## Acceptance Criteria

1. **Given** l'admin est connecté et accède à `/admin`  
   **When** le layout admin est rendu  
   **Then** le menu latéral affiche les 10 sections dans l'ordre : Tableau de bord (`/admin/dashboard`), Utilisateurs (`/admin/users`), Abonnements & Droits (`/admin/entitlements`), Générations IA (`/admin/ai-generations`), Prompts & Personas (`/admin/prompts`), Contenus & Paywalls (`/admin/content`), Billing (`/admin/billing`), Logs & Incidents (`/admin/logs`), Support (`/admin/support`), Paramètres (`/admin/settings`)

2. **Given** les 4 sections existantes (`/admin/pricing`, `/admin/monitoring`, `/admin/personas`, `/admin/reconciliation`)  
   **When** l'admin y accède via leur ancienne URL  
   **Then** elles continuent de fonctionner (pas de 404) — soit via redirect vers leur nouvelle URL dans la structure, soit en conservant l'URL  
   **And** elles apparaissent dans le menu unifié de la nouvelle navigation

3. **Given** le composant menu admin  
   **When** il est rendu  
   **Then** il accepte `allowedSections: string[]` depuis `AdminPermissionsContext`  
   **And** dans l'implémentation initiale, `allowedSections` contient toutes les 10 sections pour le rôle `admin`  
   **And** le composant filtre les sections affichées selon cette liste (prêt pour restriction future sans refonte)

4. **Given** l'admin navigue entre sections  
   **When** une section est active  
   **Then** l'entrée de menu correspondante a un style actif visible (`aria-current="page"`)

## Tasks / Subtasks

- [x] Créer `frontend/src/state/AdminPermissionsContext.tsx` (AC: 3)
  - [x] Définir l'interface : `{ allowedSections: string[], canEdit: (domain: string) => boolean, canExport: boolean }`
  - [x] Provider initialise avec toutes les 10 sections pour le rôle `admin`
  - [x] Exporter `useAdminPermissions()` hook
- [x] Mettre à jour `frontend/src/pages/AdminPage.tsx` (AC: 1, 2, 3, 4)
  - [x] Remplacer le tableau statique de 4 sections par 10 sections avec les nouvelles URLs
  - [x] Intégrer `AdminPermissionsProvider`
  - [x] Passer les sections via le context de l'Outlet
- [x] Mettre à jour `frontend/src/layouts/AdminLayout.tsx` (AC: 4)
  - [x] Ajouter un menu latéral permanent pour l'espace admin
  - [x] Utiliser `NavLink` pour gérer `aria-current="page"` et le style actif
  - [x] Consommer `allowedSections` pour filtrer les sections affichées
- [x] Ajouter/mettre à jour les routes dans le router React (`frontend/src/app/routes.tsx`) (AC: 1, 2)
  - [x] Déclarer les 10 nouvelles routes sous `/admin/*`
  - [x] Ajouter des redirections pour les 4 routes legacy
- [x] Créer les pages placeholder pour les nouvelles sections dans `frontend/src/pages/admin/` (AC: 1)
  - [x] `AdminDashboardPage.tsx`, `AdminUsersPage.tsx`, etc.
  - [x] `AdminHubPage.tsx` pour le hub `/admin`
- [x] Ajouter les clés i18n dans `frontend/src/i18n/admin.ts` (AC: 1)
- [x] CSS dans `frontend/src/layouts/AdminLayout.css` (AC: 4)

### File List
- `frontend/src/state/AdminPermissionsContext.tsx`
- `frontend/src/pages/AdminPage.tsx`
- `frontend/src/layouts/AdminLayout.tsx`
- `frontend/src/layouts/AdminLayout.css`
- `frontend/src/app/routes.tsx`
- `frontend/src/pages/admin/AdminHubPage.tsx`
- `frontend/src/pages/admin/AdminDashboardPage.tsx`
- `frontend/src/pages/admin/AdminUsersPage.tsx`
- `frontend/src/pages/admin/AdminEntitlementsPage.tsx`
- `frontend/src/pages/admin/AdminAiGenerationsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminContentPage.tsx`
- `frontend/src/pages/admin/AdminBillingPage.tsx`
- `frontend/src/pages/admin/AdminLogsPage.tsx`
- `frontend/src/pages/admin/AdminSupportPage.tsx`
- `frontend/src/pages/admin/AdminSettingsPage.tsx`
- `frontend/src/i18n/admin.ts`
- `frontend/src/tests/AdminPage.test.tsx`

### Completion Notes List

- Revue Epic 65 du 2026-04-06 : le layout repose désormais uniquement sur `NavLink` pour l'état actif et `aria-current`, ce qui corrige le cas des sous-routes admin (`/admin/users/123`, etc.) sans logique manuelle redondante.
