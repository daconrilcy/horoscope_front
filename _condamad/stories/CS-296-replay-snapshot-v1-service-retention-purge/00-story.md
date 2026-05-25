# Story CS-296 replay-snapshot-v1-service-retention-purge: Implement replay_snapshot_v1 Service Retention And Purge
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-296-implement-replay-snapshot-v1-service-retention-purge.md`.
- Required dependency: CS-295 replay snapshot storage and redaction is expected before implementation.
- Existing owner found: `LlmReplaySnapshotModel` owns table `llm_replay_snapshots`.
- Existing owner found: `backend/app/domain/llm/runtime/observability_service.py` currently creates and purges replay rows.
- Existing owner found: `backend/app/ops/llm/replay_service.py` currently reads encrypted replay snapshots for replay execution.
- Existing owner found: `backend/app/services/ops/audit_service.py` records bounded audit events.
- Existing owner found: `backend/app/domain/audit/safe_details.py` owns safe audit detail DTOs.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: replay snapshot lifecycle logic must move behind one internal service for creation, metadata reads and purge decisions.
- Source-alignment evidence: PASS; service centralization, expiry blocking, purge safety, audit hooks and no API route are covered.

## Objective

Implement one internal `replay_snapshot_v1` service that centralizes snapshot creation, controlled metadata reads, automatic purge and manual purge.

The service must enforce 30-day retention, return explicit business outcomes, prepare safe audit hooks, and keep diagnostics plus
`narrative_answer_audit_v1` records unchanged.

## Target State

- `ReplaySnapshotV1Service` or the existing canonical service is the only application service for replay snapshot lifecycle behavior.
- `create_snapshot` creates replay snapshots through the CS-295 storage owner with `expires_at = created_at + 30 days`.
- `get_snapshot_metadata` returns controlled metadata and refuses expired or purged snapshots.
- `purge_expired` purges all expired replay snapshots through one service method and returns deterministic counts.
- `purge_snapshot` applies the approved tombstone or delete policy for one replay snapshot and returns a controlled result.
- Business results distinguish `success`, `not_found`, `expired`, `already_purged` and validation failure states without route-level logic.
- Safe audit payloads are prepared through `AuditService` and `safe_details` without adding admin endpoints.
- No public route, frontend surface, generated client or public OpenAPI exposure is added.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-296-implement-replay-snapshot-v1-service-retention-purge.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-296`.
- Evidence 3: `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/00-story.md` - storage dependency inspected.
- Evidence 4: `backend/app/domain/llm/runtime/observability_service.py` - existing snapshot creation and expiry purge owner found.
- Evidence 5: `backend/app/ops/llm/replay_service.py` - existing snapshot read owner found.
- Evidence 6: `backend/app/services/ops/audit_service.py` - audit event service inspected.
- Evidence 7: `backend/app/domain/audit/safe_details.py` - safe audit detail owner inspected.
- Evidence 8: `resolve_guardrails.py` - scoped resolver run for backend service, retention, purge, audit and no-public-API scope.
- Repository structure alert: backend, backend/app, backend/tests, frontend and frontend/src exist in this workspace.
- Source-alignment evidence: PASS; no brief criterion was dropped, softened or replaced by generic LLM observability work.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Internal replay snapshot lifecycle service for `replay_snapshot_v1`.
  - `create_snapshot`, `get_snapshot_metadata`, `purge_expired` and `purge_snapshot` service methods.
  - 30-day retention enforcement and expired snapshot non-usability.
  - Controlled business results for success, missing, expired and already-purged states.
  - Safe audit hook preparation for manual and automatic purge actions.
  - Unit and integration tests for lifecycle, retention, purge policy and non-cascade safety.
- Out of scope:
  - Frontend UI, public/client routes, admin endpoints, generated clients, styling, i18n, build tooling and public OpenAPI exposure.
  - Replay execution redesign, scheduled global jobs, role taxonomy redesign, diagnostics redesign and unrelated LLM observability cleanup.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No admin endpoint, replay execution feature, scheduled global job, UI, generated client or public OpenAPI path.
  - No deletion of diagnostics, `narrative_answer_audit_v1`, call logs, prompt snapshots or unrelated LLM release snapshots.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits backend service lifecycle, retention and purge orchestration.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only one canonical internal service surface for `replay_snapshot_v1` lifecycle behavior.
  - Keep storage ownership on CS-295 replay snapshot persistence owners.
  - Keep public routes, public OpenAPI, frontend, generated clients and unrelated LLM observability behavior unchanged.
  - Keep purge operations bounded to replay snapshot payload references and replay snapshot state.
  - Keep audit data bounded through `AuditService` and safe audit detail DTOs.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: CS-295 did not approve tombstone versus physical delete policy for manual purge.
- Additional validation rules:
  - The implementation must prove one service owns lifecycle decisions for create, metadata read and purge.
  - The implementation must prove snapshots older than 30 days cannot be used through `get_snapshot_metadata`.
  - The implementation must prove manual purge returns `success`, `not_found`, `expired` or `already_purged`.
  - The implementation must prove automatic purge affects only expired replay snapshots and their payload references.
  - The implementation must prove diagnostics and `narrative_answer_audit_v1` records are unchanged by purge operations.
  - Runtime evidence must include `pytest`, DB schema inspection, `AST guard`, `app.routes` and `app.openapi()`.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, DB schema inspection, `AST guard`, `app.routes` and `app.openapi()` prove lifecycle behavior. |
| Baseline Snapshot | yes | Before and after artifacts prove the only allowed surface delta is the internal service and tests. |
| Ownership Routing | yes | Creation, metadata read, purge and audit hook ownership must not be duplicated. |
| Allowlist Exception | no | No broad allowlist handling is authorized for this lifecycle service slice. |
| Contract Shape | yes | Service method inputs, outputs, retention states and purge outcomes are exact. |
| Batch Migration | no | CS-296 does not authorize schema migration work beyond using CS-295 storage. |
| Reintroduction Guard | yes | Public exposure, parallel services and unsafe cascade deletes must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | One lifecycle service owns decisions. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/unit/test_replay_snapshot_v1_service_ownership.py` |
| AC2 | `create_snapshot` applies 30-day retention. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_replay_snapshot_v1_service_retention.py`. |
| AC3 | Expired snapshots are unusable. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_replay_snapshot_v1_service_metadata.py`. |
| AC4 | Metadata reads return controlled states. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_replay_snapshot_v1_service_metadata.py`. |
| AC5 | Automatic purge affects expired rows only. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_replay_snapshot_v1_service_purge.py` |
| AC6 | Manual purge returns controlled outcomes. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_replay_snapshot_v1_service_manual_purge.py`. |
| AC7 | Related audit rows remain unchanged. | Evidence profile: baseline_before_after_diff; `pytest -q backend/tests/integration/test_replay_snapshot_v1_service_non_cascade.py` |
| AC8 | Safe audit hook payloads are bounded. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_replay_snapshot_v1_service_audit.py`. |
| AC9 | Public API exposure is unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`. |
| AC10 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-296 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect the brief, CS-295, replay services, audit service, safe details and current replay snapshot model. (AC: AC1)
- [ ] Task 2: Add or extend the canonical `ReplaySnapshotV1Service` for all lifecycle decisions. (AC: AC1)
- [ ] Task 3: Implement `create_snapshot` with CS-295 storage owner reuse and 30-day `expires_at` calculation. (AC: AC2)
- [ ] Task 4: Implement `get_snapshot_metadata` with controlled metadata and expired snapshot refusal. (AC: AC3, AC4)
- [ ] Task 5: Implement `purge_expired` with deterministic counts and replay-only scope. (AC: AC5, AC7)
- [ ] Task 6: Implement `purge_snapshot` with approved tombstone or delete policy and controlled outcomes. (AC: AC6, AC7)
- [ ] Task 7: Add safe audit hook DTOs or service calls for manual and automatic purge outcomes. (AC: AC8)
- [ ] Task 8: Add runtime exposure guards proving no route or OpenAPI path was added. (AC: AC9)
- [ ] Task 9: Persist source, ownership, purge, audit and validation evidence under the CS-296 evidence folder. (AC: AC10)

## Files to Inspect First

- `_story_briefs/cs-296-implement-replay-snapshot-v1-service-retention-purge.md` - source brief.
- `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/00-story.md` - storage and redaction dependency.
- `backend/app/services/llm_observability/**` - existing observability service patterns.
- `backend/app/ops/llm/**` - existing LLM operations service patterns and replay reader.
- `backend/app/services/ops/audit_service.py` - audit event service.
- `backend/app/domain/audit/safe_details.py` - safe audit details DTO owner.
- `backend/app/domain/llm/runtime/observability_service.py` - current snapshot creation and purge behavior.
- `backend/app/infra/db/models/llm/llm_observability.py` - canonical replay snapshot model owner from CS-295.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `ReplaySnapshotV1Service` or the canonical existing service for lifecycle behavior.
  - `LlmReplaySnapshotModel` and migrated SQLAlchemy metadata for persisted replay snapshot state.
  - `AuditService` and safe audit details for purge audit payload preparation.
  - `pytest`, DB schema inspection, `AST guard`, `app.routes` and `app.openapi()` for final runtime evidence.
- Secondary evidence:
  - Targeted `rg` scans over backend replay service, observability service, audit service and tests.
  - Persisted evidence under `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/evidence`.
- Static scans alone are not sufficient because:
  - service ownership, retention math, purge effects and public API non-exposure must be proven from executable tests.

## Contract Shape

- Contract type:
  - Backend internal service lifecycle contract for `replay_snapshot_v1`.
- Service methods:
  - `create_snapshot`: creates one replay snapshot using CS-295 storage and returns a success result with snapshot metadata.
  - `get_snapshot_metadata`: returns controlled metadata or a controlled unavailable state.
  - `purge_expired`: purges expired replay snapshots and returns count plus audit-safe details.
  - `purge_snapshot`: purges one replay snapshot by identifier and returns a controlled result.
- Fields:
  - `snapshot_id`: replay snapshot identifier used for metadata and manual purge.
  - `created_at`: retention base timestamp.
  - `expires_at`: exact value derived as `created_at + 30 days`.
  - `purged_at`: populated only when tombstone policy is the CS-295 approved policy.
  - `status`: controlled business outcome for metadata and purge calls.
  - `audit_details`: bounded purge hook details approved by safe audit DTOs.
- Required fields:
  - `snapshot_id`
  - `created_at`
  - `expires_at`
  - `status`
- Optional fields:
  - `purged_at`
  - `audit_details`
- Required business outcomes:
  - `success`
  - `not_found`
  - `expired`
  - `already_purged`
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - service DTO names and persisted field names must match the canonical backend model and tests.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose a new `replay_snapshot_v1` public path.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-296-implement-replay-snapshot-v1-service-retention-purge.md`
  - `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/00-story.md`
  - `backend/app/domain/llm/runtime/observability_service.py`
  - `backend/app/ops/llm/replay_service.py`
  - `backend/app/services/ops/audit_service.py`
  - `backend/app/domain/audit/safe_details.py`
- Comparison after implementation:
  - `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/evidence/source-checklist.md`
  - `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/evidence/service-ownership.txt`
  - `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/evidence/purge-non-cascade.txt`
  - `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/evidence/validation.txt`
- Expected invariant:
  - The only intended delta is the internal replay snapshot lifecycle service, audit-safe purge hooks, tests and evidence.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Lifecycle orchestration | `backend/app/services/replay_snapshot_v1_service.py` or existing canonical service | Route handler or job-local logic |
| Snapshot persistence | `backend/app/infra/db/models/llm/llm_observability.py` | Second replay snapshot table |
| Snapshot creation source | canonical replay snapshot service | `backend/app/domain/llm/runtime/observability_service.py` direct business branching |
| Snapshot metadata read | canonical replay snapshot service | `backend/app/ops/llm/replay_service.py` ad hoc status checks |
| Purge policy | canonical replay snapshot service | scheduled job-only purge implementation |
| Audit event write | `backend/app/services/ops/audit_service.py` | Raw audit payload dump |
| Safe audit details | `backend/app/domain/audit/safe_details.py` | Inline unbounded dictionaries |

## Mandatory Reuse / DRY Constraints

- Reuse CS-295 `LlmReplaySnapshotModel` and `llm_replay_snapshots` as the canonical persistence owner.
- Reuse existing replay payload reference and encrypted payload boundaries rather than adding a second payload store.
- Reuse `AuditService.record_event` and safe audit detail DTO patterns for purge hooks.
- Reuse existing datetime provider patterns for deterministic retention tests.
- Reuse existing SQLAlchemy session and repository patterns in the current backend service layer.
- Do not duplicate snapshot schema, sanitizer logic, purge logic, audit writing, role taxonomy or replay execution logic.

## No Legacy / Forbidden Paths

- No legacy replay lifecycle service may be added for `replay_snapshot_v1`.
- No compatibility replay lifecycle service may be added for `replay_snapshot_v1`.
- No fallback replay lifecycle service may be added for `replay_snapshot_v1`.
- No second replay snapshot table, duplicate model, duplicate writer or manual DB mutation script is authorized.
- No public route, frontend route, generated client or public OpenAPI path may expose `replay_snapshot_v1`.
- No route handler, scheduled job or replay execution function may own lifecycle decisions outside the canonical service.
- No purge action may delete diagnostics, `narrative_answer_audit_v1`, call logs, prompt snapshots or LLM release snapshots.

## Reintroduction Guard

- Forbidden runtime surfaces:
  - Public `replay_snapshot_v1` path in `app.routes` or `app.openapi()`.
  - Duplicate replay snapshot lifecycle service or second replay snapshot table.
  - Metadata read path that returns expired or purged snapshots as usable.
  - Purge path that cascades into diagnostics, `narrative_answer_audit_v1`, call logs or LLM release snapshots.
- Required deterministic guards:
  - `pytest -q backend/tests/unit/test_replay_snapshot_v1_service_ownership.py`
  - `pytest -q backend/tests/unit/test_replay_snapshot_v1_service_retention.py`
  - `pytest -q backend/tests/unit/test_replay_snapshot_v1_service_metadata.py`
  - `pytest -q backend/tests/unit/test_replay_snapshot_v1_service_manual_purge.py`
  - `pytest -q backend/tests/unit/test_replay_snapshot_v1_service_audit.py`
  - `pytest -q backend/tests/integration/test_replay_snapshot_v1_service_purge.py`
  - `pytest -q backend/tests/integration/test_replay_snapshot_v1_service_non_cascade.py`
  - `python -c "from app.main import app; assert 'replay_snapshot_v1' not in str(app.openapi())"`
  - `python -c "from app.main import app; assert 'replay_snapshot_v1' not in {getattr(r, 'path', '') for r in app.routes}"`
  - `rg -n "ReplaySnapshotV1Service|purge_snapshot|purge_expired|get_snapshot_metadata" backend/app backend/tests`

## Regression Guardrails

| Guardrail | Applies because | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend route surfaces must not gain public replay exposure. | `python` checks `app.routes`; `app.openapi()`. |
| RG-003 `architecture-routes-api-v1` | Backend API routing remains out of scope for this service story. | scoped `git status`; runtime route guard. |
| RG-007 `admin-llm-observability` | LLM observability access must stay behind backend service ownership. | targeted `pytest`; scoped `rg`. |
| RG-022 `prompt-generation-validation-plans` | Backend LLM service tests and validation plans are in scope. | targeted `pytest`; validation output. |
| RG-047 `CS-029-encadrer-styles-inline-statiques-frontend` | Non-applicable example: frontend UI is out of scope. | `git status --short -- frontend/src`. |
| RG-052 `CS-075-converger-namespaces-css-migration-only-restants` | Non-applicable example: frontend CSS is out of scope. | `git status --short -- frontend/src`. |
| Registry gap `replay_snapshot_v1-service-retention-purge` | No exact replay snapshot service guardrail was resolved. | `resolve_guardrails.py` scoped output. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Source checklist | `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/evidence/source-checklist.md` | Prove source and owners were inspected. |
| Service ownership | `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/evidence/service-ownership.txt` | Prove single service ownership. |
| Purge non-cascade | `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/evidence/purge-non-cascade.txt` | Prove unrelated rows remain. |
| Runtime status | `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/evidence/runtime-surface-status.txt` | Prove route exposure. |
| Validation output | `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/evidence/validation.txt` | Keep lint, tests and scans output. |
| Review output | `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this lifecycle service slice.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/services/replay_snapshot_v1_service.py` - canonical lifecycle service, unless an existing canonical service is extended.
- `backend/app/domain/llm/runtime/observability_service.py` - delegate replay snapshot creation and expiry purge to the canonical service.
- `backend/app/ops/llm/replay_service.py` - delegate metadata availability checks to the canonical service.
- `backend/app/domain/audit/safe_details.py` - add bounded replay snapshot purge audit details.
- `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/evidence/source-checklist.md` - persisted source evidence.
- `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/evidence/service-ownership.txt` - ownership evidence.
- `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/evidence/purge-non-cascade.txt` - purge safety evidence.
- `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/evidence/runtime-surface-status.txt` - runtime exposure evidence.
- `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/evidence/validation.txt` - validation evidence.

Likely tests:

- `backend/tests/unit/test_replay_snapshot_v1_service_ownership.py` - single service and no parallel lifecycle logic.
- `backend/tests/unit/test_replay_snapshot_v1_service_retention.py` - creation and 30-day retention behavior.
- `backend/tests/unit/test_replay_snapshot_v1_service_metadata.py` - metadata read states and expired refusal.
- `backend/tests/unit/test_replay_snapshot_v1_service_manual_purge.py` - manual purge outcomes.
- `backend/tests/unit/test_replay_snapshot_v1_service_audit.py` - audit-safe purge hook payloads.
- `backend/tests/integration/test_replay_snapshot_v1_service_purge.py` - automatic purge against persisted rows.
- `backend/tests/integration/test_replay_snapshot_v1_service_non_cascade.py` - diagnostics and narrative audit rows remain unchanged.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no route is added.
- `backend/migrations/versions/**` - out of scope unless CS-295 storage contract is incomplete.
- `backend/app/domain/astrology/runtime/**` - out of scope; no astrology runtime is touched.
- `docs/architecture/replay-snapshot-v1-storage-security-model.md` - source contract should remain stable.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `pytest -q backend/tests/unit/test_replay_snapshot_v1_service_ownership.py`
- VC2: `pytest -q backend/tests/unit/test_replay_snapshot_v1_service_retention.py`
- VC3: `pytest -q backend/tests/unit/test_replay_snapshot_v1_service_metadata.py`
- VC4: `pytest -q backend/tests/unit/test_replay_snapshot_v1_service_manual_purge.py`
- VC5: `pytest -q backend/tests/unit/test_replay_snapshot_v1_service_audit.py`
- VC6: `pytest -q backend/tests/integration/test_replay_snapshot_v1_service_purge.py`
- VC7: `pytest -q backend/tests/integration/test_replay_snapshot_v1_service_non_cascade.py`
- VC8: `python -c "from app.main import app; assert 'replay_snapshot_v1' not in str(app.openapi())"`
- VC9: `python -c "from app.main import app; assert 'replay_snapshot_v1' not in {getattr(r, 'path', '') for r in app.routes}"`
- VC10: `rg -n "ReplaySnapshotV1Service|create_snapshot|get_snapshot_metadata|purge_expired|purge_snapshot" backend/app backend/tests`
- VC11: `rg -n "narrative_answer_audit|admin_chart_diagnostics|llm_call_logs|llm_release_snapshots" backend/tests`
- VC12: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/evidence/validation.txt').exists()"`
- VC13: `ruff format .`
- VC14: `ruff check .`
- VC15: `python -B -m pytest -q tests\unit tests\integration --tb=short`
- VC16: `pytest -q`

## Regression Risks

- Lifecycle decisions could remain split across observability, replay and job code.
- Expired snapshots could remain usable through a metadata read or replay path.
- Manual purge could delete diagnostics, `narrative_answer_audit_v1`, call logs or release snapshots.
- Audit hook details could include unbounded or sensitive data.
- Public API or frontend exposure could appear before product approval.
- A scheduled job could duplicate service logic instead of calling the canonical service.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the backend virtual environment before any Python command.
- Reuse the existing replay snapshot DB owner before adding any model, table or service.
- Keep documentation comments and public docstrings in French for new or significantly modified applicative files.
- Keep frontend, public API, generated client, route, migration and broad LLM observability surfaces unchanged.

## References

- `_story_briefs/cs-296-implement-replay-snapshot-v1-service-retention-purge.md`
- `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/00-story.md`
- `backend/app/services/llm_observability/**`
- `backend/app/ops/llm/**`
- `backend/app/services/ops/audit_service.py`
- `backend/app/domain/audit/safe_details.py`
- `backend/app/domain/llm/runtime/observability_service.py`
- `backend/app/infra/db/models/llm/llm_observability.py`
- `_condamad/stories/regression-guardrails.md`
