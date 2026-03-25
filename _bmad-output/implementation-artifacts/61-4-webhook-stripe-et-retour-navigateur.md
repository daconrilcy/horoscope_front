# Story 61.4 : Webhook Stripe et retour navigateur

Status: done

## Story

En tant que système backend,
je veux recevoir, vérifier et traiter les événements Stripe via webhook pour mettre à jour le plan d'accès SaaS des utilisateurs,
afin que l'activation de l'abonnement soit fiable, idempotente et indépendante du retour navigateur.

En tant qu'utilisateur ayant complété le paiement Stripe,
je veux voir une page de confirmation adaptée lors de mon retour sur l'application,
afin de comprendre que mon paiement est en cours de traitement sans que cette page n'active elle-même mon accès.

## Contexte métier et position dans l'Epic 61

```text
61-1 (done) : table DB + StripeBillingProfileService + derive_entitlement_plan()
61-2 (done) : SDK stripe==14.4.1 + get_stripe_client() + secrets + STRIPE_PRICE_ENTITLEMENT_MAP
61-3 (done) : POST /v1/billing/stripe-checkout-session (success_url avec ?session_id={CHECKOUT_SESSION_ID})
61-4 (cette story) : Webhook handler + vérification signature + pages retour navigateur
```

**Principe fondamental (Stripe officiel)**

> L'activation de l'accès SaaS DOIT être déclenchée par le webhook, pas par le retour navigateur.
> Le navigateur peut manquer des événements, être fermé, ou subir une défaillance réseau.
> Le webhook est le mécanisme fiable pour les changements d'état d'abonnement, y compris les cas asynchrones.

Le `success_url` ne sert donc qu'au confort utilisateur et, éventuellement, à de l'affichage ou du debug contrôlé. Il ne constitue jamais la source de vérité métier.

## Acceptance Criteria

### Backend — Webhook Handler

1. [x] **Endpoint exposé sans auth JWT** : `POST /v1/billing/stripe-webhook` reçoit les requêtes Stripe sans `require_authenticated_user`. Toute requête Stripe valide doit pouvoir être traitée sans JWT.

2. [x] **Vérification de signature obligatoire** : le handler lit le body brut avec `await request.body()` puis vérifie la signature Stripe à l'aide de l'API officielle `stripe.Webhook.construct_event(payload_bytes, sig_header, webhook_secret)`.
   - Si le header `stripe-signature` est absent ou invalide, retourner HTTP 400.
   - Si `settings.stripe_webhook_secret` est `None` ou vide, retourner HTTP 503 avec un code métier `webhook_secret_not_configured`.

3. [x] **Réponse rapide à Stripe** : le endpoint doit répondre sans traitement bloquant inutile afin d'éviter les retries Stripe.
   - **Signature invalide / secret absent** : erreur explicite (`400` ou `503`).
   - **Erreur applicative interne après signature valide** : logger l'erreur, auditer l'événement, puis retourner HTTP 200 pour éviter un retry non pertinent côté Stripe.

4. [x] **Événements traités** :
   - `checkout.session.completed` : extraire `client_reference_id` posé en 61-3 (attendu comme `str(user_id)`), le convertir en `int`, puis appeler `StripeBillingProfileService.update_from_event_payload(db, user_id, event_dict)`.
   - `customer.subscription.created` / `customer.subscription.updated` / `customer.subscription.deleted` : résoudre `user_id` via `StripeBillingProfileService.get_by_stripe_customer_id(db, customer_id)`, puis appeler `update_from_event_payload()`.
   - `customer.updated` : résoudre `user_id` via `StripeBillingProfileService.get_by_stripe_customer_id(db, customer_id)` où `customer_id = event.data.object.id`, puis appeler `update_from_event_payload()`.
   - Tout autre événement : logger proprement et retourner HTTP 200 avec un statut logique de type `event_ignored`.

5. [x] **Idempotence déléguée à la couche service** : `StripeBillingProfileService.update_from_event_payload()` reste la seule source de vérité pour l'idempotence, la déduplication et la gestion du désordre temporel des événements. Le handler webhook ne doit pas réimplémenter cette logique.

6. [x] **Utilisateur non résolu** : si la résolution du `user_id` échoue, logger un warning, auditer le cas, puis retourner HTTP 200. Stripe ne doit pas retenter pour une incohérence métier locale.

7. [x] **Audit** : chaque événement webhook reçu avec signature valide, qu'il soit traité, ignoré ou en échec non fatal, est enregistré via `_record_audit_event` avec `action="stripe_webhook_event"`, `target_type="stripe_event"`, `target_id=event.id`.

8. [x] **Logs structurés** : les logs doivent inclure au minimum `event_id`, `event_type`, `customer_id` si disponible, `user_id` si résolu, et l'action finale (`processed`, `ignored`, `failed_non_fatal`).

9. [x] **Tests unitaires** : `StripeWebhookService` est couvert pour les événements suivants :
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `customer.updated`
   - signature invalide
   - événement ignoré
   - utilisateur introuvable

10. [x] **Tests d'intégration** : le endpoint HTTP est testé avec payload signé valide, payload signé invalide, secret absent, et cas d'erreur applicative non fatale.

### Frontend — Pages de retour Stripe

11. [x] **Page `/billing/success`** :
   - Lit le paramètre `?session_id=cs_...` via `useSearchParams()`.
   - Affiche un état du type : **"Paiement en cours de confirmation"**.
   - Affiche un indicateur visuel de traitement.
   - Explique clairement que l'activation peut prendre quelques instants.
   - Propose un bouton **"Retour au tableau de bord"** vers `/dashboard`.
   - N'appelle aucune API destinée à activer l'accès SaaS.
   - Peut, à titre optionnel, afficher ou conserver le `session_id` pour debug ou usage futur non bloquant.

12. [x] **Page `/billing/cancel`** :
   - Affiche un état du type : **"Paiement annulé"**.
   - Affiche un message rassurant indiquant qu'aucune activation n'a eu lieu.
   - Propose un bouton **"Retour aux abonnements"** vers `/settings/subscription`.
   - Propose un bouton **"Réessayer"** vers `/billing`.

13. [x] **Aucune logique métier d'activation côté front** : ni `/billing/success` ni `/billing/cancel` ne doivent déclencher de modification d'accès, de plan ou d'entitlement. Le front reste purement informatif.

14. [x] **Routes enregistrées** : les deux pages sont ajoutées sous `AuthGuard` dans `frontend/src/app/routes.tsx`, sous la forme `/billing/success` et `/billing/cancel`.

15. [x] **i18n** : tous les textes sont externalisés dans `frontend/src/i18n/`, dans `settings.ts` si cohérent avec l'organisation existante, ou dans un nouveau fichier `billing.ts`.

16. [x] **CSS** : aucun style inline. Les pages utilisent les variables CSS existantes du design system (`var(--text-1)`, `var(--text-2)`, `var(--glass)`, `var(--glass-border)`, `var(--primary)`, etc.) dans un fichier dédié ou dans les fichiers de style existants.

### Config & Dev

17. [x] **Variable `STRIPE_WEBHOOK_SECRET`** : la variable existe déjà dans `config.py` et ne doit pas être recréée. La documentation doit expliciter les deux modes d'utilisation :
   - **mode dev** via Stripe CLI installée localement avec `winget install Stripe.StripeCLI`
   - **mode production** via endpoint déclaré dans le Dashboard Stripe

18. [x] **Documentation `.env.example`** : le fichier documente clairement la différence entre le secret de signature webhook local fourni par `stripe listen` et le secret de signature webhook production fourni par le Dashboard Stripe.

19. [x] **Non-régression** : `ruff` et `pytest` passent intégralement.

## Tasks / Subtasks

### Backend

- [x] **Créer `StripeWebhookService`** dans `backend/app/services/stripe_webhook_service.py` (AC: 2, 4, 5, 6, 8, 9)
- [x] **Ajouter le endpoint `POST /v1/billing/stripe-webhook`** dans `backend/app/api/v1/routers/billing.py` (AC: 1, 2, 3, 7, 10)
- [x] **Créer les tests unitaires** `backend/app/tests/unit/test_stripe_webhook_service.py` (AC: 9)
- [x] **Créer les tests d'intégration** `backend/app/tests/integration/test_stripe_webhook_api.py` (AC: 10)

### Frontend

- [x] **Créer `/billing/success`** dans `frontend/src/pages/billing/BillingSuccessPage.tsx` (AC: 11)
- [x] **Créer `/billing/cancel`** dans `frontend/src/pages/billing/BillingCancelPage.tsx` (AC: 12)
- [x] **Créer le CSS** dans `frontend/src/pages/billing/billing-return.css` ou fichier équivalent (AC: 16)
- [x] **Déclarer les routes** dans `frontend/src/app/routes.tsx` (AC: 14)
- [x] **Ajouter les traductions i18n** avec les clés `billingSuccess.*` et `billingCancel.*` (AC: 15)

### Config & Validation

- [x] **Documenter `.env.example`** avec les deux modes webhook (AC: 17, 18)
- [x] **Valider la non-régression** avec `ruff` et `pytest` (AC: 19)

## Dev Notes

... (unchanged) ...

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

- Fixed AuditService status validation error (received -> success)
- Fixed Button icon prop issue in frontend (icon -> leftIcon)
- Fixed i18n type exports and imports in index.ts
- **Refactoring (Post-Review):**
  - Standardized webhook flow on `stripe.Event` object for robust type safety (Issue 1).
  - Prioritized business logic processing before audit in router (Issue 2).
  - Wrapped audit in try/except to make it best-effort and non-blocking (Issue 2).
  - Removed `setTimeout` false success confirmation in `BillingSuccessPage.tsx` (Issue 3).
  - Added `session_id` extraction via `useSearchParams()` (Issue 4).
  - Aligned `BillingCancelPage.tsx` routes with story requirements (Issue 5).
  - Enhanced structured logging with systematic `customer_id` and `outcome` (Issue 6).
  - **Final Compliance:** Removed all remaining inline styles in `BillingSuccessPage.tsx` and moved them to `billing-return.css` (AC16).

### Completion Notes List

- Stripe webhook endpoint implemented at POST /v1/billing/stripe-webhook
- Signature verification using Stripe SDK (construct_event)
- Idempotent processing via StripeBillingProfileService
- Frontend success/cancel pages with glassmorphism UI
- Full i18n support for billing return flow
- All unit and integration tests passing with refactored Event object handling

### File List

- backend/app/services/stripe_webhook_service.py
- backend/app/api/v1/routers/billing.py
- backend/app/tests/unit/test_stripe_webhook_service.py
- backend/app/tests/integration/test_stripe_webhook_api.py
- frontend/src/pages/billing/BillingSuccessPage.tsx
- frontend/src/pages/billing/BillingCancelPage.tsx
- frontend/src/pages/billing/billing-return.css
- frontend/src/i18n/billing.ts
- frontend/src/i18n/index.ts
- frontend/src/app/routes.tsx
- frontend/src/i18n/astrologers.ts
- frontend/src/i18n/birthProfile.ts
- frontend/src/i18n/consultations.ts
- frontend/src/i18n/insights.ts
- frontend/src/i18n/natalChart.ts
- frontend/src/i18n/settings.ts
