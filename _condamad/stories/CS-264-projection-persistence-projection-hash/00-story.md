# Story CS-264 projection-persistence-projection-hash: Persist Projection Payloads With projection_hash
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-264-implement-projection-persistence-and-projection-hash.md`.
- Related dependency: CS-256 defines `structured_facts_v1` as a stable hashable projection contract.
- Related dependency: CS-259 defines `narrative_answer_audit_v1` and requires `projection_hash`.
- Related dependency: CS-263 defines the future projection endpoint contract and the `persist` request intent.
- Related dependency: CS-285, CS-286 and CS-287 are named builder prerequisites in the brief but are not registered yet.
- Existing owner found: `backend/app/infra/db/models/chart_result.py` stores chart result payloads and input hashes.
- Existing owner found: `backend/app/infra/db/repositories/chart_result_repository.py` owns chart lookup semantics.
- Existing owner found: `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` builds AI narrative input links.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: generated projections cannot be audited because no persisted projection row records payload, version, sources and hash.
- Source-alignment evidence: PASS; ACs preserve persistence, stable canonical hash, source versions, audit linkage and builder gating.

## Objective

Add controlled backend persistence for projection payloads that are already produced by real validated builders.

The implementation must introduce one canonical persistence model, deterministic `projection_hash` calculation, source-version storage,
role/type-filtered access and tests without inventing projection builders or exposing internal projection payloads to clients.

## Target State

- A persisted projection record stores `projection_type`, `projection_version`, `projection_hash`, canonical payload, `source_versions`,
  `source`, owner identifiers and UTC `generated_at`.
- `projection_hash` is computed from canonical JSON using deterministic key ordering, stable separators and UTF-8 SHA-256.
- Equal canonical payloads produce the same hash, and a meaningful canonical payload change produces a different hash.
- Source versions are stored as structured JSON and remain queryable with the persisted projection.
- Repository and service reads are filtered by projection type and requesting role or access scope.
- `narrative_answer_audit_v1` can reference a persisted projection by type, version and `projection_hash`.
- The implementation stops and records a blocker if no real builder exists for the first persisted projection type.
- No fake projection, placeholder builder, client exposure, back-office screen or broad historical versioning is created.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-264-implement-projection-persistence-and-projection-hash.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-264`.
- Evidence 3: `backend/app/infra/db/models/chart_result.py` - existing result payload and `input_hash` persistence owner found.
- Evidence 4: `backend/app/infra/db/repositories/chart_result_repository.py` - existing `chart_id` lookup owner found.
- Evidence 5: `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` - `source_versions` vocabulary found.
- Evidence 6: `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` - public projection link builder found.
- Evidence 7: targeted `rg` found no current `projection_hash` persistence implementation in `backend`.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output only.
- Source-alignment evidence: PASS; the story does not replace missing builders with invented projections.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend DB model, Alembic migration, repository and service for persisted projection records.
  - Canonical JSON hash helper for projection payloads.
  - Access filtering by `projection_type` and requesting role or access scope.
  - Linkage contract to `narrative_answer_audit_v1` through `projection_type`, `projection_version` and `projection_hash`.
  - Tests proving hash stability, hash change, source-version retention, DB schema and builder gating.
- Out of scope:
  - Frontend UI, client generation, public API implementation, back-office, i18n, styling and build tooling.
  - Implementing every projection, long historical retention, prompt/provider changes and LLM narrative generation.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No public endpoint or OpenAPI route for reading persisted internal projections.
  - No fake projection builder, placeholder projection payload or synthetic builder result.
  - No multi-version historical archive beyond the current persisted row contract.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend persistence and hash contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only persistence, hash, repository, service and tests for controlled projections.
  - Persist only payloads returned by an existing real builder selected during implementation.
  - Keep frontend, public API routes, OpenAPI output, auth implementation, i18n, style and build tooling unchanged.
  - Keep projection construction separate from chart calculation and narrative audit storage.
  - Keep internal projection payloads unavailable to clients through this story.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: no real builder exists for the first projection type selected for persistence.
- Additional validation rules:
  - A persisted projection must include `projection_type`, `projection_version`, `projection_hash`, `source_versions`, `source` and `generated_at`.
  - The hash helper must serialize canonical JSON with stable key ordering before SHA-256.
  - Tests must prove identical canonical payload stability and changed canonical payload divergence.
  - Repository reads must require projection type and role or access scope filters.
  - `narrative_answer_audit_v1` linkage must name `projection_hash` and the persisted projection identity.
  - Builder gating must fail before persistence when a real builder is unavailable.
  - DB schema checks, `pytest`, `ruff`, `app.routes` and `app.openapi()` prove the intended backend-only surface.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | DB schema, loaded config, `pytest`, `app.routes` and `app.openapi()` prove backend-only behavior. |
| Baseline Snapshot | yes | Before and after artifacts prove the intended DB and service delta. |
| Ownership Routing | yes | Model, repository, hash helper, service and audit linkage need canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this projection persistence story. |
| Contract Shape | yes | The persisted projection row has exact required fields and hash rules. |
| Batch Migration | no | No batch conversion is in scope; one Alembic schema migration is in scope. |
| Reintroduction Guard | yes | Fake builders, unfiltered reads and public projection leakage must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | A persisted projection row carries `projection_hash`. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/projections/test_projection_persistence.py`. |
| AC2 | Equal canonical payloads keep one stable hash. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/projections/test_projection_hash.py`. |
| AC3 | Changed canonical payload changes the hash. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/projections/test_projection_hash.py`. |
| AC4 | Source versions are retained. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/projections/test_projection_persistence.py`. |
| AC5 | Access reads require scoped filters. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/unit/projections/test_projection_access.py`. |
| AC6 | Builder absence blocks persistence. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/unit/projections/test_projection_builder_gate.py`. |
| AC7 | Narrative audit linkage is explicit. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks `narrative_answer_audit_v1` and `projection_hash`. |
| AC8 | DB migration exposes the required schema. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/integration/test_projection_persistence_schema.py`. |
| AC9 | Public API runtime surface stays unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`. |
| AC10 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-264 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect existing projection contracts, chart persistence, AI narrative input and builder owners before editing. (AC: AC1, AC6, AC7)
- [ ] Task 2: Select the first real builder-backed projection type or stop with a recorded blocker. (AC: AC6)
- [ ] Task 3: Add the persisted projection model with required fields and French module/class docstrings. (AC: AC1, AC4, AC8)
- [ ] Task 4: Add one Alembic migration for the projection persistence table and indexes. (AC: AC1, AC4, AC8)
- [ ] Task 5: Add a canonical JSON SHA-256 hash helper for projection payloads. (AC: AC2, AC3)
- [ ] Task 6: Add repository and service methods for filtered writes and reads. (AC: AC1, AC4, AC5)
- [ ] Task 7: Enforce builder gating before persistence and forbid synthetic projection payloads. (AC: AC6)
- [ ] Task 8: Document or type the `narrative_answer_audit_v1` linkage to persisted projection identity. (AC: AC7)
- [ ] Task 9: Add unit and integration tests for hash, persistence, access, builder gate and schema. (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC8)
- [ ] Task 10: Persist validation, schema and surface evidence under the CS-264 evidence folder. (AC: AC9, AC10)

## Files to Inspect First

- `_story_briefs/cs-264-implement-projection-persistence-and-projection-hash.md` - source brief.
- `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md` - stable hashable projection dependency.
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md` - audit hash dependency.
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/00-story.md` - future persist command dependency.
- `backend/app/infra/db/models/chart_result.py` - existing chart result persistence pattern.
- `backend/app/infra/db/repositories/chart_result_repository.py` - existing chart result repository pattern.
- `backend/app/infra/db/models/llm/llm_audit.py` - existing timestamp mixin and audit model pattern.
- `backend/migrations/env.py` - Alembic metadata loading pattern.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` - current builder owner.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output only.

## Runtime Source of Truth

- Primary source of truth:
  - SQLAlchemy metadata and migrated DB schema for the persisted projection table.
  - The selected real projection builder for payload production.
  - Repository/service tests for type and role filtered reads.
  - `app.routes`, `app.openapi()`, loaded config and `pytest` for backend-only runtime checks.
- Secondary evidence:
  - Targeted `rg` scans for `projection_hash`, `source_versions`, fake builder wording and narrative audit linkage.
- Static scans alone are not sufficient because:
  - schema creation, hash determinism and access filtering must be proven at runtime.

## Contract Shape

- Contract type:
  - Backend persisted projection record and service contract.
- Fields:
  - `id`: internal persisted projection identifier.
  - `chart_id`: chart identifier associated with the generated projection.
  - `user_id`: owner identifier used for access filtering.
  - `projection_type`: canonical projection identifier such as `structured_facts_v1`.
  - `projection_version`: projection contract version persisted with the payload.
  - `projection_hash`: SHA-256 hex digest of the canonical projection payload.
  - `payload`: canonical JSON projection payload returned by a real builder.
  - `source_versions`: JSON object containing source contract, runtime and reference versions.
  - `source`: canonical builder or service source identifier.
  - `generated_at`: timezone-aware UTC generation timestamp.
- Required fields:
  - `chart_id`
  - `user_id`
  - `projection_type`
  - `projection_version`
  - `projection_hash`
  - `payload`
  - `source_versions`
  - `source`
  - `generated_at`
- Optional fields:
  - none for the initial persisted row contract.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - DB and service JSON names stay `projection_type`, `projection_version`, `projection_hash`, `payload`, `source_versions`, `source`.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose a new projection persistence route from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-264-implement-projection-persistence-and-projection-hash.md`
  - `backend/app/infra/db/models/chart_result.py`
  - `backend/app/infra/db/repositories/chart_result_repository.py`
  - `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`
- Comparison after implementation:
  - `_condamad/stories/CS-264-projection-persistence-projection-hash/evidence/schema-after.txt`
  - `_condamad/stories/CS-264-projection-persistence-projection-hash/evidence/validation.txt`
  - `_condamad/stories/CS-264-projection-persistence-projection-hash/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended application delta is backend persistence, service/hash logic, migration and tests for projection persistence.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Projection DB model | `backend/app/infra/db/models/projection_persistence.py` | API routers or frontend |
| Projection repository | `backend/app/infra/db/repositories/projection_repository.py` | domain builder modules |
| Canonical hash helper | `backend/app/domain/astrology/projections/projection_hash.py` | route handler or DB model method |
| Persistence service | `backend/app/services/projection_persistence_service.py` | projection builder implementation |
| Builder output | selected real builder module | persistence service as fake builder |
| Narrative audit linkage | `backend/app/domain/astrology/interpretation/**` or docs contract | client response payloads |
| Evidence artifacts | `_condamad/stories/CS-264-projection-persistence-projection-hash/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse existing chart result persistence and repository patterns instead of creating a second DB access style.
- Reuse existing `source_versions` vocabulary from `AINarrativeSourceVersions`.
- Reuse `projection_hash` requirements from CS-256 and CS-259 instead of inventing a separate hash field.
- Reuse the selected real projection builder output without duplicating builder logic in the persistence service.
- Keep one canonical hash helper for all persisted projection types.
- Do not add external packages, fake builders, duplicate projection registries, frontend helpers or generated clients.

## No Legacy / Forbidden Paths

- No legacy projection persistence path may be added.
- No compatibility projection store may be added beside the canonical table.
- No fallback branch may persist a synthetic payload when a real builder is unavailable.
- Do not create aliases, shims, wrappers or parallel documents for the same persisted projection contract.
- Do not expose internal projection payloads through a public API route in this story.
- Forbidden surfaces:
  - `frontend/src/**`
  - public API route registration
  - generated OpenAPI clients
  - prompt/provider implementation
  - fake projection builders
  - unfiltered repository reads

## Reintroduction Guard

- Guard target:
  - persisted projections cannot omit `projection_hash`, `projection_version`, `source_versions`, `source` or `generated_at`;
  - canonical hash logic cannot depend on dict insertion order or non-deterministic JSON output;
  - repository reads cannot bypass projection type and role or access scope filters;
  - fake builders and synthetic projection payloads cannot satisfy persistence tests;
  - public API routes and frontend files cannot be introduced by this story.
- Guard mechanism:
  - unit tests for hash stability and divergence;
  - integration test for migrated DB schema;
  - repository/service tests for access filtering and builder gating;
  - `app.routes` and `app.openapi()` neutrality checks;
  - targeted `rg` scans for forbidden fake-builder patterns and narrative audit linkage.
- Guard owner:
  - backend projection persistence model, repository, service and hash helper;
  - `_condamad/stories/CS-264-projection-persistence-projection-hash/evidence/validation.txt`;
  - `_condamad/stories/CS-264-projection-persistence-projection-hash/evidence/schema-after.txt`.
- Guard evidence:
  - `pytest -q backend/tests/unit/projections/test_projection_hash.py`;
  - `pytest -q backend/tests/unit/projections/test_projection_persistence.py`;
  - `pytest -q backend/tests/unit/projections/test_projection_access.py`;
  - `pytest -q backend/tests/unit/projections/test_projection_builder_gate.py`;
  - `pytest -q backend/tests/integration/test_projection_persistence_schema.py`;
  - `python -c "from app.main import app; assert 'projection_hash' not in str(app.openapi())"`;
  - `python -c "from app.main import app; assert all('projection' not in getattr(r, 'path', '') for r in app.routes)"`.

## Regression Guardrails

Scope vector:

- backend-domain persistence: yes;
- DB model and Alembic migration: yes;
- backend service and repository: yes;
- projection hash and audit linkage: yes;
- public API route change: no;
- frontend implementation: no;
- auth implementation, i18n, style and build tooling: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | Backend ownership stays in canonical app paths. | `git status`; targeted `pytest`. |
| RG-022 | Validation paths must be executable for backend tests. | `pytest`; persisted validation. |
| Registry gap | No exact projection persistence guardrail exists in resolver output. | Story-local schema, hash and access guards. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is out of scope because this story does not change entitlement docs.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation output | `_condamad/stories/CS-264-projection-persistence-projection-hash/evidence/validation.txt` | Keep test and lint transcript. |
| Schema output | `_condamad/stories/CS-264-projection-persistence-projection-hash/evidence/schema-after.txt` | Prove migrated table fields and indexes. |
| Application surface status | `_condamad/stories/CS-264-projection-persistence-projection-hash/evidence/app-surface-status.txt` | Prove routes stay unchanged. |
| Source checklist | `_condamad/stories/CS-264-projection-persistence-projection-hash/evidence/source-checklist.md` | Record builder and dependency checks. |
| Review output | `_condamad/stories/CS-264-projection-persistence-projection-hash/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this projection persistence story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch conversion or multi-step data migration is in scope; one Alembic schema migration is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/projections/projection_hash.py` - canonical hash helper.
- `backend/app/infra/db/models/projection_persistence.py` - persisted projection model.
- `backend/app/infra/db/models/__init__.py` - model import for metadata registration.
- `backend/app/infra/db/repositories/projection_repository.py` - filtered persistence access.
- `backend/app/services/projection_persistence_service.py` - builder-gated persistence orchestration.
- `backend/migrations/versions/20260524_0138_create_projection_persistence.py` - schema migration.
- `_condamad/stories/CS-264-projection-persistence-projection-hash/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-264-projection-persistence-projection-hash/evidence/schema-after.txt` - schema proof.
- `_condamad/stories/CS-264-projection-persistence-projection-hash/evidence/source-checklist.md` - source and builder proof.

Likely tests:

- `backend/tests/unit/projections/test_projection_hash.py` - canonical hash stability and divergence.
- `backend/tests/unit/projections/test_projection_persistence.py` - persisted fields and source versions.
- `backend/tests/unit/projections/test_projection_access.py` - type and role filtering.
- `backend/tests/unit/projections/test_projection_builder_gate.py` - real builder requirement.
- `backend/tests/integration/test_projection_persistence_schema.py` - migrated DB schema contract.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no public API route is implemented.
- prompt and provider files - out of scope; no LLM generation behavior changes.
- generated OpenAPI clients - out of scope; no generated client is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `pytest -q backend/tests/unit/projections/test_projection_hash.py`
- VC3: `pytest -q backend/tests/unit/projections/test_projection_persistence.py`
- VC4: `pytest -q backend/tests/unit/projections/test_projection_access.py`
- VC5: `pytest -q backend/tests/unit/projections/test_projection_builder_gate.py`
- VC6: `pytest -q backend/tests/integration/test_projection_persistence_schema.py`
- VC7: `python -c "from app.main import app; assert 'projection_hash' not in str(app.openapi())"`
- VC8: `python -c "from app.main import app; assert all('projection' not in getattr(r, 'path', '') for r in app.routes)"`
- VC9: `rg -n "projection_hash|source_versions|narrative_answer_audit_v1" backend/app backend/tests`
- VC10: `rg -n "fake projection|placeholder projection|synthetic projection" backend/app backend/tests`
- VC11: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-264-projection-persistence-projection-hash/evidence/validation.txt').exists()"`
- VC12: `ruff format .`
- VC13: `ruff check .`
- VC14: `pytest -q`
- VC15: `git status --short -- backend/app backend/tests backend/migrations frontend/src`

Before VC2 through VC14, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The hash could depend on non-canonical JSON ordering and break audit repeatability.
- Persistence could store a payload without source versions, making narrative answer audit evidence incomplete.
- A service could create a synthetic projection when the real builder dependency is missing.
- Repository reads could omit type or role filtering and expose internal projection payloads too broadly.
- A backend persistence story could drift into public API, frontend, back-office or prompt/provider work.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments and public or non-trivial docstrings in French for new or significantly modified backend files.
- Start by proving whether a real builder exists for the selected projection type.
- Persist only outputs from real builders and record a blocker instead of creating a synthetic projection.
- Keep public API routes, OpenAPI output, frontend and generated clients unchanged.
- Persist the required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-264-implement-projection-persistence-and-projection-hash.md`
- `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md`
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md`
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/00-story.md`
- `backend/app/infra/db/models/chart_result.py`
- `backend/app/infra/db/repositories/chart_result_repository.py`
- `backend/app/infra/db/models/llm/llm_audit.py`
- `backend/migrations/env.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`
- `_condamad/stories/regression-guardrails.md`
