# Story CS-405 cloture-qa-live-lecture-natale: Cloture QA Live Lecture Natale
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-405-cloture-qa-live-lecture-natale.md`.
- Selected mode: Repo-informed story in Fast Story Writer Mode.
- Source problem: le rapport live CS-390/395 conserve un constat obsolète alors que CS-396 a CS-399 changent les risques de clôture.
- Source stakes: preuve authentifiée Free, Basic, Premium, richesse éditoriale, quota, rendu moderne, absence de fuite technique publique.
- Source-alignment evidence: objectif, AC, tâches, validations et guardrails couvrent chaque primitive du brief sans ajouter de fonctionnalité.

## Objective

Produire la clôture QA live de la lecture natale après CS-396 a CS-399.
Remplacer le constat obsolète par des preuves reproductibles backend, frontend et navigateur.

## Target State

- `_condamad/reports/cs-390-395-qa-live-natal-ecarts-restant.md` reflète l'état actuel de clôture.
- `_condamad/reports/cs-400-cloture-qa-live-lecture-natale.md` contient la matrice Free, Basic et Premium.
- Le rapport CS-400 contient les matrices desktop et mobile.
- Le rapport CS-400 distingue provider contrôlé, fixtures et relecture persistée.
- Le rapport CS-400 documente quota, rejet éditorial, régénération corrective Basic et risques résiduels.
- Les screenshots de preuve sont stockés sous `output/playwright/`.
- Les commandes backend, frontend et navigateur exécutées sont traçables dans les artefacts de story.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-405-cloture-qa-live-lecture-natale.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted; next available story number is `CS-405`.
- Evidence 3: `_condamad/reports/cs-390-395-qa-live-natal-ecarts-restant.md` - current live report still carries the historical QA context.
- Evidence 4: `backend/docs/narrative-natal-reading-v1-contract.md` - public narrative contract consulted.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - targeted lookup found the brief-listed local IDs.
- Evidence 6: selected guardrails include `RG-047`, `RG-052`, `RG-071`, `RG-073`, `RG-129`, `RG-149` to `RG-158`.
- Evidence 7: guardrail resolver ran for QA live natal scope; exact local IDs were kept from the brief and targeted registry lookup.
- Evidence 8: mandatory backend test paths from the brief exist in this workspace.
- Evidence 9: mandatory frontend test paths from the brief exist in this workspace.
- Repository structure alert: expected backend, frontend, reports and `output/playwright` roots exist in this workspace.
- Scope vector:
  - operation `audit`, domain `qa-live-natal-reading`
  - paths `_condamad/reports`, `backend/docs`, `backend/tests`, `frontend/src/tests`, `output/playwright`
  - contracts `narrative_natal_reading_v1`, `quota`, `public-dom`, `browser-qa`, `qa-report`

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| report CS-390/395 update | in scope | AC1, Task 1 |
| report CS-400 creation | in scope | AC2, Task 2 |
| Free profile QA | in scope | AC3, Task 3 |
| Basic profile QA | in scope | AC4, Task 4 |
| Premium profile QA | in scope | AC5, Task 5 |
| desktop matrix | in scope | AC6, Task 6 |
| mobile matrix | in scope | AC6, Task 6 |
| modern accordions | in scope | AC7, Task 7 |
| sources not empty | in scope | AC8, Task 4 |
| corrective Basic regeneration | in scope | AC9, Task 8 |
| editorial rejection quota | in scope | AC10, Task 8 |
| Basic coverage metrics | in scope | AC11, Task 9 |
| RG-155 to RG-158 guards | in scope | AC12, Task 10 |
| screenshots in `output/playwright` | in scope | AC13, Task 6 |
| provider real calls outside controlled QA | out of scope | Non-goals |
| feature changes and astrology calculations | out of scope | Non-goals |

## Domain Boundary

- Domain: qa-live-natal-reading
- In scope:
  - Report update and closure report creation under `_condamad/reports`.
  - Backend validation commands for natal narrative, rejected boundary, quota and long entitlement.
  - Frontend validation commands for `/natal` narrative rendering, public DOM, page states and astrologer mode.
  - Browser QA for Free, Basic and Premium in desktop and mobile.
  - Screenshot and command-output evidence capture.
- Out of scope:
  - New functionality, provider production calls, DB schema changes, auth model changes, i18n copy rewrites, build tooling changes and astrology calculation changes.
- Explicit non-goals:
  - No backend route change, frontend feature change, quota rule change, migration, broad tolerance entry or registry enrichment.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested QA closure and report evidence contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Only report files and story evidence artifacts may change.
  - Runtime validation may create screenshots and command logs.
  - Application behavior, contracts, tests and guardrails stay unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: live QA exposes a critical or major residual risk without a follow-up story decision.
- Additional validation rules:
  - Use backend `pytest` commands with the Python venv activated.
  - Use frontend `pnpm` commands from the repository root with `--dir frontend`.
  - Use browser QA with authenticated `daconrilcy@hotmail.com` flows for Free, Basic and Premium.
  - Use `app.routes`, `app.openapi()`, `TestClient` only when API runtime contract evidence is captured.
  - Use `AST guard` or targeted `rg` scans for public DOM denylist and legacy rendering guards.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, `TestClient`, frontend tests and browser QA prove actual behavior. |
| Baseline Snapshot | yes | Before and after report artifacts prove the old live statement was replaced. |
| Ownership Routing | yes | QA reports, screenshots and evidence logs must stay in canonical artifact paths. |
| Allowlist Exception | no | No tolerance entry is authorized for leaks, quota drift or legacy public rendering. |
| Contract Shape | yes | The closure report has mandatory sections and matrices from the brief. |
| Batch Migration | no | No multi-file migration or conversion is in scope. |
| Reintroduction Guard | yes | Guardrails RG-155 to RG-158 must remain backed by deterministic commands. |
| Persistent Evidence | yes | QA artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The old live report is updated. | Evidence profile: baseline_before_after_diff; `python` checks `_condamad/reports/cs-390-395-qa-live-natal-ecarts-restant.md`. |
| AC2 | The CS-400 closure report exists. | Evidence profile: baseline_before_after_diff; `python` checks `_condamad/reports/cs-400-cloture-qa-live-lecture-natale.md`. |
| AC3 | Free QA is documented. | Evidence profile: baseline_before_after_diff; `python` checks browser QA artifact paths. |
| AC4 | Basic QA proves five chapters. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_narrative_natal_reading_v1.py`. |
| AC5 | Premium QA preserves astrologer mode. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalAstrologerMode`. |
| AC6 | Viewport matrices are documented. | Evidence profile: baseline_before_after_diff; `python` checks report viewport headings. |
| AC7 | Modern accordions are verified. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalNarrativeReading`. |
| AC8 | Public sources are non-empty. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_narrative_natal_reading_v1.py`. |
| AC9 | Basic remediation is verified. | Evidence profile: runtime_openapi_contract; `pytest -q backend/app/tests/integration/test_natal_chart_long_entitlement.py`. |
| AC10 | Rejection preserves quota. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`. |
| AC11 | Basic coverage metrics are verified. | Evidence profile: json_contract_shape; `pytest -q backend/tests -k "natal and (narrative or rejected or quota or theme_astral)"`. |
| AC12 | RG-155 to RG-158 evidence is listed. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks report rows for `RG-155|RG-156|RG-157|RG-158`. |
| AC13 | Screenshot evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks `output/playwright` screenshot paths from the report. |
| AC14 | No critical residual risk is hidden. | Evidence profile: baseline_before_after_diff; `rg` checks report risk classification and follow-up story references. |

## Implementation Tasks

- [ ] Task 1: Update the CS-390/395 live report with the current narrative, quota and closure status. (AC: AC1)
- [ ] Task 2: Create the CS-400 closure report with all mandatory sections from the brief. (AC: AC2, AC6, AC14)
- [ ] Task 3: Execute and record authenticated Free QA with API and browser evidence. (AC: AC3, AC13)
- [ ] Task 4: Execute and record authenticated Basic QA proving five distinct chapters and non-empty sources. (AC: AC4, AC8, AC11, AC13)
- [ ] Task 5: Execute and record authenticated Premium QA proving deeper content and preserved astrologer mode. (AC: AC5, AC13)
- [ ] Task 6: Capture desktop and mobile screenshots under `output/playwright/`. (AC: AC6, AC13)
- [ ] Task 7: Verify modern narrative accordions through frontend tests and browser QA. (AC: AC7)
- [ ] Task 8: Verify corrective Basic regeneration and rejection quota behavior. (AC: AC9, AC10)
- [ ] Task 9: Record Basic editorial coverage metrics in the closure report. (AC: AC11)
- [ ] Task 10: Record guardrail evidence for `RG-155`, `RG-156`, `RG-157` and `RG-158`. (AC: AC12)
- [ ] Task 11: Persist command outputs under this story evidence directory. (AC: AC12, AC14)

## Files to Inspect First

- `_condamad/reports/cs-390-395-qa-live-natal-ecarts-restant.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/docs/narrative-natal-reading-v1-contract.md`
- `backend/tests/unit/test_narrative_natal_reading_v1.py`
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`
- `backend/app/tests/integration/test_natal_chart_long_entitlement.py`
- `backend/app/tests/integration/test_natal_interpretation_endpoint.py`
- `frontend/src/tests/natalNarrativeReading.test.tsx`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `frontend/src/tests/NatalAstrologerMode.test.tsx`

## Runtime Source of Truth

- Primary source of truth:
  - `pytest`, `TestClient`, frontend component tests, browser QA screenshots and authenticated API responses.
- Runtime evidence:
  - Backend tests prove narrative integrity, rejection boundary, quota behavior and long entitlement.
  - Frontend tests prove `/natal` rendering, modern accordions, public DOM denylist and astrologer mode.
  - Browser QA proves Free, Basic and Premium on desktop and mobile.
- Secondary evidence:
  - `app.routes` and `app.openapi()` may be captured only to document unchanged API route exposure.
  - Targeted `rg` scans prove report content and forbidden public markers.
- Static scans alone are not sufficient for this story because:
  - The closure requires authenticated runtime behavior and screenshots, not only source inspection.

## Contract Shape

- Contract type:
  - QA closure report and evidence artifact contract.
- Fields:
  - `baseline`: defect state from 2026-05-30 and updated closure statement.
  - `plan_matrix`: Free, Basic and Premium outcomes.
  - `viewport_matrix`: desktop and mobile outcomes.
  - `quota_evidence`: valid quota, rejected editorial output and corrective Basic regeneration.
  - `richness_evidence`: chapter distinctness, covered families and public sources.
  - `screenshots`: before and after paths under `output/playwright/`.
  - `commands`: executed backend, frontend and browser commands with results.
  - `guardrails`: `RG-155`, `RG-156`, `RG-157`, `RG-158` plus related local guardrails.
  - `residual_risks`: explicit severity and follow-up story reference for each major risk.
- Required fields:
  - `baseline`, `plan_matrix`, `viewport_matrix`, `quota_evidence`, `richness_evidence`, `screenshots`, `commands`, `guardrails`, `residual_risks`.
- Optional fields:
  - none.
- Status codes:
  - unchanged; this story changes reports and QA artifacts only.
- Serialization names:
  - `narrative_natal_reading_v1`, `used_astrological_elements`, `natal_chart_long` remain unchanged.
- Frontend type impact:
  - none; no generated client or type change is authorized.
- Generated contract impact:
  - no OpenAPI, migration or generated manifest change.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-405-cloture-qa-live-lecture-natale/evidence/cs-390-395-report-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-405-cloture-qa-live-lecture-natale/evidence/cs-390-395-report-after.md`
- Expected invariant:
  - The only intended persisted delta is QA reporting, screenshots and command evidence.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Live gap report update | `_condamad/reports/cs-390-395-qa-live-natal-ecarts-restant.md` | story notes only |
| Closure report | `_condamad/reports/cs-400-cloture-qa-live-lecture-natale.md` | backend docs or frontend docs |
| Browser screenshots | `output/playwright/` | `_condamad/reports` embedded binaries |
| Story command evidence | `_condamad/stories/CS-405-cloture-qa-live-lecture-natale/evidence/` | untracked console-only proof |
| Automatic review output | `_condamad/stories/CS-405-cloture-qa-live-lecture-natale/generated/11-code-review.md` | report files |

## Mandatory Reuse / DRY Constraints

- Reuse the existing CS-390/395 live report instead of creating a parallel gap tracker.
- Reuse `backend/docs/narrative-natal-reading-v1-contract.md` as the public narrative contract reference.
- Reuse existing backend and frontend tests from the brief.
- Reuse existing `output/playwright/` screenshot convention.
- Do not duplicate guardrail registry content in the report; cite IDs and executable proof.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy public rendering may be accepted as a QA pass.
- No compatibility result may count as Basic or Premium narrative proof.
- No fallback report wording may hide empty sources, duplicated chapters or quota drift.
- Do not add a shim, alias, broad tolerance register, hidden residual path, provider production call or registry enrichment.
- Forbidden public content: `chart_json`, `natal_data`, `evidence_refs`, `audit_input`, `interpretive_signal_ids`, `technical_scores`.
- Forbidden UI markers: `.ni-evidence-tags`, `.ni-projections`, `NatalInterpretationLegacyBody`, `LockedSection`.

## Reintroduction Guard

- Guard source:
  - `rg -n "RG-155|RG-156|RG-157|RG-158" _condamad/reports/cs-400-cloture-qa-live-lecture-natale.md`
  - `rg -n "ni-evidence-tags|ni-projections|NatalInterpretationLegacyBody|LockedSection" frontend/src frontend/src/tests`
  - `rg -n "fallback = response\\.sections\\[0\\]|check_and_consume" backend/app backend/tests`
- Runtime guard:
  - `pytest` commands for narrative integrity, rejected boundary, quota and long entitlement.
  - `pnpm --dir frontend test -- NatalChartPage natalNarrativeReading natalPublicDomGuard NatalAstrologerMode`.
- Browser guard:
  - Authenticated Free, Basic and Premium QA in desktop and mobile with screenshot evidence.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-047 | scope -> frontend QA -> no inline style drift in rendered `/natal`. | `pnpm` lint; browser QA. |
| RG-052 | scope -> frontend CSS -> no stale migration namespace accepted. | `pnpm` build; targeted review. |
| RG-071 | scope -> natal owner -> interpretation owner does not become monolithic. | `pnpm` page tests. |
| RG-073 | scope -> feature owner -> orchestration stays under `features/natal-chart`. | `pnpm` tests; targeted `rg`. |
| RG-129 | scope -> public JSON use -> frontend does not recalculate astrology. | `rg` anti-derivation scan. |
| RG-149 | scope -> prompt governance -> natal modern flow remains classified. | report source review. |
| RG-150 | scope -> rejected outputs -> public boundary keeps rejected payloads out. | `pytest` rejected boundary. |
| RG-152 | scope -> public narrative -> technical leak denylist remains enforced. | `pytest`; targeted `rg`. |
| RG-153 | scope -> `/natal` composition -> narrative and sources stay primary. | `pnpm` `NatalChartPage`. |
| RG-154 | scope -> DOM denylist -> public legacy markers stay absent. | `pnpm` DOM guard. |
| RG-155 | scope -> semantic integrity -> no padding or empty sources. | `pytest` narrative tests. |
| RG-156 | scope -> Basic richness -> coverage families remain proven. | `pytest` coverage metrics. |
| RG-157 | scope -> quota -> debit occurs only after accepted reading. | `pytest` quota tests. |
| RG-158 | scope -> modern accordions -> accessible chapters remain active. | `pnpm` narrative tests. |

- Needs-investigation: resolver returned generic guardrails for this broad QA scope, so exact local IDs come from the brief and targeted lookup.
- Registry gap: none; `RG-155` to `RG-158` exist in the registry.
- Non-applicable example: DB migration guardrails are out of scope because no schema change is authorized.
- Non-applicable example: auth architecture guardrails are out of scope because the test user is used only for QA.
- Non-applicable example: API route creation guardrails are out of scope because no route is added.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Report before | `_condamad/stories/CS-405-cloture-qa-live-lecture-natale/evidence/cs-390-395-report-before.md` | Preserve old report baseline. |
| Report after | `_condamad/stories/CS-405-cloture-qa-live-lecture-natale/evidence/cs-390-395-report-after.md` | Preserve updated report baseline. |
| Closure report | `_condamad/reports/cs-400-cloture-qa-live-lecture-natale.md` | Store final QA closure. |
| Backend validation | `_condamad/stories/CS-405-cloture-qa-live-lecture-natale/evidence/backend-validation.txt` | Keep backend command output. |
| Frontend validation | `_condamad/stories/CS-405-cloture-qa-live-lecture-natale/evidence/frontend-validation.txt` | Keep frontend command output. |
| Browser QA | `_condamad/stories/CS-405-cloture-qa-live-lecture-natale/evidence/browser-qa.md` | Record authenticated QA steps and outcomes. |
| Screenshots | `output/playwright/cs-400-*.png` | Keep desktop and mobile visual proof. |
| Review output | `_condamad/stories/CS-405-cloture-qa-live-lecture-natale/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | No tolerance entry is authorized for leaks, quota drift, empty sources, duplicated chapters or legacy rendering. | permanent zero-entry register |

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/reports/cs-390-395-qa-live-natal-ecarts-restant.md` - update the obsolete live QA statement.
- `_condamad/reports/cs-400-cloture-qa-live-lecture-natale.md` - create the final closure report.
- `_condamad/stories/CS-405-cloture-qa-live-lecture-natale/evidence/**` - persist command and QA artifacts.
- `output/playwright/cs-400-*.png` - persist desktop and mobile screenshots.

Likely tests:

- `backend/tests/unit/test_narrative_natal_reading_v1.py` - narrative integrity and non-empty sources.
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` - rejected output public boundary and quota evidence.
- `backend/app/tests/integration/test_natal_chart_long_entitlement.py` - Basic corrective regeneration and quota behavior.
- `backend/app/tests/integration/test_natal_interpretation_endpoint.py` - endpoint long-flow evidence.
- `frontend/src/tests/natalNarrativeReading.test.tsx` - accordions and sources.
- `frontend/src/tests/natalPublicDomGuard.test.tsx` - public DOM denylist.
- `frontend/src/tests/NatalChartPage.test.tsx` - page states and composition.
- `frontend/src/tests/NatalAstrologerMode.test.tsx` - Premium astrologer mode.

Files not expected to change:

- `backend/app/**` - out of scope; no backend behavior change is authorized.
- `frontend/src/**` - out of scope; no frontend behavior or style change is authorized.
- `_condamad/stories/regression-guardrails.md` - out of scope for normal story generation; existing IDs are referenced only.
- `backend/pyproject.toml` and `frontend/package.json` - out of scope; no dependency or script change is authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1; Push-Location backend; ruff format .; Pop-Location`
- VC2: `.\.venv\Scripts\Activate.ps1; Push-Location backend; ruff check .; Pop-Location`
- VC3: `.\.venv\Scripts\Activate.ps1; Push-Location backend; python -B -m pytest -q tests --tb=short -k "natal and (narrative or rejected or quota or theme_astral)"; Pop-Location`
- VC4a: `.\.venv\Scripts\Activate.ps1; Push-Location backend; python -B -m pytest -q --long app/tests/integration/test_natal_chart_long_entitlement.py --tb=short; Pop-Location`
- VC4b: `.\.venv\Scripts\Activate.ps1; Push-Location backend; python -B -m pytest -q --long app/tests/integration/test_natal_interpretation_endpoint.py --tb=short; Pop-Location`
- VC5: `pnpm --dir frontend test -- NatalChartPage natalNarrativeReading natalPublicDomGuard NatalAstrologerMode`
- VC6: `pnpm --dir frontend lint`
- VC7: `pnpm --dir frontend build`
- VC8: `Manual check: authenticate as daconrilcy@hotmail.com and capture Free, Basic, Premium desktop and mobile QA under output/playwright.`
- VC9: `python -B -c "from pathlib import Path; assert Path('_condamad/reports/cs-400-cloture-qa-live-lecture-natale.md').exists()"`
- VC10: `python -B -c "from pathlib import Path; assert Path('_condamad/stories/CS-405-cloture-qa-live-lecture-natale/evidence/backend-validation.txt').exists()"`
- VC11: `rg -n "RG-155|RG-156|RG-157|RG-158" _condamad/reports/cs-400-cloture-qa-live-lecture-natale.md`
- VC12: `rg -n "ni-evidence-tags|ni-projections|NatalInterpretationLegacyBody|LockedSection" frontend/src frontend/src/tests`
- VC13: `rg -n "fallback = response\\.sections\\[0\\]|check_and_consume" backend/app backend/tests`
- VC14: `python -B -c "from pathlib import Path; assert any(Path('output/playwright').glob('cs-400-*.png'))"`

`rg` scan details:

- VC11 required pattern: `RG-155|RG-156|RG-157|RG-158`.
- VC11 allowed fixture pattern: final closure report guardrail evidence rows.
- VC11 roots: `_condamad/reports/cs-400-cloture-qa-live-lecture-natale.md`.
- VC11 expected false positives: none.
- VC12 forbidden pattern: `ni-evidence-tags|ni-projections|NatalInterpretationLegacyBody|LockedSection`.
- VC12 allowed fixture pattern: test assertions proving absence are allowed only in `frontend/src/tests`.
- VC12 roots: `frontend/src`, `frontend/src/tests`.
- VC12 expected false positives: test guard definitions only.
- VC13 forbidden pattern: `fallback = response\\.sections\\[0\\]|check_and_consume`.
- VC13 allowed fixture pattern: tests proving absence or transaction behavior.
- VC13 roots: `backend/app`, `backend/tests`.
- VC13 expected false positives: test guard definitions only.

## Regression Risks

- Live QA can pass on persisted fixtures without proving a controlled provider path; the report must label each evidence source.
- Basic can show five visible chapters with duplicated or padded content; AC4, AC8 and `RG-155` require distinctness and sources.
- Rejected editorial output can consume quota before acceptance; AC10 and `RG-157` require backend proof.
- Browser QA can miss mobile regressions; AC6 and AC13 require desktop and mobile screenshots.
- Residual critical findings can be buried in prose; AC14 requires severity and follow-up story references.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep comments and docstrings in French for new or significantly modified application files.
- Activate the Python venv before every backend Python, Ruff or Pytest command.
- Do not update `_condamad/stories/regression-guardrails.md` during implementation of this story.
- Do not make provider production calls outside the controlled QA environment.

## References

- `_story_briefs/cs-405-cloture-qa-live-lecture-natale.md`
- `_condamad/reports/cs-390-395-qa-live-natal-ecarts-restant.md`
- `_condamad/stories/regression-guardrails.md#RG-047`
- `_condamad/stories/regression-guardrails.md#RG-052`
- `_condamad/stories/regression-guardrails.md#RG-071`
- `_condamad/stories/regression-guardrails.md#RG-073`
- `_condamad/stories/regression-guardrails.md#RG-129`
- `_condamad/stories/regression-guardrails.md#RG-149`
- `_condamad/stories/regression-guardrails.md#RG-150`
- `_condamad/stories/regression-guardrails.md#RG-152`
- `_condamad/stories/regression-guardrails.md#RG-153`
- `_condamad/stories/regression-guardrails.md#RG-154`
- `_condamad/stories/regression-guardrails.md#RG-155`
- `_condamad/stories/regression-guardrails.md#RG-156`
- `_condamad/stories/regression-guardrails.md#RG-157`
- `_condamad/stories/regression-guardrails.md#RG-158`
- `backend/docs/narrative-natal-reading-v1-contract.md`
- `backend/tests/unit/test_narrative_natal_reading_v1.py`
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`
- `backend/app/tests/integration/test_natal_chart_long_entitlement.py`
- `backend/app/tests/integration/test_natal_interpretation_endpoint.py`
- `frontend/src/tests/natalNarrativeReading.test.tsx`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `frontend/src/tests/NatalAstrologerMode.test.tsx`
