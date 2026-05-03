# Implementation Plan

## Initial repository findings

- `get_stripe_client` est deja le seul constructeur `stripe.StripeClient`.
- Le cache etait uniquement indexe par `api_key`.
- Aucun setting timeout/retry Stripe n'existait.
- Checkout, portal, startup validation, webhook upgrade hydration et admin refresh consomment deja la factory centrale ou les services billing.

## Proposed changes

- Ajouter `STRIPE_TIMEOUT_SECONDS=10` et `STRIPE_MAX_NETWORK_RETRIES=2`.
- Charger ces settings via `Settings`.
- Passer `timeout` et `max_network_retries` a `stripe.StripeClient`.
- Indexer le cache par secret, version API, timeout et retry.
- Ajouter tests de defaults/env/cache et garde AST d'ownership.
- Ajouter tests de timeouts/transient failures pour checkout, portal, startup, webhook et admin refresh.

## Risk assessment

- Risque principal: le SDK Stripe change son constructeur. Mitigation: test mockant les kwargs effectifs.
- Risque webhook: transitoire Stripe pendant hydration. Decision testee: fail-closed/retryable cote webhook.

## Rollback strategy

Revenir aux changements dans `config.py`, `infra/stripe/client.py`, `.env.example` et tests associes.
