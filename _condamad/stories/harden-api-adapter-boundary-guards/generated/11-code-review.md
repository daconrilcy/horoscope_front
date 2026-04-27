# CONDAMAD Code Review

## Review target

- Story: `_condamad/stories/harden-api-adapter-boundary-guards/00-story.md`
- Review pass: post-fix adversarial verification
- Review date: 2026-04-28

## Inputs reviewed

- Current worktree diff and untracked story artifacts.
- `backend/app/api/route_exceptions.py`
- `backend/app/tests/unit/test_api_router_architecture.py`
- `router-sql-inventory-before.md`, `router-sql-inventory-after.md`, `router-sql-allowlist.md`
- `generated/03-acceptance-traceability.md`, `generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md`

## Diff summary

- QA route exceptions are concrete path/method rows.
- SQL guard records imports, session calls, and both positional and keyword `Depends(get_db_session)` usage.
- SQL before inventory was rebuilt from `HEAD` with the same scanner semantics as the current after inventory.
- Evidence now reports comparable SQL counts: 852 before, 848 after.

## Findings

No actionable findings remain in this review pass.

Resolved prior findings:

- CR-003: resolved. Before/after inventories now use the same scanner scope and final evidence no longer claims stale 643/639 counts.
- CR-004: resolved. `_is_get_db_session_dependency` checks both positional and `dependency=` keyword arguments.

## Acceptance audit

- AC1: Pass. Health, public email, and each concrete QA route are structured and exact.
- AC2: Pass. `main.py` delegates to the canonical v1 registry and the structured exception register.
- AC3: Pass. SQL inventory uses comparable before/after scanner semantics and shows 852 entries before versus 848 after.
- AC4: Pass. New imports, session calls, and positional/keyword `Depends(get_db_session)` usages must be allowlisted exactly.
- AC5: Pass. The selected admin content update flow delegates persistence to a service.
- AC6: Pass. Existing OpenAPI diff reports no path, method, operation, request schema, or response schema changes.
- AC7: Pass. Observability ownership guard remains in the architecture suite.
- AC8: Pass. Allowlist rows require exact metadata and stale/missing rows fail.

## Validation audit

Reviewer commands run:

- `.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check .` - PASS
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` - PASS
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app\tests\unit\test_api_router_architecture.py` - PASS, 52 passed
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app\tests\integration\test_admin_content_api.py` - PASS, 3 passed
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app\tests\integration\test_llm_qa_router.py` - PASS, 3 passed after replacing the stale `main._include_internal_llm_qa_router` test reference
- `git diff --check` - PASS, CRLF warnings only
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` - PASS, full suite reported green by the user after the QA mount-policy test update

The full `pytest -q` was rerun by the user after the stale QA test reference was fixed and is reported green.

## DRY / No Legacy audit

- No compatibility wrapper, alias, re-export, or fallback path was found in the reviewed diff.
- The exception register remains a single owner for known route exceptions.
- The SQL allowlist is exact for detected debt and blocks silent growth for the covered forms.

## Residual risks

- Full regression suite is reported green by the user; focused validation for changed surfaces also passes.
- The SQL allowlist is intentionally large and line-number exact; future changes should regenerate it deliberately.

## Verdict

CLEAN
