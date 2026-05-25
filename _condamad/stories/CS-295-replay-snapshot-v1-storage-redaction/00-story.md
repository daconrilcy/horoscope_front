# Story CS-295 replay-snapshot-v1-storage-redaction: Implement replay_snapshot_v1 Storage And Redaction
Status: done

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-295-implement-replay-snapshot-v1-storage-redaction.md`.
- Required dependency: CS-277 storage and security model is `done`.
- Required dependency: CS-278 replay implementation gate is `ready-to-dev` after approval `DPO-REPLAY-SNAPSHOT-V1-RETENTION-001`.
- Existing owner found: `LlmReplaySnapshotModel` owns table `llm_replay_snapshots`.
- Existing owner found: `log_call` creates replay snapshots from sanitized-hash observability input flow.
- Existing owner found: `purge_expired_logs` already deletes expired replay snapshot rows.
- Existing owner found: `backend/app/core/sensitive_data.py` owns replay sink classification and sanitization.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: replay snapshots need approved internal storage fields, redaction proof and 30-day retention on the existing owner.
- Source-alignment evidence: PASS; owner reuse, 30-day retention, DB safety scans, redaction and no public exposure are covered.

## Objective

Implement approved internal persistence for `replay_snapshot_v1` by extending the existing replay snapshot storage owner.

The implementation must persist only approved references, hashes, versions and metadata, enforce `expires_at = created_at + 30 days`,
prove redaction against forbidden raw sensitive fields, and avoid any parallel replay storage.

## Target State

- `llm_replay_snapshots` remains the canonical persistence owner for replay snapshot storage.
- The replay snapshot schema supports `replay_snapshot_v1` metadata without raw prompts, raw birth data, exact coordinates, direct identifiers or secrets.
- `expires_at` is deterministically derived from `created_at + 30 days`.
- Any isolated encrypted payload reference stays bounded to the existing encrypted replay payload boundary.
- Redaction and schema tests prove only references, hashes, versions and approved metadata are stored.
- A migration updates the persisted schema when the SQLAlchemy model and current table differ.
- Existing purge behavior removes expired replay snapshots without cascading into unrelated diagnostics or AI audit records.
- No public route, frontend surface, generated client or public OpenAPI exposure is added.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-295-implement-replay-snapshot-v1-storage-redaction.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-295`.
- Evidence 3: `backend/app/infra/db/models/llm/llm_observability.py` - existing `LlmReplaySnapshotModel` owner found.
- Evidence 4: `backend/migrations/versions/51bdec8ae9a5_add_llm_observability_tables.py` - existing table migration found.
- Evidence 5: `backend/app/domain/llm/runtime/observability_service.py` - existing snapshot creation and purge owner found.
- Evidence 6: `backend/app/ops/llm/replay_service.py` - existing encrypted replay read owner found.
- Evidence 7: `backend/app/core/sensitive_data.py` - replay sink and sensitive field classifications found.
- Evidence 8: `backend/app/domain/audit/safe_details.py` - safe replay audit details owner found.
- Evidence 9: `docs/architecture/replay-snapshot-v1-storage-security-model.md` - approved storage and security model inspected.
- Evidence 10: `resolve_guardrails.py` - scoped resolver run for backend-domain storage, redaction, retention and no-public-API scope.
- Repository structure alert: backend, backend/app, backend/tests, backend/migrations, docs, frontend and frontend/src exist in this workspace.
- Source-alignment evidence: PASS; no brief criterion was dropped, softened or replaced by generic observability work.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Existing `llm_replay_snapshots` schema, SQLAlchemy model and creation path for `replay_snapshot_v1`.
  - Retention enforcement with `expires_at = created_at + 30 days`.
  - Redaction and rejection of raw prompts, raw birth data, exact coordinates, direct identifiers and secrets.
  - Alembic migration for replay snapshot schema changes.
  - Unit and integration tests for schema, redaction, retention, owner reuse, purge and DB scans.
- Out of scope:
  - Frontend UI, public/client routes, generated clients, styling, i18n, build tooling and public OpenAPI exposure.
  - Replay execution redesign, role taxonomy redesign, broad diagnostics redesign and unrelated LLM observability cleanup.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No second replay table, parallel storage service, public route, frontend route, generated client or public OpenAPI path.
  - No storage of raw prompts, raw birth data, exact coordinates, direct identifiers, provider secrets or API credentials.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits backend DB storage, redaction, retention and migration work.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Extend the existing `LlmReplaySnapshotModel` and its creation path rather than creating a second replay store.
  - Add only approved `replay_snapshot_v1` references, hashes, versions, metadata, retention and purge behavior.
  - Keep public routes, public OpenAPI, frontend, generated clients, role taxonomy and unrelated LLM observability behavior unchanged.
  - Keep forbidden raw sensitive data out of persisted replay snapshot rows.
  - Preserve the existing encrypted isolated payload boundary rather than adding a separate payload store.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: approved storage fields cannot be mapped onto the existing replay snapshot owner.
- Additional validation rules:
  - The implementation must prove `llm_replay_snapshots` is the single canonical replay snapshot table.
  - The implementation must prove `expires_at` equals `created_at + 30 days` for new replay snapshots.
  - The implementation must prove persisted fields contain only approved references, hashes, versions and metadata.
  - The implementation must prove raw prompts, raw birth data, exact coordinates, direct identifiers and secrets are not persisted.
  - The implementation must use Alembic for schema changes and keep SQLAlchemy model metadata aligned.
  - The implementation must prove purge deletes expired replay snapshots without deleting unrelated diagnostics or AI audit rows.
  - Runtime evidence must include `pytest`, DB schema inspection, `AST guard`, `app.routes` and `app.openapi()`.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, DB schema inspection, `app.routes` and `app.openapi()` prove runtime storage and exposure. |
| Baseline Snapshot | yes | Before and after artifacts prove the only allowed surface delta is approved storage and tests. |
| Ownership Routing | yes | Existing replay, DB, redaction, audit and purge owners must not be duplicated. |
| Allowlist Exception | no | No broad allowlist handling is authorized for this approved storage slice. |
| Contract Shape | yes | Snapshot fields, retention, redaction and encrypted payload reference shape are exact. |
| Batch Migration | yes | Alembic schema work must be planned and validated against current DB metadata. |
| Reintroduction Guard | yes | Parallel stores, raw sensitive data and public exposure must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | One canonical snapshot owner exists. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/unit/test_replay_snapshot_v1_ownership.py`. |
| AC2 | Replay snapshot schema stores approved fields. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_replay_snapshot_v1_storage.py`. |
| AC3 | Retention is exactly 30 days. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_replay_snapshot_v1_retention.py`. |
| AC4 | Forbidden raw fields are not persisted. | Evidence profile: targeted_forbidden_symbol_scan; `pytest -q backend/tests/unit/test_replay_snapshot_v1_redaction.py`. |
| AC5 | DB scan excludes raw data. | Evidence profile: targeted_forbidden_symbol_scan; `pytest -q backend/tests/integration/test_replay_snapshot_v1_db_redaction.py`. |
| AC6 | Migration matches model metadata. | Evidence profile: baseline_before_after_diff; `pytest -q backend/tests/integration/test_llm_db_invariants.py`. |
| AC7 | Expired snapshots are purged safely. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_replay_snapshot_v1_purge.py`. |
| AC8 | Public API exposure is unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`. |
| AC9 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-295 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect the brief, CS-277, CS-278, DPO approval, model, migration, services and redaction owners. (AC: AC1, AC2)
- [ ] Task 2: Extend `LlmReplaySnapshotModel` as the single owner for approved `replay_snapshot_v1` fields. (AC: AC1, AC2)
- [ ] Task 3: Add an Alembic migration for schema fields that are missing from the current table. (AC: AC2, AC6)
- [ ] Task 4: Enforce `created_at` and `expires_at = created_at + 30 days` for new snapshots. (AC: AC3)
- [ ] Task 5: Reuse `sensitive_data.py` policy to redact or reject raw prompts, birth data, coordinates, identifiers and secrets. (AC: AC4)
- [ ] Task 6: Add DB redaction scans over persisted snapshot rows and encrypted payload reference metadata. (AC: AC5)
- [ ] Task 7: Preserve purge behavior for expired snapshots without touching unrelated diagnostics or AI audit records. (AC: AC7)
- [ ] Task 8: Add runtime exposure guards proving no new public route or OpenAPI path is exposed. (AC: AC8)
- [ ] Task 9: Persist source, schema, redaction and validation evidence under the CS-295 evidence folder. (AC: AC9)

## Files to Inspect First

- `_story_briefs/cs-295-implement-replay-snapshot-v1-storage-redaction.md` - source brief.
- `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/00-story.md` - approved storage model.
- `_condamad/stories/CS-278-replay-snapshot-v1-implementation/00-story.md` - replay implementation gate and owner reuse.
- `docs/architecture/replay-snapshot-v1-storage-security-model.md` - approved fields, forbidden data and retention.
- `docs/architecture/replay-snapshot-v1-dpo-security-approval-request.md` - DPO/security approval.
- `backend/app/infra/db/models/llm/llm_observability.py` - canonical replay snapshot model owner.
- `backend/migrations/versions/51bdec8ae9a5_add_llm_observability_tables.py` - current replay snapshot table migration.
- `backend/app/domain/llm/runtime/observability_service.py` - snapshot creation, hashing and purge owner.
- `backend/app/ops/llm/replay_service.py` - encrypted snapshot read owner.
- `backend/app/core/sensitive_data.py` - sensitive replay classification and sanitization owner.
- `backend/app/domain/audit/safe_details.py` - safe replay audit details owner.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `LlmReplaySnapshotModel` and SQLAlchemy metadata for the canonical replay snapshot schema.
  - Alembic head migration and migrated SQLite test database for persisted schema.
  - `log_call`, `compute_input_hash`, `sanitize_payload` and `purge_expired_logs` for runtime storage behavior.
  - `pytest`, DB schema inspection, `AST guard`, `app.routes` and `app.openapi()` for final runtime evidence.
- Secondary evidence:
  - Targeted `rg` scans over backend replay, redaction, migration and tests.
  - Persisted evidence under `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/evidence`.
- Static scans alone are not sufficient because:
  - persisted schema, retention math, purge behavior and runtime API exposure must be proven from executable tests.

## Contract Shape

- Contract type:
  - Backend DB persistence and redaction contract for `replay_snapshot_v1`.
- Fields:
  - `snapshot_type`: exact value `replay_snapshot_v1`.
  - `call_log_id`: existing link to the owning LLM call log.
  - `created_at`: creation timestamp used as retention base.
  - `expires_at`: exact value derived as `created_at + 30 days`.
  - `input_ref`: approved reconstruction reference or encrypted isolated payload reference.
  - `input_hash`: approved hash used for integrity and correlation.
  - `version_identity`: graph, projection, prompt template or model version labels.
  - `provenance`: trace, correlation, diagnostics and AI audit references.
  - `redaction_state`: exact status proving forbidden data was removed or rejected.
  - `payload_enc`: encrypted isolated payload bytes only inside the approved existing boundary.
- Required fields:
  - `snapshot_type`
  - `call_log_id`
  - `created_at`
  - `expires_at`
  - `input_ref`
  - `input_hash`
  - `version_identity`
  - `provenance`
  - `redaction_state`
- Optional fields:
  - `payload_enc`
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - DB and service field names must match the approved storage model and tests.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose a new `replay_snapshot_v1` public path.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-295-implement-replay-snapshot-v1-storage-redaction.md`
  - `backend/app/infra/db/models/llm/llm_observability.py`
  - `backend/migrations/versions/51bdec8ae9a5_add_llm_observability_tables.py`
  - `backend/app/domain/llm/runtime/observability_service.py`
  - `backend/app/core/sensitive_data.py`
- Comparison after implementation:
  - `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/evidence/source-checklist.md`
  - `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/evidence/db-schema-status.txt`
  - `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/evidence/redaction-scan.txt`
  - `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/evidence/validation.txt`
- Expected invariant:
  - The only intended delta is approved backend replay snapshot storage, redaction, retention, migration, tests and evidence.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Snapshot DB model | `backend/app/infra/db/models/llm/llm_observability.py` | New replay DB model tree |
| Snapshot table | `llm_replay_snapshots` | Second replay snapshot table |
| Snapshot creation | `backend/app/domain/llm/runtime/observability_service.py` | Parallel snapshot writer |
| Snapshot read | `backend/app/ops/llm/replay_service.py` | Public route handler |
| Sensitive-data policy | `backend/app/core/sensitive_data.py` | Local ad hoc sanitizer |
| Safe audit details | `backend/app/domain/audit/safe_details.py` | Raw audit payload dump |
| Schema migration | `backend/migrations/versions/**` | Manual DB mutation script |

## Mandatory Reuse / DRY Constraints

- Reuse `LlmReplaySnapshotModel` and `llm_replay_snapshots` as the canonical persistence owner.
- Reuse the existing encrypted replay payload boundary instead of adding a second payload store.
- Reuse `compute_input_hash`, `sanitize_payload` and `Sink.LLM_REPLAY_SNAPSHOTS` for redaction and integrity.
- Reuse `purge_expired_logs` or the approved purge owner for expiry deletion.
- Reuse CS-277 and the DPO approval document for allowed fields, forbidden data and retention.
- Do not duplicate snapshot schema, sanitizer logic, purge logic, role taxonomy or replay ownership.

## No Legacy / Forbidden Paths

- No legacy replay storage path may be added for `replay_snapshot_v1`.
- No compatibility replay storage path may be added for `replay_snapshot_v1`.
- No fallback replay storage path may be added for `replay_snapshot_v1`.
- No second replay snapshot table, duplicate model, duplicate writer or manual DB mutation script is authorized.
- No public route, frontend route, generated client or public OpenAPI path may expose `replay_snapshot_v1`.
- No raw prompt, raw birth data, exact coordinate, direct identifier, secret, API key, token or credential may be persisted.
- No retention bypass or purge bypass is authorized.

## Reintroduction Guard

- Forbidden runtime surfaces:
  - Public `replay_snapshot_v1` path in `app.routes` or `app.openapi()`.
  - Duplicate replay snapshot model or table outside `llm_replay_snapshots`.
  - Snapshot persistence containing raw prompts, raw birth data, exact coordinates, direct identifiers or secrets.
  - Retention value other than 30 days for new `replay_snapshot_v1` rows.
- Required deterministic guards:
  - `pytest -q backend/tests/unit/test_replay_snapshot_v1_ownership.py`
  - `pytest -q backend/tests/unit/test_replay_snapshot_v1_redaction.py`
  - `pytest -q backend/tests/unit/test_replay_snapshot_v1_retention.py`
  - `pytest -q backend/tests/integration/test_replay_snapshot_v1_db_redaction.py`
  - `python -c "from app.main import app; assert 'replay_snapshot_v1' not in str(app.openapi())"`
  - `python -c "from app.main import app; assert 'replay_snapshot_v1' not in {getattr(r, 'path', '') for r in app.routes}"`
  - `rg -n "raw_prompt|birth_date|birth_time|birth_place|latitude|longitude|email|password|api_key" backend/app backend/tests`

## Regression Guardrails

| Guardrail | Applies because | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | API route surfaces must not gain public replay exposure. | `python` checks `app.routes`; `app.openapi()`. |
| RG-003 `architecture-routes-api-v1` | Backend API routing remains out of scope for this storage story. | scoped `git status`; runtime route guard. |
| RG-007 `admin-llm-observability` | Existing LLM observability surfaces own replay storage access. | targeted `pytest`; scoped `rg`. |
| RG-022 `prompt-generation-validation-plans` | Backend LLM storage tests and validation plans are in scope. | targeted `pytest`; validation output. |
| RG-047 `CS-029-encadrer-styles-inline-statiques-frontend` | Non-applicable example: frontend UI is out of scope. | `git status --short -- frontend/src`. |
| RG-052 `CS-075-converger-namespaces-css-migration-only-restants` | Non-applicable example: frontend CSS is out of scope. | `git status --short -- frontend/src`. |
| Registry gap `replay_snapshot_v1-storage` | No exact replay snapshot storage guardrail was resolved. | `resolve_guardrails.py` scoped output. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Source checklist | `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/evidence/source-checklist.md` | Prove source and owners were inspected. |
| Schema status | `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/evidence/db-schema-status.txt` | Prove DB schema alignment. |
| Redaction scan | `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/evidence/redaction-scan.txt` | Prove forbidden DB data is absent. |
| Runtime status | `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/evidence/runtime-surface-status.txt` | Prove route and OpenAPI exposure. |
| Validation output | `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/evidence/validation.txt` | Keep lint, tests and scans output. |
| Review output | `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this approved storage slice.

## Batch Migration Plan

- Batch migration plan: active

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| B1 | `llm_replay_snapshots` 7-day table | Same table with approved v1 fields | writer and reader services | storage and DB tests | no second store | unsafe backfill |

- Imports or contracts changed:
  - SQLAlchemy model metadata, Alembic migration contract and replay snapshot service contract.
- Scope:
  - Compare current `llm_replay_snapshots` columns with the final SQLAlchemy model metadata.
  - Add one Alembic migration for missing approved fields.
  - Keep existing rows compatible through nullable or deterministic backfill-safe fields only.
  - Do not create a second table, manual mutation script or data copy pipeline.
- Mapping:
  - Existing `input_enc` remains inside the approved encrypted isolated payload boundary.
  - Existing `expires_at` is changed to 30-day retention for new rows.
  - New metadata fields map only to approved references, hashes, versions and redaction state.
- Validation:
  - `pytest -q backend/tests/integration/test_llm_db_invariants.py`
  - `pytest -q backend/tests/integration/test_replay_snapshot_v1_db_redaction.py`

## Expected Files to Modify

Likely files:

- `backend/app/infra/db/models/llm/llm_observability.py` - canonical replay snapshot model owner.
- `backend/app/domain/llm/runtime/observability_service.py` - snapshot creation, redaction and retention behavior.
- `backend/app/ops/llm/replay_service.py` - encrypted snapshot read boundary.
- `backend/app/core/sensitive_data.py` - replay sink field classification and sanitizer policy.
- `backend/app/domain/audit/safe_details.py` - safe replay audit details shape.
- `backend/migrations/versions/20260525_replay_snapshot_v1_storage_redaction.py` - schema migration.
- `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/evidence/source-checklist.md` - persisted source evidence.
- `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/evidence/db-schema-status.txt` - schema evidence.
- `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/evidence/redaction-scan.txt` - redaction scan evidence.
- `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/evidence/runtime-surface-status.txt` - runtime exposure evidence.
- `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/evidence/validation.txt` - validation evidence.

Likely tests:

- `backend/tests/unit/test_replay_snapshot_v1_ownership.py` - single owner and no parallel store.
- `backend/tests/unit/test_replay_snapshot_v1_storage.py` - approved schema and metadata shape.
- `backend/tests/unit/test_replay_snapshot_v1_redaction.py` - forbidden sensitive data redaction.
- `backend/tests/unit/test_replay_snapshot_v1_retention.py` - 30-day retention behavior.
- `backend/tests/unit/test_replay_snapshot_v1_purge.py` - safe purge behavior.
- `backend/tests/integration/test_replay_snapshot_v1_db_redaction.py` - persisted DB scan for forbidden data.
- `backend/tests/integration/test_llm_db_invariants.py` - migrated schema and model alignment.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no route is added.
- `backend/app/api/v1/routers/public/**` - out of scope; no public route is added.
- `backend/app/domain/astrology/runtime/**` - out of scope; no astrology runtime is touched.
- `docs/architecture/replay-snapshot-v1-storage-security-model.md` - source contract should remain stable.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `pytest -q backend/tests/unit/test_replay_snapshot_v1_ownership.py`
- VC2: `pytest -q backend/tests/unit/test_replay_snapshot_v1_storage.py`
- VC3: `pytest -q backend/tests/unit/test_replay_snapshot_v1_redaction.py`
- VC4: `pytest -q backend/tests/unit/test_replay_snapshot_v1_retention.py`
- VC5: `pytest -q backend/tests/unit/test_replay_snapshot_v1_purge.py`
- VC6: `pytest -q backend/tests/integration/test_replay_snapshot_v1_db_redaction.py`
- VC7: `pytest -q backend/tests/integration/test_llm_db_invariants.py`
- VC8: `python -c "from app.main import app; assert 'replay_snapshot_v1' not in str(app.openapi())"`
- VC9: `python -c "from app.main import app; assert 'replay_snapshot_v1' not in {getattr(r, 'path', '') for r in app.routes}"`
- VC10: `rg -n "class LlmReplaySnapshotModel|__tablename__ = \"llm_replay_snapshots\"" backend/app/infra/db/models/llm`
- VC11: `rg -n "raw_prompt|birth_date|birth_time|birth_place|latitude|longitude|email|password|api_key" backend/app backend/tests`
- VC12: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/evidence/validation.txt').exists()"`
- VC13: `ruff format .`
- VC14: `ruff check .`
- VC15: `python -B -m pytest -q tests\unit\test_replay_snapshot_v1_storage_security_model.py tests\integration --tb=short`
- VC16: `pytest -q`

## Regression Risks

- A second replay snapshot store could diverge from `llm_replay_snapshots`.
- The 7-day retention default could remain active instead of the approved 30-day policy.
- Raw prompts, birth data, coordinates, identifiers or secrets could be persisted in plaintext columns or test fixtures.
- A migration could add storage fields without model metadata alignment.
- Purge behavior could delete unrelated diagnostics or AI audit records.
- Public API or frontend exposure could appear before product approval.

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
- Keep frontend, public API, generated client, role-taxonomy and broad LLM observability surfaces unchanged.

## References

- `_story_briefs/cs-295-implement-replay-snapshot-v1-storage-redaction.md`
- `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/00-story.md`
- `_condamad/stories/CS-278-replay-snapshot-v1-implementation/00-story.md`
- `docs/architecture/replay-snapshot-v1-storage-security-model.md`
- `docs/architecture/replay-snapshot-v1-dpo-security-approval-request.md`
- `backend/app/infra/db/models/llm/llm_observability.py`
- `backend/migrations/versions/51bdec8ae9a5_add_llm_observability_tables.py`
- `backend/app/domain/llm/runtime/observability_service.py`
- `backend/app/ops/llm/replay_service.py`
- `backend/app/core/sensitive_data.py`
- `backend/app/domain/audit/safe_details.py`
- `_condamad/stories/regression-guardrails.md`
