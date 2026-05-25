# Story CS-301 revalidate-replay-snapshot-v1-runtime-closure: Revalidate replay_snapshot_v1 Runtime Closure
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-301-revalidate-replay-snapshot-v1-runtime-closure-after-integrity-fix.md`.
- Selected mode: Repo-informed story.
- Source problem: CS-299 closed replay runtime before the real `log_call -> snapshot -> replay` path was proven after the payload/hash repair.
- User impact: CS-278 can be marked done from weak proof while real persisted snapshots still fail replay integrity.
- Closure expectation: revalidate the runtime closure after CS-300 and update CONDAMAD evidence plus the delivery report.
- Source-alignment evidence: objective, ACs, tasks, evidence, and guardrails preserve the brief stakes without narrowing the proof problem.

## Objective

Prove that the approved `replay_snapshot_v1` runtime closure remains valid after CS-300 by rerunning focused backend validation,
recording the real persisted snapshot replay path, and correcting closure evidence that relied on insufficient tests.

## Target State

- The final evidence explicitly proves `log_call -> snapshot -> replay` using snapshots produced by application runtime code.
- Replay success no longer depends only on a fabricated `encrypt_input(user_input)` setup outside the application snapshot path.
- DPO/security constraints remain enforced for forbidden data, redacted audit details, and approved encrypted payload handling.
- `replay_snapshot_v1` exposure remains strictly admin/internal in `app.routes`, `app.openapi()`, and `frontend/src` scans.
- `_condamad/reports/CS-256-CS-291-delivery-report.md` states that CS-278 closure is valid only after the CS-300 repair proof.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-301-revalidate-replay-snapshot-v1-runtime-closure-after-integrity-fix.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-301` after `CS-300`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output.
- Evidence 4: `_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/generated/10-final-evidence.md` - closure claim reviewed.
- Evidence 5: `_condamad/stories/CS-278-replay-snapshot-v1-implementation/generated/10-final-evidence.md` - parent closure evidence reviewed.
- Evidence 6: `_condamad/reports/CS-256-CS-291-delivery-report.md` - delivery report currently ties CS-278 closure to CS-299.
- Evidence 7: `_condamad/stories/CS-300-replay-snapshot-v1-payload-hash-integrity/00-story.md` - CS-300 repair contract reviewed.
- Evidence 8: CS-300 final evidence files are not present in this workspace at story-writing time; dev execution must verify the repair first.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Runtime proof for `replay_snapshot_v1` after CS-300 payload/hash repair.
  - CONDAMAD final evidence updates for CS-278 and CS-299.
  - Delivery report correction for CS-278 closure status after CS-300.
  - Backend replay tests, route/OpenAPI exposure checks, forbidden-data scans, and evidence artifacts.
- Out of scope:
  - Frontend UI changes, new API routes, generated clients, DB schema changes, auth changes, i18n, styling, build tooling, and migrations.
- Explicit non-goals:
  - No new replay service, no DPO/security model change, no role expansion, no public route, and no bulk export.
  - No behavior change beyond evidence/report correction and validation-driven closure classification.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Update evidence and report artifacts only after replay runtime validation proves the CS-300 repair.
  - Reclassify CS-278 or CS-299 evidence as not closed when the real persisted snapshot replay path fails.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-300 remains unimplemented or the real replay path still fails after the repair attempt.
- Additional validation rules:
  - Runtime evidence must include `pytest` for the real `log_call -> snapshot -> replay` path.
  - Runtime evidence must include `app.routes` and `app.openapi()` checks for replay exposure.
  - Static evidence must include `frontend/src` and backend scans for unauthorized public/client replay surfaces.
  - Report evidence must cite CS-300 as the repair point before CS-278 closure is reaffirmed.

## Dependencies / Closure Map

- CS-300 is the direct prerequisite; CS-301 execution must first confirm CS-300 final evidence and repair validation are present.
- CS-278 remains the parent implementation story whose `done` evidence is being revalidated.
- CS-299 remains the earlier runtime closure story whose proof must be corrected or superseded.
- CS-295 through CS-298 remain historical implementation slices and must not be broadened by this proof story.
- The delivery report must reflect the actual replay closure state after CS-300, not the insufficient CS-299-only proof.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, `TestClient`, `app.routes`, and `app.openapi()` prove replay runtime behavior and exposure. |
| Baseline Snapshot | yes | Before/after evidence proves report and final evidence changes are tied to the CS-300 repair. |
| Ownership Routing | yes | Replay evidence remains owned by backend story artifacts and report files, not frontend or route rewrites. |
| Allowlist Exception | no | No allowlist handling is authorized for this proof and reporting story. |
| Contract Shape | yes | The evidence must name exact runtime path, forbidden data tokens, exposure state, and report closure wording. |
| Batch Migration | no | No batch migration or multi-record conversion is in scope. |
| Reintroduction Guard | yes | Fabricated-only replay proof and public/client replay exposure must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The real replay path is proven. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_replay_snapshot_v1_execution_audit.py`. |
| AC2 | Fabricated-only replay proof is rejected. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans replay tests and final evidence. |
| AC3 | CS-278 closure cites CS-300 repair proof. | Evidence profile: baseline_before_after_diff; `python` checks CS-278 final evidence text. |
| AC4 | CS-299 closure is corrected or superseded. | Evidence profile: baseline_before_after_diff; `python` checks CS-299 final evidence text. |
| AC5 | Delivery report states the repaired closure. | Evidence profile: baseline_before_after_diff; `python` checks the delivery report text. |
| AC6 | Replay targeted validations pass. | Evidence profile: json_contract_shape; `pytest -q backend/tests/api/admin/test_replay_snapshot_v1_api.py`. |
| AC7 | Backend lint passes. | Evidence profile: ast_architecture_guard; `ruff check .` from `backend`. |
| AC8 | Full backend pytest status is recorded. | Evidence profile: json_contract_shape; `pytest -q backend/tests` or `python -B -m pytest -q --tb=short`. |
| AC9 | Runtime exposure stays internal. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`. |
| AC10 | Forbidden replay data stays absent. | Evidence profile: repo_wide_negative_scan; `rg` scans forbidden tokens and `pytest` checks redaction. |
| AC11 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks this story evidence directory. |

## Implementation Tasks

- [ ] Task 1: Confirm CS-300 has final evidence and validation output before revalidating closure. (AC: AC1, AC3, AC4)
- [ ] Task 2: Run the replay runtime test set covering `log_call -> snapshot -> replay`. (AC: AC1, AC6)
- [ ] Task 3: Scan replay tests and evidence so fabricated-only `encrypt_input(user_input)` proof cannot be the success proof. (AC: AC2)
- [ ] Task 4: Verify `app.routes`, `app.openapi()`, and `TestClient` keep replay under approved admin/internal paths. (AC: AC6, AC9)
- [ ] Task 5: Run forbidden-data scans for replay outputs, metadata, admin responses, and audit details. (AC: AC10)
- [ ] Task 6: Run `ruff check .` and full backend pytest, then persist validation output. (AC: AC7, AC8, AC11)
- [ ] Task 7: Update CS-278 final evidence with CS-300 repair proof and current validation status. (AC: AC3, AC11)
- [ ] Task 8: Update CS-299 final evidence to disclose the original proof defect and the corrected status. (AC: AC4, AC11)
- [ ] Task 9: Update the CS-256 to CS-291 delivery report with the repaired CS-278 closure state. (AC: AC5, AC11)

## Files to Inspect First

- `_condamad/stories/CS-300-replay-snapshot-v1-payload-hash-integrity/generated/10-final-evidence.md`
- `_condamad/stories/CS-300-replay-snapshot-v1-payload-hash-integrity/evidence/validation.txt`
- `_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/generated/10-final-evidence.md`
- `_condamad/stories/CS-278-replay-snapshot-v1-implementation/generated/10-final-evidence.md`
- `_condamad/reports/CS-256-CS-291-delivery-report.md`
- `backend/tests/unit/test_replay_snapshot_v1_execution_audit.py`
- `backend/tests/integration/test_replay_snapshot_v1_db_redaction.py`
- `backend/tests/api/admin/test_replay_snapshot_v1_api.py`
- `backend/tests/architecture/test_admin_replay_snapshot_v1_public_exposure.py`

## Runtime Source of Truth

- Primary source of truth:
  - `pytest` execution for replay runtime, DB redaction, admin API, and architecture exposure tests.
  - `TestClient`, `app.routes`, and `app.openapi()` checks for admin/internal exposure.
- Secondary evidence:
  - Targeted `rg` scans for fabricated-only proof, forbidden data tokens, frontend exposure, and public replay paths.
- Static scans alone are not sufficient for this story because:
  - The closure defect is about the loaded runtime path from logged call to persisted snapshot and replay.

## Contract Shape

- Contract type:
  - Backend runtime closure evidence and delivery report contract.
- Fields:
  - `real_path`: evidence must name `log_call -> snapshot -> replay`.
  - `repair_story`: evidence must name `CS-300`.
  - `closure_story`: evidence must name `CS-299` as corrected or superseded.
  - `parent_story`: evidence must name `CS-278` as closed only after CS-300 validation.
  - `exposure_state`: evidence must state admin/internal only.
  - `forbidden_data_scan`: evidence must include the token set from the brief.
- Required fields:
  - `real_path`
  - `repair_story`
  - `parent_story`
  - `exposure_state`
  - `forbidden_data_scan`
- Optional fields:
  - CI action reference when full backend pytest cannot complete locally.
- Status codes:
  - Existing admin API status codes remain unchanged.
- Serialization names:
  - Existing replay snapshot API response field names remain unchanged.
- Frontend type impact:
  - none.
- Generated contract impact:
  - `app.openapi()` must keep replay snapshot exposure limited to approved admin paths.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-301-revalidate-replay-snapshot-v1-runtime-closure/evidence/closure-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-301-revalidate-replay-snapshot-v1-runtime-closure/evidence/closure-after.txt`
- Expected invariant:
  - The only intended artifact delta is corrected closure evidence and report wording after CS-300 validation.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Replay closure evidence | `_condamad/stories/CS-278-replay-snapshot-v1-implementation/generated/10-final-evidence.md` | Frontend or backend source. |
| Closure correction evidence | `_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/generated/10-final-evidence.md` | New parallel report. |
| Delivery report status | `_condamad/reports/CS-256-CS-291-delivery-report.md` | Story tracker only. |
| Runtime replay proof | `backend/tests/**replay_snapshot_v1**` and loaded `app` checks | Fabricated-only helper proof. |

## Mandatory Reuse / DRY Constraints

- Reuse the CS-300 repair evidence, existing replay test suites, existing admin exposure tests, and existing CONDAMAD final evidence files.
- Do not duplicate closure reports; update the canonical CS-278, CS-299, and delivery report artifacts only.
- Keep validation commands in one persisted story evidence transcript rather than scattering untracked proof files.

## No Legacy / Forbidden Paths

- No legacy replay proof path may be introduced or retained as the sole success evidence.
- No compatibility replay path may be added for this proof story.
- No fallback replay route, report, or evidence capsule may be created.
- Do not add public replay routes, frontend replay surfaces, generated clients, raw prompt storage, raw birth data storage, coordinates, or secrets.
- Do not claim closure from `encrypt_input(user_input)` fabricated setup without the real application snapshot path proof.

## Reintroduction Guard

- Guard exact forbidden symbols and paths:
  - `encrypt_input(user_input)` as the only replay success proof.
  - Public replay paths `/v1/replay_snapshot_v1`, `/v1/public/replay_snapshot_v1`, `/api/replay_snapshot_v1`, and `/replay_snapshot_v1`.
  - Frontend replay surfaces under `frontend/src`.
  - Forbidden data keys `email`, `payload_enc`, `birth_date`, `birth_time`, `birth_place`, `latitude`, `longitude`.
  - Forbidden data keys `raw_prompt`, `raw_output`, `structured_output`, `password`, and `api_key`.
- Required deterministic guard:
  - `pytest -q backend/tests/architecture/test_admin_replay_snapshot_v1_public_exposure.py`
  - `rg -n "replay_snapshot_v1" frontend/src`
  - `rg -n "email|payload_enc|birth_date|birth_time|birth_place|latitude|longitude|raw_prompt|raw_output|structured_output|password|api_key" backend/tests`

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | API ownership must not absorb replay proof logic. | `pytest` architecture tests. |
| RG-003 `converge-api-v1-route-architecture` | Runtime route inventory must preserve approved admin paths. | `app.routes`; `app.openapi()`. |
| RG-007 `converge-admin-llm-observability-router` | Admin LLM observability remains the replay API owner. | `TestClient`; OpenAPI diff. |
| RG-022 `align-prompt-generation-story-validation-paths` | Validation paths must point to collected backend pytest files. | Explicit `pytest` commands. |
| Non-applicable example | RG-047 frontend inline styles are out of scope because no frontend files are modified. | Manual check: domain boundary excludes UI. |
| Non-applicable example | RG-052 frontend CSS namespaces are out of scope because no styling files are modified. | Manual check: domain boundary excludes CSS. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Guardrail resolver output | `_condamad/stories/CS-301-revalidate-replay-snapshot-v1-runtime-closure/evidence/guardrails.txt` | Preserve scoped guardrail selection. |
| Closure before snapshot | `_condamad/stories/CS-301-revalidate-replay-snapshot-v1-runtime-closure/evidence/closure-before.txt` | Record pre-update proof state. |
| Closure after snapshot | `_condamad/stories/CS-301-revalidate-replay-snapshot-v1-runtime-closure/evidence/closure-after.txt` | Record corrected closure state. |
| Runtime surface status | `_condamad/stories/CS-301-revalidate-replay-snapshot-v1-runtime-closure/evidence/runtime-surface-status.txt` | Preserve routes and OpenAPI checks. |
| Forbidden data scan | `_condamad/stories/CS-301-revalidate-replay-snapshot-v1-runtime-closure/evidence/forbidden-data-scan.txt` | Preserve data leakage scan results. |
| Validation output | `_condamad/stories/CS-301-revalidate-replay-snapshot-v1-runtime-closure/evidence/validation.txt` | Preserve lint and test command output. |
| Review output | `_condamad/stories/CS-301-revalidate-replay-snapshot-v1-runtime-closure/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this runtime closure proof.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/stories/CS-278-replay-snapshot-v1-implementation/generated/10-final-evidence.md` - update parent closure proof after CS-300.
- `_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/generated/10-final-evidence.md` - disclose corrected closure basis.
- `_condamad/reports/CS-256-CS-291-delivery-report.md` - align delivery status with CS-300 repair evidence.
- `_condamad/stories/CS-301-revalidate-replay-snapshot-v1-runtime-closure/evidence/validation.txt` - persist validation output.
- `_condamad/stories/CS-301-revalidate-replay-snapshot-v1-runtime-closure/evidence/runtime-surface-status.txt` - persist route evidence.
- `_condamad/stories/CS-301-revalidate-replay-snapshot-v1-runtime-closure/evidence/forbidden-data-scan.txt` - persist scan evidence.

Likely tests:

- `backend/tests/unit/test_replay_snapshot_v1_execution_audit.py`
- `backend/tests/integration/test_replay_snapshot_v1_db_redaction.py`
- `backend/tests/api/admin/test_replay_snapshot_v1_api.py`
- `backend/tests/architecture/test_replay_snapshot_v1_execution_boundary.py`
- `backend/tests/architecture/test_admin_replay_snapshot_v1_public_exposure.py`

Files not expected to change:

- `backend/app/**` - out of scope unless CS-300 remains incomplete and implementation is explicitly redirected.
- `frontend/src/**` - out of scope; only read-only exposure scans are authorized.
- `backend/alembic/**` - out of scope; no schema migration is authorized.
- `docs/architecture/**` - out of scope; DPO/security decisions remain unchanged.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `python -B -m pytest -q tests\unit\test_replay_snapshot_v1_execution_audit.py --tb=short`
- VC2: `python -B -m pytest -q tests\integration\test_replay_snapshot_v1_db_redaction.py --tb=short`
- VC3: `python -B -m pytest -q tests\api\admin\test_replay_snapshot_v1_api.py --tb=short`
- VC4: `python -B -m pytest -q tests\architecture\test_replay_snapshot_v1_execution_boundary.py --tb=short`
- VC5: `python -B -m pytest -q tests\architecture\test_admin_replay_snapshot_v1_public_exposure.py --tb=short`
- VC6: `ruff check .`
- VC7: `python -B -m pytest -q --tb=short`
- VC8: `python -c "from app.main import app; assert all(path.startswith('/v1/admin/audit') for path in app.openapi()['paths'] if 'replay_snapshot_v1' in path)"`
- VC9: `python -c "from app.main import app; assert all('/replay_snapshot_v1' != getattr(route, 'path', '') for route in app.routes)"`
- VC10: `rg -n "replay_snapshot_v1" frontend/src`
- VC11: `rg -n "encrypt_input\\(user_input\\)" tests\unit\test_replay_snapshot_v1_execution_audit.py`
- VC12: `rg -n "email|payload_enc|birth_date|birth_time|birth_place|latitude|longitude|raw_prompt|raw_output|structured_output|password|api_key" tests`

## Regression Risks

- Revalidation could preserve the CS-299 closure wording without naming the original proof defect.
- Report updates could overstate CS-278 closure before CS-300 final evidence exists.
- Public/client exposure could be missed by checking only OpenAPI and not `app.routes` or `frontend/src`.
- Forbidden data scans could omit brief-mandated tokens such as `email` or `payload_enc`.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python, Ruff, or pytest command.
- Run backend validation from `backend` after activation unless a command explicitly uses a repository-root path.
- Persist validation output under this story evidence directory before moving the story beyond implementation.
- Do not update CS-278, CS-299, or the delivery report to a passing closure state without CS-300 repair proof.

## References

- `_story_briefs/cs-301-revalidate-replay-snapshot-v1-runtime-closure-after-integrity-fix.md`
- `_condamad/stories/CS-300-replay-snapshot-v1-payload-hash-integrity/00-story.md`
- `_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/generated/10-final-evidence.md`
- `_condamad/stories/CS-278-replay-snapshot-v1-implementation/generated/10-final-evidence.md`
- `_condamad/reports/CS-256-CS-291-delivery-report.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/story-status.md`
