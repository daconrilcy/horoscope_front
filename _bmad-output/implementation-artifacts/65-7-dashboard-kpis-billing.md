# Story 65.7 : Dashboard — KPIs billing (échecs de paiement, revenu, Stripe summary)

Status: ready-for-dev

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

- [ ] Créer l'endpoint `GET /api/v1/admin/dashboard/kpis-billing?period=7d&plan=all` dans `admin_dashboard.py` (AC: 1, 3)
  - [ ] Échecs de paiement sur période : `SELECT count(*) FROM user_subscriptions WHERE failure_reason IS NOT NULL AND updated_at >= start_date`
  - [ ] Revenu estimé sur période : calcul approximatif MRR × (jours / 30) pour les abonnements actifs
  - [ ] Répartition par plan : `SELECT bp.code, count(*), SUM(bp.monthly_price_cents) FROM user_subscriptions JOIN billing_plans WHERE status = 'active' GROUP BY bp.code`
- [ ] Créer le schéma `KpisBillingResponse` (AC: 1)
  - [ ] Champs : `payment_failures: int`, `estimated_revenue_cents: int`, `revenue_by_plan: list[{plan_code, count, revenue_cents}]`
- [ ] Intégrer dans `frontend/src/pages/admin/AdminDashboardPage.tsx` (AC: 1, 2, 3)
  - [ ] Section "Billing" distincte des KPIs snapshot et flux
  - [ ] Compteur d'échecs de paiement cliquable → navigation vers `/admin/users?filter=payment_failure` (AC: 2)
  - [ ] Répartition revenu par plan : tableau ou mini-graphe à barres
  - [ ] Les filtres de période/plan partagés avec Story 65-6 déclenchent aussi ce fetch
- [ ] Ajouter un lien "Voir le détail complet →" vers `/admin/billing` (section Billing à implémenter dans un epic futur)
- [ ] CSS dans `AdminDashboardPage.css` pour la section billing (AC: 1)
  - [ ] Style de la section billing distincte des autres sections
  - [ ] Compteur cliquable : cursor pointer + survol `var(--primary)`

## Dev Notes

### Contexte architectural
- **Source de données** : uniquement DB applicative (`user_subscriptions`, `billing_plans`) — **pas d'appel Stripe API**
- **Revenu "estimé"** : clairement labellisé comme estimation dans l'UI (label "Revenu estimé (MRR appliqué)" ou similaire) — les données réelles sont dans Stripe
- **Échecs de paiement** : `UserSubscriptionModel.failure_reason` est la source — un `failure_reason IS NOT NULL` indique un échec récent
- **Filtre partagé** : le contexte de filtre (période + plan) est partagé entre Stories 65-5, 65-6 et 65-7 — tous les trois fetches se déclenchent avec les mêmes paramètres. Implémenter l'état des filtres dans `AdminDashboardPage` et le passer à chaque section

### Navigation vers Users filtrés
- L'AC 2 demande de rediriger vers `/admin/users?filter=payment_failure` — la page Users n'existe pas encore (Story 65-8), mais préparer le lien maintenant avec les query params. La page Users les consommera quand elle sera implémentée

### Project Structure Notes
- Modifier : `backend/app/api/v1/routers/admin_dashboard.py` (ajout endpoint billing)
- Modifier : `frontend/src/pages/admin/AdminDashboardPage.tsx` + `.css`
- Prerequisite : Stories 65-5 et 65-6 doivent être livrées ou en cours

### References
- `backend/app/infra/db/models/billing.py` — `UserSubscriptionModel.failure_reason`, `BillingPlanModel.monthly_price_cents` [Source: session context]
- Epic 65 FR65-1, FR65-17 : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-7`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
