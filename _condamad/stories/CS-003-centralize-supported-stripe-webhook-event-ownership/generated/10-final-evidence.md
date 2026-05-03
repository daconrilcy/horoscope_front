# Final Evidence — CS-003-centralize-supported-stripe-webhook-event-ownership

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-003-centralize-supported-stripe-webhook-event-ownership
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-003-centralize-supported-stripe-webhook-event-ownership`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/CS-003-centralize-supported-stripe-webhook-event-ownership/00-story.md`
- Initial `git status --short`: `_condamad/stories/story-status.md` modified; CS-003 capsule untracked; git emitted access warnings for pytest temp artifact directories.
- Pre-existing dirty files: `_condamad/stories/story-status.md`, CS-003 capsule path.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Rebuilt from loaded story scope and audit source. |
| `generated/01-execution-brief.md` | yes | yes | PASS | |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | |
| `generated/04-target-files.md` | yes | yes | PASS | |
| `generated/06-validation-plan.md` | yes | yes | PASS | |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | |
| `generated/10-final-evidence.md` | yes | yes | PASS | |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Added `backend/app/services/billing/stripe_webhook_events.py` outside API with typed event definitions and exported groups. | `pytest -q app/tests/unit/test_stripe_webhook_local_dev_assets.py` passed; `rg -n "from app\.api|import app\.api" app/services app/domain app/infra app/core` no-hit. | PASS | Registry owner is billing service namespace. |
| AC2 | `StripeWebhookService.handle_event` consumes `is_supported_webhook_event` and `CHECKOUT_UPGRADE_EVENT_TYPES`. | `pytest -q app/tests/unit/test_stripe_webhook_service.py` passed; local asset guard checks no duplicated async/schedule event strings in dispatch source. | PASS | |
| AC3 | `_resolve_user_id` consumes `CHECKOUT_CLIENT_REFERENCE_EVENT_TYPES`, `CUSTOMER_LOOKUP_EVENT_TYPES`, and `CUSTOMER_OBJECT_ID_LOOKUP_EVENT_TYPES`. | `pytest -q app/tests/unit/test_stripe_webhook_service.py` passed; local asset guard checks no duplicated async/schedule event strings in resolver source. | PASS | |
| AC4 | `scripts/stripe-listen-webhook.ps1`, `docs/billing-webhook-local-testing.md`, and `docs/stripe-webhook-dev.md` aligned with registry. | `pytest -q app/tests/unit/test_stripe_webhook_local_dev_assets.py` passed. | PASS | Docs expose names for human use; guard prevents drift. |
| AC5 | `invoice.payment_succeeded` is absent from registry and has explicit unit/integration ignored coverage. | `pytest -q app/tests/integration/test_stripe_webhook_api.py` passed. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `_condamad/stories/CS-003-centralize-supported-stripe-webhook-event-ownership/00-story.md` | generated | Rebuilt story capsule source from loaded story scope and audit source. | all |
| `_condamad/stories/CS-003-centralize-supported-stripe-webhook-event-ownership/generated/01-execution-brief.md` | generated | Execution brief. | all |
| `_condamad/stories/CS-003-centralize-supported-stripe-webhook-event-ownership/generated/03-acceptance-traceability.md` | generated/modified | AC traceability. | all |
| `_condamad/stories/CS-003-centralize-supported-stripe-webhook-event-ownership/generated/04-target-files.md` | generated | Target map. | all |
| `_condamad/stories/CS-003-centralize-supported-stripe-webhook-event-ownership/generated/05-implementation-plan.md` | generated/modified | Implementation plan. | all |
| `_condamad/stories/CS-003-centralize-supported-stripe-webhook-event-ownership/generated/06-validation-plan.md` | generated | Validation plan. | all |
| `_condamad/stories/CS-003-centralize-supported-stripe-webhook-event-ownership/generated/07-no-legacy-dry-guardrails.md` | generated | No Legacy guardrails. | all |
| `_condamad/stories/CS-003-centralize-supported-stripe-webhook-event-ownership/generated/09-dev-log.md` | generated/modified | Dev log and command evidence. | all |
| `_condamad/stories/CS-003-centralize-supported-stripe-webhook-event-ownership/generated/10-final-evidence.md` | generated/modified | Final evidence. | all |
| `_condamad/stories/CS-003-centralize-supported-stripe-webhook-event-ownership/evidence/webhook-event-registry-baseline.md` | added | Before snapshot. | AC1, AC4 |
| `_condamad/stories/CS-003-centralize-supported-stripe-webhook-event-ownership/evidence/webhook-event-registry-after.md` | added | After snapshot. | AC1, AC4 |
| `_condamad/stories/story-status.md` | modified | Mark CS-003 ready for review. | all |
| `backend/app/services/billing/stripe_webhook_events.py` | added | Canonical registry. | AC1 |
| `backend/app/services/billing/stripe_webhook_service.py` | modified | Runtime dispatch and resolver consume registry. | AC2, AC3, AC5 |
| `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py` | modified | Registry parity and reintroduction guard. | AC1, AC4 |
| `backend/app/tests/unit/test_stripe_webhook_service.py` | modified | Async checkout and schedule support coverage. | AC2, AC3 |
| `backend/app/tests/integration/test_stripe_webhook_api.py` | modified | HTTP ignored behavior for `invoice.payment_succeeded`. | AC5 |
| `docs/billing-webhook-local-testing.md` | modified | Canonical local runbook events. | AC4 |
| `docs/stripe-webhook-dev.md` | modified | Historical rationale aligned to registry. | AC4 |
| `scripts/stripe-listen-webhook.ps1` | modified | Listener event list aligned to registry. | AC4 |

## Files deleted

- None.

## Tests added or updated

- `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py`
- `backend/app/tests/unit/test_stripe_webhook_service.py`
- `backend/app/tests/integration/test_stripe_webhook_api.py`

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `ruff format app/services/billing/stripe_webhook_events.py app/services/billing/stripe_webhook_service.py app/tests/unit/test_stripe_webhook_service.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/integration/test_stripe_webhook_api.py` | `backend` | PASS | 0 | 5 files left unchanged. |
| `ruff check --fix app/services/billing/stripe_webhook_service.py` | `backend` | PASS | 0 | Import order fixed. |
| `ruff check app/services/billing/stripe_webhook_events.py app/services/billing/stripe_webhook_service.py app/tests/unit/test_stripe_webhook_service.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/integration/test_stripe_webhook_api.py` | `backend` | PASS | 0 | All checks passed. |
| `pytest -q app/tests/unit/test_stripe_webhook_service.py app/tests/unit/test_stripe_webhook_local_dev_assets.py` | `backend` | PASS | 0 | 27 passed. |
| `pytest -q app/tests/integration/test_stripe_webhook_api.py` | `backend` | PASS | 0 | 11 passed. |
| `pytest -q app/tests/unit/test_stripe_webhook_service.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/integration/test_stripe_webhook_api.py` | `backend` | PASS | 0 | 38 passed. |
| `python -c "from app.main import app; assert '/v1/billing/stripe-webhook' in app.openapi()['paths']"` | `backend` | PASS | 0 | OpenAPI path present. |
| `rg -n "subscription_schedule|checkout.session.async_payment_succeeded" app/services/billing ../docs ../scripts app/tests` | `backend` | PASS | 0 | Hits classified as canonical registry, docs/script/tests/evidence, plus existing billing profile schedule handling. |
| `rg -n "from app\.api|import app\.api" app/services app/domain app/infra app/core` | `backend` | PASS | 1 | No hits. |
| `rg -n "stripe-listen-webhook\.sh" ../scripts ../docs app/tests` | `backend` | PASS | 1 | No hits. |
| `git diff --stat` | repo root | PASS | 0 | Story-scoped files changed. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; line-ending warnings only. |

## Commands skipped or blocked

- None.

## DRY / No Legacy evidence

- Canonical registry is the only active event ownership path.
- Runtime no longer embeds supported event tuples in dispatch or resolver.
- Docs and listener still show event names for humans, but test parity imports the registry.
- `subscription_schedule` and async checkout hits are classified as canonical registry/docs/script/tests/evidence or existing billing profile service schedule handling.
- No service/domain/infra/core import from `app.api`.
- No Bash listener support found.

## Diff review

- `git diff --stat`: PASS, story-scoped files changed.
- `git diff --check`: PASS, no whitespace errors; Git reported line-ending normalization warnings only.

## Final worktree status

- `git status --short` shows expected story changes:
  - modified `_condamad/stories/story-status.md`;
  - modified backend service/tests, docs, and PowerShell listener files;
  - untracked `_condamad/stories/CS-003-centralize-supported-stripe-webhook-event-ownership/`;
  - untracked `backend/app/services/billing/stripe_webhook_events.py`.
- Git also emitted access warnings for existing pytest temp artifact directories under `.codex-artifacts/`, `artifacts/`, and `backend/.tmp-pytest`.

## Remaining risks

- The original untracked capsule was rebuilt after a Windows path casing mistake during helper use. The restored story source preserves the loaded scope and audit source, but reviewers should focus on code/evidence rather than exact prose identity of the pre-existing untracked file.

## Suggested reviewer focus

- Confirm that classifying all supported backend events as local listener events is the desired local dev posture.
- Review the registry shape and whether `subscription_schedule.*` should remain first-class supported behavior.
