# Webhook Event Registry Baseline

Captured before convergence from the pre-existing files inspected at preflight.

## Runtime dispatch tuple

- `checkout.session.completed`
- `checkout.session.async_payment_succeeded`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `customer.subscription.paused`
- `customer.subscription.resumed`
- `customer.subscription.trial_will_end`
- `subscription_schedule.created`
- `subscription_schedule.updated`
- `subscription_schedule.canceled`
- `subscription_schedule.completed`
- `customer.updated`
- `invoice.paid`
- `invoice.payment_failed`
- `invoice.payment_action_required`

## Runtime resolver tuple

- `checkout.session.completed` via `client_reference_id`
- `checkout.session.async_payment_succeeded` via `customer`
- `customer.subscription.created` via `customer`
- `customer.subscription.updated` via `customer`
- `customer.subscription.deleted` via `customer`
- `customer.subscription.paused` via `customer`
- `customer.subscription.resumed` via `customer`
- `customer.subscription.trial_will_end` via `customer`
- `subscription_schedule.created` via `customer`
- `subscription_schedule.updated` via `customer`
- `subscription_schedule.canceled` via `customer`
- `subscription_schedule.completed` via `customer`
- `customer.updated` via object `id`
- `invoice.paid` via `customer`
- `invoice.payment_failed` via `customer`
- `invoice.payment_action_required` via `customer`

## Local listener script before convergence

- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.paid`
- `invoice.payment_failed`
- `invoice.payment_action_required`

## Docs/tests before convergence

- `docs/billing-webhook-local-testing.md` documented a standard listener subset and a separate expanded backend list.
- `docs/stripe-webhook-dev.md` documented historical rationale and an expanded backend list without async checkout or subscription schedule events.
- `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py` owned duplicated `STANDARDIZED_EVENT_LIST` and `EXTENDED_EVENT_LIST` constants and parsed service source strings.
