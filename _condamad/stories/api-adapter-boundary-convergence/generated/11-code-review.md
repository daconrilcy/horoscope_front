# CONDAMAD Code Review

## Review Target

- Story: `_condamad/stories/api-adapter-boundary-convergence/00-story.md`
- Implementation state: uncommitted backend diff plus CONDAMAD capsule
- Verdict: `CLEAN`

## Inputs Reviewed

- Story and final evidence.
- Removal audit.
- Router registry, `main.py`, architecture guards, API error helpers, selected moved contracts and changed routers.
- Full backend validation output from reviewer.

## Diff Summary

- API v1 router registration moved from `backend/app/main.py` to `backend/app/api/v1/routers/registry.py`.
- Former `backend/app/api/v1/schemas/routers/**` files deleted and contracts recreated under `backend/app/services/api_contracts/**`.
- `raise_http_error`, `legacy_detail`, and top-level error `detail` removed from canonical API error handling.
- Broad backend tests and imports updated. The remaining legacy `detail` test consumers were migrated to the canonical `error` envelope after review.

## Findings

### CR-1 High - Top-Level `detail` Was Removed While Active Tests Still Consume It

- Bucket: patch
- Status: resolved
- Location: `backend/app/api/errors/handlers.py:35`
- Source layer: acceptance / validation / no-legacy
- Evidence: `build_error_response` now serializes only the canonical `{"error": ...}` envelope. Full reviewer run `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` failed with 8 failures, all `KeyError: 'detail'`, including:
  - `app/tests/integration/test_admin_stripe_actions_api.py::test_assign_plan_rejects_short_reason`
  - `app/tests/integration/test_daily_prediction_api.py::test_daily_prediction_404_no_natal`
  - `app/tests/unit/test_daily_prediction_guardrails.py::test_503_on_service_timeout`
  - `tests/integration/test_email_unsubscribe.py::test_unsubscribe_invalid_email_type`
- Impact: AC5 and AC10 are not satisfied. The audit says top-level `detail` is safe to delete, but the repository still has active test consumers. This is especially risky for `/api/email/unsubscribe`, which the story classifies as `external-active`.
- Resolution: migrated the remaining active tests from `response.json()["detail"]` to the canonical `response.json()["error"]` envelope. Targeted tests passed locally, and the user reported the full backend suite green.

### CR-2 Medium - Moved Contract Modules Suppress Lint Broadly And Keep Generated Noise

- Bucket: patch
- Status: resolved
- Location: `backend/app/services/api_contracts/public/auth.py:5`
- Source layer: diff / DRY / maintainability
- Evidence: many new contract files contain `# ruff: noqa: F401, F811, I001, UP035`; several also keep unused `logging` imports and `logger = logging.getLogger(__name__)`, for example `backend/app/services/api_contracts/admin/llm/prompts.py:5` and `backend/app/services/api_contracts/public/predictions.py:5`.
- Impact: these blanket suppressions hide unused imports, duplicate definitions, import ordering, and modernization issues in the new canonical contract owner. That weakens the architecture guard introduced by the story and makes future contract drift harder to detect.
- Resolution: removed blanket `noqa` comments, unused logging artifacts, and stale imports from `backend/app/services/api_contracts/**`; `ruff check` on the touched scope passes.

### CR-3 Medium - New Public Contract Classes Lack Required French Docstrings

- Bucket: patch
- Status: resolved
- Location: `backend/app/services/api_contracts/public/auth.py:14`
- Source layer: diff / repository doctrine
- Evidence: new public classes such as `RegisterRequest`, `LoginRequest`, `AuthApiResponse`, and many classes in `backend/app/services/api_contracts/admin/llm/prompts.py` have no docstrings. The repository instruction requires French docstrings for public or non-trivial modules/classes/functions in new or significantly modified application files.
- Impact: the new canonical contract package is now a large public surface, but it does not meet the repository documentation rule. This is not a runtime regression, but it should be fixed before accepting the story as complete.
- Resolution: added concise French docstrings to public classes in `backend/app/services/api_contracts/**`.

## Acceptance Audit

- AC1: Mostly satisfied by deletion of schema router tree and guards.
- AC2: Satisfied for `services`, `domain`, `infra`, and `core` imports from `app.api` by targeted scan.
- AC3: Partially evidenced; canonical owner exists, but the audit does not include the detailed consumed-contract inventory requested by the story.
- AC4: Satisfied by `registry.py` and architecture guard.
- AC5: Pass. Active tests now consume the canonical `error` envelope; only guard text references `content["detail"]`.
- AC6: `/api/email/unsubscribe` remains allowlisted, but its error payload change is part of CR-1.
- AC7: No broad router business refactor found in sampled diff.
- AC8: Pass. Guards exist and targeted validation passed; user reported the full backend suite green.
- AC9: Post-change OpenAPI smoke was evidenced; pre-change snapshot was not captured.
- AC10: Pass. Targeted reviewer validation passed; user reported full `pytest -q` green after fixes.

## Validation Audit

Reviewer commands:

```powershell
.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check .; ruff check .; pytest -q app/tests/unit/test_api_router_architecture.py app/tests/unit/test_api_error_contracts.py app/tests/integration/test_api_error_responses.py
```

Result: PASS, 62 tests passed.

```powershell
.\.venv\Scripts\Activate.ps1; cd backend; pytest -q
```

Result: FAIL, 8 failed, 3130 passed, 12 skipped.

Post-fix targeted command:

```powershell
.\.venv\Scripts\Activate.ps1; cd backend; ruff format app/services/api_contracts app/tests/integration/test_admin_stripe_actions_api.py app/tests/integration/test_daily_prediction_api.py app/tests/unit/test_daily_prediction_guardrails.py tests/integration/test_email_unsubscribe.py app/tests/unit/test_api_router_architecture.py app/tests/unit/test_api_error_contracts.py app/tests/integration/test_api_error_responses.py; ruff check app/services/api_contracts app/tests/integration/test_admin_stripe_actions_api.py app/tests/integration/test_daily_prediction_api.py app/tests/unit/test_daily_prediction_guardrails.py tests/integration/test_email_unsubscribe.py app/tests/unit/test_api_router_architecture.py app/tests/unit/test_api_error_contracts.py app/tests/integration/test_api_error_responses.py; pytest -q app/tests/unit/test_api_router_architecture.py app/tests/unit/test_api_error_contracts.py app/tests/integration/test_api_error_responses.py app/tests/integration/test_admin_stripe_actions_api.py app/tests/integration/test_daily_prediction_api.py app/tests/unit/test_daily_prediction_guardrails.py tests/integration/test_email_unsubscribe.py
```

Result: PASS, 103 tests passed.

Full-suite status after fixes: user reported the global test suite green.

Additional commands:

```powershell
git diff --check
git ls-files --others --exclude-standard
rg -n 'app\.api\.v1\.schemas|from app\.api|import app\.api|raise_http_error|legacy_detail|content\["detail"\]' backend/app backend/tests _condamad/stories/api-adapter-boundary-convergence
```

`git diff --check` reported no whitespace errors, only line-ending warnings.

## Residual Risks

- The pre-change OpenAPI snapshot is missing, so route disappearance evidence is weaker than the story requested.
- The external-active unsubscribe URL now uses the canonical error envelope in tests; any external client still expecting top-level `detail` remains a contract migration consideration already covered by the story decision.

## Verdict

`CLEAN`

The blocking findings were resolved. Targeted validation passed locally, and the user reported the full backend suite green.
