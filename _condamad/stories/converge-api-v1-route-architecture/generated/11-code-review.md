# CONDAMAD Code Review

## Review target

- Story: `_condamad/stories/converge-api-v1-route-architecture/00-story.md`
- Diff reviewed: uncommitted worktree against `HEAD`, including untracked story/code files.
- Verdict: `ACCEPTABLE_WITH_LIMITATIONS` après corrections

## Inputs reviewed

- Story contract and AC1-AC19.
- Capsule evidence: `generated/03-acceptance-traceability.md`, `generated/06-validation-plan.md`, `generated/07-no-legacy-dry-guardrails.md`, `generated/10-final-evidence.md`.
- Diff/status evidence from `git status --short`, `git diff --stat`, `git diff --name-status`, `git diff HEAD --stat`, `git diff HEAD --name-status`, `git ls-files --others --exclude-standard`, `git diff --check`.
- Target files and architecture guards around router roots, router imports, schemas, and OpenAPI contract tests.

## Diff summary

- Large API v1 route/schema/router_logic convergence with deleted old modules and new canonical modules.
- New central `errors.py`, `constants.py`, and `schemas/common.py`.
- Updated architecture and OpenAPI tests.
- `backend/horoscope.db` remains dirty in the worktree; final evidence records it as pre-existing.

## Findings

### CR-1 High - Router root audit is not complete

- Bucket: patch
- Location: `_condamad/stories/converge-api-v1-route-architecture/router-root-audit.md:5`
- Source layer: acceptance / validation
- Evidence: AC1 requires a complete v1 router inventory by effective HTTP root. The audit table contains only six entries, while `rg -n "APIRouter\(" backend/app/api/v1/routers` reports 49 router declarations. `generated/10-final-evidence.md:36` also says AC1 is only "focused on active moved/non-v1 routes", which contradicts the story requirement for a complete inventory.
- Impact: route/root drift outside the moved subset can remain invisible, so AC1 and the route architecture convergence are not actually proven.
- Suggested fix: generate the audit from the registered FastAPI app for every active API v1 router and include each route/module/root decision in `router-root-audit.md`; extend the guard to fail when any active router path is absent from the inventory.

### CR-2 High - A non-registry router still imports another router

- Bucket: patch
- Location: `backend/app/api/v1/routers/admin/llm/observability.py:5`
- Source layer: acceptance / no-legacy
- Evidence: `observability.py` defines its own `APIRouter` at line 14 and imports handlers/models from `app.api.v1.routers.admin.llm.prompts` at line 5. The architecture guard explicitly allowlists this in `backend/app/tests/unit/test_api_router_architecture.py:108`, and final evidence notes this remaining hit at `generated/10-final-evidence.md:41`.
- Impact: AC6/target-state says routeurs should not import other routeurs for shared handlers/helpers. This keeps `prompts.py` as an implicit owner for observability endpoints and preserves a cross-router coupling the story was meant to eliminate.
- Suggested fix: move the observability handlers and response models out of `routers.admin.llm.prompts` into a canonical non-router module, then have both route modules import from that owner or split the endpoints into their canonical router directly. Remove the special allowlist.

### CR-3 Medium - New moved route modules miss required French module documentation

- Bucket: patch
- Location: `backend/app/api/v1/routers/ops/b2b/reconciliation.py:1`
- Source layer: validation / maintainability
- Evidence: repository instructions require every new or significantly modified application file to have a French global comment/docstring. New moved route modules such as `backend/app/api/v1/routers/ops/b2b/reconciliation.py:1` and `backend/app/api/v1/routers/b2b/credentials.py:1` start directly with `from __future__ import annotations`.
- Impact: the implementation misses a non-negotiable repository documentation rule on newly added application files.
- Suggested fix: add concise French module docstrings to the new/moved router files and docstrings for public/non-trivial route functions where absent.

## Acceptance audit

- AC1 is not satisfied: the audit is subset-only, not complete.
- AC6 is not satisfied: one active non-registry router still imports another router and the guard masks it with a special allowlist.
- AC10 targeted reviewer checks passed, but the findings above prevent acceptance.

## Validation audit

Reviewer commands run:

- `git status --short`
- `git diff --stat`
- `git diff --name-status`
- `git diff --cached --stat`
- `git diff --cached --name-status`
- `git diff HEAD --stat`
- `git diff HEAD --name-status`
- `git ls-files --others --exclude-standard`
- `git diff --check`
- `rg -n "APIRouter|import \*" backend/app/api/v1/router_logic`
- `rg -n "from app\.api\.v1\.routers\." backend/app/api/v1/schemas backend/app/api/v1/router_logic backend/app/api/v1/routers`
- `rg -n "prefix=\"/v1/ops" backend/app/api/v1/routers/b2b backend/app/api/v1/routers/public`
- `rg -n "prefix=\"/v1/b2b" backend/app/api/v1/routers/public backend/app/api/v1/routers/ops`
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .`
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_api_router_architecture.py app/tests/unit/test_api_error_contracts.py app/tests/integration/test_api_v1_router_contracts.py`

Reviewer validation results:

- `ruff check .`: passed.
- Targeted pytest command: 41 passed.
- `git diff --check`: no whitespace errors; CRLF warnings only.

## DRY / No Legacy audit

- Old moved router import scans only found architecture-test expected references.
- The remaining `observability.py` to `prompts.py` router import is an active cross-router dependency, not just documentation or test evidence.

## Residual risks

- Full `pytest -q` was not rerun by the reviewer; final evidence claims it passed earlier.
- `backend/horoscope.db` is dirty and binary; final evidence says it was pre-existing, but it remains in the review worktree.
- Permission warnings appeared while listing untracked files under pytest artifact directories.

## Verdict

`ACCEPTABLE_WITH_LIMITATIONS`

## Resolution notes

- CR-1 corrigé: `router-root-audit.md` liste maintenant les 47 modules routeurs actifs enregistrés sous `app.api.v1.routers`, et `test_router_root_audit_lists_every_registered_api_v1_router_module` bloque un audit partiel.
- CR-2 corrigé: `backend/app/api/v1/routers/admin/llm/observability.py` importe désormais ses handlers depuis `router_logic.admin.llm.observability`, et l'allowlist routeur-vers-routeur a été supprimée.
- CR-3 corrigé: les nouveaux modules applicatifs signalés ont reçu une docstring de module en français.

Validation après corrections:

- `.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check .` -> PASS.
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` -> PASS.
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_api_router_architecture.py app/tests/unit/test_api_error_contracts.py app/tests/integration/test_api_v1_router_contracts.py tests/unit/test_story_70_14_transition_guards.py::test_admin_observability_router_exposes_only_observability_endpoints` -> 43 passed.
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` -> 3108 passed, 12 skipped.
- `git diff --check` -> PASS, avec avertissements CRLF uniquement.
