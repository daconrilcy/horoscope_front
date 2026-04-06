# Story 65.21 : Infrastructure permissions — contexte auth frontend + préparation RBAC

Status: done

## Story

En tant qu'**développeur frontend et architect**,  
je veux que l'infrastructure de permissions admin soit en place pour les profils fins futurs,  
afin que l'ajout de profils `admin_business`, `admin_support`, `admin_ops` ne nécessite pas de refonte.

## Acceptance Criteria

1. **Given** l'utilisateur admin est connecté  
   **When** le contexte auth est initialisé  
   **Then** un `AdminPermissionsContext` React expose : `allowedSections: string[]`, `canEdit: (domain: string) => boolean`, `canExport: boolean`

2. **Given** l'implémentation initiale (rôle unique `admin`)  
   **When** le contexte est initialisé pour un utilisateur `admin`  
   **Then** `allowedSections` contient toutes les 10 sections  
   **And** `canEdit("entitlements")`, `canEdit("prompts")`, `canExport` retournent tous `true`

3. **Given** un composant admin reçoit `canEdit("entitlements") = false` (simulation future)  
   **When** le composant est rendu  
   **Then** le bouton "Modifier" n'est pas affiché (ou est désactivé avec indication visuelle)  
   **And** le mode consultation reste pleinement accessible

4. **Given** le backend reçoit une requête admin  
   **When** le guard `require_admin_user` valide le token  
   **Then** l'objet `AuthenticatedUser` retourné inclut `permissions: list[str]` (liste vide pour MVP, extensible sans breaking change)

## Tasks / Subtasks

- [x] Créer et consolider `AdminPermissionsContext.tsx` (AC: 1, 2, 3)
  - [x] Définir l'interface `AdminPermissions`
  - [x] Implémenter le Provider avec support des `overrides` pour les tests
  - [x] Documenter les profils cibles futurs
- [x] Audit et consommation du contexte dans les composants (AC: 3)
  - [x] `AdminEntitlementsPage.tsx` utilise `canEdit("entitlements")`
  - [x] `AdminSettingsPage.tsx` utilise `canExport` (implémenté via accessibilité directe ou props)
- [x] Ajouter `permissions: list[str] = []` à `AuthenticatedUser` dans `backend/app/api/dependencies/auth.py` (AC: 4)
- [x] Tests unitaires frontend `frontend/src/tests/AdminPermissions.test.tsx` (AC: 1, 2, 3)

### File List
- `frontend/src/state/AdminPermissionsContext.tsx`
- `backend/app/api/dependencies/auth.py`
- `frontend/src/pages/AdminPage.tsx`
- `frontend/src/pages/admin/AdminEntitlementsPage.tsx`
- `frontend/src/pages/admin/AdminSettingsPage.tsx`
- `frontend/src/tests/AdminPermissions.test.tsx`
- `frontend/src/tests/AdminSettingsPage.test.tsx`
