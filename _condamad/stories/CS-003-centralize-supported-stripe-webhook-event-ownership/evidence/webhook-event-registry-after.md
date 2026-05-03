# Webhook Event Registry After

Captured after convergence.

## Canonical registry owner

- `backend/app/services/billing/stripe_webhook_events.py`
- Exported records: `SUPPORTED_WEBHOOK_EVENTS`
- Exported groups:
  - `SUPPORTED_WEBHOOK_EVENT_TYPES`
  - `LOCAL_LISTENER_EVENT_TYPES`
  - `CHECKOUT_UPGRADE_EVENT_TYPES`
  - `CHECKOUT_CLIENT_REFERENCE_EVENT_TYPES`
  - `CUSTOMER_LOOKUP_EVENT_TYPES`
  - `CUSTOMER_OBJECT_ID_LOOKUP_EVENT_TYPES`

## Canonical supported events

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

## Consumer parity

- Runtime dispatch consumes `is_supported_webhook_event`.
- Runtime checkout upgrade routing consumes `CHECKOUT_UPGRADE_EVENT_TYPES`.
- Runtime user resolution consumes registry-derived resolution groups.
- PowerShell listener events equal `LOCAL_LISTENER_EVENT_TYPES`.
- Runbook and historical Stripe webhook doc include all `SUPPORTED_WEBHOOK_EVENT_TYPES`.
- Local asset guard imports the registry and fails on docs/script/runtime drift.

## Unsupported event invariant

- `invoice.payment_succeeded` is intentionally absent from `SUPPORTED_WEBHOOK_EVENT_TYPES`.
- Unit and integration tests preserve `event_ignored` behavior for `invoice.payment_succeeded`.
