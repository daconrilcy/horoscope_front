# Story CS-288 narrative-answer-audit-v1-persistence: Implement narrative_answer_audit_v1 Persistence
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-288-implement-narrative-answer-audit-v1-persistence.md`.
- Related dependency: CS-259 defines the target `narrative_answer_audit_v1` fields and grounding vocabulary.
- Related dependency: CS-262 defines the mandatory audit-before-create rule for prompt, answer and provider storage.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: audited narrative answers need one persisted backend record before admin APIs can read real data.
- Source-alignment evidence: PASS; the story preserves persistence, CS-259 field coverage, CS-262 reuse and privacy stakes.

## Objective

Implement backend persistence for `narrative_answer_audit_v1` by extending verified existing storage or creating one canonical storage owner.

The implementation must persist answer identity, answer category, chart, user, plan, versions, hashes, prompt provenance, provider,
model, `grounding_status` and `evidence_refs` linkage without exposing this audit data to clients.

## Target State

- `narrative_answer_audit_v1` records can be created and read through a backend persistence owner.
- The implementation reuses `UserNatalInterpretationModel`, `LlmCallLogModel` and existing LLM prompt storage when they fit the field.
- A single canonical storage owner covers CS-259 mandatory fields without creating a duplicate answer-audit table beside an adequate owner.
- `answer_type` supports exactly `basic`, `premium`, `long`, `sensitive` and `free_short`.
- Versions, hashes, prompt reference, prompt snapshot policy, provider, model and `grounding_status` are persisted.
- `evidence_refs` has a prepared persisted link shape for later validation without implementing full proof validation.
- Sensitive prompt, provider and model data follows existing sensitive-data masking or isolation policy.
- Creation and read tests prove the persistence behavior.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-288-implement-narrative-answer-audit-v1-persistence.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-288`.
- Evidence 3: `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md` - target audit contract read.
- Evidence 4: `_condamad/stories/CS-262-audit-existing-prompt-version-answer-id-storage/00-story.md` - reuse-before-create rule read.
- Evidence 5: `backend/app/infra/db/models/user_natal_interpretation.py` - existing answer storage has user, chart and prompt version fields.
- Evidence 6: `backend/app/infra/db/models/llm/llm_observability.py` - existing LLM logs have model, provider metadata and input hash.
- Evidence 7: `backend/app/core/sensitive_data.py` - sensitive LLM field masking policy exists for provider, model and prompt identifiers.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output and targeted ID lookup only.
- Evidence 9: `resolve_guardrails.py` - scoped resolver run for backend persistence, SQLAlchemy, Alembic and sensitive-data surfaces.
- Repository structure alert: no expected backend root is absent; implementation may still create scoped files listed below.
- Source-alignment review result: PASS; no brief stake was narrowed into API work, UI work or documentation-only work.

## Domain Boundary

- Domain: backend-persistence
- In scope:
  - SQLAlchemy persistence for `narrative_answer_audit_v1`.
  - Repository or service functions for creating and reading answer audit records.
  - Alembic migration or existing schema extension required by the final storage design.
  - `answer_id`, `answer_type`, `chart_id`, `user_id`, `plan`, versions, hashes, prompt, provider, model and `grounding_status`.
  - Prepared persisted `evidence_refs` linkage without full evidence validation.
  - Unit and integration tests for creation, read, reuse of existing storage and sensitive-data masking or isolation.
- Out of scope:
  - Frontend UI, public API exposure, admin API routes, auth, i18n, styling, build tooling and generated clients.
  - Full validation of `evidence_refs`, final GDPR retention decision, prompt editing and provider-call behavior.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No public endpoint, admin endpoint, OpenAPI schema or response serializer for audit reads.
  - No second persistence path when an existing storage owner covers the field contract.
  - No final retention policy decision beyond using the current masking or isolation policy.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend persistence and schema-extension story.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add or adapt only backend persistence surfaces required for `narrative_answer_audit_v1`.
  - Reuse existing answer, LLM call, prompt and sensitive-data owners before creating a new storage owner.
  - Keep public API, admin API, frontend, auth, i18n, style and build tooling unchanged.
  - Persist only the prepared `evidence_refs` link shape; full proof validation remains out of scope.
  - Keep client-facing projections free of prompt payloads, provider internals, model internals and audit rows.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-262 implementation evidence proves final GDPR retention is unresolved for the chosen storage shape.
- Additional validation rules:
  - The final storage design must cover every mandatory CS-259 field listed in this story.
  - The final storage design must not create a duplicate audit table when `UserNatalInterpretationModel` can be extended cleanly.
  - `answer_type` must allow only `basic`, `premium`, `long`, `sensitive` and `free_short`.
  - `grounding_status` must allow only `grounded`, `partial`, `ungrounded`, `rejected` and `not_checked`.
  - Creation and read tests must use persisted rows, not in-memory-only DTOs.
  - Sensitive prompt/provider/model data must be masked, referenced or isolated under the existing policy.
  - DB schema checks, `pytest`, `ruff`, loaded SQLAlchemy metadata and targeted `rg` scans prove the final state.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | SQLAlchemy metadata, DB schema inspection, repository reads and `pytest` prove persisted behavior. |
| Baseline Snapshot | yes | Before and after schema evidence prove the only intended persistence surface delta. |
| Ownership Routing | yes | Existing answer, LLM call, prompt and audit storage owners must not be duplicated. |
| Allowlist Exception | no | No allowlist handling is authorized for this persistence story. |
| Contract Shape | yes | The stored record has exact fields, enums, hashes, prompt evidence and privacy rules. |
| Batch Migration | yes | Schema extension and backfill planning are required for existing narrative rows. |
| Reintroduction Guard | yes | Duplicate storage, client exposure and unmasked sensitive fields must stay absent. |
| Persistent Evidence | yes | Schema, validation and source-decision artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Existing storage is classified before creation. | Evidence profile: ast_architecture_guard; `pytest` architecture boundary test. |
| AC2 | Audit records are persisted. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_narrative_answer_audit_repository.py`. |
| AC3 | Audit records are readable. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_narrative_answer_audit_repository.py`. |
| AC4 | CS-259 identity fields are stored. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_narrative_answer_audit_model.py`. |
| AC5 | CS-259 hash fields are stored. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_narrative_answer_audit_model.py`. |
| AC6 | LLM provenance fields are stored. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_narrative_answer_audit_model.py`. |
| AC7 | `answer_type` values are constrained. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_narrative_answer_audit_model.py`. |
| AC8 | `grounding_status` values are constrained. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_narrative_answer_audit_model.py`. |
| AC9 | `evidence_refs` linkage is persisted. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_narrative_answer_audit_repository.py`. |
| AC10 | Sensitive fields follow policy. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/unit/test_narrative_answer_audit_sensitive_data.py`. |
| AC11 | Duplicate storage is blocked. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans backend for parallel audit owners. |
| AC12 | Schema migration is validated. | Evidence profile: baseline_before_after_diff; `pytest -q backend/tests/integration/test_narrative_answer_audit_schema.py`. |
| AC13 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-288 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-259, CS-262 and existing answer, LLM call, prompt and sensitive-data owners before editing. (AC: AC1)
- [ ] Task 2: Decide the canonical persistence owner and record the reuse decision in story evidence. (AC: AC1, AC11, AC13)
- [ ] Task 3: Add or adapt the SQLAlchemy model fields for the CS-259 identity contract. (AC: AC4, AC12)
- [ ] Task 4: Add or adapt version, hash, prompt, provider, model and `grounding_status` persistence. (AC: AC5, AC6, AC8, AC12)
- [ ] Task 5: Add the prepared persisted `evidence_refs` link shape without full proof validation. (AC: AC9, AC12)
- [ ] Task 6: Add repository or service create/read operations under the existing backend ownership boundary. (AC: AC2, AC3)
- [ ] Task 7: Apply sensitive-data masking or isolation for prompt, provider and model fields. (AC: AC10)
- [ ] Task 8: Add Alembic migration and schema validation for the chosen persistence shape. (AC: AC12)
- [ ] Task 9: Add tests for create, read, field constraints, schema, duplicate-storage guard and sensitive-data behavior. (AC: AC2, AC3, AC7, AC10)
- [ ] Task 10: Persist validation transcripts, schema snapshots and the storage decision under the CS-288 evidence folder. (AC: AC13)

## Files to Inspect First

- `_story_briefs/cs-288-implement-narrative-answer-audit-v1-persistence.md` - source brief.
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md` - target field and status contract.
- `_condamad/stories/CS-262-audit-existing-prompt-version-answer-id-storage/00-story.md` - reuse-before-create dependency.
- `backend/app/infra/db/models/user_natal_interpretation.py` - existing persisted narrative answer owner.
- `backend/app/infra/db/models/llm/llm_observability.py` - existing LLM call, model, provider and hash owner.
- `backend/app/infra/db/models/llm/llm_prompt.py` - prompt version storage owner.
- `backend/app/infra/db/repositories/llm/prompting_repository.py` - existing prompt DB access owner.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - current narrative answer write/read service.
- `backend/app/core/sensitive_data.py` - existing sensitive-data masking policy.
- `backend/migrations/**` - schema history and migration destination.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - SQLAlchemy metadata for the final model and table columns.
  - Alembic migration state for schema creation or extension.
  - Repository or service tests that insert and read persisted audit rows.
  - DB schema inspection in `pytest -q backend/tests/integration/test_narrative_answer_audit_schema.py`.
  - Existing sensitive-data policy in `backend/app/core/sensitive_data.py`.
- Secondary evidence:
  - Targeted `rg` scans for duplicate storage owners and unauthorized client/API exposure.
  - Persisted source-decision evidence under `_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/evidence/`.
- Static scans alone are not sufficient because:
  - persistence must be proven through SQLAlchemy metadata, migrated schema and persisted create/read behavior.

## Contract Shape

- Contract type:
  - Backend SQLAlchemy persistence contract for `narrative_answer_audit_v1`.
- Fields:
  - `answer_id`: stable narrative answer identifier.
  - `answer_type`: one of `basic`, `premium`, `long`, `sensitive` or `free_short`.
  - `chart_id`: chart identifier used for the audited answer.
  - `user_id`: user identifier associated with the answer.
  - `plan`: commercial plan at generation time.
  - `projection_version`: upstream projection version.
  - `projection_hash`: stable hash of the audited projection payload.
  - `llm_input_version`: AI input contract version.
  - `llm_input_hash`: stable hash of the LLM input payload.
  - `prompt_version`: prompt contract version or prompt version identifier.
  - `prompt_ref`: stable reference to retained prompt material when full prompt text is isolated.
  - `prompt_snapshot_ref`: persisted snapshot reference or isolated snapshot payload pointer.
  - `provider`: provider identifier stored or isolated under sensitive-data policy.
  - `model`: model identifier stored or isolated under sensitive-data policy.
  - `grounding_status`: one of `grounded`, `partial`, `ungrounded`, `rejected` or `not_checked`.
  - `evidence_refs`: persisted structured link list prepared for later proof validation.
  - `created_at`: UTC creation timestamp.
- Required fields:
  - `answer_id`
  - `answer_type`
  - `chart_id`
  - `user_id`
  - `plan`
  - `projection_version`
  - `projection_hash`
  - `llm_input_version`
  - `llm_input_hash`
  - `prompt_version`
  - `provider`
  - `model`
  - `grounding_status`
  - `evidence_refs`
  - `created_at`
- Optional fields:
  - `prompt_ref`
  - `prompt_snapshot_ref`
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - persisted field names stay snake_case and match CS-259 terminology.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must stay unchanged for `narrative_answer_audit_v1`.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-288-implement-narrative-answer-audit-v1-persistence.md`
  - `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md`
  - `_condamad/stories/CS-262-audit-existing-prompt-version-answer-id-storage/00-story.md`
  - scoped model inventory for `UserNatalInterpretationModel` and `LlmCallLogModel`
  - current DB schema snapshot for candidate tables
- Comparison after implementation:
  - final SQLAlchemy metadata snapshot for the chosen audit persistence owner
  - final DB schema snapshot for migrated audit persistence columns or table
  - final source-decision artifact explaining reuse versus new canonical storage
  - final validation transcript under the CS-288 evidence folder
- Expected invariant:
  - The only intended surface delta is backend persistence, migration, tests and CONDAMAD evidence for `narrative_answer_audit_v1`.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Persisted answer identity | existing answer storage or one audit model | duplicate answer-audit model |
| LLM call provenance | `backend/app/infra/db/models/llm/llm_observability.py` or linked audit owner | public API serializers |
| Prompt version provenance | existing prompt model or linked audit owner | prompt template files |
| Audit create/read behavior | backend infra repository or narrow service owner | API router business logic |
| Sensitive field policy | `backend/app/core/sensitive_data.py` and isolated storage policy | client projections |
| Schema migration | `backend/migrations/**` | ad hoc runtime `create_all` |
| Evidence artifacts | `_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse CS-259 field names and grounding vocabulary.
- Reuse the CS-262 audit-before-create rule before adding a table, model, repository or service.
- Reuse `UserNatalInterpretationModel` for answer persistence linkage when it is the clean owner for answer rows.
- Reuse `LlmCallLogModel` and LLM prompt models for call, prompt, provider, model and input hash provenance when suitable.
- Keep one canonical persistence path for `narrative_answer_audit_v1`.
- Do not add external packages, generated clients, frontend helpers, public routes, admin routes, prompt templates or provider calls.

## No Legacy / Forbidden Paths

- No legacy audit storage path may be added for this endpoint-independent persistence.
- No compatibility storage path may bypass the canonical `narrative_answer_audit_v1` owner.
- No fallback storage branch may store narrative answers without audit metadata.
- Do not create aliases, shims, wrappers or parallel repositories for the same audit persistence.
- Do not place prompt payloads, provider internals, model internals, technical proof fields or audit rows inside client-facing projections.
- Forbidden surfaces:
  - `frontend/src/**`
  - public API routers
  - admin API routers
  - prompt template files
  - generated OpenAPI clients
  - duplicate audit storage beside an adequate existing owner

## Reintroduction Guard

- Guard target:
  - narrative answers cannot be persisted without CS-259 identity, version, hash, prompt, provider, model and grounding fields;
  - `answer_type` cannot accept values outside `basic`, `premium`, `long`, `sensitive` and `free_short`;
  - `grounding_status` cannot accept values outside `grounded`, `partial`, `ungrounded`, `rejected` and `not_checked`;
  - duplicate storage cannot appear while an existing owner covers the same responsibility;
  - public API, admin API and frontend surfaces cannot expose audit rows from this story.
- Guard mechanism:
  - SQLAlchemy metadata tests for required columns, enum values and relationships;
  - migrated DB schema tests for final columns, indexes and constraints;
  - repository integration tests for create and read;
  - targeted `rg` scans for duplicate owners and unauthorized API/client exposure;
  - persisted source-decision evidence under the CS-288 evidence folder.
- Guard owner:
  - `backend/app/infra/db/models/**` final chosen persistence owner;
  - `backend/app/infra/db/repositories/**` or `backend/app/services/**` final create/read owner;
  - `backend/tests/**` narrative answer audit persistence tests.
- Guard evidence:
  - `pytest -q backend/tests/unit/test_narrative_answer_audit_model.py`;
  - `pytest -q backend/tests/integration/test_narrative_answer_audit_repository.py`;
  - `pytest -q backend/tests/integration/test_narrative_answer_audit_schema.py`;
  - `rg -n "NarrativeAnswerAudit|narrative_answer_audit" backend/app backend/tests`.

## Regression Guardrails

Scope vector:

- backend persistence: yes;
- SQLAlchemy model and repository/service owner: yes;
- Alembic migration and DB schema: yes;
- LLM prompt version storage referenced: yes;
- public API, admin API and frontend implementation: no;
- auth, i18n, style and build tooling: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | Backend app paths keep business logic out of route modules. | `rg`; targeted `pytest`. |
| Registry gap | No exact `narrative_answer_audit_v1` persistence guardrail exists in resolver output. | Schema tests and duplicate-owner scan. |

Non-applicable examples:

- RG-022 prompt-generation validation paths are out of scope because this story changes persistence, not active prompt-generation plans.
- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is out of scope because this story targets audit persistence, not entitlement policy.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Source decision | `_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/evidence/storage-decision.md` | Record reuse versus new storage choice. |
| Schema before snapshot | `_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/evidence/schema-before.json` | Capture candidate schema before work. |
| Schema after snapshot | `_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/evidence/schema-after.json` | Capture final audit schema. |
| Validation output | `_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/evidence/validation.txt` | Keep lint, tests and targeted scans. |
| Duplicate owner scan | `_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/evidence/duplicate-owner-scan.txt` | Prove no parallel storage path. |
| Review output | `_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this persistence story.

## Batch Migration Plan

- Batch migration plan: active
- Migration scope:
  - Add or extend only the chosen canonical persistence owner for `narrative_answer_audit_v1`.
  - Add indexes or constraints required for `answer_id`, `user_id`, `chart_id`, `answer_type` and `created_at` reads.
  - Backfill strategy must be explicit for existing narrative rows with missing audit metadata.

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | User answer rows | audit owner | repo reads | repo/schema | `rg` owner scan | CS-259 gap |
| 2 | LLM call logs | audit provenance | create flow | model/integration | no parallel repo | no persisted link |
| 3 | no `evidence_refs` | persisted refs | audit reads | refs integration | no API serializer | full validation requested |

- Stop condition:
  - schema tests, repository tests and duplicate-owner scans pass with one canonical storage owner.

## Expected Files to Modify

Likely files:

- `backend/app/infra/db/models/user_natal_interpretation.py` - candidate answer storage extension.
- `backend/app/infra/db/models/llm/narrative_answer_audit.py` - possible canonical audit model only after reuse decision.
- `backend/app/infra/db/models/llm/__init__.py` - model registration for a new canonical model.
- `backend/app/infra/db/repositories/llm/narrative_answer_audit_repository.py` - create/read persistence owner.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - narrow integration point for audit creation.
- `backend/app/core/sensitive_data.py` - masking or isolation registration for new sensitive fields.
- `backend/migrations/**` - Alembic schema migration for the final storage design.
- `_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/evidence/**` - persisted implementation evidence.

Likely tests:

- `backend/tests/unit/test_narrative_answer_audit_model.py` - field, enum and sensitive-data constraints.
- `backend/tests/unit/test_narrative_answer_audit_sensitive_data.py` - masking or isolation policy.
- `backend/tests/integration/test_narrative_answer_audit_repository.py` - create and read behavior.
- `backend/tests/integration/test_narrative_answer_audit_schema.py` - migrated DB schema checks.
- `backend/tests/architecture/test_narrative_answer_audit_persistence_boundary.py` - duplicate-owner and API exposure guard.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- public API routers - out of scope; no client route is touched.
- admin API routers - out of scope; no admin API is implemented.
- prompt template files - out of scope; prompt content is not changed.
- generated OpenAPI clients - out of scope; no API contract is exposed.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `. .\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `pytest -q tests/unit/test_narrative_answer_audit_model.py`
- VC6: `pytest -q tests/unit/test_narrative_answer_audit_sensitive_data.py`
- VC7: `pytest -q tests/integration/test_narrative_answer_audit_repository.py`
- VC8: `pytest -q tests/integration/test_narrative_answer_audit_schema.py`
- VC9: `pytest -q tests/architecture/test_narrative_answer_audit_persistence_boundary.py`
- VC10: `pytest -q`
- VC11: `rg -n "NarrativeAnswerAudit|narrative_answer_audit" app tests`
- VC12: `rg -n "answer_id|answer_type|projection_hash|llm_input_hash|grounding_status|evidence_refs" app tests`
- VC13: `python -c "from pathlib import Path; p=Path('../_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/evidence/validation.txt'); assert p.exists()"`
- VC14: `python -c "from pathlib import Path; p=Path('../_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/evidence/schema-after.json'); assert p.exists()"`
- VC15: `python -c "from pathlib import Path; p=Path('../_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/evidence/storage-decision.md'); assert p.exists()"`
- VC16: `python -c "from pathlib import Path; p=Path('../_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/evidence/duplicate-owner-scan.txt'); assert p.exists()"`
- VC17: `python -c "from pathlib import Path; p=Path('../_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/evidence/schema-before.json'); assert p.exists()"`
- VC18: `git status --short -- app tests migrations ../frontend/src`

Before VC3 through VC17, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The implementation could duplicate answer audit storage instead of extending an adequate existing owner.
- Existing narrative rows could receive incomplete backfill semantics for answer type, prompt version or grounding status.
- Prompt payloads, provider internals or model identifiers could become client-visible through an accidental serializer path.
- `evidence_refs` could be treated as fully validated despite this story only preparing its persisted link shape.
- Schema updates could rely on runtime `create_all` instead of Alembic migration and migrated schema evidence.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments and public or non-trivial docstrings in French for new or significantly modified backend files.
- Start by recording the reuse decision against `UserNatalInterpretationModel`, `LlmCallLogModel` and prompt models.
- Prefer extending an adequate existing owner over creating a new storage owner.
- Persist required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-288-implement-narrative-answer-audit-v1-persistence.md`
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md`
- `_condamad/stories/CS-262-audit-existing-prompt-version-answer-id-storage/00-story.md`
- `backend/app/infra/db/models/user_natal_interpretation.py`
- `backend/app/infra/db/models/llm/llm_observability.py`
- `backend/app/infra/db/models/llm/llm_prompt.py`
- `backend/app/infra/db/repositories/llm/prompting_repository.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/core/sensitive_data.py`
- `_condamad/stories/regression-guardrails.md`
