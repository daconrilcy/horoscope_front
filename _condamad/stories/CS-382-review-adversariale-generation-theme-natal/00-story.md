# Story CS-382 review-adversariale-generation-theme-natal: Review Adversariale Generation Theme Natal Apres Corrections
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-382-review-adversariale-generation-theme-natal-apres-corrections.md`.
- Selected mode: Audit-to-story.
- Problem statement: after CS-379, CS-380, and CS-381, the natal generation fix must be attacked before closure.
- Source stakes: creation payload safety, complete `traditional_conditions`, no-time policy, frontend non-invention, and prompt enrichment.
- Closure expectation: produce one adversarial report with severity-ranked findings and a clear closure or correction decision.
- Source-alignment evidence: PASS; objective, ACs, tasks, validation, non-goals, and guardrails preserve every source review axis.

## Objective

Produce an adversarial review report that tries to disprove the apparent closure of CS-379, CS-380, and CS-381.
The story must not correct findings; it must classify proof gaps, false-positive tests, contract drift, and residual risks.

## Target State

- A report exists at `_condamad/reports/cs-382-review-adversariale-generation-theme-natal.md`.
- The report inspects CS-379, CS-380, and CS-381 diffs, tests, evidence, and generated review outputs.
- The report verifies `POST /v1/users/me/natal-chart` for a known birth time before accepting any `GET /latest` proof.
- The report verifies a `no_time` case and confirms that `traditional_conditions` absence is not tied to a commercial plan.
- The report verifies that React guards avoid crashes without computing `hayz`, `rejoicing`, or scores.
- The report verifies that `theme_astral_llm_input_v1` keeps enriched prompt-visible blocks separate from public UI payloads.
- Findings are deduplicated, severity-ranked, source-routed, and actionable.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-382-review-adversariale-generation-theme-natal-apres-corrections.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-382`.
- Evidence 3: `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/00-story.md` - backend repair contract read.
- Evidence 4: `_condamad/stories/CS-380-durcir-natal-expert-panel-contre-payloads-partiels/00-story.md` - frontend hardening contract read.
- Evidence 5: `_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts/00-story.md` - regression proof contract read.
- Evidence 6: `backend` and `frontend` roots exist in this workspace, so the review can inspect both implementation surfaces.
- Evidence 7: `resolve_guardrails.py` selected backend API and frontend local validation guardrails for this mixed review scope.
- Source-alignment evidence: the final story keeps all source acceptance checks and forbids code correction inside the review story.

## Domain Boundary

- Domain: natal-generation-adversarial-review
- In scope:
  - Adversarial review of CS-379, CS-380, and CS-381 implementation diffs, tests, and evidence.
  - Backend public natal chart creation payload, latest reload payload, and `traditional_conditions` policy.
  - Frontend `NatalExpertPanel` rendering guards and nominal natal API type contract.
  - Provider prompt payload boundary for `theme_astral_llm_input_v1` enrichment.
  - Report creation under `_condamad/reports`.
- Out of scope:
  - Code corrections, new features, provider LLM calls, product contract redesign, DB schema changes, auth, i18n, styling, and migrations.
- Explicit non-goals:
  - No backend fix, frontend fix, prompt rewrite, provider invocation, schema migration, or dependency change.
  - No approval based only on absence of a visible crash.
  - No broad acceptance of partial `traditional_conditions` as the nominal product contract.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a cross-stack adversarial review report after multiple fixes.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Create only the report and story evidence artifacts.
  - Do not modify backend runtime, frontend runtime, tests, docs, examples, migrations, or prompt configuration.
  - Route every discovered defect to a future correction story instead of fixing it in this story.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-379, CS-380, or CS-381 implementation artifacts are unavailable for review.
- Additional validation rules:
  - Runtime proof must inspect `POST /v1/users/me/natal-chart` with `pytest` or `TestClient`.
  - Route inventory proof must name `app.routes` and `app.openapi()` for natal endpoints.
  - Frontend proof must include `pnpm` validation or a bounded manual finding when the suite cannot run.
  - Prompt proof must verify `theme_astral_llm_input_v1` enriched blocks and absence of public payload conflation.
  - Every finding must include severity, proof, impact, expected correction, and target story or owner.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `TestClient`, `pytest`, `app.routes`, `app.openapi()`, and `pnpm` prove the reviewed behavior. |
| Baseline Snapshot | yes | Report and command artifacts persist the adversarial review result. |
| Ownership Routing | yes | Findings must route to backend, frontend, prompt, or evidence owners without in-story correction. |
| Allowlist Exception | no | No broad allowlist handling is authorized for proof gaps or partial payload acceptance. |
| Contract Shape | yes | The report has mandatory sections and finding fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | The review must guard against old carriers, UI-synthesized astrology, and POST-only blind spots. |
| Persistent Evidence | yes | Report, command output, guardrail output, and review handoff must be persisted. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The report inspects CS-379 through CS-381. | Evidence profile: baseline_before_after_diff; `python` checks report source sections. |
| AC2 | Creation payload review covers POST. | Evidence profile: runtime_openapi_contract; `pytest` or `TestClient` covers `POST /v1/users/me/natal-chart`. |
| AC3 | Known-time data returns complete traditions. | Evidence profile: json_contract_shape; `pytest -q backend/tests --tb=short -k "traditional_conditions"`. |
| AC4 | No-time data has bounded absence. | Evidence profile: json_contract_shape; `pytest -q backend/tests --tb=short -k "no_time"`. |
| AC5 | Plan tier does not decide absence. | Evidence profile: ast_architecture_guard; `rg` scans plan and `traditional_conditions` coupling. |
| AC6 | React does not compute astrology facts. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans `hayz`, `rejoicing`, and scoring tokens. |
| AC7 | Frontend nominal types stay strict. | Evidence profile: frontend_typecheck_no_orphan; `pnpm --dir frontend build`. |
| AC8 | Prompt-visible enrichment is retained. | Evidence profile: json_contract_shape; `pytest -q backend/tests --tb=short -k "theme_astral or llm_astrology_input"`. |
| AC9 | Provider payload remains separate. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans `chart_json`, `natal_data`, and prompt carriers. |
| AC10 | Findings are actionable. | Evidence profile: json_contract_shape; `python` checks report finding blocks. |
| AC11 | Closure decision is explicit. | Evidence profile: baseline_before_after_diff; `python` checks report decision heading. |
| AC12 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks evidence paths. |
| AC13 | Findings are deduplicated. | Evidence profile: json_contract_shape; `python` checks finding identifiers in the report. |

## Implementation Tasks

- [ ] Task 1: Read CS-379, CS-380, and CS-381 stories, diffs, tests, validation evidence, and generated reviews. (AC: AC1)
- [ ] Task 2: Inspect backend public payload assembly for creation and latest reload paths. (AC: AC2, AC3)
- [ ] Task 3: Verify known-time and `no_time` cases through deterministic backend tests or precise review findings. (AC: AC3, AC4)
- [ ] Task 4: Verify plan tier is not used to hide reliable `traditional_conditions`. (AC: AC5)
- [ ] Task 5: Inspect frontend guards, nominal API types, and tests for non-invention and crash containment. (AC: AC6, AC7)
- [ ] Task 6: Inspect prompt payload construction for retained `theme_astral_llm_input_v1` enrichment. (AC: AC8, AC9)
- [ ] Task 7: Execute required backend, frontend, and scan validation commands, then persist command output. (AC: AC2, AC7, AC12)
- [ ] Task 8: Create the adversarial report with verdict, inspected files, findings, checks, residual risks, and final decision. (AC: AC10, AC11, AC13)
- [ ] Task 9: Verify changed paths are limited to report, story evidence, generated review handoff, and tracker artifacts. (AC: AC12)

## Files to Inspect First

- `_story_briefs/cs-379-stabiliser-contrat-public-generation-theme-natal-apres-enrichissement-prompts.md`
- `_story_briefs/cs-380-durcir-natal-expert-panel-contre-payloads-partiels-sans-masquer-contrat.md`
- `_story_briefs/cs-381-non-regression-generation-theme-natal-et-enrichissement-prompts.md`
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
  - `pytest` or `TestClient` assertions for `GET /v1/users/me/natal-chart/latest`.
  - `app.routes` and `app.openapi()` from the loaded FastAPI app for natal endpoint inventory.
  - Vitest, Playwright, or Testing Library proof for `NatalExpertPanel` rendering behavior.
  - Backend pytest assertions over `theme_astral_llm_input_v1` provider payload enrichment.
- Secondary evidence:
  - Targeted `rg` scans for plan coupling, astrology derivation in React, public/provider carrier conflation, and reviewed report sections.
- Static scans alone are not sufficient for this story because:
  - The source brief requires hostile runtime review of creation payload behavior after the correction wave.

## Contract Shape

- Contract type:
  - Adversarial review report for corrected natal generation and enriched prompt regression.
- Fields:
  - `Synthese du verdict`: global verdict and closure decision.
  - `Fichiers et tests inspectes`: exact implementation, test, and evidence surfaces.
  - `Findings`: severity-ranked `Critical`, `High`, `Medium`, `Low` findings.
  - `Checks executes`: command, status, and persisted output path.
  - `Risques residuels`: residual risks with owner or decision.
  - `Decision finale`: corrections required or closure acceptable.
- Required fields:
  - `Synthese du verdict`, `Fichiers et tests inspectes`, `Findings`, `Checks executes`, `Risques residuels`, `Decision finale`.
- Optional fields:
  - none.
- Status codes:
  - none; no API route behavior is created by this story.
- Serialization names:
  - Report headings must stay stable enough for `python` validation checks.
- Frontend type impact:
  - none; frontend files are inspected, not changed.
- Generated contract impact:
  - none; `app.openapi()` is runtime evidence only.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-382-review-adversariale-generation-theme-natal/evidence/review-baseline-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-382-review-adversariale-generation-theme-natal/evidence/review-baseline-after.txt`
- Expected invariant:
  - The only intended repository delta is the adversarial report, story evidence artifacts, generated review handoff, and tracker update.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Adversarial report | `_condamad/reports/cs-382-review-adversariale-generation-theme-natal.md` | Backend runtime package |
| Story evidence | `_condamad/stories/CS-382-review-adversariale-generation-theme-natal/evidence/**` | Backend tests |
| Backend public payload finding | `backend/app/services/chart/json_builder.py` or exact finding owner | Report patch |
| Traditional calculation finding | `backend/app/domain/astrology/advanced_conditions/**` | Frontend guard |
| Frontend guard finding | `frontend/src/features/natal-chart/NatalExpertPanel.tsx` | Backend projection |
| Prompt enrichment finding | `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` | Public UI payload |

## Mandatory Reuse / DRY Constraints

- Reuse CS-379, CS-380, and CS-381 source briefs, stories, tests, and evidence as the review ledger.
- Reuse existing backend and frontend validation commands from the source brief before adding narrower scans.
- Do not duplicate JSON payload samples in the story; keep detailed payload proof in report evidence artifacts.
- Do not create a second report location or parallel finding register.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy carrier may be accepted as active proof for canonical `theme_astral_llm_input_v1` enrichment.
- No compatibility route, UI adapter, or prompt carrier may be accepted as closure proof.
- No fallback React calculation may be accepted for missing `hayz`, `rejoicing`, dignities, or scores.
- Forbidden shortcut: proving only `GET /latest` while skipping `POST /v1/users/me/natal-chart`.
- Do not preserve legacy behavior.

## Reintroduction Guard

- Guard target: prevent closure based on masked crashes, partial public contract acceptance, or prompt enrichment loss.
- Forbidden surfaces:
  - Report approval without direct POST payload review.
  - Plan-tier logic controlling reliable `traditional_conditions` absence.
  - React-derived `hayz`, `rejoicing`, or score values.
  - Prompt construction driven by public UI payload carriers instead of canonical provider payload input.
- Required guard evidence:
  - `python -B -m pytest -q tests --tb=short -k "natal_chart or traditional_conditions or theme_astral or llm_astrology_input"`
  - `pnpm --dir frontend test -- NatalExpertPanel BirthProfilePage natalChartApi`
  - `rg -n "is_hayz|is_rejoicing|traditional_conditions|chart_json|natal_data|llm_astrology_input_v1|theme_astral_llm_input_v1" backend/app backend/tests frontend/src`

## Regression Guardrails

| Guardrail | Applied invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Review must not move API business logic into router surfaces. | `pytest`; diff review. |
| RG-003 `converge-api-v1-route-architecture` | Natal endpoints remain proven from the canonical loaded app. | `app.routes`; `app.openapi()`. |
| RG-047 `CS-029-encadrer-styles-inline-statiques-frontend` | Frontend review must flag inline style drift in touched TSX. | `rg`; `pnpm lint`. |
| RG-052 `CS-075-converger-namespaces-css-migration-only-restants` | Frontend CSS changes remain out of scope for this report. | Changed-path check. |
| Registry gap | No exact guardrail covers post-correction natal generation adversarial review. | Resolver output persisted. |

Non-applicable examples:

- RG-027 prediction infra is out of scope because the review targets natal generation and prompt payloads.
- RG-007 admin LLM observability is out of scope because the review targets natal endpoints and provider prompt payloads.
- RG-041 entitlement documentation is out of scope because plan behavior is checked in runtime contracts, not docs.
- RG-042 docs LLM source-of-truth is out of scope because prompt docs are not modified by this review.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Adversarial report | `_condamad/reports/cs-382-review-adversariale-generation-theme-natal.md` | Keep final review. |
| Baseline before | `_condamad/stories/CS-382-review-adversariale-generation-theme-natal/evidence/review-baseline-before.txt` | Before proof. |
| Baseline after | `_condamad/stories/CS-382-review-adversariale-generation-theme-natal/evidence/review-baseline-after.txt` | After proof. |
| Guardrail output | `_condamad/stories/CS-382-review-adversariale-generation-theme-natal/evidence/guardrails.txt` | Guardrail resolver result. |
| Validation output | `_condamad/stories/CS-382-review-adversariale-generation-theme-natal/evidence/validation.txt` | Command results. |
| Review output | `_condamad/stories/CS-382-review-adversariale-generation-theme-natal/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no broad allowlist handling is authorized for review gaps, masked crashes, or prompt-carrier drift.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/reports/cs-382-review-adversariale-generation-theme-natal.md` - final adversarial review report.
- `_condamad/stories/CS-382-review-adversariale-generation-theme-natal/evidence/**` - persisted review evidence.
- `_condamad/stories/CS-382-review-adversariale-generation-theme-natal/generated/11-code-review.md` - review handoff.

Likely tests:

- `backend/tests/**` selected by `natal_chart`, `traditional_conditions`, `theme_astral`, and `llm_astrology_input`.
- `frontend/src/tests/NatalExpertPanel.test.tsx`
- `frontend/src/tests/BirthProfilePage.test.tsx`
- `frontend/src/api/natal-chart/index.ts` type/build witness.

Files not expected to change:

- `backend/app/**` - out of scope; this review reports backend findings without fixing them.
- `backend/tests/**` - out of scope; this review inspects and runs tests without changing them.
- `frontend/src/**` - out of scope; this review reports frontend findings without fixing them.
- `backend/alembic/**` - out of scope; no migration is authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1; ruff check backend`
- VC2: `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend/tests --tb=short -k "natal_chart or traditional_conditions or theme_astral or llm_astrology_input"`
- VC3: `pnpm --dir frontend lint`
- VC4: `pnpm --dir frontend test -- NatalExpertPanel BirthProfilePage natalChartApi`
- VC5: `pnpm --dir frontend build`
- VC6: `rg -n "is_hayz|is_rejoicing|traditional_conditions|chart_json|natal_data|llm_astrology_input_v1|theme_astral_llm_input_v1" backend/app backend/tests frontend/src`
- VC7: `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -c "from app.main import app; assert any('natal-chart' in getattr(r, 'path', '') for r in app.routes)"`
- VC8: `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -c "from app.main import app; assert '/v1/users/me/natal-chart' in app.openapi()['paths']"`
- VC9: `.\.venv\Scripts\Activate.ps1; python -c "from pathlib import Path; assert Path('_condamad/reports/cs-382-review-adversariale-generation-theme-natal.md').exists()"`
- VC10: from repository root after venv activation, run:
  - `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-382-review-adversariale-generation-theme-natal/evidence/validation.txt').exists()"`
- VC11: from repository root after venv activation, run:
  - `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-382-review-adversariale-generation-theme-natal/evidence/guardrails.txt').exists()"`
- VC12: from repository root after venv activation, run:
  - `python -c "import subprocess as s; x=s.check_output(['git','status','--short'], text=True); assert 'backend/app/' not in x"`

## Regression Risks

- The report could approve the wave by observing only no-crash behavior while the POST payload remains invalid.
- Tests could pass against permissive fixtures that would not fail on the original partial `traditional_conditions` bug.
- A `no_time` case could be conflated with commercial plan behavior.
- Frontend guards could hide invalid backend data by inventing astrology facts.
- Prompt enrichment could regress while public UI payload tests still pass.
- Static scan hits for old carrier names could be audit-only; the report must classify each hit by runtime role.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the Python venv before every Python, Ruff, or Pytest command.
- Produce the report before marking the story implemented.
- Keep all findings tied to file, line, command, or persisted artifact proof.
- Do not modify backend, frontend, migrations, docs, examples, or tests while executing this review.
- Classify empty findings explicitly with closure proof instead of leaving the findings section blank.

## References

- `_story_briefs/cs-382-review-adversariale-generation-theme-natal-apres-corrections.md`
- `_story_briefs/cs-379-stabiliser-contrat-public-generation-theme-natal-apres-enrichissement-prompts.md`
- `_story_briefs/cs-380-durcir-natal-expert-panel-contre-payloads-partiels-sans-masquer-contrat.md`
- `_story_briefs/cs-381-non-regression-generation-theme-natal-et-enrichissement-prompts.md`
- `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/00-story.md`
- `_condamad/stories/CS-380-durcir-natal-expert-panel-contre-payloads-partiels/00-story.md`
- `_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts/00-story.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
