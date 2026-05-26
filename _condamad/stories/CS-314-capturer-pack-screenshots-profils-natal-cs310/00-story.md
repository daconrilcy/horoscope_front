# Story CS-314 capturer-pack-screenshots-profils-natal-cs310: Capture CS-310 Natal Profile Screenshot Pack
Status: ready-to-review

## Trigger / Source

Mode: Repo-informed story.

Source brief: `_story_briefs/cs-314-capturer-pack-screenshots-profils-natal-cs310.md`.

CS-310 closed with browser-equivalent proof but no fresh browser screenshots. The delivery report keeps that point as a residual visual QA
limit for `/natal` after projection wiring.

Source-alignment evidence: this story preserves the brief stakes by requiring a real browser pass, screenshots for the five CS-310
synthetic profiles, a screenshot ledger, anomaly classification, and unchanged targeted frontend/backend validation.

## Objective

Produce a reviewable browser screenshot pack for the five CS-310 synthetic natal profiles on `/natal`, without changing application code
unless a reproducible blocker is captured and converted into a bounded follow-up brief.

## Target State

- A CS-314 evidence capsule contains browser screenshots for the CS-310 profile set.
- Each screenshot is linked to route, profile, viewport, visible state, result, and artifact path in a machine-readable ledger.
- Missing-time and controlled-incomplete categories include desktop and mobile captures showing degraded or controlled error states.
- Disclaimers and absence of sensitive raw payload surfaces are visible or documented per profile.
- Targeted frontend and backend validations from the brief are rerun and persisted.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-314-capturer-pack-screenshots-profils-natal-cs310.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-314`.
- Evidence 3: `_condamad/reports/CS-307-CS-311-delivery-report.md` - residual CS-310 screenshot gap confirmed.
- Evidence 4: `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/profile-set.json` - five profiles read.
- Evidence 5: `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/manual-qa-ledger.json` - prior QA states read.
- Evidence 6: `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/browser-equivalent-notes.md` - gap read.
- Evidence 7: `frontend/src/pages/NatalChartPage.tsx` - `/natal` page surface inspected.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - registry consulted through the local resolver and targeted ID lookup.

## Domain Boundary

- Domain: frontend-browser-qa
- In scope:
  - Real browser screenshot execution for `/natal` using the CS-310 synthetic profile categories.
  - Screenshot and ledger artifacts under `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/evidence/`.
  - Targeted frontend and backend validation evidence required by the source brief.
  - Follow-up brief creation under `_story_briefs/` for any reproducible visual or runtime anomaly.
- Out of scope:
  - Backend API contract changes, DB schema, auth model, i18n policy, styling refactor, build tooling, and migrations.
  - Subjective astrology content validation.
  - New permanent E2E suite ownership.
- Explicit non-goals:
  - No modification of CS-310 synthetic profile semantics without written justification in the CS-314 ledger.
  - No new frontend feature, route, copy rewrite, entitlement policy, or analytics behavior.
  - No broad screenshot inventory outside `/natal` and the five CS-310 profile categories.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a frontend browser QA evidence pack with persistent screenshot artifacts.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Create only CS-314 evidence artifacts and follow-up briefs for proven anomalies.
  - Change application code only to unblock a reproduced issue captured by screenshot and targeted test.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the five CS-310 profile states cannot be exercised in a real browser session with available local services.
- Additional validation rules:
  - Evidence must include browser screenshots, a JSON ledger, validation logs, and source-alignment notes.
  - Runtime proof must name browser route `/natal`, viewport, profile id, visible state, and artifact path.
  - Runtime proof must include a generated manifest: `evidence/screenshot-ledger.json`.
  - Application code edits require before/after screenshots and a targeted regression test in the same implementation capsule.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Browser route `/natal`, local services, and rendered screenshots prove the visual QA surface. |
| Baseline Snapshot | yes | CS-310 browser-equivalent notes and CS-314 screenshots prove the intended evidence delta. |
| Ownership Routing | yes | Screenshot artifacts and follow-up briefs need canonical destinations. |
| Allowlist Exception | no | No allowlist handling is authorized for this QA evidence story. |
| Contract Shape | yes | The screenshot ledger has required fields and profile coverage rules. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Browser-equivalent-only closure must not replace this screenshot pack. |
| Persistent Evidence | yes | Screenshots, ledgers, and validation logs must be persisted for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The CS-314 screenshot directory exists. | Evidence profile: baseline_before_after_diff; `python` checks the screenshot directory. |
| AC2 | Every CS-310 profile has browser evidence. | Evidence profile: json_contract_shape; `python` validates `evidence/screenshot-ledger.json` profile coverage. |
| AC3 | Missing-time desktop capture exists. | Evidence profile: baseline_before_after_diff; `python` checks `cs310-missing-time-paris` desktop. |
| AC4 | Missing-time mobile capture exists. | Evidence profile: baseline_before_after_diff; `python` checks `cs310-missing-time-paris` mobile. |
| AC5 | Controlled-incomplete desktop capture exists. | Evidence profile: baseline_before_after_diff; `python` checks `cs310-controlled-incomplete` desktop. |
| AC6 | Controlled-incomplete mobile capture exists. | Evidence profile: baseline_before_after_diff; `python` checks `cs310-controlled-incomplete` mobile. |
| AC7 | Disclaimers are visible or classified per profile. | Evidence profile: json_contract_shape; `python` validates ledger `disclaimer_result`. |
| AC8 | Sensitive raw payload surfaces are absent. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans ledger and notes for payload markers. |
| AC9 | Reproducible anomalies are tracked as briefs. | Evidence profile: baseline_before_after_diff; `python` checks anomaly ledger and brief links. |
| AC10 | Targeted frontend validations pass. | Evidence profile: frontend_typecheck_no_orphan; `pnpm lint` and `vitest` output are persisted. |
| AC11 | Targeted backend validations pass. | Evidence profile: json_contract_shape; `pytest` runs projection real-condition and endpoint tests. |
| AC12 | Final evidence summarizes the browser pass. | Evidence profile: baseline_before_after_diff; `python` checks `generated/10-final-evidence.md`. |

## Implementation Tasks

- [x] Task 1: Read CS-310 profile and QA ledgers, then derive the exact five browser scenarios. (AC: AC2)
- [x] Task 2: Start the required local frontend and backend services with the standard project commands. (AC: AC8, AC9)
- [x] Task 3: Authenticate with the provided test user only when `/natal` requires an authenticated session. (AC: AC2)
- [x] Task 4: Capture desktop screenshots for all five CS-310 profiles under the CS-314 screenshot directory. (AC: AC1, AC2)
- [x] Task 5: Capture mobile screenshots for missing-time and controlled-incomplete scenarios. (AC: AC4, AC6)
- [x] Task 6: Record route, profile, viewport, visible state, result, and screenshot path in `evidence/screenshot-ledger.json`. (AC: AC2, AC3, AC4, AC5, AC6)
- [x] Task 7: Record disclaimer and sensitive-surface results for each profile. (AC: AC7, AC8)
- [x] Task 8: Create `evidence/anomaly-ledger.json` and follow-up briefs for reproducible anomalies. (AC: AC9)
- [x] Task 9: Persist frontend and backend validation output in evidence files. (AC: AC10, AC11)
- [x] Task 10: Write `generated/10-final-evidence.md` with source alignment and final QA status. (AC: AC12)

## Files to Inspect First

- `_condamad/reports/CS-307-CS-311-delivery-report.md`
- `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/profile-set.json`
- `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/manual-qa-ledger.json`
- `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/browser-equivalent-notes.md`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `backend/tests/api/test_projection_real_conditions.py`
- `backend/tests/api/test_projection_endpoint.py`

## Runtime Source of Truth

- Primary source of truth:
  - Real browser rendering of `/natal` against locally started frontend and backend services.
  - Generated manifest `evidence/screenshot-ledger.json`.
  - CS-310 `profile-set.json` for the five synthetic profile identifiers and categories.
  - `screenshot-ledger.json` for profile-to-screenshot traceability.
- Secondary evidence:
  - `pnpm lint`, targeted Vitest, and targeted backend `pytest` outputs.
- Static scans alone are not sufficient for this story because:
  - The gap is visual browser evidence, not only component or API behavior.

## Contract Shape

- Contract type:
  - Browser screenshot evidence pack and JSON ledger.
- Fields:
  - `profile_id`: one CS-310 profile id.
  - `profile_category`: one CS-310 category.
  - `route`: `/natal`.
  - `viewport`: `desktop` or `mobile`.
  - `visible_state`: rendered state observed in the browser.
  - `result`: `pass`, `blocked`, or `follow_up_created`.
  - `screenshot_path`: persisted screenshot path under the CS-314 capsule.
  - `disclaimer_result`: `visible`, `not_applicable`, or `blocked`.
  - `sensitive_surface_result`: `pass`, `blocked`, or `follow_up_created`.
- Required fields:
  - `profile_id`, `profile_category`, `route`, `viewport`, `visible_state`, `result`, and `screenshot_path`.
- Optional fields:
  - `notes`, `follow_up_brief_path`, and `validation_reference`.
- Status codes:
  - No HTTP status-code contract is owned by the screenshot ledger.
- Serialization names:
  - JSON keys are emitted exactly as listed in this section.
- Frontend type impact:
  - none, unless an implementation blocker forces a bounded code fix with tests.
- Generated contract impact:
  - `generated/10-final-evidence.md` must summarize ledger coverage and validation outcomes.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/browser-equivalent-notes.md`
  - `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/manual-qa-ledger.json`
- Comparison after implementation:
  - `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/evidence/screenshot-ledger.json`
  - `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/evidence/screenshots/`
- Expected invariant:
  - The intended delta is fresh browser screenshot evidence for the same CS-310 profile set.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Screenshot images | `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/evidence/screenshots/` | `frontend/src/**` |
| Screenshot ledger | `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/evidence/screenshot-ledger.json` | CS-310 capsule |
| Final evidence | `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/generated/10-final-evidence.md` | Repository root |
| Follow-up briefs | `_story_briefs/` with a CS-314 source reference | Code comments or tracker-only notes |

## Mandatory Reuse / DRY Constraints

- Reuse the five profile identifiers and categories from CS-310 instead of inventing new synthetic profiles.
- Reuse the existing frontend and backend validation commands from the source brief.
- Reuse the existing `/natal` page flow and central API behavior; do not duplicate business logic in a screenshot helper.
- Keep one canonical screenshot ledger; do not create parallel CSV, markdown, and JSON ledgers for the same facts.

## No Legacy / Forbidden Paths

- No legacy browser-equivalent-only closure may satisfy this story.
- No compatibility screenshot path outside the CS-314 capsule may be introduced.
- No fallback evidence based only on component tests may replace the required browser screenshots.
- Do not add route aliases, mocked public routes, or fixture-only UI states to make screenshots pass.
- Do not preserve legacy behavior through hidden mappers, aliases, broad allowlists, or duplicated profile definitions.

## Reintroduction Guard

- Guard target:
  - CS-314 must not be closed using only CS-306 screenshots or CS-310 browser-equivalent notes.
- Required guard:
  - `python` validates `screenshot-ledger.json` includes CS-314 screenshot paths for all five profile ids.
  - `rg` verifies final evidence does not classify fresh screenshot capture as skipped.

## Regression Guardrails

| Guardrail | Local invariant | Evidence |
|---|---|---|
| RG-047 `inline-styles` | A blocker fix must not add static inline TSX styles. | `rg` scan from `frontend`; targeted `pnpm lint`. |
| RG-052 `css-namespaces` | A blocker fix must not add stale migration-only CSS namespaces. | `rg` scan from `frontend`; targeted `pnpm lint`. |
| Registry gap `browser-screenshot-pack` | No exact `/natal` screenshot-pack guardrail was resolved. | Resolver output and CS-314 ledger validation. |

Non-applicable examples: RG-027 backend prediction infra, RG-041 entitlement documentation, and RG-042 LLM docs are not local to this
browser QA evidence story.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Screenshot directory | `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/evidence/screenshots/` | Keep browser captures for review. |
| Screenshot ledger | `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/evidence/screenshot-ledger.json` | Map profiles to captures. |
| Anomaly ledger | `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/evidence/anomaly-ledger.json` | Classify anomalies and follow-ups. |
| Frontend validation | `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/evidence/validation-frontend.txt` | Preserve frontend command output. |
| Backend validation | `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/evidence/validation-backend.txt` | Preserve backend command output. |
| Final evidence | `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/generated/10-final-evidence.md` | Summarize closure. |
| Review output | `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist exception: not required
- Reason: no allowlist handling is authorized for this browser QA evidence story.
- Permanence decision: permanently not authorized for this story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/evidence/screenshots/` - add screenshot files.
- `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/evidence/screenshot-ledger.json` - add ledger.
- `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/evidence/anomaly-ledger.json` - add anomaly classification.
- `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/evidence/validation-frontend.txt` - add frontend output.
- `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/evidence/validation-backend.txt` - add backend output.
- `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/generated/10-final-evidence.md` - add final evidence.
- `_story_briefs/*.md` - create follow-up briefs only for reproducible anomalies.

Likely tests:

- `frontend/src/tests/NatalChartPage.test.tsx` - targeted page-state coverage.
- `frontend/src/tests/natalInterpretation.test.tsx` - targeted projection rendering coverage.
- `frontend/src/tests/natalChartApi.test.tsx` - targeted API-client coverage.
- `backend/tests/api/test_projection_real_conditions.py` - real-condition projection coverage.
- `backend/tests/api/test_projection_endpoint.py` - projection endpoint coverage.

Files not expected to change:

- `frontend/src/pages/NatalChartPage.tsx` - inspect only unless a captured blocker requires a bounded fix.
- `frontend/src/features/natal-chart/**` - inspect only unless a captured blocker requires a bounded fix.
- `backend/app/**` - out of scope; backend API contract must stay unchanged.
- `backend/alembic/**` - out of scope; no migration is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `python -c "from pathlib import Path; p=Path('evidence/screenshots'); assert p.exists() and any(p.iterdir())"`
  - Run from `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310`.
- VC2: `python -c "import json; d=json.load(open('evidence/screenshot-ledger.json')); assert len({r['profile_id'] for r in d['entries']}) == 5"`
  - Run from `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310`.
- VC3: `python` validates desktop and mobile rows for `cs310-missing-time-paris` in `evidence/screenshot-ledger.json`.
  - Run from `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310`.
- VC4: `python` validates desktop and mobile rows for `cs310-controlled-incomplete` in `evidence/screenshot-ledger.json`.
  - Run from `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310`.
- VC5: from `frontend`, `pnpm lint`
- VC6: from `frontend`, `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi`
- VC7: activate `.venv`, then from `backend`, `python -B -m pytest -q tests\api\test_projection_real_conditions.py tests\api\test_projection_endpoint.py --tb=short`
- VC8: `rg -n "raw_payload|access_token|refresh_token|password|birth_input.*raw" _condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/evidence`
- VC9: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/generated/10-final-evidence.md').exists()"`

## Regression Risks

- Browser setup may reveal an auth or data seeding blocker not covered by CS-310 simulated evidence.
- Screenshots may expose sensitive raw payloads if the browser state is not inspected before persistence.
- A visual blocker fix could drift into product wording or styling changes outside the QA evidence objective.
- Backend validation must run with the project venv active before any Python command.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep screenshot filenames deterministic with profile id and viewport.
- Use the test user `daconrilcy@hotmail.com` only for local authenticated browser access.
- Activate `.venv` before every Python command, including backend tests and ledger validation scripts.
- Do not enrich `_condamad/stories/regression-guardrails.md` during implementation.

## References

- `_story_briefs/cs-314-capturer-pack-screenshots-profils-natal-cs310.md`
- `_condamad/reports/CS-307-CS-311-delivery-report.md`
- `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/profile-set.json`
- `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/manual-qa-ledger.json`
- `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/browser-equivalent-notes.md`
- `frontend/src/pages/NatalChartPage.tsx`
