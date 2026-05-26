# Story CS-315 product-plan-matrix-signoff-natal-projections: Validate Natal Projection Product Plan Matrix
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-315-faire-valider-matrice-produit-plans-projections-natal.md`.
- Related dependency: CS-309 produced QA evidence for free, basic and premium `/natal` projection behavior.
- Related dependency: CS-283 owns the B2C projection entitlement policy at `docs/architecture/b2c-projection-entitlement-policy.md`.
- Existing evidence found: CS-309 records the product limitation in `product-ambiguities.md`.
- Existing tests found: backend authorization and frontend natal rendering tests already cover projection outcomes.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: CS-309 proves technical behavior, but product ownership has not signed off the commercial matrix.
- Source-alignment evidence: PASS; the story preserves the brief stakes without turning product policy into React logic.

## Objective

Record a product-owned decision for the `/natal` projection plan matrix covering `beginner_summary_v1` and
`client_interpretation_projection_v1` for free, basic and premium users.

The implementation must document the accepted product matrix, owner and date, distinguish decision from backend behavior,
prove CS-309 frontend fixtures remain backend-sourced, and create a follow-up brief when product and backend behavior differ.

## Target State

- One product decision artifact documents the official free/basic/premium matrix for `/natal` projections.
- The decision artifact names the accountable product owner role and the decision date.
- The document states that backend authorization remains the implementation source for access decisions.
- React continues to render backend success and 403 responses without owning a separate entitlement matrix.
- CS-309 frontend tests remain fixture-driven from backend-shaped responses.
- Any product/backend divergence is recorded as a separate backend brief, not corrected locally in React.
- No Stripe, pricing, checkout, subscription, auth, DB, migration, i18n, styling or build behavior changes.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-315-faire-valider-matrice-produit-plans-projections-natal.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-315`.
- Evidence 3: `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-after.md` - QA matrix read.
- Evidence 4: `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/product-ambiguities.md` - product limitation read.
- Evidence 5: `backend/tests/api/test_projection_authorization.py` - backend authorization evidence path read.
- Evidence 6: `frontend/src/tests/natalInterpretation.test.tsx` - CS-309 frontend fixture tests read.
- Evidence 7: `docs/architecture/b2c-projection-entitlement-policy.md` - existing entitlement policy owner read.
- Evidence 8: `docs/architecture/official-product-primitives-public-projections.md` - public projection registry read.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output and targeted ID lookup only.
- Source-alignment evidence: PASS; all brief items map to ACs, tasks, validation commands and non-goals.

## Domain Boundary

- Domain: product-documentation
- In scope:
  - Product decision artifact for `/natal` plan matrix sign-off.
  - Owner, date and accepted free/basic/premium behavior for the two public projection IDs.
  - Linkage to CS-309 QA evidence and existing CS-283 entitlement policy.
  - Verification that frontend fixtures still mirror backend-shaped success and 403 responses.
  - Follow-up brief creation path for a product/backend divergence.
- Out of scope:
  - Backend entitlement implementation, frontend UI changes, Stripe, pricing, checkout, subscription, DB, migrations, auth, i18n, styling and build tooling.
  - Rewriting upsell copy beyond the matrix decision.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No React-owned entitlement matrix, plan gate, hardcoded policy table or local authorization source.
  - No backend route, service, schema, migration, billing rule or subscription catalog change.
  - No replacement of CS-283 as the canonical B2C projection entitlement policy owner.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a product decision artifact with backend/frontend parity evidence.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the product decision artifact, story evidence artifacts and a follow-up brief only for a documented divergence.
  - Reuse CS-309 matrix rows and CS-283 entitlement terminology.
  - Keep backend application code, frontend source, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Keep React as a renderer of backend responses, not the owner of access policy.
  - Keep product decision and backend implementation evidence explicitly separated.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product rejects the CS-309 matrix or names a different commercial boundary than backend behavior.
- Additional validation rules:
  - The decision artifact must name `free`, `basic` and `premium`.
  - The decision artifact must name `beginner_summary_v1` and `client_interpretation_projection_v1`.
  - The decision artifact must contain an owner role and decision date.
  - The decision artifact must state that backend authorization remains the implementation source.
  - The story must require `pytest` evidence for backend authorization and `vitest` evidence for frontend rendering parity.
  - A product/backend mismatch must create a separate `_story_briefs/` backend brief instead of React policy edits.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Backend pytest, frontend vitest, `app.openapi()` and `app.routes` prove implementation evidence. |
| Baseline Snapshot | yes | CS-309 matrix before and product decision after must be persisted for review. |
| Ownership Routing | yes | Product decision, backend authorization and frontend rendering have separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this product documentation story. |
| Contract Shape | yes | The decision artifact needs exact plans, projections, owner, date and divergence handling fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | React-owned policy duplication and local entitlement matrices must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The official product matrix is documented. | Evidence profile: baseline_before_after_diff; `rg` checks plans, projections, owner and date. |
| AC2 | The implementation source boundary is explicit. | Evidence profile: json_contract_shape; `rg` checks decision versus implementation source wording. |
| AC3 | CS-309 frontend fixtures stay backend-sourced. | Evidence profile: frontend_typecheck_no_orphan; `pnpm` vitest runs `frontend/src/tests/natalInterpretation.test.tsx`. |
| AC4 | Backend authorization remains the access source. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/api/test_projection_authorization.py`. |
| AC5 | Product/backend divergence creates a follow-up brief. | Evidence profile: external_usage_blocker; `python` checks brief path or decision artifact no-divergence marker. |
| AC6 | React does not own plan policy. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks `frontend/src` for local plan matrix policy. |
| AC7 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-315 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Re-read CS-309 matrix and ambiguity evidence before writing the decision artifact. (AC: AC1, AC2)
- [ ] Task 2: Inspect CS-283 and public projection registry ownership before choosing the target document path. (AC: AC1, AC2)
- [ ] Task 3: Create or update one product decision artifact with owner, date and accepted plan matrix. (AC: AC1)
- [ ] Task 4: State that backend authorization owns access decisions and React renders backend responses. (AC: AC2, AC6)
- [ ] Task 5: Run backend authorization evidence for projection access behavior. (AC: AC4)
- [ ] Task 6: Run frontend natal projection rendering evidence against CS-309 fixture scenarios. (AC: AC3)
- [ ] Task 7: Create a separate backend brief only when the product decision differs from backend behavior. (AC: AC5)
- [ ] Task 8: Persist validation and source-alignment evidence under the CS-315 evidence folder. (AC: AC7)

## Files to Inspect First

- `_story_briefs/cs-315-faire-valider-matrice-produit-plans-projections-natal.md` - source contract.
- `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-after.md` - QA matrix.
- `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/product-ambiguities.md` - product limitation.
- `docs/architecture/b2c-projection-entitlement-policy.md` - existing entitlement policy owner.
- `docs/architecture/official-product-primitives-public-projections.md` - public projection registry owner.
- `backend/tests/api/test_projection_authorization.py` - backend authorization evidence target.
- `frontend/src/tests/natalInterpretation.test.tsx` - CS-309 frontend fixture evidence target.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `docs/architecture/b2c-projection-entitlement-policy.md` for the existing B2C projection entitlement policy.
  - CS-309 evidence artifacts for the observed free/basic/premium `/natal` matrix.
  - `backend/tests/api/test_projection_authorization.py` through `pytest` for backend access behavior.
  - `app.openapi()` and `app.routes` for proof that this product story does not add API surfaces.
  - `frontend/src/tests/natalInterpretation.test.tsx` through `pnpm` vitest for frontend response rendering.
- Secondary evidence:
  - Targeted `rg` scans over the product decision artifact and `frontend/src`.
- Static scans alone are not sufficient because:
  - backend authorization and frontend fixture parity must be proven through their existing test runners.

## Contract Shape

- Contract type:
  - Markdown product decision artifact for `/natal` projection plan matrix sign-off.
- Fields:
  - `decision_id`: stable identifier for the `/natal` projection plan matrix.
  - `decision_date`: exact date of product sign-off.
  - `owner`: product owner role accountable for the commercial matrix.
  - `scope`: `/natal`, `beginner_summary_v1`, `client_interpretation_projection_v1`, `free`, `basic`, `premium`.
  - `accepted_matrix`: documented expected behavior per plan and projection.
  - `implementation_source`: backend authorization and projection responses.
  - `frontend_policy`: render backend responses without local entitlement ownership.
  - `divergence_policy`: create a separate backend brief for any product/backend mismatch.
- Required fields:
  - `decision_id`
  - `decision_date`
  - `owner`
  - `scope`
  - `accepted_matrix`
  - `implementation_source`
  - `frontend_policy`
  - `divergence_policy`
- Optional fields:
  - none
- Status codes:
  - Documentation only; existing backend authorization tests keep HTTP behavior evidence.
- Serialization names:
  - Documentation only; no runtime JSON serializer is added.
- Frontend type impact:
  - none; no frontend source or generated client is touched unless a future story is created.
- Generated contract impact:
  - none; this story must not add OpenAPI paths, generated schemas or generated clients.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-after.md`
  - `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/product-ambiguities.md`
  - `docs/architecture/b2c-projection-entitlement-policy.md`
  - `backend/tests/api/test_projection_authorization.py`
  - `frontend/src/tests/natalInterpretation.test.tsx`
- Comparison after implementation:
  - `docs/architecture/natal-projection-plan-matrix-product-decision.md`
  - `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/validation.txt`
  - `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/source-alignment.md`
- Expected invariant:
  - The only intended repository delta is one product decision artifact, optional follow-up brief and CONDAMAD story/evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Product matrix sign-off | `docs/architecture/natal-projection-plan-matrix-product-decision.md` | React components or tests as policy owner |
| B2C entitlement policy | `docs/architecture/b2c-projection-entitlement-policy.md` | duplicated product decision artifact |
| Backend authorization behavior | `backend/tests/api/test_projection_authorization.py` and backend services | frontend fixture logic |
| Frontend rendering parity | `frontend/src/tests/natalInterpretation.test.tsx` | backend entitlement policy |
| Follow-up divergence brief | `_story_briefs/` | local React correction |
| Evidence artifacts | `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse the CS-309 matrix rows instead of inventing a second plan grid.
- Reuse CS-283 entitlement terminology instead of creating a competing policy vocabulary.
- Reuse existing backend authorization tests as the access-behavior evidence.
- Reuse existing CS-309 frontend fixture scenarios instead of duplicating product policy in React.
- Keep one product decision artifact for the `/natal` matrix sign-off.
- Do not add external packages, scripts, API schemas, frontend helpers, services, prompts, migrations or generated clients.

## No Legacy / Forbidden Paths

- No legacy product matrix may be introduced in React.
- No compatibility plan gate may be added to frontend source.
- No fallback branch may translate product policy into local UI authorization.
- Do not create aliases, shims, wrappers or parallel documents for the same matrix decision.
- Do not add a hardcoded entitlement table under `frontend/src/**`.
- Do not change backend entitlement behavior in this story.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/**`
  - `backend/migrations/**`
  - Stripe, pricing, checkout and subscription files
  - generated OpenAPI clients

## Reintroduction Guard

- Guard target:
  - React cannot become the source of plan authorization;
  - backend behavior cannot be silently changed by a product documentation story;
  - the product decision cannot contradict CS-309 without a separate backend brief;
  - CS-309 fixture tests cannot drift away from backend-shaped responses.
- Guard mechanism:
  - targeted `rg` checks for decision artifact fields;
  - backend `pytest` authorization evidence;
  - frontend `pnpm` vitest evidence;
  - scoped scans for local plan policy in `frontend/src`;
  - persisted evidence under the CS-315 evidence folder.
- Guard owner:
  - `docs/architecture/natal-projection-plan-matrix-product-decision.md`;
  - `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/validation.txt`;
  - `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/source-alignment.md`.
- Guard evidence:
  - `rg -n "decision_id|decision_date|owner|accepted_matrix|divergence_policy" docs/architecture/natal-projection-plan-matrix-product-decision.md`;
  - `pytest -q backend/tests/api/test_projection_authorization.py`;
  - `pnpm vitest run natalInterpretation`;
  - `rg -n "free.*basic.*premium|client_interpretation_projection_v1.*plan" frontend/src`.

## Regression Guardrails

Scope vector:

- product documentation contract: yes;
- entitlement policy reference: yes;
- backend authorization evidence: yes;
- frontend fixture evidence: yes;
- API route change: no;
- DB, auth, i18n, style, build and migration: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-022 | Validation paths must point to collected pytest targets. | backend `pytest`; frontend `pnpm` vitest. |
| RG-041 | Entitlement documentation must stay aligned with runtime and API evidence. | decision artifact scans; backend tests. |
| Registry gap | No exact `/natal` product matrix sign-off guardrail exists in resolver output. | story-local scans and evidence artifacts. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-002 API route layout is out of scope because no backend router file is modified.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Product decision | `docs/architecture/natal-projection-plan-matrix-product-decision.md` | Keep the official product matrix sign-off. |
| Validation output | `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/validation.txt` | Keep command results. |
| Source alignment | `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/source-alignment.md` | Prove brief stakes stayed covered. |
| Divergence brief | `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md` | Required only when product/backend behavior differs. |
| Review output | `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this product documentation story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/natal-projection-plan-matrix-product-decision.md` - product sign-off artifact.
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/source-alignment.md` - source coverage evidence.
- `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md` - created only when product/backend behavior differs.

Likely tests:

- `backend/tests/api/test_projection_authorization.py` - backend authorization behavior evidence.
- `frontend/src/tests/natalInterpretation.test.tsx` - CS-309 frontend fixture parity evidence.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend source surface is touched.
- `backend/app/**` - out of scope; no backend application source is touched.
- `backend/migrations/**` - out of scope; no database migration is touched.
- Stripe, pricing, checkout and subscription files - out of scope for this decision story.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `rg -n "decision_id|decision_date|owner|accepted_matrix" docs/architecture/natal-projection-plan-matrix-product-decision.md`
- VC2: `rg -n "backend authorization|implementation_source|frontend_policy" docs/architecture/natal-projection-plan-matrix-product-decision.md`
- VC3: `rg -n "beginner_summary_v1|client_interpretation_projection_v1|free|basic|premium" docs/architecture/natal-projection-plan-matrix-product-decision.md`
- VC4: `pnpm --dir frontend lint`
- VC5: `pnpm --dir frontend exec node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi`
- VC6: `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests\api\test_projection_authorization.py tests\api\test_projection_endpoint.py --tb=short`
- VC7: `rg -n "free.*basic.*premium|accepted_matrix|entitlement matrix" frontend/src`
- VC8: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/validation.txt').exists()"`
- VC9: `ruff format .`
- VC10: `ruff check .`
- VC11: `pytest -q`
- VC12: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/source-alignment.md').exists()"`
- VC13: `python -c "from app.main import app; assert app.openapi(); assert isinstance(app.routes, list)"`

Before VC8, VC9, VC10, VC11, VC12 and VC13, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- Product sign-off could be treated as a React entitlement implementation.
- CS-309 fixture scenarios could become a product policy source instead of backend-shaped rendering evidence.
- A product/backend mismatch could be hidden by frontend behavior.
- The CS-283 entitlement policy could be duplicated by a second canonical matrix document.
- Documentation work could drift into Stripe, subscription, route, DB, migration or styling changes.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments in French for new or significantly modified documentation files.
- Keep this implementation documentation-only unless product/backend divergence requires the specified brief.
- Persist the required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-315-faire-valider-matrice-produit-plans-projections-natal.md`
- `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-after.md`
- `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/product-ambiguities.md`
- `docs/architecture/b2c-projection-entitlement-policy.md`
- `docs/architecture/official-product-primitives-public-projections.md`
- `backend/tests/api/test_projection_authorization.py`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `_condamad/stories/regression-guardrails.md`
