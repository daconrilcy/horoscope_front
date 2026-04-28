# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `decide-public-email-unsubscribe-canonicalization`
- Source story: `_condamad/stories/decide-public-email-unsubscribe-canonicalization/00-story.md`
- Capsule path: `_condamad/stories/decide-public-email-unsubscribe-canonicalization/`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: untracked `_condamad/audits/api-adapter/2026-04-28-0046/`, `_condamad/stories/decide-public-email-unsubscribe-canonicalization/`, `_condamad/stories/reduce-api-sql-boundary-debt-public-email/`; Git also warned about unreadable pytest temp directories.
- Pre-existing dirty files: same as initial status.
- AGENTS.md files considered: `AGENTS.md`.
- Regression guardrails considered: `_condamad/stories/regression-guardrails.md`.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story exists. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated for this run. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Covers AC1-AC7. |
| `generated/04-target-files.md` | yes | yes | PASS | Story-specific targets and scans. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Executable checks listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific guardrails. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Updated at completion. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `route-consumption-audit.md`, `openapi-before.json`, `runtime-routes-before.md`, `openapi-after.json`, `runtime-routes-after.md`. | OpenAPI smoke passed; consumer scan classified active link generator, templates, tests, register, and historical evidence. | PASS | Route classified `external-active`. |
| AC2 | `decision-record.md` records `needs-user-decision`, no permanence/deletion/migration approval, and future migration conditions. | Decision record contains `Decision`, `User decision`, and `Risk`; route not removed. | PASS | External-active deletion and permanence are blocked until explicit approval. |
| AC3 | `backend/app/api/route_exceptions.py` decision text changed to exact `needs-user-decision` external-active language. | `pytest -q app/tests/unit/test_api_router_architecture.py` passed with exact assertions. | PASS | |
| AC4 | Handler, link generation, and OpenAPI path preserved. | OpenAPI before/after comparison had no path diff; integration unsubscribe tests passed. | PASS | Runtime route comparison only differs by document title. |
| AC5 | No migration selected because no approval exists and route is external-active. | `decision-record.md` documents no migration approval. | NOT_APPLICABLE | Conditional migrate AC does not apply to `needs-user-decision`. |
| AC6 | No deletion selected because no approval exists and route is external-active. | `decision-record.md`; duplicate handler scan confirms no wrapper/redirect added. | NOT_APPLICABLE | Conditional delete AC does not apply to `needs-user-decision`. |
| AC7 | Single active handler kept in `backend/app/api/v1/routers/public/email.py`; exact exception entry kept in `route_exceptions.py`. | Duplicate scan found one handler, one route exception entry, and one link generator; architecture tests passed. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/api/route_exceptions.py` | modified | Persist `needs-user-decision` external-active blocker in exception register. | AC2, AC3, AC4 |
| `backend/app/api/v1/routers/public/email.py` | modified | Preserve the historical route while adding `Cache-Control: no-store` and token-safe unexpected-error logging without changing tested status codes. | AC4 |
| `backend/app/tests/unit/test_api_router_architecture.py` | modified | Assert exact unsubscribe exception decision and route metadata. | AC3, AC7 |
| `backend/tests/integration/test_email_unsubscribe.py` | modified | Assert `no-store` responses and preserve the existing absent-user `400` contract. | AC4 |
| `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md` | modified | Update line-number evidence after public email route edits without adding SQL debt. | RG-008 |
| `_condamad/stories/decide-public-email-unsubscribe-canonicalization/00-story.md` | modified | Mark implementation tasks complete and status ready for review. | AC1-AC7 |
| `_condamad/stories/decide-public-email-unsubscribe-canonicalization/decision-record.md` | added | Persist selected decision and blockers for deletion/migration. | AC2 |
| `_condamad/stories/decide-public-email-unsubscribe-canonicalization/route-consumption-audit.md` | added | Classify route consumers and duplicate handler evidence. | AC1, AC7 |
| `_condamad/stories/decide-public-email-unsubscribe-canonicalization/openapi-before.json` | added | Baseline OpenAPI contract. | AC1, AC4 |
| `_condamad/stories/decide-public-email-unsubscribe-canonicalization/openapi-after.json` | added | Final OpenAPI contract. | AC4 |
| `_condamad/stories/decide-public-email-unsubscribe-canonicalization/runtime-routes-before.md` | added | Baseline route table. | AC1, AC4, AC7 |
| `_condamad/stories/decide-public-email-unsubscribe-canonicalization/runtime-routes-after.md` | added | Final route table. | AC4, AC7 |
| `_condamad/stories/decide-public-email-unsubscribe-canonicalization/generated/*.md` | added/modified | CONDAMAD capsule and final evidence. | AC1-AC7 |

## Files deleted

- None.

## Tests added or updated

- Updated `backend/app/tests/unit/test_api_router_architecture.py` to assert exact `public_email_unsubscribe` route metadata and `needs-user-decision` external-active decision.
- Updated `backend/tests/integration/test_email_unsubscribe.py` to assert `Cache-Control: no-store` while preserving the existing `400` response for signed tokens whose user is absent.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; python -B -c "...capture before snapshots..."` | repo root | FAIL | 1 | First snapshot attempt failed due PowerShell/Python quoting; no files were changed by that failed command. |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; @'...capture before snapshots...'@ \| python -B -` | repo root | PASS | 0 | Created `openapi-before.json` and `runtime-routes-before.md`. |
| `ruff format .` | `backend/` | PASS | 0 | 1234 files left unchanged. |
| `ruff check .` | `backend/` | PASS | 0 | All checks passed. |
| `pytest -q app/tests/unit/test_api_router_architecture.py` | `backend/` | PASS | 0 | 52 passed. |
| `pytest -q tests/integration/test_email_unsubscribe.py` | `backend/` | PASS | 0 | 6 passed. |
| `python -B -c "from app.main import app; paths = app.openapi()['paths']; assert '/api/email/unsubscribe' in paths"` | `backend/` | PASS | 0 | OpenAPI keeps `/api/email/unsubscribe`. |
| `rg -n "api/email/unsubscribe|/email/unsubscribe|get_unsubscribe_link|unsubscribe_url" ..\backend ..\frontend ..\_condamad` | `backend/` | PASS | 0 | Active hits classified in `route-consumption-audit.md`; historical evidence hits are expected. |
| `rg -n "def unsubscribe|/unsubscribe|api/email/unsubscribe" ..\backend\app` | `backend/` | PASS | 0 | One handler, one exception entry, one link generator, plus test assertion. |
| `rg -n "legacy|compat|shim|fallback|deprecated|alias" backend\app\api backend\app\tests\unit\test_api_router_architecture.py backend\tests\integration\test_email_unsubscribe.py` | repo root | PASS | 0 | Hits are pre-existing guard/test/router terminology outside this story; no new unsubscribe wrapper, redirect, alias, fallback, or duplicate route. |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; @'...capture after snapshots...'@ \| python -B -` | repo root | PASS | 0 | Created `openapi-after.json` and `runtime-routes-after.md`. |
| `pytest -q` | `backend/` | PASS | 0 | 3149 passed, 12 skipped. |
| `rg -n "Decision|User decision|Risk" _condamad\stories\decide-public-email-unsubscribe-canonicalization\decision-record.md` | repo root | PASS | 0 | Decision, user-decision blocker, and risk sections are present. |
| `Compare-Object openapi-before.json openapi-after.json` | repo root | PASS | 0 | No OpenAPI diff. |
| `Compare-Object runtime-routes-before.md runtime-routes-after.md` | repo root | PASS | 0 | Only document title differs; route rows unchanged. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; Git reported LF/CRLF warnings for touched Python files. |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff format --check .; ruff check .; pytest -q app/tests/unit/test_api_router_architecture.py tests/integration/test_email_unsubscribe.py; python -B -c "from app.main import app; paths = app.openapi()['paths']; assert '/api/email/unsubscribe' in paths"` | repo root | PASS | 0 | Fix pass after review issue correction: 1234 files already formatted, lint passed, 58 tests passed, OpenAPI keeps `/api/email/unsubscribe`. |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest -q tests/integration/test_email_unsubscribe.py` | repo root | PASS | 0 | Security hardening pass: 6 unsubscribe integration tests passed, including `no-store` and preserved absent-user `400` behavior. |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff format --check .; ruff check .; pytest -q app/tests/unit/test_api_router_architecture.py tests/integration/test_email_unsubscribe.py; python -B -c "from app.main import app; paths = app.openapi()['paths']; assert '/api/email/unsubscribe' in paths"` | repo root | PASS | 0 | Final security hardening validation: 1234 files already formatted, lint passed, 58 tests passed, OpenAPI keeps `/api/email/unsubscribe`. |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff format --check .; ruff check .` | repo root | PASS | 0 | Post-review fix validation: 1234 files already formatted; lint passed. |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest -q app/tests/unit/test_api_router_architecture.py tests/integration/test_email_unsubscribe.py` | repo root | PASS | 0 | Post-review fix validation: 58 tests passed. |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; python -B -c "from app.main import app; paths = app.openapi()['paths']; assert '/api/email/unsubscribe' in paths"` | repo root | PASS | 0 | Post-review fix validation: OpenAPI keeps `/api/email/unsubscribe`. |
| `git diff --check` | repo root | PASS | 0 | Post-review fix validation: no whitespace errors; Git reported LF/CRLF warnings for touched files. |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest -q` | repo root | TIMEOUT | 124 | First post-review full-suite attempt timed out after 304 seconds without a usable result. |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest -q` | repo root | PASS | 0 | Second post-review full-suite run passed: 3149 passed, 12 skipped in 729.09s. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| None | no | All required commands were run. | None | Not applicable. |

## DRY / No Legacy evidence

- No new route, redirect, wrapper, alias, fallback, or compatibility facade was introduced.
- `/api/email/unsubscribe` is kept only as an exact, documented `API_ROUTE_MOUNT_EXCEPTIONS` entry.
- Duplicate handler scan found one active handler: `backend/app/api/v1/routers/public/email.py::unsubscribe`.
- Consumer scan confirms the route is externally active through generated email links and template variables.
- Broad legacy scan had pre-existing architecture guard and unrelated route terminology hits; none are new unsubscribe compatibility paths.
- Public route hardening was added without changing the URL or tested status codes: `Cache-Control: no-store` and token-safe unexpected-error logging.
- `router-sql-allowlist.md` line numbers for `public/email.py` were updated after adding the module docstring/imports; no new SQL boundary entry was introduced.

## Diff review

- `git diff --stat` after the final correction includes `backend/app/api/route_exceptions.py`, `backend/app/api/v1/routers/public/email.py`, `backend/app/tests/unit/test_api_router_architecture.py`, `backend/tests/integration/test_email_unsubscribe.py`, `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md`, and this story capsule.
- `backend/horoscope.db` was restored because it was an unrelated artifact modified by the full test suite.
- Relevant code diff contains the route exception decision update, public route cache/logging hardening with preserved absent-user `400` behavior, integration-test assertions, architecture-test assertions, and SQL allowlist line-number evidence updates.
- OpenAPI before/after snapshots are identical.
- Runtime before/after rows are identical except the markdown title.

## Final worktree status

```text
 M _condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md
 M backend/app/api/route_exceptions.py
 M backend/app/api/v1/routers/public/email.py
 M backend/app/tests/unit/test_api_router_architecture.py
 M backend/tests/integration/test_email_unsubscribe.py
?? _condamad/audits/api-adapter/2026-04-28-0046/
?? _condamad/stories/decide-public-email-unsubscribe-canonicalization/
?? _condamad/stories/reduce-api-sql-boundary-debt-public-email/
warning: could not open directory '.codex-artifacts/pytest-basetemp/': Permission denied
warning: could not open directory '.codex-artifacts/tmp/pytest-of-cyril/': Permission denied
warning: could not open directory 'artifacts/pytest-basetemp/': Permission denied
```

## Remaining risks

- Already-sent emails may continue to reference `/api/email/unsubscribe`; this is the reason deletion and migration remain blocked without future explicit approval.
- The route handler still owns DB work in `backend/app/api/v1/routers/public/email.py`; this story did not refactor that debt.

## Suggested reviewer focus

- Review the pending product decision for public unsubscribe links before selecting permanence, migration, or deletion.
- Review the exact route exception decision text and architecture guard coverage.
- Confirm that no future migration should be started without explicit external-link transition approval.
