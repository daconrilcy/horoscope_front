# Story 65.10 : Actions avec effets Stripe — refresh abonnement, plan manuel, geste commercial

Status: done

## Story

En tant qu'**admin billing/support**,  
je veux pouvoir resynchroniser un abonnement depuis Stripe, attribuer un plan manuellement ou enregistrer un geste commercial,  
afin de corriger des incohérences ou accorder des exceptions sans toucher à la facturation.

## Acceptance Criteria

1. **Given** l'admin clique "Forcer un refresh d'abonnement" sur une fiche utilisateur  
   **When** la modale s'affiche  
   **Then** un avertissement explicite est visible : "Cette action resynchronise le statut et le plan depuis Stripe en lecture+écriture. Aucun changement de facturation ne sera effectué côté Stripe."  
   **And** après confirmation, l'abonnement DB est mis à jour depuis Stripe (statut, plan_id)  
   **And** un audit log : `action: "subscription_refresh_forced"`, `details: {before: {...}, after: {...}}`

2. **Given** l'admin attribue un plan manuellement  
   **When** la modale s'ouvre  
   **Then** un sélecteur de plan est disponible + un champ de motif **obligatoire**  
   **And** le badge "Applicatif uniquement — sans effet Stripe" est visible  
   **And** après confirmation avec motif saisi, le plan en DB est mis à jour  
   **And** un audit log : `action: "plan_manually_assigned"`, `details: {before: plan_code_avant, after: plan_code_après, reason: "..."}`

3. **Given** l'admin enregistre un geste commercial  
   **When** la modale s'ouvre  
   **Then** les champs disponibles : type de geste (jours supplémentaires / messages supplémentaires), valeur numérique, motif (optionnel)  
   **And** le badge "Applicatif uniquement — aucun crédit Stripe" est visible  
   **And** après confirmation, un flag `commercial_gesture` est appliqué sur l'abonnement  
   **And** un audit log : `action: "commercial_gesture_recorded"`, `details: {gesture_type, value, reason, before, after}`

## Tasks / Subtasks

- [x] Migration Alembic : ajouter `commercial_gestures` (JSON) à `user_subscriptions`
- [x] Endpoint `POST /api/v1/admin/users/{user_id}/refresh-subscription` (AC: 1)
  - [x] Récupérer via SDK Stripe
  - [x] Update local DB via `StripeBillingProfileService`
  - [x] Audit log `subscription_refresh_forced`
- [x] Endpoint `POST /api/v1/admin/users/{user_id}/assign-plan` (AC: 2)
  - [x] Validation raison min 5 chars
  - [x] Update local DB `entitlement_plan`
  - [x] Invalidation cache billing
  - [x] Audit log `plan_manually_assigned`
- [x] Endpoint `POST /api/v1/admin/users/{user_id}/commercial-gesture` (AC: 3)
  - [x] Stockage JSON dans `user_subscriptions`
  - [x] Audit log `commercial_gesture_recorded`
- [x] Mettre à jour `frontend/src/pages/admin/AdminUserDetailPage.tsx` (AC: 1, 2, 3)
  - [x] Boutons d'action
  - [x] Modales dédiées pour refresh / assignation / geste commercial
  - [x] Feedback de chargement
- [x] Tests d'intégration backend `backend/app/tests/integration/test_admin_stripe_actions_api.py`

### File List
- `backend/app/infra/db/models/billing.py`
- `backend/migrations/versions/35adfdeeceb4_add_commercial_gestures_to_user_.py`
- `backend/app/api/v1/routers/admin_users.py`
- `frontend/src/pages/admin/AdminUserDetailPage.tsx`
- `frontend/src/pages/admin/AdminUserDetailPage.css`
- `backend/app/tests/integration/test_admin_stripe_actions_api.py`

### Completion Notes List

- Revue AI du 2026-04-06 : la story était marquée done alors que les actions Stripe n'étaient pas réellement exposées dans la fiche utilisateur. L'UI admin a été complétée avec des actions visibles, des modales explicites de périmètre et des formulaires pour le plan manuel et le geste commercial.

## Senior Developer Review (AI)

- Corrigé le faux positif d'implémentation côté frontend : les endpoints existaient, mais l'UI ne permettait pas d'exécuter les actions annoncées par les AC.
- La story reste `done` après correction : l'écran expose maintenant `refresh-subscription`, `assign-plan` et `commercial-gesture` avec un wording de périmètre conforme.
