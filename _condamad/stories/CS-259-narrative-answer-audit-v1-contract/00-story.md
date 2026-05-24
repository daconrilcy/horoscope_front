# Story CS-259 narrative-answer-audit-v1-contract: Define narrative_answer_audit_v1 Audit Contract
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-259-define-narrative-answer-audit-v1.md`.
- Related dependency: CS-254 defines `AINarrativeInputContract` as the internal AI scoring and narrative input contract.
- Related dependency: CS-256 defines `structured_facts_v1` as the stable factual projection for downstream audit references.
- Existing owner found: `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` owns AI narrative input fields.
- Existing owner found: `docs/architecture/official-product-primitives-public-projections.md` classifies `llm_input` as LLM-only.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: narrative AI answers lack one versioned audit contract tying prose to facts, prompts, provider, model and proof state.
- Source-alignment evidence: PASS; ACs cover mandatory IDs, hashes, statuses, prompt storage, rejected answers and client proof masking.

## Objective

Define one canonical backend-domain contract document for `narrative_answer_audit_v1`.

The implementation must specify how generated narrative answers are audited against facts, LLM inputs, prompt versions, provider, model,
grounding state and rejected answer storage without implementing persistence, prompts, admin UI, API routes or frontend behavior.

## Target State

- `narrative_answer_audit_v1` is documented as the audit contract for basic, premium, long, sensitive and free_short narrative answers.
- The contract requires `answer_id`, `answer_type`, `chart_id`, `user_id`, `plan`, `projection_version`, `projection_hash`.
- The contract requires `llm_input_version`, `llm_input_hash`, `prompt_version`, `provider` and `model`.
- The contract defines `grounding_status` values: `grounded`, `partial`, `ungrounded`, `rejected` and `not_checked`.
- The contract defines prompt evidence storage as full prompt retention or `prompt_ref` plus payload snapshot.
- Rejected narrative answers remain auditable with the same source, prompt and grounding metadata.
- Client-facing projections never expose technical proof fields, provider internals, prompt payloads or audit rows.
- No backend runtime builder, service, route, model, database object, migration, frontend file, prompt template or provider integration is created.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-259-define-narrative-answer-audit-v1.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-259`.
- Evidence 3: `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/00-story.md` - AI input dependency read.
- Evidence 4: `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md` - structured facts dependency read.
- Evidence 5: `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` - AI narrative input owner found.
- Evidence 6: `docs/architecture/official-product-primitives-public-projections.md` - `llm_input` and public proof boundaries found.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output and targeted lookup only.
- Evidence 8: `resolve_guardrails.py` - scoped resolver run for backend-domain audit contract, LLM input and no-public-API surfaces.
- Source-alignment evidence: PASS; the story preserves every brief stake without turning the audit contract into persistence or UI work.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Canonical contract documentation for `narrative_answer_audit_v1`.
  - Mandatory answer, chart, user, plan, projection, LLM input, prompt, provider and model fields.
  - `answer_type` values for `basic`, `premium`, `long`, `sensitive` and `free_short`.
  - `grounding_status` values for grounded, partial, ungrounded, rejected and not_checked outcomes.
  - Prompt retention alternatives and rejected answer audit requirements.
  - Negative checks for client proof exposure, API route drift, DB drift, prompt drift and frontend drift.
- Out of scope:
  - Frontend UI, public API exposure, DB schema, migrations, auth, i18n, styling, build tooling and generated clients.
  - Persistence implementation, final GDPR retention policy, admin screens, prompt modification and provider calls.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No public endpoint, OpenAPI schema, response serializer or API contract for `narrative_answer_audit_v1`.
  - No database table, migration, repository, retention policy, admin route or admin screen.
  - No prompt template change, LLM provider implementation or narrative renderer change.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain audit contract documentation.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the `narrative_answer_audit_v1` contract documentation and story evidence artifacts.
  - Reuse CS-254 `AINarrativeInputContract`, CS-256 `structured_facts_v1` and existing public projection governance terminology.
  - Keep backend runtime code, API routes, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Keep technical audit proof, provider internals and prompt payloads outside client-facing projections.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product asks to expose audit proof fields to clients or to define final GDPR retention in this story.
- Additional validation rules:
  - The contract must name `narrative_answer_audit_v1` exactly.
  - The contract must define all mandatory answer, chart, user, plan, projection, LLM input, prompt, provider and model fields.
  - The contract must define `answer_type` values `basic`, `premium`, `long`, `sensitive` and `free_short`.
  - The contract must define `grounding_status` values `grounded`, `partial`, `ungrounded`, `rejected` and `not_checked`.
  - The contract must require `projection_hash` and `llm_input_hash`.
  - The contract must define full prompt retention or `prompt_ref` plus payload snapshot.
  - The contract must state that client-facing payloads do not expose technical audit proof.
  - `app.routes`, `app.openapi()`, `pytest` and scoped `git status` prove no public API or application surface drift.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Existing AI input, projection contracts, `app.routes`, `app.openapi()` and `pytest` prove source boundaries. |
| Baseline Snapshot | yes | Before and after evidence must prove one contract document and no application surface drift. |
| Ownership Routing | yes | Audit contract, AI input, structured facts, prompts, provider metadata and client projections need separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this contract documentation story. |
| Contract Shape | yes | `narrative_answer_audit_v1` has exact fields, enums, prompt evidence and client masking rules. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Client proof exposure, persistence work and prompt edits must stay out. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `narrative_answer_audit_v1` is documented. | Evidence profile: baseline_before_after_diff; `python` checks the contract document path. |
| AC2 | Mandatory identity fields are explicit. | Evidence profile: json_contract_shape; `rg` checks answer_id, chart_id, user_id, plan and projection_version. |
| AC3 | Mandatory hashes are explicit. | Evidence profile: json_contract_shape; `rg` checks projection_hash and llm_input_hash. |
| AC4 | LLM provenance fields are explicit. | Evidence profile: json_contract_shape; `rg` checks llm_input_version, prompt_version, provider and model. |
| AC5 | Grounding statuses are defined. | Evidence profile: json_contract_shape; `rg` checks grounded, partial, ungrounded, rejected and not_checked. |
| AC6 | Answer categories are defined. | Evidence profile: json_contract_shape; `rg` checks basic, premium, long, sensitive and free_short. |
| AC7 | Prompt evidence storage is defined. | Evidence profile: json_contract_shape; `rg` checks full prompt, prompt_ref and payload snapshot. |
| AC8 | Client proof exposure is forbidden. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks client-facing masking and proof wording. |
| AC9 | Public API surface stays unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`. |
| AC10 | Application source surfaces remain unchanged. | Evidence profile: repo_wide_negative_scan; `python` records scoped `git status --short` output. |
| AC11 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-259 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-254, CS-256, AI narrative input and public projection governance before writing the contract. (AC: AC1, AC4)
- [ ] Task 2: Create `docs/architecture/narrative-answer-audit-v1-contract.md` with a French global file comment. (AC: AC1)
- [ ] Task 3: Define the audit role for basic, premium, long, sensitive and free_short answers. (AC: AC1, AC6)
- [ ] Task 4: Document mandatory answer, chart, user, plan and projection identity fields. (AC: AC2)
- [ ] Task 5: Document `projection_hash` and `llm_input_hash` as required audit anchors. (AC: AC3)
- [ ] Task 6: Document LLM input, prompt, provider and model provenance fields. (AC: AC4)
- [ ] Task 7: Document `grounding_status` values and rejected answer storage rules. (AC: AC5)
- [ ] Task 8: Document full prompt retention or `prompt_ref` plus payload snapshot. (AC: AC7)
- [ ] Task 9: Document client-facing masking so technical proofs stay internal. (AC: AC8)
- [ ] Task 10: Persist validation, scoped status and source checklist evidence under the CS-259 evidence folder. (AC: AC9, AC10, AC11)

## Files to Inspect First

- `_story_briefs/cs-259-define-narrative-answer-audit-v1.md` - source contract.
- `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/00-story.md` - AI narrative input dependency.
- `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md` - upstream factual projection dependency.
- `docs/architecture/structured-facts-v1-contract.md` - expected upstream factual contract after CS-256 implementation.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` - existing AI input owner.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` - existing AI input builder owner.
- `docs/architecture/official-product-primitives-public-projections.md` - public projection and LLM-only governance.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` for AI input provenance vocabulary.
  - `docs/architecture/structured-facts-v1-contract.md` for factual projection and hash linkage after CS-256.
  - `docs/architecture/official-product-primitives-public-projections.md` for public and LLM-only projection boundaries.
  - `app.routes`, `app.openapi()`, scoped `git status`, `pytest` and targeted `rg` scans for no public API or app-source drift.
- Secondary evidence:
  - Targeted `rg` scans over `docs/architecture/narrative-answer-audit-v1-contract.md`.
- Static scans alone are not sufficient because:
  - public API neutrality and application-source non-change must be proven from the loaded app and scoped status.

## Contract Shape

- Contract type:
  - Markdown backend-domain contract for a future narrative answer audit record.
- Fields:
  - `contract_id`: exact value `narrative_answer_audit_v1`.
  - `answer_id`: unique generated answer identifier.
  - `answer_type`: one of `basic`, `premium`, `long`, `sensitive` or `free_short`.
  - `chart_id`: chart identifier used to derive the projection.
  - `user_id`: user identifier associated with the answer owner.
  - `plan`: commercial plan at answer generation time.
  - `projection_version`: upstream projection version.
  - `projection_hash`: stable hash of the audited projection payload.
  - `llm_input_version`: AI input contract version.
  - `llm_input_hash`: stable hash of the LLM input payload.
  - `prompt_version`: prompt contract version used for generation.
  - `provider`: LLM provider identifier.
  - `model`: provider model identifier.
  - `grounding_status`: one of `grounded`, `partial`, `ungrounded`, `rejected` or `not_checked`.
  - `prompt_storage`: full prompt text or `prompt_ref` plus payload snapshot.
  - `rejection_record`: rejected answer content, reason and source evidence metadata.
  - `client_exposure_policy`: technical proof fields remain internal.
- Required fields:
  - `contract_id`
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
  - `prompt_storage`
  - `client_exposure_policy`
- Optional fields:
  - `rejection_record` only for rejected outputs.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - documentation only; no runtime JSON serializer is added.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose `narrative_answer_audit_v1` from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-259-define-narrative-answer-audit-v1.md`
  - `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/00-story.md`
  - `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md`
  - `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`
  - `docs/architecture/official-product-primitives-public-projections.md`
- Comparison after implementation:
  - `docs/architecture/narrative-answer-audit-v1-contract.md`
  - `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/evidence/validation.txt`
  - `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended repository delta is one architecture contract document plus CONDAMAD story and evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| `narrative_answer_audit_v1` contract | `docs/architecture/narrative-answer-audit-v1-contract.md` | API routers, frontend, DB models |
| AI input provenance | `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` | prompt templates or provider code |
| Factual projection hash | `docs/architecture/structured-facts-v1-contract.md` | audit contract as calculation owner |
| Public and LLM-only policy | `docs/architecture/official-product-primitives-public-projections.md` | duplicated public registry |
| Future persistence | later CS-288 persistence story | this documentation story |
| Evidence artifacts | `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse CS-254 `AINarrativeInputContract` and `llm_input` terminology instead of creating a parallel AI input contract.
- Reuse CS-256 `structured_facts_v1` and projection hash language for factual traceability.
- Reuse existing public projection governance for client proof masking.
- Keep one canonical `narrative_answer_audit_v1` document and one audit contract identifier.
- Do not duplicate persistence, prompt, provider, public API or frontend ownership inside this contract story.
- Do not add external packages, scripts, API schemas, frontend helpers, builders, services, prompts, migrations or generated clients.

## No Legacy / Forbidden Paths

- No legacy public route path may be added for this audit contract.
- No compatibility projection path may bypass `narrative_answer_audit_v1`.
- No fallback branch may store unaudited narrative answers outside the contract once implemented by later stories.
- Do not create aliases, shims, wrappers or parallel documents for the same audit contract.
- Do not place prompt payloads, provider internals, model internals, technical proof fields or audit rows inside client-facing projections.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/**`
  - `backend/app/infra/db/**`
  - `backend/migrations/**`
  - generated OpenAPI clients
  - prompt template files as audit contract owners

## Reintroduction Guard

- Guard target:
  - narrative answers cannot be documented without answer, projection, LLM input, prompt, provider and model provenance;
  - `projection_hash` and `llm_input_hash` cannot become optional in the audit contract;
  - rejected narrative answers cannot bypass the audit metadata contract;
  - client-facing payloads cannot expose prompt payloads, provider internals, model internals or technical proof fields;
  - public API routes, database migrations and frontend files cannot be introduced by this story.
- Guard mechanism:
  - targeted `rg` checks for required contract terms and forbidden client exposure terms;
  - `app.routes` and `app.openapi()` neutrality checks;
  - scoped `git status --short` for application roots;
  - persisted evidence under the CS-259 evidence folder.
- Guard owner:
  - `docs/architecture/narrative-answer-audit-v1-contract.md`;
  - `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/evidence/validation.txt`;
  - `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/evidence/app-surface-status.txt`.
- Guard evidence:
  - `rg -n "narrative_answer_audit_v1|answer_id|projection_hash|llm_input_hash" docs _story_briefs`;
  - `python -c "from app.main import app; assert 'narrative_answer_audit_v1' not in str(app.openapi())"`;
  - `python -c "from app.main import app; assert all('narrative_answer_audit' not in getattr(r, 'path', '') for r in app.routes)"`;
  - `git status --short -- backend/app frontend/src backend/tests backend/migrations`.

## Regression Guardrails

Scope vector:

- backend-domain contract documentation: yes;
- docs architecture contract: yes;
- backend interpretation source reference: yes;
- LLM input provenance reference: yes;
- API route change: no;
- frontend implementation: no;
- DB, auth, i18n, style, build and migration: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | Backend app paths are referenced only as source owners, not modified. | `git status`; `python` loaded app checks. |
| RG-003 | Route architecture stays unchanged because this contract adds no route. | `app.routes`; `app.openapi()`. |
| RG-007 | Admin LLM observability remains the route owner for observability surfaces. | `app.routes`; targeted `rg`. |
| RG-022 | Prompt-generation validation discipline applies to LLM contract evidence. | `rg`; `pytest`; persisted validation. |
| Registry gap | No exact `narrative_answer_audit_v1` guardrail exists in resolver output. | Story-local scans and loaded app checks. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is out of scope because this story defines audit metadata, not access rights.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Contract document | `docs/architecture/narrative-answer-audit-v1-contract.md` | Keep the canonical narrative answer audit contract. |
| Validation output | `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/evidence/validation.txt` | Keep content scans and validation. |
| Application surface status | `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/evidence/app-surface-status.txt` | Prove app roots stayed untouched. |
| Source checklist | `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/evidence/source-checklist.md` | Record mandatory source coverage. |
| Review output | `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this contract documentation story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/narrative-answer-audit-v1-contract.md` - new canonical contract document.
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/evidence/app-surface-status.txt` - application non-change proof.
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/evidence/source-checklist.md` - source coverage evidence.

Likely tests:

- `docs/architecture/narrative-answer-audit-v1-contract.md` - checked by `rg` and `python` validation commands.
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
- VC2: `python -c "from pathlib import Path; assert Path('docs/architecture/narrative-answer-audit-v1-contract.md').exists()"`
- VC3: `rg -n "narrative_answer_audit_v1|answer_id|answer_type|chart_id|user_id|plan" docs/architecture/narrative-answer-audit-v1-contract.md`
- VC4: `rg -n "projection_version|projection_hash|llm_input_version|llm_input_hash" docs/architecture/narrative-answer-audit-v1-contract.md`
- VC5: `rg -n "prompt_version|provider|model|full prompt|prompt_ref|payload snapshot" docs/architecture/narrative-answer-audit-v1-contract.md`
- VC6: `rg -n "grounded|partial|ungrounded|rejected|not_checked" docs/architecture/narrative-answer-audit-v1-contract.md`
- VC7: `rg -n "basic|premium|long|sensitive|free_short" docs/architecture/narrative-answer-audit-v1-contract.md`
- VC8: `rg -n "client-facing|technical proof|provider internals|audit rows" docs/architecture/narrative-answer-audit-v1-contract.md`
- VC9: `python -c "from app.main import app; assert 'narrative_answer_audit_v1' not in str(app.openapi())"`
- VC10: `python -c "from app.main import app; assert all('narrative_answer_audit' not in getattr(r, 'path', '') for r in app.routes)"`
- VC11: `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`
- VC12: `git status --short -- backend/app frontend/src backend/tests backend/migrations`
- VC13: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-259-narrative-answer-audit-v1-contract/evidence/validation.txt').exists()"`
- VC14: `ruff format .`
- VC15: `ruff check .`
- VC16: `pytest -q`
- VC17: `rg -n "narrative_answer_audit_v1|answer_id|answer_type|projection_hash|llm_input_hash|grounding_status|rejected" .\docs .\_story_briefs`
- VC18: `git status --short -- backend/app frontend/src`

Before VC2, VC9, VC10 and VC13, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- Narrative answers could be stored without enough source linkage to prove the factual, prompt and provider context used to generate them.
- Hash fields could be treated as optional metadata instead of mandatory audit anchors.
- Rejected outputs could be discarded without preserving the evidence needed to explain why they failed grounding.
- Client-facing projections could leak prompt payloads, provider internals, model internals or audit proof fields.
- A documentation story could drift into persistence, API, admin UI, prompt, provider, frontend or migration implementation.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments and public or non-trivial docstrings in French for new or significantly modified backend files.
- Keep the implementation documentation-only unless a separate user decision authorizes code, DB, route, prompt or frontend work.
- Persist the required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-259-define-narrative-answer-audit-v1.md`
- `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/00-story.md`
- `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md`
- `docs/architecture/structured-facts-v1-contract.md`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`
- `docs/architecture/official-product-primitives-public-projections.md`
- `_condamad/stories/regression-guardrails.md`
