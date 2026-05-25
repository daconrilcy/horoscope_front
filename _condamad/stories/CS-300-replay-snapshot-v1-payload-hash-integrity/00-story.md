# Story CS-300 replay-snapshot-v1-payload-hash-integrity: Repair replay_snapshot_v1 Payload Hash Integrity
Status: done

## Trigger / Source

- Source brief: `_story_briefs/cs-300-fix-replay-snapshot-v1-payload-hash-integrity.md`.
- Selected mode: Repo-informed story.
- Source problem: `create_snapshot` encrypts sanitized replay input, while replay recomputes the hash from another input representation.
- User impact: snapshots created by the real `log_call -> create_snapshot -> replay` path can fail with `input_hash_mismatch`.
- Closure expectation: repair the replay snapshot v1 payload/hash contract without broadening the approved DPO/security storage model.
- Source-alignment evidence: objective, ACs, tasks, evidence, and guardrails preserve the brief stakes without narrowing the defect.

## Objective

Make `replay_snapshot_v1` use one canonical replay payload representation for encrypted storage, stored `input_hash`, and replay integrity checks.

## Target State

- `log_call -> create_snapshot -> persisted snapshot -> replay` succeeds when the canonical payload and stored hash match.
- The stored `llm_replay_snapshots.input_hash` is computed from the same canonical payload that is encrypted for replay.
- Replay refusal remains explicit for incomplete, expired, purged, or canonical-hash-mismatched snapshots.
- DPO/security forbidden data remains absent from DB, admin API payloads, OpenAPI exposure, metadata, and replay audit details.
- Tests no longer prove replay by encrypting a fabricated raw input path that bypasses the application snapshot creation path.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-300-fix-replay-snapshot-v1-payload-hash-integrity.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-300` after `CS-299`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output.
- Evidence 4: `backend/app/services/replay_snapshot_v1_service.py` - `create_snapshot` encrypts `snapshot_metadata["sanitized_input"]`.
- Evidence 5: `backend/app/ops/llm/replay_service.py` - replay recomputes `compute_input_hash(user_input)` before mismatch refusal.
- Evidence 6: `backend/tests/unit/test_replay_snapshot_v1_execution_audit.py` - current tests build snapshots with `encrypt_input(user_input)`.
- Evidence 7: `docs/architecture/replay-snapshot-v1-dpo-security-approval-request.md` - approved controls forbid raw sensitive data and public exposure.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Canonical replay payload/hash contract for `replay_snapshot_v1`.
  - Snapshot creation, replay integrity check, redacted audit behavior, and related backend tests.
  - Existing admin replay snapshot API exposure guards only as regression proof.
- Out of scope:
  - Frontend UI, new public routes, new client generation, DB schema changes, auth model changes, i18n, styling, build tooling, and migrations.
- Explicit non-goals:
  - No storage of raw prompts, raw birth data, exact coordinates, direct identifiers, secrets, or provider credentials.
  - No second replay store, no public replay API, no frontend route, and no DPO/security decision change.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Align encrypted payload, stored hash, and replay integrity checks on one canonical replay payload.
  - Preserve existing DPO/security redaction and audit boundaries.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: faithful replay requires data forbidden by `DPO-REPLAY-SNAPSHOT-V1-RETENTION-001`.
- Additional validation rules:
  - Runtime evidence must include `pytest` coverage for the real `log_call -> create_snapshot -> replay` path.
  - Runtime evidence must include `app.routes` and `app.openapi()` exposure guards for replay snapshot admin API boundaries.
  - Static evidence must prove fabricated `encrypt_input(user_input)` replay setup is not the success-path proof.

## Dependencies / Closure Map

- CS-295 storage and redaction decisions remain the approved source for persisted replay snapshot fields.
- CS-296 retention and purge behavior remains in force; this story must not change expiry or purge semantics.
- CS-298 execution/audit behavior remains the owner of replay success/refusal evidence and redacted audit details.
- CS-299 closure evidence must be rechecked after the payload/hash repair and recorded as still valid or superseded.
- DPO/security decision `DPO-REPLAY-SNAPSHOT-V1-RETENTION-001` remains binding; forbidden data requires a new decision.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, service runtime behavior, `app.routes`, and `app.openapi()` prove the backend contract. |
| Baseline Snapshot | yes | Before/after artifacts prove the intended replay payload/hash delta and unchanged exposure surface. |
| Ownership Routing | yes | Replay snapshot lifecycle remains owned by backend service/runtime modules. |
| Allowlist Exception | no | No allowlist handling is authorized for this canonical contract repair. |
| Contract Shape | yes | Canonical payload, hash input, refusal reasons, and redacted audit fields need exact shape. |
| Batch Migration | no | No batch migration or multi-record conversion is in scope. |
| Reintroduction Guard | yes | Alternate payload/hash paths and fabricated replay test setup must stay out. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The real snapshot replay path succeeds. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_replay_snapshot_v1_execution_audit.py`. |
| AC2 | Stored hash uses the canonical replay payload. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_replay_snapshot_v1_db_redaction.py`. |
| AC3 | Invalid snapshot states are refused explicitly. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_replay_snapshot_v1_execution_audit.py`. |
| AC4 | Fabricated raw encrypted replay setup is not the success proof. | Evidence profile: targeted_forbidden_symbol_scan; `rg` and `pytest` check replay tests. |
| AC5 | DPO/security forbidden data remains absent. | Evidence profile: repo_wide_negative_scan; `pytest -q backend/tests/unit/test_replay_snapshot_v1_redaction.py`. |
| AC6 | Admin replay exposure stays internal. | Evidence profile: runtime_openapi_contract; `pytest` checks `app.routes` and `app.openapi()`. |
| AC7 | Service ownership remains single-owner. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/architecture/test_replay_snapshot_v1_execution_boundary.py`. |
| AC8 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks the story evidence directory. |

## Implementation Tasks

- [ ] Task 1: Define one canonical replay payload helper or value object owned by `replay_snapshot_v1` service/runtime code. (AC: AC1, AC2)
- [ ] Task 2: Calculate `llm_replay_snapshots.input_hash` from the same canonical payload that is encrypted for replay. (AC: AC2)
- [ ] Task 3: Update replay integrity checking to compare the stored hash against the canonical decrypted replay payload. (AC: AC1, AC3)
- [ ] Task 4: Replace fabricated success-path tests with a real `log_call -> create_snapshot -> replay` test. (AC: AC1, AC4)
- [ ] Task 5: Keep incomplete, expired, purged, and hash-mismatch refusal paths explicit and audited without raw payload details. (AC: AC3, AC5)
- [ ] Task 6: Preserve admin API and OpenAPI exposure boundaries with `app.routes`, `app.openapi()`, and architecture tests. (AC: AC6, AC7)
- [ ] Task 7: Persist before/after evidence and validation output under this story evidence directory. (AC: AC8)
- [ ] Task 8: Recheck CS-299 closure evidence after repair and record whether it remains valid or is superseded. (AC: AC8)

## Files to Inspect First

- `docs/architecture/replay-snapshot-v1-storage-security-model.md`
- `docs/architecture/replay-snapshot-v1-dpo-security-approval-request.md`
- `backend/app/core/sensitive_data.py`
- `backend/app/domain/llm/runtime/observability_service.py`
- `backend/app/services/replay_snapshot_v1_service.py`
- `backend/app/ops/llm/replay_service.py`
- `backend/tests/unit/test_replay_snapshot_v1_execution_audit.py`
- `backend/tests/integration/test_replay_snapshot_v1_db_redaction.py`

## Runtime Source of Truth

- Primary source of truth:
  - `pytest` execution of replay snapshot service tests and integration redaction tests.
  - `app.routes`, `app.openapi()`, and admin API `TestClient` tests for exposure boundaries.
- Secondary evidence:
  - Targeted `rg` scans for fabricated replay test setup and forbidden public replay paths.
- Static scans alone are not sufficient for this story because:
  - Hash integrity and replay refusal must be proven through the loaded backend runtime path.

## Contract Shape

- Contract type:
  - Backend replay snapshot payload/hash integrity contract.
- Fields:
  - `input_enc`: encrypted canonical replay payload approved by the DPO/security model.
  - `input_hash`: deterministic hash computed from the same canonical replay payload.
  - `sanitized_input`: redacted representation used only inside the approved replay payload contract.
  - `reason`: explicit replay refusal reason, including `input_hash_mismatch` for canonical hash mismatch.
- Required fields:
  - `input_enc`
  - `input_hash`
  - `snapshot_type`
  - `expires_at`
- Optional fields:
  - Existing redacted metadata references already approved by the storage model.
- Status codes:
  - Existing admin API status codes remain unchanged for replay snapshot endpoints.
- Serialization names:
  - Existing admin API response field names remain unchanged.
- Frontend type impact:
  - none.
- Generated contract impact:
  - `app.openapi()` must keep replay snapshot exposure limited to approved admin paths.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-300-replay-snapshot-v1-payload-hash-integrity/evidence/replay-hash-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-300-replay-snapshot-v1-payload-hash-integrity/evidence/replay-hash-after.txt`
- Expected invariant:
  - The only intended backend behavior delta is canonical replay payload/hash agreement for `replay_snapshot_v1`.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Replay payload canonicalization | `backend/app/services/replay_snapshot_v1_service.py` or a local service helper | API router, frontend, or DB model. |
| Replay integrity check | `backend/app/ops/llm/replay_service.py` using service-owned contract | Test-only helper or admin API layer. |
| Sensitive data policy | `backend/app/core/sensitive_data.py` | Ad hoc sanitizer in replay execution code. |
| Runtime observability handoff | `backend/app/domain/llm/runtime/observability_service.py` | Direct DB write from UI or route layer. |

## Mandatory Reuse / DRY Constraints

- Reuse the existing `compute_input_hash`, encryption helpers, sensitive-data sanitizer, service models, and audit event writer.
- Introduce one canonical payload/hash path only; do not duplicate hash normalization in tests and runtime code.
- Keep replay snapshot lifecycle under the existing service/runtime boundary.

## No Legacy / Forbidden Paths

- No legacy replay payload path may be added for this contract.
- No compatibility replay hash path may be added for this contract.
- No fallback replay hash path may be added for this contract.
- Do not add public replay paths, frontend replay surfaces, raw prompt storage, raw birth data storage, exact coordinates, direct identifiers, or secrets.
- Do not retain a test-only success path that proves replay through `encrypt_input(user_input)` on fabricated raw input.

## Reintroduction Guard

- Guard exact forbidden symbols and paths:
  - `encrypt_input(user_input)` in replay snapshot success-path tests.
  - Public replay paths `/v1/replay_snapshot_v1`, `/v1/public/replay_snapshot_v1`, `/api/replay_snapshot_v1`, and `/replay_snapshot_v1`.
  - Raw sensitive data keys listed by the DPO/security model in replay metadata, admin responses, and audit details.
- Required deterministic guard:
  - `rg -n "encrypt_input\\(user_input\\)" backend/tests/unit/test_replay_snapshot_v1_execution_audit.py`
  - `pytest -q backend/tests/architecture/test_admin_replay_snapshot_v1_public_exposure.py`

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Admin API route ownership remains isolated from service logic. | `pytest` admin API and architecture tests. |
| RG-022 `align-prompt-generation-story-validation-paths` | Validation paths must point to collected backend pytest files. | `pytest` commands use explicit backend test files. |
| Needs-investigation | Registry has no exact `replay_snapshot_v1` payload/hash guardrail. | Resolver output recorded in evidence. |
| Non-applicable example | RG-047 frontend inline styles are out of scope because no frontend files are touched. | Manual check: domain boundary excludes frontend. |
| Non-applicable example | RG-052 frontend CSS namespaces are out of scope because no styling files are touched. | Manual check: domain boundary excludes styling. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Guardrail resolver output | `_condamad/stories/CS-300-replay-snapshot-v1-payload-hash-integrity/evidence/guardrails.txt` | Preserve scoped guardrail selection. |
| Before replay hash evidence | `_condamad/stories/CS-300-replay-snapshot-v1-payload-hash-integrity/evidence/replay-hash-before.txt` | Show failing pre-change path. |
| After replay hash evidence | `_condamad/stories/CS-300-replay-snapshot-v1-payload-hash-integrity/evidence/replay-hash-after.txt` | Show canonical post-change path. |
| Validation output | `_condamad/stories/CS-300-replay-snapshot-v1-payload-hash-integrity/evidence/validation.txt` | Preserve lint and test command output. |
| CS-299 recheck | `_condamad/stories/CS-300-replay-snapshot-v1-payload-hash-integrity/evidence/cs-299-recheck.txt` | Track CS-299 impact. |
| Review output | `_condamad/stories/CS-300-replay-snapshot-v1-payload-hash-integrity/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this canonical replay payload/hash repair.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/services/replay_snapshot_v1_service.py` - own canonical replay payload/hash creation.
- `backend/app/ops/llm/replay_service.py` - verify replay integrity against the canonical payload contract.
- `backend/app/domain/llm/runtime/observability_service.py` - preserve `log_call` handoff into snapshot creation.
- `backend/tests/unit/test_replay_snapshot_v1_execution_audit.py` - add real path replay success and refusal coverage.
- `backend/tests/integration/test_replay_snapshot_v1_db_redaction.py` - prove DB hash and payload redaction contract.
- `_condamad/stories/CS-300-replay-snapshot-v1-payload-hash-integrity/evidence/validation.txt` - persist validation output.

Likely tests:

- `backend/tests/unit/test_replay_snapshot_v1_execution_audit.py`
- `backend/tests/integration/test_replay_snapshot_v1_db_redaction.py`
- `backend/tests/unit/test_replay_snapshot_v1_redaction.py`
- `backend/tests/api/admin/test_replay_snapshot_v1_api.py`
- `backend/tests/architecture/test_replay_snapshot_v1_execution_boundary.py`
- `backend/tests/architecture/test_admin_replay_snapshot_v1_public_exposure.py`
- `_condamad/stories/CS-300-replay-snapshot-v1-payload-hash-integrity/evidence/cs-299-recheck.txt` - record CS-299 evidence impact.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/alembic/**` - out of scope; no schema migration is authorized.
- `backend/app/api/**` - out of scope unless an existing admin exposure guard needs a test-only assertion.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `python -B -m pytest -q tests\unit\test_replay_snapshot_v1_execution_audit.py --tb=short`
- VC2: `python -B -m pytest -q tests\integration\test_replay_snapshot_v1_db_redaction.py --tb=short`
- VC3: `python -B -m pytest -q tests\unit\test_replay_snapshot_v1_redaction.py --tb=short`
- VC4: `python -B -m pytest -q tests\api\admin\test_replay_snapshot_v1_api.py --tb=short`
- VC5: `python -B -m pytest -q tests\architecture\test_replay_snapshot_v1_execution_boundary.py --tb=short`
- VC6: `python -B -m pytest -q tests\architecture\test_admin_replay_snapshot_v1_public_exposure.py --tb=short`
- VC7: `python -B -m pytest -q tests\unit\test_replay_snapshot_v1_*.py tests\integration\test_replay_snapshot_v1_*.py --tb=short`
- VC8: `python -B -m pytest -q tests\api\admin\test_replay_snapshot_v1_api.py tests\architecture\test_admin_replay_snapshot_v1_public_exposure.py --tb=short`
- VC9: `ruff format .`
- VC10: `ruff check .`
- VC11: `rg -n "encrypt_input\\(user_input\\)" tests\unit\test_replay_snapshot_v1_execution_audit.py`
- VC12: `python -c "from app.main import app; assert all('/v1/replay_snapshot_v1' not in p for p in app.openapi()['paths'])"`
- VC13: `python -c "from app.main import app; assert all(getattr(r, 'path', '') != '/replay_snapshot_v1' for r in app.routes)"`

## Regression Risks

- Hash repair could accidentally persist a richer payload than the approved sanitized replay payload.
- Replay success could be restored through a test-only path instead of the real `log_call` lifecycle.
- Admin API changes could broaden replay snapshot exposure beyond approved internal paths.
- Audit details could leak payload fragments while recording replay success or refusal.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python, Ruff, or pytest command.
- Run backend validation from `backend` after activation unless a command explicitly uses a repository-root path.
- Persist validation output under the story evidence directory before moving the story beyond implementation.

## References

- `_story_briefs/cs-300-fix-replay-snapshot-v1-payload-hash-integrity.md`
- `docs/architecture/replay-snapshot-v1-storage-security-model.md`
- `docs/architecture/replay-snapshot-v1-dpo-security-approval-request.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/story-status.md`
