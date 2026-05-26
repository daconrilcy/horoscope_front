# Story CS-328 architecture-transition-calculs-interpretations-injection-llm: Architecture Transition Calculs Interpretations Injection LLM
Status: ready-to-dev

## Trigger / Source

Brief direct source:
`_story_briefs/cs-328-architecture-transition-calculs-interpretations-injection-llm.md`.

Problem statement: les audits CS-324 a CS-327 doivent etre consolides en une
architecture de transition qui separe calcul, interpretation pre-narrative,
injection LLM interne, prompt runtime et audit narratif.

Source stakes:

- User impact: eviter une reponse LLM fondee sur une surface appauvrie ou sur
  une projection produit non faite pour etre l'entree interne canonique.
- Technical risk: melanger faits calcules, signaux interpretatifs, shaping
  editorial, preuves d'audit et payload runtime dans un seul contrat implicite.
- Closure expectation: produire un rapport d'architecture actionnable avec
  decisions, owners, contrat cible conceptuel et stories candidates.
- Forbidden regression: aucune modification applicative, prompt, provider,
  endpoint public, securite, CI, frontend, DB ou migration.

Source-alignment evidence: the objective, ACs, tasks, evidence artifacts,
validation plan, non-goals and guardrails map back to the brief's mandatory
questions, matrices, source audits and closure expectation.

## Objective

Produire un dossier d'architecture intermediaire qui decide la cible de
transition entre calculs astrologiques, interpretations pre-narratives et
injection LLM interne.

Le rapport doit designer l'entree LLM canonique, cadrer les surfaces de
transition a confiner, definir le contrat conceptuel d'injection et proposer
les stories de refactor prioritaires.

## Target State

Un dossier d'architecture est cree sous:
`_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/`.

Il contient:

- `00-architecture.md` avec le flux cible, les decisions et les reponses aux
  questions obligatoires.
- `01-evidence-map.md` avec le mapping des audits CS-324 a CS-327 vers chaque
  decision d'architecture.
- `02-target-contract.md` avec le contrat cible conceptuel d'injection LLM.
- `03-legacy-transition.md` avec le plan de confinement et transition des
  surfaces historiques.
- `04-story-candidates.md` avec les candidates de refactor priorisees.
- `05-risk-register.md` avec les risques et mitigations.

Le flux cible documente:

```text
CalculationGraph / ChartObjectRuntimeData
-> ChartInterpretationInput
-> contrat interne d'injection LLM
-> prompt runtime
-> audit narrative answer
```

## Current State Evidence

- Evidence 1: `_story_briefs/cs-328-architecture-transition-calculs-interpretations-injection-llm.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign the story number.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `_condamad/stories/CS-324-audit-calculs-interpretations-llm/00-story.md` - source audit contract inspected.
- Evidence 5: `_condamad/stories/CS-325-audit-pipeline-prompt-llm-natal/00-story.md` - source audit contract inspected.
- Evidence 6: `_condamad/stories/CS-326-audit-projections-interpretatives-llm-input-readiness/00-story.md` - source audit contract inspected.
- Evidence 7: `_condamad/stories/CS-327-audit-configuration-prompts-placeholders-input-schema/00-story.md` - source audit contract inspected.
- Evidence 8: `_story_briefs/cs-245-archi-canonical-astrology-runtime-transition.md` - runtime architecture source brief inspected.
- Evidence 9: `_story_briefs/cs-254-ai-scoring-narrative-input-contract.md` - AI narrative input contract brief inspected.
- Evidence 10: `_story_briefs/cs-256-define-structured-facts-v1-stable-hashable-fact-projection.md` - fact projection brief inspected.
- Evidence 11: `_story_briefs/cs-258-define-client-interpretation-projection-v1-by-plan.md` - client projection brief inspected.
- Evidence 12: `_story_briefs/cs-259-define-narrative-answer-audit-v1.md` - narrative audit brief inspected.
- Evidence 13: `_story_briefs/cs-287-implement-client-interpretation-projection-v1-builder-by-plan.md` - builder brief inspected.
- Evidence 14: `_story_briefs/cs-291-implement-generic-projection-endpoint.md` - projection endpoint brief inspected.
- Evidence 15: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver.
- Repository structure alert: expected audit output folders for CS-324 to CS-327 are not present in this workspace yet.
- Repository structure alert: implementation must create the architecture timestamp folder and stop if required audit deliverables are still missing.

## Domain Boundary

- Domain: architecture
- In scope:
  - Consolidation of audits CS-324, CS-325, CS-326 and CS-327.
  - Architecture target for canonical internal LLM input.
  - Conceptual target contract for facts, signals, limits, evidence, shaping,
    provenance and exclusions.
  - Transition plan for historical payload surfaces.
  - Refactor story candidates, owners and sequencing.
  - Creation of `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/` artifacts.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling,
    migrations, prompt edits, provider changes, public endpoints and app code.
- Explicit non-goals:
  - No implementation of the target contract.
  - No prompt wording change.
  - No provider integration.
  - No endpoint change.
  - No application source or test change.
  - No application source change for existing historical surfaces.

Named brief primitives in scope:

- `CalculationGraph`
- `ChartObjectRuntimeData`
- `ChartInterpretationInput`
- `ChartInterpretationInputRuntimeData`
- `structured_facts_v1`
- `client_interpretation_projection_v1`
- `AINarrativeInputContract`
- `narrative_answer_audit_v1`
- `NatalExecutionInput`
- `ExecutionContext`
- `chart_json`
- `natal_data`
- `astro_context`
- `evidence_catalog`
- `projection_hash`
- `llm_input_hash`
- `evidence_refs`
- prompt runtime

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this architecture report for LLM input transition.
- Behavior change allowed: no
- Behavior change constraints:
  - Create only architecture and story evidence artifacts.
  - Keep backend application files unchanged.
  - Keep backend test files unchanged.
  - Keep frontend files unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: required audit deliverables from CS-324 to CS-327 are unavailable during implementation.
- Additional validation rules:
  - `AST guard` or bounded `rg` evidence must prove no application source was modified.
  - `python` path checks must prove all architecture deliverables exist.
  - `rg` evidence must prove the required matrices and hash tokens are present.
  - The report must separate architecture decisions from future refactor implementation.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Source audits and code-owner citations prove each architecture decision. |
| Baseline Snapshot | yes | The evidence map compares current audited surfaces with target decisions. |
| Ownership Routing | yes | Each target layer must have a canonical owner and forbidden destination. |
| Allowlist Exception | no | No allowlist handling is authorized for this architecture-only story. |
| Contract Shape | yes | The architecture deliverables have fixed files, matrices and sections. |
| Batch Migration | no | No multi-file conversion is in scope. |
| Reintroduction Guard | yes | App, prompt, provider, endpoint and frontend surfaces must stay unchanged. |
| Persistent Evidence | yes | Architecture outputs and validation evidence must persist for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The four source audits are cited. | Evidence profile: baseline_before_after_diff; `rg -n "CS-324|CS-325|CS-326|CS-327"` in architecture folder. |
| AC2 | The target flow is documented. | Evidence profile: ast_architecture_guard; `rg` checks `CalculationGraph` and `prompt runtime` in `00-architecture.md`. |
| AC3 | The required surface matrix exists. | Evidence profile: json_contract_shape; `rg` checks `ChartObjectRuntimeData` and `Action recommandee`. |
| AC4 | The injection block matrix exists. | Evidence profile: json_contract_shape; `rg` checks `faits structurels` and `Source interdite`. |
| AC5 | The target contract is precise. | Evidence profile: json_contract_shape; `rg` checks `llm_input_hash` and `evidence_refs` in `02-target-contract.md`. |
| AC6 | Transition surfaces are confined. | Evidence profile: reintroduction_guard; `rg` checks `chart_json`, `natal_data` and `transition-condition`. |
| AC7 | Refactor candidates are prioritized. | Evidence profile: batch_migration_mapping; `rg` checks `Priorite` and `Validation attendue` in `04-story-candidates.md`. |
| AC8 | Application code remains unchanged. | Evidence profile: repo_wide_negative_scan; `python` checks `git status --short -- backend/app backend/tests frontend/src`. |
| AC9 | Architecture artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks all six architecture files exist. |

## Implementation Tasks

- [ ] Task 1: Verify CS-324 to CS-327 audit folders and record availability in `01-evidence-map.md`. (AC: AC1)
- [ ] Task 2: Read the four audit deliverables and map findings to architecture decisions. (AC: AC1, AC2)
- [ ] Task 3: Write `00-architecture.md` with target flow, owners, answers and the required surface matrix. (AC: AC2, AC3)
- [ ] Task 4: Write `02-target-contract.md` with fact, signal, limit, evidence, shaping, provenance and exclusion blocks. (AC: AC4, AC5)
- [ ] Task 5: Write `03-legacy-transition.md` with confined historical surfaces and transition-condition rows. (AC: AC6)
- [ ] Task 6: Write `04-story-candidates.md` with prioritized refactor candidates and validation expectations. (AC: AC7)
- [ ] Task 7: Write `05-risk-register.md` with product, auditability and refactor sequencing risks. (AC: AC2, AC5)
- [ ] Task 8: Run validation commands and persist output in the architecture folder. (AC: AC8, AC9)

## Files to Inspect First

- `_story_briefs/cs-328-architecture-transition-calculs-interpretations-injection-llm.md`
- `_condamad/audits/calculs-interpretations-vers-llm/**`
- `_condamad/audits/pipeline-prompt-llm-natal/**`
- `_condamad/audits/projections-interpretatives-llm-input-readiness/**`
- `_condamad/audits/configuration-prompts-placeholders-input-schema/**`
- `_condamad/stories/CS-324-audit-calculs-interpretations-llm/00-story.md`
- `_condamad/stories/CS-325-audit-pipeline-prompt-llm-natal/00-story.md`
- `_condamad/stories/CS-326-audit-projections-interpretatives-llm-input-readiness/00-story.md`
- `_condamad/stories/CS-327-audit-configuration-prompts-placeholders-input-schema/00-story.md`
- `_story_briefs/cs-245-archi-canonical-astrology-runtime-transition.md`
- `_story_briefs/cs-254-ai-scoring-narrative-input-contract.md`
- `_story_briefs/cs-256-define-structured-facts-v1-stable-hashable-fact-projection.md`
- `_story_briefs/cs-258-define-client-interpretation-projection-v1-by-plan.md`
- `_story_briefs/cs-259-define-narrative-answer-audit-v1.md`
- `_story_briefs/cs-287-implement-client-interpretation-projection-v1-builder-by-plan.md`
- `_story_briefs/cs-291-implement-generic-projection-endpoint.md`

## Runtime Source of Truth

- Primary source of truth:
  - Completed audit deliverables from CS-324, CS-325, CS-326 and CS-327.
  - Source briefs CS-245, CS-254, CS-256, CS-258, CS-259, CS-287 and CS-291.
  - `AST guard` or bounded `rg` scans over architecture artifacts.
- Secondary evidence:
  - `git status --short -- _condamad _story_briefs backend/app backend/tests frontend/src`.
  - Architecture evidence map citations with source path and decision mapping.
- Static scans alone are not sufficient for this story because:
  - The report must prove decisions from the completed source audits before
    recommending a canonical LLM input surface.

## Contract Shape

- Contract type:
  - Architecture artifact set and conceptual LLM injection contract.
- Fields:
  - `Surface`: audited or target transition surface.
  - `Bloc`: conceptual injection block name.
  - `Owner`: canonical owner path or source audit owner.
  - `Decision`: architecture decision tied to audit evidence.
  - `Validation attendue`: deterministic check for a future refactor story.
- Required fields:
  - `Surface`
  - `Bloc`
  - `Owner`
  - `Decision`
  - `Validation attendue`
- Optional fields:
  - none
- Serialization names:
  - Matrix headings are emitted exactly as listed in this contract shape.
- Required files:
  - `00-architecture.md`
  - `01-evidence-map.md`
  - `02-target-contract.md`
  - `03-legacy-transition.md`
  - `04-story-candidates.md`
  - `05-risk-register.md`
- Required matrices:
  - Surface matrix.
  - Target injection block matrix.
  - Story candidate matrix.
- Required surface matrix columns:
  - `Surface`
  - `Statut actuel`
  - `Statut cible`
  - `Owner actuel`
  - `Owner cible`
  - `LLM input`
  - `Public`
  - `Legacy`
  - `Action recommandee`
- Required injection block columns:
  - `Bloc`
  - `Contenu`
  - `Source canonique`
  - `Source interdite`
  - `Hashable`
  - `Prompt-visible`
  - `Audit-visible`
  - `Owner`
- Required story candidate columns:
  - `Priorite`
  - `Story candidate`
  - `But`
  - `Prerequis`
  - `Risque`
  - `Validation attendue`
- Required target contract blocks:
  - `faits structurels`
  - `signaux interpretatifs`
  - `limites et donnees manquantes`
  - `preuves / evidence refs`
  - `shaping editorial par plan`
  - `provenance et versions`
  - `exclusions explicites`
- Required audit tokens:
  - `projection_hash`
  - `llm_input_hash`
  - `evidence_refs`
- Status codes:
  - none; no API route is created or changed.
- Frontend type impact:
  - none; no frontend generated client or UI surface is in scope.
- Generated contract impact:
  - none; no OpenAPI or generated manifest change is in scope.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `01-evidence-map.md` records the available CS-324 to CS-327 audit artifacts and source brief citations.
- Comparison after implementation:
  - `00-architecture.md`, `02-target-contract.md`, `03-legacy-transition.md` and `04-story-candidates.md` contain decisions.
- Expected invariant:
  - The only intended repository delta is the architecture artifact directory plus story execution evidence.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Runtime calculation decision | CS-324 audit evidence and `ChartObjectRuntimeData` owners | Prompt text or frontend code |
| Prompt injection decision | CS-325 audit evidence and LLM runtime owners | Projection endpoint code |
| Projection readiness decision | CS-326 audit evidence and interpretation projection owners | Public API shape |
| Prompt schema readiness decision | CS-327 audit evidence and prompt configuration owners | Provider adapters |
| Architecture deliverables | `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/**` | Backend app or tests |

## Mandatory Reuse / DRY Constraints

- Reuse the four source audit deliverables as the evidence base.
- Keep one canonical decision mapping in `01-evidence-map.md`.
- Keep one canonical conceptual contract in `02-target-contract.md`.
- Reference the surface matrix instead of duplicating every row across files.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy route, prompt, provider, projection or payload path may be added.
- No compatibility route, prompt, provider, projection or payload path may be added.
- No fallback route, prompt, provider, projection or payload path may be added.
- Do not move application logic into architecture artifacts.
- Do not add source aliases, shims or broad allowlists.
- Forbidden app surfaces for edits:
  - `backend/app/**`
  - `backend/tests/**`
  - `frontend/**`
  - `backend/migrations/**`
  - prompt files, providers, public endpoints and DB models

## Reintroduction Guard

- Guarded surfaces:
  - `backend/app/**`
  - `backend/tests/**`
  - `frontend/src/**`
  - `_condamad/audits/**`
  - `_condamad/architecture/calculs-interpretations-injection-llm/**`
- Required guard:
  - `python` checks that `git status --short -- backend/app backend/tests frontend/src backend/migrations` returns no changed app surfaces.
  - `rg` checks architecture artifacts contain all required source audit IDs, matrices and hash evidence tokens.
  - `AST architecture guard` checks architecture guard against reintroduced source rewrites behind the report.

## Regression Guardrails

Scope vector: operation `create`, domain `architecture`, paths
`_condamad/architecture`, `_condamad/audits` and `_story_briefs`, contracts
`architecture-report`, `llm-input` and `no-app-change`.

| Guardrail | Local invariant | Evidence |
|---|---|---|
| Registry gap | No exact architecture-transition guardrail was returned by the scoped resolver. | `python` resolver output. |
| RG-041 non-applicable | Entitlement documentation is outside this architecture transition scope. | Manual check: no entitlement docs. |
| RG-047 non-applicable | Frontend inline style rules are outside this architecture-only scope. | Manual check: no `frontend` edits. |
| RG-052 non-applicable | Frontend CSS namespace rules are outside this architecture-only scope. | Manual check: no style edits. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Architecture synthesis | `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/00-architecture.md` | Keep target flow and decisions. |
| Evidence map | `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/01-evidence-map.md` | Map audits to decisions. |
| Target contract | `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/02-target-contract.md` | Keep conceptual LLM input contract. |
| Transition plan | `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/03-legacy-transition.md` | Keep confinement plan. |
| Story candidates | `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/04-story-candidates.md` | Keep prioritized refactor list. |
| Risk register | `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/05-risk-register.md` | Keep risks and mitigations. |
| Validation output | `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/validation-output.md` | Keep command output. |
| Review output | `_condamad/stories/CS-328-architecture-transition-calculs-interpretations-injection-llm/generated/11-code-review.md` | Keep automatic review output. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this architecture-only story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/00-architecture.md` - architecture target.
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/01-evidence-map.md` - audit-to-decision map.
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/02-target-contract.md` - conceptual injection contract.
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/03-legacy-transition.md` - confinement plan.
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/04-story-candidates.md` - refactor story candidates.
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/05-risk-register.md` - risk register.
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/validation-output.md` - validation output.

Likely tests:

- No new tests are expected because the story is architecture-only.
- Existing validation may run `git status --short -- _condamad _story_briefs backend/app backend/tests`.

Files not expected to change:

- `backend/app/**` - out of scope; application runtime and service code remain unchanged.
- `backend/tests/**` - out of scope; tests are read or checked only.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no schema or migration work is touched.
- `_condamad/stories/regression-guardrails.md` - out of scope for normal story implementation.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1:
  `Test-Path .\_condamad\audits\calculs-interpretations-vers-llm`
  puis `Test-Path .\_condamad\audits\pipeline-prompt-llm-natal`.
- VC2:
  `Test-Path .\_condamad\audits\projections-interpretatives-llm-input-readiness`
  puis `Test-Path .\_condamad\audits\configuration-prompts-placeholders-input-schema`.
- VC3:
  `rg -n "CS-324|CS-325|CS-326|CS-327" _condamad/architecture/calculs-interpretations-injection-llm`.
- VC4:
  `rg -n "CalculationGraph|ChartObjectRuntimeData|ChartInterpretationInput|prompt runtime" _condamad/architecture/calculs-interpretations-injection-llm`.
- VC5:
  `rg -n "chart_json|natal_data|astro_context|evidence_catalog|AINarrativeInputContract" _condamad/architecture/calculs-interpretations-injection-llm`.
- VC6:
  `rg -n "projection_hash|llm_input_hash|evidence_refs|transition-condition" _condamad/architecture/calculs-interpretations-injection-llm`.
- VC7:
  `python -c "from pathlib import Path; root=Path('_condamad/architecture/calculs-interpretations-injection-llm'); assert root.exists()"`
  then use `python` to assert the six required files exist in the latest timestamp folder.
- VC8: `git status --short -- _condamad _story_briefs backend/app backend/tests`
- VC9: `git status --short -- frontend/src backend/migrations`

## Regression Risks

- The report may promote `client_interpretation_projection_v1` as the internal
  LLM input without proving lossless fact and evidence coverage.
- The report may treat prompt placeholders as a source of truth instead of a
  rendering surface.
- The report may merge product shaping and fact blocks in a way that weakens
  `projection_hash`, `llm_input_hash` or `evidence_refs`.
- The report may propose refactor candidates that silently require prompt or
  provider changes.
- The report may proceed before CS-324 to CS-327 audit artifacts are complete.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the repository Python venv before every Python command.
- Keep architecture citations short and path-based; do not paste long source blocks.
- Stop and record a blocker if any required audit deliverable from CS-324 to CS-327 is missing.
- Keep `backend/app`, `backend/tests`, `frontend/src` and `backend/migrations` unchanged.
- Use one timestamped architecture folder for all deliverables.
- Include the three mandatory matrices exactly once in the target deliverables.

## References

- `_story_briefs/cs-328-architecture-transition-calculs-interpretations-injection-llm.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-324-audit-calculs-interpretations-llm/00-story.md`
- `_condamad/stories/CS-325-audit-pipeline-prompt-llm-natal/00-story.md`
- `_condamad/stories/CS-326-audit-projections-interpretatives-llm-input-readiness/00-story.md`
- `_condamad/stories/CS-327-audit-configuration-prompts-placeholders-input-schema/00-story.md`
- `_story_briefs/cs-245-archi-canonical-astrology-runtime-transition.md`
- `_story_briefs/cs-254-ai-scoring-narrative-input-contract.md`
- `_story_briefs/cs-256-define-structured-facts-v1-stable-hashable-fact-projection.md`
- `_story_briefs/cs-258-define-client-interpretation-projection-v1-by-plan.md`
- `_story_briefs/cs-259-define-narrative-answer-audit-v1.md`
- `_story_briefs/cs-287-implement-client-interpretation-projection-v1-builder-by-plan.md`
- `_story_briefs/cs-291-implement-generic-projection-endpoint.md`
