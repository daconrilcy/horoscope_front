# Story CS-377 audit-review-adversariale-complete-theme-astral-prompt-contract-final: Audit Review Adversariale Complete Theme Astral Prompt Contract Final
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-377-audit-review-adversariale-complete-theme-astral-prompt-contract-final.md`.
- Selected mode: Audit-to-story.
- Source problem: after CS-372 through CS-376, the `theme_astral` prompt contract needs a final adversarial audit.
- Source stakes: delivery profile alignment, structured birth context, sourced examples, backend-only plan handling, old carrier closure, and doc coherence.
- Closure expectation: produce one severity-ranked audit report with file or line proof and a closure decision.
- Source-alignment review: PASS; objective, ACs, tasks, validation, non-goals, and guardrails map to the brief stakes.

## Objective

Produce a final adversarial audit report that tries to break the completed `theme_astral` prompt contract before closure.
The story must not correct findings; it must classify them with proof, interpretation, and a clear closure decision.

## Target State

- A final audit report exists under `_condamad/audits/theme-astral-prompt-contract/YYYY-MM-DD-HHMM/`.
- The report includes verdict, severity-ranked findings, file or line proof, CS-372 to CS-376 compliance, scans, commands, risks, and decision.
- The audit verifies `essential`, `expanded`, and `complete` across code, DB, tests, docs, and examples.
- The audit verifies that `birth_context` is structured and not derived only from `chart_id`.
- The audit verifies that examples use representative sourced interpretive material or raise a finding.
- The audit verifies that commercial plan handling remains backend-only.
- The audit verifies that old carriers cannot feed the canonical `theme_astral` prompt path.
- The audit records whether CS-376 provider smoke was executed, skipped by missing opt-in, or not implemented.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-377-audit-review-adversariale-complete-theme-astral-prompt-contract-final.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-377`.
- Evidence 3: `_story_briefs/cs-372-*.md` through `_story_briefs/cs-376-*.md` - same-wave source briefs read.
- Evidence 4: `_condamad/stories/CS-369-audit-review-adversariale-correction-theme-astral-prompt-contract/00-story.md` - sibling audit shape read.
- Evidence 5: `_condamad/stories/CS-376-validation-provider-smoke-theme-astral/00-story.md` - provider smoke contract read.
- Evidence 6: `_condamad/stories/regression-guardrails.md` - scoped guardrails resolved with the local resolver.
- Source-alignment evidence: the final story keeps every source audit axis and forbids code correction inside this story.

## Domain Boundary

- Domain: backend-llm-audit
- In scope:
  - Final adversarial audit of CS-372, CS-373, CS-374, CS-375, and CS-376 deliverables.
  - Backend `theme_astral` prompt contract code, persistence, tests, examples, docs, provider payload, and evidence reports.
  - Report creation under `_condamad/audits/theme-astral-prompt-contract/`.
- Out of scope:
  - Frontend UI, auth, i18n, styling, unrelated LLM features, provider calls without explicit opt-in, and architecture redesign.
  - Correcting findings found by the audit.
- Explicit non-goals:
  - No code, DB, docs, or example correction in this story.
  - No provider invocation unless CS-376 opt-in prerequisites are explicitly available.
  - No broad prompt-generation refactor or new contract design.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a final adversarial backend LLM audit report.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Create only the audit report and story evidence artifacts.
  - Do not modify backend runtime, docs, examples, migrations, tests, or frontend files as part of this audit.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the audit cannot access required CS-372 to CS-376 implementation artifacts.
- Additional validation rules:
  - Runtime proof must name `pytest`, loaded payload or config checks, DB persistence evidence, and targeted `rg` scans.
  - Every finding must be classified as bug, accepted risk, false positive, or out of scope.
  - Negative `rg` scans must be interpreted as expected success or as missing proof, not pasted without decision.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, payload builder tests, DB tests, loaded config, and targeted scans prove the audited runtime. |
| Baseline Snapshot | yes | Audit command output and scan matrices persist the final closure evidence. |
| Ownership Routing | yes | Audit output belongs under `_condamad/audits`, while findings route future fixes to canonical owners. |
| Allowlist Exception | no | No broad allowlist handling is authorized for old carriers, plan labels, or audit omissions. |
| Contract Shape | yes | The audit report has mandatory sections and finding classifications. |
| Batch Migration | no | No batch migration or conversion is in scope. |
| Reintroduction Guard | yes | Old carriers and plan leakage must remain audited with deterministic scans. |
| Persistent Evidence | yes | Audit report, scan output, validation output, and review handoff must be persisted. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The audit covers every source axis. | Evidence profile: json_contract_shape; `python` checks report headings. |
| AC2 | Findings are severity-ranked. | Evidence profile: baseline_before_after_diff; `python` parses report finding sections. |
| AC3 | CS-372 to CS-376 each have a compliance verdict. | Evidence profile: baseline_before_after_diff; `python` checks report matrix rows. |
| AC4 | Delivery profiles are audited. | Evidence profile: json_contract_shape; `pytest` runs provider payload builder tests. |
| AC5 | Birth context structure is audited. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`. |
| AC6 | Example source quality is classified. | Evidence profile: baseline_before_after_diff; `rg` scans example source tokens. |
| AC7 | Backend-only plan handling is audited. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans plan tokens in payload surfaces. |
| AC8 | Old carriers are interpreted by domain. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans `chart_json`, `natal_data`, and `llm_astrology_input_v1`. |
| AC9 | CS-376 provider smoke status is explicit. | Evidence profile: json_contract_shape; `python` checks report provider-smoke row. |
| AC10 | No code correction is part of this story. | Evidence profile: ast_architecture_guard; `python` checks changed paths from git status. |
| AC11 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks report and evidence paths. |

## Implementation Tasks

- [ ] Task 1: Read CS-372 through CS-376 briefs, stories, implementation evidence, and available generated review outputs. (AC: AC1, AC3)
- [ ] Task 2: Inspect `theme_astral` code, DB persistence, examples, docs, tests, and reports required by the source brief. (AC: AC1)
- [ ] Task 3: Execute deterministic validation commands and persist raw command output under the story evidence directory. (AC: AC4, AC5, AC11)
- [ ] Task 4: Run positive and negative scans for delivery profiles, birth context, old carriers, and commercial plan tokens. (AC: AC6, AC7, AC8)
- [ ] Task 5: Interpret every scan result as expected success, bug, accepted risk, false positive, or out of scope. (AC: AC2, AC6, AC7, AC8)
- [ ] Task 6: Create the final adversarial audit report with mandatory sections and file or line proof for each finding. (AC: AC1, AC2, AC3)
- [ ] Task 7: Record whether CS-376 provider smoke ran, skipped by missing opt-in, or was not implemented. (AC: AC9)
- [ ] Task 8: Verify that the story changed only audit, story, and evidence artifacts. (AC: AC10, AC11)

## Files to Inspect First

- `_story_briefs/cs-372-aligner-delivery-profiles-db-provider-theme-astral.md`
- `_story_briefs/cs-373-structurer-birth-context-theme-astral-llm-input-v1.md`
- `_story_briefs/cs-374-renforcer-exemples-json-theme-astral-avec-textes-interpretation-reels.md`
- `_story_briefs/cs-375-mettre-a-jour-docs-structure-json-theme-astral-apres-corrections.md`
- `_story_briefs/cs-376-ajouter-validation-provider-smoke-theme-astral-sans-production.md`
- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/**`
- `_condamad/reports/**`
- `backend/app/domain/llm/**`
- `backend/app/domain/astrology/interpretation/**`
- `backend/app/infra/db/repositories/interpretation_material_source_repository.py`
- `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py`
- `backend/pyproject.toml`
- `backend/tests/**`

## Runtime Source of Truth

- Primary source of truth:
  - `pytest`, loaded payload builder outputs, loaded config, DB persistence tests, and generated audit report content.
- Secondary evidence:
  - Targeted `rg` scans for profile names, birth context fields, old carriers, plan tokens, docs contradictions, and provider smoke gating.
- Static scans alone are not sufficient for this story because:
  - The audit must interpret runtime test outcomes and scan results together before issuing a closure decision.

## Contract Shape

- Contract type:
  - Final adversarial audit report for the `theme_astral` prompt contract.
- Fields:
  - `Verdict global`: closure verdict for the audited contract.
  - `Findings par severite`: severity-ranked findings with source proof.
  - `Matrice de conformite CS-372 a CS-376`: one row per upstream story.
  - `Matrice des scans`: positive and negative scans with interpretation.
  - `Commandes executees`: commands, status, and evidence artifact path.
  - `Risques residuels`: residual risks with decision.
  - `Decision`: ready for closure or corrections required.
- Required fields:
  - `Verdict global`, `Findings par severite`, `Matrice de conformite CS-372 a CS-376`, `Matrice des scans`, `Commandes executees`, `Risques residuels`, `Decision`.
- Optional fields:
  - none.
- Status codes:
  - none; no API route behavior is created by this story.
- Serialization names:
  - Report headings must stay stable enough for `python` validation checks.
- Frontend type impact:
  - none.
- Generated contract impact:
  - none.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-377-audit-review-adversariale-complete-theme-astral-prompt-contract-final/evidence/audit-baseline-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-377-audit-review-adversariale-complete-theme-astral-prompt-contract-final/evidence/audit-baseline-after.txt`
- Expected invariant:
  - The only intended repository delta is the final audit report, story evidence artifacts, and CONDAMAD tracker update.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Final adversarial report | `_condamad/audits/theme-astral-prompt-contract/**` | Backend runtime package |
| Story evidence | `_condamad/stories/CS-377-audit-review-adversariale-complete-theme-astral-prompt-contract-final/evidence/**` | Backend tests |
| Future backend findings | `backend/app/domain/llm/**` or canonical owner named by finding | Audit report patch |
| Future documentation findings | `_condamad/docs/prompt-generation-cartography/**` | Backend runtime package |
| Future example findings | `_condamad/examples/prompt-generation-cartography/**` | Provider smoke test |

## Mandatory Reuse / DRY Constraints

- Reuse CS-372 to CS-376 stories and evidence as the source ledger instead of rewriting their contracts.
- Reuse existing backend tests and scans from the source brief before adding manual interpretation.
- Reuse existing report folders under `_condamad/audits/theme-astral-prompt-contract/`.
- Do not duplicate payload schema, persistence schema, or example JSON inside the audit story.
- Keep one final audit report and one persisted validation evidence set.

## No Legacy / Forbidden Paths

- No legacy prompt carrier may be accepted as active evidence for canonical `theme_astral` prompt construction.
- No compatibility prompt path may be accepted as a closure route.
- No fallback prompt path may be accepted as equivalent to the canonical builder.
- `chart_json`, `natal_data`, and `llm_astrology_input_v1` must not feed canonical `theme_astral`.
- Commercial labels `free`, `basic`, and `premium` must not be emitted as LLM-visible plan labels.
- Do not preserve legacy behavior.

## Reintroduction Guard

- Guard target: final closure of `theme_astral` prompt contract without silent old-carrier or plan-label drift.
- Forbidden surfaces:
  - Active `theme_astral` construction from `chart_json`, `natal_data`, or `llm_astrology_input_v1`.
  - LLM-visible commercial plan values in provider payloads.
  - Report sections that list scan hits without interpretation.
- Required guard evidence:
  - `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
  - `pytest -q backend/tests/integration/test_theme_astral_prompt_contract_persistence.py`
  - `pytest -q backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`
  - `pytest -q backend/tests/architecture/test_theme_astral_prompt_contract_guard.py`
  - `rg -n "chart_json|natal_data|llm_astrology_input_v1|legacy|free|basic|premium|\"plan\"" backend/app backend/tests _condamad/examples`

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend audit must not move business logic into router surfaces. | Targeted `rg`; backend `pytest`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Prompt-generation validation paths must point to collected tests. | Targeted `pytest`; report matrix. |
| Registry gap `theme_astral-final-adversarial-audit` | No exact invariant covers this final audit closure scope. | Resolver output persisted. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no frontend file is touched.
- RG-052 frontend CSS namespaces are out of scope because no styling surface is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Final audit report | `_condamad/audits/theme-astral-prompt-contract/YYYY-MM-DD-HHMM/05-audit-review-adversariale-finale-theme-astral-prompt-contract.md` | Keep final audit. |
| Baseline before | `_condamad/stories/CS-377-audit-review-adversariale-complete-theme-astral-prompt-contract-final/evidence/audit-baseline-before.txt` | Before proof. |
| Baseline after | `_condamad/stories/CS-377-audit-review-adversariale-complete-theme-astral-prompt-contract-final/evidence/audit-baseline-after.txt` | After proof. |
| Guardrail output | `_condamad/stories/CS-377-audit-review-adversariale-complete-theme-astral-prompt-contract-final/evidence/guardrails.txt` | Guardrails. |
| Validation output | `_condamad/stories/CS-377-audit-review-adversariale-complete-theme-astral-prompt-contract-final/evidence/validation.txt` | Validation. |
| Review output | `generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no broad allowlist handling is authorized for old carriers, plan labels, scan omissions, or audit findings.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/theme-astral-prompt-contract/YYYY-MM-DD-HHMM/05-audit-review-adversariale-finale-theme-astral-prompt-contract.md` - final audit report.
- `_condamad/stories/CS-377-audit-review-adversariale-complete-theme-astral-prompt-contract-final/evidence/**` - validation evidence.
- `_condamad/stories/CS-377-audit-review-adversariale-complete-theme-astral-prompt-contract-final/generated/11-code-review.md` - review handoff.

Likely tests:

- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py`
- `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`
- `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py`

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/**` - out of scope; this audit does not correct code findings.
- `backend/tests/**` - out of scope; this audit runs tests but does not change them.
- `_condamad/docs/**` - out of scope; documentation findings are reported, not corrected.
- `_condamad/examples/**` - out of scope; example findings are reported, not corrected.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: from `backend`, run `ruff check .` after `.\.venv\Scripts\Activate.ps1`.
- VC2: from `backend`, run:
  - `python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py --tb=short`
- VC3: from `backend`, run:
  - `python -B -m pytest -q tests/integration/test_theme_astral_prompt_contract_persistence.py --tb=short`
- VC4: from `backend`, run:
  - `python -B -m pytest -q tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py --tb=short`
- VC5: from `backend`, run:
  - `python -B -m pytest -q tests/architecture/test_theme_astral_prompt_contract_guard.py --tb=short`
- VC6: from `backend`, run:
  - `rg -n "deep|essential|expanded|complete|delivery_profile|birth_context|birth_date|birth_time_local|birth_place" app tests ..\_condamad\docs ..\_condamad\examples`
- VC7: from `backend`, run:
  - `rg -n "chart_json|natal_data|llm_astrology_input_v1|legacy|free|basic|premium|\"plan\"" app tests ..\_condamad\examples`
- VC8: from `_condamad/audits/theme-astral-prompt-contract`, run:
  - `python -c "from pathlib import Path; assert any(Path('.').rglob('05-audit-review*.md'))"`
- VC9: from the story directory, run:
  - `python -c "from pathlib import Path; assert Path('evidence/validation.txt').exists()"`
- VC10: from the story directory, run:
  - `python -c "from pathlib import Path; assert Path('evidence/guardrails.txt').exists()"`
- VC11: after `.\.venv\Scripts\Activate.ps1`, run:
  - `python -c "import subprocess as s; x=s.check_output(['git','status','--short'],text=True); assert 'backend' not in x"`

## Regression Risks

- The audit could become a passive confirmation instead of actively searching for contract drift.
- Negative scans could be misread as missing evidence rather than expected success.
- Commercial plan labels could remain legitimate in filenames or mapping tests while leaking into provider payload values.
- CS-376 provider smoke status could be omitted, hiding the remaining provider acceptance risk.
- A report-only story could accidentally correct code and blur the boundary for CS-378.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the Python venv before every Python, Ruff, or Pytest command.
- From repository root, run `.\.venv\Scripts\Activate.ps1`, then `cd backend` before backend validation commands.
- Persist command output under the story evidence directory.
- Keep all findings tied to file or line proof.
- Do not modify backend, frontend, docs, examples, migrations, or tests while executing this audit.

## References

- `_story_briefs/cs-377-audit-review-adversariale-complete-theme-astral-prompt-contract-final.md`
- `_story_briefs/cs-372-aligner-delivery-profiles-db-provider-theme-astral.md`
- `_story_briefs/cs-373-structurer-birth-context-theme-astral-llm-input-v1.md`
- `_story_briefs/cs-374-renforcer-exemples-json-theme-astral-avec-textes-interpretation-reels.md`
- `_story_briefs/cs-375-mettre-a-jour-docs-structure-json-theme-astral-apres-corrections.md`
- `_story_briefs/cs-376-ajouter-validation-provider-smoke-theme-astral-sans-production.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md#RG-002`
- `_condamad/stories/regression-guardrails.md#RG-022`
