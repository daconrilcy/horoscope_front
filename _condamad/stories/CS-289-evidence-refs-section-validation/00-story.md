# Story CS-289 evidence-refs-section-validation: Implement evidence_refs Section Validation
Status: done

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-289-implement-evidence-refs-validation.md`.
- Related dependency: CS-260 defines the `evidence_refs` contract and source/hash requirements.
- Related dependency: CS-288 prepares `narrative_answer_audit_v1` persistence and persisted `evidence_refs` linkage.
- Related dependency: CS-264 defines `projection_hash` as the stable projection proof anchor.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: narrative answers can carry decorative `evidence_refs` unless section validation proves authorized hashed sources.
- Source-alignment evidence: PASS; ACs cover decorative rejection, hash-backed acceptance, section status and audit integration.

## Objective

Implement backend validation of `evidence_refs` per narrative section so answer audits can classify each section from real authorized proofs.

The implementation must reject decorative references, accept only validated hashed sources, distinguish no-proof-required sections from invalid
sections, and integrate the result with `narrative_answer_audit_v1` without exposing technical proof details to clients.

## Target State

- A canonical backend validator evaluates `evidence_refs` section by section.
- Each `evidence_ref` must resolve to an authorized source kind from CS-260.
- A valid reference proves a link to a persisted projection hash or hashed LLM input source.
- Decorative strings, unknown source kinds, missing source rows and hash mismatches are rejected.
- Section validation produces explicit statuses for `grounded`, `partial`, `ungrounded` and no-proof-required sections.
- `narrative_answer_audit_v1` stores or receives the section validation outcome through the canonical audit owner.
- Existing provenance, projection hash and audit persistence owners are reused before any new helper is created.
- No frontend, admin UI, public API, astrology calculation, prompt content or provider behavior is changed.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-289-implement-evidence-refs-validation.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-289`.
- Evidence 3: `_condamad/stories/CS-260-evidence-refs-contract-validation/00-story.md` - upstream evidence contract read.
- Evidence 4: `_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/00-story.md` - audit persistence dependency read.
- Evidence 5: `_condamad/stories/CS-264-projection-persistence-projection-hash/00-story.md` - projection hash dependency read.
- Evidence 6: `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` - existing source vocabulary inspected.
- Evidence 7: `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` - AI narrative input owner inspected.
- Evidence 8: targeted `rg` found existing `evidence_refs` only in doctrine governance, not narrative answer audit validation.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output and targeted IDs only.
- Evidence 10: `resolve_guardrails.py` - scoped resolver run for backend-domain validation, hash and narrative audit surfaces.
- Repository structure alert: no expected backend root is absent; implementation may create scoped files listed below.
- Source-alignment review result: PASS; no brief stake was narrowed into API, UI, documentation-only or calculation work.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend validator for section-level `evidence_refs`.
  - Authorized source checks for hashed projections and hashed LLM input sources.
  - Section validation status calculation for `grounded`, `partial`, `ungrounded` and no-proof-required sections.
  - Integration with `narrative_answer_audit_v1` through its canonical persistence or service owner.
  - Unit and integration tests for absent proof, invalid proof, valid proof and audit linkage.
- Out of scope:
  - Frontend UI, admin UI, public API, auth, i18n, styling, build tooling and generated clients.
  - Semantic scoring engine, client exposure of proof internals, prompt content changes, provider calls and astrology calculations.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No public endpoint, admin endpoint, OpenAPI schema or response serializer for proof details.
  - No semantic meaning engine beyond source authorization, hash verification and section status aggregation.
  - No astrology calculation, prompt template, LLM provider or narrative renderer rewrite.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend domain validation and audit-integration story.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only backend validation surfaces required for section-level `evidence_refs`.
  - Reuse CS-260 source rules, CS-264 `projection_hash` rules and CS-288 audit persistence before creating new owners.
  - Keep public API, admin API, frontend, DB schema beyond CS-288-owned audit linkage, auth, i18n, style and build tooling unchanged.
  - Keep technical proof metadata internal and absent from client-facing projections.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-288 is not implemented and no canonical audit owner exists to attach section validation results.
- Additional validation rules:
  - The validator must classify every audited narrative section independently.
  - The validator must reject decorative strings that do not resolve to authorized validated sources.
  - Authorized source kinds must align with CS-260 and include hashed projection or hashed LLM input proof anchors.
  - Hash validation must compare the referenced hash with the stored source hash before marking a reference valid.
  - Sections with no proof requirement must not be classified as invalid.
  - Section outcomes must include `grounded`, `partial` and `ungrounded`.
  - Integration tests must prove `narrative_answer_audit_v1` receives section validation results.
  - `pytest`, DB or repository checks, AST guard, `app.routes` and `app.openapi()` prove the final runtime state.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, repository checks, AST guard, `app.routes` and `app.openapi()` prove validation and no API drift. |
| Baseline Snapshot | yes | Before and after evidence proves the intended validator and audit-link delta. |
| Ownership Routing | yes | Evidence validation, source lookup, hash proof and audit persistence need canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this validation story. |
| Contract Shape | yes | Section validation has exact inputs, source kinds, hash anchors, statuses and output shape. |
| Batch Migration | no | No batch migration or multi-step conversion is in scope. |
| Reintroduction Guard | yes | Decorative references, unverified hashes and client proof leakage must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Decorative `evidence_ref` values are rejected. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_evidence_refs_validation.py`. |
| AC2 | Hash-backed projection sources are accepted. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_evidence_refs_validation.py`. |
| AC3 | Hash-backed LLM input sources are accepted. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_evidence_refs_validation.py`. |
| AC4 | Missing proof requirements stay distinct. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_evidence_refs_section_status.py`. |
| AC5 | Invalid section proof is classified. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_evidence_refs_section_status.py`. |
| AC6 | `grounded` status is produced. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_evidence_refs_section_status.py`. |
| AC7 | `partial` status is produced. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_evidence_refs_section_status.py`. |
| AC8 | `ungrounded` status is produced. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_evidence_refs_section_status.py`. |
| AC9 | Audit persists results. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_narrative_answer_audit_evidence_refs.py`. |
| AC10 | API runtime surface stays unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`. |
| AC11 | Parallel validators are blocked. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/architecture/test_evidence_refs_validation_boundary.py`. |
| AC12 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-289 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-260, CS-264, CS-288 and current provenance owners before editing. (AC: AC1, AC2, AC3, AC11)
- [ ] Task 2: Record the reuse decision for source lookup, hash lookup and audit owner in story evidence. (AC: AC11, AC12)
- [ ] Task 3: Add the canonical section-level `evidence_refs` validator under the backend domain owner. (AC: AC1, AC4, AC5)
- [ ] Task 4: Implement authorized source resolution for projection hash and LLM input hash anchors. (AC: AC2, AC3)
- [ ] Task 5: Implement section status aggregation for grounded, partial, ungrounded and no-proof-required results. (AC: AC4, AC6, AC7, AC8)
- [ ] Task 6: Integrate validation results into the canonical `narrative_answer_audit_v1` persistence or service path. (AC: AC9)
- [ ] Task 7: Add architecture guard coverage for one canonical validator and no client/API proof leakage. (AC: AC10, AC11)
- [ ] Task 8: Add unit and integration tests for absent, invalid, valid and audit-linked proof cases. (AC: AC1, AC2, AC3, AC9)
- [ ] Task 9: Persist validation transcript, source decision and runtime surface evidence under the CS-289 evidence folder. (AC: AC10, AC12)

## Files to Inspect First

- `_story_briefs/cs-289-implement-evidence-refs-validation.md` - source brief.
- `_condamad/stories/CS-260-evidence-refs-contract-validation/00-story.md` - evidence refs source contract.
- `_condamad/stories/CS-264-projection-persistence-projection-hash/00-story.md` - projection hash dependency.
- `_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/00-story.md` - audit persistence dependency.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` - source vocabulary owner.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` - narrative input assembly owner.
- `backend/app/infra/db/models/llm/**` - expected audit and LLM input hash persistence owners.
- `backend/app/services/llm_generation/natal/**` - expected narrative answer audit integration point.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - Unit tests for reference validation and section status aggregation.
  - Integration tests proving persisted or service-level `narrative_answer_audit_v1` receives validation results.
  - Repository or DB checks for stored projection hashes and LLM input hashes.
  - AST guard for one canonical validator and no route/client leakage.
  - `app.routes`, `app.openapi()` and `pytest` for runtime surface checks.
- Secondary evidence:
  - Targeted `rg` scans for `evidence_refs`, `projection_hash`, `llm_input_hash` and duplicate validator symbols.
- Static scans alone are not sufficient because:
  - section status, source resolution and hash comparison must be proven by runtime tests.

## Contract Shape

- Contract type:
  - Backend domain validation contract for section-level `evidence_refs`.
- Fields:
  - `section_id`: audited narrative section identifier.
  - `requires_evidence`: boolean deciding whether missing references are invalid.
  - `evidence_refs`: structured references supplied for the section.
  - `source_type`: authorized source kind aligned with CS-260.
  - `source_id`: persisted source identifier.
  - `source_version`: source contract or projection version.
  - `source_hash`: referenced stable hash.
  - `validation_state`: `valid`, `missing_source`, `unsupported_source_type`, `missing_hash` or `hash_mismatch`.
  - `section_status`: `grounded`, `partial`, `ungrounded` or `not_required`.
  - `validation_errors`: bounded internal diagnostics for audit use.
- Required fields:
  - `section_id`
  - `requires_evidence`
  - `evidence_refs`
  - `section_status`
  - `validation_state`
- Optional fields:
  - `validation_errors` for internal audit surfaces.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - backend and audit names stay snake_case and align with `narrative_answer_audit_v1`.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose technical evidence validation internals from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-289-implement-evidence-refs-validation.md`
  - CS-260 `evidence_refs` contract story
  - CS-264 projection hash story
  - CS-288 narrative answer audit persistence story
  - targeted scan of current `evidence_refs` and provenance owners
- Comparison after implementation:
  - `_condamad/stories/CS-289-evidence-refs-section-validation/evidence/validation.txt`
  - `_condamad/stories/CS-289-evidence-refs-section-validation/evidence/source-decision.md`
  - `_condamad/stories/CS-289-evidence-refs-section-validation/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended application delta is backend validation, audit integration, tests and CONDAMAD evidence for `evidence_refs`.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Evidence refs validation | `backend/app/domain/astrology/interpretation/evidence_refs_validation.py` | API routers or frontend |
| Source hash lookup | projection and LLM input persistence owners | duplicated in UI or prompt code |
| Section status aggregation | evidence refs validation owner | narrative renderer text logic |
| Audit result storage | canonical `narrative_answer_audit_v1` repository or service | parallel audit writer |
| Runtime integration | narrow backend service orchestration point | public route handler |
| Evidence artifacts | `_condamad/stories/CS-289-evidence-refs-section-validation/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse CS-260 field names and authorized source vocabulary.
- Reuse CS-264 `projection_hash` calculation and persisted projection identity once implemented.
- Reuse CS-288 `narrative_answer_audit_v1` persistence or service ownership.
- Reuse existing AI narrative input source vocabulary rather than creating another source taxonomy.
- Keep one canonical validator for section-level proof validation.
- Do not add external packages, generated clients, API serializers, frontend helpers, prompt templates or provider calls.

## No Legacy / Forbidden Paths

- No legacy validation path may accept decorative `evidence_refs`.
- No compatibility validation path may bypass source and hash checks.
- No fallback branch may mark a section grounded from a plain string.
- Do not create aliases, shims, wrappers or parallel validators for the same proof contract.
- Do not expose technical proof metadata in client-facing projections.
- Forbidden surfaces:
  - `frontend/src/**`
  - public API routers
  - admin API routers
  - generated OpenAPI clients
  - prompt template files
  - astrology calculation modules
  - duplicate evidence validator modules

## Reintroduction Guard

- Guard target:
  - decorative references cannot validate;
  - valid references must resolve to authorized sources and matching hashes;
  - no-proof-required sections must remain distinct from invalid sections;
  - `grounded`, `partial` and `ungrounded` must be observable in tests;
  - audit integration cannot leak proof internals to client or API surfaces.
- Guard mechanism:
  - unit tests for validation outcomes and section statuses;
  - integration tests for `narrative_answer_audit_v1` linkage;
  - AST guard for canonical validator ownership;
  - `app.routes` and `app.openapi()` neutrality checks;
  - targeted `rg` scans for duplicate validators and proof leakage.
- Guard owner:
  - backend evidence refs validation owner;
  - backend narrative answer audit owner;
  - backend tests listed in this story.
- Guard evidence:
  - `pytest -q backend/tests/unit/test_evidence_refs_validation.py`;
  - `pytest -q backend/tests/unit/test_evidence_refs_section_status.py`;
  - `pytest -q backend/tests/integration/test_narrative_answer_audit_evidence_refs.py`;
  - `pytest -q backend/tests/architecture/test_evidence_refs_validation_boundary.py`;
  - `python -c "from app.main import app; assert 'evidence_refs' not in str(app.openapi())"`.

## Regression Guardrails

Scope vector:

- backend-domain validation: yes;
- narrative answer audit integration: yes;
- projection and LLM input hash proof: yes;
- backend tests and architecture guard: yes;
- public API, admin API and frontend implementation: no;
- DB schema, auth, i18n, style, build tooling and migration: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | Backend ownership stays in canonical app paths. | `rg`; targeted `pytest`. |
| RG-022 | Validation paths must remain executable for backend tests. | `pytest`; persisted validation. |
| Registry gap | No exact `evidence_refs` section-validation guardrail exists in resolver output. | Story-local hash, status and audit guards. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is out of scope because this story targets narrative evidence validation.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Source decision | `_condamad/stories/CS-289-evidence-refs-section-validation/evidence/source-decision.md` | Record reused source and audit owners. |
| Validation output | `_condamad/stories/CS-289-evidence-refs-section-validation/evidence/validation.txt` | Keep lint, tests and targeted scans. |
| Application surface status | `_condamad/stories/CS-289-evidence-refs-section-validation/evidence/app-surface-status.txt` | Prove API and client surfaces stay unchanged. |
| Duplicate validator scan | `_condamad/stories/CS-289-evidence-refs-section-validation/evidence/duplicate-validator-scan.txt` | Prove one canonical validator. |
| Review output | `_condamad/stories/CS-289-evidence-refs-section-validation/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this validation story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/interpretation/evidence_refs_validation.py` - canonical section validator.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` - source vocabulary extension only after reuse decision.
- `backend/app/infra/db/models/llm/**` - audit linkage adjustment owned by CS-288 persistence shape.
- `backend/app/services/llm_generation/natal/**` - narrow validation call before audit persistence.
- `_condamad/stories/CS-289-evidence-refs-section-validation/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-289-evidence-refs-section-validation/evidence/source-decision.md` - reuse decision evidence.
- `_condamad/stories/CS-289-evidence-refs-section-validation/evidence/app-surface-status.txt` - API/client neutrality proof.

Likely tests:

- `backend/tests/unit/test_evidence_refs_validation.py` - decorative, invalid and valid reference validation.
- `backend/tests/unit/test_evidence_refs_section_status.py` - grounded, partial, ungrounded and no-proof-required statuses.
- `backend/tests/integration/test_narrative_answer_audit_evidence_refs.py` - audit integration behavior.
- `backend/tests/architecture/test_evidence_refs_validation_boundary.py` - canonical owner and no API/client leakage guard.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- public API routers - out of scope; no client route is touched.
- admin API routers - out of scope; no admin API is implemented.
- prompt template files - out of scope; prompt content is not changed.
- generated OpenAPI clients - out of scope; no API contract is exposed.
- astrology calculation modules - out of scope; no calculation behavior is changed.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `. .\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `pytest -q tests/unit/test_evidence_refs_validation.py`
- VC6: `pytest -q tests/unit/test_evidence_refs_section_status.py`
- VC7: `pytest -q tests/integration/test_narrative_answer_audit_evidence_refs.py`
- VC8: `pytest -q tests/architecture/test_evidence_refs_validation_boundary.py`
- VC9: `pytest -q`
- VC10: `python -c "from app.main import app; assert 'evidence_refs' not in str(app.openapi())"`
- VC11: `python -c "from app.main import app; assert all('evidence_refs' not in getattr(r, 'path', '') for r in app.routes)"`
- VC12: `rg -n "evidence_refs|projection_hash|llm_input_hash|grounded|partial|ungrounded" app tests`
- VC13: `rg -n "EvidenceRefsValidator|validate_evidence_refs|section_status" app tests`
- VC14: `python -c "from pathlib import Path; p=Path('../_condamad/stories/CS-289-evidence-refs-section-validation/evidence/validation.txt'); assert p.exists()"`
- VC15: `python -c "from pathlib import Path; p=Path('../_condamad/stories/CS-289-evidence-refs-section-validation/evidence/source-decision.md'); assert p.exists()"`
- VC16: `python -c "from pathlib import Path; p=Path('../_condamad/stories/CS-289-evidence-refs-section-validation/evidence/app-surface-status.txt'); assert p.exists()"`
- VC17: `git status --short -- app tests migrations ../frontend/src`

Before VC3 through VC16, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The validator could accept any non-empty string instead of resolving a real authorized source.
- Hash comparison could be skipped and make `projection_hash` or LLM input hash decorative.
- Sections without proof requirements could be merged with invalid sections, hiding audit meaning.
- Audit integration could persist only global grounding status and lose per-section validation detail.
- Proof internals could leak into public API, admin API, frontend projections or generated clients.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments and public or non-trivial docstrings in French for new or significantly modified backend files.
- Start by proving whether CS-288 has created the canonical audit persistence owner.
- Record the source and audit reuse decision before adding a validator or integration point.
- Persist required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-289-implement-evidence-refs-validation.md`
- `_condamad/stories/CS-260-evidence-refs-contract-validation/00-story.md`
- `_condamad/stories/CS-264-projection-persistence-projection-hash/00-story.md`
- `_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/00-story.md`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`
- `_condamad/stories/regression-guardrails.md`
