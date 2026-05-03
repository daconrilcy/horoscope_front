# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-005-define-central-stripe-timeout-and-retry-policy
- Source story: `_condamad/stories/CS-005-define-central-stripe-timeout-and-retry-policy/00-story.md`
- Capsule path: `_condamad/stories/CS-005-define-central-stripe-timeout-and-retry-policy`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/CS-005-define-central-stripe-timeout-and-retry-policy/00-story.md`
- Initial `git status --short`: `M _condamad/stories/story-status.md`; `?? _condamad/stories/CS-005-define-central-stripe-timeout-and-retry-policy/`
- Pre-existing dirty files: `_condamad/stories/story-status.md`, `_condamad/stories/CS-005-define-central-stripe-timeout-and-retry-policy/`
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes, then restored on canonical case-sensitive story path after Windows path casing collision.
- Regression guardrails considered: `RG-004`, `RG-006`, `RG-024`; new invariant `RG-025` added.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status updated to ready-to-review. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Story-specific. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | All ACs PASS. |
| `generated/04-target-files.md` | yes | yes | PASS | Story-specific targets. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Commands executed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | RG-004/RG-006/RG-024 mapped. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `backend/app/core/config.py` adds `stripe_timeout_seconds` and `stripe_max_network_retries`; `backend/app/infra/stripe/client.py` passes both to `stripe.StripeClient`. | Targeted tests passed; full `pytest -q` passed. | PASS | Defaults: 10 seconds, 2 retries. |
| AC2 | `test_stripe_client.py` adds AST guard; `RG-025` records invariant. | Ownership scan classifies only infra Stripe hits plus unrelated LLM timeout false positives. | PASS | No second Stripe client owner. |
| AC3 | Checkout and portal timeout tests assert `stripe_api_error` mapping. | Targeted tests passed; full `pytest -q` passed. | PASS | Existing public mapping preserved. |
| AC4 | Startup timeout tests document warn fail-open and strict fail-closed; webhook transient hydration test asserts retryable 500; admin refresh maps Stripe errors. | Targeted tests passed; full `pytest -q` passed. | PASS | Webhook remains fail-closed/retryable. |
| AC5 | `.env.example` documents `STRIPE_TIMEOUT_SECONDS` and `STRIPE_MAX_NETWORK_RETRIES`; `test_stripe_client.py` checks env loading. | Env/settings scan and tests passed. | PASS | Operator docs follow config source. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `.env.example` | modified | Document Stripe timeout/retry env vars. | AC5 |
| `_condamad/stories/regression-guardrails.md` | modified | Add `RG-025` durable invariant. | AC2, AC5 |
| `_condamad/stories/story-status.md` | modified | Set CS-005 to ready-to-review. | AC1-AC5 |
| `_condamad/stories/CS-005-define-central-stripe-timeout-and-retry-policy/**` | added | Story capsule and evidence. | AC1-AC5 |
| `backend/app/core/config.py` | modified | Load Stripe network policy settings. | AC1, AC5 |
| `backend/app/infra/stripe/client.py` | modified | Apply timeout/retry and cache by policy. | AC1, AC2 |
| `backend/app/services/billing/stripe_billing_profile_service.py` | modified | Map admin refresh Stripe failures to service error. | AC4 |
| `backend/app/tests/unit/test_stripe_client.py` | modified | Runtime policy and ownership guard tests. | AC1, AC2, AC5 |
| `backend/app/tests/unit/test_stripe_checkout_service.py` | modified | Checkout timeout mapping test. | AC3 |
| `backend/app/tests/unit/test_stripe_customer_portal_service.py` | modified | Portal timeout mapping test. | AC3 |
| `backend/app/tests/unit/test_stripe_portal_startup_validation.py` | modified | Startup transient failure decision tests. | AC4 |
| `backend/app/tests/unit/test_stripe_billing_profile_service.py` | modified | Admin refresh transient failure mapping test. | AC4 |
| `backend/app/tests/integration/test_stripe_webhook_api.py` | modified | Webhook hydration transient failure test. | AC4 |

## Files deleted

- None.

## Tests added or updated

- `test_get_stripe_client_returns_client_when_secret_present`
- `test_stripe_client_cache_is_keyed_by_network_policy`
- `test_stripe_network_policy_settings_have_operator_defaults`
- `test_stripe_network_policy_settings_are_loaded_from_env`
- `test_stripe_network_policy_is_owned_by_config_and_infra_client`
- `test_create_checkout_session_timeout_keeps_stripe_api_error_mapping`
- `test_create_portal_session_timeout_keeps_stripe_api_error_mapping`
- `test_startup_validation_timeout_is_fail_open_in_warn_mode`
- `test_startup_validation_timeout_is_fail_closed_in_strict_mode`
- `test_force_admin_subscription_refresh_timeout_keeps_admin_error_mapping`
- `test_webhook_transient_hydration_failure_is_retryable`

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py _condamad\stories\CS-005-define-central-stripe-timeout-and-retry-policy\00-story.md --root . --story-key CS-005-define-central-stripe-timeout-and-retry-policy --with-optional` | repo root | PASS | 0 | Created initial generated capsule, then canonical path restored due Windows case collision. |
| `pytest -q app/tests/unit/test_stripe_client.py app/tests/unit/test_stripe_checkout_service.py app/tests/unit/test_stripe_customer_portal_service.py app/tests/unit/test_stripe_portal_startup_validation.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/integration/test_stripe_webhook_api.py` | `backend/` | FAIL | 1 | First run found missing `stripe` import in startup test. |
| `pytest -q app/tests/unit/test_stripe_client.py app/tests/unit/test_stripe_checkout_service.py app/tests/unit/test_stripe_customer_portal_service.py app/tests/unit/test_stripe_portal_startup_validation.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/integration/test_stripe_webhook_api.py` | `backend/` | PASS | 0 | 87 passed before strict invalid-config tests. |
| `rg -n "timeout|max_network_retries|StripeClient\(" app/infra/stripe app/services/billing app/api/v1/routers app/startup -g "*.py"` | `backend/` | PASS | 0 | Stripe policy hits only in infra client; remaining timeout hits are unrelated LLM/natal API error-code references. |
| `rg -n "from app\.api|import app\.api|HTTPException|JSONResponse|fastapi" app/services/billing app/infra/stripe app/startup -g "*.py"` | `backend/` | PASS | 1 | Zero hits. |
| `ruff format app/infra/stripe/client.py app/core/config.py app/services/billing/stripe_billing_profile_service.py app/tests/unit/test_stripe_client.py app/tests/unit/test_stripe_checkout_service.py app/tests/unit/test_stripe_customer_portal_service.py app/tests/unit/test_stripe_portal_startup_validation.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/integration/test_stripe_webhook_api.py` | `backend/` | PASS | 0 | 3 files reformatted, 6 unchanged. |
| `ruff check app/infra/stripe app/core/config.py app/services/billing app/startup/stripe_portal_validation.py app/tests/unit/test_stripe_client.py app/tests/unit/test_stripe_checkout_service.py app/tests/unit/test_stripe_customer_portal_service.py app/tests/unit/test_stripe_portal_startup_validation.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/integration/test_stripe_webhook_api.py` | `backend/` | PASS | 0 | All checks passed. |
| `pytest -q` | `backend/` | PASS | 0 | 3572 passed, 12 skipped in 700.98s. |
| `ruff check .` | `backend/` | PASS | 0 | All checks passed. |
| `python -c "from app.main import app; print(len(app.routes))"` | `backend/` | PASS | 0 | App imports successfully; 220 routes registered. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-005-define-central-stripe-timeout-and-retry-policy --final` | repo root | PASS | 0 | CONDAMAD validation passed after traceability table cleanup. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; Git emitted line-ending warnings only. |
| `ruff format app/core/config.py app/tests/unit/test_stripe_client.py` | `backend/` | PASS | 0 | 2 files left unchanged after strict invalid-config tests. |
| `ruff check app/infra/stripe app/core/config.py app/services/billing app/startup/stripe_portal_validation.py app/tests/unit/test_stripe_client.py app/tests/unit/test_stripe_checkout_service.py app/tests/unit/test_stripe_customer_portal_service.py app/tests/unit/test_stripe_portal_startup_validation.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/integration/test_stripe_webhook_api.py` | `backend/` | PASS | 0 | All checks passed. |
| `pytest -q app/tests/unit/test_stripe_client.py app/tests/unit/test_stripe_checkout_service.py app/tests/unit/test_stripe_customer_portal_service.py app/tests/unit/test_stripe_portal_startup_validation.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/integration/test_stripe_webhook_api.py` | `backend/` | PASS | 0 | 90 passed after strict invalid-config tests. |
| `ruff check .` | `backend/` | PASS | 0 | Final global lint passed. |
| `pytest -q` | `backend/` | PASS | 0 | Final full suite: 3575 passed, 12 skipped in 691.30s. |
| `python -c "from app.main import app; print(len(app.routes))"` | `backend/` | PASS | 0 | Final app import succeeded; 220 routes registered. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| None | no | All required commands ran. | None. | Full backend tests and lint passed. |

## DRY / No Legacy evidence

| Pattern | File | Classification | Action | Status |
|---|---|---|---|---|
| `stripe.StripeClient(` | `backend/app/infra/stripe/client.py` | canonical owner | Kept and hardened. | PASS |
| `timeout|max_network_retries` | `backend/app/infra/stripe/client.py` | canonical SDK policy | Kept. | PASS |
| `stripe_timeout_seconds|stripe_max_network_retries` | `backend/app/core/config.py` | canonical config source | Kept. | PASS |
| `timeout` in public LLM/natal routers | `backend/app/api/v1/routers/public/*.py` | false positive | Not Stripe network policy. | PASS |
| `from app.api|import app.api|HTTPException|JSONResponse|fastapi` | services/infra/startup scan | zero-hit | No action. | PASS |

## Diff review

- `git diff --stat`: story-scoped backend/config/test/evidence files only.
- `git diff --check`: PASS; only Git line-ending warnings.

## Final worktree status

```text
 M .env.example
 M _condamad/stories/regression-guardrails.md
 M _condamad/stories/story-status.md
 M backend/app/core/config.py
 M backend/app/infra/stripe/client.py
 M backend/app/services/billing/stripe_billing_profile_service.py
 M backend/app/tests/integration/test_stripe_webhook_api.py
 M backend/app/tests/unit/test_stripe_billing_profile_service.py
 M backend/app/tests/unit/test_stripe_checkout_service.py
 M backend/app/tests/unit/test_stripe_client.py
 M backend/app/tests/unit/test_stripe_customer_portal_service.py
 M backend/app/tests/unit/test_stripe_portal_startup_validation.py
?? _condamad/stories/CS-005-define-central-stripe-timeout-and-retry-policy/
```

## Remaining risks

- None identified.

## Suggested reviewer focus

- Confirm the chosen defaults (`10s`, `2` retries) match operational expectations.
- Review `RG-025` and the AST guard for ownership strictness.
