# Story CS-383 fermeture-findings-generation-theme-natal: Close Natal Generation Adversarial Review Findings
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-383-corriger-findings-review-adversariale-generation-theme-natal.md`.
- Selected mode: Audit-to-story.
- Problem statement: findings from CS-382 must be classified, corrected, accepted with owner, or proven false before closure.
- Source stakes: creation payload validity, complete `traditional_conditions`, frontend stability, non-invention, and prompt enrichment.
- Closure expectation: no actionable `Critical`, `High`, or `Medium` finding remains open after correction and re-review.
- Source-alignment evidence: PASS; objective, ACs, tasks, validation, non-goals, and guardrails preserve every brief concern.

## Objective

Close the actionable CS-382 adversarial review findings by applying the smallest coherent code, test, and documentation changes.
The story must prove corrected natal generation behavior, frontend tolerance, and intact prompt-visible enrichment.

## Target State

- `_condamad/reports/cs-383-corrections-findings-generation-theme-natal.md` records every CS-382 finding and its decision.
- Every actionable `Critical`, `High`, and `Medium` finding is corrected or has a documented false-positive proof.
- Every `Low` finding is corrected or accepted with justification and owner.
- `POST /v1/users/me/natal-chart` remains the priority runtime proof for a theme with known birth time.
- `traditional_conditions` is complete whenever reliable calculation is possible.
- `traditional_conditions` is absent only for a documented reliable-calculation blocker such as missing time data.
- `NatalExpertPanel` tolerates partial payloads without computing astrology facts locally.
- `theme_astral_llm_input_v1` enrichment remains prompt-visible and separate from public UI payload carriers.
- CS-382 or a targeted equivalent re-review is rerun after corrections and persisted in the CS-383 report.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-383-corriger-findings-review-adversariale-generation-theme-natal.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-383`.
- Evidence 3: `_condamad/stories/CS-382-review-adversariale-generation-theme-natal/00-story.md` - source review story read.
- Evidence 4: `_condamad/reports/cs-382-review-adversariale-generation-theme-natal.md` - report read; finding register is empty.
- Evidence 5: backend and frontend target roots exist in this workspace.
- Evidence 6: required backend and frontend files named by the brief exist in this workspace.
- Evidence 7: `resolve_guardrails.py` selected backend API, frontend, and local validation guardrails for this scope.
- Source-alignment evidence: the story keeps the brief's full closure ledger and does not replace correction with reporting only.

## Domain Boundary

- Domain: natal-generation-correction
- In scope:
  - Classification and closure of every CS-382 finding.
  - Backend natal chart creation payload and `traditional_conditions` calculation/projection behavior.
  - Backend prompt payload enrichment through `theme_astral_llm_input_v1`.
  - Frontend `NatalExpertPanel` and natal API client behavior required by CS-382 findings.
  - Regression tests, targeted docs, validation evidence, re-review output, and CS-383 closure report.
- Out of scope:
  - Provider LLM calls, unrelated findings, product contract redesign, DB schema changes, auth, i18n, styling, build tooling, and migrations.
- Explicit non-goals:
  - No real LLM provider invocation.
  - No new partial public contract for `traditional_conditions`.
  - No prompt wording rewrite outside a CS-382 finding.
  - No modification of the CS-382 report to hide a finding.
  - No correction outside the CS-382 finding list.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits post-review correction across natal runtime, prompt payload, and frontend guard surfaces.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Change only files required to close CS-382 findings.
  - Preserve the public natal chart contract outside the specific corrected finding surface.
  - Preserve `theme_astral_llm_input_v1` as the prompt source of truth.
  - Preserve frontend non-invention: display only backend-provided astrology facts.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: a CS-382 finding requires changing the product contract for `traditional_conditions`.
- Additional validation rules:
  - Runtime proof must include `pytest` or `TestClient` for `POST /v1/users/me/natal-chart`.
  - Route inventory proof must name `app.routes` and `app.openapi()` for natal endpoints.
  - Frontend proof must include `pnpm` validation for `NatalExpertPanel`, `BirthProfilePage`, or `natalChartApi`.
  - Prompt proof must verify `theme_astral_llm_input_v1` enrichment and provider payload separation.
  - Every corrected finding must have a regression test or a precise proof artifact in the closure report.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `TestClient`, `pytest`, `app.routes`, `app.openapi()`, and `pnpm` prove corrected behavior. |
| Baseline Snapshot | yes | CS-382 findings, before/after evidence, and closure report prove the allowed surface delta. |
| Ownership Routing | yes | Each finding must route to backend, frontend, prompt, test, docs, or acceptance owner. |
| Allowlist Exception | no | No broad allowlist handling is authorized for unresolved review findings. |
| Contract Shape | yes | The CS-383 closure report has mandatory fields and finding decisions. |
| Batch Migration | no | No batch migration or multi-file conversion program is in scope. |
| Reintroduction Guard | yes | Prior crash, partial payload, old carrier, and prompt enrichment regressions must stay closed. |
| Persistent Evidence | yes | Report, validation output, guardrail output, and re-review handoff must be persisted. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Every CS-382 finding has a decision. | Evidence profile: json_contract_shape; `python` checks the CS-383 report finding ledger. |
| AC2 | No actionable major finding remains open. | Evidence profile: json_contract_shape; `rg` scans CS-383 report severities and open status. |
| AC3 | Every correction has proof. | Evidence profile: baseline_before_after_diff; `python` checks test or artifact links in the report. |
| AC4 | POST creation remains the primary proof. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests --tb=short -k "natal_chart"`. |
| AC5 | Known-time traditions stay complete. | Evidence profile: json_contract_shape; `pytest -q backend/tests --tb=short -k "traditional_conditions"`. |
| AC6 | Reliable absence is bounded. | Evidence profile: json_contract_shape; `pytest -q backend/tests --tb=short -k "no_time or traditional_conditions"`. |
| AC7 | Frontend avoids local astrology derivation. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans `NatalExpertPanel` derivation tokens. |
| AC8 | Frontend partial payloads render safely. | Evidence profile: frontend_typecheck_no_orphan; `pnpm --dir frontend test -- NatalExpertPanel BirthProfilePage natalChartApi`. |
| AC9 | Prompt enrichment remains present. | Evidence profile: json_contract_shape; `pytest -q backend/tests --tb=short -k "theme_astral or llm_astrology_input"`. |
| AC10 | Old prompt carriers are not source of truth. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans `chart_json`, `natal_data`, and prompt carriers. |
| AC11 | Re-review result is persisted. | Evidence profile: baseline_before_after_diff; `python` checks the CS-383 report re-review section. |
| AC12 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-383 evidence paths. |
| AC13 | Runtime route inventory is proven. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`. |

## Implementation Tasks

- [ ] Task 1: Read the CS-382 report, CS-382 story, and the CS-379 through CS-381 implementation evidence. (AC: AC1)
- [ ] Task 2: Classify each CS-382 finding as corrected, accepted, false positive, or out of scope. (AC: AC1, AC2)
- [ ] Task 3: Correct actionable backend natal payload findings with focused tests. (AC: AC3, AC4, AC5, AC6)
- [ ] Task 4: Correct actionable frontend rendering or API-client findings with focused tests. (AC: AC3, AC7, AC8)
- [ ] Task 5: Correct actionable prompt payload enrichment findings with focused tests. (AC: AC3, AC9, AC10)
- [ ] Task 6: Preserve `POST /v1/users/me/natal-chart` route evidence through the loaded app. (AC: AC4, AC13)
- [ ] Task 7: Persist validation output, guardrail output, and before/after evidence for the correction set. (AC: AC11, AC12)
- [ ] Task 8: Rerun CS-382 or a targeted equivalent re-review against changed files. (AC: AC2, AC11)
- [ ] Task 9: Write the CS-383 closure report with findings, decisions, fixes, tests, commands, re-review, and risks. (AC: AC1, AC11)

## Files to Inspect First

- `_condamad/reports/cs-382-review-adversariale-generation-theme-natal.md`
- `_condamad/stories/CS-382-review-adversariale-generation-theme-natal/00-story.md`
- `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/00-story.md`
- `_condamad/stories/CS-380-durcir-natal-expert-panel-contre-payloads-partiels/00-story.md`
- `_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts/00-story.md`
- `backend/app/services/chart/json_builder.py`
- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `frontend/src/features/natal-chart/NatalExpertPanel.tsx`
- `frontend/src/api/natal-chart/index.ts`
- `backend/tests/**`
- `frontend/src/tests/**`
- `frontend/e2e/**`

## Runtime Source of Truth

- Primary source of truth:
  - `pytest` or `TestClient` assertions for `POST /v1/users/me/natal-chart`.
  - `app.routes` and `app.openapi()` from the loaded FastAPI app for natal endpoint inventory.
  - Backend pytest assertions for `traditional_conditions` and `theme_astral_llm_input_v1`.
  - Vitest, Testing Library, or build proof for `NatalExpertPanel`, `BirthProfilePage`, and `natalChartApi`.
- Secondary evidence:
  - Targeted `rg` scans for old carriers, frontend derivation, plan coupling, and unresolved finding terms.
- Static scans alone are not sufficient for this story because:
  - The brief requires runtime closure of a creation payload bug and prompt-visible enrichment non-regression.

## Contract Shape

- Contract type:
  - Correction closure report for CS-382 adversarial findings.
- Fields:
  - `Liste des findings CS-382`: each finding identifier, severity, source, and evidence.
  - `Decision par finding`: corrected, accepted, false positive, or out of scope.
  - `Correction appliquee`: changed files, tests, and proof for every corrected finding.
  - `Commandes executees`: command, status, and persisted output path.
  - `Resultat de re-review`: post-correction review verdict and remaining risks.
  - `Risques residuels acceptes`: owner and justification for every accepted residual risk.
- Required fields:
  - `Liste des findings CS-382`, `Decision par finding`, `Correction appliquee`, `Commandes executees`.
  - `Resultat de re-review`, `Risques residuels acceptes`.
- Optional fields:
  - none.
- Status codes:
  - `200` remains expected for successful `POST /v1/users/me/natal-chart` validation cases.
- Serialization names:
  - `traditional_conditions` and `theme_astral_llm_input_v1` must keep their exact names.
- Frontend type impact:
  - `frontend/src/api/natal-chart/index.ts` remains the nominal client contract touched by findings only.
- Generated contract impact:
  - `app.openapi()` must expose `/v1/users/me/natal-chart` with method `post`.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-383-fermeture-findings-generation-theme-natal/evidence/findings-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-383-fermeture-findings-generation-theme-natal/evidence/findings-after.md`
- Expected invariant:
  - The only intended surface delta is the correction of CS-382 findings and their focused tests or documentation.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Closure report | `_condamad/reports/cs-383-corrections-findings-generation-theme-natal.md` | CS-382 report |
| Public natal payload | `backend/app/services/chart/json_builder.py` | Frontend mapper |
| Traditional calculations | `backend/app/domain/astrology/advanced_conditions/**` | UI component |
| LLM input mapping | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | Public payload builder |
| Provider prompt payload | `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` | Frontend API client |
| Natal frontend rendering | `frontend/src/features/natal-chart/NatalExpertPanel.tsx` | Backend domain layer |
| Natal API client | `frontend/src/api/natal-chart/index.ts` | Component-local parser |

## Mandatory Reuse / DRY Constraints

- Reuse the CS-382 finding list as the correction ledger.
- Reuse existing natal chart and prompt payload builders instead of duplicating projection logic.
- Reuse existing frontend API client types instead of adding component-local payload contracts.
- Add focused regression tests beside the existing backend or frontend tests for the corrected surface.
- Do not duplicate astrology calculation rules in React.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy prompt carrier may become the source of truth for `theme_astral_llm_input_v1`.
- No compatibility route, UI adapter, or prompt carrier may be added to close a finding.
- No fallback React calculation may be added for `hayz`, `rejoicing`, dignities, or scores.
- No finding may be hidden by editing the CS-382 report instead of recording CS-383 closure.
- No old `chart_json` or `natal_data` carrier may replace the canonical provider payload input.
- Do not preserve legacy behavior.

## Reintroduction Guard

- Guard target: prevent the original natal generation defect or a prompt enrichment regression from returning.
- Forbidden surfaces:
  - Closing a major finding without test or proof artifact.
  - Treating `GET /latest` as sufficient proof while skipping `POST /v1/users/me/natal-chart`.
  - Suppressing `traditional_conditions` for plan-tier or UI convenience reasons.
  - Computing astrology facts inside `NatalExpertPanel`.
  - Feeding prompt construction from public UI carriers instead of canonical provider payload input.
- Required guard evidence:
  - `python -B -m pytest -q tests --tb=short -k "natal_chart or traditional_conditions or theme_astral or llm_astrology_input"`
  - `pnpm --dir frontend test -- NatalExpertPanel BirthProfilePage natalChartApi`
  - `rg -n "traditional_conditions|chart_json|natal_data|llm_astrology_input_v1|theme_astral_llm_input_v1" backend/app backend/tests frontend/src`

## Regression Guardrails

| Guardrail | Applied invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | API business logic stays outside router surfaces. | `pytest`; diff review. |
| RG-003 `converge-api-v1-route-architecture` | Natal endpoint proof comes from the loaded app. | `app.routes`; `app.openapi()`. |
| RG-047 `CS-029-encadrer-styles-inline-statiques-frontend` | Touched TSX must not add inline style drift. | `rg`; `pnpm lint`. |
| RG-129 `CS-202-natal-expert-panel` | Frontend displays only backend-provided natal facts. | `pnpm`; targeted `rg`. |
| RG-131 `CS-204-hayz-rejoicing-explicit-condition-contracts` | `traditional_conditions` stays normalized from calculated facts. | `pytest`; targeted `rg`. |

Non-applicable examples:

- RG-007 admin LLM observability is out of scope because no admin endpoint behavior is touched.
- RG-027 prediction infra is out of scope because the correction domain is natal generation.
- RG-041 entitlement documentation is out of scope because plan policy is validated in runtime behavior, not docs.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Closure report | `_condamad/reports/cs-383-corrections-findings-generation-theme-natal.md` | Keep final finding decisions. |
| Findings before | `_condamad/stories/CS-383-fermeture-findings-generation-theme-natal/evidence/findings-before.md` | Baseline finding ledger. |
| Findings after | `_condamad/stories/CS-383-fermeture-findings-generation-theme-natal/evidence/findings-after.md` | Closure ledger. |
| Guardrail output | `_condamad/stories/CS-383-fermeture-findings-generation-theme-natal/evidence/guardrails.txt` | Resolver result. |
| Validation output | `_condamad/stories/CS-383-fermeture-findings-generation-theme-natal/evidence/validation.txt` | Command results. |
| Re-review output | `_condamad/stories/CS-383-fermeture-findings-generation-theme-natal/evidence/re-review.md` | Post-correction review proof. |
| Review output | `_condamad/stories/CS-383-fermeture-findings-generation-theme-natal/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no broad allowlist handling is authorized for unresolved review findings or prompt-carrier drift.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/reports/cs-383-corrections-findings-generation-theme-natal.md` - closure report.
- `backend/app/services/chart/json_builder.py` - likely public payload correction owner.
- `backend/app/domain/astrology/advanced_conditions/**` - likely traditional conditions correction owner.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - likely LLM input correction owner.
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` - likely provider payload correction owner.
- `frontend/src/features/natal-chart/NatalExpertPanel.tsx` - likely frontend rendering correction owner.
- `frontend/src/api/natal-chart/index.ts` - likely frontend API contract correction owner.
- `_condamad/stories/CS-383-fermeture-findings-generation-theme-natal/evidence/**` - persisted evidence.
- `_condamad/stories/CS-383-fermeture-findings-generation-theme-natal/generated/11-code-review.md` - review handoff.

Likely tests:

- `backend/tests/**` selected by `natal_chart`, `traditional_conditions`, `theme_astral`, and `llm_astrology_input`.
- `frontend/src/tests/NatalExpertPanel.test.tsx`
- `frontend/src/tests/BirthProfilePage.test.tsx`
- `frontend/src/api/natal-chart/index.ts` type/build witness.

Files not expected to change:

- `backend/alembic/**` - out of scope; no migration is authorized.
- `frontend/src/styles/**` - out of scope unless a CS-382 finding names a concrete style defect.
- `_condamad/reports/cs-382-review-adversariale-generation-theme-natal.md` - source report must remain audit evidence.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1; cd backend; ruff format .`
- VC2: `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .`
- VC3: `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests --tb=short -k "natal_chart or traditional_conditions or theme_astral or llm_astrology_input"`
- VC4: `pnpm --dir frontend lint`
- VC5: `pnpm --dir frontend test -- NatalExpertPanel BirthProfilePage natalChartApi`
- VC6: `pnpm --dir frontend build`
- VC7: run the CS-382 and CS-383 closure scan:
  - `rg -n "Critical|High|Medium|open|corrections requises|traditional_conditions|chart_json|natal_data" _condamad/reports`
- VC8: from repository root after venv activation, run:
  - `python -c "from app.main import app; assert any('/v1/users/me/natal-chart' == getattr(r, 'path', '') for r in app.routes)"`
- VC9: `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -c "from app.main import app; assert '/v1/users/me/natal-chart' in app.openapi()['paths']"`
- VC10: `.\.venv\Scripts\Activate.ps1; python -c "from pathlib import Path; assert Path('_condamad/reports/cs-383-corrections-findings-generation-theme-natal.md').exists()"`
- VC11: from repository root after venv activation, run:
  - `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-383-fermeture-findings-generation-theme-natal/evidence/validation.txt').exists()"`
- VC12: from repository root after venv activation, run:
  - `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-383-fermeture-findings-generation-theme-natal/evidence/re-review.md').exists()"`

## Regression Risks

- A correction could close the visible crash while leaving `POST /v1/users/me/natal-chart` incomplete.
- A low-severity acceptance could hide a future user-visible regression without owner.
- A backend change could make `traditional_conditions` plan-dependent or silently partial.
- A frontend guard could invent values while appearing tolerant to partial payloads.
- Prompt enrichment could regress while public payload tests still pass.
- The CS-382 report was absent at story-writing time; implementation must use the now-present CS-382 evidence before code edits.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the Python venv before every Python, Ruff, or Pytest command.
- Read the CS-382 report before changing code.
- Keep every finding decision traceable to a file, line, test, command, or persisted artifact.
- Do not edit the CS-382 report to reduce the finding list.
- Add or update one focused regression proof for every corrected bug.
- Persist the post-correction re-review result before marking the implementation ready for review.

## References

- `_story_briefs/cs-383-corriger-findings-review-adversariale-generation-theme-natal.md`
- `_condamad/reports/cs-382-review-adversariale-generation-theme-natal.md`
- `_condamad/stories/CS-382-review-adversariale-generation-theme-natal/00-story.md`
- `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/00-story.md`
- `_condamad/stories/CS-380-durcir-natal-expert-panel-contre-payloads-partiels/00-story.md`
- `_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts/00-story.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
