# Story CS-310 tests-manuels-profils-naissance-projections-natal: Test Natal Projections With Manual Birth Profiles
Status: ready-to-dev

## Trigger / Source

- Source type: product QA brief with repository-informed boundary.
- Source reference: `_story_briefs/cs-310-tests-manuels-profils-naissance-projections-natal.md`.
- Selected mode: Repo-informed story with Fast Story Writer Mode.
- Problem statement: `/natal` needs manual QA across representative birth profiles to prove B2C projection robustness beyond automated contracts.
- Source stakes: protect user trust, prove degraded display, prevent sensitive payload exposure, and convert reproducible anomalies into tracked work.
- Source-alignment evidence: PASS; objective, ACs, tasks, evidence, validation, and guardrails preserve every included scope item from the brief.

## Objective

Produce a manual QA evidence capsule for `/natal` across at least five non-sensitive birth profiles covering precise time, missing time,
foreign location, controlled incomplete data, and a standard profile.

The story must document visible projection results, degraded states, errors, disclaimers, sensitive-data checks, and reproducible anomalies.

## Target State

- A non-sensitive birth-profile test set documents at least five profiles and the reason each profile exists.
- `/natal` is exercised manually or through an equivalent browser simulation for every profile.
- The QA ledger records projection visibility, degraded mode, errors, disclaimers, sensitive-data exposure checks, and outcome.
- The missing-time profile shows a clear degraded or approximate state without crashing the UI.
- Controlled incomplete data is handled without a React crash or unbounded raw payload display.
- Prompt, provider, replay, admin, debug, and internal payload surfaces remain invisible in the public `/natal` UI.
- Reproducible anomalies are either corrected inside this story scope or written as explicit follow-up story briefs.
- Frontend targeted validation and backend projection validation pass.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-310-tests-manuels-profils-naissance-projections-natal.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-310` after `CS-309`.
- Evidence 3: `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/response-samples.json` - projection samples read.
- Evidence 4: `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/frontend-after.md` - frontend wiring proof read.
- Evidence 5: `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/evidence/browser-qa-ledger.json` - browser QA baseline read.
- Evidence 6: `frontend/src/pages/NatalChartPage.tsx` - `/natal` page owner inspected.
- Evidence 7: `frontend/src/features/natal-chart/NatalInterpretation.tsx` - projection orchestration owner inspected.
- Evidence 8: `backend/app/services/api_contracts/public/projections.py` - public projection response contract inspected.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - scoped resolver output and targeted ID lookup consulted.
- Source-alignment evidence: PASS; every brief prerequisite, included scope item, expected validation command, and risk maps to an AC or task.

## Domain Boundary

- Domain: frontend-natal-manual-qa
- In scope:
  - `/natal` manual or browser-simulated QA for representative birth profiles.
  - B2C projection visibility for `beginner_summary_v1` and `client_interpretation_projection_v1`.
  - Degraded, controlled incomplete, error, disclaimer, and sensitive-data exposure checks.
  - Evidence artifacts under the CS-310 capsule.
  - Targeted frontend and backend projection validations listed in the brief.
- Out of scope:
  - Backend projection builder redesign, DB schema, auth model, entitlement policy, i18n expansion, styling redesign, build tooling, and migrations.
  - Permanent sensitive fixtures, new browser framework, new frontend route, pricing changes, provider changes, and guardrail registry enrichment.
- Explicit non-goals:
  - No subjective validation of astrological truth.
  - No use of real personal birth data unless explicitly justified in the QA ledger.
  - No UI redesign of `/natal`.
  - No fragile E2E suite without an owner.
  - No public display of prompt, provider, replay, admin, debug, or internal payload data.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a frontend manual QA story with supporting backend projection validation.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Change only `/natal` QA artifacts, targeted tests, and narrow fixes required by reproducible profile findings.
  - Keep `frontend/src/pages/NatalChartPage.tsx` as the page owner.
  - Keep `frontend/src/features/natal-chart/NatalInterpretation.tsx` as the projection orchestration owner.
  - Keep `frontend/src/api/astrologyProjections.ts` as the projection HTTP client owner.
  - Preserve backend projection route shape, builders, persistence, prompts, providers, auth, DB schema, and migrations unchanged.
  - Use story follow-up artifacts for anomalies that exceed this QA closure boundary.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: a manual finding needs product interpretation, real personal data, or backend business-rule changes.
- Additional validation rules:
  - The profile set must include precise time, missing time, foreign location, controlled incomplete data, and standard profile rows.
  - The manual QA ledger must include one row per profile and state the visible result for `/natal`.
  - Evidence must include a sensitive-surface check for prompts, provider payloads, replay payloads, admin data, and debug internals.
  - Runtime evidence must include targeted frontend `vitest` commands and backend `pytest` projection commands from the brief.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Browser QA, Vitest, backend `pytest`, and TestClient-backed projection tests prove user-visible behavior. |
| Baseline Snapshot | yes | CS-302, CS-303, CS-306, profile set, and QA ledger establish before and after evidence. |
| Ownership Routing | yes | Manual QA artifacts, `/natal` page, projection orchestration, and API contract owners must remain clear. |
| Allowlist Exception | no | No allowlist handling or broad waiver is authorized for manual QA closure. |
| Contract Shape | yes | Profile set, manual QA ledger, and follow-up ledger have exact required fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Sensitive payload display, direct provider data, fragile E2E drift, and inline styles must stay absent. |
| Persistent Evidence | yes | Profile set, QA ledger, screenshots or notes, anomaly ledger, validation log, and review handoff must be kept. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The non-sensitive profile set covers five categories. | Evidence profile: baseline_before_after_diff; `python` checks CS-310 profile set artifact. |
| AC2 | Every profile has a traced `/natal` result. | Evidence profile: baseline_before_after_diff; `python` checks QA ledger rows. |
| AC3 | Missing birth time shows degraded UI. | Evidence profile: json_contract_shape; `vitest` covers degraded state and Manual check records profile result. |
| AC4 | Controlled incomplete data does not crash UI. | Evidence profile: json_contract_shape; `vitest` covers error state and Manual check records profile result. |
| AC5 | Sensitive internal surfaces are not visible. | Evidence profile: targeted_forbidden_symbol_scan; `rg` and Manual check inspect public `/natal` output. |
| AC6 | Reproducible anomalies are closed or tracked. | Evidence profile: baseline_before_after_diff; `python` checks anomaly ledger and follow-up paths. |
| AC7 | Frontend targeted validation passes. | Evidence profile: frontend_typecheck_no_orphan; `pnpm lint` and `vitest` commands from `frontend`. |
| AC8 | Backend projection validation passes. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/api/test_projection_real_conditions.py`. |
| AC9 | QA evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-310 evidence and validation artifacts. |

## Implementation Tasks

- [ ] Task 1: Inspect the brief, CS-302 samples, CS-303 frontend proof, CS-306 browser ledger, `/natal` owners, and projection contract. (AC: AC1)
- [ ] Task 2: Create the non-sensitive profile set with five required categories and coverage rationale. (AC: AC1)
- [ ] Task 3: Execute `/natal` or browser-equivalent simulation for every profile and record visible projection results. (AC: AC2)
- [ ] Task 4: Verify missing-time degraded messaging remains understandable and backed by targeted frontend tests. (AC: AC3, AC7)
- [ ] Task 5: Verify controlled incomplete data produces bounded error handling without React crash. (AC: AC4, AC7)
- [ ] Task 6: Check public `/natal` output for prompt, provider, replay, admin, debug, and internal payload leakage. (AC: AC5)
- [ ] Task 7: Convert reproducible anomalies into targeted corrections or explicit follow-up story briefs. (AC: AC6)
- [ ] Task 8: Run frontend validation and backend projection validation, then persist outputs under the CS-310 capsule. (AC: AC7, AC8, AC9)

## Files to Inspect First

- `_story_briefs/cs-310-tests-manuels-profils-naissance-projections-natal.md` - source brief.
- `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/response-samples.json` - projection samples.
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/frontend-after.md` - frontend wiring proof.
- `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/evidence/browser-qa-ledger.json` - browser QA baseline.
- `frontend/src/pages/NatalChartPage.tsx` - `/natal` page owner.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - projection orchestration owner.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - projection display owner.
- `frontend/src/api/astrologyProjections.ts` - projection API client owner.
- `frontend/src/tests/natalInterpretation.test.tsx` - targeted projection state tests.
- `frontend/src/tests/NatalChartPage.test.tsx` - page-level `/natal` tests.
- `frontend/src/tests/natalChartApi.test.tsx` - projection API wrapper tests.
- `backend/app/services/api_contracts/public/projections.py` - public projection contract.
- `backend/tests/api/test_projection_real_conditions.py` - real-condition projection backend tests.
- `backend/tests/api/test_projection_endpoint.py` - projection endpoint backend tests.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - Manual or browser-equivalent execution of `/natal` for every profile in the CS-310 profile set.
  - `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi` from `frontend`.
  - `pnpm lint` from `frontend`.
  - `python -B -m pytest -q tests\api\test_projection_real_conditions.py tests\api\test_projection_endpoint.py --tb=short` from `backend` with venv active.
  - `TestClient` coverage in backend projection tests.
- Secondary evidence:
  - Profile set, manual QA ledger, sensitive-surface scan, anomaly ledger, screenshots or notes, and validation log under the CS-310 capsule.
  - Targeted `rg` scans for prompt, provider, replay, admin, debug, internal payload labels, direct API bypass, and inline styles.
- Static scans alone are not sufficient because:
  - The story must prove user-visible `/natal` behavior across representative real-world profile shapes.

## Contract Shape

- Contract type:
  - Manual QA profile set, manual QA ledger, sensitive-surface ledger, and anomaly ledger.
- Fields:
  - `audit_date`: ISO date of the verification.
  - `route`: `/natal`.
  - `profile_id`: stable non-sensitive identifier.
  - `profile_category`: precise_time, missing_time, foreign_location, controlled_incomplete, or standard.
  - `birth_input_summary`: non-sensitive summary without full real personal data.
  - `execution_mode`: manual_browser, simulated_browser, or test_fixture.
  - `projection_types_checked`: list containing checked B2C projection types.
  - `visible_result`: success, degraded, controlled_error, empty, loading, entitlement, or blocked.
  - `disclaimer_result`: visible, missing, unchanged, or not_applicable.
  - `sensitive_surface_result`: pass or finding.
  - `anomaly_id`: stable anomaly identifier or none.
  - `evidence_path`: persisted artifact path.
- Required fields:
  - `audit_date`
  - `route`
  - `profile_id`
  - `profile_category`
  - `birth_input_summary`
  - `execution_mode`
  - `projection_types_checked`
  - `visible_result`
  - `sensitive_surface_result`
  - `evidence_path`
- Optional fields:
  - `disclaimer_result`
  - `screenshot_path`
  - `anomaly_id`
  - `follow_up_path`
- Status codes:
  - Backend validation preserves existing projection endpoint status behavior from CS-302 and endpoint tests.
- Serialization names:
  - Ledger keys are written exactly as listed in this section.
- Frontend type impact:
  - only targeted type updates required by QA findings and tests are authorized.
- Backend type impact:
  - none; backend projection request and response contracts remain unchanged.
- Generated contract impact:
  - no generated client, OpenAPI output, or generated manifest change is authorized.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/baseline-summary.md`
- Comparison after implementation:
  - `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/profile-set.json`
  - `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/manual-qa-ledger.json`
  - `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/anomalies.md`
  - `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/validation.txt`
- Expected invariant:
  - The only intended behavior delta is bounded QA-driven correction of reproducible `/natal` findings, not a projection architecture change.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| `/natal` page composition | `frontend/src/pages/NatalChartPage.tsx` | New duplicate page |
| Projection orchestration | `frontend/src/features/natal-chart/NatalInterpretation.tsx` | Public API client |
| Projection display | `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` | Page-level ad hoc renderer |
| Projection HTTP calls | `frontend/src/api/astrologyProjections.ts` | React component direct fetch |
| Frontend projection tests | `frontend/src/tests/natalInterpretation.test.tsx` | Manual-only proof |
| Page-level tests | `frontend/src/tests/NatalChartPage.test.tsx` | Backend-only proof |
| Backend projection proof | `backend/tests/api/test_projection_real_conditions.py` | Frontend fixture comments |
| Manual QA evidence | CS-310 `evidence/` directory | Application source comments |
| Follow-up work | `_story_briefs/` or later story capsule | Hidden TODO in code |

## Mandatory Reuse / DRY Constraints

- Reuse existing `/natal` page, `NatalInterpretationSection`, projection content component, API client, and test setup.
- Reuse CS-302, CS-303, and CS-306 evidence as context only; do not copy their generated capsule content.
- Reuse existing i18n strings, CSS classes, and design tokens for any narrow UI correction.
- Do not add external packages, generated clients, new routes, duplicate projection parsers, or duplicate state machines.
- Do not store permanent sensitive birth fixtures or real personal data in source.

## No Legacy / Forbidden Paths

- No legacy QA path may be added for `/natal`.
- No compatibility projection path may be added for manual profile coverage.
- No fallback public payload display may expose internal projection data.
- Do not create aliases, shims, wrappers, duplicated QA runners, or duplicated projection clients.
- Do not add inline `style` attributes in TSX files.
- Do not change backend projection builders, prompts, providers, DB schema, migrations, auth, pricing, Stripe, or public API route shape.

## Reintroduction Guard

- Guard path 1: manual QA uses non-sensitive profiles and excludes real personal data by default.
- Guard path 2: public `/natal` output does not reveal prompt, provider, replay, admin, debug, or internal payload data.
- Guard path 3: missing birth time remains a degraded user-readable state.
- Guard path 4: controlled incomplete data remains bounded and does not crash the UI.
- Guard path 5: reproducible anomalies are visible in correction evidence or follow-up briefs.
- Required deterministic guards:
  - `rg -n "prompt|provider|replay|admin|debug|internal_payload|raw_runtime" frontend/src/pages frontend/src/features frontend/src/components`.
  - `rg -n "fetch\\(.*/v1/astrology/projections|axios\\(.*/v1/astrology/projections" frontend/src`.
  - `rg -n "style=" frontend/src/pages frontend/src/features/natal-chart frontend/src/components/natal-interpretation -g "*.tsx"`.
  - `git diff --name-only -- frontend backend _condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal _story_briefs`.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-047 `CS-029-encadrer-styles-inline-statiques-frontend` | Touched TSX files keep static styles out of inline attributes. | `rg` inline-style scan; `pnpm lint`. |
| Story-local `/natal` QA guard | Representative profiles must have traced visible outcomes. | Profile set; QA ledger; Manual check. |
| Story-local sensitive-surface guard | Public projection UI must not reveal internal payload surfaces. | `rg` scan; browser notes. |
| Story-local backend projection guard | Backend projection contract remains the runtime support proof. | `pytest`; `TestClient`. |
| Needs-investigation | Resolver returned backend docs and prediction guardrails that are non-local to this story. | Resolver output stored in evidence. |

Non-applicable examples that prevent scope drift:

- RG-002 is not selected because no backend router change is in scope.
- RG-041 is not selected because entitlement documentation is not edited.
- RG-052 is not selected because CSS namespace migration is not edited.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline summary | `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/baseline-summary.md` | Record source context. |
| Profile set | `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/profile-set.json` | Define non-sensitive profiles. |
| Manual QA ledger | `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/manual-qa-ledger.json` | Prove per-profile outcomes. |
| Sensitive-surface scan | `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/sensitive-surface-scan.txt` | Record leak checks. |
| Anomaly ledger | `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/anomalies.md` | Record corrections or follow-ups. |
| Validation log | `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/validation.txt` | Keep final validation commands. |
| Final evidence | `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/generated/10-final-evidence.md` | Summarize implementation evidence. |
| Review output | `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling, test suppression, or broad waiver is authorized.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/profile-set.json` - define profile coverage.
- `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/manual-qa-ledger.json` - record outcomes.
- `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/anomalies.md` - record findings and follow-ups.
- `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/validation.txt` - persist validation output.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - adjust only narrow orchestration defects found by QA.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - adjust only narrow rendering defects found by QA.
- `frontend/src/tests/natalInterpretation.test.tsx` - cover degraded, error, sensitive-surface, or visibility findings.
- `frontend/src/tests/NatalChartPage.test.tsx` - cover page-level findings from manual QA.
- `frontend/src/tests/natalChartApi.test.tsx` - cover API wrapper findings only when wrapper behavior changes.
- `_story_briefs/cs-310-follow-up-*.md` - create explicit follow-up briefs for out-of-scope reproducible anomalies.

Likely tests:

- `frontend/src/tests/natalInterpretation.test.tsx` - primary projection state tests.
- `frontend/src/tests/NatalChartPage.test.tsx` - page-level `/natal` tests.
- `frontend/src/tests/natalChartApi.test.tsx` - projection API wrapper tests.
- `backend/tests/api/test_projection_real_conditions.py` - real-condition projection backend tests.
- `backend/tests/api/test_projection_endpoint.py` - projection endpoint backend tests.

Files not expected to change:

- `backend/app/**` - out of scope; backend projection runtime and public contracts remain unchanged.
- `backend/alembic/**` - out of scope; no migration is touched.
- `frontend/package.json` - out of scope; no package or script change is authorized.
- `_condamad/stories/regression-guardrails.md` - out of scope; normal story generation must not enrich the registry.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: create profile set, manual QA ledger, sensitive-surface scan, anomaly ledger, final evidence, and validation log under the CS-310 capsule.
- VC2: from `frontend`, run `pnpm lint`.
- VC3: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi`.
- VC4: with venv active, run from `backend`: `python -B -m pytest -q tests\api\test_projection_real_conditions.py tests\api\test_projection_endpoint.py --tb=short`.
- VC5: from repo root, run `rg -n "prompt|provider|replay|admin|debug|internal_payload|raw_runtime" frontend/src/pages frontend/src/features frontend/src/components`.
- VC6: from repo root, run `rg -n "fetch\\(.*/v1/astrology/projections|axios\\(.*/v1/astrology/projections" frontend/src`.
- VC7: from repo root, run `rg -n "style=" frontend/src/pages frontend/src/features/natal-chart frontend/src/components/natal-interpretation -g "*.tsx"`.
- VC8: with venv active, run `python -B` to assert CS-310 profile set, QA ledger, anomaly ledger, and validation artifacts exist.

## Regression Risks

- Manual QA could drift into subjective astrology validation instead of robustness and disclosure checks.
- Incomplete data could reveal raw backend payloads while trying to explain an error.
- Browser simulation could cover only happy-path data and miss the missing-time degraded case.
- Reproducible anomalies could remain as informal notes instead of corrections or follow-up briefs.
- A narrow UI correction could introduce inline styles or duplicate projection client logic.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Start by writing the profile set before running manual or simulated browser QA.
- Keep birth profiles non-sensitive and synthetic by default.
- Keep every style change in CSS and reuse existing variables.
- Use the test user only when browser authentication is required for `/natal` execution.
- Put out-of-scope reproducible anomalies into explicit follow-up briefs.

## References

- `_story_briefs/cs-310-tests-manuels-profils-naissance-projections-natal.md`
- `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/response-samples.json`
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/frontend-after.md`
- `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/evidence/browser-qa-ledger.json`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/api/astrologyProjections.ts`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `frontend/src/tests/natalChartApi.test.tsx`
- `backend/app/services/api_contracts/public/projections.py`
- `backend/tests/api/test_projection_real_conditions.py`
- `backend/tests/api/test_projection_endpoint.py`
- `_condamad/stories/regression-guardrails.md`
