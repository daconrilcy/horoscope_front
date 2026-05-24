# Story CS-260 evidence-refs-contract-validation: Add evidence_refs Contract And Validation
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-260-add-evidence-refs-contract-and-validation.md`.
- Related dependency: CS-256 defines `structured_facts_v1` as the stable hashable fact projection.
- Related dependency: CS-259 defines `narrative_answer_audit_v1` as the answer audit contract.
- Existing owner found: `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` owns AI narrative source vocabulary.
- Existing owner found: `docs/architecture/official-product-primitives-public-projections.md` owns public projection boundaries.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: audited narrative sections lack a versioned `evidence_refs` contract tying claims to validated hashable sources.
- Source-alignment evidence: PASS; ACs cover section proofs, source control, unfounded status and client masking.

## Objective

Define one canonical backend-domain contract document for `evidence_refs`.

The implementation must specify how each audited narrative section links to validated and hashed sources without exposing technical proof rows
to client-facing payloads, creating admin UI, altering astrology calculations, or implementing a semantic engine.

## Target State

- `evidence_refs` is documented as a versioned contract for audited narrative sections.
- Each audited section can carry one or more proof references tied to a section identifier.
- Authorized evidence sources are limited to structured facts, interpretive signals and projection versions.
- Each reference must point to a validated source with a stable hash, not a decorative string.
- Missing or invalid proof references can drive an `unfounded` grounding status for the audited section.
- Technical admin proof metadata and client-facing support wording are defined as separate surfaces.
- No backend runtime builder, service, route, model, database object, migration, frontend file, prompt template or provider call is created.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-260-add-evidence-refs-contract-and-validation.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-260`.
- Evidence 3: `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md` - structured facts dependency read.
- Evidence 4: `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md` - answer audit dependency read.
- Evidence 5: `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` - AI source vocabulary owner found.
- Evidence 6: `docs/architecture/official-product-primitives-public-projections.md` - public and LLM-only boundaries found.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output and targeted ID lookup only.
- Evidence 8: `resolve_guardrails.py` - scoped resolver run for backend-domain contract, validation, hashable source and narrative audit.
- Source-alignment evidence: PASS; no source concern was dropped or replaced by implementation cleanup.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Canonical contract documentation for `evidence_refs`.
  - Section-level proof reference shape and validation rules.
  - Authorized source kinds: structured facts, interpretive signals and projection versions.
  - Stable source hashing, source validation state and section grounding outcomes.
  - Separation between admin technical proof metadata and client-facing support wording.
  - Negative checks for public API, frontend, DB, prompt, provider and calculation drift.
- Out of scope:
  - Frontend UI, public API exposure, DB schema, migrations, auth, i18n, styling, build tooling and generated clients.
  - Admin viewer, semantic engine, astrology calculation changes, prompt changes and LLM provider calls.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No public endpoint, OpenAPI schema, response serializer or API contract for `evidence_refs`.
  - No database table, migration, repository, admin route, admin screen or semantic scoring engine.
  - No astrology calculation, prompt template, LLM provider or narrative renderer change.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract documentation.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the `evidence_refs` contract documentation and story evidence artifacts.
  - Reuse CS-256 `structured_facts_v1`, CS-259 `narrative_answer_audit_v1` and existing public projection governance terminology.
  - Keep backend runtime code, API routes, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Keep admin technical proof metadata separate from client-facing support wording.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product asks to expose technical proof metadata to clients or to implement an admin viewer in this story.
- Additional validation rules:
  - The contract must name `evidence_refs` exactly.
  - The contract must define `evidence_ref_id`, `section_id`, `source_type`, `source_id`, `source_version`, `source_hash` and `validation_state`.
  - The contract must define authorized `source_type` values for structured facts, interpretive signals and projection versions.
  - The contract must require every `evidence_ref` to point to a validated source and stable hash.
  - The contract must define invalid evidence errors for missing source, unsupported source type, missing hash and hash mismatch.
  - The contract must define section grounding outcomes including `grounded`, `partial`, `unfounded` and `not_checked`.
  - The contract must separate admin technical proof metadata from client-facing support wording.
  - `app.routes`, `app.openapi()`, `pytest` and scoped `git status` prove no public API or application surface drift.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Existing source owners, `app.routes`, `app.openapi()` and `pytest` prove no runtime surface drift. |
| Baseline Snapshot | yes | Before and after evidence must prove one contract document and no application surface drift. |
| Ownership Routing | yes | Evidence refs, structured facts, narrative audit and client support wording need separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this contract documentation story. |
| Contract Shape | yes | `evidence_refs` has exact fields, source types, validation errors and exposure rules. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Decorative refs, unvalidated sources, API drift and client proof leakage must stay out. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `evidence_refs` is documented. | Evidence profile: baseline_before_after_diff; `python` checks the contract document path. |
| AC2 | Section ownership is explicit. | Evidence profile: json_contract_shape; `rg` checks section_id and audited section wording. |
| AC3 | Proof reference fields are explicit. | Evidence profile: json_contract_shape; `rg` checks evidence_ref_id, source_id, source_version and source_hash. |
| AC4 | Authorized source kinds are explicit. | Evidence profile: json_contract_shape; `rg` checks structured facts, interpretive signals and projection versions. |
| AC5 | Source validation is mandatory. | Evidence profile: json_contract_shape; `rg` checks validated source, stable hash and hash mismatch. |
| AC6 | Missing proof can mark a section unfounded. | Evidence profile: json_contract_shape; `rg` checks missing proof and unfounded status. |
| AC7 | Client support wording is separated. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks admin technical proof and client-facing support. |
| AC8 | Public API surface stays unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`; `pytest` runs. |
| AC9 | Application source surfaces remain unchanged. | Evidence profile: repo_wide_negative_scan; `python` records scoped `git status --short` output. |
| AC10 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-260 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-256, CS-259, AI input and public projection governance before writing the contract. (AC: AC1, AC4)
- [ ] Task 2: Create `docs/architecture/evidence-refs-contract.md` with a French global file comment. (AC: AC1)
- [ ] Task 3: Define section-level ownership with stable `section_id` references. (AC: AC2)
- [ ] Task 4: Document mandatory proof reference fields and stable source hash requirements. (AC: AC3, AC5)
- [ ] Task 5: Document authorized source kinds for facts, interpretive signals and projection versions. (AC: AC4)
- [ ] Task 6: Document validation errors for missing source, unsupported source type, missing hash and hash mismatch. (AC: AC5, AC6)
- [ ] Task 7: Document section grounding outcomes including `grounded`, `partial`, `unfounded` and `not_checked`. (AC: AC6)
- [ ] Task 8: Document separation between admin technical proof metadata and client-facing support wording. (AC: AC7)
- [ ] Task 9: Persist validation, scoped status and source checklist evidence under the CS-260 evidence folder. (AC: AC8, AC9, AC10)

## Files to Inspect First

- `_story_briefs/cs-260-add-evidence-refs-contract-and-validation.md` - source contract.
- `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md` - upstream factual projection dependency.
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md` - downstream audit dependency.
- `docs/architecture/structured-facts-v1-contract.md` - expected upstream contract after CS-256 implementation.
- `docs/architecture/narrative-answer-audit-v1-contract.md` - expected audit contract after CS-259 implementation.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` - existing AI source vocabulary owner.
- `docs/architecture/official-product-primitives-public-projections.md` - public projection and LLM-only governance.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - CS-256 `structured_facts_v1` story for stable hashable factual source expectations.
  - CS-259 `narrative_answer_audit_v1` story for narrative audit and grounding vocabulary.
  - `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` for structured facts and signal source names.
  - `docs/architecture/official-product-primitives-public-projections.md` for public and LLM-only projection boundaries.
  - `app.routes`, `app.openapi()`, scoped `git status`, `pytest` and targeted `rg` scans for no public API or app-source drift.
- Secondary evidence:
  - Targeted `rg` scans over `docs/architecture/evidence-refs-contract.md`.
- Static scans alone are not sufficient because:
  - public API neutrality and application-source non-change must be proven from the loaded app and scoped status.

## Contract Shape

- Contract type:
  - Markdown backend-domain contract for section-level narrative evidence references.
- Fields:
  - `contract_id`: exact value `evidence_refs`.
  - `contract_version`: version of the evidence reference contract.
  - `section_id`: stable audited narrative section identifier.
  - `evidence_ref_id`: stable proof reference identifier unique inside the answer audit.
  - `source_type`: one of `structured_fact`, `interpretive_signal` or `projection_version`.
  - `source_id`: identifier of the validated source record.
  - `source_version`: version of the source contract or projection.
  - `source_hash`: stable hash of the source payload or validated projection artifact.
  - `validation_state`: one of `validated`, `missing_source`, `unsupported_source_type`, `missing_hash` or `hash_mismatch`.
  - `admin_proof`: internal technical metadata usable by audit and anti-hallucination validation.
  - `client_support`: vulgarized support wording allowed for client-facing explanations.
  - `grounding_status`: one of `grounded`, `partial`, `unfounded` or `not_checked`.
- Required fields:
  - `contract_id`
  - `contract_version`
  - `section_id`
  - `evidence_ref_id`
  - `source_type`
  - `source_id`
  - `source_version`
  - `source_hash`
  - `validation_state`
  - `grounding_status`
- Optional fields:
  - `admin_proof` for protected audit surfaces.
  - `client_support` for approved client-facing support text.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - documentation only; no runtime JSON serializer is added.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose `evidence_refs` from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-260-add-evidence-refs-contract-and-validation.md`
  - `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md`
  - `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md`
  - `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`
  - `docs/architecture/official-product-primitives-public-projections.md`
- Comparison after implementation:
  - `docs/architecture/evidence-refs-contract.md`
  - `_condamad/stories/CS-260-evidence-refs-contract-validation/evidence/validation.txt`
  - `_condamad/stories/CS-260-evidence-refs-contract-validation/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended repository delta is one architecture contract document plus CONDAMAD story and evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| `evidence_refs` contract | `docs/architecture/evidence-refs-contract.md` | API routers, frontend, DB models |
| Stable factual sources | `docs/architecture/structured-facts-v1-contract.md` | evidence ref contract as calculation owner |
| Narrative audit linkage | `docs/architecture/narrative-answer-audit-v1-contract.md` | prompt templates or provider code |
| AI source vocabulary | `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` | duplicated source taxonomy |
| Client support wording | future projection contract story | admin technical proof metadata |
| Evidence artifacts | `_condamad/stories/CS-260-evidence-refs-contract-validation/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse CS-256 `structured_facts_v1` and source hash language for factual traceability.
- Reuse CS-259 `narrative_answer_audit_v1` and grounding vocabulary for audited answer sections.
- Reuse existing `AINarrativeInputContract` structural facts, interpretive signals and source version terminology.
- Reuse public projection governance for client-facing masking instead of creating a parallel exposure rule.
- Keep one canonical `evidence_refs` document and one contract identifier.
- Do not add external packages, scripts, API schemas, frontend helpers, builders, services, prompts, migrations or generated clients.

## No Legacy / Forbidden Paths

- No legacy public route path may be added for this contract.
- No compatibility projection path may bypass `evidence_refs`.
- No fallback branch may accept decorative proof strings as valid references.
- Do not create aliases, shims, wrappers or parallel documents for the same evidence contract.
- Do not place admin technical proof metadata inside client-facing projections.
- Do not allow an `evidence_ref` without a validated source and stable hash.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/**`
  - `backend/app/infra/db/**`
  - `backend/migrations/**`
  - generated OpenAPI clients
  - prompt template files as evidence contract owners

## Reintroduction Guard

- Guard target:
  - evidence refs cannot point to decorative strings;
  - validated source and stable hash cannot become optional;
  - audited sections cannot omit grounding status;
  - client-facing payloads cannot expose admin technical proof metadata;
  - public API routes, database migrations and frontend files cannot be introduced by this story.
- Guard mechanism:
  - targeted `rg` checks for required contract terms and forbidden client exposure terms;
  - `app.routes` and `app.openapi()` neutrality checks;
  - scoped `git status --short` for application roots;
  - persisted evidence under the CS-260 evidence folder.
- Guard owner:
  - `docs/architecture/evidence-refs-contract.md`;
  - `_condamad/stories/CS-260-evidence-refs-contract-validation/evidence/validation.txt`;
  - `_condamad/stories/CS-260-evidence-refs-contract-validation/evidence/app-surface-status.txt`.
- Guard evidence:
  - `rg -n "evidence_refs|section_id|source_hash|validated source|unfounded" docs _story_briefs`;
  - `python -c "from app.main import app; assert 'evidence_refs' not in str(app.openapi())"`;
  - `python -c "from app.main import app; assert all('evidence_refs' not in getattr(r, 'path', '') for r in app.routes)"`;
  - `git status --short -- backend/app frontend/src backend/tests backend/migrations`.

## Regression Guardrails

Scope vector:

- backend-domain contract documentation: yes;
- docs architecture contract: yes;
- backend interpretation source reference: yes;
- narrative audit validation reference: yes;
- API route change: no;
- frontend implementation: no;
- DB, auth, i18n, style, build and migration: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | Backend app paths are referenced only as source owners, not modified. | `git status`; `python` loaded app checks. |
| Registry gap | No exact `evidence_refs` guardrail exists in scoped resolver output. | Story-local `rg`, `app.routes` and `app.openapi()` guards. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is out of scope because this contract concerns narrative evidence validation.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Contract document | `docs/architecture/evidence-refs-contract.md` | Keep the canonical `evidence_refs` contract. |
| Validation output | `_condamad/stories/CS-260-evidence-refs-contract-validation/evidence/validation.txt` | Keep content scans and validation. |
| Application surface status | `_condamad/stories/CS-260-evidence-refs-contract-validation/evidence/app-surface-status.txt` | Prove app roots stayed untouched. |
| Source checklist | `_condamad/stories/CS-260-evidence-refs-contract-validation/evidence/source-checklist.md` | Record mandatory source coverage. |
| Review output | `_condamad/stories/CS-260-evidence-refs-contract-validation/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this contract documentation story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/evidence-refs-contract.md` - new canonical contract document.
- `_condamad/stories/CS-260-evidence-refs-contract-validation/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-260-evidence-refs-contract-validation/evidence/app-surface-status.txt` - application non-change proof.
- `_condamad/stories/CS-260-evidence-refs-contract-validation/evidence/source-checklist.md` - source coverage evidence.

Likely tests:

- `docs/architecture/evidence-refs-contract.md` - checked by `rg` and `python` validation commands.
- `backend/tests/architecture/test_api_contract_neutrality.py` - targeted architecture regression check for no public route drift.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/**` - out of scope; no backend application source is touched.
- `backend/tests/**` - out of scope except existing architecture tests executed as evidence.
- `backend/migrations/**` - out of scope; no database migration is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `python -c "from pathlib import Path; assert Path('docs/architecture/evidence-refs-contract.md').exists()"`
- VC3: `rg -n "evidence_refs|section_id|evidence_ref_id|source_id|source_version|source_hash" docs/architecture/evidence-refs-contract.md`
- VC4: `rg -n "structured facts|interpretive signals|projection versions|validated source" docs/architecture/evidence-refs-contract.md`
- VC5: `rg -n "missing source|unsupported source type|missing hash|hash mismatch" docs/architecture/evidence-refs-contract.md`
- VC6: `rg -n "grounded|partial|unfounded|not_checked|grounding_status" docs/architecture/evidence-refs-contract.md`
- VC7: `rg -n "admin technical proof|client-facing support|vulgarized" docs/architecture/evidence-refs-contract.md`
- VC8: `python -c "from app.main import app; assert 'evidence_refs' not in str(app.openapi())"`
- VC9: `python -c "from app.main import app; assert all('evidence_refs' not in getattr(r, 'path', '') for r in app.routes)"`
- VC10: `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`
- VC11: `git status --short -- backend/app frontend/src backend/tests backend/migrations`
- VC12: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-260-evidence-refs-contract-validation/evidence/validation.txt').exists()"`
- VC13: `ruff format .`
- VC14: `ruff check .`
- VC15: `pytest -q`
- VC16: `rg -n "evidence_refs|preuve|section|grounding|hash|source validée|vulgarisé|admin" .\docs .\_story_briefs`
- VC17: `git status --short -- backend/app frontend/src`

Before VC2, VC8, VC9 and VC12, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- Narrative section claims could cite decorative strings instead of validated hashable sources.
- Hash fields could be treated as optional metadata instead of mandatory proof anchors.
- Missing proof references could leave a section looking grounded when it must be marked unfounded.
- Client-facing projections could leak admin technical proof metadata instead of vulgarized support wording.
- A documentation story could drift into persistence, API, admin UI, semantic engine, frontend, prompt, provider or migration implementation.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments and public or non-trivial docstrings in French for new or significantly modified backend files.
- Keep the implementation documentation-only unless a separate user decision authorizes code, DB, route, prompt, provider or frontend work.
- Persist the required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-260-add-evidence-refs-contract-and-validation.md`
- `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md`
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md`
- `docs/architecture/structured-facts-v1-contract.md`
- `docs/architecture/narrative-answer-audit-v1-contract.md`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`
- `docs/architecture/official-product-primitives-public-projections.md`
- `_condamad/stories/regression-guardrails.md`
