# Story 65.6 : Dashboard — KPIs de flux avec filtres temporels (conversion, churn, upgrades)

Status: ready-for-dev

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

- [ ] Créer l'endpoint `GET /api/v1/admin/dashboard/kpis-flux?period=7d&plan=all` dans `admin_dashboard.py` (AC: 1, 2, 3)
  - [ ] Paramètres : `period: Literal["7d", "30d", "12m"]`, `plan: Literal["all", "free", "basic", "premium"]`
  - [ ] Calculer `start_date` depuis `period` : `now - 7 days`, `now - 30 days`, `now - 365 days`
  - [ ] Nouveaux inscrits : `SELECT count(*) FROM users WHERE created_at >= start_date`
  - [ ] Upgrades/downgrades : depuis `audit_events` (`action = "plan_changed"`) ou `user_subscriptions` avec `started_at` — identifier la source fiable
  - [ ] Churn MVP : `SELECT count(*) FROM user_subscriptions WHERE status IN ('cancelled', 'expired') AND updated_at >= start_date`
  - [ ] Échecs de paiement : `SELECT count(*) FROM user_subscriptions WHERE failure_reason IS NOT NULL AND updated_at >= start_date`
  - [ ] Filtrage par plan : JOIN `billing_plans` + `WHERE bp.code = plan` si plan ≠ "all"
  - [ ] Données de tendance (pour graphe) : aggregation journalière/hebdo des inscrits + upgrades
- [ ] Créer le schéma `KpisFluxResponse` dans `admin_dashboard.py` (AC: 1, 2)
  - [ ] Inclure `trend_data: list[TrendPoint]` avec `date: date`, `new_users: int`, `upgrades: int`
- [ ] Créer/mettre à jour `frontend/src/pages/admin/AdminDashboardPage.tsx` (AC: 1, 2, 3)
  - [ ] Sélecteur de période : `7j / 30j / 12 mois` (boutons ou select)
  - [ ] Sélecteur de plan : `Tous / Free / Basic / Premium`
  - [ ] Re-fetch des KPIs flux quand les filtres changent
  - [ ] Afficher les KPIs flux dans des cartes distinctes des KPIs snapshot (Story 65-5)
  - [ ] Graphe de tendance pour "12 mois" : utiliser une lib SVG légère ou canvas natif — **pas de lib externe** si le projet n'en utilise pas déjà une — vérifier `package.json`
- [ ] CSS dans `AdminDashboardPage.css` (AC: 1, 2, 3)
  - [ ] Styles des sélecteurs de filtre
  - [ ] Styles du graphe de tendance

## Dev Notes

### Contexte architectural
- **Source upgrades/downgrades** : les transitions de plan peuvent être dans `audit_events` (`action: "plan_changed"`, `details.before.plan`, `details.after.plan`) si l'audit trail existe déjà, sinon dans `user_subscriptions` avec les timestamps. Vérifier ce qui est disponible en DB avant d'implémenter
- **Churn MVP** : ne pas tenter de calculer un churn par cohorte (trop complexe pour MVP) — utiliser le count de subscriptions passées à `cancelled/expired` dans la période
- **Revenu par plan** : calcul approximatif = `SUM(monthly_price_cents) × (nombre de jours période / 30)` pour les abonnements actifs — pas de données de revenu réel Stripe
- **Graphe de tendance** : vérifier si le projet utilise déjà `recharts`, `chart.js`, `d3` ou autre lib graphique dans `frontend/package.json`. Si oui, utiliser la même. Si non, implémenter un graphe SVG simple (courbe) en CSS/SVG natif pour éviter une nouvelle dépendance

### Sélecteur de filtre
- Période par défaut : `30j`
- Plan par défaut : `Tous`
- Les filtres du Dashboard doivent être partagés entre KPIs flux (cette story) et KPIs billing (Story 65-7) — prévoir un état local ou un hook partagé dans `AdminDashboardPage`

### Project Structure Notes
- Modifier : `backend/app/api/v1/routers/admin_dashboard.py` (ajout d'endpoint dans le router créé Story 65-5)
- Modifier : `frontend/src/pages/admin/AdminDashboardPage.tsx` + `.css`
- Prerequisite : Story 65-5 (endpoint snapshot + page dashboard créés)

### References
- `backend/app/infra/db/models/billing.py` — `UserSubscriptionModel.failure_reason`, `UserSubscriptionModel.status` [Source: session context]
- `backend/app/infra/db/models/audit_event.py` — `AuditEventModel.action`, `.details` [Source: session context]
- Epic 65 FR65-1, FR65-17 : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-6`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
