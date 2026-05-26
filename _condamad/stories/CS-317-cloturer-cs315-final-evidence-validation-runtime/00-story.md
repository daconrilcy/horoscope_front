# Story CS-317 cloturer-cs315-final-evidence-validation-runtime: Close CS-315 Final Evidence And Runtime Validation
Status: ready-to-dev

## Trigger / Source

- Source type: repo-informed closure brief.
- Source reference: `_story_briefs/cs-317-cloturer-cs315-final-evidence-validation-runtime.md`.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: CS-315 has a product decision artifact, but the CONDAMAD capsule is not closed with final evidence and runtime proof.
- Source-alignment evidence: PASS; this story keeps the brief focused on evidence closure, not matrix reimplementation.

## Objective

Close CS-315 by producing missing final evidence, replacing the editorial review with implementation review evidence, running backend and frontend runtime
validations, and aligning CS-315 statuses only when the evidence is green.

## Target State

- CS-315 contains `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/10-final-evidence.md`.
- CS-315 contains a real implementation review in `generated/11-code-review.md`.
- Backend projection authorization validation is executed with the repository venv active.
- Backend projection endpoint validation is executed with the authorization runtime suite.
- Frontend natal projection validation is executed through the existing Vite logged runner.
- React remains free of a local free/basic/premium entitlement matrix.
- CS-315 `00-story.md` and `_condamad/stories/story-status.md` are set to `done` only after passing evidence exists.
- The CS-312/CS-316 delivery report can be reclassified without any remaining CS-315 evidence gap.
- Any product/backend mismatch is documented in a separate brief instead of changing React.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-317-cloturer-cs315-final-evidence-validation-runtime.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-317`.
- Evidence 3: `_condamad/reports/CS-312-CS-316-delivery-report.md` - report classifies CS-315 as implemented but not validated.
- Evidence 4: `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/00-story.md` - CS-315 currently starts as `ready-to-dev`.
- Evidence 5: `docs/architecture/natal-projection-plan-matrix-product-decision.md` - product matrix decision already exists.
- Evidence 6: `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/validation.txt` - prior validation lacks runtime closure.
- Evidence 7: `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/source-alignment.md` - source alignment exists.
- Evidence 8: `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/11-code-review.md` - current review is editorial.
- Evidence 9: `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-after.md` - source matrix read.
- Evidence 10: `backend/tests/api/test_projection_authorization.py` - backend runtime validation target read.
- Evidence 11: `frontend/src/tests/natalInterpretation.test.tsx` - frontend runtime validation target read.
- Evidence 12: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output and targeted ID lookup only.
- Source-alignment evidence: PASS; ACs cover final evidence, implementation review, backend runtime, frontend runtime, scans and status closure.

## Domain Boundary

- Domain: condamad-evidence-validation
- In scope:
  - CS-315 capsule evidence completion.
  - Runtime validation commands for backend projection authorization and frontend natal projection rendering.
  - Implementation review artifact for the existing CS-315 product decision work.
  - CS-315 story and tracker status alignment after passing validation.
  - Separate brief creation for product/backend divergence.
- Out of scope:
  - Backend entitlement policy changes, frontend entitlement logic, Stripe, pricing, checkout, subscription, DB, migrations, auth, i18n, styling and build tooling.
  - Rewriting the CS-315 product decision without evidence of divergence.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No React-owned matrix for free, basic or premium projection access.
  - No backend authorization behavior change.
  - No pricing, billing, schema, migration, route, generated client or UI style change.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a CONDAMAD capsule closure with runtime validation and final evidence.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add or update only CS-315 evidence, CS-315 generated review/final-evidence artifacts, CS-315 status lines, tracker rows and a divergence brief.
  - Keep backend application code, frontend source, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Keep the existing product decision as the source unless runtime validation proves a product/backend mismatch.
  - Use loaded runtime checks through `pytest`, `TestClient`, `app.routes` and `app.openapi()` for backend evidence.
  - Use the existing frontend test runner for natal rendering evidence.
- Deletion allowed: no
- Replacement allowed: yes
- Replacement constraints:
  - `generated/11-code-review.md` may replace editorial review content with implementation review evidence.
- User decision required if: backend or frontend runtime validation fails because product and implementation behavior differ.
- Additional validation rules:
  - `generated/10-final-evidence.md` must map every CS-315 AC to concrete evidence.
  - `generated/11-code-review.md` must review implemented artifacts, not only story text.
  - Python commands must activate `.\.venv\Scripts\Activate.ps1` first.
  - Runtime evidence must include `pytest`, `TestClient`, `app.routes` or `app.openapi()` for backend closure.
  - Frontend evidence must include `pnpm lint` and Vite logged Vitest output for natal projection tests.
  - Status changes to `done` are forbidden until all required runtime and capsule validations pass.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, `TestClient`, `app.routes`, `app.openapi()` and Vitest prove runtime closure. |
| Baseline Snapshot | yes | CS-315 pre-closure artifacts and final evidence must show before/after closure. |
| Ownership Routing | yes | CS-315 evidence, review, status and divergence brief have canonical destinations. |
| Allowlist Exception | no | No allowlist handling is authorized for this closure story. |
| Contract Shape | yes | Final evidence and implementation review need exact sections and AC-by-AC proof. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | React-owned plan matrices and unvalidated status drift must stay absent. |
| Persistent Evidence | yes | Validation transcripts and review artifacts must be kept for handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | CS-315 final evidence exists. | Evidence profile: baseline_before_after_diff; `python` checks generated final evidence path. |
| AC2 | CS-315 implementation review exists. | Evidence profile: baseline_before_after_diff; `rg` checks implementation review verdict and findings. |
| AC3 | Backend projection runtime suite passes. | Evidence profile: runtime_openapi_contract; `pytest` runs `backend/tests/api/test_projection_endpoint.py`. |
| AC4 | Backend app runtime contract is neutral. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`. |
| AC5 | Frontend natal projection validation passes. | Evidence profile: frontend_typecheck_no_orphan; `pnpm` runs natalInterpretation Vitest target. |
| AC6 | React has no local plan matrix policy. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks `frontend/src` for matrix policy terms. |
| AC7 | CS-315 status reflects proven closure. | Evidence profile: baseline_before_after_diff; `python` checks CS-315 story and tracker status. |
| AC8 | Capsule validation passes. | Evidence profile: reintroduction_guard; `python` runs condamad-dev-story capsule validation for CS-315. |
| AC9 | Product divergence is routed separately. | Evidence profile: external_usage_blocker; `python` checks divergence brief path or no-divergence marker. |
| AC10 | Delivery report has no residual CS-315 gap. | Evidence profile: baseline_before_after_diff; `rg` checks report gap status. |

## Implementation Tasks

- [ ] Task 1: Re-read CS-315 story, report, decision artifact and existing evidence before editing generated artifacts. (AC: AC1, AC2)
- [ ] Task 2: Run backend projection authorization and endpoint validations with the venv active, then persist the transcript. (AC: AC3)
- [ ] Task 3: Run a backend runtime neutrality check through `app.routes` and `app.openapi()`. (AC: AC4)
- [ ] Task 4: Run frontend lint and natal projection Vitest targets, then persist the transcript. (AC: AC5)
- [ ] Task 5: Run targeted scans proving React has no local free/basic/premium entitlement matrix. (AC: AC6)
- [ ] Task 6: Write `generated/10-final-evidence.md` with AC-by-AC proof and validation command results. (AC: AC1)
- [ ] Task 7: Replace `generated/11-code-review.md` with implementation review verdict and findings. (AC: AC2)
- [ ] Task 8: Create a separate backend divergence brief only when runtime evidence contradicts the product matrix. (AC: AC9)
- [ ] Task 9: Run CS-315 capsule validation before changing CS-315 status to `done`. (AC: AC8)
- [ ] Task 10: Update CS-315 `00-story.md` and `_condamad/stories/story-status.md` only after validations pass. (AC: AC7)
- [ ] Task 11: Record delivery-report reclassification readiness after CS-315 evidence is complete. (AC: AC10)

## Files to Inspect First

- `_condamad/reports/CS-312-CS-316-delivery-report.md` - source closure gap.
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/00-story.md` - target story status and ACs.
- `docs/architecture/natal-projection-plan-matrix-product-decision.md` - implemented product decision artifact.
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/validation.txt` - prior validation transcript.
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/source-alignment.md` - existing source alignment.
- `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-after.md` - matrix source.
- `backend/tests/api/test_projection_authorization.py` - backend authorization runtime target.
- `backend/tests/api/test_projection_endpoint.py` - backend endpoint runtime target.
- `frontend/src/tests/natalInterpretation.test.tsx` - frontend natal projection runtime target.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `pytest` with `TestClient` for backend projection authorization behavior.
  - `app.routes` and `app.openapi()` for backend route and schema neutrality.
  - Vite logged Vitest for frontend rendering of backend-shaped projection responses.
  - `pnpm lint` for frontend static validation.
- Secondary evidence:
  - Targeted `rg` scans for React plan-matrix policy drift and decision artifact fields.
- Static scans alone are not sufficient because:
  - CS-315 closure requires actual backend and frontend runtime validation evidence.

## Contract Shape

- Contract type:
  - CONDAMAD closure evidence for CS-315.
- Fields:
  - `final_evidence`: AC-by-AC evidence for CS-315.
  - `implementation_review`: implementation review verdict, findings and residual risk.
  - `backend_runtime`: pytest transcript and `app.routes` or `app.openapi()` proof.
  - `frontend_runtime`: `pnpm lint` and natal Vitest transcript.
  - `scan_evidence`: React matrix policy scan and decision field scan.
  - `status_alignment`: CS-315 story status and tracker status after validation.
  - `divergence_policy`: separate backend brief path or no-divergence marker.
- Required fields:
  - `final_evidence`
  - `implementation_review`
  - `backend_runtime`
  - `frontend_runtime`
  - `scan_evidence`
  - `status_alignment`
  - `divergence_policy`
- Optional fields:
  - none
- Status codes:
  - Existing backend tests keep HTTP behavior evidence; no new HTTP status is introduced.
- Serialization names:
  - Documentation only; no runtime serializer is added.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - CS-315 generated evidence files are updated; no OpenAPI paths or generated schemas are added.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/reports/CS-312-CS-316-delivery-report.md`
  - `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/00-story.md`
  - `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/11-code-review.md`
  - `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/validation.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/10-final-evidence.md`
  - `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/11-code-review.md`
  - `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/validation.txt`
  - `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/00-story.md`
  - `_condamad/stories/story-status.md`
  - `_condamad/reports/CS-312-CS-316-delivery-report.md` or CS-315 final evidence reclassification note
- Expected invariant:
  - The only intended surface delta is CS-315 closure evidence, status alignment, report readiness and divergence routing when runtime proof requires it.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| CS-315 final evidence | `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/10-final-evidence.md` | application source |
| CS-315 implementation review | `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/11-code-review.md` | editorial-only review |
| CS-315 validation transcript | `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/validation.txt` | untracked console output |
| Backend runtime proof | `backend/tests/api/test_projection_authorization.py` and `backend/tests/api/test_projection_endpoint.py` | frontend policy logic |
| Frontend runtime proof | `frontend/src/tests/natalInterpretation.test.tsx` | backend entitlement policy |
| Delivery report readiness | `_condamad/reports/CS-312-CS-316-delivery-report.md` or final evidence note | untracked local note |
| Divergence brief | `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md` | React entitlement workaround |
| Status registry | `_condamad/stories/story-status.md` | local notes or report-only status |

## Mandatory Reuse / DRY Constraints

- Reuse the existing CS-315 product decision artifact instead of creating a competing matrix document.
- Reuse CS-309 matrix evidence instead of copying a new unaudited plan table into React.
- Reuse existing backend projection tests and frontend natal tests as runtime evidence.
- Reuse the existing CONDAMAD capsule validation script for CS-315.
- Do not add external packages, scripts, API schemas, frontend helpers, services, prompts, migrations or generated clients.

## No Legacy / Forbidden Paths

- No legacy evidence-only closure may mark CS-315 done without runtime validation.
- No compatibility review may replace implementation review evidence.
- No fallback status update may bypass failed backend or frontend validation.
- Do not create aliases, shims, wrappers or parallel product matrix documents.
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
  - CS-315 cannot return to a status/evidence mismatch;
  - React cannot become the source of plan authorization;
  - backend behavior cannot be silently changed by a closure story;
  - editorial review cannot stand in for implementation review.
- Guard mechanism:
  - backend `pytest` runtime evidence;
  - frontend `pnpm` lint and Vitest evidence;
  - `app.routes` and `app.openapi()` neutrality checks;
  - targeted `rg` scans for local plan policy in `frontend/src`;
  - CS-315 capsule validation before status update.
- Guard owner:
  - `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/10-final-evidence.md`;
  - `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/11-code-review.md`;
  - `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/validation.txt`.
- Guard evidence:
  - `pytest -q backend/tests/api/test_projection_authorization.py`;
  - `python -c "from app.main import app; assert app.openapi(); assert any(getattr(r, 'path', '') for r in app.routes)"`;
  - `pnpm --dir frontend exec node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi`;
  - `rg -n "free.*basic.*premium|accepted_matrix|entitlement matrix" frontend/src`.

## Regression Guardrails

Scope vector:

- CONDAMAD capsule evidence closure: yes;
- backend runtime validation target: yes;
- frontend natal projection test target: yes;
- entitlement documentation reference: yes;
- API route creation: no;
- DB, auth, i18n, style, build and migration: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-022 | Validation paths must point to collected pytest targets. | backend `pytest`; CS-315 validation transcript. |
| RG-041 | Entitlement documentation must stay aligned with runtime evidence. | decision scans; backend and frontend runtime tests. |
| RG-003 | Runtime route inventory must stay canonical. | `app.routes` and `app.openapi()` neutrality proof. |
| Registry gap | No exact CS-315 final-evidence closure guardrail exists in resolver output. | story-local capsule validation and status checks. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-002 API router layout is not active because this story must not edit backend routers.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Final evidence | `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/10-final-evidence.md` | Keep AC-by-AC closure proof. |
| Review output | `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/11-code-review.md` | Keep review evidence. |
| Validation output | `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/validation.txt` | Keep command results. |
| Source alignment | `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/source-alignment.md` | Keep source coverage proof. |
| Divergence brief | `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md` | Required only when product/backend behavior differs. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this closure story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/10-final-evidence.md` - final closure proof.
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/11-code-review.md` - implementation review.
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/00-story.md` - status update to `done` after validation.
- `_condamad/stories/story-status.md` - CS-315 and CS-317 tracker rows.
- `_condamad/reports/CS-312-CS-316-delivery-report.md` - updated only if closure evidence justifies reclassification.
- `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md` - created only when product/backend behavior differs.

Likely tests:

- `backend/tests/api/test_projection_authorization.py` - backend authorization behavior evidence.
- `backend/tests/api/test_projection_endpoint.py` - endpoint behavior evidence.
- `frontend/src/tests/natalInterpretation.test.tsx` - frontend natal projection rendering evidence.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend source surface is touched.
- `backend/app/**` - out of scope; no backend application source is touched.
- `backend/migrations/**` - out of scope; no database migration is touched.
- Stripe, pricing, checkout and subscription files - out of scope for this closure story.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests\api\test_projection_authorization.py tests\api\test_projection_endpoint.py --tb=short`
- VC2: `.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "from app.main import app; assert app.openapi(); assert any(getattr(r, 'path', '') for r in app.routes)"`
- VC3: `pnpm --dir frontend lint`
- VC4: `pnpm --dir frontend exec node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi`
- VC5: `rg -n "free.*basic.*premium|accepted_matrix|entitlement matrix" frontend/src`
- VC6: `rg -n "decision_id|decision_date|owner|accepted_matrix|implementation_source|frontend_policy" docs/architecture/natal-projection-plan-matrix-product-decision.md`
- VC7: From activated venv: `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-315-product-plan-matrix-signoff-natal-projections`
- VC8: From activated venv and CS-315 folder: `python -B -c "from pathlib import Path; assert Path('generated/10-final-evidence.md').exists()"`
- VC9: From activated venv and CS-315 folder: `python -B -c "from pathlib import Path; assert 'Status: done' in Path('00-story.md').read_text()"`
- VC10: From activated venv: `python -B -c "from pathlib import Path as P; t=P('_condamad/stories/story-status.md').read_text(); assert '| CS-315 |' in t and '| done |' in t"`
- VC14: `rg -n "CS-315|Implemented but not validated|gap" _condamad/reports/CS-312-CS-316-delivery-report.md`
- VC11: `ruff format .`
- VC12: `ruff check .`
- VC13: `pytest -q`

Before VC7, VC8, VC9, VC10, VC11, VC12 and VC13, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- CS-315 could be marked `done` while runtime backend or frontend validation remains absent.
- A product/backend mismatch could be hidden by a documentation-only closure.
- React could grow a local entitlement matrix while tests still pass.
- An editorial story review could remain mistaken for implementation review.
- The delivery report could be reclassified without final evidence artifacts.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments in French for new or significantly modified documentation files.
- Keep application source unchanged unless the user explicitly authorizes a separate implementation story.
- Persist the required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-317-cloturer-cs315-final-evidence-validation-runtime.md`
- `_condamad/reports/CS-312-CS-316-delivery-report.md`
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/00-story.md`
- `docs/architecture/natal-projection-plan-matrix-product-decision.md`
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/validation.txt`
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/source-alignment.md`
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/11-code-review.md`
- `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-after.md`
- `backend/tests/api/test_projection_authorization.py`
- `backend/tests/api/test_projection_endpoint.py`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `_condamad/stories/regression-guardrails.md`
