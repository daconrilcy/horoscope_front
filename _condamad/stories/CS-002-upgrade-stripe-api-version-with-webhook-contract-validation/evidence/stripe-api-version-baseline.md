# Stripe API Version Baseline

## Capture

- Date: 2026-05-03
- Command: `.\.venv\Scripts\Activate.ps1; cd backend; python -c "from app.core.config import Settings; import stripe; print(Settings().stripe_api_version); print(getattr(stripe, 'VERSION', getattr(stripe, '__version__', 'unknown')))"`
- Runtime default before implementation: `2024-12-18.acacia`
- Installed Stripe SDK version: `14.4.1`
- `.env.example` value before implementation: `STRIPE_API_VERSION=2024-12-18.acacia`

## Affected contract surfaces

- `backend/app/core/config.py`: runtime default source.
- `backend/app/infra/stripe/client.py`: canonical Stripe SDK client construction.
- `backend/app/services/billing/stripe_checkout_service.py`: checkout session payload.
- `backend/app/services/billing/stripe_customer_portal_service.py`: portal, invoice preview, subscription upgrade and subscription schedule-adjacent payload assumptions.
- `backend/app/services/billing/stripe_webhook_service.py`: consumed webhook event fields.

## Baseline decision

The old default is retained only as historical evidence and rollback guidance. It must not remain an active default after CS-002.
