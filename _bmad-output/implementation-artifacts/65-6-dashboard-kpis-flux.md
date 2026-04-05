# Story 65.6 : Dashboard — KPIs de flux avec filtres temporels (conversion, churn, upgrades)

Status: done

## Story

En tant qu'**admin business**,  
je veux voir les métriques de flux filtrées par période sur le tableau de bord,  
afin de détecter si la croissance accélère, ralentit ou si une friction apparaît dans le funnel.

## Acceptance Criteria

1. **Given** l'admin est sur `/admin/dashboard`  
   **When** il sélectionne une période (7j / 30j / 12 mois)  
   **Then** les KPIs de flux suivants se recalculent pour la période choisie :
   - Nouveaux inscrits
   - Upgrades (free→basic, free→premium, basic→premium) — count par transition
   - Downgrades (premium→basic, etc.)
   - Churn estimé (abonnements passés de `active` à `cancelled` ou `expired`)
   - Échecs de paiement (abonnements avec `failure_reason` non null)
   - Revenu par plan sur la période

2. **Given** l'admin sélectionne "12 mois"  
   **When** la visualisation de tendance est affichée  
   **Then** un graphe en courbes montre l'évolution journalière ou hebdomadaire des inscrits et upgrades  
   **And** la granularité est cohérente avec la période (7j → journalier, 30j → journalier, 12m → hebdomadaire)

3. **Given** l'admin applique un filtre de plan (tous / free / basic / premium)  
   **When** le filtre est actif  
   **Then** tous les KPIs de flux se recalculent pour le segment de plan sélectionné

## Tasks / Subtasks

- [x] Créer l'endpoint `GET /api/v1/admin/dashboard/kpis-flux?period=7d&plan=all` dans `admin_dashboard.py` (AC: 1, 2, 3)
  - [x] Paramètres : `period`, `plan`
  - [x] Calculer `start_date` depuis `period`
  - [x] Nouveaux inscrits : `SELECT count(*) FROM users WHERE created_at >= start_date`
  - [x] Churn MVP : `SELECT count(*) FROM stripe_billing_profiles WHERE subscription_status IN ('canceled', 'unpaid') AND updated_at >= start_date`
  - [x] Échecs de paiement : `SELECT count(*) FROM user_subscriptions WHERE failure_reason IS NOT NULL AND updated_at >= start_date`
  - [x] Revenu par plan : `SUM(monthly_price_cents)` pour les abonnements `active`
  - [x] Données de tendance : aggregation journalière/hebdo des inscrits
- [x] Créer/mettre à jour `frontend/src/pages/admin/AdminDashboardPage.tsx` (AC: 1, 2, 3)
  - [x] Sélecteur de période : `7j / 30j / 12 mois`
  - [x] Sélecteur de plan : `Tous / Free / Basic / Premium`
  - [x] Re-fetch des KPIs flux quand les filtres changent
  - [x] Afficher les KPIs flux dans des cartes distinctes
  - [x] Graphe de tendance SVG natif (sans lib externe)
- [x] CSS dans `AdminDashboardPage.css` (AC: 1, 2, 3)
  - [x] Styles des sélecteurs de filtre
  - [x] Styles du graphe de tendance
- [x] Tests d'intégration backend `backend/app/tests/integration/test_admin_dashboard_api.py`
- [x] Tests unitaires frontend `frontend/src/tests/AdminDashboardPage.test.tsx`

### File List
- `backend/app/api/v1/routers/admin_dashboard.py`
- `frontend/src/pages/admin/AdminDashboardPage.tsx`
- `frontend/src/pages/admin/AdminDashboardPage.css`
- `backend/app/tests/integration/test_admin_dashboard_api.py`
- `frontend/src/tests/AdminDashboardPage.test.tsx`
