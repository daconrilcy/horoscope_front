# Story 61.3 : Endpoint `POST /v1/billing/stripe-checkout-session`

Status: done

## Story

En tant qu'utilisateur authentifié,
je veux que le backend crée une Stripe Checkout Session d'abonnement lorsque je demande à souscrire à un plan,
afin d'être redirigé vers la page de paiement Stripe sécurisée sans que le backend ne manipule directement ma carte bancaire.

## Contexte métier et position dans l'Epic 61

```
61-1 (done) : table DB + service de mapping StripeBillingProfileService
61-2 (done) : SDK stripe==14.4.1 + StripeClient + secrets + STRIPE_PRICE_ENTITLEMENT_MAP alimentée
61-3 (cette story) : endpoint create_checkout_session via get_stripe_client()
61-4 (à venir) : Webhook handler + vérification de signature
```

L'endpoint reçoit `plan` ("basic" | "premium") depuis un utilisateur JWT authentifié, retrouve ou crée son `stripe_customer_id`, puis crée une Checkout Session Stripe en mode `subscription`. Stripe recommande de créer une **nouvelle session à chaque tentative** — pas d'idempotence de session (à la différence des PaymentIntent).

## Acceptance Criteria

1. [x] **Endpoint exposé** : `POST /v1/billing/stripe-checkout-session` est accessible et requiert un JWT valide. Un utilisateur avec rôle autre que `"user"` ou `"admin"` reçoit un 403.

2. [x] **Paramètre `plan` validé** : le corps de la requête contient `{"plan": "basic"}` ou `{"plan": "premium"}`. Toute autre valeur retourne un 422 `invalid_checkout_request`.

3. [x] **Stripe indisponible** : si `get_stripe_client()` retourne `None` (clé absente), l'endpoint retourne un 503 `stripe_unavailable` sans crash.

4. [x] **Price ID introuvable** : si le `plan` demandé n'a pas de `price_id` dans `STRIPE_PRICE_ENTITLEMENT_MAP` (variable d'env absente), l'endpoint retourne un 422 `plan_price_not_configured`.

5. [x] **`stripe_customer_id` récupéré ou créé** : avant l'appel Stripe, `StripeBillingProfileService.get_or_create_profile(db, user_id)` est appelé. Si le profil a déjà un `stripe_customer_id`, il est passé dans le paramètre `customer` de la session. Sinon, `customer_email` de l'utilisateur est utilisé. Si le profil n'a pas de `stripe_customer_id` **et** que `current_user.email` est absent ou vide, l'endpoint retourne un 422 `invalid_checkout_request` (impossible de créer la session sans identifier le client).

6. [x] **Session créée avec les bons paramètres** : la Checkout Session créée via le SDK Stripe inclut obligatoirement :
   - `mode="subscription"`
   - `line_items=[{"price": price_id, "quantity": 1}]`
   - `success_url` (depuis config `settings.stripe_checkout_success_url`)
   - `cancel_url` (depuis config `settings.stripe_checkout_cancel_url`)
   - `client_reference_id=str(user_id)` (réconciliation user interne)
   - `metadata={"app_user_id": str(user_id)}`
   - `customer=stripe_customer_id` OU `customer_email=user.email` (jamais les deux simultanément)
   - `subscription_data={"metadata": {"app_user_id": str(user_id), "plan": plan}}`

7. [x] **Réponse nominale** : l'endpoint retourne `{"data": {"checkout_url": "<url_stripe>"}, "meta": {"request_id": "..."}}` avec HTTP 200.

8. [x] **Erreur Stripe API** : toute `stripe.StripeError` est interceptée et retourne un 502 `stripe_api_error` avec log d'erreur.

9. [x] **Audit** : chaque tentative de création de session (succès ou échec) est loguée via `_record_audit_event`.

10. [x] **Rate limiting** : l'endpoint applique les limites de `_enforce_billing_limits` avec `operation="stripe_checkout"`.

11. [x] **Config** : deux nouvelles variables `STRIPE_CHECKOUT_SUCCESS_URL` et `STRIPE_CHECKOUT_CANCEL_URL` ajoutées.

12. [x] **Non-régression** : ruff et pytest passent (avec mocks).

13. [x] **Tests unitaires** : `StripeCheckoutService` testé.

14. [x] **Tests d'intégration** : Endpoint HTTP testé.

## Tasks / Subtasks

- [x] **Config — nouvelles variables** (AC: 11)
- [x] **Service `StripeCheckoutService`** (AC: 3, 4, 5, 6, 8)
- [x] **Endpoint HTTP** (AC: 1, 2, 7, 9, 10)
- [x] **Tests unitaires** (AC: 13)
- [x] **Tests d'intégration** (AC: 14)
- [x] **Validation finale** (AC: 12)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List
- Implemented `POST /v1/billing/stripe-checkout-session`.
- Added `StripeCheckoutService` for session creation with proper `customer` / `customer_email` handling.
- Added unit tests for the service and integration tests for the API.
- Fixed code review findings: added missing audit log in `ValidationError` block and improved model validation with `Literal`.
- Verified with `ruff` and `pytest` (2110+ tests passing).

### File List
- backend/app/core/config.py
- .env.example
- backend/app/services/stripe_checkout_service.py
- backend/app/api/v1/routers/billing.py
- backend/app/tests/unit/test_stripe_checkout_service.py
- backend/app/tests/integration/test_stripe_checkout_api.py
