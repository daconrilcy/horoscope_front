# Story CS-309 verifier-differenciation-free-basic-premium-projections-natal: Verify Free Basic Premium Natal Projection Differentiation
Status: done

## Trigger / Source

- Source type: product QA brief with repository-informed boundary.
- Source reference: `_story_briefs/cs-309-verifier-differenciation-free-basic-premium-projections-natal.md`.
- Selected mode: Repo-informed story with Fast Story Writer Mode.
- Problem statement: `/natal` must prove visible differences between free, basic, and premium projection states without duplicating backend entitlement policy.
- Source stakes: avoid misleading users, preserve backend authorization ownership, keep upgrade states clear, and prove all three plan experiences.
- Source-alignment evidence: PASS; objective, ACs, tasks, validation, and guardrails preserve the brief and CS-302/CS-303 dependencies.

## Objective

Verify and correct the `/natal` frontend experience for `free`, `basic`, and `premium` users across `beginner_summary_v1` and
`client_interpretation_projection_v1`.

The story must document the expected visible matrix, prove plan-specific rendering through tests, and keep access decisions driven by
`POST /v1/astrology/projections`.

## Target State

- A plan matrix documents the expected `/natal` visible state for both B2C projections across `free`, `basic`, and `premium`.
- Frontend tests prove each plan renders the authorized content, locked states, upgrade messaging, 403 handling, and partial content states.
- The frontend consumes backend projection responses and 403 details without recreating the entitlement matrix in React.
- Upgrade CTAs reuse existing supported subscription paths.
- Backend projection authorization tests are rerun as dependency evidence.
- A QA ledger records the visible differences by plan and any product ambiguity about delivered value.
- Premium content is never rendered as available for a non-authorized plan.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-309-verifier-differenciation-free-basic-premium-projections-natal.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-309` after `CS-308`.
- Evidence 3: `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/generated/10-final-evidence.md` - backend plan proof read.
- Evidence 4: `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md` - frontend wiring proof read.
- Evidence 5: `backend/tests/api/test_projection_authorization.py` - backend 403 entitlement evidence inspected.
- Evidence 6: `frontend/src/api/astrologyProjections.ts` - projection API client and query ownership inspected.
- Evidence 7: `frontend/src/features/natal-chart/NatalInterpretation.tsx` - `/natal` projection orchestration inspected.
- Evidence 8: `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - projection rendering owner inspected.
- Evidence 9: `frontend/src/tests/natalInterpretation.test.tsx` - current projection state coverage inspected.
- Evidence 10: `_condamad/stories/regression-guardrails.md` - scoped resolver and targeted ID lookup consulted.
- Source-alignment evidence: PASS; each source prerequisite, included scope item, validation command, and risk maps to an AC or task.

## Domain Boundary

- Domain: frontend-api-integration
- In scope:
  - `/natal` visible projection differentiation for `free`, `basic`, and `premium`.
  - `beginner_summary_v1` and `client_interpretation_projection_v1` content, locked, upgrade, 403, and partial states.
  - Frontend tests for the three plans and backend authorization regression evidence.
  - QA ledger and plan matrix artifacts under the CS-309 capsule.
- Out of scope:
  - Backend entitlement policy changes, projection builders, DB schema, auth model, pricing page, Stripe flow, i18n expansion, build tooling, and migrations.
  - New frontend route, generated client, payment checkout flow, product pricing decision, and regression-guardrail registry enrichment.
- Explicit non-goals:
  - No duplicated entitlement matrix in React.
  - No bypass of a backend 403.
  - No premium content presented as available to `free` or `basic`.
  - No inline style implementation.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a frontend API-integration QA story spanning plan states and backend evidence.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Change only `/natal` projection presentation, tests, and evidence artifacts required to prove plan differentiation.
  - Keep `frontend/src/api/astrologyProjections.ts` as the HTTP client owner for projection requests.
  - Keep access decisions sourced from backend responses and 403 payloads.
  - Keep upgrade navigation on existing supported subscription paths.
  - Preserve backend projection builders, entitlement policy, public route shape, persistence, prompts, and providers unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the expected matrix reveals unclear product value for a plan or conflicts with backend authorization behavior.
- Additional validation rules:
  - The plan matrix must name `free`, `basic`, `premium`, `beginner_summary_v1`, and `client_interpretation_projection_v1`.
  - Frontend tests must cover all three plans using mocked backend responses or 403 errors.
  - Runtime backend evidence must include `pytest -q backend/tests/api/test_projection_authorization.py`.
  - Static guards must prove React does not own a hardcoded entitlement decision table.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Vitest, Testing Library, backend `pytest`, and TestClient-backed authorization tests prove plan behavior. |
| Baseline Snapshot | yes | Plan matrix and QA ledger prove the intended visible delta by plan. |
| Ownership Routing | yes | Frontend API, React rendering, backend authorization tests, and evidence artifacts need canonical owners. |
| Allowlist Exception | no | No allowlist handling or broad waiver is authorized for plan differentiation. |
| Contract Shape | yes | The plan matrix and QA ledger have exact required fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Hardcoded entitlement policy, 403 bypass, premium leaks, and inline styles must stay absent. |
| Persistent Evidence | yes | Matrix, QA ledger, validation output, and review handoff must be kept. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The expected plan matrix is documented. | Evidence profile: baseline_before_after_diff; `python` checks CS-309 matrix artifact. |
| AC2 | Free `/natal` projection states are tested. | Evidence profile: json_contract_shape; `vitest` covers free content, locked state, and upgrade CTA. |
| AC3 | Basic `/natal` projection states are tested. | Evidence profile: json_contract_shape; `vitest` covers basic content and premium restriction. |
| AC4 | Premium `/natal` projection states are tested. | Evidence profile: json_contract_shape; `vitest` covers both projection contents as available. |
| AC5 | Backend 403 projection refusal is user-readable. | Evidence profile: api_error_shape_contract; `vitest` covers 403 UI and backend `pytest` covers details. |
| AC6 | React does not own entitlement policy. | Evidence profile: targeted_forbidden_symbol_scan; `rg` and `AST guard` check frontend hardcoded plan logic. |
| AC7 | Upgrade CTAs use supported paths. | Evidence profile: frontend_typecheck_no_orphan; `vitest` covers `/settings/subscription` navigation. |
| AC8 | Premium content is not leaked to lower plans. | Evidence profile: targeted_forbidden_symbol_scan; `vitest` and `rg` scan premium fixtures and rendered text. |
| AC9 | Backend authorization tests pass. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/api/test_projection_authorization.py`. |
| AC10 | QA evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-309 QA ledger and validation paths. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-302 evidence, CS-303 evidence, projection authorization tests, frontend API client, `/natal` owners, and current tests. (AC: AC1, AC6, AC9)
- [ ] Task 2: Create the plan matrix artifact for `free`, `basic`, and `premium` across both projection types. (AC: AC1)
- [ ] Task 3: Add or strengthen frontend tests for the free plan visible content, locked state, and upgrade CTA. (AC: AC2, AC7, AC8)
- [ ] Task 4: Add or strengthen frontend tests for the basic plan visible content and premium restriction. (AC: AC3, AC7, AC8)
- [ ] Task 5: Add or strengthen frontend tests for the premium plan with both projection contents available. (AC: AC4, AC8)
- [ ] Task 6: Verify 403 rendering uses backend error state without bypassing the refusal. (AC: AC5, AC6)
- [ ] Task 7: Run backend authorization tests with venv active and frontend validation commands. (AC: AC5, AC9)
- [ ] Task 8: Persist QA ledger, product ambiguities, static guard output, and validation output under the CS-309 capsule. (AC: AC10)

## Files to Inspect First

- `_story_briefs/cs-309-verifier-differenciation-free-basic-premium-projections-natal.md` - source brief.
- `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/generated/10-final-evidence.md` - backend plan proof.
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md` - frontend wiring proof.
- `backend/tests/api/test_projection_authorization.py` - backend 403 entitlement tests.
- `frontend/src/api/astrologyProjections.ts` - projection client and query owner.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - `/natal` orchestration owner.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - projection display owner.
- `frontend/src/tests/natalInterpretation.test.tsx` - main targeted frontend test owner.
- `frontend/src/tests/NatalChartPage.test.tsx` - `/natal` page-level test owner.
- `frontend/src/tests/natalChartApi.test.tsx` - projection API wrapper test owner.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi` from `frontend`.
  - `node .\scripts\run-vite-logged.mjs vitest vitest run` from `frontend`.
  - `pnpm lint` from `frontend`.
  - `python -B -m pytest -q tests\api\test_projection_authorization.py tests\api\test_projection_endpoint.py --tb=short` from `backend` with venv active.
  - `TestClient` coverage in backend authorization tests.
- Secondary evidence:
  - Plan matrix, QA ledger, product ambiguity ledger, static guard output, and validation log under the CS-309 capsule.
  - Targeted `rg` scans for hardcoded entitlement ownership, direct API bypass, premium leak strings, and inline styles.
- Static scans alone are not sufficient because:
  - The story must prove rendered `/natal` behavior for three user plans and real backend authorization refusals.

## Contract Shape

- Contract type:
  - Frontend plan differentiation matrix and QA ledger.
- Fields:
  - `audit_date`: ISO date of the verification.
  - `route`: `/natal`.
  - `plan_code`: `free`, `basic`, or `premium`.
  - `projection_type`: `beginner_summary_v1` or `client_interpretation_projection_v1`.
  - `expected_state`: available, locked, upgrade, forbidden, partial, empty, loading, or error.
  - `visible_message`: user-facing text or `none`.
  - `content_visibility`: visible, hidden, partial, or not-rendered.
  - `backend_source`: response, 403, or CS-302 authorization evidence.
  - `frontend_test`: exact test file or test name.
  - `decision`: verified, corrected, or product-decision-required.
  - `evidence_path`: persisted artifact path.
- Required fields:
  - `audit_date`
  - `route`
  - `plan_code`
  - `projection_type`
  - `expected_state`
  - `content_visibility`
  - `backend_source`
  - `frontend_test`
  - `decision`
  - `evidence_path`
- Optional fields:
  - `visible_message`
  - `product_ambiguity`
  - `validation_command`
- Status codes:
  - `403` remains the backend refusal status for unauthorized projection access.
- Serialization names:
  - Ledger keys are written exactly as listed in this section.
- Frontend type impact:
  - only targeted type updates required by plan-state tests are authorized.
- Backend type impact:
  - none; backend projection response and entitlement policy contracts remain unchanged.
- Generated contract impact:
  - no generated client, OpenAPI output, or generated manifest change is authorized.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-after.md`
  - `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/qa-ledger.md`
  - `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/validation.txt`
- Expected invariant:
  - The only intended behavior delta is clearer verified `/natal` plan differentiation, not a backend entitlement policy change.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Projection HTTP calls | `frontend/src/api/astrologyProjections.ts` | React component direct fetch |
| `/natal` query orchestration | `frontend/src/features/natal-chart/NatalInterpretation.tsx` | Presentational projection card |
| Projection display | `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` | New duplicate renderer |
| Frontend plan-state tests | `frontend/src/tests/natalInterpretation.test.tsx` | Manual-only QA |
| Page-level tests | `frontend/src/tests/NatalChartPage.test.tsx` | Backend-only proof |
| API wrapper tests | `frontend/src/tests/natalChartApi.test.tsx` | Component fixtures only |
| Backend refusal proof | `backend/tests/api/test_projection_authorization.py` | React entitlement matrix |
| Evidence artifacts | CS-309 `evidence/` directory | Application source comments |

## Mandatory Reuse / DRY Constraints

- Reuse existing `useAstrologyProjections`, `ApiError`, projection panel, subscription path, and Testing Library setup.
- Reuse existing CS-302 and CS-303 evidence as context only; do not copy their generated capsule content.
- Reuse existing CSS classes and design tokens for any layout adjustment.
- Do not add external packages, generated clients, new route owners, duplicate projection parsers, or duplicate entitlement decision tables.
- Do not encode plan authorization policy in React beyond rendering backend-provided success or refusal states.

## No Legacy / Forbidden Paths

- No legacy projection access path may be added for `/natal`.
- No compatibility route or copy source may be added for plan differentiation.
- No fallback entitlement decision may be added in React.
- Do not create aliases, shims, wrappers, or duplicated state machines for projection access.
- Do not bypass, swallow, or reinterpret backend `403` as available content.
- Do not add inline `style` attributes in TSX files.
- Do not change backend projection builders, prompts, providers, DB schema, migrations, pricing, Stripe, or public API route shape.

## Reintroduction Guard

- Guard path 1: projection access decisions remain backend-sourced through success responses or 403 errors.
- Guard path 2: React does not contain a duplicated `free/basic/premium` entitlement matrix.
- Guard path 3: premium-only content stays hidden for non-authorized plans.
- Guard path 4: upgrade CTAs continue to use existing subscription navigation.
- Guard path 5: backend authorization tests remain part of validation evidence.
- Required deterministic guards:
  - `rg -n "free.*basic.*premium|basic.*premium|plan_code.*===" frontend/src/features/natal-chart frontend/src/components/natal-interpretation`.
  - `rg -n "fetch\\(.*/v1/astrology/projections|axios\\(.*/v1/astrology/projections" frontend/src`.
  - `rg -n "style=" frontend/src/features/natal-chart frontend/src/components/natal-interpretation -g "*.tsx"`.
  - `git diff --name-only -- backend frontend _condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal`.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-047 `CS-029-encadrer-styles-inline-statiques-frontend` | Touched TSX files keep static styles out of inline attributes. | `rg` inline-style scan; `pnpm lint`. |
| RG-069 `CS-113-classer-converger-composants-consommateurs-api` | Shared components must not become API orchestration owners. | `vitest`; API import scan. |
| RG-071 `CS-115-decomposer-natal-interpretation-owner` | `NatalInterpretation` must not grow into a plan-policy owner. | `vitest`; import-boundary scan. |
| RG-073 `CS-118-relocate-natal-interpretation-feature-owner` | `/natal` orchestration remains under feature owner paths. | `vitest`; path scan. |
| Story-local plan guard | Plan differences stay backend-sourced and visible in QA evidence. | Plan matrix; QA ledger; `pytest`. |
| Needs-investigation | Resolver returned backend docs and prediction guardrails that are non-local to this story. | Resolver output stored in evidence. |

Non-applicable examples that prevent scope drift:

- RG-002 is not selected because no backend router change is in scope.
- RG-041 is not selected because entitlement documentation is not edited.
- RG-052 is not selected because CSS namespace migration is not edited.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Plan matrix before | `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-before.md` | Record expected visible states. |
| Plan matrix after | `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-after.md` | Record verified final states. |
| QA ledger | `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/qa-ledger.md` | Prove visible plan differences. |
| Product ambiguity ledger | `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/product-ambiguities.md` | Record unclear value. |
| Static guards | `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/static-guards.txt` | Keep no-policy-duplication scans. |
| Validation log | `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/validation.txt` | Keep final validation commands. |
| Final evidence | `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/generated/10-final-evidence.md` | Summarize implementation evidence. |
| Review output | `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/generated/11-code-review.md` | Keep automatic review. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling, test suppression, or broad waiver is authorized.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `frontend/src/api/astrologyProjections.ts` - adjust only error or metadata handling required by tests.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - adjust projection state mapping or CTA routing without owning plan policy.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - adjust projection rendering, locked copy, and partial-state display.
- `frontend/src/tests/natalInterpretation.test.tsx` - cover free, basic, premium, 403, partial, locked, and upgrade states.
- `frontend/src/tests/NatalChartPage.test.tsx` - cover `/natal` plan-level behavior from page composition.
- `frontend/src/tests/natalChartApi.test.tsx` - cover API wrapper error mapping only when wrapper behavior changes.
- `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/**` - persist matrix and QA evidence.

Likely tests:

- `frontend/src/tests/natalInterpretation.test.tsx` - primary plan-state rendering tests.
- `frontend/src/tests/NatalChartPage.test.tsx` - page-level plan routing and CTA checks.
- `frontend/src/tests/natalChartApi.test.tsx` - projection API wrapper and 403 mapping.
- `backend/tests/api/test_projection_authorization.py` - backend refusal details.
- `backend/tests/api/test_projection_endpoint.py` - existing projection endpoint dependency validation.

Files not expected to change:

- `backend/app/**` - out of scope; backend entitlement and projection runtime remain unchanged.
- `backend/alembic/**` - out of scope; no migration is touched.
- `frontend/package.json` - out of scope; no package or script change is authorized.
- `_condamad/stories/regression-guardrails.md` - out of scope; normal story generation must not enrich the registry.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: create plan matrix, QA ledger, product ambiguity ledger, static guard output, and final evidence under the CS-309 capsule.
- VC2: from `frontend`, run `pnpm lint`.
- VC3: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi`.
- VC4: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run`.
- VC5: with venv active, run from `backend`: `python -B -m pytest -q tests\api\test_projection_authorization.py tests\api\test_projection_endpoint.py --tb=short`.
- VC6: from repo root, run `rg -n "free.*basic.*premium|basic.*premium|plan_code.*===" frontend/src/features/natal-chart frontend/src/components/natal-interpretation`.
- VC7: from repo root, run `rg -n "fetch\\(.*/v1/astrology/projections|axios\\(.*/v1/astrology/projections" frontend/src`.
- VC8: from repo root, run `rg -n "style=" frontend/src/features/natal-chart frontend/src/components/natal-interpretation -g "*.tsx"`.
- VC9: with venv active, run `python -B` to assert CS-309 matrix, QA ledger, static guards, and validation artifacts exist.

## Regression Risks

- React could accidentally become the plan policy owner while trying to improve visible states.
- A 403 could be hidden behind generic error text that users cannot understand.
- Premium projection content could appear in a lower-plan fixture or locked card.
- CTA tests could pass while pointing to an unsupported subscription route.
- Product value ambiguity could be left undocumented and converted into accidental copy.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Start by writing the plan matrix before changing UI behavior.
- Keep access decisions backend-sourced.
- Keep every style change in CSS and reuse existing variables.
- Keep backend policy concerns in a separate product or backend story decision record.

## References

- `_story_briefs/cs-309-verifier-differenciation-free-basic-premium-projections-natal.md`
- `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/generated/10-final-evidence.md`
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md`
- `backend/tests/api/test_projection_authorization.py`
- `backend/tests/api/test_projection_endpoint.py`
- `frontend/src/api/astrologyProjections.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `frontend/src/tests/natalChartApi.test.tsx`
- `_condamad/stories/regression-guardrails.md`
