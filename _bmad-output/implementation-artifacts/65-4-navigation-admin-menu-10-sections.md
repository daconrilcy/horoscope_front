# Story 65.4 : Navigation admin — menu 10 sections avec architecture de permissions conditionnelle

Status: ready-for-dev

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

- [ ] Créer `frontend/src/context/AdminPermissionsContext.tsx` (AC: 3)
  - [ ] Définir l'interface : `{ allowedSections: string[], canEdit: (domain: string) => boolean, canExport: boolean }`
  - [ ] Provider initialise avec toutes les 10 sections pour le rôle `admin` (valeurs hardcodées dans cet epic)
  - [ ] Exporter `useAdminPermissions()` hook
- [ ] Mettre à jour `frontend/src/pages/AdminPage.tsx` (AC: 1, 2, 3, 4)
  - [ ] Remplacer le tableau statique de 4 sections par 10 sections avec les nouvelles URLs
  - [ ] Intégrer `AdminPermissionsContext.Provider` en haut de l'arbre admin
  - [ ] Filtrer les sections du menu avec `allowedSections` depuis le contexte
  - [ ] Gérer la rétrocompatibilité des 4 URLs existantes (redirects ou conservation)
- [ ] Mettre à jour `frontend/src/layouts/AdminLayout.tsx` (AC: 4)
  - [ ] Ajouter `aria-current="page"` sur le lien actif (utiliser `useMatch` ou `NavLink` de React Router)
  - [ ] Consommer `allowedSections` pour filtrer les sections affichées
- [ ] Ajouter/mettre à jour les routes dans le router React (`App.tsx`) (AC: 1, 2)
  - [ ] Déclarer les 10 nouvelles routes sous `/admin/*`
  - [ ] Maintenir les 4 routes existantes (ou ajouter des redirects)
  - [ ] Route de fallback `/admin/*` non reconnue → redirect vers `/admin/dashboard`
- [ ] Créer les pages placeholder pour les 6 nouvelles sections (AC: 1)
  - [ ] `AdminDashboardPage.tsx`, `AdminUsersPage.tsx`, `AdminEntitlementsPage.tsx`, `AdminAiGenerationsPage.tsx`, `AdminContentPage.tsx`, `AdminBillingPage.tsx`, `AdminLogsPage.tsx`, `AdminSupportPage.tsx`, `AdminSettingsPage.tsx` — pages vides avec titre, à étoffer dans les stories suivantes
- [ ] Ajouter les clés i18n dans `frontend/src/i18n/` namespace `admin` (AC: 1)
  - [ ] Labels des 10 sections : `sections.dashboard`, `sections.users`, `sections.entitlements`, `sections.ai_generations`, `sections.prompts`, `sections.content`, `sections.billing`, `sections.logs`, `sections.support`, `sections.settings`
- [ ] CSS dans `frontend/src/layouts/AdminLayout.css` ou `frontend/src/pages/AdminPage.css` (AC: 4)
  - [ ] Style `.nav-item--active` ou `[aria-current="page"]` pour la section active
  - [ ] Utiliser `var(--primary)`, `var(--glass)`, `var(--text-1)`, `var(--text-2)`

## Dev Notes

### Contexte architectural
- **`AdminPage.tsx`** (lire avant de modifier) : actuellement 4 sections statiques `PricingIcon`, `MonitoringIcon`, `PersonasIcon`, `ReconciliationIcon` dans un `AdminSection[]` passé à `AdminLayout`
- **`AdminLayout`** : composant dans `frontend/src/layouts/` — accepte `title`, `sections: AdminSection[]`, `backToHubLabel` — lire avant de modifier
- **`AdminSection` type** : `{ path: string, label: string, Icon: ComponentType<{className?: string}> }` — l'étendre si nécessaire mais préserver la compatibilité
- **Frontière avec Story 65-21** : cette story crée `AdminPermissionsContext` et l'instancie pour le menu. La story 65-21 (dernier sprint) contractualise l'interface complète et vérifie la consommation cross-composants. Ne pas sur-ingéniérer le contexte ici — juste `allowedSections` suffit pour cette story
- **React Router NavLink** : utiliser `<NavLink>` de react-router-dom qui gère automatiquement `aria-current` et la classe active — vérifier si `AdminLayout` utilise déjà `NavLink` ou `Link`

### Rétrocompatibilité des 4 URLs existantes
Vérifier dans `App.tsx` quelles routes existent pour `/admin/pricing`, `/admin/monitoring`, `/admin/personas`, `/admin/reconciliation`. Options :
1. Conserver les routes existantes ET les mapper dans le nouveau menu (URL `pricing` → section "Billing", `monitoring` → "Logs & Incidents", `personas` → "Prompts & Personas", `reconciliation` → "Billing")
2. Ajouter des `<Route path="/admin/pricing" element={<Navigate to="/admin/billing" replace />} />`
Préférer l'option 2 pour la cohérence long terme.

### CSS — aucun style inline
- Tout le CSS dans `AdminLayout.css` ou `AdminPage.css`
- Variables : `var(--primary)`, `var(--primary-strong)`, `var(--glass)`, `var(--glass-border)`, `var(--text-1)`, `var(--text-2)`, `var(--bg-base)`, `var(--line)`

### Project Structure Notes
- Nouveau fichier : `frontend/src/context/AdminPermissionsContext.tsx`
- Modifier : `frontend/src/pages/AdminPage.tsx`, `frontend/src/layouts/AdminLayout.tsx` (lire d'abord), `frontend/src/App.tsx` (routing)
- Nouveaux fichiers pages : dans `frontend/src/pages/admin/` (suivre le pattern existant)
- i18n : `frontend/src/i18n/` — namespace `admin` déjà présent, ajouter/compléter les clés

### References
- `frontend/src/pages/AdminPage.tsx` [Source: session context — structure actuelle lue]
- `frontend/src/layouts/` — `AdminLayout` [Source: architecture frontend]
- i18n : `frontend/src/i18n/` namespace `admin` [Source: architecture frontend]
- Epic 65 FR65-12, FR65-13, FR65-18 : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-4`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
