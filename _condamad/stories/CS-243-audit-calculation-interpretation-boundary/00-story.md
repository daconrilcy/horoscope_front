# Story CS-243 audit-calculation-interpretation-boundary: Audit Calculation Interpretation Boundary
Status: ready-to-dev

## Trigger / Source

- Source type: audit-to-story with repository-informed boundary.
- Source reference: `_story_briefs/cs-243-audit-calculation-interpretation-boundary-audit.md`.
- Related context: CS-229 to CS-236 separated structural runtime facts, interpretive hints, chart object payloads, and enriched sign profiles.
- Problem statement: produce a CONDAMAD audit that classifies the boundary between calculated facts, interpretive signals, text, LLM prompts, and product projections.
- Source-alignment evidence: PASS; the story preserves the requested audit folder, six standard files, required grid, boundary decisions, and CS-252 to CS-254.

## Objective

Create one timestamped CONDAMAD audit folder under `_condamad/audits/astro-calculation-interpretation-boundary/`.

The audit must classify current backend astrology surfaces across astronomical fact, structural astrological fact, structural scoring, interpretive signal,
text, LLM prompt, and product projection categories.

## Target State

- A latest audit folder exists under `_condamad/audits/astro-calculation-interpretation-boundary/`.
- `00-audit-report.md` contains the mandatory grid and explicit boundary decisions.
- `01-evidence-log.md` contains reproducible proof for structural surfaces, interpretive surfaces, prompts, LLM adapters, and projections.
- `02-finding-register.md` lists potential boundary violations and confusion risks with severity, evidence, and closure route.
- `03-story-candidates.md` qualifies CS-252, CS-253, and CS-254 with priority, source finding, validation plan, and stop condition.
- `04-risk-matrix.md` maps calculation, interpretation, scoring, prompt, text, and product projection risks.
- `05-executive-summary.md` gives a decision-ready summary for product and engineering follow-up.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-243-audit-calculation-interpretation-boundary-audit.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-243`.
- Evidence 3: `_condamad/stories/CS-242-audit-calculation-graph-readiness/00-story.md` - sibling audit story shape consulted.
- Evidence 4: `backend/tests/architecture/test_chart_interpretation_input_boundary.py` - scoped evidence for interpretation input boundary guards.
- Evidence 5: `backend/tests/architecture/test_structural_runtime_boundary.py` - scoped evidence for structural runtime boundary guards.
- Evidence 6: `backend/app/tests/unit/test_chart_result_service.py` - scoped evidence for persisted natal payload boundaries.
- Evidence 7: `backend/app/tests/integration/test_llm_qa_runtime_contracts.py` - scoped evidence for LLM runtime contract checks.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - registry consulted through the guardrail resolver for this audit scope.
- Source-alignment review result: PASS; no source concern was narrowed, deferred, or replaced by an implementation task.

## Domain Boundary

- Domain: backend-astrology-audit
- In scope:
  - Documentation-only audit of backend astrology calculation, scoring, interpretation, prompt, LLM adapter, and projection surfaces.
  - Inventory of structural surfaces, interpretive surfaces, prompts, LLM adapters, and product projections.
  - Classification using the exact categories from the source brief.
  - Boundary decisions separating internal contracts, public contracts, and LLM contracts.
  - Qualification of candidate stories CS-252, CS-253, and CS-254.
- Out of scope:
  - Frontend UI, API endpoint creation, DB migrations, auth, i18n, styling, build tooling, and production configuration changes.
  - Modifying prompts, calculators, projection code, adapters, public payloads, tests, or runtime behavior.
- Explicit non-goals:
  - No code change outside the audit artifacts.
  - No prompt edit, calculator edit, new projection, schema change, seed change, migration, or frontend screen.
  - No replacement of implementation work for CS-252, CS-253, or CS-254.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend calculation and interpretation boundary audit contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Produce documentation artifacts only under the scoped audit folder.
  - Do not change prompts, calculators, projections, adapters, public payloads, tests, routes, database schema, or frontend behavior.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: repository evidence cannot classify a required surface or boundary owner.
- Additional validation rules:
  - The audit report must include every mandatory grid column from the source brief.
  - The audit report must use the seven required category labels from the source brief.
  - The evidence log must cite code, tests, docs, generated evidence, or bounded absence scans for each classified surface.
  - Internal contract, public contract, and LLM contract recommendations must be separate decisions.
  - Story candidates CS-252, CS-253, and CS-254 must include source-finding links, validation evidence, and stop conditions.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Boundary claims must cite source files, architecture guards, tests, docs, and scans proving actual backend behavior. |
| Baseline Snapshot | yes | The audit must persist a reproducible baseline for calculation, interpretation, prompt, adapter, and projection evidence. |
| Ownership Routing | yes | Audit artifacts have canonical CONDAMAD locations and must not be mixed into app code or test suites. |
| Allowlist Exception | no | No allowlist handling is authorized for this documentation-only audit. |
| Contract Shape | yes | The audit has required files, required grid columns, required categories, and candidate stories. |
| Batch Migration | no | No migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | The story must guard against implementing prompt, calculator, projection, or adapter changes while auditing. |
| Persistent Evidence | yes | The audit folder itself is the review handoff evidence. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The timestamped audit folder exists. | Evidence profile: baseline_before_after_diff; `python` checks `_condamad/audits/astro-calculation-interpretation-boundary`. |
| AC2 | All six standard audit files exist. | Evidence profile: baseline_before_after_diff; `python` checks required filenames in the latest audit folder. |
| AC3 | The mandatory grid columns are present. | Evidence profile: json_contract_shape; `rg` checks each column in `00-audit-report.md`. |
| AC4 | The required categories are used. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks all seven category labels in audit artifacts. |
| AC5 | Structural surfaces are inventoried. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/architecture/test_structural_runtime_boundary.py`. |
| AC6 | Interpretation inputs are inventoried. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/architecture/test_chart_interpretation_input_boundary.py`. |
| AC7 | Prompt surfaces are analyzed. | Evidence profile: baseline_before_after_diff; `rg` checks prompt and LLM terms in `01-evidence-log.md`. |
| AC8 | Adapter surfaces are analyzed. | Evidence profile: baseline_before_after_diff; `pytest -q backend/app/tests/integration/test_llm_qa_runtime_contracts.py`. |
| AC9 | Product projections are analyzed. | Evidence profile: baseline_before_after_diff; `pytest -q backend/app/tests/unit/test_chart_result_service.py`. |
| AC10 | Boundary violations are registered. | Evidence profile: baseline_before_after_diff; `rg` checks `02-finding-register.md` for violation and confusion risk terms. |
| AC11 | Contract recommendations are separated. | Evidence profile: json_contract_shape; `rg` checks internal, public, and LLM contract terms. |
| AC12 | Candidate stories are qualified. | Evidence profile: baseline_before_after_diff; `rg` checks `03-story-candidates.md` for CS-252, CS-253, and CS-254. |
| AC13 | Audit validation commands pass. | Evidence profile: baseline_before_after_diff; `python` runs the CONDAMAD audit validator. |
| AC14 | No application files are changed. | Evidence profile: no_legacy_contract; `python` or `git diff --name-only` verifies only audit artifacts changed. |

## Implementation Tasks

- [ ] Task 1: Create the latest audit folder under `_condamad/audits/astro-calculation-interpretation-boundary/`. (AC: AC1)
- [ ] Task 2: Create the six standard audit files with coherent cross-references. (AC: AC2)
- [ ] Task 3: Build the mandatory classification grid with every required column. (AC: AC3)
- [ ] Task 4: Classify all required categories from astronomical fact through product projection. (AC: AC4)
- [ ] Task 5: Inventory structural runtime facts, scoring, chart objects, and calculation graph surfaces. (AC: AC5)
- [ ] Task 6: Inventory interpretation inputs, interpretive signals, text, prompts, LLM adapters, and projections. (AC: AC6, AC7, AC8, AC9)
- [ ] Task 7: Register every potential boundary violation with owner, runtime surface, public surface, and confusion risk. (AC: AC10)
- [ ] Task 8: Write separate recommendations for internal contracts, public contracts, and LLM contracts. (AC: AC11)
- [ ] Task 9: Qualify CS-252, CS-253, and CS-254 with priority, source finding, validation evidence, and stop condition. (AC: AC12)
- [ ] Task 10: Run document validation and verify that no app, test, migration, config, or frontend file changed. (AC: AC1, AC2, AC13, AC14)

## Files to Inspect First

- `_story_briefs/cs-243-audit-calculation-interpretation-boundary-audit.md` - source contract.
- `_condamad/stories/CS-229-aspect-runtime-structural-interpretive-contracts/00-story.md` - structural and interpretive predecessor.
- `_condamad/stories/CS-230-migrate-aspect-runtime-to-structural-and-hints/00-story.md` - runtime migration predecessor.
- `_condamad/stories/CS-231-runtime-boundary-guardrails-structural-vs-interpretive/00-story.md` - boundary guard predecessor.
- `_condamad/stories/CS-236-exploiter-profils-signes-enrichis-signatures-interpretation/00-story.md` - recent interpretation predecessor.
- `_condamad/stories/CS-242-audit-calculation-graph-readiness/00-story.md` - sibling audit story shape.
- `backend/app/domain/astrology/**` - calculated facts, structural facts, scoring, chart object, and interpretation surfaces.
- `backend/app/domain/llm/**` - LLM runtime, prompt, contract, and narrator surfaces.
- `backend/app/llm_orchestration/**` - effective prompt rendering, gateway, adapter, and provider orchestration.
- `backend/app/services/**` - business services that bridge calculation, interpretation, or LLM generation.
- `backend/app/prediction/**` - daily prediction projection and narration surfaces.
- `backend/app/api/v1/routers/**` - public or admin surfaces that expose or trigger interpreted content.
- `backend/tests/architecture/test_chart_interpretation_input_boundary.py` - interpretation input boundary guard.
- `backend/tests/architecture/test_structural_runtime_boundary.py` - structural runtime boundary guard.
- `backend/app/tests/integration/test_llm_qa_runtime_contracts.py` - LLM contract runtime evidence.
- `backend/app/tests/unit/test_chart_result_service.py` - persisted natal payload evidence.
- `docs/2026-04-20-audit-prompts-backend.md` - prompt process audit context.
- `docs/2026-04-20-audit-prompts-backend-post-story-70-14.md` - post-refactor prompt process context.

## Runtime Source of Truth

- Primary source of truth:
  - `AST guard`, generated audit manifest, Python source files, architecture tests, unit tests, integration tests, and docs.
- Secondary evidence:
  - Targeted `rg` scans proving calculation terms, interpretation terms, narrative terms, prompt terms, adapter paths, and projection paths.
- Static scans alone are not sufficient for boundary claims because:
  - Each claim must cite code, tests, generated audit evidence, documented absence scans, or deterministic architecture guards.

## Contract Shape

- Contract type:
  - CONDAMAD domain audit folder.
- Fields:
  - `element`: calculated fact, signal, text, prompt, adapter, projection, or public surface.
  - `categorie`: one required category label from the source brief.
  - `owner`: canonical backend owner or unresolved owner.
  - `surface_runtime`: runtime file, function, contract, test, doc, or documented absence.
  - `surface_publique`: public payload, API output, UI-visible projection, or `none`.
  - `risque_confusion`: bounded confusion risk between calculation, interpretation, text, prompt, and product projection.
  - `decision_frontiere`: keep, move-to-internal, move-to-public-contract, move-to-llm-contract, or story-candidate.
  - `preuve`: evidence command, file path, test path, generated artifact, or bounded absence scan.
- Required fields:
  - `element`
  - `categorie`
  - `owner`
  - `surface_runtime`
  - `surface_publique`
  - `risque_confusion`
  - `decision_frontiere`
  - `preuve`
- Optional fields:
  - none
- Status codes:
  - none; this is not an API route.
- Serialization names:
  - Markdown grid columns keep the exact French labels from the source brief.
- Required files:
  - `00-audit-report.md`
  - `01-evidence-log.md`
  - `02-finding-register.md`
  - `03-story-candidates.md`
  - `04-risk-matrix.md`
  - `05-executive-summary.md`
- Required grid columns:
  - `Élément`
  - `Catégorie`
  - `Owner`
  - `Surface runtime`
  - `Surface publique`
  - `Risque de confusion`
- Required categories:
  - `fait astronomique`
  - `fait astrologique structurel`
  - `scoring structurel`
  - `signal interprétatif`
  - `texte`
  - `prompt LLM`
  - `projection produit`
- Required examples:
  - `longitude Mars`
  - `Mars maison 10`
  - `Mars dominant`
  - `Mars combatif`
  - `Vous avez une énergie de conquête`
- Required candidate stories:
  - `CS-252`
  - `CS-253`
  - `CS-254`
- Frontend type impact:
  - none.
- Generated contract impact:
  - none.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-243-audit-calculation-interpretation-boundary-audit.md`
  - `backend/app/domain/astrology`
  - `backend/app/domain/llm`
  - `backend/app/llm_orchestration`
  - `backend/app/services`
  - `backend/app/prediction`
  - `backend/tests/architecture`
  - `docs/2026-04-20-audit-prompts-backend.md`
- Comparison after implementation:
  - Latest child folder under `_condamad/audits/astro-calculation-interpretation-boundary/`.
- Expected invariant:
  - The only intended repository delta is the new audit folder and its standard CONDAMAD audit files.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Calculation interpretation boundary audit | `_condamad/audits/astro-calculation-interpretation-boundary/` | `backend/app/**` |
| Evidence log | `_condamad/audits/astro-calculation-interpretation-boundary/` | `backend/tests/**` |
| Finding register | `_condamad/audits/astro-calculation-interpretation-boundary/` | Runtime guard source files |
| Story candidates | `_condamad/audits/astro-calculation-interpretation-boundary/` | `_condamad/stories/**` |
| Boundary recommendations | `_condamad/audits/astro-calculation-interpretation-boundary/` | Prompt, calculator, or projection code |

## Mandatory Reuse / DRY Constraints

- Reuse the source brief categories, examples, and expected validation commands as the audit contract.
- Reuse existing code, tests, docs, prior story evidence, and architecture guards instead of duplicating large source excerpts.
- Use one canonical category vocabulary across report, evidence log, findings, candidates, risk matrix, and summary.
- Use one canonical boundary decision vocabulary across all six audit files.
- Do not add external packages or custom audit tooling.

## No Legacy / Forbidden Paths

- No legacy route path may be added during this audit.
- No compatibility route path may be added during this audit.
- No fallback route path may be added during this audit.
- Do not create app-code aliases, shims, runtime fallback branches, or compatibility wrappers.
- Do not modify prompts, calculators, projections, adapters, public payloads, route handlers, tests, seeds, migrations, or frontend files.
- Do not transform a product projection or LLM output into a calculated fact.
- Do not put narrative tokens into calculators or structural scoring code.

## Reintroduction Guard

- Forbidden app-code delta:
  - `backend/app/**`
  - `backend/tests/**`
  - `backend/app/tests/**`
  - `backend/migrations/**`
  - `frontend/src/**`
  - `docs/db_seeder/**`
- Required guard:
  - `git diff --name-only` must show only the audit folder for implementation changes.
  - `rg` must prove boundary decisions are documented in audit artifacts, not implemented as prompt, calculator, adapter, projection, or test changes.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Local anti-drift: no API router change belongs to this audit. | `git diff --name-only`; bounded `rg`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Applicable pattern: candidate validation paths must be concrete. | `rg` over `03-story-candidates.md`. |
| Registry gap | No exact calculation-interpretation boundary audit guardrail was present in the resolver output. | Resolver output reviewed. |

Non-applicable examples retained to prevent scope drift:

- RG-047 frontend inline styles are out of scope because no frontend files are touched.
- RG-052 frontend CSS namespace convergence is out of scope because no styling files are touched.
- RG-041 entitlement documentation is out of scope because calculation and interpretation boundaries are audited.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Audit report | `_condamad/audits/astro-calculation-interpretation-boundary/{timestamp}/00-audit-report.md` | Grid and boundary decisions. |
| Evidence log | `_condamad/audits/astro-calculation-interpretation-boundary/{timestamp}/01-evidence-log.md` | Reproducible proof by surface. |
| Finding register | `_condamad/audits/astro-calculation-interpretation-boundary/{timestamp}/02-finding-register.md` | Violations and confusion risks. |
| Story candidates | `_condamad/audits/astro-calculation-interpretation-boundary/{timestamp}/03-story-candidates.md` | Prioritized CS-252 through CS-254. |
| Risk matrix | `_condamad/audits/astro-calculation-interpretation-boundary/{timestamp}/04-risk-matrix.md` | Calculation and interpretation risks. |
| Executive summary | `_condamad/audits/astro-calculation-interpretation-boundary/{timestamp}/05-executive-summary.md` | Decision summary. |
| Review output | `_condamad/stories/CS-243-audit-calculation-interpretation-boundary/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this documentation-only audit.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/astro-calculation-interpretation-boundary/{timestamp}/00-audit-report.md` - grid and boundary decisions.
- `_condamad/audits/astro-calculation-interpretation-boundary/{timestamp}/01-evidence-log.md` - reproducible evidence.
- `_condamad/audits/astro-calculation-interpretation-boundary/{timestamp}/02-finding-register.md` - violations and confusion risks.
- `_condamad/audits/astro-calculation-interpretation-boundary/{timestamp}/03-story-candidates.md` - prioritized CS-252 through CS-254.
- `_condamad/audits/astro-calculation-interpretation-boundary/{timestamp}/04-risk-matrix.md` - risk classification.
- `_condamad/audits/astro-calculation-interpretation-boundary/{timestamp}/05-executive-summary.md` - decision summary.

Likely tests:

- Document validation through `condamad_domain_audit_validate.py`.
- Document lint through `condamad_domain_audit_lint.py`.
- Targeted `rg` checks against latest audit artifacts.
- `pytest -q backend/tests/architecture/test_structural_runtime_boundary.py` for structural runtime boundary evidence.
- `pytest -q backend/tests/architecture/test_chart_interpretation_input_boundary.py` for interpretation input boundary evidence.
- `pytest -q backend/app/tests/integration/test_llm_qa_runtime_contracts.py` for LLM runtime evidence.
- `pytest -q backend/app/tests/unit/test_chart_result_service.py` for projection persistence evidence.

Files not expected to change:

- `backend/app/**` - out of scope; no backend runtime is touched.
- `backend/tests/**` - out of scope; no test code is touched.
- `backend/app/tests/**` - out of scope; no app-local tests are touched.
- `backend/migrations/**` - out of scope; no database migration is touched.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `docs/db_seeder/**` - out of scope; no seed or reference data is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `$auditFolder = Get-ChildItem -Directory .\_condamad\audits\astro-calculation-interpretation-boundary | Sort-Object Name -Descending | Select-Object -First 1`
- VC2: `rg -n "interpretation|prompt|narrative|LLM|ChartInterpretationInput|adapter|runtime" backend/app backend/tests docs`
- VC3: `rg -n "fait astronomique|scoring structurel|prompt LLM|projection produit" "$($auditFolder.FullName)\00-audit-report.md"`
- VC4: `rg -n "longitude Mars|Mars maison 10|Mars dominant|Mars combatif|Vous avez une énergie de conquête" "$($auditFolder.FullName)\00-audit-report.md"`
- VC5: `rg -n "contrat interne|contrat public|contrat LLM|CS-252|CS-253|CS-254" "$($auditFolder.FullName)\03-story-candidates.md"`
- VC6: `pytest -q backend/tests/architecture/test_structural_runtime_boundary.py`
- VC7: `pytest -q backend/tests/architecture/test_chart_interpretation_input_boundary.py`
- VC8: `pytest -q backend/app/tests/integration/test_llm_qa_runtime_contracts.py`
- VC9: `pytest -q backend/app/tests/unit/test_chart_result_service.py`
- VC10: `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py $auditFolder.FullName`
- VC11: `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py $auditFolder.FullName`
- VC12: `python -c "from pathlib import Path; p=max(Path('_condamad/audits/astro-calculation-interpretation-boundary').iterdir()); assert (p/'00-audit-report.md').exists()"`
- VC13: `git diff --name-only`

Before VC6, VC7, VC8, VC9, VC10, VC11, and VC12, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The audit may treat narrative text or prompt content as calculated truth without marking the confusion risk.
- The audit may treat structural scores as interpretation without recording owner and public surface impact.
- Product projections may be confused with internal contracts or LLM contract inputs.
- Candidate stories may drift into implementation design without evidence links or stop conditions.
- A developer may accidentally change app code, tests, config, prompts, calculators, projections, or frontend files while producing audit artifacts.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all audit artifacts under the latest `_condamad/audits/astro-calculation-interpretation-boundary/` child folder.
- Treat calculated facts, structural facts, scoring, interpretive signals, text, prompts, and projections as separate categories.
- Treat public contracts, internal contracts, and LLM contracts as separate recommendation surfaces.
- Do not modify backend, frontend, migration, seed, prompt, adapter, projection, calculator, serializer, or test files.

## References

- `_story_briefs/cs-243-audit-calculation-interpretation-boundary-audit.md`
- `_condamad/stories/CS-229-aspect-runtime-structural-interpretive-contracts/00-story.md`
- `_condamad/stories/CS-230-migrate-aspect-runtime-to-structural-and-hints/00-story.md`
- `_condamad/stories/CS-231-runtime-boundary-guardrails-structural-vs-interpretive/00-story.md`
- `_condamad/stories/CS-236-exploiter-profils-signes-enrichis-signatures-interpretation/00-story.md`
- `_condamad/stories/CS-242-audit-calculation-graph-readiness/00-story.md`
- `backend/tests/architecture/test_chart_interpretation_input_boundary.py`
- `backend/tests/architecture/test_structural_runtime_boundary.py`
- `backend/app/tests/integration/test_llm_qa_runtime_contracts.py`
- `backend/app/tests/unit/test_chart_result_service.py`
- `docs/2026-04-20-audit-prompts-backend.md`
- `docs/2026-04-20-audit-prompts-backend-post-story-70-14.md`
- `_condamad/stories/regression-guardrails.md`
