# Story CS-298 replay-snapshot-v1-execution-audit: Implement replay_snapshot_v1 Execution And Audit
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-298-implement-replay-snapshot-v1-execution-audit.md`.
- Required dependency: CS-295 replay snapshot storage and redaction.
- Required dependency: CS-296 replay snapshot service retention and purge.
- Required dependency: CS-297 internal admin replay snapshot API.
- Existing owner found: `backend/app/ops/llm/replay_service.py` owns current LLM replay orchestration behavior.
- Existing owner found: `backend/app/services/ops/audit_service.py` owns bounded audit event recording.
- Existing owner found: `backend/app/domain/audit/safe_details.py` owns safe audit detail DTO normalization.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: replay snapshots need controlled internal execution and safe audit logs for reads, replay attempts and purge outcomes.
- Source-alignment evidence: PASS; replay execution, refusal rules, audit logging, non-leakage and reproducibility limits are preserved.

## Objective

Implement bounded `replay_snapshot_v1` execution orchestration and mandatory audit events for snapshot metadata reads, replay attempts and purges.

The implementation must reuse existing replay, snapshot, admin API and audit owners, refuse unsafe snapshot states, avoid raw provider or prompt material, and document
deterministic limits.

## Target State

- Admin snapshot metadata reads record one safe audit event.
- Admin replay attempts record one safe audit event for success and failed outcomes.
- Admin purge requests record one safe audit event for success and failed outcomes.
- Replay execution uses only the approved snapshot data already stored by CS-295 and governed by CS-296.
- Expired, purged or incomplete snapshots are refused before provider execution.
- Audit details contain bounded identifiers, statuses, reason codes and diff summaries only.
- Runtime checks prove API wiring with `app.routes`, OpenAPI exposure with `app.openapi()` and HTTP behavior through `TestClient`.
- Reproducibility documentation states deterministic inputs, non-deterministic provider limits and forbidden raw data surfaces.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-298-implement-replay-snapshot-v1-execution-audit.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-298`.
- Evidence 3: `backend/app/ops/llm/replay_service.py` - current replay orchestration owner inspected.
- Evidence 4: `backend/app/services/ops/audit_service.py` - canonical audit recording owner inspected.
- Evidence 5: `backend/app/domain/audit/safe_details.py` - bounded audit detail DTO owner inspected.
- Evidence 6: `backend/app/services/llm_observability/` - existing LLM observability service boundary inspected.
- Evidence 7: `backend/app/domain/llm/runtime/` - LLM runtime owner exists and was scoped.
- Evidence 8: `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/00-story.md` - admin API dependency inspected.
- Evidence 9: `resolve_guardrails.py` - scoped resolver run for backend replay, audit log, no-sensitive-data and runtime contracts.
- Repository structure alert: backend, backend/app, backend/tests, frontend and frontend/src exist in this workspace.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend replay orchestration for `replay_snapshot_v1`.
  - Audit events for metadata read, replay attempt and purge outcomes.
  - Safe audit detail DTOs for replay snapshot activity.
  - Runtime refusal for expired, purged or incomplete snapshots.
  - Backend tests proving audit logs do not expose prompt, birth data, secrets or raw provider payloads.
  - Reproducibility documentation for deterministic and non-deterministic replay limits.
- Out of scope:
  - Frontend UI, public routes, support routes, B2B routes, i18n, styling, build tooling and generated public clients.
  - DB schema, migrations, model training, bulk export, prompt modification, provider payload exposure and free-form LLM execution.
- Explicit non-goals:
  - No raw prompt replay.
  - No raw provider output exposure.
  - No model training surface.
  - No mass export feature.
  - No LLM prompt change.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only bounded replay snapshot execution orchestration and audit events.
  - Reuse existing snapshot storage, service, admin API, replay runtime and audit owners.
  - Keep raw prompt, raw birth data, secret and raw provider payload surfaces out of responses and audit details.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-295, CS-296 or CS-297 contract files are not implemented when development starts.
- Additional validation rules:
  - `AST guard` must prove no broad provider execution path bypasses snapshot state checks.
  - `pytest -q tests/unit/test_replay_snapshot_v1_execution_audit.py` must cover replay and audit outcomes from `backend`.
  - `pytest -q tests/api/admin/test_replay_snapshot_v1_api.py` must prove admin read, replay and purge auditing from `backend`.
  - `app.routes` must keep replay snapshot API under the existing admin audit namespace.
  - `app.openapi()` must not expose replay snapshot operations outside the internal admin route family.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, `TestClient`, `app.routes`, `app.openapi()` and `AST guard` prove runtime replay behavior. |
| Baseline Snapshot | yes | Before and after audit/replay artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Replay, audit details, API handlers and docs must stay in canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this replay snapshot execution slice. |
| Contract Shape | yes | Audit events and replay outcomes have exact safe fields and statuses. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Raw prompt, raw provider payload, secret and uncontrolled replay paths must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Admin metadata reads are audited. | Evidence profile: json_contract_shape; `pytest -q tests/api/admin/test_replay_snapshot_v1_api.py`. |
| AC2 | Replay attempts are audited. | Evidence profile: json_contract_shape; `pytest -q tests/unit/test_replay_snapshot_v1_execution_audit.py`. |
| AC3 | Purge outcomes are audited. | Evidence profile: json_contract_shape; `pytest -q tests/api/admin/test_replay_snapshot_v1_api.py`. |
| AC4 | Unsafe snapshot states are refused. | Evidence profile: json_contract_shape; `pytest -q tests/unit/test_replay_snapshot_v1_execution_audit.py`. |
| AC5 | Audit details do not leak sensitive material. | Evidence profile: targeted_forbidden_symbol_scan; `pytest`; `rg`. |
| AC6 | Runtime API wiring stays internal. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`; `TestClient`. |
| AC7 | Replay execution stays bounded. | Evidence profile: ast_architecture_guard; `pytest -q tests/architecture/test_replay_snapshot_v1_execution_boundary.py`. |
| AC8 | Reproducibility limits are documented. | Evidence profile: repo_wide_negative_scan; `rg` checks replay docs and tests. |
| AC9 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-298 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Add safe replay snapshot audit detail DTOs for read, replay and purge outcomes. (AC: AC1, AC2, AC3, AC5)
- [ ] Task 2: Record audit events around admin metadata reads using bounded identifiers and status details. (AC: AC1, AC5)
- [ ] Task 3: Add controlled replay execution from the approved snapshot state. (AC: AC2, AC4, AC7)
- [ ] Task 4: Refuse expired, purged and incomplete snapshots before provider execution. (AC: AC4, AC7)
- [ ] Task 5: Record replay attempt success and failed outcomes through the canonical audit service. (AC: AC2, AC5)
- [ ] Task 6: Record purge success and failed outcomes through the canonical audit service. (AC: AC3, AC5)
- [ ] Task 7: Add non-leakage unit and admin API tests for audit details. (AC: AC1, AC2, AC3, AC5, AC6)
- [ ] Task 8: Add an architecture guard for bounded replay execution ownership. (AC: AC7)
- [ ] Task 9: Document deterministic replay inputs and non-deterministic provider limits. (AC: AC8)
- [ ] Task 10: Persist validation and audit evidence artifacts under the CS-298 story folder. (AC: AC9)

## Files to Inspect First

- `backend/app/services/llm_observability/**`
- `backend/app/ops/llm/replay_service.py`
- `backend/app/domain/llm/runtime/**`
- `backend/app/services/ops/audit_service.py`
- `backend/app/domain/audit/safe_details.py`
- `backend/app/api/v1/routers/admin/audit.py`
- `backend/app/api/v1/routers/admin/replay_snapshot.py`
- `backend/app/services/api_contracts/admin/audit.py`
- `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/00-story.md`
- `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/00-story.md`
- `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/00-story.md`

## Runtime Source of Truth

- Primary source of truth:
  - `pytest`, `TestClient`, `AST guard`, `app.routes` and `app.openapi()`.
- Secondary evidence:
  - Targeted `rg` scans for raw prompt, birth data, secrets, raw provider payloads and uncontrolled replay paths.
- Static scans alone are not sufficient for this story because:
  - Audit events, refusal paths and replay execution must be proven from runtime tests.

## Contract Shape

- Contract type:
  - Backend domain service behavior, audit event details and internal admin API behavior.
- Fields:
  - `action`: one of `replay_snapshot_v1.metadata_read`, `replay_snapshot_v1.replay_attempt` or `replay_snapshot_v1.purge`.
  - `status`: `success` or `failed`.
  - `snapshot_id`: stable snapshot identifier only.
  - `request_id`: request correlation identifier only.
  - `reason`: bounded refusal or failure reason code.
  - `diff_summary`: bounded replay summary without raw text or provider payload.
- Required fields:
  - `action`
  - `status`
  - `snapshot_id`
  - `request_id`
- Optional fields:
  - `reason`
  - `diff_summary`
- Status codes:
  - Existing CS-297 admin API status behavior remains the HTTP source of truth.
- Serialization names:
  - Audit detail keys are emitted with the same snake_case names listed above.
- Frontend type impact:
  - none; no frontend or generated public client surface is in scope.
- Generated contract impact:
  - `app.openapi()` must keep replay snapshot operations inside the internal admin audit route family.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-298-replay-snapshot-v1-execution-audit/evidence/audit-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-298-replay-snapshot-v1-execution-audit/evidence/audit-after.json`
- Expected invariant:
  - The only intended runtime surface delta is safe replay snapshot execution and audit events.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Replay orchestration | `backend/app/ops/llm/replay_service.py` | API router business logic |
| Audit event recording | `backend/app/services/ops/audit_service.py` | Direct ORM writes from routers |
| Safe audit details | `backend/app/domain/audit/safe_details.py` | Unbounded dict assembly in handlers |
| Runtime LLM execution | `backend/app/domain/llm/runtime/**` | New provider execution adapter |
| Admin HTTP behavior | `backend/app/api/v1/routers/admin/replay_snapshot.py` | Public or support routers |
| Reproducibility notes | backend docs or existing replay module docs | Frontend copy or prompt files |

## Mandatory Reuse / DRY Constraints

- Reuse the CS-295 snapshot storage and redaction contract.
- Reuse the CS-296 lifecycle service for retention, purge and snapshot state checks.
- Reuse the CS-297 admin API route ownership and authorization model.
- Reuse `AuditService.record_event` and `to_safe_details` for audit persistence.
- Reuse current LLM runtime gateway abstractions rather than adding a parallel provider executor.
- Do not duplicate sensitive-data sanitization logic outside the canonical audit sanitization path.

## No Legacy / Forbidden Paths

- No legacy replay snapshot route path may be added.
- No compatibility route path may be added for this replay execution.
- No fallback route path may be added for this replay execution.
- Do not add public, support, B2B, frontend or generated-client replay snapshot surfaces.
- Do not store or emit raw prompts, birth data, secrets, encrypted payload bytes or raw provider payloads in audit details.
- Do not add broad free-form replay execution that bypasses snapshot approval, expiry, purge or completeness checks.

## Reintroduction Guard

- Forbidden route paths:
  - `/v1/replay_snapshot_v1`
  - `/v1/public/replay_snapshot_v1`
  - `/v1/support/replay_snapshot_v1`
  - `/api/replay_snapshot_v1`
  - `/replay_snapshot_v1`
- Forbidden audit fields:
  - `raw_prompt`, `birth_date`, `birth_time`, `birth_place`, `latitude`, `longitude`, `email`, `password`, `api_key`, `payload_enc`
- Forbidden runtime surfaces:
  - direct provider execution from admin handlers
  - replay execution before snapshot state validation
  - raw provider output in audit details
- Required deterministic guards:
  - `pytest -q tests/unit/test_replay_snapshot_v1_execution_audit.py`
  - `pytest -q tests/api/admin/test_replay_snapshot_v1_api.py`
  - `pytest -q tests/architecture/test_replay_snapshot_v1_execution_boundary.py`
  - `$env:PYTHONPATH='backend'; python -c "from app.main import app; assert all('/admin/' in p for p in app.openapi()['paths'] if 'replay_snapshot_v1' in p)"`
  - `$env:PYTHONPATH='backend'; python -c "from app.main import app; assert not any(getattr(r,'path','') == '/replay_snapshot_v1' for r in app.routes)"`
  - `rg -n "raw_prompt|birth_date|birth_time|birth_place|latitude|longitude|email|password|api_key|payload_enc" app tests`

## Regression Guardrails

Scope vector:

- backend-domain: yes;
- operation type: create;
- paths: `backend/app/ops/llm`, `backend/app/services/ops`, `backend/app/domain/audit`, `backend/tests`;
- contracts: audit log, replay_snapshot_v1, no-sensitive-data, runtime refusal;
- frontend, DB schema, migration, i18n, style and build: no.

Selected guardrails:

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend API route wiring keeps clear ownership. | `app.routes`; API `pytest`. |
| RG-047 `frontend-inline-styles` | Non-applicable; prevents frontend drift for this backend story. | No frontend file changes. |
| RG-052 `css-namespace-migration` | Non-applicable; prevents style/build drift for this backend story. | No CSS file changes. |

Registry gap:

- No exact replay snapshot audit guardrail was returned by the scoped resolver; story uses local runtime and non-leakage guards instead.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Audit baseline | `_condamad/stories/CS-298-replay-snapshot-v1-execution-audit/evidence/audit-before.json` | Capture pre-change audit behavior. |
| Audit final | `_condamad/stories/CS-298-replay-snapshot-v1-execution-audit/evidence/audit-after.json` | Prove bounded audit event details. |
| Runtime routes | `_condamad/stories/CS-298-replay-snapshot-v1-execution-audit/evidence/routes-after.txt` | Prove internal route exposure. |
| Runtime docs | `_condamad/stories/CS-298-replay-snapshot-v1-execution-audit/evidence/reproducibility.md` | Preserve replay limit notes. |
| Validation output | `_condamad/stories/CS-298-replay-snapshot-v1-execution-audit/evidence/validation.txt` | Keep final command output. |
| Review output | `_condamad/stories/CS-298-replay-snapshot-v1-execution-audit/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist Exception: not applicable
- Reason: no allowlist handling is authorized for this replay snapshot execution slice.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/ops/llm/replay_service.py` - implement bounded replay execution and snapshot state refusal.
- `backend/app/services/ops/audit_service.py` - reuse or extend canonical audit recording behavior.
- `backend/app/domain/audit/safe_details.py` - add bounded replay snapshot audit details.
- `backend/app/api/v1/routers/admin/replay_snapshot.py` - call audit-aware service behavior from existing admin endpoints.
- `backend/app/services/api_contracts/admin/audit.py` - align admin response contract with safe replay outcomes.
- backend docs or replay module docs - document deterministic and non-deterministic replay limits.
- `_condamad/stories/CS-298-replay-snapshot-v1-execution-audit/evidence/audit-before.json` - baseline evidence.
- `_condamad/stories/CS-298-replay-snapshot-v1-execution-audit/evidence/audit-after.json` - final evidence.
- `_condamad/stories/CS-298-replay-snapshot-v1-execution-audit/evidence/validation.txt` - validation evidence.

Likely tests:

- `backend/tests/unit/test_replay_snapshot_v1_execution_audit.py` - replay refusal, audit event and non-leakage unit coverage.
- `backend/tests/api/admin/test_replay_snapshot_v1_api.py` - TestClient coverage for admin read, replay and purge audit behavior.
- `backend/tests/architecture/test_replay_snapshot_v1_execution_boundary.py` - AST guard for bounded replay ownership.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no persistence schema is created.
- `backend/app/api/v1/routers/public/**` - out of scope; no public route is added.
- `backend/app/domain/llm/prompting/**` - out of scope; prompt definitions are unchanged.
- `backend/app/infra/db/models/**` - out of scope; CS-295 owns replay snapshot persistence schema.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `pytest -q tests/unit/test_replay_snapshot_v1_execution_audit.py`
- VC2: `pytest -q tests/api/admin/test_replay_snapshot_v1_api.py`
- VC3: `pytest -q tests/architecture/test_replay_snapshot_v1_execution_boundary.py`
- VC4: `$env:PYTHONPATH='backend'; python -c "from app.main import app; assert all('/admin/' in p for p in app.openapi()['paths'] if 'replay_snapshot_v1' in p)"`
- VC5: `$env:PYTHONPATH='backend'; python -c "from app.main import app; assert not any(getattr(r,'path','') == '/replay_snapshot_v1' for r in app.routes)"`
- VC6: `rg -n "raw_prompt|birth_date|birth_time|birth_place|latitude|longitude|email|password|api_key|payload_enc" app tests`
- VC7: `rg -n "deterministic|non-deterministic|replay_snapshot_v1" app tests`
- VC8: `python -B -c "from pathlib import Path; assert Path('../_condamad/stories/CS-298-replay-snapshot-v1-execution-audit/evidence/audit-after.json').exists()"`
- VC9: `python -B -c "from pathlib import Path; assert Path('../_condamad/stories/CS-298-replay-snapshot-v1-execution-audit/evidence/validation.txt').exists()"`
- VC10: `ruff format .`
- VC11: `ruff check .`
- VC12: `python -B -m pytest -q tests\unit tests\integration tests\api\admin --tb=short`
- VC13: `pytest -q`

## Regression Risks

- Replay execution could become an unrestricted LLM execution path from admin routes.
- Audit events could contain prompt text, birth details, secrets, encrypted bytes or raw provider output.
- Expired, purged or incomplete snapshots could reach provider execution before refusal.
- Reproducibility notes could overstate determinism for provider behavior.
- Purge or read flows could skip audit recording while replay attempts are covered.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the backend virtual environment before all Python commands.
- Run validation commands from `backend` only after activation, matching the repository PowerShell workflow.
- Keep audit detail fields bounded and reject raw source material at the DTO or service boundary.
- Persist final validation output under the CS-298 evidence folder before requesting review.

## References

- `_story_briefs/cs-298-implement-replay-snapshot-v1-execution-audit.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `backend/app/services/llm_observability/**`
- `backend/app/ops/llm/replay_service.py`
- `backend/app/domain/llm/runtime/**`
- `backend/app/services/ops/audit_service.py`
- `backend/app/domain/audit/safe_details.py`
- `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/00-story.md`
- `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/00-story.md`
- `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/00-story.md`
- `_condamad/stories/regression-guardrails.md`
