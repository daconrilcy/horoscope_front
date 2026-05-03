# Implementation Plan

## Initial repository findings

- `backend/app/api/v1/routers/public/billing.py` retourne actuellement `{"status": status}` apres `StripeWebhookService.handle_event`, y compris pour `failed_internal`.
- `StripeWebhookService.handle_event` marque deja la ligne idempotence en `failed` puis renvoie `failed_internal`.
- `StripeWebhookIdempotencyService.claim_event` accepte deja le reclaim d'une ligne `failed` et incremente `processing_attempts`.
- Les tests d'integration verrouillent aujourd'hui `HTTP 200` + `{"status": "failed_internal"}` pour les echecs signes.

## Proposed changes

- Conserver la logique metier dans `StripeWebhookService`.
- Mapper uniquement le statut logique `failed_internal` vers une erreur API centralisee dans le routeur, apres commit de la ligne idempotence.
- Ajouter la reponse OpenAPI `500` sur `/v1/billing/stripe-webhook`.
- Mettre a jour les tests API pour exiger un non-2xx retryable et l'enveloppe d'erreur.
- Mettre a jour la documentation d'idempotence et de test local.

## Files to modify

- `backend/app/api/v1/routers/public/billing.py`
- `backend/app/tests/integration/test_stripe_webhook_api.py`
- `backend/app/tests/unit/test_stripe_webhook_service.py`
- `docs/billing-webhook-idempotency.md`
- `docs/billing-webhook-local-testing.md`
- Capsule/evidence CONDAMAD.

## Files to delete

- Aucun.

## Tests to add or update

- Mettre a jour `test_webhook_app_error_returns_200`.
- Mettre a jour `test_webhook_business_failure_persists_failed_and_retry_is_accepted`.
- Ajouter/adapter une assertion service pour `failed_internal` comme outcome retryable et non terminal HTTP.

## Risk assessment

- Risque principal: lever l'erreur avant commit ferait perdre la ligne `failed`; le routeur doit donc committer avant de produire le non-2xx.
- Risque secondaire: transformer les erreurs de parsing non fatales en retry; elles doivent rester en HTTP 200.

## Rollback strategy

- Revenir au mapping routeur precedent et restaurer les assertions HTTP 200 uniquement si la decision produit abandonne le retry automatique Stripe.
