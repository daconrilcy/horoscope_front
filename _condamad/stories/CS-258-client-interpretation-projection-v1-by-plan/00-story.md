# Story CS-258 client-interpretation-projection-v1-by-plan: Define client_interpretation_projection_v1 By Plan
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-258-define-client-interpretation-projection-v1-by-plan.md`.
- Related dependency: CS-256 defines `structured_facts_v1` as the stable factual base for downstream projections.
- Related dependency: CS-257 defines `beginner_summary_v1` as the deterministic B2C projection for beginner use.
- Existing owner found: `docs/architecture/official-product-primitives-public-projections.md` owns public projection governance.
- Existing owner found: `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` owns AI narrative input links.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: `client_interpretation_projection_v1` lacks one B2C contract that differentiates free, basic and premium by narrative value.
- Source-alignment evidence: PASS; ACs preserve plan depth, vulgarized support elements, internal proof boundaries and LLM writer role.

## Objective

Define one canonical backend-domain contract document for `client_interpretation_projection_v1` as the B2C interpreted projection by plan.

The implementation must formalize free, basic and premium section depth, narrative depth rules, vulgarized support elements, technical client exclusions,
`structured_facts_v1` linkage, interpretive signals and LLM writer boundaries without implementing a provider, route, prompt, DB object or frontend screen.

## Target State

- `client_interpretation_projection_v1` is documented as the client-facing interpretation projection for free, basic and premium plans.
- Free, basic and premium differ by narrative depth, personalization, section count, predictions and explanatory richness.
- The projection exposes vulgarized client support elements, not raw factual dumps, trace IDs, graph payloads, prompt internals or audit internals.
- Technical proof, scoring evidence and calculation details remain internal or controlled expert surfaces.
- `structured_facts_v1` is named as the upstream factual source and `beginner_summary_v1` remains a simpler sibling projection.
- Interpretive signals are named as pre-narrative inputs that guide text, not as public technical payloads.
- The LLM role is documented as rédacteur that writes from prepared facts and signals, not as astrologer calculator or source of calculation truth.
- No backend runtime builder, service, route, model, database object, migration, frontend file, prompt template or provider integration is created by this story.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-258-define-client-interpretation-projection-v1-by-plan.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-258`.
- Evidence 3: `docs/architecture/official-product-primitives-public-projections.md` - public projection registry owner found.
- Evidence 4: `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md` - upstream factual projection dependency read.
- Evidence 5: `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/00-story.md` - sibling B2C projection dependency read.
- Evidence 6: `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` - interpretive signal and AI input owner found.
- Evidence 7: `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` - existing public projection links found.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output and targeted ID lookup only.
- Source-alignment evidence: PASS; the story answers every brief stake without turning plan depth into technical payload exposure.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Canonical contract documentation for `client_interpretation_projection_v1`.
  - Free, basic and premium B2C plan sections and narrative depth rules.
  - Vulgarized support elements, technical client exclusions and internal proof boundaries.
  - Relationship to `structured_facts_v1`, interpretive signals and LLM writer responsibility.
  - Negative checks for raw runtime, prompt/provider work, expert projection, API route and frontend drift.
  - Persistent evidence artifacts for contract validation scans.
- Out of scope:
  - Frontend UI, public API exposure, DB schema, migrations, auth, i18n, styling, build tooling and generated clients.
  - Runtime projection builder, service orchestration, serializer, persistence, provider integration and final prompts.
  - `expert_technical_projection_v1`, admin roles, astrologer debug data and registry enrichment.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No public endpoint, OpenAPI schema, response serializer or API contract for `client_interpretation_projection_v1`.
  - No runtime projection builder, service orchestration, database table or migration.
  - No provider LLM implementation, definitive prompt template, admin role definition or expert technical projection exposure.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain interpretation projection contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only `client_interpretation_projection_v1` contract documentation, product registry alignment and story evidence artifacts.
  - Reuse existing public projection, `structured_facts_v1`, `beginner_summary_v1` and AI narrative input terminology.
  - Keep backend runtime code, API routes, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Keep raw runtime payloads, proof internals, prompt internals and expert technical fields outside the B2C projection.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product asks to expose expert technical fields or provider internals inside the B2C client projection.
- Additional validation rules:
  - The contract must name `client_interpretation_projection_v1` exactly.
  - The contract must define free, basic and premium plan sections with differentiated product depth.
  - The contract must define narrative depth rules for personalization, section count, predictions and explanatory richness.
  - The contract must describe vulgarized support elements for clients without exposing raw technical proof.
  - The contract must list technical client exclusions, including runtime internals, prompt internals and scoring proof internals.
  - The contract must link `structured_facts_v1`, interpretive signals and the LLM writer role without making the LLM a calculator.
  - The contract must exclude `expert_technical_projection_v1`, definitive prompts, provider implementation and admin roles.
  - `app.routes`, `app.openapi()`, `pytest` and scoped `git status` prove no public API or application surface drift.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Existing projection registry and AI input owners prove the source boundary before documentation claims it. |
| Baseline Snapshot | yes | Before and after evidence must prove one contract document, registry alignment and no app-surface drift. |
| Ownership Routing | yes | Product registry, projection contract, source facts, signals and LLM writer boundaries need separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this single projection contract story. |
| Contract Shape | yes | `client_interpretation_projection_v1` has exact plan variants, depth rules, exclusions and source links. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Raw runtime, proof internals, expert projection and provider work must stay out. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `client_interpretation_projection_v1` is documented. | Evidence profile: baseline_before_after_diff; `python` checks the contract document path. |
| AC2 | Plan sections are explicit. | Evidence profile: json_contract_shape; `rg` checks free, basic, premium and section matrix wording. |
| AC3 | Narrative depth rules are explicit. | Evidence profile: json_contract_shape; `rg` checks depth, personalization, predictions and explanatory richness. |
| AC4 | Client support elements are vulgarized. | Evidence profile: json_contract_shape; `rg` checks vulgarized support elements and client-readable wording. |
| AC5 | Technical payload exposure is forbidden. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks raw runtime and proof internals. |
| AC6 | Source linkage is explicit. | Evidence profile: json_contract_shape; `rg` checks `structured_facts_v1`, interpretive signals and LLM writer role. |
| AC7 | Expert projection remains out of scope. | Evidence profile: external_usage_blocker; `rg` checks `expert_technical_projection_v1` exclusion wording. |
| AC8 | Public API surface stays unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`. |
| AC9 | Application source surfaces remain unchanged. | Evidence profile: repo_wide_negative_scan; `python` records scoped `git status --short` output. |
| AC10 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-258 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect existing public projection, structured facts, beginner summary and AI narrative owners before writing the contract. (AC: AC1, AC6)
- [ ] Task 2: Create `docs/architecture/client-interpretation-projection-v1-contract.md` with a French global file comment. (AC: AC1)
- [ ] Task 3: Define the B2C role of `client_interpretation_projection_v1` for free, basic and premium. (AC: AC1, AC2)
- [ ] Task 4: Document the plan section matrix for free, basic and premium. (AC: AC2)
- [ ] Task 5: Document narrative depth rules for personalization, section count, predictions and explanatory richness. (AC: AC3)
- [ ] Task 6: Document vulgarized support elements that can help clients understand the interpretation. (AC: AC4)
- [ ] Task 7: Document technical client exclusions and internal proof boundaries. (AC: AC5, AC7)
- [ ] Task 8: Link `structured_facts_v1`, interpretive signals and the LLM writer role. (AC: AC6)
- [ ] Task 9: Align `docs/architecture/official-product-primitives-public-projections.md` to name CS-258 and the new projection. (AC: AC1, AC2)
- [ ] Task 10: Persist validation, scoped status and source checklist evidence under the CS-258 evidence folder. (AC: AC8, AC9, AC10)

## Files to Inspect First

- `_story_briefs/cs-258-define-client-interpretation-projection-v1-by-plan.md` - source contract.
- `docs/architecture/official-product-primitives-public-projections.md` - existing public projection governance owner.
- `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md` - upstream factual projection dependency.
- `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/00-story.md` - sibling beginner B2C projection dependency.
- `docs/architecture/structured-facts-v1-contract.md` - expected upstream factual contract after CS-256 implementation.
- `docs/architecture/beginner-summary-v1-contract.md` - expected sibling beginner contract after CS-257 implementation.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` - existing interpretive signal owner.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` - existing public projection link builder owner.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `docs/architecture/official-product-primitives-public-projections.md` for product projection ownership.
  - `docs/architecture/structured-facts-v1-contract.md` for upstream factual projection after CS-256.
  - `docs/architecture/beginner-summary-v1-contract.md` for sibling B2C projection after CS-257.
  - `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` for interpretive signal terminology.
  - `app.routes`, `app.openapi()`, scoped `git status`, `pytest` and targeted `rg` scans for no public API or app-source drift.
- Secondary evidence:
  - Targeted `rg` scans over `docs/architecture/client-interpretation-projection-v1-contract.md`.
- Static scans alone are not sufficient because:
  - public API neutrality and application-source non-change must be proven from the loaded app and scoped status.

## Contract Shape

- Contract type:
  - Markdown backend-domain contract for a future controlled B2C interpretation projection.
- Fields:
  - `projection_id`: exact value `client_interpretation_projection_v1`.
  - `audience`: public-user, free, basic and premium B2C clients.
  - `source_projection`: exact value `structured_facts_v1`.
  - `sibling_projection`: exact value `beginner_summary_v1`.
  - `plan_variant`: one of `free`, `basic` or `premium`.
  - `sections`: plan-specific section list with readable titles and intent.
  - `narrative_depth`: section count, personalization depth, predictions depth and explanatory richness.
  - `support_elements`: vulgarized highlights, confidence wording, source labels and display hints.
  - `llm_role`: rédacteur from prepared facts and signals, not calculator or truth owner.
  - `excluded_surfaces`: raw runtime, proof internals, prompt internals, provider internals and expert technical fields.
- Required fields:
  - `projection_id`
  - `audience`
  - `source_projection`
  - `plan_variant`
  - `sections`
  - `narrative_depth`
  - `support_elements`
  - `llm_role`
  - `excluded_surfaces`
- Optional fields:
  - `prediction_window` only for plan variants that authorize predictions.
  - `personalization_notes` only when source signals support plan-specific personalization.
  - `upgrade_hint` only when product copy remains client-readable and non-technical.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - documentation only; no runtime JSON serializer is added.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose `client_interpretation_projection_v1` from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-258-define-client-interpretation-projection-v1-by-plan.md`
  - `docs/architecture/official-product-primitives-public-projections.md`
  - `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md`
  - `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/00-story.md`
  - `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`
- Comparison after implementation:
  - `docs/architecture/client-interpretation-projection-v1-contract.md`
  - `docs/architecture/official-product-primitives-public-projections.md`
  - `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/evidence/validation.txt`
  - `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended repository delta is one architecture contract document, one registry alignment and CONDAMAD story/evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| `client_interpretation_projection_v1` contract | `docs/architecture/client-interpretation-projection-v1-contract.md` | API routers, frontend, DB models |
| Product primitive registry | `docs/architecture/official-product-primitives-public-projections.md` | duplicated projection registry |
| Upstream factual source | `docs/architecture/structured-facts-v1-contract.md` | B2C interpretation contract as factual owner |
| Beginner sibling projection | `docs/architecture/beginner-summary-v1-contract.md` | client interpretation contract as beginner owner |
| Interpretive signal source | `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` | prompt templates or provider code |
| Evidence artifacts | `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse existing public projection governance wording instead of creating a parallel product registry.
- Reuse CS-256 `structured_facts_v1` terminology for the upstream factual source.
- Reuse CS-257 `beginner_summary_v1` terminology for the simpler B2C projection boundary.
- Reuse `AINarrativeInterpretiveSignals` vocabulary for pre-narrative signal references.
- Keep one canonical `client_interpretation_projection_v1` document and one projection identifier.
- Do not add external packages, scripts, API schemas, frontend helpers, builders, services, prompts or generated clients.

## No Legacy / Forbidden Paths

- No legacy public route path may be added for this projection.
- No compatibility projection path may bypass `client_interpretation_projection_v1`.
- No fallback branch may expose raw runtime objects as the B2C interpretation projection.
- Do not create aliases, shims, wrappers or parallel documents for the same projection contract.
- Do not place raw runtime payloads, proof internals, prompt internals, provider internals or expert technical fields inside the projection.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/**`
  - `backend/app/infra/db/**`
  - `backend/migrations/**`
  - generated OpenAPI clients
  - prompt template files as projection contract owners

## Reintroduction Guard

- Guard target:
  - raw runtime payloads cannot become B2C client interpretation payloads;
  - proof internals and scoring evidence cannot become client-facing support elements;
  - expert technical fields cannot enter the free/basic/premium client projection;
  - the LLM cannot be documented as calculator or source of calculation truth;
  - public API routes and OpenAPI schemas cannot be introduced by this story.
- Guard mechanism:
  - targeted `rg` checks for required contract terms and forbidden raw-surface terms;
  - `app.routes` and `app.openapi()` neutrality checks;
  - scoped `git status --short` for application roots;
  - persisted evidence under the CS-258 evidence folder.
- Guard owner:
  - `docs/architecture/client-interpretation-projection-v1-contract.md`;
  - `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/evidence/validation.txt`;
  - `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/evidence/app-surface-status.txt`.
- Guard evidence:
  - `rg -n "client_interpretation_projection_v1|free|basic|premium|LLM|rédacteur" docs/architecture`;
  - `python -c "from app.main import app; assert 'client_interpretation_projection_v1' not in str(app.openapi())"`;
  - `python -c "from app.main import app; assert all('client_interpretation' not in getattr(r, 'path', '') for r in app.routes)"`;
  - `git status --short -- backend/app frontend/src backend/tests backend/migrations`.

## Regression Guardrails

Scope vector:

- backend-domain contract documentation: yes;
- docs architecture contract: yes;
- backend interpretation source reference: yes;
- API route change: no;
- frontend implementation: no;
- DB, auth, i18n, style, build and migration: no.

Selected guardrails:

- RG-002: backend app paths are referenced only as source owners, not modified; use `git status` and loaded app checks.
- Registry gap: no exact `client_interpretation_projection_v1` guardrail exists; use story-local `rg`, `app.routes` and `app.openapi()`.

Non-applicable examples:

- RG-041 entitlement documentation is out of scope because this story defines projection depth, not access rights.
- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Contract document | `docs/architecture/client-interpretation-projection-v1-contract.md` | Keep the canonical B2C interpretation projection contract. |
| Validation output | `evidence/validation.txt` | Keep content scans and story execution validation. |
| Application surface status | `evidence/app-surface-status.txt` | Prove app roots stayed untouched. |
| Source checklist | `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/evidence/source-checklist.md` | Record mandatory source coverage. |
| Review output | `generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this contract documentation story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/client-interpretation-projection-v1-contract.md` - new canonical contract document.
- `docs/architecture/official-product-primitives-public-projections.md` - align the public projection registry with CS-258.
- `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/evidence/app-surface-status.txt` - application non-change proof.
- `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/evidence/source-checklist.md` - source coverage evidence.

Likely tests:

- `docs/architecture/client-interpretation-projection-v1-contract.md` - checked by `rg` and `python` validation commands.
- `backend/tests/architecture/test_api_contract_neutrality.py` - targeted architecture regression check for public projection neutrality.

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
- VC2: `python -c "from pathlib import Path; assert Path('docs/architecture/client-interpretation-projection-v1-contract.md').exists()"`
- VC3: `rg -n "client_interpretation_projection_v1|free|basic|premium" docs/architecture/client-interpretation-projection-v1-contract.md`
- VC4: `rg -n "section matrix|narrative depth|personalization|predictions|explanatory richness" docs/architecture/client-interpretation-projection-v1-contract.md`
- VC5: `rg -n "vulgarized support elements|client-readable|technical client exclusions" docs/architecture/client-interpretation-projection-v1-contract.md`
- VC6: `rg -n "structured_facts_v1|interpretive signals|LLM|rédacteur|not calculator" docs/architecture/client-interpretation-projection-v1-contract.md`
- VC7: `rg -n "expert_technical_projection_v1|provider implementation|definitive prompt|admin roles" docs/architecture/client-interpretation-projection-v1-contract.md`
- VC8: `python -c "from app.main import app; assert 'client_interpretation_projection_v1' not in str(app.openapi())"`
- VC9: `python -c "from app.main import app; assert all('client_interpretation' not in getattr(r, 'path', '') for r in app.routes)"`
- VC10: `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`
- VC11: `git status --short -- backend/app frontend/src backend/tests backend/migrations`
- VC12: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/evidence/validation.txt').exists()"`
- VC13: `ruff format .`
- VC14: `ruff check .`
- VC15: `pytest -q`
- VC16: `rg -n "client_interpretation|free|basic|premium|LLM|rédacteur|runtime technique" .\docs .\_story_briefs`
- VC17: `git status --short -- backend/app frontend/src`

Before VC2, VC8, VC9 and VC12, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The projection could vary plans by exposing technical payloads instead of increasing narrative and functional value.
- Premium could drift into `expert_technical_projection_v1` instead of remaining B2C client interpretation.
- The LLM could be framed as calculation authority instead of rédacteur from prepared facts and signals.
- Vulgarized support elements could become raw proof, scoring evidence or trace exposure.
- A documentation story could drift into API, frontend, builder, service, prompt, provider or migration implementation.

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

- `_story_briefs/cs-258-define-client-interpretation-projection-v1-by-plan.md`
- `docs/architecture/official-product-primitives-public-projections.md`
- `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md`
- `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/00-story.md`
- `docs/architecture/structured-facts-v1-contract.md`
- `docs/architecture/beginner-summary-v1-contract.md`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`
- `_condamad/stories/regression-guardrails.md`
