# CONDAMAD Code Review

## Review target

- Story: `_condamad/stories/converge-admin-llm-observability-router/00-story.md`
- Capsule: `_condamad/stories/converge-admin-llm-observability-router/`
- Reviewed state: post-fix worktree on 2026-04-27
- Applicable guardrails: `RG-001`, `RG-002`, `RG-003`, `RG-005`, `RG-006`, `RG-007`

## Findings

No blocking or material findings remain.

Previously reported CR-001 is resolved: replay disabled failures now preserve the historical application
code `replay_failed`; no `replay_disabled` code or enum remains. The service preserves the old 403/400
status distinction through the existing `_raise_error` extra-status mechanism without introducing the
forbidden `status_code` literal in the service layer.

Previously reported CR-002 is resolved: `generated/10-final-evidence.md` now reflects the current
worktree, including the observability service fix, the new replay error regression test, and the full
backend validation result.

## Acceptance audit

- AC1, AC5, AC8: PASS. Runtime owner and route cardinality are asserted by architecture tests and the runtime owner script.
- AC2, AC7: PASS. OpenAPI path/method contract is stable and integration coverage includes all four endpoints.
- AC3: PASS. The four observability handlers are absent from `prompts.py`.
- AC4: PASS. `observability.py` remains a delegating adapter with no forbidden SQL/model/prompts imports.
- AC6: PASS. Persistent evidence artifacts exist and final evidence has been updated.
- `RG-007`: PASS. Canonical route ownership is protected by runtime owner, OpenAPI diff, and anti-reintroduction scans.

## Validation audit

Reviewer/fix validation commands:

- `.\.venv\Scripts\Activate.ps1; cd backend; ruff format .` - PASS.
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check .` - PASS.
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` - PASS.
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_api_error_architecture.py app/tests/unit/test_admin_llm_observability_errors.py app/tests/unit/test_api_router_architecture.py tests/unit/test_story_70_14_transition_guards.py app/tests/integration/test_admin_llm_config_api.py` - PASS, 70 passed.
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` - PASS, 3144 passed, 12 skipped.
- Runtime owner script via `python -B -` - PASS.
- `rg -n "replay_disabled|REPLAY_DISABLED" backend` - PASS, no hits.
- `git diff --check` - PASS, line-ending warnings only.

## DRY / No Legacy audit

No duplicate active implementation remains for the four observability endpoints. `prompts.py` no longer
declares the observability handlers, `observability.py` is the runtime owner, and the reintroduction
guards cover owner drift, duplicate cardinality, forbidden decorators, SQL/model imports, and prompts
imports.

## Residual risks

No story-blocking residual risk identified. The only remaining noise is environmental `git status`
permission warnings for existing pytest artifact directories.

## Verdict

CLEAN
