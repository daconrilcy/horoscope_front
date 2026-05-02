# Target Files

## Must Read

- `AGENTS.md`
- `_condamad/stories/harden-local-dev-stack-script/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `scripts/start-dev-stack.ps1`
- `scripts/stripe-listen-webhook.ps1`
- `scripts/ownership-index.md`
- `backend/app/tests/unit/test_scripts_ownership.py`
- `backend/app/tests/unit/test_backend_quality_test_ownership.py`
- `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md`
- `docs/development-guide-backend.md`

## Must Search

- `rg --files backend | rg 'test_start_dev_stack_script|test_scripts|ownership|quality_test_ownership'`
- `rg -n "start-dev-stack|stripe-listen-webhook|WithStripe|SkipStripe|Get-Command stripe" scripts docs backend/app/tests`
- `rg -n "fallback|compat|alias|SkipStripe" scripts/start-dev-stack.ps1`

## Likely Modified

- `scripts/start-dev-stack.ps1`
- `backend/app/tests/unit/test_start_dev_stack_script.py`
- `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md`
- `docs/local-dev-stack.md`
- `_condamad/stories/harden-local-dev-stack-script/dev-stack-usage-evidence.md`
- `_condamad/stories/harden-local-dev-stack-script/generated/*.md`

## Forbidden Unless Justified

- `scripts/stripe-listen-webhook.ps1`
- `scripts/stripe-listen-webhook.sh`
- Backend runtime API/application files
- Frontend application files

## Existing Tests To Inspect First

- `backend/app/tests/unit/test_scripts_ownership.py`
- `backend/app/tests/unit/test_backend_quality_test_ownership.py`
- `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py`
