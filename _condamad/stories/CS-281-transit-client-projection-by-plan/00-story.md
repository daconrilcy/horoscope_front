# Story CS-281 transit-client-projection-by-plan: Define Transit Client Projection By Plan
Status: done

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-281-define-transit-client-projection-by-plan.md`.
- Related dependency: CS-280 keeps `transit_chart_v1` internal and non-public.
- Related dependency: CS-258 defines the client interpretation projection pattern by plan.
- Existing owner found: `docs/architecture/product-architecture-current-state-2026-05-24.md` records temporal public runtime as blocked.
- Existing owner found: `docs/architecture/official-product-primitives-public-projections.md` owns projection governance.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: future B2C transit projection by plan is undefined while runtime exposure remains blocked by proof and doctrine gates.
- Source-alignment evidence: PASS; ACs preserve plan differentiation, proof gate blocking, LLM writer limits and non-public transit runtime.

## Objective

Define one canonical backend-domain contract document for a future `transit_client_projection_v1` segmented by free, basic and premium plans.

The implementation must specify client-visible transit content, degraded states, unavailable states, required proof, LLM writer boundaries and technical
exclusions without implementing a runtime projection, route, frontend screen, provider call, DB object, migration or product promise.

## Target State

- `transit_client_projection_v1` is documented as a future B2C projection layered above internal `transit_chart_v1`.
- Free, basic and premium differ by narration, timing depth, explanatory richness and guidance framing, not by debug payload access.
- Degraded and unavailable states are explicit, including proof-gate blocked, data incomplete, unsupported technique and doctrine-limited states.
- Required proof is mandatory before exposure and names astronomical evidence, source versions, doctrine limits and projection validation evidence.
- Clients receive narrative and client-readable support elements only, never raw runtime objects, graph traces, proof internals or debug fields.
- The LLM role is documented as rédacteur from prepared transit facts and signals, not as calculator, proof owner or doctrine authority.
- No public API route, OpenAPI schema, backend runtime builder, frontend component, DB model, migration or entitlement implementation is created.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-281-define-transit-client-projection-by-plan.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-281`.
- Evidence 3: `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/00-story.md` - plan projection pattern inspected.
- Evidence 4: `_condamad/stories/CS-280-internal-transit-runtime/00-story.md` - internal transit runtime boundary inspected.
- Evidence 5: `docs/architecture/product-architecture-current-state-2026-05-24.md` - temporal public runtime blocker inspected.
- Evidence 6: `docs/architecture/official-product-primitives-public-projections.md` - projection governance owner inspected.
- Evidence 7: `backend/tests/architecture/test_api_contract_neutrality.py` - public API neutrality evidence owner exists.
- Evidence 8: guardrail resolver run for backend-domain documentation and transit projection scope; no exact route guardrail was returned.
- Repository structure alert: `docs/architecture/transit-client-projection-v1-contract.md` is absent in this workspace.
- Source-alignment evidence: PASS; the final contract keeps client exposure blocked until proof gate validation.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Canonical contract documentation for future `transit_client_projection_v1`.
  - Free, basic and premium content boundaries for transit interpretation.
  - Degraded states, unavailable states, required proof, doctrine limits and LLM writer role.
  - Negative checks proving no public route, OpenAPI schema, frontend surface or raw runtime exposure is introduced.
  - Persistent evidence artifacts for contract validation scans.
- Out of scope:
  - Frontend UI, public API exposure, DB schema, migrations, auth, i18n, styling, build tooling and generated clients.
  - Runtime projection builder, service orchestration, serializer, persistence, provider integration and final prompts.
  - Entitlement enforcement, product pricing, commercial promise, admin expert surface and registry enrichment.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No public endpoint, OpenAPI schema, response serializer or API contract for transit clients.
  - No runtime projection builder, service orchestration, database table or migration.
  - No provider LLM implementation, definitive prompt template, entitlement policy or premium product copy.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain projection contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only `transit_client_projection_v1` contract documentation, projection governance alignment and story evidence artifacts.
  - Reuse CS-258 plan projection rules and CS-280 transit non-public runtime boundaries.
  - Keep backend runtime code, API routes, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Keep raw runtime payloads, graph traces, proof internals, debug fields and expert technical data outside the client projection.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product asks to expose transit data before proof gate validation or to show raw runtime/debug fields to clients.
- Additional validation rules:
  - The contract must name `transit_client_projection_v1` exactly.
  - The contract must define free, basic and premium transit content boundaries.
  - The contract must state that plans differ by narration and richness, not debug payload access.
  - The contract must define degraded and unavailable states.
  - The contract must require proof gate validation before public exposure.
  - The contract must define the LLM role as rédacteur from prepared facts and signals.
  - The contract must exclude public API, frontend, backend runtime implementation, DB, migration and product promise work.
  - `app.routes`, `app.openapi()`, `pytest` and scoped `git status` prove no public API or application surface drift.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Existing transit runtime, projection docs and loaded app checks prove the non-public boundary. |
| Baseline Snapshot | yes | Before and after evidence must prove documentation-only change and no app-surface drift. |
| Ownership Routing | yes | Transit runtime, client projection, proof gate and LLM writer boundaries need separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this single projection contract story. |
| Contract Shape | yes | `transit_client_projection_v1` needs exact plan, state, proof and exclusion fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Public transit routes, raw runtime exposure and debug-by-plan drift must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `transit_client_projection_v1` is documented. | Evidence profile: baseline_before_after_diff; `python` checks the contract document path. |
| AC2 | Plan content boundaries are explicit. | Evidence profile: json_contract_shape; `rg` checks free, basic, premium and transit content wording. |
| AC3 | Plan differentiation excludes debug access. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks narration, richness and debug exclusion wording. |
| AC4 | Degraded states are explicit. | Evidence profile: json_contract_shape; `rg` checks degraded, unavailable and proof-gate states. |
| AC5 | Proof gate blocks exposure. | Evidence profile: baseline_before_after_diff; `rg` checks proof gate and non-public exposure wording. |
| AC6 | LLM writer boundaries are explicit. | Evidence profile: json_contract_shape; `rg` checks LLM, rédacteur and not calculator wording. |
| AC7 | Raw runtime stays hidden. | Evidence profile: targeted_forbidden_symbol_scan; `python` checks `app.openapi()` and `app.routes`; `rg` checks exclusions. |
| AC8 | Public API surface stays unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`. |
| AC9 | Application source surfaces remain unchanged. | Evidence profile: repo_wide_negative_scan; `python` records scoped `git status --short` output. |
| AC10 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-281 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-258, CS-280 and projection governance before writing the transit client contract. (AC: AC1)
- [ ] Task 2: Create `docs/architecture/transit-client-projection-v1-contract.md` with a French global file comment. (AC: AC1)
- [ ] Task 3: Define free, basic and premium transit content boundaries. (AC: AC2)
- [ ] Task 4: Define plan differentiation through narration, timing depth and explanatory richness. (AC: AC2, AC3)
- [ ] Task 5: Define degraded and unavailable states for proof, data, technique and doctrine limits. (AC: AC4)
- [ ] Task 6: Define mandatory proof gate evidence before exposure. (AC: AC5)
- [ ] Task 7: Define the LLM rédacteur role and forbid calculation authority. (AC: AC6)
- [ ] Task 8: Document raw runtime, trace, debug, API, frontend and product-promise exclusions. (AC: AC7, AC8, AC9)
- [ ] Task 9: Align projection governance docs to name the blocked future transit projection. (AC: AC1, AC5)
- [ ] Task 10: Persist validation, scoped status and source checklist evidence under the CS-281 evidence folder. (AC: AC8, AC9, AC10)

## Files to Inspect First

- `_story_briefs/cs-281-define-transit-client-projection-by-plan.md` - source contract.
- `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/00-story.md` - plan projection pattern.
- `_condamad/stories/CS-280-internal-transit-runtime/00-story.md` - internal transit runtime boundary.
- `docs/architecture/product-architecture-current-state-2026-05-24.md` - temporal public runtime blocker and product architecture.
- `docs/architecture/official-product-primitives-public-projections.md` - public projection governance owner.
- `backend/tests/architecture/test_api_contract_neutrality.py` - existing OpenAPI and route neutrality tests.
- `docs/architecture/transit-client-projection-v1-contract.md` - expected implementation-created path.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `_condamad/stories/CS-280-internal-transit-runtime/00-story.md` for non-public `transit_chart_v1` boundaries.
  - `docs/architecture/product-architecture-current-state-2026-05-24.md` for temporal public runtime blocker status.
  - `docs/architecture/official-product-primitives-public-projections.md` for projection governance.
  - `app.routes`, `app.openapi()`, scoped `git status`, `pytest` and targeted `rg` scans for no public API or app-source drift.
- Secondary evidence:
  - Targeted `rg` scans over `docs/architecture/transit-client-projection-v1-contract.md`.
- Static scans alone are not sufficient because:
  - public API neutrality and application-source non-change must be proven from the loaded app and scoped status.

## Contract Shape

- Contract type:
  - Markdown backend-domain contract for a future controlled B2C transit projection.
- Fields:
  - `projection_id`: exact value `transit_client_projection_v1`.
  - `audience`: public-user, free, basic and premium B2C clients.
  - `source_runtime`: exact value `transit_chart_v1`.
  - `source_projection_policy`: references CS-258 plan projection rules.
  - `plan_variant`: one of `free`, `basic` or `premium`.
  - `client_content`: plan-specific narrative sections and support elements.
  - `degraded_state`: proof, data, technique or doctrine limitation state shown to clients.
  - `proof_gate`: required evidence status before exposure.
  - `llm_role`: rédacteur from prepared facts and signals, not calculator or proof owner.
  - `excluded_surfaces`: raw runtime, graph traces, debug fields, API route, frontend and product promise.
- Required fields:
  - `projection_id`
  - `audience`
  - `source_runtime`
  - `plan_variant`
  - `client_content`
  - `degraded_state`
  - `proof_gate`
  - `llm_role`
  - `excluded_surfaces`
- Optional fields:
  - `upgrade_hint` only as non-technical product guidance.
  - `timing_window` only after proof gate validation names the supported temporal window.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - documentation only; no runtime JSON serializer is added.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose `transit_client_projection_v1` or public transit paths from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-281-define-transit-client-projection-by-plan.md`
  - `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/00-story.md`
  - `_condamad/stories/CS-280-internal-transit-runtime/00-story.md`
  - `docs/architecture/product-architecture-current-state-2026-05-24.md`
  - `docs/architecture/official-product-primitives-public-projections.md`
- Comparison after implementation:
  - `docs/architecture/transit-client-projection-v1-contract.md`
  - `docs/architecture/official-product-primitives-public-projections.md`
  - `_condamad/stories/CS-281-transit-client-projection-by-plan/evidence/validation.txt`
  - `_condamad/stories/CS-281-transit-client-projection-by-plan/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended repository delta is one architecture contract document, one projection governance alignment and CONDAMAD evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Transit client projection contract | `docs/architecture/transit-client-projection-v1-contract.md` | API routers, frontend, DB models |
| Product projection governance | `docs/architecture/official-product-primitives-public-projections.md` | duplicated transit projection registry |
| Temporal runtime boundary | `backend/app/domain/astrology/runtime/transit_chart_runtime.py` | public serializer or frontend |
| Proof gate policy | existing astronomical proof and product architecture docs | client copy without evidence status |
| Plan projection pattern | CS-258 client projection story and docs | transit-specific entitlement logic |
| LLM writer boundary | AI narrative input and projection contracts | provider code or prompt owner |
| Evidence artifacts | `_condamad/stories/CS-281-transit-client-projection-by-plan/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse CS-258 plan projection vocabulary instead of creating a second plan differentiation model.
- Reuse CS-280 non-public transit runtime vocabulary instead of implying runtime exposure.
- Reuse product architecture blocker wording for temporal public runtime.
- Reuse public projection governance docs instead of creating a parallel projection registry.
- Reuse existing proof gate and doctrine vocabulary instead of embedding a transit-only proof policy.
- Keep one canonical `transit_client_projection_v1` document and one projection identifier.
- Do not add external packages, scripts, API schemas, frontend helpers, builders, services, prompts or generated clients.

## No Legacy / Forbidden Paths

- No legacy public route path may be added for transit projection.
- No compatibility projection path may bypass `transit_client_projection_v1`.
- No fallback branch may expose raw transit runtime objects as a client projection.
- Do not create aliases, shims, wrappers or parallel documents for the same transit client projection contract.
- Do not expose raw runtime payloads, graph traces, proof internals, debug fields or expert technical data through plan tiers.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/**`
  - `backend/app/infra/db/**`
  - `backend/migrations/**`
  - generated OpenAPI clients
  - prompt template files as projection contract owners

## Reintroduction Guard

- Guard target:
  - transit client projection cannot become a public route or OpenAPI schema in this story;
  - plan differentiation cannot grant debug, trace or raw runtime payload access;
  - proof gate validation cannot be softened into optional documentation;
  - the LLM cannot be documented as calculator, proof owner or doctrine authority;
  - frontend, DB, migration and entitlement implementation cannot enter this documentation story.
- Guard mechanism:
  - targeted `rg` checks for required contract terms and forbidden raw-surface terms;
  - `app.routes` and `app.openapi()` neutrality checks;
  - scoped `git status --short` for application roots;
  - persisted evidence under the CS-281 evidence folder.
- Guard owner:
  - `docs/architecture/transit-client-projection-v1-contract.md`;
  - `_condamad/stories/CS-281-transit-client-projection-by-plan/evidence/validation.txt`;
  - `_condamad/stories/CS-281-transit-client-projection-by-plan/evidence/app-surface-status.txt`.
- Guard evidence:
  - `rg -n "transit_client_projection_v1|free|basic|premium|proof gate|non public|LLM" docs/architecture`;
  - `python -c "from app.main import app; assert 'transit_client_projection_v1' not in str(app.openapi())"`;
  - `python -c "from app.main import app; assert all('transit' not in getattr(r, 'path', '') for r in app.routes)"`;
  - `git status --short -- backend/app frontend/src`.

## Regression Guardrails

Scope vector:

- backend-domain contract documentation: yes;
- docs architecture contract: yes;
- transit runtime referenced but not modified: yes;
- API route change: no;
- frontend implementation: no;
- DB, auth, i18n, style, build and migration: no.

Selected guardrails:

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `Routeurs API v1` | API router ownership must stay untouched. | `app.routes`; `rg` API scan. |
| Registry gap | No exact `transit_client_projection_v1` guardrail exists. | Story-local proof and API guards. |

Non-applicable examples:

- RG-041 entitlement documentation is out of scope because this story defines projection content, not access enforcement.
- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Contract document | `docs/architecture/transit-client-projection-v1-contract.md` | Keep the canonical future transit client projection contract. |
| Validation output | `_condamad/stories/CS-281-transit-client-projection-by-plan/evidence/validation.txt` | Keep content scans and story execution validation. |
| Application surface status | `_condamad/stories/CS-281-transit-client-projection-by-plan/evidence/app-surface-status.txt` | Prove app roots stayed untouched. |
| Source checklist | `_condamad/stories/CS-281-transit-client-projection-by-plan/evidence/source-checklist.md` | Record mandatory source coverage. |
| Review output | `_condamad/stories/CS-281-transit-client-projection-by-plan/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this contract documentation story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/transit-client-projection-v1-contract.md` - new canonical contract document.
- `docs/architecture/official-product-primitives-public-projections.md` - align projection governance with the blocked future transit projection.
- `_condamad/stories/CS-281-transit-client-projection-by-plan/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-281-transit-client-projection-by-plan/evidence/app-surface-status.txt` - application non-change proof.
- `_condamad/stories/CS-281-transit-client-projection-by-plan/evidence/source-checklist.md` - source coverage evidence.

Likely tests:

- `docs/architecture/transit-client-projection-v1-contract.md` - checked by `rg` and `python` validation commands.
- `backend/tests/architecture/test_api_contract_neutrality.py` - targeted architecture regression check for public transit neutrality.

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
- VC2: `python -c "from pathlib import Path; assert Path('docs/architecture/transit-client-projection-v1-contract.md').exists()"`
- VC3: `rg -n "transit_client_projection_v1|free|basic|premium" docs/architecture/transit-client-projection-v1-contract.md`
- VC4: `rg -n "narration|richness|debug|raw runtime|trace" docs/architecture/transit-client-projection-v1-contract.md`
- VC5: `rg -n "degraded|unavailable|proof gate|non public" docs/architecture/transit-client-projection-v1-contract.md`
- VC6: `rg -n "LLM|rédacteur|not calculator|proof owner" docs/architecture/transit-client-projection-v1-contract.md`
- VC7: `python -c "from app.main import app; assert 'transit_client_projection_v1' not in str(app.openapi())"`
- VC8: `python -c "from app.main import app; assert all('transit' not in getattr(r, 'path', '') for r in app.routes)"`
- VC9: `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`
- VC10: `git status --short -- backend/app frontend/src`
- VC11: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-281-transit-client-projection-by-plan/evidence/validation.txt').exists()"`
- VC12: `ruff format .`
- VC13: `ruff check .`
- VC14: `pytest -q`
- VC15: `rg -n "transit|free|basic|premium|proof gate|non public|LLM" .\docs .\_story_briefs`

Before VC2, VC7, VC8 and VC11, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The future transit projection could be treated as public before proof gate validation.
- Free, basic and premium could drift into debug access tiers instead of narrative richness tiers.
- The LLM could be framed as calculation authority instead of rédacteur from prepared facts and signals.
- Degraded states could hide proof or doctrine limits behind reassuring product wording.
- A documentation story could drift into API, frontend, runtime builder, provider, entitlement or migration implementation.

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

- `_story_briefs/cs-281-define-transit-client-projection-by-plan.md`
- `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/00-story.md`
- `_condamad/stories/CS-280-internal-transit-runtime/00-story.md`
- `docs/architecture/product-architecture-current-state-2026-05-24.md`
- `docs/architecture/official-product-primitives-public-projections.md`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `_condamad/stories/regression-guardrails.md`
