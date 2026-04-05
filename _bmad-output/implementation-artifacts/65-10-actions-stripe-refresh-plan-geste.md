# Story 65.10 : Actions avec effets Stripe — refresh abonnement, plan manuel, geste commercial

Status: ready-for-dev

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

- [ ] Endpoint `POST /api/v1/admin/users/{user_id}/refresh-subscription` (AC: 1)
  - [ ] Récupérer le `stripe_subscription_id` de l'utilisateur depuis la DB
  - [ ] Appeler `stripe.Subscription.retrieve(stripe_subscription_id)` via le SDK Stripe existant
  - [ ] Mettre à jour `user_subscriptions` en DB : statut + plan_id depuis la réponse Stripe
  - [ ] Capturer l'état avant pour le audit log
  - [ ] Générer l'audit log via `AuditService`
  - [ ] Si pas de `stripe_subscription_id` → erreur 400 avec message explicite
- [ ] Endpoint `POST /api/v1/admin/users/{user_id}/assign-plan` body: `{plan_code: str, reason: str}` (AC: 2)
  - [ ] Validation backend : `reason` non vide (longueur min. 5 caractères)
  - [ ] Trouver le plan par `plan_code` dans `billing_plans`
  - [ ] Mettre à jour `user_subscriptions.plan_id` en DB — **aucun appel Stripe**
  - [ ] Générer l'audit log avec `reason` dans `details`
- [ ] Endpoint `POST /api/v1/admin/users/{user_id}/commercial-gesture` body: `{gesture_type: str, value: int, reason: str}` (AC: 3)
  - [ ] Identifier où stocker le geste commercial — probablement champ JSON dans `user_subscriptions` ou nouvelle colonne
  - [ ] Appliquer le geste en DB (quota supplémentaire ou extension de date selon `gesture_type`)
  - [ ] Générer l'audit log
- [ ] Mettre à jour `frontend/src/pages/admin/AdminUserDetailPage.tsx` (AC: 1, 2, 3)
  - [ ] Bouton "Refresh abonnement" avec modale d'avertissement explicite (badge rouge "Synchronisation Stripe")
  - [ ] Bouton "Attribuer un plan" avec modale : sélecteur de plan + champ motif obligatoire + badge "Applicatif uniquement"
  - [ ] Bouton "Geste commercial" avec modale : type + valeur + motif + badge "Applicatif uniquement"
  - [ ] Feedback ≤ 200ms sur tous les boutons (NFR3)
  - [ ] Rafraîchissement de la fiche après chaque action réussie

## Dev Notes

### Indicateur de périmètre (FR65-16)
Chaque action doit afficher dans l'UI un badge coloré indiquant son périmètre :
- Badge vert "Applicatif uniquement" → `var(--success)` background
- Badge orange "Synchronisation Stripe (lecture+écriture)" → `var(--primary)` ou couleur warning
**Ce badge est OBLIGATOIRE** dans la modale de confirmation — c'est une exigence explicite FR65-16

### SDK Stripe
Vérifier comment le SDK Stripe est utilisé dans le projet — probablement `backend/app/infra/stripe/` ou un service `stripe_service.py`. Ne pas instancier Stripe directement dans le router — passer par le service existant.

### Refresh abonnement — périmètre exact
- **Lecture Stripe** : `stripe.Subscription.retrieve()` pour lire le statut et le `price_id`
- **Écriture DB** : mise à jour de `user_subscriptions.status` et `plan_id` (via mapping `price_id → plan_code`)
- **Aucune écriture Stripe** : ne jamais appeler `stripe.Subscription.modify()` ou équivalent

### Plan manuel — uniquement pour plans internes
La note FR65-3 précise "uniquement pour des plans internes ou des périodes d'essai prolongées" — ajouter un avertissement dans l'UI si le plan sélectionné est un plan Stripe (plan avec `stripe_price_id` non null) pour éviter les incohérences.

### Geste commercial
Identifier la structure du geste commercial en DB :
- Option A : champ `commercial_gesture JSON` dans `user_subscriptions`
- Option B : table dédiée `commercial_gestures`
- Choisir la solution la plus simple (Option A pour MVP) en vérifiant les migrations existantes

### References
- `backend/app/infra/db/models/billing.py` — `UserSubscriptionModel` [Source: session context]
- SDK Stripe : vérifier `backend/app/infra/stripe/` [Source: architecture]
- Epic 65 FR65-3, FR65-16, NFR3, NFR8 : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-10`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
