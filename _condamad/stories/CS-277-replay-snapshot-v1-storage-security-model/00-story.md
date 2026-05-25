# Story CS-277 replay-snapshot-v1-storage-security-model: Define replay_snapshot_v1 Storage And Security Model
Status: done

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-277-define-replay-snapshot-v1-storage-and-security-model.md`.
- Required dependency: CS-275 admin chart diagnostics retention, redaction and replay policy.
- Required dependency: CS-276 admin chart diagnostics implementation story.
- Existing owner found: CS-275 keeps replay separate from current diagnostics and requires storage, input, version and retention prerequisites.
- Existing owner found: CS-276 keeps `admin_chart_diagnostics_v1` distinct from `replay_snapshot_v1`.
- Existing owner found: `backend/app/core/sensitive_data.py` classifies LLM replay snapshots and birth-data fields as sensitive.
- Existing owner found: `backend/app/infra/db/models/llm/llm_canonical_perimeter.py` names `replay_snapshot` in the LLM perimeter.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: `replay_snapshot_v1` needs an approved storage and security model before any replay implementation.
- Source-alignment evidence: PASS; this story covers stored content, masked data, roles, retention, diagnostics and AI audit links.

## Objective

Define one canonical backend-domain contract for the `replay_snapshot_v1` storage and security model.

The implementation must document minimal stored replay content, forbidden or masked data, authorized access roles, retention or DPO blocker state, purge rules,
and links with diagnostics and AI audit without creating replay execution, routes, services, models, migrations, frontend UI or RGPD policy changes.

## Target State

- `docs/architecture/replay-snapshot-v1-storage-security-model.md` exists and starts with a French global file comment.
- The document defines `replay_snapshot_v1` as a protected internal storage contract, not a runtime replay executor.
- Minimal stored content is listed for calculation identity, input reconstruction reference, version identity, provenance, diagnostics link and AI audit link.
- Forbidden or masked data categories are listed, including raw birth data, coordinates, direct identifiers, prompts, model payloads and secrets.
- Authorized roles are limited to approved internal roles from CS-270 and CS-271, with denied roles documented.
- Retention is decided with a concrete target or blocked by a named DPO decision entry with exact implementation surfaces held back.
- Purge behavior is documented for expiry, manual deletion, linked diagnostics and linked AI audit records.
- Replay storage remains separate from current redacted diagnostics, `admin_chart_diagnostics_v1` and narrative answer audit records.
- No replay route, replay service, replay builder, DB model, migration, UI, public OpenAPI path or RGPD policy change is created.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-277-define-replay-snapshot-v1-storage-and-security-model.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-277`.
- Evidence 3: `_condamad/stories/CS-275-admin-chart-diagnostics-policy/00-story.md` - replay prerequisites dependency inspected.
- Evidence 4: `_condamad/stories/CS-276-admin-chart-diagnostics-v1/00-story.md` - diagnostic implementation boundary inspected.
- Evidence 5: `backend/app/core/sensitive_data.py` - sensitive replay and birth-data classifications found by targeted search.
- Evidence 6: `backend/app/infra/db/models/llm/llm_canonical_perimeter.py` - LLM replay perimeter naming found by targeted search.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output only.
- Evidence 8: `resolve_guardrails.py` - scoped resolver run for backend-domain, docs, replay, retention, redaction and audit scope.
- Repository structure alert: backend, backend/app, backend/tests, frontend, frontend/src and docs exist in this workspace.
- Source-alignment evidence: PASS; no brief criterion was dropped, softened or replaced by generic security documentation.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Canonical storage and security model documentation for `replay_snapshot_v1` under `docs/architecture`.
  - Minimal snapshot content, forbidden data, masking rules, authorized roles, retention, purge, diagnostics links and AI audit links.
  - Contract tests proving required sections and runtime neutrality through `pytest`, `app.routes`, `app.openapi()` and targeted `rg`.
  - Reuse of CS-275, CS-276, CS-270 and CS-271 decisions instead of creating a parallel security model.
- Out of scope:
  - Frontend UI, database schema, auth redesign, i18n, styling, build tooling, migrations, seeds, generated clients and public API changes.
  - Replay execution, production replay runs, replay builder, replay service, route creation, persistence implementation and RGPD policy modification.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No client route, admin route, generated client, DB table, Alembic migration, background purge job, replay executor or prompt replay pipeline.
  - No change to `admin_chart_diagnostics_v1`, narrative answer audit, calculation results, graph execution or public projection behavior.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a documentation-first backend storage and security model contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only `docs/architecture/replay-snapshot-v1-storage-security-model.md`, targeted contract tests and story evidence artifacts.
  - Reuse CS-275 for replay prerequisites and CS-276 for diagnostic separation.
  - Reuse CS-270 and CS-271 for internal roles and data-domain permission ownership.
  - Keep backend runtime code, API routes, OpenAPI output, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Keep `replay_snapshot_v1` separate from redacted diagnostics, narrative answer audit and LLM release snapshots.
  - Conclude `non approuve` in the document when retention, role access or sensitive-data policy lacks an approved decision.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: DPO, security or product owners cannot approve retention, purge, sensitive-data handling or role access.
- Additional validation rules:
  - The model must name `replay_snapshot_v1` exactly.
  - The model must define the minimal stored snapshot content.
  - The model must identify forbidden or masked sensitive data categories.
  - The model must limit access to explicit internal roles from CS-270 and CS-271.
  - The model must decide retention or record a named DPO blocker.
  - The model must define purge behavior for expiry and manual deletion.
  - The model must link replay snapshots to diagnostics and AI audit without merging those records.
  - The model must state that production replay execution is not approved by this story.
  - `app.routes`, `app.openapi()`, `pytest`, `python`, `rg` and scoped `git status` must prove runtime neutrality.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, `pytest` and source owners prove no runtime exposure is introduced. |
| Baseline Snapshot | yes | Before and after evidence prove the only allowed surface delta is documentation, tests and story evidence. |
| Ownership Routing | yes | Storage model, sensitive data, roles, diagnostics, AI audit, retention and purge owners must stay separated. |
| Allowlist Exception | no | No allowlist handling is authorized for this single canonical storage model. |
| Contract Shape | yes | The model has exact content, masking, permissions, retention, purge and linkage fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Replay execution, raw sensitive data and public exposure must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The storage model exists. | Evidence profile: baseline_before_after_diff; `python` checks the contract document path. |
| AC2 | Minimal snapshot content is defined. | Evidence profile: json_contract_shape; `rg` checks calculation identity, input reference, versions and provenance. |
| AC3 | Sensitive data handling is defined. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_replay_snapshot_v1_storage_security_model.py`. |
| AC4 | Authorized roles are limited. | Evidence profile: json_contract_shape; `rg` checks CS-270 roles, CS-271 domains and denied roles. |
| AC5 | Retention has a decision state. | Evidence profile: json_contract_shape; `rg` checks retention target, DPO blocker and held-back surfaces. |
| AC6 | Purge behavior is defined. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_replay_snapshot_v1_storage_security_model.py`. |
| AC7 | Diagnostics links stay separate. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks diagnostics links without replay implementation owners. |
| AC8 | AI audit links stay separate. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks narrative answer audit is referenced, not merged. |
| AC9 | Runtime exposure is absent. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`; `pytest` uses TestClient. |
| AC10 | Application source surfaces remain unchanged. | Evidence profile: repo_wide_negative_scan; `python` records scoped `git status --short` output. |
| AC11 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-277 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect the brief, CS-275, CS-276, CS-270, CS-271, sensitive-data policy and LLM perimeter owner. (AC: AC1, AC3, AC4)
- [ ] Task 2: Create `docs/architecture/replay-snapshot-v1-storage-security-model.md` with a French global file comment. (AC: AC1)
- [ ] Task 3: Define the minimal `replay_snapshot_v1` stored content and excluded runtime replay executor scope. (AC: AC2)
- [ ] Task 4: Define forbidden or masked data categories for birth data, coordinates, identifiers, prompts, payloads and secrets. (AC: AC3)
- [ ] Task 5: Define authorized internal roles and denied role classes using CS-270 and CS-271 as source decisions. (AC: AC4)
- [ ] Task 6: Record retention target or DPO blocker with implementation surfaces held back. (AC: AC5)
- [ ] Task 7: Define purge behavior for expiry, manual deletion, diagnostics links and AI audit links. (AC: AC6)
- [ ] Task 8: Document separation from diagnostics, `admin_chart_diagnostics_v1`, narrative answer audit and LLM release snapshots. (AC: AC7, AC8)
- [ ] Task 9: Add targeted contract tests for document shape, sensitive-data handling, purge and runtime neutrality. (AC: AC3, AC6, AC9)
- [ ] Task 10: Persist validation, scoped status and source-checklist evidence under the CS-277 evidence folder. (AC: AC10, AC11)

## Files to Inspect First

- `_story_briefs/cs-277-define-replay-snapshot-v1-storage-and-security-model.md` - source brief.
- `_condamad/stories/CS-275-admin-chart-diagnostics-policy/00-story.md` - retention, redaction and replay policy dependency.
- `_condamad/stories/CS-276-admin-chart-diagnostics-v1/00-story.md` - diagnostics implementation separation dependency.
- `_condamad/stories/CS-270-internal-role-model/00-story.md` - internal role source decision.
- `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md` - admin data permission source decision.
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md` - AI audit boundary.
- `_condamad/stories/CS-268-answer-audit-access-logs/00-story.md` - audit access log boundary.
- `backend/app/core/sensitive_data.py` - sensitive data and replay classification owner.
- `backend/app/infra/db/models/llm/llm_canonical_perimeter.py` - LLM perimeter and replay snapshot naming owner.
- `backend/app/main.py` - loaded FastAPI app for `app.routes` and `app.openapi()`.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - CS-275 for current diagnostics replay prerequisites and redaction policy.
  - CS-276 for `admin_chart_diagnostics_v1` separation from replay.
  - CS-270 and CS-271 for internal roles and admin data-domain permissions.
  - `backend/app/core/sensitive_data.py` for sensitive replay and birth-data classifications.
  - `app.routes`, `app.openapi()`, `TestClient`, `pytest`, scoped `git status` and targeted `rg` scans for runtime neutrality.
- Secondary evidence:
  - Targeted `rg` scans over `docs/architecture/replay-snapshot-v1-storage-security-model.md`.
  - `pytest -q backend/tests/unit/test_replay_snapshot_v1_storage_security_model.py` for policy content and runtime-neutrality checks.
- Static scans alone are not sufficient because:
  - public OpenAPI neutrality and route absence must be checked from the loaded FastAPI app.

## Contract Shape

- Contract type:
  - Markdown backend-domain storage and security model for replay snapshots.
- Fields:
  - `model_id`: exact value `replay_snapshot_v1_storage_security_model`.
  - `snapshot_type`: exact value `replay_snapshot_v1`.
  - `classification`: protected internal replay support and debug data.
  - `minimal_stored_content`: calculation identity, input reconstruction reference, version identity, provenance and correlation ids.
  - `forbidden_data`: raw birth data, exact coordinates, direct identifiers, raw prompts, raw model payloads and secrets.
  - `masking_policy`: mask, hash, truncate, tokenize or deny storage for each sensitive category.
  - `authorized_roles`: explicit internal roles allowed to request or view snapshot metadata.
  - `denied_roles`: client, public, marketing-only and unauthorized admin classes denied by default.
  - `retention_policy`: concrete retention target or DPO blocker with held-back implementation surfaces.
  - `purge_policy`: expiry purge, manual purge, linked diagnostics update and audit log retention notes.
  - `diagnostics_link`: reference from diagnostics to replay metadata without embedding replay payloads.
  - `ai_audit_link`: reference from AI audit to replay metadata without merging narrative answer audit data.
  - `approval_state`: approved, non approuve or blocked by named owner decision.
- Required fields:
  - `model_id`
  - `snapshot_type`
  - `classification`
  - `minimal_stored_content`
  - `forbidden_data`
  - `masking_policy`
  - `authorized_roles`
  - `denied_roles`
  - `retention_policy`
  - `purge_policy`
  - `diagnostics_link`
  - `ai_audit_link`
  - `approval_state`
- Optional fields:
  - none.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - documentation only; no runtime JSON serializer is added.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose `replay_snapshot_v1` from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-277-define-replay-snapshot-v1-storage-and-security-model.md`
  - `_condamad/stories/CS-275-admin-chart-diagnostics-policy/00-story.md`
  - `_condamad/stories/CS-276-admin-chart-diagnostics-v1/00-story.md`
  - `backend/app/core/sensitive_data.py`
  - `backend/app/infra/db/models/llm/llm_canonical_perimeter.py`
- Comparison after implementation:
  - `docs/architecture/replay-snapshot-v1-storage-security-model.md`
  - `backend/tests/unit/test_replay_snapshot_v1_storage_security_model.py`
  - `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/evidence/validation.txt`
  - `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended repository delta is one architecture model document, one targeted test and CONDAMAD evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Storage and security model | `docs/architecture/replay-snapshot-v1-storage-security-model.md` | Backend route, service or DB model |
| Sensitive data classification | `backend/app/core/sensitive_data.py` | Local ad hoc sanitizer in replay docs or tests |
| Role permissions | CS-270 and CS-271 story contracts | New role taxonomy inside replay model |
| Diagnostics linkage | CS-275 and CS-276 contracts | Embedded replay payload inside diagnostics |
| AI audit linkage | CS-259 and CS-268 contracts | Merged replay payload inside narrative answer audit |

## Mandatory Reuse / DRY Constraints

- Reuse CS-275 for replay prerequisites and redaction policy language.
- Reuse CS-276 for `admin_chart_diagnostics_v1` separation and denied replay implementation scope.
- Reuse CS-270 and CS-271 for role and permission names; do not define a competing role system.
- Reuse `backend/app/core/sensitive_data.py` classifications for sensitive replay and birth-data categories.
- Reuse existing architecture documentation style under `docs/architecture`.
- Do not duplicate storage, security or replay policy in another documentation file.

## No Legacy / Forbidden Paths

- No legacy replay route may be added for this storage model.
- No compatibility replay path may be added for this storage model.
- No fallback storage path may be added for this storage model.
- No replay executor, replay builder, replay service, DB model, migration or background purge job is authorized.
- No raw birth data, exact coordinates, direct identifiers, raw prompts, raw model payloads or secrets may be approved as default stored content.
- No public route, frontend client, generated client or public OpenAPI exposure may mention `replay_snapshot_v1`.

## Reintroduction Guard

- Forbidden runtime surfaces:
  - `replay_snapshot_v1` route registration in `app.routes`.
  - `replay_snapshot_v1` public or admin path in `app.openapi()`.
  - Replay executor, builder, service, DB model, migration or frontend source delta.
- Required deterministic guards:
  - `python -c "from app.main import app; assert 'replay_snapshot_v1' not in str(app.openapi())"`
  - `python -c "from app.main import app; assert 'replay_snapshot_v1' not in {getattr(r, 'path', '') for r in app.routes}"`
  - `rg -n "replay_snapshot_v1|replay snapshot" docs/architecture backend/tests/unit`
  - `git status --short -- backend/app frontend/src`

## Regression Guardrails

| Guardrail | Applies because | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Runtime route surfaces must stay unchanged. | `python` checks `app.routes`; scoped `git status`. |
| RG-047 `CS-029-encadrer-styles-inline-statiques-frontend` | Non-applicable example: frontend UI is out of scope. | `git status --short -- frontend/src`. |
| RG-052 `CS-075-converger-namespaces-css-migration-only-restants` | Non-applicable example: frontend CSS is out of scope. | `git status --short -- frontend/src`. |
| Registry gap `replay_snapshot_v1-security` | No exact replay snapshot storage guardrail was resolved. | `resolve_guardrails.py` scoped output. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Source checklist | `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/evidence/source-checklist.md` | Prove brief and dependencies were inspected. |
| Runtime status | `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/evidence/app-surface-status.txt` | Prove runtime route and OpenAPI neutrality. |
| Validation output | `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/evidence/validation.txt` | Keep lint, tests and scans output. |
| Review output | `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this single canonical storage and security model.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/replay-snapshot-v1-storage-security-model.md` - canonical storage and security model.
- `backend/tests/unit/test_replay_snapshot_v1_storage_security_model.py` - contract and runtime-neutrality tests.
- `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/evidence/source-checklist.md` - persisted source evidence.
- `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/evidence/app-surface-status.txt` - runtime neutrality evidence.
- `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/evidence/validation.txt` - validation evidence.

Likely tests:

- `backend/tests/unit/test_replay_snapshot_v1_storage_security_model.py` - cover shape, sensitive data, roles, retention, purge and neutrality.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no route is added.
- `backend/app/infra/db/**` - out of scope; no persistence or migration is added.
- `backend/app/services/llm_generation/**` - out of scope; no LLM replay execution is added.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `python -c "from pathlib import Path; assert Path('docs/architecture/replay-snapshot-v1-storage-security-model.md').exists()"`
- VC2: `pytest -q backend/tests/unit/test_replay_snapshot_v1_storage_security_model.py`
- VC3: `python -c "from app.main import app; assert 'replay_snapshot_v1' not in str(app.openapi())"`
- VC4: `python -c "from app.main import app; assert 'replay_snapshot_v1' not in {getattr(r, 'path', '') for r in app.routes}"`
- VC5: `rg -n "replay_snapshot_v1|snapshot|stockage|sécurité|rétention|audit IA|diagnostics" .\docs .\_story_briefs`
- VC6: `git status --short -- backend/app frontend/src`
- VC7: `ruff format .`
- VC8: `ruff check .`
- VC9: `pytest -q`

## Regression Risks

- A replay snapshot could store raw inputs, prompts or identifiers before security approval.
- A replay storage contract could merge with current redacted diagnostics and weaken the CS-275 boundary.
- Role names could drift from CS-270 and CS-271, creating a parallel permission model.
- Retention could remain vague, allowing implementation without DPO approval.
- AI audit links could become payload copies instead of stable references.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the backend virtual environment before any Python command.
- Keep documentation comments and public docstrings in French for new or significantly modified applicative files.
- Keep all frontend, DB migration, route, replay executor and RGPD policy surfaces unchanged.

## References

- `_story_briefs/cs-277-define-replay-snapshot-v1-storage-and-security-model.md`
- `_condamad/stories/CS-275-admin-chart-diagnostics-policy/00-story.md`
- `_condamad/stories/CS-276-admin-chart-diagnostics-v1/00-story.md`
- `_condamad/stories/CS-270-internal-role-model/00-story.md`
- `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md`
- `backend/app/core/sensitive_data.py`
- `backend/app/infra/db/models/llm/llm_canonical_perimeter.py`
- `_condamad/stories/regression-guardrails.md`
