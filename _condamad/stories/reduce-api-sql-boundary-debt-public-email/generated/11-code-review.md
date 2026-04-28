# CONDAMAD Code Review

## Review target

- Story: `_condamad/stories/reduce-api-sql-boundary-debt-public-email`
- Status reviewed: `ready-for-review`
- Applicable guardrails: `RG-006`, `RG-008`
- Review scope: current worktree diff and CONDAMAD capsule evidence for this story only.

## Inputs reviewed

- `_condamad/stories/reduce-api-sql-boundary-debt-public-email/00-story.md`
- `_condamad/stories/reduce-api-sql-boundary-debt-public-email/generated/03-acceptance-traceability.md`
- `_condamad/stories/reduce-api-sql-boundary-debt-public-email/generated/10-final-evidence.md`
- `_condamad/stories/reduce-api-sql-boundary-debt-public-email/openapi-before.json`
- `_condamad/stories/reduce-api-sql-boundary-debt-public-email/openapi-after.json`
- `_condamad/stories/reduce-api-sql-boundary-debt-public-email/router-sql-public-email-before.md`
- `_condamad/stories/reduce-api-sql-boundary-debt-public-email/router-sql-public-email-after.md`
- `_condamad/stories/reduce-api-sql-boundary-debt-public-email/allowlist-diff.md`
- `_condamad/stories/reduce-api-sql-boundary-debt-public-email/route-consumption-audit.md`
- `_condamad/stories/regression-guardrails.md`
- Current tracked diff for router, service, tests, architecture guard, and SQL allowlist.

## Diff summary

- `backend/app/api/v1/routers/public/email.py` no longer imports SQLAlchemy, `Session`, `UserModel`, or `get_db_session`.
- `unsubscribe` delegates persistence to `EmailService.mark_user_unsubscribed`.
- `backend/app/services/email/service.py` owns the SQL update and commit.
- `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md` removes all stale `public/email.py` rows.
- `backend/app/tests/unit/test_api_router_architecture.py` adds a targeted anti-reintroduction guard.
- `backend/tests/integration/test_email_unsubscribe.py` adds delegation coverage while keeping success and error behavior tests.
- Persistent OpenAPI and SQL before/after evidence exists in the story capsule.

## Findings

No actionable findings.

## Acceptance audit

- AC1: PASS. `backend/app/api/v1/routers/public/email.py:8` imports only FastAPI HTTP primitives, and `backend/app/api/v1/routers/public/email.py:52` delegates persistence without route-level SQL/session usage. Negative route scan returned no hits.
- AC2: PASS. `backend/app/services/email/service.py:69` defines `EmailService.mark_user_unsubscribed`, and `backend/app/services/email/service.py:72` owns the `update(UserModel)` persistence. Service ownership scan finds the update only under `app/services`.
- AC3: PASS. The allowlist diff removes the stale `app/api/v1/routers/public/email.py` entries only; exact SQL allowlist guard passes.
- AC4: PASS. `backend/tests/integration/test_email_unsubscribe.py:55` covers successful unsubscribe, `:89` invalid type, `:100` expired token, and `:122` unknown user. Targeted integration tests pass.
- AC5: PASS. Runtime OpenAPI still exposes `/api/email/unsubscribe`, and the before/after path snapshot comparison passes.
- AC6: PASS. `backend/app/tests/unit/test_api_router_architecture.py:893` enforces the exact SQL allowlist, `:908` guards the public email router specifically, and the non-API import boundary test passes.

## Validation audit

Reviewer commands run in this review:

```powershell
.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check app/api/v1/routers/public/email.py app/services/email/service.py app/tests/unit/test_api_router_architecture.py tests/integration/test_email_unsubscribe.py; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; ruff check app/api/v1/routers/public/email.py app/services/email/service.py app/tests/unit/test_api_router_architecture.py tests/integration/test_email_unsubscribe.py
.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/integration/test_email_unsubscribe.py
.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_api_router_architecture.py::test_api_sql_boundary_debt_matches_exact_allowlist app/tests/unit/test_api_router_architecture.py::test_public_email_unsubscribe_router_has_no_sql_boundary_debt app/tests/unit/test_api_router_architecture.py::test_non_api_layers_do_not_import_api_package
.\.venv\Scripts\Activate.ps1; cd backend; rg -n "get_db_session|Session|UserModel|sqlalchemy|db\." app/api/v1/routers/public/email.py
.\.venv\Scripts\Activate.ps1; cd backend; rg -n "app/api/v1/routers/public/email.py" ..\_condamad\stories\harden-api-adapter-boundary-guards\router-sql-allowlist.md
.\.venv\Scripts\Activate.ps1; cd backend; rg -n "email_unsubscribed=True|update\(UserModel\)" app/services
.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "from app.main import app; spec=app.openapi(); assert '/api/email/unsubscribe' in spec['paths']; print('unsubscribe-route-present')"
.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "import json; from pathlib import Path; root=Path('..')/'_condamad'/'stories'/'reduce-api-sql-boundary-debt-public-email'; before=json.loads((root/'openapi-before.json').read_text(encoding='utf-8')); after=json.loads((root/'openapi-after.json').read_text(encoding='utf-8')); assert before['paths']['/api/email/unsubscribe'] == after['paths']['/api/email/unsubscribe']; print('unsubscribe-openapi-stable')"
.\.venv\Scripts\Activate.ps1; cd backend; rg -n "from app\.api|import app\.api" app/services app/domain app/infra app/core
git diff --check
git status --short
git diff --stat
```

Results:

- Targeted format and lint: PASS, 4 files already formatted; all checks passed.
- Targeted integration: PASS, 7 passed.
- Targeted architecture: PASS, 3 passed.
- Negative route SQL/session scan: PASS via expected `rg` exit 1.
- Negative allowlist scan: PASS via expected `rg` exit 1.
- Service ownership scan: PASS, one hit in `app/services/email/service.py`.
- Runtime OpenAPI route assertion: PASS.
- OpenAPI before/after path comparison: PASS.
- Non-API import scan: PASS via expected `rg` exit 1.
- `git diff --check`: PASS, CRLF warnings only.
- Worktree scope: PASS; tracked diff is limited to expected story files and no `backend/horoscope.db` change is present.

Full validation evidence from `generated/10-final-evidence.md` is also PASS:

```powershell
.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check .; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; ruff check .; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; pytest -q
```

Recorded result: 1234 files already formatted; all Ruff checks passed; 3151 tests passed, 12 skipped.

## DRY / No Legacy audit

- No second unsubscribe endpoint was added.
- No wrapper, alias, fallback, compatibility route, or re-export was introduced.
- `/api/email/unsubscribe` remains external-active and is kept, as required.
- Route-level SQL/session debt for `public/email.py` is removed from code and allowlist.
- `RG-006`: no `app.api` import was found in `app/services`, `app/domain`, `app/infra`, or `app/core`.
- `RG-008`: exact allowlist and targeted AST guard protect against silent SQL debt reintroduction.

## Residual risks

- The story prose mentions three SQL entries, while the actual exact allowlist contained seven `public/email.py` rows. This is documented in final evidence and the persisted allowlist diff; all seven rows were stale after extraction.

## Verdict

CLEAN
