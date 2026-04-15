# Admin `/admin` - Implémentation existante

## Objectif du document
Ce document décrit ce qui est **déjà mis en oeuvre** pour l'espace d'administration accessible via la route frontend `/admin`.

Il couvre :
- le contrôle d'accès et le routing ;
- les sections disponibles dans l'UI admin ;
- les APIs backend consommées ;
- les tests déjà présents pour sécuriser ce périmètre.

## Accès et sécurité d'entrée

### Route principale
- Route frontend : `/admin`
- Définie dans `frontend/src/app/routes.tsx` avec des sous-routes (`/admin/dashboard`, `/admin/users`, etc.).

### Garde d'accès
- Le composant `AdminGuard` (`frontend/src/components/AdminGuard.tsx`) protège toutes les routes `/admin`.
- Comportement actuel :
  - vérifie le token et charge `/v1/auth/me` ;
  - redirige vers `/login?returnTo=...` si non authentifié ;
  - redirige vers `/` si le rôle n'est pas `admin` ;
  - autorise l'accès uniquement si `authMe.data.role === "admin"`.

### Permissions internes (préparation granularité)
- Le contexte `AdminPermissionsContext` existe (`frontend/src/state/AdminPermissionsContext.tsx`).
- Aujourd'hui, un admin a tous les droits (toutes sections, édition, export).
- Cette couche est déjà structurée pour évoluer vers des profils admin plus granulaires.

## Structure UI accessible depuis `/admin`

### Layout commun
- `frontend/src/pages/AdminPage.tsx` compose l'espace admin :
  - sidebar ;
  - hub (`/admin`) ;
  - navigation vers 10 sections principales.
- `frontend/src/layouts/AdminLayout.tsx` applique un filtrage des sections selon `allowedSections`.

### Sections fonctionnelles disponibles
Depuis `/admin`, les sections suivantes sont routées et implémentées :

1. `/admin/dashboard` - `AdminDashboardPage`
   - KPIs snapshot, flux et billing.
   - Filtres période/plan.
   - Endpoints : `/v1/admin/dashboard/kpis-snapshot`, `/kpis-flux`, `/kpis-billing`.

2. `/admin/users` - `AdminUsersPage`
   - Recherche utilisateurs (email/ID/filter).
   - Navigation vers fiche détail.
   - Endpoint : `/v1/admin/users?q=...`.

3. `/admin/users/:userId` - `AdminUserDetailPage`
   - Détail utilisateur, activité, quotas, tickets/audits récents.
   - Actions admin (refresh abonnement, assignation plan, geste commercial).
   - Révélation Stripe ID masqué via action dédiée.
   - Endpoints : `/v1/admin/users/{id}`, `/v1/admin/users/{id}/{action}`, `/v1/admin/users/{id}/reveal-stripe-id`.

4. `/admin/entitlements` - `AdminEntitlementsPage`
   - Matrice plans/features.
   - Mode édition avec confirmations.
   - Mise à jour ciblée de cellule (access_mode/quota/is_enabled).
   - Endpoints : `/v1/admin/entitlements/matrix`, `PATCH /v1/admin/entitlements/{planId}/{featureId}`.

5. `/admin/ai-generations` - `AdminAiGenerationsPage`
   - Supervision LLM par use case : volume, tokens, coût, latence, erreurs.
   - Vue de détail avec derniers échecs.
   - Endpoints : `/v1/admin/ai/metrics`, `/v1/admin/ai/metrics/{useCase}`.

6. `/admin/prompts` - `AdminPromptsPage`
   - Onglets Prompts / Personas.
   - Historique versions de prompts.
   - Diff côte à côte.
   - Rollback d'une version active.
   - S'appuie sur la couche API admin LLM (`/v1/admin/llm/...`).

7. `/admin/content` - `AdminContentPage`
   - Gestion textes (paywall/transactionnel/marketing).
   - Feature flags (activation/désactivation).
   - Templates éditoriaux versionnés (publication + rollback).
   - Règles de calibration modifiables.
   - Endpoints principaux : `/v1/admin/content/...` (+ routes éditoriales/calibration exposées via la couche API frontend).

8. `/admin/billing` - `AdminBillingPage`
   - Vue tarification via `PricingAdmin`.
   - Lecture des plans de facturation.
   - Pas d'édition complète des plans en UI pour l'instant (message "upcoming").

9. `/admin/logs` - `AdminLogsPage`
   - Observabilité technique : quota alerts, audit logs, logs LLM, événements Stripe.
   - Replay d'appel LLM.
   - Export d'audit.
   - Protection UI supplémentaire : masquage de clés sensibles dans la modale détail audit.
   - Endpoints : `/v1/admin/logs/quota-alerts`, `/v1/admin/logs/stripe`, `/v1/admin/audit`, `/v1/admin/audit/export`, `/v1/admin/llm/call-logs`, `/v1/admin/llm/replay`.

10. `/admin/support` - `AdminSupportPage`
    - Tickets support.
    - Modération des contenus signalés.
    - Endpoints : `/v1/admin/support/tickets`, `/v1/admin/support/flagged-content`.

11. `/admin/settings` - `AdminSettingsPage`
    - Exports admin (users, generations, billing).
    - Flux sécurisé avec confirmation explicite côté UI.
    - Endpoints : `/v1/admin/exports/users|generations|billing`.

12. `/admin/reconciliation` - `ReconciliationAdmin`
    - Intègre le panel de réconciliation B2B.

## Redirects legacy déjà gérés
Les anciennes routes admin sont redirigées automatiquement :
- `/admin/pricing` -> `/admin/billing`
- `/admin/monitoring` -> `/admin/logs`
- `/admin/personas` -> `/admin/prompts`

## Couverture backend admin déjà branchée
Le backend inclut les routeurs admin dans `backend/app/main.py` :
- `admin_dashboard_router` (`/v1/admin/dashboard`)
- `admin_entitlements_router` (`/v1/admin/entitlements`)
- `admin_ai_router` (`/v1/admin/ai`)
- `admin_logs_router` (`/v1/admin/logs`)
- `admin_exports_router` (`/v1/admin/exports`)
- `admin_llm_router` (`/v1/admin/llm`)
- `admin_llm_assembly_router` (`/v1/admin/llm/assembly`)
- `admin_llm_release_router` (monté sur `/v1/admin/llm/releases`)
- `admin_users_router` (`/v1/admin/users`)
- `admin_support_router` (`/v1/admin/support`)
- `admin_audit_router` (`/v1/admin/audit`)
- `admin_content_router` (`/v1/admin/content`)
- `admin_pdf_templates_router` (`/v1/admin/pdf-templates`)

## Tests existants autour du périmètre admin
Des tests frontend existent déjà et valident notamment :
- accès refusé aux non-admins et accès autorisé aux admins (`frontend/src/tests/router.test.tsx`, `frontend/src/tests/AdminPage.test.tsx`) ;
- présence des sections admin dans la navigation ;
- redirects legacy ;
- comportement du contexte de permissions (`frontend/src/tests/AdminPermissions.test.tsx`) ;
- tests dédiés de pages admin (dashboard, logs, prompts, content, settings, users, etc.).

## Limites observables à ce stade
- La granularité fine des permissions admin est préparée mais pas encore active (modèle "admin full access" par défaut).
- Certaines zones sont plutôt orientées visualisation/opérations, avec des actions d'édition encore partielles selon les domaines (ex. tarification).
- Le périmètre admin est déjà large et couvre aussi des capacités LLM avancées (prompts, rollback, replay, release ops), mais reste dépendant des droits backend effectifs et de l'industrialisation continue.

