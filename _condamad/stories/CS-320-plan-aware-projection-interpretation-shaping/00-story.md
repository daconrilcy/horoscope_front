# Story CS-320 plan-aware-projection-interpretation-shaping: Define LLM And Front Differentiation By B2C Plan
Status: ready-to-review

## Trigger / Source

- Source type: repo-informed follow-up brief.
- Source reference: `_story_briefs/cs-320-definir-differenciation-llm-front-par-plan-b2c.md`.
- Prior divergence source: `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md`.
- Related source: `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/00-story.md`.
- Related closure: `_condamad/stories/CS-317-cloturer-cs315-final-evidence-validation-runtime/00-story.md`.
- Related product signoff evidence: `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/10-final-evidence.md`.
- Related runtime closure evidence: `_condamad/stories/CS-317-cloturer-cs315-final-evidence-validation-runtime/generated/10-final-evidence.md`.
- Related frontend guard: `_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/generated/10-final-evidence.md`.
- Decision artifact: `docs/architecture/natal-projection-plan-matrix-product-decision.md`.
- Runtime evidence: `backend/tests/api/test_projection_real_conditions.py`.
- Public API contract owner: `backend/app/services/api_contracts/public/projections.py`.
- Feature page rendering owner: `frontend/src/features/natal-chart/NatalInterpretation.tsx`.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: CS-315 keeps all B2C calculations available, but LLM and frontend differentiation still need one executable contract.
- Source-alignment evidence: PASS; the story preserves full calculation for all plans and moves differentiation after backend projection output.

## Objective

Define one plan-aware product and technical contract for natal projection interpretation output after calculation.

The contract must specify LLM input subsets, editorial depth profiles, precision/detail levels and frontend visibility for `free`, `basic` and `premium`.
`beginner_summary_v1` and `client_interpretation_projection_v1` stay executable for every supported B2C plan.

## Target State

- `client_interpretation_projection_v1` keeps full calculation execution for `free`, `basic` and `premium`.
- A canonical product/technical contract maps each plan to LLM input selection, editorial depth, precision, detail and frontend visibility rules.
- The contract names the future backend, LLM and frontend owners that must implement the plan shaping without moving policy into React.
- Future backend validations prove all B2C plans still receive HTTP 200 for `client_interpretation_projection_v1`.
- Future frontend validations prove rendering follows backend-shaped sections and display hints instead of a local entitlement matrix.
- No immediate prompt, provider integration, frontend rendering rewrite or backend access restriction is included in this story.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-320-definir-differenciation-llm-front-par-plan-b2c.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-320`.
- Evidence 3: `docs/architecture/natal-projection-plan-matrix-product-decision.md` - product decision says differentiation happens after calculation.
- Evidence 4: `backend/tests/api/test_projection_real_conditions.py` - runtime test posts `client_interpretation_projection_v1` for all B2C plans.
- Evidence 5: `docs/architecture/client-interpretation-projection-v1-contract.md` - existing plan-depth contract read.
- Evidence 6: `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` - current builder sections and display hints read.
- Evidence 7: `backend/tests/unit/domain/astrology/test_client_interpretation_projection_v1_builder.py` - existing plan builder tests read.
- Evidence 8: `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - frontend projection rendering owner found.
- Evidence 9: `frontend/src/tests/component-architecture-guards.test.ts` - existing React entitlement matrix guard found.
- Evidence 10: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output and targeted ID lookup only.
- Evidence 11: `_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/generated/10-final-evidence.md` - React policy guard closure read.
- Source-alignment evidence: PASS; ACs cover the brief's backend, product, frontend and validation stakes without blocking calculations.

## Domain Boundary

- Domain: projection-plan-differentiation
- In scope:
  - Backend/projection contract for plan-specific LLM input subsets.
  - Editorial depth, precision and detail profile for `free`, `basic` and `premium`.
  - Frontend section visibility contract emitted from backend projection payloads.
  - Future validation targets that stop a return to access blocking or React local policy.
  - Owner routing for future backend builder, LLM prompt/depth and frontend rendering implementation stories.
  - Future validation targets that prove full calculation still executes for all B2C plans.
- Out of scope:
  - Stripe, pricing, checkout, subscription, DB schema, migrations, auth, i18n, styling and build tooling.
  - React-owned entitlement policy, local access matrix, provider LLM integration, final prompt text, runtime builder changes,
    frontend rendering changes and new public route creation.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No backend restriction that blocks `client_interpretation_projection_v1` for `free`, `basic` or `premium`.
  - No frontend-owned access policy or commercial entitlement matrix.
  - No database table, Alembic migration, Stripe plan rule, generated client or LLM provider call.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend projection shaping plus frontend rendering contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Define only the plan-aware shaping fields for LLM input selection, editorial depth and frontend visibility.
  - Define precision and detail-level semantics for each B2C plan.
  - Preserve the requirement that projection execution remains available for `free`, `basic` and `premium`.
  - Route future implementation to `client_interpretation_projection_v1` and `structured_facts_v1` owners before adjacent helpers.
  - Keep API routes, DB, migrations, auth, i18n, style, build tooling, Stripe and subscription files unchanged.
  - Keep React as a renderer of backend-shaped projection sections, not a policy owner.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product owners cannot define the per-plan LLM input subset or editorial depth profile.
- Additional validation rules:
  - The contract must name `free`, `basic`, `premium`, `LLMInputSelection`, `EditorialDepthProfile` and `FrontendVisibilityRules`.
  - The contract must name the precision and detail-level semantics used by each B2C plan.
  - The contract must require future builder output to include plan shaping metadata without raw runtime, provider payload or prompt internals.
  - Future backend tests must prove `client_interpretation_projection_v1` returns HTTP 200 for all three B2C plans.
  - Future backend tests must prove free, basic and premium shaping differ by fields, section visibility or editorial depth.
  - Future frontend tests must prove rendering follows backend visibility metadata and not a local plan matrix.
  - Future runtime evidence must include `pytest`, `TestClient`, `app.routes` and `app.openapi()`.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, `TestClient`, `app.routes` and `app.openapi()` prove runtime behavior and route neutrality. |
| Baseline Snapshot | yes | Before and after artifacts prove plan shaping changes without access blocking. |
| Ownership Routing | yes | LLM input, editorial depth, frontend visibility and access policy need separate canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this projection shaping story. |
| Contract Shape | yes | The plan shaping metadata needs exact fields, plan values and frontend visibility semantics. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Backend access blocking and React-owned plan policy must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | A canonical shaping contract uses the B2C plan set. | Evidence profile: json_contract_shape; `rg` checks plan names and contract terms. |
| AC2 | The contract defines LLM input selection by plan. | Evidence profile: json_contract_shape; `rg` checks `LLMInputSelection` and allowed fact groups. |
| AC3 | The contract defines `EditorialDepthProfile` by plan. | Evidence profile: json_contract_shape; `rg` checks `EditorialDepthProfile`. |
| AC4 | The contract defines frontend visibility by plan. | Evidence profile: json_contract_shape; `rg` checks `FrontendVisibilityRules`. |
| AC5 | The contract preserves full projection for all plans. | Evidence profile: runtime_openapi_contract; `pytest` runs real conditions tests. |
| AC6 | The contract defines future implementation ownership. | Evidence profile: ownership_routing; `rg` checks the listed backend, LLM and frontend owner paths. |
| AC7 | Future validations prevent policy drift. | Evidence profile: targeted_forbidden_symbol_scan; `pnpm` runs architecture guards. |
| AC8 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-320 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Re-read the CS-315 decision, existing projection contract and listed owners before finalizing the shaping contract. (AC: AC1, AC6)
- [ ] Task 2: Define the plan-aware contract with LLM inputs, editorial depth, precision, detail and frontend visibility. (AC: AC1, AC2, AC3, AC4)
- [ ] Task 3: Document that `client_interpretation_projection_v1` execution stays available for `free`, `basic` and `premium`. (AC: AC5)
- [ ] Task 4: Name backend, LLM and frontend implementation owners and their forbidden destinations. (AC: AC6)
- [ ] Task 5: Define future backend validations for full execution and plan-differentiated metadata. (AC: AC5, AC7)
- [ ] Task 6: Define future frontend validations for backend-shaped visibility and no React local plan matrix. (AC: AC4, AC7)
- [ ] Task 7: Persist validation and source-alignment evidence under the CS-320 evidence folder. (AC: AC8)

## Files to Inspect First

- `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md` - source brief.
- `_story_briefs/cs-320-definir-differenciation-llm-front-par-plan-b2c.md` - current source brief.
- `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md` - prior divergence brief.
- `docs/architecture/natal-projection-plan-matrix-product-decision.md` - product decision and post-calculation boundary.
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/10-final-evidence.md` - CS-315 signoff evidence.
- `_condamad/stories/CS-317-cloturer-cs315-final-evidence-validation-runtime/generated/10-final-evidence.md` - runtime closure evidence.
- `_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/generated/10-final-evidence.md` - React policy guard evidence.
- `docs/architecture/client-interpretation-projection-v1-contract.md` - existing plan-depth contract.
- `docs/architecture/b2c-projection-entitlement-policy.md` - access policy owner that must not be moved to React.
- `backend/app/services/api_contracts/public/projections.py` - public projection API contract owner.
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` - canonical builder owner.
- `backend/app/services/projections/projection_endpoint_service.py` - endpoint orchestration owner for projection payloads.
- `backend/tests/unit/domain/astrology/test_client_interpretation_projection_v1_builder.py` - backend builder tests.
- `backend/tests/api/test_projection_real_conditions.py` - TestClient evidence for supported B2C plans.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - natal feature page rendering owner.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - projection rendering owner.
- `frontend/src/tests/natalInterpretation.test.tsx` - frontend projection rendering tests.
- `frontend/src/tests/component-architecture-guards.test.ts` - React entitlement matrix guard.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - This story defines the contract and names the future implementation validators below.
  - `backend/tests/api/test_projection_real_conditions.py` through `pytest` and `TestClient`.
  - `backend/tests/unit/domain/astrology/test_client_interpretation_projection_v1_builder.py` for shaped payload behavior.
  - `frontend/src/tests/natalInterpretation.test.tsx` for backend-shaped rendering.
  - `app.routes` and `app.openapi()` for runtime API neutrality.
- Secondary evidence:
  - Targeted `rg` scans for shaping contract fields and React policy drift.
- Static scans alone are not sufficient for later implementation stories because:
  - all three B2C plans must then prove runtime projection execution and frontend rendering from backend-shaped payloads.

## Contract Shape

- Contract type:
  - Backend projection shaping metadata consumed by frontend rendering.
- Fields:
  - `projection_id`: exact value `client_interpretation_projection_v1`.
  - `plan_variant`: one of `free`, `basic` or `premium`.
  - `llm_input_selection`: stable `LLMInputSelection` profile with allowed fact groups and evidence labels.
  - `editorial_depth_profile`: stable `EditorialDepthProfile` with depth code, section budget and prediction detail level.
  - `precision_level`: stable client-readable level for specificity, prediction granularity and caveat density.
  - `frontend_visibility_rules`: stable `FrontendVisibilityRules` with visible section codes and display hints.
  - `sections`: backend-shaped client sections filtered by visibility rules.
  - `support_elements`: client-readable support elements allowed by plan.
  - `calculation_scope`: exact marker proving full calculation source was available before shaping.
  - `excluded_surfaces`: raw runtime, provider payload, prompt internals, React access policy and expert-only proof.
- Required fields:
  - `projection_id`
  - `plan_variant`
  - `llm_input_selection`
  - `editorial_depth_profile`
  - `frontend_visibility_rules`
  - `precision_level`
  - `sections`
  - `support_elements`
  - `calculation_scope`
  - `excluded_surfaces`
- Optional fields:
  - `audit_input` only for plans already authorized by the existing projection contract.
  - `missing_data` only for degraded public states.
- Status codes:
  - Existing endpoint keeps `200` for supported B2C plans requesting `client_interpretation_projection_v1`.
- Serialization names:
  - Runtime JSON keys must stay snake_case and match the names listed in this section.
- Frontend type impact:
  - frontend view parsing may add optional fields for visibility metadata from backend responses.
- Generated contract impact:
  - `app.openapi()` must keep `/v1/astrology/projections` as the generic route and must not add a plan-specific route.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `docs/architecture/natal-projection-plan-matrix-product-decision.md`
  - `docs/architecture/client-interpretation-projection-v1-contract.md`
  - `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
  - `backend/tests/api/test_projection_real_conditions.py`
  - `frontend/src/tests/natalInterpretation.test.tsx`
- Comparison after implementation:
  - `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/free-sample.json`
  - `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/basic-sample.json`
  - `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/premium-sample.json`
  - `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/validation.txt`
  - `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/runtime-surface-guard.txt`
- Expected invariant:
  - The only intended behavioral delta is post-calculation shaping metadata and frontend rendering from backend-shaped visibility rules.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| LLM input selection profile | backend projection contract or interpretation domain owner | React component policy |
| Editorial depth profile | backend projection contract or interpretation domain owner | local UI access matrix |
| Precision and detail profile | backend projection contract or interpretation domain owner | local UI display heuristics |
| Frontend visibility rules | backend projection payload consumed by React | frontend entitlement table |
| Projection execution access | CS-283 policy and backend entitlement service boundary | frontend rendering code |
| Runtime builder behavior | `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` | API router branching |
| Frontend rendering | `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` | backend access policy |
| Evidence artifacts | `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse `client_interpretation_projection_v1` as the single interpreted projection identifier.
- Reuse `structured_facts_v1` as the factual source before shaping.
- Reuse existing builder tests and add focused cases instead of creating parallel projection suites.
- Reuse `NatalInterpretationContent.tsx` projection rendering rather than adding a second natal projection renderer.
- Reuse the existing component architecture guard against React-owned entitlement matrices.
- Do not add external packages, API routes, DB models, migrations, generated clients, provider calls or prompt templates.

## No Legacy / Forbidden Paths

- No legacy route path may be added for plan-differentiated projections.
- No compatibility plan gate may block lower plans from calculation execution.
- No fallback branch may move access policy into React.
- Do not create aliases, shims, wrappers or parallel builders for `client_interpretation_projection_v1`.
- Do not add a hardcoded free/basic/premium entitlement table under `frontend/src/**`.
- Do not expose raw runtime objects, provider payloads, prompt internals or expert proof in B2C payloads.
- Forbidden surfaces:
  - `backend/app/api/**` as owner of plan shaping logic
  - `backend/migrations/**`
  - `frontend/src/**` as owner of access policy
  - Stripe, pricing, checkout and subscription files
  - generated OpenAPI clients

## Reintroduction Guard

- Guard target:
  - all B2C plans keep full projection execution;
  - plan differentiation remains post-calculation shaping;
  - React cannot own the free/basic/premium access matrix;
  - no plan-specific route or OpenAPI path is introduced;
  - raw runtime, prompt internals and provider payloads stay out of B2C output.
- Guard mechanism:
  - backend `pytest` with `TestClient` for all supported plans;
  - builder tests for shaping metadata by plan;
  - frontend Vitest for backend-shaped visibility rendering;
  - `app.routes` and `app.openapi()` neutrality checks;
  - targeted `rg` scans for React-owned policy drift.
- Guard owner:
  - `backend/tests/api/test_projection_real_conditions.py`;
  - `backend/tests/unit/domain/astrology/test_client_interpretation_projection_v1_builder.py`;
  - `frontend/src/tests/component-architecture-guards.test.ts`;
  - `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/validation.txt`.
- Guard evidence:
  - `pytest -q backend/tests/api/test_projection_real_conditions.py`;
  - `pytest -q backend/tests/unit/domain/astrology/test_client_interpretation_projection_v1_builder.py`;
  - `python -c "from app.main import app; assert app.openapi(); assert any(getattr(r, 'path', '') == '/v1/astrology/projections' for r in app.routes)"`;
  - `pnpm --dir frontend vitest run natalInterpretation component-architecture-guards`.

## Regression Guardrails

Scope vector:

- backend projection shaping: yes;
- backend API runtime evidence: yes;
- frontend projection rendering: yes;
- entitlement documentation reference: yes;
- DB, auth, i18n, style, build and migration: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | Backend ownership stays inside canonical app paths. | builder tests and loaded app checks. |
| RG-003 | Runtime route inventory must stay canonical. | `app.routes` and `app.openapi()` proof. |
| RG-022 | Backend test evidence must point to collected tests. | targeted `pytest` commands. |
| RG-041 | Entitlement docs must align with runtime evidence. | CS-315 decision and B2C policy scans. |
| Registry gap | No exact plan-aware projection shaping guardrail exists in resolver output. | story-local runtime and React policy guards. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because this story does not require TSX inline style work.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-042 LLM docs source-of-truth is not active because this story defines shaping metadata, not backend/docs LLM governance.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Free sample payload | `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/free-sample.json` | Keep free shaping output. |
| Basic sample payload | `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/basic-sample.json` | Keep basic shaping output. |
| Premium sample payload | `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/premium-sample.json` | Keep premium shaping output. |
| Validation output | `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/validation.txt` | Keep lint and test transcript. |
| Runtime surface guard | `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/runtime-surface-guard.txt` | Prove route neutrality. |
| Source alignment | `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/source-alignment.md` | Prove brief alignment. |
| Review output | `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/generated/11-code-review.md` | Keep review evidence. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this projection shaping story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/client-interpretation-projection-v1-contract.md` - add shaping metadata contract fields.
- `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/source-alignment.md` - source alignment proof.

Likely files for later implementation stories:

- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` - emit shaping metadata by plan.
- `backend/app/services/projections/projection_endpoint_service.py` - preserve generic endpoint orchestration for shaped payloads.
- `frontend/src/components/natal-interpretation/NatalInterpretationTypes.ts` - parse optional backend shaping metadata.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - render backend-shaped visibility metadata.
- `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/runtime-surface-guard.txt` - route and OpenAPI proof.

Likely tests:

- `backend/tests/unit/domain/astrology/test_client_interpretation_projection_v1_builder.py` - plan shaping metadata tests.
- `backend/tests/api/test_projection_real_conditions.py` - all supported B2C plans still execute the projection.
- `frontend/src/tests/natalInterpretation.test.tsx` - backend-shaped visibility rendering.
- `frontend/src/tests/component-architecture-guards.test.ts` - React entitlement matrix guard.

Files not expected to change:

- `backend/app/api/**` - out of scope; no public or internal API route is touched.
- `backend/migrations/**` - out of scope; no database migration is touched.
- `backend/app/infra/db/**` - out of scope; no persistence adapter is touched.
- Stripe, pricing, checkout and subscription files - out of scope for this projection shaping story.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `ruff format backend`
- VC3: `ruff check backend`
- VC4: `pytest -q backend/tests/unit/domain/astrology/test_client_interpretation_projection_v1_builder.py`
- VC5: `pytest -q backend/tests/api/test_projection_real_conditions.py`
- VC6: `pytest -q backend/tests`
- VC7: `python -c "import sys; sys.path.insert(0,'backend'); from app.main import app; assert app.openapi()"`
- VC8: `python -c "import sys; sys.path.insert(0,'backend'); from app.main import app; assert any(getattr(r,'path','') == '/v1/astrology/projections' for r in app.routes)"`
- VC9: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/validation.txt').exists()"`
- VC10: `rg -n "LLMInputSelection|EditorialDepthProfile|FrontendVisibilityRules|precision_level" docs/architecture backend/app/domain/astrology/interpretation`
- VC11: `rg -n "React.*entitlement|free.*basic.*premium.*policy|accepted_matrix" frontend/src`
- VC12: `pytest -q`
- VC13: `pnpm --dir frontend lint`
- VC14: `pnpm --dir frontend vitest run natalInterpretation component-architecture-guards`
- VC15: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/source-alignment.md').exists()"`

Before VC2 through VC12, activate the venv with `. .\.venv\Scripts\Activate.ps1`.
Before VC15, activate the venv with `. .\.venv\Scripts\Activate.ps1` from the repository root.

## Regression Risks

- A developer could treat plan differentiation as backend access denial instead of post-calculation shaping.
- React could regain a local entitlement matrix while still rendering backend responses.
- Premium could expose raw runtime, prompt internals or provider payloads instead of richer client-safe sections.
- The generic projection route could drift into plan-specific routes or generated clients.
- The frontend could hide sections by local plan branching rather than backend visibility metadata.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments and public or non-trivial docstrings in French for new or significantly modified backend files.
- Keep frontend styles in CSS files only; do not add inline styles.
- Persist the required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md`
- `_story_briefs/cs-320-definir-differenciation-llm-front-par-plan-b2c.md`
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/00-story.md`
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/10-final-evidence.md`
- `_condamad/stories/CS-317-cloturer-cs315-final-evidence-validation-runtime/00-story.md`
- `_condamad/stories/CS-317-cloturer-cs315-final-evidence-validation-runtime/generated/10-final-evidence.md`
- `_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/generated/10-final-evidence.md`
- `docs/architecture/natal-projection-plan-matrix-product-decision.md`
- `docs/architecture/client-interpretation-projection-v1-contract.md`
- `docs/architecture/b2c-projection-entitlement-policy.md`
- `backend/app/services/api_contracts/public/projections.py`
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/services/projections/projection_endpoint_service.py`
- `backend/tests/unit/domain/astrology/test_client_interpretation_projection_v1_builder.py`
- `backend/tests/api/test_projection_real_conditions.py`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/component-architecture-guards.test.ts`
- `_condamad/stories/regression-guardrails.md`
