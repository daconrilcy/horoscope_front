# Story 65.7 : Dashboard — KPIs billing (échecs de paiement, revenu, Stripe summary)

Status: done

## Story

En tant qu'**admin billing**,  
je veux voir les indicateurs de santé du billing sur le tableau de bord,  
afin de détecter immédiatement une friction de paiement ou un écart de revenu.

## Acceptance Criteria

1. **Given** l'admin est sur `/admin/dashboard`  
   **When** la section billing est affichée  
   **Then** les indicateurs suivants sont visibles :
   - Nombre d'abonnements en échec de paiement (count par période)
   - Revenu total facturé sur la période (somme calculée depuis `user_subscriptions` actifs × prix plan)
   - Répartition revenu par plan (graphe ou tableau)

2. **Given** un indicateur d'échec de paiement est non nul  
   **When** l'admin clique sur le compteur  
   **Then** il est redirigé vers la section Users filtrée sur les comptes avec `failure_reason` non null

3. **Given** la section billing est affichée  
   **When** le filtre de période est changé  
   **Then** les KPIs billing recalculent avec la même période que les KPIs de flux (cohérence du contexte de filtre)

## Tasks / Subtasks

- [x] Créer l'endpoint `GET /api/v1/admin/dashboard/kpis-billing?period=7d&plan=all` dans `admin_dashboard.py` (AC: 1, 3)
  - [x] Échecs de paiement sur période via `UserSubscriptionModel`
  - [x] Revenu estimé sur période via `StripeBillingProfileModel` active plans
  - [x] Répartition par plan
- [x] Intégrer dans `frontend/src/pages/admin/AdminDashboardPage.tsx` (AC: 1, 2, 3)
  - [x] Section "Répartition du revenu estimé" avec tableau
  - [x] Compteur d'échecs de paiement cliquable → `/admin/users?filter=payment_failure`
  - [x] Filtres partagés
- [x] Ajouter un lien vers `/admin/billing` (Voir le détail complet)
- [x] CSS dans `AdminDashboardPage.css` pour la section billing et table
- [x] Tests d'intégration backend `backend/app/tests/integration/test_admin_dashboard_api.py`

### File List
- `backend/app/api/v1/routers/admin_dashboard.py`
- `frontend/src/pages/admin/AdminDashboardPage.tsx`
- `frontend/src/pages/admin/AdminDashboardPage.css`
- `backend/app/tests/integration/test_admin_dashboard_api.py`
