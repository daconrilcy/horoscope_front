# Target Files

## Must read

- `scripts/stripe-listen-webhook.ps1`
- `scripts/stripe-listen-webhook.sh`
- `scripts/ownership-index.md`
- `scripts/start-dev-stack.ps1`
- `docs/billing-webhook-local-testing.md`
- `docs/local-dev-stack.md`
- `docs/development-guide-backend.md`
- `backend/app/tests/unit/test_scripts_ownership.py`
- `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py`
- `backend/app/tests/unit/test_start_dev_stack_script.py`
- `_condamad/audits/scripts-ops/2026-05-03-0857/02-finding-register.md`
- `_condamad/stories/regression-guardrails.md`

## Must search

- `rg -n "stripe-listen-webhook\\.sh|Git Bash|WSL|#!/usr/bin/env bash" scripts docs backend/app/tests`
- `rg --files scripts`
- `rg -n "legacy|compat|shim|fallback|deprecated|alias" scripts docs backend/app/tests`

## Likely modified

- `scripts/ownership-index.md`
- `docs/billing-webhook-local-testing.md`
- `backend/app/tests/unit/test_scripts_ownership.py`
- `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py`
- `backend/app/tests/unit/test_start_dev_stack_script.py`
- `_condamad/stories/remove-bash-stripe-dev-listener/generated/*`
- `_condamad/stories/remove-bash-stripe-dev-listener/reference-baseline.txt`
- `_condamad/stories/remove-bash-stripe-dev-listener/reference-after.txt`
- `_condamad/stories/remove-bash-stripe-dev-listener/removal-audit.md`

## Likely deleted

- `scripts/stripe-listen-webhook.sh`

## Forbidden unless justified

- `backend/app/services/billing/stripe_webhook_service.py`
- `backend/app/api/**`
- `frontend/**`
- New dependencies or replacement shell listener scripts.
