# CONDAMAD Code Review

## Review target

- Story: `_condamad/stories/decide-public-email-unsubscribe-canonicalization/00-story.md`
- Status reviewed: `ready-for-review`
- Review date: 2026-04-28
- Verdict: `CLEAN`

## Inputs reviewed

- Story contract and acceptance criteria.
- Regression guardrails: `_condamad/stories/regression-guardrails.md`.
- Decision and evidence artifacts:
  - `_condamad/stories/decide-public-email-unsubscribe-canonicalization/decision-record.md`
  - `_condamad/stories/decide-public-email-unsubscribe-canonicalization/route-consumption-audit.md`
  - `_condamad/stories/decide-public-email-unsubscribe-canonicalization/openapi-before.json`
  - `_condamad/stories/decide-public-email-unsubscribe-canonicalization/openapi-after.json`
  - `_condamad/stories/decide-public-email-unsubscribe-canonicalization/runtime-routes-before.md`
  - `_condamad/stories/decide-public-email-unsubscribe-canonicalization/runtime-routes-after.md`
  - `_condamad/stories/decide-public-email-unsubscribe-canonicalization/generated/10-final-evidence.md`
- Diff for:
  - `backend/app/api/route_exceptions.py`
  - `backend/app/api/v1/routers/public/email.py`
  - `backend/app/tests/unit/test_api_router_architecture.py`
  - `backend/tests/integration/test_email_unsubscribe.py`
  - `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md`

## Diff summary

The implementation classifies `GET /api/email/unsubscribe` as `external-active` and records a `needs-user-decision` blocker. The historical public route remains mounted through the exact `API_ROUTE_MOUNT_EXCEPTIONS` entry. The route adds `Cache-Control: no-store` and token-safe unexpected-error logging while preserving the tested success/error status codes, including the absent-user `400` response. Architecture tests assert the exception metadata, and the SQL boundary allowlist is updated only for line-number drift caused by the route file edits.

## Review layers

- Diff integrity: no unexpected application files or generated runtime artifacts were introduced by this review pass; untracked CONDAMAD audit/story directories remain visible in `git status`.
- Acceptance audit: AC1-AC4 and AC7 are satisfied; AC5 and AC6 are not applicable because no migration or deletion was selected.
- Validation audit: required targeted checks and full backend tests passed in the activated venv.
- DRY / No Legacy audit: no second unsubscribe handler, redirect, wrapper, alias, fallback, or permanent compatibility facade was found.
- Security/data audit: `no-store` is asserted for success and expected error responses; unexpected-error logging uses a stable event name without interpolating token/query details.

## Findings

No actionable findings.

## Acceptance audit

- AC1: PASS. `route-consumption-audit.md` classifies `/api/email/unsubscribe` as `external-active`; consumer scan confirms active link generation, templates, tests, OpenAPI, and story/audit references.
- AC2: PASS. `decision-record.md` records `needs-user-decision`, no approval for permanence/deletion/migration, and the external-active deletion blocker.
- AC3: PASS. `backend/app/api/route_exceptions.py` contains the exact `public_email_unsubscribe` route metadata and decision text; architecture tests cover it.
- AC4: PASS. The path stays exposed, OpenAPI snapshots are identical, integration tests preserve status behavior and assert `Cache-Control: no-store`.
- AC5: Not applicable. No migration was selected.
- AC6: Not applicable. No deletion was selected.
- AC7: PASS. Duplicate handler scan shows one handler, one route exception entry, and one link generator.

## Validation audit

Reviewer commands run:

```powershell
.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff format --check .; ruff check .
.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest -q app/tests/unit/test_api_router_architecture.py tests/integration/test_email_unsubscribe.py
.\.venv\Scripts\Activate.ps1; Set-Location backend; python -B -c "from app.main import app; paths = app.openapi()['paths']; assert '/api/email/unsubscribe' in paths"
git diff --check
rg -n "api/email/unsubscribe|/email/unsubscribe|get_unsubscribe_link|unsubscribe_url" backend frontend _condamad
rg -n "def unsubscribe|/unsubscribe|api/email/unsubscribe" backend/app
Compare-Object (Get-Content -LiteralPath '_condamad\stories\decide-public-email-unsubscribe-canonicalization\openapi-before.json') (Get-Content -LiteralPath '_condamad\stories\decide-public-email-unsubscribe-canonicalization\openapi-after.json')
Compare-Object (Get-Content -LiteralPath '_condamad\stories\decide-public-email-unsubscribe-canonicalization\runtime-routes-before.md') (Get-Content -LiteralPath '_condamad\stories\decide-public-email-unsubscribe-canonicalization\runtime-routes-after.md')
rg -n "Decision|User decision|Risk" _condamad\stories\decide-public-email-unsubscribe-canonicalization\decision-record.md
rg -n "non-enumerating|generic successful|BLOCKING|CR-1 High|CR-2 High" _condamad\stories\decide-public-email-unsubscribe-canonicalization
.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest -q
```

Results:

- Ruff format check: PASS, `1234 files already formatted`.
- Ruff check: PASS.
- Targeted tests: PASS, `58 passed in 14.69s`.
- OpenAPI path smoke: PASS.
- `git diff --check`: PASS, with LF/CRLF warnings only.
- Consumer scan: PASS; active hits are classified by `route-consumption-audit.md`.
- Duplicate handler scan: PASS; one handler, one exception entry, one link generator.
- OpenAPI before/after comparison: PASS; no diff.
- Runtime routes before/after comparison: PASS with title-only markdown difference.
- Decision record scan: PASS.
- Stale blocking-review wording scan: PASS; no hits.
- Full backend test suite: PASS, `3149 passed, 12 skipped in 777.37s`.

## DRY / No Legacy audit

- `RG-001`: no deleted historical facade was reintroduced; the route was not deleted.
- `RG-003`: route mounting remains governed by the existing runtime architecture tests and exact exception register.
- `RG-006`: no new non-API owner or competing business logic owner was added; the remaining route-level DB work is pre-existing debt and documented.
- `RG-008`: the non-v1 route exception and SQL boundary allowlist remain exact; the allowlist changes are line-number updates only.

## Residual risks

- Already-sent emails may still reference `/api/email/unsubscribe`; deletion or migration remains blocked until explicit future approval.
- The route still performs a state-changing unsubscribe action through `GET`; the audit records this as a future decision area, not as a regression introduced here.

## Verdict

`CLEAN`
