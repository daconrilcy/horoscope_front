# Story CS-256 structured-facts-v1-contract: Define structured_facts_v1 Stable Hashable Fact Projection
Status: done

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-256-define-structured-facts-v1-stable-hashable-fact-projection.md`.
- Related dependency: CS-254 defines `AINarrativeInputContract` as the internal AI scoring and narrative input contract.
- Related dependency: CS-255 documents the current product architecture and separates facts, signals, narration and projections.
- Existing owner found: `docs/architecture/official-product-primitives-public-projections.md` already lists `structured_facts`.
- Existing owner found: `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` owns `AINarrativeInputContract`.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: `structured_facts_v1` lacks one stable, hashable and non narrative contract that can anchor audit and future projections.
- Source-alignment evidence: PASS; ACs preserve stable facts, hashability, non narrative scope, AI input link and raw runtime exclusions.

## Objective

Define one canonical backend-domain contract document for `structured_facts_v1` as a stable, hashable and non narrative fact projection.

The implementation must formalize the role, authorized fact families, hash rules, `AINarrativeInputContract` relationship and forbidden raw surfaces
without implementing the projection, exposing a public API or modifying frontend behavior.

## Target State

- `structured_facts_v1` is documented as the common factual base for future client, admin/expert, LLM input, audit and `evidence_refs` projections.
- The contract lists authorized fact families: positions, houses, major aspects, dominants and source metadata.
- The contract defines deterministic ordering, stable serialization, hash input boundaries and hash purpose for AI audit.
- The contract explicitly states that it is non narrative and cannot contain prompt text, rendered prose, advice or LLM output.
- The contract explains how `AINarrativeInputContract` may consume or reference `structured_facts_v1` without owning calculation truth.
- The contract excludes `ChartObjectRuntimeData`, raw `chart_objects`, debug raw traces, runtime traces and internal payloads from public surfaces.
- The B2C client is not presented as a mandatory direct consumer.
- No backend runtime builder, service, route, model, database object, migration, frontend file or generated client is created by this story.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-256-define-structured-facts-v1-stable-hashable-fact-projection.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-256`.
- Evidence 3: `docs/architecture/official-product-primitives-public-projections.md` - existing `structured_facts` primitive owner found.
- Evidence 4: `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/00-story.md` - AI input dependency read.
- Evidence 5: `_condamad/stories/CS-255-product-architecture-current-state/00-story.md` - product architecture dependency read.
- Evidence 6: `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` - `AINarrativeInputContract` owner found.
- Evidence 7: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - raw runtime source owner found by targeted search.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output only.
- Source-alignment evidence: PASS; the story answers every brief AC without turning the projection into B2C UX or public API work.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Canonical contract documentation for `structured_facts_v1`.
  - Stable fact families, hashability rules, source metadata and AI audit linkage.
  - Relationship to `AINarrativeInputContract` as downstream consumer or reference.
  - Negative checks for raw runtime, narrative content, API route and frontend drift.
  - Persistent evidence artifacts for the contract and validation scans.
- Out of scope:
  - Frontend UI, public API exposure, DB schema, migrations, auth, i18n, styling, build tooling and generated clients.
  - Projection implementation, builder service, runtime model, route, serializer, persistence and LLM narrative content.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No public endpoint, OpenAPI schema, response serializer or API contract for `structured_facts_v1`.
  - No runtime projection builder, service orchestration, database table or migration.
  - No prompt template, final prose, advice text or LLM provider integration.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract documentation.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the `structured_facts_v1` contract documentation and story evidence artifacts.
  - Reuse existing `structured_facts`, `AINarrativeInputContract`, `ChartObjectRuntimeData` and architecture terminology.
  - Keep backend runtime code, API routes, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Keep raw runtime payloads outside public or B2C direct-consumer surfaces.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product asks to expose `structured_facts_v1` directly to B2C before an API projection story exists.
- Additional validation rules:
  - The contract must name `structured_facts_v1` exactly.
  - The contract must include positions, houses, major aspects, dominants and source metadata as authorized fact families.
  - The contract must define stable ordering, deterministic serialization and a hash input boundary.
  - The contract must state that narrative text, prompt text, advice and LLM output are forbidden from the projection.
  - The contract must link `AINarrativeInputContract` as downstream input or reference, not as calculation truth.
  - `ChartObjectRuntimeData`, raw `chart_objects`, debug raw traces and internal payloads must remain outside public surfaces.
  - `app.routes`, `app.openapi()`, `pytest` and scoped `git status` prove no public API or application surface drift.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Existing runtime and AI contract owners prove the factual source boundary before documentation claims it. |
| Baseline Snapshot | yes | Before and after evidence must prove one contract document and no application surface drift. |
| Ownership Routing | yes | Contract documentation, runtime facts, AI input and future public projections need separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this contract documentation story. |
| Contract Shape | yes | `structured_facts_v1` has exact families, hash rules, exclusions and consumer boundaries. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Narrative content, raw runtime payloads and direct B2C ownership must stay out of the contract. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `structured_facts_v1` is documented. | Evidence profile: baseline_before_after_diff; `python` checks the contract document path. |
| AC2 | Authorized fact families are explicit. | Evidence profile: json_contract_shape; `rg` checks positions, houses, major aspects, dominants and source metadata. |
| AC3 | Hashability rules are explicit. | Evidence profile: json_contract_shape; `rg` checks stable ordering, deterministic serialization and hash input boundary. |
| AC4 | Narrative content is forbidden. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks non narrative and forbidden prose tokens in the document. |
| AC5 | AI input linkage is explicit. | Evidence profile: json_contract_shape; `rg` checks `AINarrativeInputContract` and downstream reference wording. |
| AC6 | B2C direct consumption is not required. | Evidence profile: external_usage_blocker; `rg` checks B2C, optional consumer and product projection wording. |
| AC7 | Raw runtime surfaces remain outside public scope. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`; `rg` checks raw names. |
| AC8 | Application source surfaces remain unchanged. | Evidence profile: repo_wide_negative_scan; `python` records scoped `git status --short` output for app roots. |
| AC9 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-256 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect existing `structured_facts`, AI input and runtime owners before writing the contract. (AC: AC1, AC5)
- [ ] Task 2: Create `docs/architecture/structured-facts-v1-contract.md` with a French global file comment. (AC: AC1)
- [ ] Task 3: Define the role of `structured_facts_v1` as stable factual base for future controlled projections. (AC: AC1, AC6)
- [ ] Task 4: Document authorized fact families for positions, houses, major aspects, dominants and source metadata. (AC: AC2)
- [ ] Task 5: Document stable ordering, deterministic serialization, hash boundary and AI audit purpose. (AC: AC3)
- [ ] Task 6: Document the non narrative constraint and forbidden text-like fields. (AC: AC4)
- [ ] Task 7: Link `AINarrativeInputContract` as downstream consumer or reference while preserving runtime source ownership. (AC: AC5)
- [ ] Task 8: Document excluded raw surfaces including `ChartObjectRuntimeData`, `chart_objects`, debug traces and internal payloads. (AC: AC7)
- [ ] Task 9: Persist validation, scoped status and contract evidence under the CS-256 evidence folder. (AC: AC8, AC9)

## Files to Inspect First

- `_story_briefs/cs-256-define-structured-facts-v1-stable-hashable-fact-projection.md` - source contract.
- `docs/architecture/official-product-primitives-public-projections.md` - existing product primitive owner.
- `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/00-story.md` - AI input contract dependency.
- `_condamad/stories/CS-255-product-architecture-current-state/00-story.md` - product architecture dependency.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` - existing AI input owner.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` - existing AI input builder owner.
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - raw runtime owner that must remain non-public.
- `backend/app/domain/astrology/natal_calculation.py` - current public result boundary and internal `chart_objects` handling.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `backend/app/domain/astrology/runtime/**` canonical runtime facts.
  - `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` for AI input relationship.
  - `docs/architecture/official-product-primitives-public-projections.md` for product projection ownership.
  - `app.routes`, `app.openapi()`, scoped `git status`, and targeted `rg` scans for no public API or app-source drift.
- Secondary evidence:
  - Targeted `rg` scans over `docs/architecture/structured-facts-v1-contract.md`.
- Static scans alone are not sufficient because:
  - public API neutrality and application-source non-change must be proven from the loaded app and scoped status.

## Contract Shape

- Contract type:
  - Markdown backend-domain contract for a future controlled factual projection.
- Fields:
  - `projection_id`: exact value `structured_facts_v1`.
  - `role`: stable factual base for future client, admin/expert, LLM input, audit and `evidence_refs` projections.
  - `fact_families`: positions, houses, major aspects, dominants and source metadata.
  - `stability_rules`: deterministic ordering, stable identifiers, stable units, stable precision and no runtime-only ordering.
  - `hash_rules`: canonical serialization, hash input boundary, source version inclusion and audit purpose.
  - `ai_input_link`: relationship to `AINarrativeInputContract`.
  - `consumer_policy`: future projection consumers without mandatory direct B2C consumption.
  - `excluded_surfaces`: narrative text, debug raw traces, runtime traces, internal payloads and raw runtime objects.
- Required fields:
  - `projection_id`
  - `role`
  - `fact_families`
  - `stability_rules`
  - `hash_rules`
  - `ai_input_link`
  - `consumer_policy`
  - `excluded_surfaces`
- Optional fields:
  - none.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - documentation only; no runtime JSON serializer is added.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose `structured_facts_v1` from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-256-define-structured-facts-v1-stable-hashable-fact-projection.md`
  - `docs/architecture/official-product-primitives-public-projections.md`
  - `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/00-story.md`
  - `_condamad/stories/CS-255-product-architecture-current-state/00-story.md`
- Comparison after implementation:
  - `docs/architecture/structured-facts-v1-contract.md`
  - `_condamad/stories/CS-256-structured-facts-v1-contract/evidence/validation.txt`
  - `_condamad/stories/CS-256-structured-facts-v1-contract/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended repository delta is one architecture contract document plus CONDAMAD story and evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| `structured_facts_v1` contract | `docs/architecture/structured-facts-v1-contract.md` | API routers, frontend, DB models |
| Product primitive registry | `docs/architecture/official-product-primitives-public-projections.md` | duplicated projection registry |
| AI input relationship | `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` | prompt templates or LLM output |
| Runtime fact source | `backend/app/domain/astrology/runtime/**` | public documentation as raw payload contract |
| Evidence artifacts | `_condamad/stories/CS-256-structured-facts-v1-contract/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse the existing `structured_facts` product primitive wording instead of creating a parallel primitive name.
- Reuse CS-254 `AINarrativeInputContract` terminology for AI linkage instead of creating a second AI input contract.
- Reuse CS-255 facts to signals to narration boundary language.
- Reuse `ChartObjectRuntimeData` and `chart_objects` only as internal source references, not public payload shapes.
- Keep one canonical `structured_facts_v1` document and one projection identifier.
- Do not add external packages, scripts, API schemas, frontend helpers, builders, services or generated clients.

## No Legacy / Forbidden Paths

- No legacy public route path may be added for this contract.
- No compatibility projection path may bypass `structured_facts_v1`.
- No fallback branch may expose raw runtime objects as the projection.
- Do not create aliases, shims, wrappers or parallel documents for the same projection contract.
- Do not place narrative text, prompt text, LLM output, final prose, raw debug traces or internal payloads inside the projection.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/**`
  - `backend/app/infra/db/**`
  - `backend/migrations/**`
  - generated OpenAPI clients
  - prompt template files as factual contract owners

## Reintroduction Guard

- Guard target:
  - narrative and prompt-owned fields cannot enter `structured_facts_v1`;
  - raw runtime payloads cannot become public projection payloads;
  - B2C direct consumption cannot become mandatory before a separate product story;
  - public API routes and OpenAPI schemas cannot be introduced by this story.
- Guard mechanism:
  - targeted `rg` checks for required contract terms and forbidden raw-surface terms;
  - `app.routes` and `app.openapi()` neutrality checks;
  - scoped `git status --short` for application roots;
  - persisted evidence under the CS-256 evidence folder.
- Guard owner:
  - `docs/architecture/structured-facts-v1-contract.md`;
  - `_condamad/stories/CS-256-structured-facts-v1-contract/evidence/validation.txt`;
  - `_condamad/stories/CS-256-structured-facts-v1-contract/evidence/app-surface-status.txt`.
- Guard evidence:
  - `rg -n "structured_facts_v1|hash|non narrative|ChartObjectRuntimeData|AINarrativeInputContract" docs _condamad _story_briefs`;
  - `python -c "from app.main import app; assert 'structured_facts_v1' not in str(app.openapi())"`;
  - `python -c "from app.main import app; assert all('structured_facts' not in getattr(r, 'path', '') for r in app.routes)"`;
  - `git status --short -- backend/app frontend/src`.

## Regression Guardrails

Scope vector:

- backend-domain contract documentation: yes;
- docs architecture contract: yes;
- backend runtime source reference: yes;
- API route change: no;
- frontend implementation: no;
- DB, auth, i18n, style, build and migration: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | Backend app paths are referenced only as source owners, not modified. | `git status`; `python` loaded app checks. |
| Registry gap | No exact `structured_facts_v1` guardrail exists in scoped resolver output. | Story-local `rg`, `app.routes` and `app.openapi()` guards. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is out of scope because this contract concerns astrology factual projections.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Contract document | `docs/architecture/structured-facts-v1-contract.md` | Keep the canonical `structured_facts_v1` contract. |
| Validation output | `_condamad/stories/CS-256-structured-facts-v1-contract/evidence/validation.txt` | Keep content scans and story execution validation. |
| Application surface status | `_condamad/stories/CS-256-structured-facts-v1-contract/evidence/app-surface-status.txt` | Prove app roots stayed untouched. |
| Source checklist | `_condamad/stories/CS-256-structured-facts-v1-contract/evidence/source-checklist.md` | Record mandatory source coverage. |
| Review output | `_condamad/stories/CS-256-structured-facts-v1-contract/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this contract documentation story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/structured-facts-v1-contract.md` - new canonical contract document.
- `_condamad/stories/CS-256-structured-facts-v1-contract/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-256-structured-facts-v1-contract/evidence/app-surface-status.txt` - application non-change proof.
- `_condamad/stories/CS-256-structured-facts-v1-contract/evidence/source-checklist.md` - source coverage evidence.

Likely tests:

- `docs/architecture/structured-facts-v1-contract.md` - checked by `rg` and `python` validation commands; no test file is expected to change.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/**` - out of scope; no backend application source is touched.
- `backend/tests/**` - out of scope; no backend test is touched.
- `backend/migrations/**` - out of scope; no database migration is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `python -c "from pathlib import Path; assert Path('docs/architecture/structured-facts-v1-contract.md').exists()"`
- VC3: `rg -n "structured_facts_v1|stable|hashable|non narrative" docs/architecture/structured-facts-v1-contract.md`
- VC4: `rg -n "positions|houses|major aspects|dominants|source metadata" docs/architecture/structured-facts-v1-contract.md`
- VC5: `rg -n "stable ordering|deterministic serialization|hash input boundary|AI audit" docs/architecture/structured-facts-v1-contract.md`
- VC6: `rg -n "AINarrativeInputContract|downstream|reference|calculation truth" docs/architecture/structured-facts-v1-contract.md`
- VC7: `rg -n "ChartObjectRuntimeData|chart_objects|debug raw traces|internal payloads" docs/architecture/structured-facts-v1-contract.md`
- VC8: `python -c "from app.main import app; assert 'structured_facts_v1' not in str(app.openapi())"`
- VC9: `python -c "from app.main import app; assert all('structured_facts' not in getattr(r, 'path', '') for r in app.routes)"`
- VC10: `git status --short -- backend/app frontend/src`
- VC11: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-256-structured-facts-v1-contract/evidence/validation.txt').exists()"`
- VC12: `ruff format .`
- VC13: `ruff check .`
- VC14: `pytest -q`

Before VC2, VC8, VC9 and VC11, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The contract could become a client UX projection instead of a stable factual base.
- Hash rules could omit source versions or deterministic ordering, weakening AI audit repeatability.
- `AINarrativeInputContract` could be reframed as the owner of calculation truth.
- Raw runtime objects could be documented as public payload fields.
- A documentation story could drift into API, frontend, builder, service or migration implementation.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments and public or non-trivial docstrings in French for new or significantly modified backend files.
- Keep the implementation documentation-only unless a separate user decision authorizes code or API work.
- Persist the required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-256-define-structured-facts-v1-stable-hashable-fact-projection.md`
- `docs/architecture/official-product-primitives-public-projections.md`
- `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/00-story.md`
- `_condamad/stories/CS-255-product-architecture-current-state/00-story.md`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `_condamad/stories/regression-guardrails.md`
