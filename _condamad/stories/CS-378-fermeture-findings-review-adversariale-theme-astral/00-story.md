# Story CS-378 fermeture-findings-review-adversariale-theme-astral: Close Theme Astral Final Adversarial Review Findings
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-378-corriger-findings-review-adversariale-finale-theme-astral.md`.
- Selected mode: Audit-to-story.
- Source problem: CS-377 must not leave actionable final adversarial review findings open for `theme_astral`.
- Source stakes: closure of Critical, High, and Medium findings; tested corrections; aligned docs and examples; closure report proof.
- Closure expectation: every CS-377 finding receives a decision, a correction or accepted residual risk, validation evidence, and re-review proof.
- Source-alignment evidence: PASS; objective, ACs, tasks, validation, non-goals, and guardrails preserve every source closure demand.

## Objective

Close actionable findings from the CS-377 final adversarial review for the `theme_astral` prompt contract.
The implementation must correct scoped code, tests, docs, examples, and evidence until the closure report proves no actionable major finding remains open.

## Target State

- `_condamad/reports/cs-378-corrections-review-adversariale-finale-theme-astral.md` exists as the correction closure report.
- Every CS-377 finding is classified as corrected, accepted residual risk, false positive, or out of scope.
- Critical, High, and Medium actionable findings from CS-377 are corrected with tests or bounded validation proof.
- Minor findings are corrected or accepted with owner, justification, and residual risk.
- Tests, docs, examples, and generated payload examples match the final `theme_astral` contract.
- A targeted post-correction re-review proves that corrected findings are no longer open.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-378-corriger-findings-review-adversariale-finale-theme-astral.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-378`.
- Evidence 3: `_condamad/stories/CS-377-audit-review-adversariale-complete-theme-astral-prompt-contract-final/00-story.md` - upstream audit contract read.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - scoped guardrails resolved with the local resolver.
- Evidence 5: `backend` exists in this workspace; expected backend validation paths can be targeted during implementation.
- Assumption: the CS-377 final audit report is produced before CS-378 execution or during the first implementation task.

## Domain Boundary

- Domain: backend-llm-correction
- In scope:
  - Findings from the CS-377 final adversarial review of the `theme_astral` prompt contract.
  - Backend `theme_astral` prompt code, tests, docs, examples, reports, and generated evidence touched by CS-372 through CS-376.
  - Regeneration of example provider payloads only when the corrected contract or source data changes.
  - Targeted post-correction re-review on the corrected finding surfaces.
- Out of scope:
  - Frontend UI, auth, i18n, styling, unrelated LLM domains, provider calls without explicit opt-in, and architecture redesign.
  - New product features or new prompt contract versions beyond the corrected `theme_astral` closure scope.
- Explicit non-goals:
  - No new feature behavior beyond closing CS-377 findings.
  - No full architecture rewrite unless a CS-377 blocker proves it is the only closure path.
  - No provider LLM invocation without explicit opt-in.
  - No report-only closure that hides an actionable finding.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a backend LLM finding-correction and closure-report contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Change only surfaces required to close CS-377 findings for `theme_astral`.
  - Preserve the canonical `theme_astral` prompt contract unless CS-377 identifies a contract defect.
  - Keep docs and examples aligned with corrected runtime behavior.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: a CS-377 finding requires a product decision, external provider opt-in, or architecture choice not present in the brief.
- Additional validation rules:
  - Runtime proof must name full `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` commands.
  - Static proof must use targeted `rg` scans for old carriers, placeholder docs, example JSON validity, and report closure language.
  - Closure proof must include a targeted re-review artifact or command output proving corrected findings are no longer open.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, loaded payload checks, JSON parsing, and targeted scans prove corrected runtime and artifacts. |
| Baseline Snapshot | yes | CS-377 findings and before/after closure evidence prove the only allowed surface delta. |
| Ownership Routing | yes | Findings must route to canonical backend, docs, examples, tests, or report owners. |
| Allowlist Exception | no | No broad allowlist handling is authorized for unresolved findings or old carriers. |
| Contract Shape | yes | The closure report has mandatory finding decisions, commands, results, and residual risks. |
| Batch Migration | no | No broad migration or multi-domain conversion is in scope. |
| Reintroduction Guard | yes | Corrected findings must not return through old carriers, stale docs, or stale examples. |
| Persistent Evidence | yes | Closure report, validation output, re-review output, and changed-path proof must persist. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Every CS-377 finding has one decision. | Evidence profile: baseline_before_after_diff; `python` parses the CS-378 report finding table. |
| AC2 | No actionable Critical finding remains open. | Evidence profile: json_contract_shape; `rg` checks closure report severity rows. |
| AC3 | No actionable High finding remains open. | Evidence profile: json_contract_shape; `rg` checks closure report severity rows. |
| AC4 | No actionable Medium finding remains open. | Evidence profile: json_contract_shape; `rg` checks closure report severity rows. |
| AC5 | Accepted findings name an owner. | Evidence profile: json_contract_shape; `python` checks accepted-risk rows in the report. |
| AC6 | Corrected findings have regression tests. | Evidence profile: baseline_before_after_diff; `pytest` covers the provider payload builder test. |
| AC7 | Prompt persistence remains valid. | Evidence profile: json_contract_shape; `pytest` covers `tests/integration/test_theme_astral_prompt_contract_persistence.py`. |
| AC8 | Bigbang prompt behavior remains valid. | Evidence profile: json_contract_shape; `pytest` covers `tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`. |
| AC9 | Architecture guard behavior remains valid. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/architecture/test_theme_astral_prompt_contract_guard.py`. |
| AC10 | Example JSON payloads parse successfully. | Evidence profile: json_contract_shape; `python` JSON-loads the three provider payload files. |
| AC11 | Docs contain no stale placeholders. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans `_condamad/docs`. |
| AC12 | Post-correction re-review proves closure. | Evidence profile: baseline_before_after_diff; `rg` checks the re-review and CS-378 report. |
| AC13 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks evidence and generated review paths. |
| AC14 | Accepted findings state justification. | Evidence profile: json_contract_shape; `python` checks accepted-risk rows in the report. |
| AC15 | Examples contain no stale placeholders. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans `_condamad/examples`. |

## Implementation Tasks

- [ ] Task 1: Read the CS-377 final audit report and create a finding ledger in the CS-378 closure report. (AC: AC1)
- [ ] Task 2: Classify each finding as corrected, accepted residual risk, false positive, or out of scope. (AC: AC1, AC5, AC14)
- [ ] Task 3: Correct every actionable Critical, High, and Medium finding in canonical owner files. (AC: AC2, AC3, AC4)
- [ ] Task 4: Correct Minor findings or record accepted residual risk with owner and justification. (AC: AC5, AC14)
- [ ] Task 5: Add or update regression tests for each corrected backend behavior. (AC: AC6, AC7, AC8, AC9)
- [ ] Task 6: Update docs and example payloads only for corrected contract or source-data deltas. (AC: AC10, AC11, AC15)
- [ ] Task 7: Regenerate provider payload examples when contract fields or source examples changed. (AC: AC10, AC15)
- [ ] Task 8: Run Ruff, targeted pytest, JSON validation, and stale-placeholder scans. (AC: AC6, AC7, AC8, AC9, AC10, AC11, AC15)
- [ ] Task 9: Run a targeted post-correction re-review on the changed files and corrected findings. (AC: AC12)
- [ ] Task 10: Finalize the CS-378 closure report with commands, results, changed-path proof, and residual risks. (AC: AC1, AC12, AC13)

## Files to Inspect First

- CS-377 final audit report under `_condamad/audits/theme-astral-prompt-contract/**`.
- `_condamad/stories/CS-377-audit-review-adversariale-complete-theme-astral-prompt-contract-final/00-story.md`
- `_condamad/stories/CS-372-aligner-profils-livraison-theme-astral-db-provider/00-story.md`
- `_condamad/stories/CS-373-structurer-birth-context-theme-astral-llm-input/00-story.md`
- `_condamad/stories/CS-374-renforcer-exemples-json-theme-astral-textes-interpretation/00-story.md`
- `_condamad/stories/CS-375-mettre-a-jour-docs-structure-json-theme-astral/00-story.md`
- `_condamad/stories/CS-376-validation-provider-smoke-theme-astral/00-story.md`
- `backend/app/domain/llm/**`
- `backend/app/domain/astrology/interpretation/**`
- `backend/app/infra/db/repositories/interpretation_material_source_repository.py`
- `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py`
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py`
- `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`
- `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py`
- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/**`

## Runtime Source of Truth

- Primary source of truth:
  - `pytest`, loaded config, DB schema, loaded provider payload outputs, JSON parsing, and the CS-378 closure report.
- Secondary evidence:
  - Targeted `rg` scans for old carriers, commercial plan labels, stale placeholders, unresolved review wording, and changed paths.
- Static scans alone are not sufficient for this story because:
  - Corrected backend behavior must be proven by collected tests and report evidence, not only by absence of text hits.

## Contract Shape

- Contract type:
  - Correction closure report for the final `theme_astral` adversarial review.
- Fields:
  - `Liste des findings CS-377`: one row per upstream finding.
  - `Decision`: corrected, accepted residual risk, false positive, or out of scope.
  - `Correction appliquee`: concise description and touched owner files.
  - `Tests ajoutes ou modifies`: deterministic validation evidence per corrected finding.
  - `Commandes executees`: command, status, and output artifact path.
  - `Resultat final`: closure verdict for Critical, High, Medium, and Minor findings.
  - `Risques residuels acceptes`: owner, justification, and residual risk.
- Required fields:
  - `Liste des findings CS-377`, `Decision`, `Correction appliquee`, `Tests ajoutes ou modifies`, `Commandes executees`, `Resultat final`.
- Optional fields:
  - `Risques residuels acceptes` only when an accepted residual risk exists; otherwise the section states `none`.
- Status codes:
  - none; no API route behavior is created by this story.
- Serialization names:
  - Report headings must stay stable enough for `python` validation checks.
- Frontend type impact:
  - none.
- Generated contract impact:
  - Example payload JSON files must remain parseable with `python` JSON loading.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-378-fermeture-findings-review-adversariale-theme-astral/evidence/cs-377-findings-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-378-fermeture-findings-review-adversariale-theme-astral/evidence/cs-378-closure-after.md`
- Expected invariant:
  - The only intended repository delta is scoped correction of CS-377 findings, matching tests/docs/examples, and closure evidence.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Finding ledger and closure report | `_condamad/reports/cs-378-corrections-review-adversariale-finale-theme-astral.md` | CS-377 audit report |
| Provider payload behavior | `backend/app/domain/llm/**` | `_condamad/docs/**` |
| Persistence behavior | `backend/app/infra/**` or canonical repository owner | Prompt examples |
| Regression tests | `backend/tests/**` | Runtime source files only |
| Prompt contract documentation | `_condamad/docs/prompt-generation-cartography/**` | Backend tests |
| Provider payload examples | `_condamad/examples/prompt-generation-cartography/**` | Backend runtime package |

## Mandatory Reuse / DRY Constraints

- Reuse the CS-377 finding ledger as the source of work instead of creating a parallel finding taxonomy.
- Reuse canonical `theme_astral` builders, factories, repositories, and validators before adding new code paths.
- Reuse existing test modules for corrected behavior unless a new focused test file is required by a new finding surface.
- Keep one closure report and one evidence set; do not duplicate the same decision across multiple report files.
- Do not duplicate JSON schema, provider payload shape, or prompt contract definitions in tests or docs.

## No Legacy / Forbidden Paths

- No legacy prompt carrier may be reintroduced as an active source for canonical `theme_astral` prompt construction.
- No compatibility route through old prompt input names may be used to close a finding.
- No fallback behavior may hide an unresolved finding.
- `chart_json`, `natal_data`, and `llm_astrology_input_v1` must not feed canonical `theme_astral`.
- Commercial labels `free`, `basic`, and `premium` must not become LLM-visible plan values.
- Do not preserve legacy behavior.

## Reintroduction Guard

- Guard target: final closure of CS-377 findings without stale report, docs, examples, or old-carrier drift.
- Forbidden surfaces:
  - Active prompt construction from `chart_json`, `natal_data`, or `llm_astrology_input_v1`.
  - LLM-visible commercial plan labels in provider payloads.
  - Report rows that keep an actionable Critical, High, or Medium finding open.
  - Docs or examples containing unresolved placeholder or CS-371 wording.
- Required guard evidence:
  - `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
  - `pytest -q backend/tests/integration/test_theme_astral_prompt_contract_persistence.py`
  - `pytest -q backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`
  - `pytest -q backend/tests/architecture/test_theme_astral_prompt_contract_guard.py`
  - `rg -n "chart_json|natal_data|llm_astrology_input_v1|legacy|free|basic|premium|\"plan\"" backend/app backend/tests _condamad/examples`
  - `rg -n "\\{\\{|[T]ODO|[T]BD|Quand CS-371 sera implemente" _condamad/docs _condamad/examples`

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend corrections must not move business logic into router surfaces. | Targeted `rg`; backend `pytest`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Prompt-generation validation paths must point to collected tests. | Targeted `pytest`; report matrix. |
| Registry gap `theme_astral-cs377-finding-closure` | No exact invariant covers CS-377 finding closure. | Resolver output persisted. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no frontend file is touched.
- RG-052 frontend CSS namespaces are out of scope because no styling surface is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| CS-377 finding baseline | `_condamad/stories/CS-378-fermeture-findings-review-adversariale-theme-astral/evidence/cs-377-findings-before.md` | Findings before corrections. |
| Closure report | `_condamad/reports/cs-378-corrections-review-adversariale-finale-theme-astral.md` | Final correction ledger. |
| Validation output | `_condamad/stories/CS-378-fermeture-findings-review-adversariale-theme-astral/evidence/validation.txt` | Lint and tests. |
| Re-review output | `_condamad/stories/CS-378-fermeture-findings-review-adversariale-theme-astral/evidence/re-review.txt` | Post-correction proof. |
| Changed-path proof | `_condamad/stories/CS-378-fermeture-findings-review-adversariale-theme-astral/evidence/changed-paths.txt` | Scope proof. |
| Guardrail output | `_condamad/stories/CS-378-fermeture-findings-review-adversariale-theme-astral/evidence/guardrails.txt` | Scoped guardrails. |
| Review output | `_condamad/stories/CS-378-fermeture-findings-review-adversariale-theme-astral/generated/11-code-review.md` | Review handoff. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no broad allowlist handling is authorized for unresolved findings, old carriers, stale docs, or provider payload drift.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/reports/cs-378-corrections-review-adversariale-finale-theme-astral.md` - final closure report.
- `backend/app/domain/llm/**` - corrected prompt contract behavior from CS-377 findings.
- `backend/app/domain/astrology/interpretation/**` - corrected interpretation material behavior from CS-377 findings.
- `backend/app/infra/db/repositories/interpretation_material_source_repository.py` - corrected persistence behavior from CS-377 findings.
- `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py` - corrected seeded contract data from CS-377 findings.
- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md` - aligned docs after corrections.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/**` - regenerated examples after corrections.
- `_condamad/stories/CS-378-fermeture-findings-review-adversariale-theme-astral/evidence/**` - persisted validation evidence.
- `_condamad/stories/CS-378-fermeture-findings-review-adversariale-theme-astral/generated/11-code-review.md` - review handoff.

Likely tests:

- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py`
- `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`
- `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py`

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope unless CS-377 names an API finding for this contract.
- `backend/alembic/**` - out of scope unless CS-377 names a schema finding for this contract.
- `_condamad/stories/regression-guardrails.md` - out of scope during normal story generation.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: from repository root, run `.\.venv\Scripts\Activate.ps1`, then `cd backend`.
- VC2: from `backend`, run `ruff format .`.
- VC3: from `backend`, run `ruff check .`.
- VC4: from `backend`, run:
  - `python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py --tb=short`
  - `python -B -m pytest -q tests/integration/test_theme_astral_prompt_contract_persistence.py --tb=short`
  - `python -B -m pytest -q tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py --tb=short`
  - `python -B -m pytest -q tests/architecture/test_theme_astral_prompt_contract_guard.py --tb=short`
- VC5: from `backend`, run `python -B -m pytest -q tests --tb=short` when corrected CS-377 findings touch broader LLM runtime surfaces.
- VC6: from repository root, run `python -m json.tool` on each provider payload file:
  - `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/free-provider-payload.json`
  - `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/basic-provider-payload.json`
  - `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/premium-provider-payload.json`
- VC7: from repository root, run:
  - `rg -n "\\{\\{|[T]ODO|[T]BD|Quand CS-371 sera implemente" _condamad/docs _condamad/examples`
- VC8: from repository root, run targeted re-review scans:
  - `rg -n "Critical|High|Medium|open|invalide|corrections requises" _condamad/audits/theme-astral-prompt-contract`
  - `rg -n "Critical|High|Medium|open|invalide|corrections requises" _condamad/reports/cs-378-corrections-review-adversariale-finale-theme-astral.md`
- VC9: from repository root, run:
  - `python -c "from pathlib import Path; p=Path('_condamad/reports/cs-378-corrections-review-adversariale-finale-theme-astral.md'); assert p.exists()"`
- VC10: from `_condamad/reports`, run:
  - `rg -n "Liste des findings CS-377" cs-378-corrections-review-adversariale-finale-theme-astral.md`
  - `rg -n "Resultat final" cs-378-corrections-review-adversariale-finale-theme-astral.md`
- VC11: from the CS-378 story directory, run:
  - `python -c "from pathlib import Path; base=Path('evidence'); assert (base/'validation.txt').exists(); assert (base/'re-review.txt').exists()"`
- VC12: from repository root, run `git status --short` and persist the changed-path proof.

## Regression Risks

- A report could mark a finding closed without a matching code, test, doc, or example delta.
- CS-377 may contain findings that require a product decision before code can change.
- Example payload regeneration can drift from runtime builders unless JSON parsing and targeted tests run together.
- Commercial plan labels can remain valid file names while being invalid inside provider payload values.
- A broad runtime change can create unrelated worktree deltas that obscure CS-377 closure.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the Python venv before every Python, Ruff, or Pytest command.
- From repository root, run `.\.venv\Scripts\Activate.ps1`, then `cd backend` before backend validation commands.
- Persist command output under `_condamad/stories/CS-378-fermeture-findings-review-adversariale-theme-astral/evidence/`.
- Keep each corrected finding tied to the CS-377 finding ID or report heading.
- Do not edit the CS-377 audit report to make findings disappear.

## References

- `_story_briefs/cs-378-corriger-findings-review-adversariale-finale-theme-astral.md`
- `_condamad/stories/CS-377-audit-review-adversariale-complete-theme-astral-prompt-contract-final/00-story.md`
- `_condamad/stories/CS-372-aligner-profils-livraison-theme-astral-db-provider/00-story.md`
- `_condamad/stories/CS-373-structurer-birth-context-theme-astral-llm-input/00-story.md`
- `_condamad/stories/CS-374-renforcer-exemples-json-theme-astral-textes-interpretation/00-story.md`
- `_condamad/stories/CS-375-mettre-a-jour-docs-structure-json-theme-astral/00-story.md`
- `_condamad/stories/CS-376-validation-provider-smoke-theme-astral/00-story.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md#RG-002`
- `_condamad/stories/regression-guardrails.md#RG-022`
