# Story 65.21 : Infrastructure permissions — contexte auth frontend + préparation RBAC

Status: ready-for-dev

## Story

En tant que **développeur frontend et architect**,  
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

- [ ] Vérifier et consolider `AdminPermissionsContext.tsx` créé en Story 65-4 (AC: 1, 2, 3)
  - [ ] Lire `frontend/src/context/AdminPermissionsContext.tsx` — créé en Story 65-4
  - [ ] Vérifier que l'interface est : `{ allowedSections: string[], canEdit: (domain: string) => boolean, canExport: boolean }`
  - [ ] Compléter si manquant : `canEdit` doit accepter les domaines `"entitlements"`, `"prompts"`, `"content"`, `"users"`, `"billing"`, `"audit"`, `"exports"`, `"settings"`
  - [ ] Pour MVP : tous les domaines retournent `true` pour le rôle `admin`
  - [ ] Préparer la structure pour injection future : le Provider doit accepter une config optionnelle de permissions
- [ ] Audit de consommation du contexte dans tous les composants admin (AC: 3)
  - [ ] Vérifier que `AdminEntitlementsPage.tsx` utilise `canEdit("entitlements")` pour le bouton "Mode édition"
  - [ ] Vérifier que `AdminPromptsPage.tsx` utilise `canEdit("prompts")` pour le rollback
  - [ ] Vérifier que la section Exports utilise `canExport`
  - [ ] Si un composant n'utilise pas le contexte : l'adapter pour le consommer
- [ ] Test de régression permission : simuler `canEdit = () => false` (AC: 3)
  - [ ] Dans un test ou via un flag de dev : passer `canEdit: () => false` au Provider
  - [ ] Vérifier que tous les boutons d'édition disparaissent / sont désactivés sans casser l'affichage
- [ ] Ajouter `permissions: list[str] = []` à `AuthenticatedUser` dans `backend/app/api/dependencies/auth.py` (AC: 4)
  - [ ] Champ avec valeur par défaut `[]` — aucun breaking change sur les endpoints existants
  - [ ] La valeur est `[]` pour tous les admins dans cet epic — structure prête pour Epic 66+ RBAC fin
  - [ ] Vérifier que les tests existants passent toujours après cet ajout
- [ ] Documenter l'architecture de permissions dans un commentaire ou docstring du Context (AC: 1)
  - [ ] Documenter les 4 profils cibles : `admin_business`, `admin_support`, `admin_ops`, `super_admin`
  - [ ] Documenter comment brancher une vraie config de permissions depuis l'API dans un epic futur

## Dev Notes

### Frontière avec Story 65-4
- **Story 65-4** : crée le contexte, instancie le Provider, implémente le filtrage du menu
- **Cette story (65-21)** : contractualise l'interface complète, audite tous les composants consommateurs, ajoute le champ `permissions` côté backend
- **Ordre** : cette story est à implémenter EN DERNIER dans l'epic (toutes les autres stories doivent être livrées d'abord)

### AdminPermissionsContext — interface contractuelle
```typescript
interface AdminPermissions {
  allowedSections: string[]  // ex: ["dashboard", "users", "entitlements", ...]
  canEdit: (domain: string) => boolean  // domain: "entitlements" | "prompts" | "content" | ...
  canExport: boolean
}

const DEFAULT_ADMIN_PERMISSIONS: AdminPermissions = {
  allowedSections: ALL_SECTIONS,  // toutes les 10 sections
  canEdit: () => true,            // MVP : tout admin peut tout éditer
  canExport: true                 // MVP : tout admin peut exporter
}
```

### Backend — champ permissions
```python
class AuthenticatedUser(BaseModel):
    id: int
    role: str
    email: str
    created_at: datetime
    permissions: list[str] = []  # Ajout ici — liste vide pour MVP
```

Ce champ est rétrocompatible : les endpoints existants qui utilisent `AuthenticatedUser` ne changent pas. La valeur sera populée dans un epic futur quand les permissions granulaires seront implémentées.

### Test de simulation permissions
Pour valider AC 3 sans un vrai système de permissions, ajouter un test React ou un story de test visuel :
```tsx
<AdminPermissionsContext.Provider value={{
  allowedSections: ["dashboard", "users"],  // sections limitées
  canEdit: () => false,                     // aucune édition
  canExport: false                          // aucun export
}}>
  <AdminEntitlementsPage />
</AdminPermissionsContext.Provider>
```
Vérifier que la page s'affiche sans bouton "Mode édition".

### Project Structure Notes
- **Lire d'abord** : `frontend/src/context/AdminPermissionsContext.tsx` (créé Story 65-4)
- **Modifier** : `backend/app/api/dependencies/auth.py` (ajout `permissions: list[str] = []`)
- **Auditer** : tous les composants admin sous `frontend/src/pages/admin/`
- Prerequisite : **TOUTES** les autres stories de l'Epic 65 doivent être livrées avant cette story

### References
- `frontend/src/context/AdminPermissionsContext.tsx` [Source: Story 65-4]
- `backend/app/api/dependencies/auth.py` — `AuthenticatedUser` [Source: session context]
- Epic 65 FR65-13, FR65-18 : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-21`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
