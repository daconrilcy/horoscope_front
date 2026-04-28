# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `reduce-api-sql-boundary-debt-public-email`
- Source story: `_condamad/stories/reduce-api-sql-boundary-debt-public-email/00-story.md`
- Capsule path: `_condamad/stories/reduce-api-sql-boundary-debt-public-email`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `?? _condamad/stories/reduce-api-sql-boundary-debt-public-email/` plus permission warnings on pytest artifact directories.
- Pre-existing dirty files: story capsule directory was already untracked.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes, missing `generated/` files created.
- Regression guardrails considered: `RG-006`, `RG-008`.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Generated with AC1-AC6. |
| `generated/04-target-files.md` | yes | yes | PASS | Generated. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Generated. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Generated. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Initial evidence file created. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `backend/app/api/v1/routers/public/email.py` no longer imports SQLAlchemy, `Session`, `UserModel`, `get_db_session`, nor accepts `db`. | OpenAPI route command PASS; architecture guards PASS; negative route scan returned no hits. | PASS | |
| AC2 | `EmailService.mark_user_unsubscribed` owns `update(UserModel).values(email_unsubscribed=True)` in `backend/app/services/email/service.py`. | `pytest -q tests/integration/test_email_unsubscribe.py` PASS; service ownership scan hit only `app/services/email/service.py`. | PASS | |
| AC3 | Seven `app/api/v1/routers/public/email.py` rows removed from `router-sql-allowlist.md`. | `pytest -q app/tests/unit/test_api_router_architecture.py::test_api_sql_boundary_debt_matches_exact_allowlist` PASS; `allowlist-diff.md` persisted. | PASS | Story expected text mentioned three SQL entries, but repository allowlist had seven exact rows for the file. |
| AC4 | Route behavior, messages, HTML success and no-store handling preserved. | `pytest -q tests/integration/test_email_unsubscribe.py` PASS, 7 tests. | PASS | |
| AC5 | `openapi-before.json` and `openapi-after.json` captured; unsubscribe path content comparison passed. | OpenAPI route assertion PASS; before/after path comparison PASS. | PASS | |
| AC6 | RG-006/RG-008 guards pass; explicit public email SQL guard added. | `pytest -q app/tests/unit/test_api_router_architecture.py` PASS, 53 tests. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `_condamad/stories/reduce-api-sql-boundary-debt-public-email/generated/*` | generated | CONDAMAD execution capsule. | AC1-AC6 |
| `_condamad/stories/reduce-api-sql-boundary-debt-public-email/openapi-before.json` | generated | Baseline OpenAPI before extraction. | AC5 |
| `_condamad/stories/reduce-api-sql-boundary-debt-public-email/openapi-after.json` | generated | OpenAPI after extraction. | AC5 |
| `_condamad/stories/reduce-api-sql-boundary-debt-public-email/router-sql-public-email-before.md` | generated | Before SQL debt inventory. | AC3 |
| `_condamad/stories/reduce-api-sql-boundary-debt-public-email/router-sql-public-email-after.md` | generated | After SQL debt inventory. | AC1, AC3 |
| `_condamad/stories/reduce-api-sql-boundary-debt-public-email/allowlist-diff.md` | generated | Persisted exact allowlist diff. | AC3 |
| `_condamad/stories/reduce-api-sql-boundary-debt-public-email/route-consumption-audit.md` | added | Documents keep/delete decisions. | AC4, AC5 |
| `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md` | modified | Removes stale public email SQL rows. | AC3 |
| `backend/app/api/v1/routers/public/email.py` | modified | Delegates persistence to email service and removes route SQL/session debt. | AC1, AC4 |
| `backend/app/services/email/service.py` | modified | Adds canonical unsubscribe persistence service function. | AC2 |
| `backend/app/tests/unit/test_api_router_architecture.py` | modified | Adds reintroduction guard for public email SQL/session debt. | AC1, AC6 |
| `backend/tests/integration/test_email_unsubscribe.py` | modified | Adds delegation coverage and preserves runtime behavior tests. | AC2, AC4 |

## Files deleted

None.

## Tests added or updated

- Added `test_unsubscribe_delegates_persistence_to_email_service`.
- Added `test_public_email_unsubscribe_router_has_no_sql_boundary_debt`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "...write openapi-before.json..."` | repo root | PASS | 0 | Before OpenAPI snapshot created. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff format .` | repo root | PASS | 0 | 1234 files left unchanged. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | repo root | PASS | 0 | All checks passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check .; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; ruff check .; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; pytest -q` | repo root | PASS | 0 | 1234 files already formatted; all Ruff checks passed; 3151 tests passed, 12 skipped. |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_api_router_architecture.py::test_api_sql_boundary_debt_matches_exact_allowlist app/tests/unit/test_api_router_architecture.py::test_public_email_unsubscribe_router_has_no_sql_boundary_debt app/tests/unit/test_api_router_architecture.py::test_non_api_layers_do_not_import_api_package` | repo root | PASS | 0 | 3 tests passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; rg -n "get_db_session|Session|UserModel|sqlalchemy|db\." app/api/v1/routers/public/email.py` | repo root | PASS | 1 | No hits; negative scan expected exit 1. |
| `.\.venv\Scripts\Activate.ps1; cd backend; rg -n "app/api/v1/routers/public/email.py" ..\_condamad\stories\harden-api-adapter-boundary-guards\router-sql-allowlist.md` | repo root | PASS | 1 | No hits; negative scan expected exit 1. |
| `.\.venv\Scripts\Activate.ps1; cd backend; rg -n "email_unsubscribed=True|update\(UserModel\)" app/services` | repo root | PASS | 0 | Hit in `app/services/email/service.py`. |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/integration/test_email_unsubscribe.py` | repo root | PASS | 0 | 7 tests passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_api_router_architecture.py` | repo root | PASS | 0 | 53 tests passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "from app.main import app; assert '/api/email/unsubscribe' in app.openapi()['paths']"` | repo root | PASS | 0 | Runtime OpenAPI route present. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "...write openapi-after.json..."` | repo root | PASS | 0 | After OpenAPI snapshot created. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "...assert before path == after path..."` | repo root | PASS | 0 | `unsubscribe-openapi-stable`. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; CRLF warnings only. |
| `git diff --stat` | repo root | PASS | 0 | Diff limited to story-related tracked files. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| None | no | Full required validation completed after reviewer fix pass. | None identified. | `ruff format --check`, `ruff check`, and full `pytest -q` passed in the activated venv. |

## DRY / No Legacy evidence

- Route SQL/session negative scan: no hits for `get_db_session`, `Session`, `UserModel`, `sqlalchemy`, `db.` in `public/email.py`.
- Allowlist negative scan: no `app/api/v1/routers/public/email.py` rows remain.
- Existing `legacy|compat|shim|fallback|deprecated|alias` hit in touched scope is the pre-existing docstring phrase `schéma local legacy` in `EmailService._assign_sqlite_email_log_id_if_needed`; classified as out-of-scope historical reference.
- No service imports `app.api`; `test_non_api_layers_do_not_import_api_package` PASS.

## Diff review

- `git diff --check` PASS.
- `git diff --stat` reviewed; after restoring test-mutated `backend/horoscope.db`, tracked diff is limited to expected code and allowlist files.
- Untracked story capsule/evidence directory is expected.

## Final worktree status

`git status --short` shows:

```text
 M _condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md
 M backend/app/api/v1/routers/public/email.py
 M backend/app/services/email/service.py
 M backend/app/tests/unit/test_api_router_architecture.py
 M backend/tests/integration/test_email_unsubscribe.py
?? _condamad/stories/reduce-api-sql-boundary-debt-public-email/
```

The command also reports permission warnings for existing pytest artifact directories under `.codex-artifacts/` and `artifacts/`.

## Remaining risks

- Repository story text expected three SQL entries, but the actual exact allowlist had seven `public/email.py` entries; all seven were stale after extraction and removed.

## Suggested reviewer focus

- Confirm that opening a new `SessionLocal` inside `EmailService.mark_user_unsubscribed` is the desired service ownership pattern for this public unauthenticated flow.
- Confirm that removing all seven exact allowlist rows matches reviewer intent despite the story summary mentioning three entries.
