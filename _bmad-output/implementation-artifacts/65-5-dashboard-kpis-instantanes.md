# Story 65.5 : Dashboard — KPIs instantanés (inscrits, actifs, MRR)

Status: ready-for-dev

## Story

En tant qu'**admin business**,  
je veux voir les métriques de santé instantanées du produit sur le tableau de bord,  
afin de comprendre en quelques secondes la taille de la base, l'activité et le revenu courant.

## Acceptance Criteria

1. **Given** l'admin accède à `/admin/dashboard`  
   **When** la page charge  
   **Then** les KPIs instantanés suivants sont affichés sans filtre de période :
   - Inscrits totaux (count `users`)
   - Utilisateurs actifs 7j (users avec au moins 1 génération ou message dans les 7 derniers jours)
   - Utilisateurs actifs 30j
   - Abonnements actifs par plan (free / basic / premium) — count + %
   - MRR estimé (sum `monthly_price_cents` des abonnements `status = active`)
   - ARR estimé (MRR × 12)
   - Essais en cours (abonnements `status = trial`)

2. **Given** les KPIs sont calculés  
   **When** la page est affichée  
   **Then** chaque KPI affiche une valeur numérique avec son label et son unité  
   **And** les données sont issues de la DB applicative (pas d'appel Stripe direct)  
   **And** un indicateur de date/heure de dernière mise à jour est visible

3. **Given** les données sont en cours de chargement  
   **When** la requête API est pendante  
   **Then** chaque carte KPI affiche un état de chargement (skeleton ou spinner)

## Tasks / Subtasks

- [ ] Créer l'endpoint backend `GET /api/v1/admin/dashboard/kpis-snapshot` (AC: 1, 2)
  - [ ] Nouveau router `backend/app/api/v1/routers/admin_dashboard.py`
  - [ ] Guard : `Depends(require_admin_user)` (de Story 65-2)
  - [ ] Requête SQL : `SELECT count(*) FROM users` (inscrits totaux)
  - [ ] Requêtes actifs 7j / 30j : JOIN avec `llm_call_logs` ou `token_usage_log` — identifier la bonne table de "dernière activité"
  - [ ] Requête abonnements : `SELECT plan_code, count(*) FROM user_subscriptions WHERE status = 'active' GROUP BY plan_code` + JOIN `billing_plans`
  - [ ] MRR : `SELECT SUM(bp.monthly_price_cents) FROM user_subscriptions us JOIN billing_plans bp ON us.plan_id = bp.id WHERE us.status = 'active'`
  - [ ] ARR : MRR × 12 (calcul applicatif)
  - [ ] Essais : `SELECT count(*) FROM user_subscriptions WHERE status = 'trial'`
  - [ ] Ajouter `generated_at: datetime` dans la réponse (utc_now)
- [ ] Créer le schéma Pydantic de réponse `KpisSnapshotResponse` (AC: 1, 2)
  - [ ] Placer dans `backend/app/api/v1/schemas/admin_dashboard.py`
- [ ] Enregistrer le nouveau router dans `backend/app/api/v1/router.py` (ou `main.py`) (AC: 1)
- [ ] Créer `frontend/src/pages/admin/AdminDashboardPage.tsx` (AC: 1, 2, 3)
  - [ ] Fetching via `useEffect` + `fetch` (ou hook API existant du projet)
  - [ ] État de chargement → afficher `KpiCardSkeleton` pour chaque KPI
  - [ ] Afficher les cartes KPI avec label, valeur, unité
  - [ ] Afficher `generated_at` formaté en bas de page
- [ ] Créer `frontend/src/pages/admin/AdminDashboardPage.css` (AC: 3)
  - [ ] Grille de cartes KPI : CSS grid ou flex
  - [ ] `.kpi-card` avec `var(--glass)`, `var(--glass-border)`, `var(--text-1)`, `var(--text-2)`
  - [ ] `.kpi-card--skeleton` pour l'état de chargement
- [ ] Ajouter les clés i18n dans namespace `admin` pour les labels KPI (AC: 2)

## Dev Notes

### Contexte architectural
- **Tables à requêter** : `users`, `user_subscriptions`, `billing_plans` — vérifier les noms exacts dans `backend/app/infra/db/models/`
- **`UserSubscriptionModel`** : champs `status` (`active`, `trial`, `cancelled`, `expired`), `plan_id` FK vers `billing_plans`
- **`BillingPlanModel`** : champs `monthly_price_cents`, `code` (free/basic/premium), `display_name`
- **Activité utilisateur** : pour "actifs 7j/30j", vérifier quelle table trace les dernières activités — candidates : `llm_observability` (`LlmCallLogModel`), `token_usage_log`, ou `chat_messages`. Utiliser la table la plus fiable disponible. Si pas de table d'activité claire, compter les users ayant un `updated_at` récent en fallback MVP
- **Pas d'appel Stripe** : toutes les données viennent de la DB applicative — jamais d'appel `stripe.subscription.retrieve` dans ce endpoint
- **Guard** : `require_admin_user` de `backend/app/api/dependencies/auth.py` (implémenté en Story 65-2, mais peut être développé en parallèle ou après)

### Nouveau router backend
Créer `admin_dashboard.py` dans `backend/app/api/v1/routers/`. Prefix `/admin/dashboard`. Le router doit être enregistré dans le fichier central de routing (vérifier `backend/app/api/v1/router.py` ou `backend/app/main.py`).

### Frontend — pattern de fetching
Identifier le pattern standard du projet pour les appels API (hooks custom, `fetch` direct, `axios`, etc.) — vérifier dans `frontend/src/api/` ou `frontend/src/hooks/` — suivre le même pattern plutôt que réinventer.

### CSS — aucun style inline
Variables à utiliser : `var(--glass)`, `var(--glass-2)`, `var(--glass-border)`, `var(--text-1)`, `var(--text-2)`, `var(--primary)`, `var(--success)`, `var(--line)`, `var(--bg-base)`

### Project Structure Notes
- Nouveau backend : `backend/app/api/v1/routers/admin_dashboard.py` + `backend/app/api/v1/schemas/admin_dashboard.py`
- Nouveau frontend : `frontend/src/pages/admin/AdminDashboardPage.tsx` + `.css`
- Prerequisite : Story 65-4 (navigation) doit être livrée pour que la route `/admin/dashboard` soit définie dans le router React

### References
- `backend/app/infra/db/models/billing.py` — `UserSubscriptionModel`, `BillingPlanModel` [Source: session context]
- `backend/app/infra/db/models/user.py` — `UserModel` [Source: session context]
- Epic 65 FR65-1, FR65-17 : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-5`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
