# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Runtime settings default is `2026-04-22.dahlia`. | `backend/app/core/config.py`, `.env.example`, baseline/after evidence. | `pytest -q app/tests/unit/test_stripe_client.py`; loaded settings command with `APP_DISABLE_BACKEND_DOTENV=1`. | PASS |
| AC2 | Infra Stripe client passes the configured version. | `backend/app/infra/stripe/client.py` remains canonical; `test_stripe_client.py` asserts the passed `stripe_version`. | `pytest -q app/tests/unit/test_stripe_client.py`. | PASS |
| AC3 | Billing Stripe flows keep existing backend contracts. | Existing checkout, portal, invoice preview, subscription upgrade and webhook payload assumptions remain unchanged. | Unit tests for checkout, customer portal and webhook services pass. | PASS |
| AC4 | Public billing integration tests still pass. | No public billing API contract change. | Integration tests for checkout, customer portal and webhook APIs pass. | PASS |
| AC5 | Upgrade evidence records SDK decision. | `evidence/stripe-api-version-baseline.md`, `evidence/stripe-api-version-after.md`, and webhook local testing docs. | Evidence/doc scan passes with classified hits. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
