# Story CS-423 qa-live-lecture-basic-natal-lisible: QA Live Lecture Basic Natal Lisible
Status: ready-to-review

## Trigger / Source

- Source brief: `_story_briefs/cs-423-qa-live-lecture-basic-natal-lisible.md`.
- Selected mode: Repo-informed story.
- Fast Story Writer Mode: active; `writer-contract-cheatsheet.md` was read first and used as priority contract source.
- Bounded problem: `/natal` must prove the live Basic natal reading is readable, plan-backed and free of known public leak tokens.
- Source-alignment evidence: ACs, tasks, validations, non-goals and guardrails map to the brief without product-fix drift.

## Objective

Create a QA-only evidence story proving that `/natal` renders a Basic natal reading that is readable, exact, non-repetitive and fit for a public user.
The story must capture automated backend, frontend, scan and browser evidence, then classify remaining product gaps without changing product code.

## Target State

- A representative Basic payload fixture or snapshot exists for the test profile, anonymized in persisted artifacts.
- Backend or contract tests reject the known baseline phrases in accepted Basic content.
- Frontend DOM tests prove the public Basic body has one source area, one legal area and no raw English label leak.
- Browser QA on `/natal` captures desktop and mobile screenshots for `daconrilcy@hotmail.com`.
- The QA report states whether the live reading source is compatible cache, controlled regeneration, fixture, or historical degraded data.
- Any product regression is classified in the QA report and routed to a correction story instead of being fixed inside this QA scope.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-423-qa-live-lecture-basic-natal-lisible.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-423`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted IDs `RG-152` to `RG-172` were queried.
- Evidence 4: `backend/tests/integration/test_basic_natal_v2_pipeline.py` - backend Basic V2 pipeline test exists.
- Evidence 5: `backend/tests/unit/test_basic_natal_narrative_validator.py` - backend narrative validator test exists.
- Evidence 6: `frontend/src/tests/natalPublicDomGuard.test.tsx` - public DOM guard test exists.
- Evidence 7: `frontend/src/tests/natalInterpretation.test.tsx` and `frontend/src/tests/NatalChartPage.test.tsx` exist.
- Evidence 8: `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/00-story.md` is `ready-to-dev`.
- Evidence 9: `_condamad/stories/CS-422-simplifier-rendu-basic-natal-sources-mentions-legales/00-story.md` is `ready-to-dev`.
- Evidence 10: CS-424 and CS-425 story files are not present yet; their briefs remain mandatory upstream source context.

## Domain Boundary

- Domain: qa-live-basic-natal
- In scope:
  - QA tests, fixtures, scans, browser captures and evidence report for `/natal` Basic V2 public reading.
  - Classification of remaining gaps as blocking, accepted, or out of scope.
  - Verification of live reading origin: compatible cache, controlled regeneration, fixture, or historical degraded data.
- Out of scope:
  - Backend generation changes, frontend rendering changes, DB migrations, auth, i18n rewrites, offers, quotas and provider calls.
  - Mass migration of historical readings.
  - Product correction under a QA story.
- Explicit non-goals:
  - No new public API contract.
  - No new frontend route, screen or style implementation.
  - No prompt, cache, generation, quota or persistence behavior change.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a QA evidence story spanning backend tests, frontend DOM tests and browser QA.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add or adjust only tests, fixtures, scans, browser evidence and QA artifacts.
  - Product runtime code is unchanged unless a test or evidence artifact is demonstrably wrong.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: live `/natal` cannot be exercised with the provided test user in the local environment.
- Additional validation rules:
  - Runtime evidence must include `pytest`, Vitest DOM tests, targeted `rg` scans and browser screenshots.
  - The QA report must classify every remaining product gap before the story can move beyond implementation.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, DOM tests, browser QA and captured payload prove the final live behavior. |
| Baseline Snapshot | yes | API payload, DOM text and screenshots prove before/after QA evidence. |
| Ownership Routing | yes | QA artifacts must stay in test and story evidence owners, not product code. |
| Allowlist Exception | no | No broad allowlist handling is authorized for public leak tokens. |
| Contract Shape | yes | The Basic QA report, DOM text and payload artifact shape must be explicit. |
| Batch Migration | no | No batch migration or data conversion is in scope. |
| Reintroduction Guard | yes | Known baseline phrases, raw labels and technical markers must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Payload excludes baseline phrases. | Evidence profile: targeted_forbidden_symbol_scan; `pytest -q backend/tests/integration/test_basic_natal_v2_pipeline.py`. |
| AC2 | Public DOM text excludes baseline phrases. | Evidence profile: targeted_forbidden_symbol_scan; `pnpm --dir frontend test -- natalPublicDomGuard`. |
| AC3 | Public DOM body excludes raw English astrology labels. | Evidence profile: targeted_forbidden_symbol_scan; `pnpm --dir frontend test -- natalPublicDomGuard`. |
| AC4 | Public DOM body excludes unaccented public labels. | Evidence profile: targeted_forbidden_symbol_scan; `pnpm --dir frontend test -- natalPublicDomGuard`. |
| AC5 | Basic DOM renders at most one source zone. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalPublicDomGuard`. |
| AC6 | Basic DOM renders at most one legal zone. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalPublicDomGuard`. |
| AC7 | Valid Basic V2 does not show regeneration message. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalChartPage`. |
| AC8 | QA payload remains plan-backed. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/unit/test_basic_natal_narrative_validator.py`. |
| AC9 | Live `/natal` desktop screenshot is persisted. | Evidence profile: baseline_before_after_diff; `python` checks the desktop screenshot path. |
| AC10 | Live `/natal` mobile screenshot is persisted. | Evidence profile: baseline_before_after_diff; `python` checks the mobile screenshot path. |
| AC11 | QA report classifies remaining gaps. | Evidence profile: baseline_before_after_diff; `python` checks `evidence/qa-report.md`. |
| AC12 | QA report states the live reading origin. | Evidence profile: baseline_before_after_diff; `python` checks `evidence/qa-report.md`. |
| AC13 | Historical degraded live content blocks QA closure. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans evidence payload, DOM text and report. |
| AC14 | Validation output is persisted. | Evidence profile: baseline_before_after_diff; `python` checks `evidence/validation.txt`. |
| AC15 | QA report confirms the final report introduction. | Evidence profile: baseline_before_after_diff; `python` checks `evidence/qa-report.md`. |
| AC16 | QA report confirms at least three explanatory themes. | Evidence profile: baseline_before_after_diff; `python` checks `evidence/qa-report.md`. |
| AC17 | QA report confirms the final report conclusion. | Evidence profile: baseline_before_after_diff; `python` checks `evidence/qa-report.md`. |

## Implementation Tasks

- [ ] Task 1: Create or update the representative Basic payload fixture or snapshot for the test profile. (AC: AC1, AC8)
- [ ] Task 2: Extend backend or contract tests for the known baseline phrase denylist. (AC: AC1, AC8)
- [ ] Task 3: Extend frontend DOM guards for source-zone, legal-zone, English-label and unaccented-label checks. (AC: AC2, AC3, AC4, AC5, AC6, AC7)
- [ ] Task 4: Run local `/natal` browser QA with the provided test user and capture desktop evidence. (AC: AC9)
- [ ] Task 5: Run local `/natal` browser QA with the provided test user and capture mobile evidence. (AC: AC10)
- [ ] Task 6: Persist payload, DOM text, screenshots and validation output under this story evidence folder. (AC: AC9, AC10, AC14)
- [ ] Task 7: Write `evidence/qa-report.md` with gap classification, live origin and readable report structure. (AC: AC11, AC12, AC13, AC15, AC16, AC17)
- [ ] Task 8: Stop QA closure if live evidence still contains known degraded historical tokens. (AC: AC2, AC13)

## Files to Inspect First

- `_story_briefs/cs-423-qa-live-lecture-basic-natal-lisible.md` - source brief.
- `_condamad/stories/regression-guardrails.md` - targeted local guardrail IDs only.
- `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/00-story.md` - editorial upstream story.
- `_condamad/stories/CS-422-simplifier-rendu-basic-natal-sources-mentions-legales/00-story.md` - DOM upstream story.
- `_story_briefs/cs-424-verifier-corriger-generation-prompts-basic-natal.md` - prompt upstream brief until story exists.
- `_story_briefs/cs-425-invalider-regenerer-lectures-basic-natal-degradees.md` - cache upstream brief until story exists.
- `backend/tests/integration/test_basic_natal_v2_pipeline.py` - Basic V2 pipeline test.
- `backend/tests/unit/test_basic_natal_narrative_validator.py` - Basic narrative validator test.
- `frontend/src/tests/natalInterpretation.test.tsx` - Basic rendering test surface.
- `frontend/src/tests/natalPublicDomGuard.test.tsx` - public DOM denylist and structure guard.
- `frontend/src/tests/NatalChartPage.test.tsx` - page-level `/natal` behavior.

## Runtime Source of Truth

- Primary source of truth:
  - Backend `pytest` results, frontend DOM tests, local browser `/natal` session and persisted artifacts.
- Secondary evidence:
  - `AST guard` coverage from frontend DOM tests and targeted `rg` scans for known phrases, raw labels and technical markers.
- Static scans alone are not sufficient for this story because:
  - The live profile may be served from compatible cache, controlled regeneration, fixture, or degraded historical data.

## Contract Shape

- Contract type:
  - QA evidence bundle for Basic V2 public `/natal` reading.
- Fields:
  - `basic-readable-api-after.json`: accepted Basic API payload evidence.
  - `basic-readable-dom-text-after.txt`: extracted rendered DOM text evidence.
  - `basic-readable-desktop-after.png`: desktop browser capture.
  - `basic-readable-mobile-after.png`: mobile browser capture.
  - `validation.txt`: executed validation command output.
  - `qa-report.md`: gap classification, live origin and closure decision.
- Required fields:
  - payload artifact, DOM text artifact, desktop screenshot, mobile screenshot, validation output and QA report.
- Optional fields:
  - anonymized fixture snapshot used by tests.
- Status codes:
  - none; no API route contract is added or changed.
- Serialization names:
  - artifact filenames are emitted exactly as listed in Persistent Evidence Artifacts.
- Frontend type impact:
  - none; test-only fixture types may be reused from existing test helpers.
- Generated contract impact:
  - none; `app.openapi()` is out of scope because no route contract changes.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - User-observed DOM from `/natal` on 2026-05-31 18:22, summarized in the source brief.
- Comparison after implementation:
  - `_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/basic-readable-dom-text-after.txt`
  - `_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/basic-readable-api-after.json`
- Expected invariant:
  - The QA evidence contains no known degraded phrase, no repeated source/legal blocks and no raw public technical marker.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Backend Basic QA fixture | `backend/tests/**` | `backend/app/**` product runtime code |
| Frontend public DOM guard | `frontend/src/tests/**` | Production components for QA-only logic |
| Browser evidence | `_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/**` | Source or fixture directories |
| QA closure report | `_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/qa-report.md` | Product code comments |

## Mandatory Reuse / DRY Constraints

- Reuse existing Basic V2 pipeline tests, narrative validator tests and DOM guard helpers.
- Reuse existing frontend test payload builders before adding a new fixture helper.
- Keep one denylist source inside the test layer for the CS-423 known baseline tokens.
- Do not duplicate product rendering or backend generation logic inside QA artifacts.
- Keep comments and docstrings in French for any new non-trivial test helper.

## No Legacy / Forbidden Paths

- No legacy route path may be added for QA.
- No compatibility rendering path may be added for QA.
- No fallback content path may be added for QA.
- Product runtime code must not be changed to pass this QA story.
- Forbidden public text includes `cette lecture s'appuie uniquement`, `Ce repere retient` and `avec une confiance editoriale controlee`.
- Forbidden raw labels include `moon`, `sun`, `saturn`, `north node` and `south node` in the main public body.
- Forbidden technical markers include `visibility_expression`, `audit_input`, `condition_axis:`, `interpretive_signal_ids` and scores.

## Reintroduction Guard

- Guard exact baseline phrases with backend tests, frontend DOM tests and targeted `rg` scans.
- Guard duplicate source and legal blocks with rendered DOM tests.
- Guard historical degraded live content by scanning persisted payload, DOM text and QA report artifacts.
- Guard raw labels and unaccented public labels with frontend DOM tests and scan evidence.

## Regression Guardrails

| Guardrail | Scope -> invariant -> evidence |
|---|---|
| RG-152 public leak guard | Basic public text -> no technical payload leak -> backend `pytest`, DOM tests and technical-marker `rg`. |
| RG-153 `/natal` public focus | `/natal` live QA -> public reading remains central -> `pnpm` page tests and screenshots. |
| RG-154 public DOM denylist | Public DOM -> no denylisted markers -> `pnpm --dir frontend test -- natalPublicDomGuard`. |
| RG-155 semantic integrity | Basic narrative -> no duplicated content -> backend `pytest` and DOM text artifact. |
| RG-156 editorial diversity | Basic themes -> at least three explanatory themes -> QA report and DOM text artifact. |
| RG-164 plan-backed Basic | Basic payload -> linked to `BasicNatalReadingPlan` -> backend `pytest`. |
| RG-165 privacy guard | Basic payload/public text -> no PII, scores, paths or raw IDs -> `rg` scan and QA report. |
| RG-166 draft validation | Accepted Basic draft -> plan match -> narrative validator `pytest`. |
| RG-167 runtime engine | Basic complete -> `basic-natal-reading-v1` origin -> QA report and backend `pytest`. |
| RG-168 Basic V2 contract | Basic V2 public contract -> canonical fields retained -> backend `pytest` and frontend tests. |
| RG-170 DOM Basic dedupe | Basic V2 DOM -> one source area and one legal area -> DOM guard and build. |

- Registry gap: `RG-169` is absent from the registry query; keep it as source context for CS-421 only.
- Registry gap: `RG-171` is absent from the registry query; keep it as source context for CS-424 only.
- Registry gap: `RG-172` is absent from the registry query; keep it as source context for CS-425 only.
- Non-applicable examples: DB migration guardrails, auth guardrails and style-system guardrails are out of this QA evidence scope.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| API payload | `_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/basic-readable-api-after.json` | Capture final Basic payload. |
| DOM text | `_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/basic-readable-dom-text-after.txt` | Capture public text. |
| Desktop screenshot | `_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/basic-readable-desktop-after.png` | Prove desktop rendering. |
| Mobile screenshot | `_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/basic-readable-mobile-after.png` | Prove mobile rendering. |
| Validation output | `_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/validation.txt` | Keep command outputs. |
| QA report | `_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/qa-report.md` | Classify gaps and origin. |
| Review output | `_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/generated/11-code-review.md` | Keep automatic review separate. |

## Allowlist / Exception Register

- Allowlist Exception: not applicable
- Reason: no broad allowlist handling is authorized for known degraded tokens, raw labels or technical markers.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step data conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/tests/integration/test_basic_natal_v2_pipeline.py` - add Basic QA payload phrase assertions.
- `backend/tests/unit/test_basic_natal_narrative_validator.py` - add accepted-content guard assertions.
- `frontend/src/tests/natalPublicDomGuard.test.tsx` - add DOM structure and denylist assertions.
- `frontend/src/tests/natalInterpretation.test.tsx` - reuse or extend representative Basic payload fixture.
- `frontend/src/tests/NatalChartPage.test.tsx` - cover valid Basic V2 page behavior.
- `_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/**` - persist QA evidence artifacts.

Likely tests:

- `backend/tests/integration/test_basic_natal_v2_pipeline.py`
- `backend/tests/unit/test_basic_natal_narrative_validator.py`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`

Files not expected to change:

- `backend/app/**` - product runtime code is out of scope for QA closure.
- `frontend/src/components/**` - product rendering code is out of scope for QA closure.
- `backend/app/infra/**` - no persistence adapter or DB access change is authorized.
- `_condamad/stories/regression-guardrails.md` - normal story generation must not enrich the registry.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: Activate the venv before all Python commands:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- VC2: Backend targeted tests from the repository root:
  ```powershell
  python -B -m pytest -q backend/tests/integration/test_basic_natal_v2_pipeline.py backend/tests/unit/test_basic_natal_narrative_validator.py --tb=short
  ```
- VC3: Backend lint and format from the repository root:
  ```powershell
  ruff format backend
  ruff check backend
  ```
- VC4: Frontend DOM tests:
  ```powershell
  pnpm --dir frontend test -- natalInterpretation natalPublicDomGuard NatalChartPage
  ```
- VC5: Frontend lint:
  ```powershell
  pnpm --dir frontend lint
  ```
- VC6: Frontend build:
  ```powershell
  pnpm --dir frontend build
  ```
- VC7: Baseline phrase scan:
  ```powershell
  rg -n `
    "cette lecture s'appuie uniquement|Ce repere retient|avec une confiance editoriale controlee|Luminaire: moon|Position planetaire:|north node|south node" `
    backend/app frontend/src backend/tests frontend/src/tests
  ```
  - Forbidden pattern: known baseline phrases and raw public labels.
  - Allowed fixture pattern: denylist constants inside test files and QA evidence reports.
  - Scan roots: backend app/tests and frontend src/tests only.
  - Expected false positives: tests defining the denylist and QA report classification lines.
- VC8: Unaccented public label scan:
  ```powershell
  rg -n "\b(Synthese|theme|themes|repere|planetaire|a integrer)\b" backend/app frontend/src backend/tests frontend/src/tests
  ```
  - Forbidden pattern: unaccented public labels in runtime public text.
  - Allowed fixture pattern: denylist constants in tests and source brief references.
  - Scan roots: backend app/tests and frontend src/tests only.
  - Expected false positives: tests defining expected denied tokens.
- VC9: Technical marker scan:
  ```powershell
  rg -n "visibility_expression|audit_input|condition_axis:|interpretive_signal_ids|projection_version|ranking_score|weighted_score|prompt_hint" backend/app frontend/src
  ```
  - Forbidden pattern: public technical carriers and scoring markers.
  - Allowed fixture pattern: none in runtime roots for public rendering.
  - Scan roots: backend app and frontend src.
  - Expected false positives: internal validators only when proven non-public in QA report.
- VC10: Persist evidence artifacts:
  ```powershell
  python -c "from pathlib import Path; root=Path('_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence'); assert root.exists()"
  python -c "from pathlib import Path; root=Path('_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence'); assert (root/'qa-report.md').exists()"
  $p = '_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/qa-report.md'
  $env:QA_REPORT = $p
  python -c "import os,pathlib; t=pathlib.Path(os.environ['QA_REPORT']).read_text().lower(); assert all(x in t for x in ['introduction','conclusion','trois themes'])"
  python -c "from pathlib import Path; root=Path('_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence'); assert (root/'validation.txt').exists()"
  ```

## Regression Risks

- A clean fixture can hide a live historical degraded cache for `daconrilcy@hotmail.com`.
- Browser QA can pass visually while persisted payload evidence still contains a denied token.
- DOM tests can count source/legal zones but miss repeated content in a collapsed or hidden branch.
- Treating CS-424 or CS-425 as already implemented would create a false closure; their missing story files must remain visible in the report.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Do not modify product runtime code except to correct a demonstrably false test or evidence artifact.
- Use the provided test user only for local browser QA and avoid persisting the password.
- Persist browser captures and extracted text before classifying QA closure.
- Route product regressions to a correction story rather than fixing them inside CS-423.

## References

- `_story_briefs/cs-423-qa-live-lecture-basic-natal-lisible.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/00-story.md`
- `_condamad/stories/CS-422-simplifier-rendu-basic-natal-sources-mentions-legales/00-story.md`
- `_story_briefs/cs-424-verifier-corriger-generation-prompts-basic-natal.md`
- `_story_briefs/cs-425-invalider-regenerer-lectures-basic-natal-degradees.md`
- `backend/tests/integration/test_basic_natal_v2_pipeline.py`
- `backend/tests/unit/test_basic_natal_narrative_validator.py`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
