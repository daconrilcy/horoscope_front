# Story 65.5 : Dashboard — KPIs instantanés (inscrits, actifs, MRR)

Status: done

## Story

En tant qu'**admin**,  
je veux voir les indicateurs clés de performance (KPIs) en temps réel,  
afin de suivre la croissance et la santé financière de la plateforme d'un coup d'œil.

## Acceptance Criteria

1. **Given** l'admin est sur le Tableau de Bord (`/admin/dashboard`)  
   **When** la page est chargée  
   **Then** elle affiche les compteurs suivants :
   - Nombre total d'utilisateurs inscrits
   - Nombre d'utilisateurs actifs (ayant fait au moins une génération) dans les 7 derniers jours et 30 derniers jours
   - Monthly Recurring Revenue (MRR) estimé (somme des abonnements `active`)
   - Nombre d'essais gratuits (`trial`) en cours

2. **Given** le chargement des KPIs  
   **When** les données sont en cours de récupération  
   **Then** des skeletons ou un indicateur de chargement discret sont affichés

3. **Given** les données de facturation  
   **When** le MRR est calculé  
   **Then** il ne prend en compte que les abonnements dont le statut est `active` (exclut `trial`, `canceled`, `past_due`)

## Tasks / Subtasks

- [x] Créer l'endpoint backend `GET /api/v1/admin/dashboard/kpis-snapshot` (AC: 1, 3)
  - [x] Protéger avec `Depends(require_admin_user)`
  - [x] Implémenter les requêtes SQL agrégées (count, sum) sur `users`, `user_subscriptions`, `billing_plans` et `user_token_usage_logs`
  - [x] Calculer le MRR en sommant `monthly_price_cents` des abonnements `active`
- [x] Développer le composant `AdminDashboardPage.tsx` (AC: 1, 2)
  - [x] Utiliser `useQuery` pour appeler l'endpoint
  - [x] Afficher les cartes de KPIs avec les labels et valeurs
  - [x] Gérer l'affichage des abonnements par plan (détail)
- [x] Intégrer les styles CSS pour les cartes de KPIs (grid responsif)
- [x] Tests d'intégration backend `backend/app/tests/integration/test_admin_dashboard_api.py`
- [x] Tests unitaires frontend `frontend/src/tests/AdminDashboardPage.test.tsx`

### File List
- `backend/app/api/v1/routers/admin_dashboard.py`
- `backend/app/main.py`
- `frontend/src/pages/admin/AdminDashboardPage.tsx`
- `frontend/src/pages/admin/AdminDashboardPage.css`
- `backend/app/tests/integration/test_admin_dashboard_api.py`
- `frontend/src/tests/AdminDashboardPage.test.tsx`
