# Story CS-278 replay-snapshot-v1-implementation: Implement replay_snapshot_v1 After Approval
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-278-implement-replay-snapshot-v1-if-approved.md`.
- Required dependency: CS-277 replay snapshot storage and security model must be approved before implementation.
- Existing owner found: CS-277 defines the expected storage, security, redaction, role, retention and purge model.
- Existing owner found: backend already contains LLM replay storage and service surfaces, so no parallel replay owner is authorized.
- Existing owner found: `backend/app/core/sensitive_data.py` classifies LLM replay snapshots as sensitive data.
- Existing owner found: `backend/app/domain/audit/safe_details.py` contains a safe audit details structure for LLM replay events.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: `replay_snapshot_v1` can be implemented only after the CS-277 approval gate is satisfied.
- Source-alignment evidence: PASS; approval gate, storage, permissions, logs, redaction, access, reproducibility and retention are covered.

## Objective

Implement the backend `replay_snapshot_v1` storage and controlled replay support only after CS-277 approval is confirmed.

The implementation must persist approved replay snapshots, enforce approved access, log every access, redact sensitive data, prove deterministic replay
behavior or document bounded non-determinism, and honor retention or purge rules without exposing the feature to clients.

## Target State

- A deterministic approval gate prevents implementation work unless CS-277 is `done` or a written approval artifact is present.
- `replay_snapshot_v1` storage uses the approved CS-277 contract for stored fields, redaction, retention and purge semantics.
- Existing backend replay, audit, sensitivity and LLM storage owners are reused or extended rather than duplicated.
- Snapshot payloads never contain secrets, raw prompts, exact coordinates, direct identifiers or unredacted birth data.
- Access to replay snapshots is restricted to the approved internal roles and data domains from CS-270, CS-271 and CS-277.
- Every replay snapshot read, replay execution attempt and purge action writes a safe audit log event.
- Reproducibility tests prove deterministic replay for approved deterministic inputs.
- Non-deterministic limits are documented in a versioned backend contract artifact.
- Retention and purge behavior is covered by tests and linked to the approved CS-277 policy.
- No frontend, public route, generated client, broad admin exposure or unrelated LLM replay redesign is introduced.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-278-implement-replay-snapshot-v1-if-approved.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-278`.
- Evidence 3: `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/00-story.md` - dependency contract inspected.
- Evidence 4: targeted `rg` found existing replay surfaces under `backend/app/ops/llm` and `backend/app/services/llm_observability`.
- Evidence 5: targeted `rg` found `llm_replay_snapshots` in backend DB model and guarded artifact files.
- Evidence 6: targeted `rg` found replay access tests under `backend/tests/llm_orchestration` and `backend/app/tests/unit`.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output only.
- Evidence 8: `resolve_guardrails.py` - scoped resolver run for backend-domain replay, storage, security, redaction and retention scope.
- Repository structure alert: backend, backend/app, backend/tests, frontend and frontend/src exist in this workspace.
- Source-alignment evidence: PASS; no brief criterion was dropped, softened or replaced by generic replay work.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend `replay_snapshot_v1` storage and controlled replay support after CS-277 approval.
  - Reuse or extension of existing LLM replay, audit, sensitive-data, storage and retention owners.
  - Permission checks, safe access logs, redaction tests, access tests, reproducibility tests and retention tests.
  - Documentation of bounded non-deterministic replay limits.
- Out of scope:
  - Frontend UI, public client exposure, generated clients, styling, i18n, build tooling and public OpenAPI exposure.
  - Role taxonomy redesign, RGPD policy change, broad diagnostics redesign and unrelated LLM observability cleanup.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No client route, public route, public projection, generated frontend client, alternate replay owner or second snapshot table.
  - No storage of secrets, raw prompts, exact coordinates, direct identifiers or unredacted birth data.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a gated backend replay storage and controlled execution implementation.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Implement only `replay_snapshot_v1` after CS-277 approval is proven.
  - Reuse existing replay, audit, sensitive-data and LLM storage owners before creating new backend owners.
  - Add only approved storage fields, permission checks, safe logs, redaction, reproducibility tests and retention or purge behavior.
  - Keep frontend, generated clients, public routes, public OpenAPI paths, role taxonomy and unrelated LLM replay behavior unchanged.
  - Keep snapshot payloads free of secrets, raw prompts, exact coordinates, direct identifiers and unredacted birth data.
  - Stop before code changes when CS-277 approval cannot be proven.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-277 is not approved or its retention, access, storage, purge or redaction policy remains undecided.
- Additional validation rules:
  - The implementation must prove the CS-277 approval gate before any code path can persist or replay snapshots.
  - The implementation must inspect and reuse existing backend replay and storage owners.
  - The implementation must store only the fields approved by CS-277.
  - The implementation must redact or reject all forbidden sensitive data categories.
  - The implementation must enforce CS-270, CS-271 and CS-277 role and data-domain permissions.
  - The implementation must log replay snapshot reads, replay attempts and purge actions with safe details.
  - The implementation must prove deterministic replay or document bounded non-determinism.
  - The implementation must cover retention and purge behavior with deterministic tests.
  - `app.routes`, `app.openapi()`, `pytest`, `rg`, loaded settings and DB schema checks must prove the final runtime surface.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, loaded config, DB schema, `app.routes` and `app.openapi()` prove gated backend behavior. |
| Baseline Snapshot | yes | Before and after artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Existing replay, audit, storage, sensitivity and permission owners must not be duplicated. |
| Allowlist Exception | no | No broad allowlist handling is authorized for this controlled replay implementation. |
| Contract Shape | yes | Snapshot fields, redaction, access log, retention and replay result shape are exact. |
| Batch Migration | no | No batch conversion of existing records is in scope. |
| Reintroduction Guard | yes | Public exposure, raw sensitive data and parallel replay owners must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | CS-277 approval is gated. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/unit/test_replay_snapshot_v1_approval_gate.py`. |
| AC2 | Existing replay owners are reused. | Evidence profile: ast_architecture_guard; `rg` checks owners; `pytest -q backend/tests/unit/test_replay_snapshot_v1_ownership.py`. |
| AC3 | Snapshot storage follows CS-277. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_replay_snapshot_v1_storage.py`. |
| AC4 | Forbidden data is redacted. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_replay_snapshot_v1_redaction.py`. |
| AC5 | Snapshot access is permissioned. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_replay_snapshot_v1_access.py`. |
| AC6 | Snapshot access is logged. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_replay_snapshot_v1_audit_logs.py`. |
| AC7 | Deterministic replay is proven. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_replay_snapshot_v1_reproducibility.py`. |
| AC8 | Replay limits are documented. | Evidence profile: baseline_before_after_diff; `rg` checks the replay limits document. |
| AC9 | Retention behavior is enforced. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_replay_snapshot_v1_retention.py`. |
| AC10 | Public API exposure is unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`. |
| AC11 | Parallel replay owners are absent. | Evidence profile: repo_wide_negative_scan; `rg` checks duplicate `replay_snapshot_v1` owners. |
| AC12 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-278 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Verify CS-277 approval state and stop before implementation when the gate is not satisfied. (AC: AC1)
- [ ] Task 2: Inspect existing replay, storage, audit, sensitive-data, permission and retention owners before editing. (AC: AC2)
- [ ] Task 3: Add or extend canonical snapshot persistence according to the approved CS-277 storage shape. (AC: AC3)
- [ ] Task 4: Add redaction or rejection rules for secrets, prompts, coordinates, identifiers and raw birth data. (AC: AC4)
- [ ] Task 5: Enforce approved internal role and data-domain permissions for every snapshot access. (AC: AC5)
- [ ] Task 6: Emit safe audit log events for reads, replay attempts and purge actions. (AC: AC6)
- [ ] Task 7: Implement controlled deterministic replay for approved deterministic snapshot inputs. (AC: AC7)
- [ ] Task 8: Document non-deterministic replay limits in the backend architecture contract. (AC: AC8)
- [ ] Task 9: Implement retention and purge behavior according to the approved CS-277 policy. (AC: AC9)
- [ ] Task 10: Add runtime guards proving no new public API route or OpenAPI path is exposed. (AC: AC10)
- [ ] Task 11: Add architecture guards against duplicate replay owners and unauthorized storage paths. (AC: AC11)
- [ ] Task 12: Persist validation, runtime, schema and source checklist evidence under the CS-278 evidence folder. (AC: AC12)

## Files to Inspect First

- `_story_briefs/cs-278-implement-replay-snapshot-v1-if-approved.md` - source brief.
- `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/00-story.md` - required approval contract.
- `_condamad/stories/CS-270-internal-role-model/00-story.md` - internal role source decision.
- `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md` - permission matrix source decision.
- `backend/app/core/sensitive_data.py` - sensitive replay classification owner.
- `backend/app/domain/audit/safe_details.py` - safe audit details owner.
- `backend/app/ops/llm/replay_service.py` - existing replay service owner.
- `backend/app/ops/llm/services.py` - existing replay service export owner.
- `backend/app/services/llm_observability/admin_observability.py` - existing admin replay access owner.
- `backend/app/api/v1/routers/admin/llm/observability.py` - existing admin LLM replay route owner.
- `backend/app/infra/db/models/llm/llm_observability.py` - existing LLM replay snapshot model owner.
- `backend/app/infra/db/models/llm/llm_canonical_perimeter.py` - LLM storage perimeter owner.
- `backend/app/services/ops/feature_flag_service.py` - existing LLM replay feature flag owner.
- `backend/app/main.py` - loaded FastAPI app for `app.routes` and `app.openapi()`.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - CS-277 approval state for the implementation gate.
  - CS-270 and CS-271 for internal roles and data-domain permissions.
  - Existing backend LLM replay, audit, sensitive-data, storage and feature-flag owners.
  - DB schema inspection for approved snapshot persistence fields.
  - Loaded settings or feature flags for controlled replay availability.
  - `app.routes`, `app.openapi()`, `TestClient`, `pytest` and targeted `rg` scans for runtime exposure checks.
- Secondary evidence:
  - Targeted unit tests for storage shape, redaction, access, logs, reproducibility and retention.
  - Targeted architecture tests for owner reuse and duplicate owner absence.
  - Runtime evidence artifacts under `_condamad/stories/CS-278-replay-snapshot-v1-implementation/evidence`.
- Static scans alone are not sufficient because:
  - permission behavior, stored fields, DB schema, loaded settings and runtime API exposure must be proven from executable tests.

## Contract Shape

- Contract type:
  - Backend `replay_snapshot_v1` storage, access, audit, retention and controlled replay behavior.
- Fields:
  - `snapshot_type`: exact value `replay_snapshot_v1`.
  - `source_kind`: approved calculation or generation source kind.
  - `source_id`: stable reference to the source event or calculation.
  - `input_reference`: redacted or hashed reconstruction reference approved by CS-277.
  - `version_identity`: graph, prompt, model, code or contract version identifiers approved by CS-277.
  - `provenance`: trace, correlation and audit references approved by CS-277.
  - `redaction_state`: exact status for stored payload safety.
  - `access_policy`: approved role and data-domain policy reference.
  - `retention_policy`: approved expiry and purge policy reference.
  - `audit_event_id`: safe audit log reference for access or replay attempt.
  - `replay_result`: deterministic outcome, documented bounded non-determinism or denied replay state.
- Required fields:
  - `snapshot_type`
  - `source_kind`
  - `source_id`
  - `input_reference`
  - `version_identity`
  - `provenance`
  - `redaction_state`
  - `access_policy`
  - `retention_policy`
  - `audit_event_id`
  - `replay_result`
- Optional fields:
  - none.
- Status codes:
  - none for public API; this story does not authorize new client exposure.
- Serialization names:
  - runtime names must match the approved CS-277 storage model.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose a new `replay_snapshot_v1` public path from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-278-implement-replay-snapshot-v1-if-approved.md`
  - `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/00-story.md`
  - `backend/app/ops/llm/replay_service.py`
  - `backend/app/infra/db/models/llm/llm_observability.py`
  - `backend/app/core/sensitive_data.py`
- Comparison after implementation:
  - `_condamad/stories/CS-278-replay-snapshot-v1-implementation/evidence/source-checklist.md`
  - `_condamad/stories/CS-278-replay-snapshot-v1-implementation/evidence/runtime-surface-status.txt`
  - `_condamad/stories/CS-278-replay-snapshot-v1-implementation/evidence/db-schema-status.txt`
  - `_condamad/stories/CS-278-replay-snapshot-v1-implementation/evidence/validation.txt`
- Expected invariant:
  - The only intended delta is approved backend replay snapshot implementation, tests, documentation and CONDAMAD evidence.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Replay implementation gate | CS-277 approval artifact and backend tests | Silent runtime toggle |
| Replay execution owner | Existing `backend/app/ops/llm` or approved backend domain owner | Duplicate service tree |
| Snapshot storage owner | Existing LLM storage model or approved CS-277 storage owner | Second replay table |
| Sensitive-data policy | `backend/app/core/sensitive_data.py` | Local ad hoc sanitizer |
| Access logs | Existing audit domain and safe details owner | Raw event payload dump |
| Permissions | CS-270, CS-271 and approved auth owner | New role taxonomy |
| Retention and purge | Approved CS-277 policy owner | Untracked scheduled job |

## Mandatory Reuse / DRY Constraints

- Reuse CS-277 as the mandatory storage, security, redaction, retention and purge contract.
- Reuse CS-270 and CS-271 for internal role and data-domain permission decisions.
- Reuse existing LLM replay service, admin observability and snapshot model owners before adding any new owner.
- Reuse `backend/app/core/sensitive_data.py` for sensitive data classification.
- Reuse `backend/app/domain/audit/safe_details.py` or the existing audit owner for safe log details.
- Do not duplicate replay storage shape in a separate model, table, route, service tree or documentation-only contract.

## No Legacy / Forbidden Paths

- No legacy replay path may be added for `replay_snapshot_v1`.
- No compatibility replay path may be added for `replay_snapshot_v1`.
- No fallback replay path may be added for `replay_snapshot_v1`.
- No public route, frontend route, generated client or public OpenAPI path may expose `replay_snapshot_v1`.
- No second snapshot table, duplicate replay service tree or parallel permission model is authorized.
- No secrets, raw prompts, exact coordinates, direct identifiers or unredacted birth data may be stored.
- No retention bypass or purge bypass is authorized.

## Reintroduction Guard

- Forbidden runtime surfaces:
  - Public `replay_snapshot_v1` path in `app.routes` or `app.openapi()`.
  - Duplicate replay service tree outside the approved owner.
  - Snapshot persistence containing secrets, raw prompts, exact coordinates, direct identifiers or unredacted birth data.
  - Replay execution before the CS-277 approval gate is proven.
- Required deterministic guards:
  - `pytest -q backend/tests/unit/test_replay_snapshot_v1_approval_gate.py`
  - `pytest -q backend/tests/unit/test_replay_snapshot_v1_redaction.py`
  - `pytest -q backend/tests/unit/test_replay_snapshot_v1_access.py`
  - `pytest -q backend/tests/unit/test_replay_snapshot_v1_retention.py`
  - `python -c "from app.main import app; assert 'replay_snapshot_v1' not in str(app.openapi())"`
  - `python -c "from app.main import app; assert 'replay_snapshot_v1' not in {getattr(r, 'path', '') for r in app.routes}"`
  - `rg -n "replay_snapshot_v1|llm_replay_snapshots" backend/app backend/tests`

## Regression Guardrails

| Guardrail | Applies because | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | API route surfaces must not gain public replay exposure. | `python` checks `app.routes`; `app.openapi()`. |
| RG-022 `prompt-generation-validation-plans` | Backend tests and validation plans touch LLM replay surfaces. | targeted `pytest`; scoped `rg`. |
| RG-047 `CS-029-encadrer-styles-inline-statiques-frontend` | Non-applicable example: frontend UI is out of scope. | `git status --short -- frontend/src`. |
| RG-052 `CS-075-converger-namespaces-css-migration-only-restants` | Non-applicable example: frontend CSS is out of scope. | `git status --short -- frontend/src`. |
| Registry gap `replay_snapshot_v1-runtime` | No exact replay snapshot implementation guardrail was resolved. | `resolve_guardrails.py` scoped output. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Source checklist | `_condamad/stories/CS-278-replay-snapshot-v1-implementation/evidence/source-checklist.md` | Prove source and owners were inspected. |
| Runtime status | `_condamad/stories/CS-278-replay-snapshot-v1-implementation/evidence/runtime-surface-status.txt` | Prove route and OpenAPI exposure. |
| Schema status | `_condamad/stories/CS-278-replay-snapshot-v1-implementation/evidence/db-schema-status.txt` | Prove approved storage schema. |
| Validation output | `_condamad/stories/CS-278-replay-snapshot-v1-implementation/evidence/validation.txt` | Keep lint, tests and scans output. |
| Review output | `_condamad/stories/CS-278-replay-snapshot-v1-implementation/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this controlled replay implementation.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/ops/llm/replay_service.py` - controlled replay behavior owner.
- `backend/app/ops/llm/services.py` - existing replay service export owner.
- `backend/app/services/llm_observability/admin_observability.py` - existing admin replay access owner.
- `backend/app/infra/db/models/llm/llm_observability.py` - existing replay snapshot storage owner.
- `backend/app/core/sensitive_data.py` - sensitive replay classification owner.
- `backend/app/domain/audit/safe_details.py` - safe replay audit details owner.
- `backend/app/services/ops/feature_flag_service.py` - replay availability gate owner.
- `backend/docs/architecture/replay-snapshot-v1-limits.md` - bounded non-determinism limits.
- `_condamad/stories/CS-278-replay-snapshot-v1-implementation/evidence/source-checklist.md` - persisted source evidence.
- `_condamad/stories/CS-278-replay-snapshot-v1-implementation/evidence/runtime-surface-status.txt` - runtime evidence.
- `_condamad/stories/CS-278-replay-snapshot-v1-implementation/evidence/db-schema-status.txt` - schema evidence.
- `_condamad/stories/CS-278-replay-snapshot-v1-implementation/evidence/validation.txt` - validation evidence.

Likely tests:

- `backend/tests/unit/test_replay_snapshot_v1_approval_gate.py` - approval gate behavior.
- `backend/tests/unit/test_replay_snapshot_v1_ownership.py` - owner reuse and duplicate-owner guard.
- `backend/tests/unit/test_replay_snapshot_v1_storage.py` - snapshot storage contract.
- `backend/tests/unit/test_replay_snapshot_v1_redaction.py` - forbidden sensitive data redaction.
- `backend/tests/unit/test_replay_snapshot_v1_access.py` - approved role and data-domain access.
- `backend/tests/unit/test_replay_snapshot_v1_audit_logs.py` - safe access and replay audit logs.
- `backend/tests/unit/test_replay_snapshot_v1_reproducibility.py` - deterministic replay contract.
- `backend/tests/unit/test_replay_snapshot_v1_retention.py` - retention and purge behavior.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/v1/routers/public/**` - out of scope; no public route is added.
- `backend/app/api/v1/routers/admin/llm/observability.py` - unchanged unless CS-277 authorizes controlled admin exposure.
- `backend/migrations/**` - unchanged unless CS-277 approval requires schema creation or alteration.
- `backend/app/domain/astrology/runtime/**` - unchanged unless CS-277 authorizes calculation replay inputs.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `pytest -q backend/tests/unit/test_replay_snapshot_v1_approval_gate.py`
- VC2: `pytest -q backend/tests/unit/test_replay_snapshot_v1_ownership.py`
- VC3: `pytest -q backend/tests/unit/test_replay_snapshot_v1_storage.py`
- VC4: `pytest -q backend/tests/unit/test_replay_snapshot_v1_redaction.py`
- VC5: `pytest -q backend/tests/unit/test_replay_snapshot_v1_access.py`
- VC6: `pytest -q backend/tests/unit/test_replay_snapshot_v1_audit_logs.py`
- VC7: `pytest -q backend/tests/unit/test_replay_snapshot_v1_reproducibility.py`
- VC8: `pytest -q backend/tests/unit/test_replay_snapshot_v1_retention.py`
- VC9: `python -c "from app.main import app; assert 'replay_snapshot_v1' not in str(app.openapi())"`
- VC10: `python -c "from app.main import app; assert 'replay_snapshot_v1' not in {getattr(r, 'path', '') for r in app.routes}"`
- VC11: `rg -n "replay_snapshot_v1|llm_replay_snapshots|replay_service" backend/app backend/tests backend/docs`
- VC12: `rg -n "OPENAI_API_KEY|SECRET|raw_prompt|exact_coordinates|direct_identifier" backend/app backend/tests`
- VC13: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-278-replay-snapshot-v1-implementation/evidence/validation.txt').exists()"`
- VC14: `ruff format .`
- VC15: `ruff check .`
- VC16: `pytest -q`

## Regression Risks

- Implementation could proceed while CS-277 remains unapproved.
- A duplicate replay storage owner could drift from the existing LLM replay perimeter.
- Snapshot payloads could retain raw sensitive inputs or prompts.
- Access logs could include unsafe details instead of references.
- Retention could be bypassed during deterministic replay testing.
- Public API or frontend exposure could appear before product approval.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the backend virtual environment before any Python command.
- Confirm CS-277 approval before editing application code for this story.
- Reuse existing replay, audit, storage and sensitive-data owners before creating new owners.
- Keep documentation comments and public docstrings in French for new or significantly modified applicative files.
- Keep frontend, public API, generated client, role-taxonomy and broad LLM observability surfaces unchanged.

## References

- `_story_briefs/cs-278-implement-replay-snapshot-v1-if-approved.md`
- `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/00-story.md`
- `_condamad/stories/CS-270-internal-role-model/00-story.md`
- `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md`
- `backend/app/core/sensitive_data.py`
- `backend/app/domain/audit/safe_details.py`
- `backend/app/ops/llm/replay_service.py`
- `backend/app/infra/db/models/llm/llm_observability.py`
- `_condamad/stories/regression-guardrails.md`
