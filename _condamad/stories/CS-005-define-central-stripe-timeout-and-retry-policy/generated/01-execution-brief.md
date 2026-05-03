# Execution Brief - CS-005-define-central-stripe-timeout-and-retry-policy

## Primary objective

Implementer une politique reseau Stripe explicite, centrale et operable depuis `app.core.config`, appliquee uniquement par `app.infra.stripe.client.get_stripe_client`.

## Boundaries

- Modifier seulement la configuration, le client infra Stripe, les tests billing/Stripe cibles, `.env.example`, et les preuves CONDAMAD.
- Ne pas changer la version API Stripe.
- Ne pas creer de second wrapper ou de proprietaire concurrent.
- Conserver les contrats d'erreur HTTP via les services/adaptateurs existants.

## Done when

- AC1 a AC5 ont une preuve code et validation.
- Les tests Stripe cibles passent dans le venv.
- Les scans prouvent l'ownership unique de `StripeClient`, `timeout` et `max_network_retries`.
- `10-final-evidence.md` et `story-status.md` sont synchronises.
