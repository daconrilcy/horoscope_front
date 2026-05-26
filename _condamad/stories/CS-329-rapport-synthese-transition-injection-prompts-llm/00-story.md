# Story CS-329 rapport-synthese-transition-injection-prompts-llm: Rapport Synthese Transition Injection Prompts LLM
Status: ready-to-dev

## Trigger / Source

Brief direct source:
`_story_briefs/cs-329-rapport-synthese-transition-injection-prompts-llm.md`.

Problem statement: les audits CS-324 a CS-327 et l'architecture CS-328 doivent
etre consolides dans un rapport final actionnable pour preparer les refactors
de transition vers une injection structuree dans les prompts LLM.

Source stakes:

- User impact: eviter des futures stories fondees sur une synthese trop
  generale ou non prouvee.
- Technical risk: melanger surfaces historiques, refonte recente, donnees
  disponibles, contrat cible et sequence de refactor.
- Closure expectation: produire un rapport `.md` unique, cite, exploitable et
  directement utilisable pour rediger les prochains briefs de refactor.
- Forbidden regression: aucune modification applicative, prompt, generateur
  LLM, endpoint public, securite, CI, astrologue ou appel LLM reel.

Source-alignment evidence: the objective, target state, ACs, tasks, evidence,
validation plan, non-goals and guardrails map back to the source brief's
required report structure, required questions, source deliverables and
no-application-change constraint.

## Objective

Produire le rapport de synthese final qui transforme les livrables CS-324,
CS-325, CS-326, CS-327 et CS-328 en base de travail pour les futures stories de
refactor.

Le rapport doit diagnostiquer la transition calculs astrologiques et
interpretations pre-narratives vers injection structuree dans les prompts LLM,
puis proposer un contrat cible, une strategie de retrait des surfaces
historiques et une roadmap de stories candidates.

## Target State

Un dossier de rapport timestamp est cree sous:
`_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/`.

Il contient:

- `rapport-transition-injection-prompts-llm.md` avec les douze sections
  obligatoires du brief.
- `evidence-sources.md` avec les sources CS-324 a CS-328 lues, les citations
  courtes et les points contradictoires releves.
- `validation-output.md` avec les commandes executees et leur resultat.

Le rapport final contient une section `Stories de refactor recommandees` avec
au minimum les six familles de stories demandees par le brief.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-329-rapport-synthese-transition-injection-prompts-llm.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign the story number.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `_condamad/stories/CS-324-audit-calculs-interpretations-llm/00-story.md` - source audit story inspected.
- Evidence 5: `_condamad/stories/CS-325-audit-pipeline-prompt-llm-natal/00-story.md` - source audit story inspected.
- Evidence 6: `_condamad/stories/CS-326-audit-projections-interpretatives-llm-input-readiness/00-story.md` - source audit story inspected.
- Evidence 7: `_condamad/stories/CS-327-audit-configuration-prompts-placeholders-input-schema/00-story.md` - source audit story inspected.
- Evidence 8: `_condamad/stories/CS-328-architecture-transition-calculs-interpretations-injection-llm/00-story.md` - source architecture story inspected.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver and targeted ID lookup.
- Repository structure alert: completed output folders for CS-324 to CS-328 may be absent until those stories are implemented.
- Repository structure alert: implementation must stop and record a blocker if a required CS-324 to CS-328 deliverable is unavailable.

## Domain Boundary

- Domain: architecture-report
- In scope:
  - Consolidation of CS-324, CS-325, CS-326, CS-327 and CS-328 deliverables.
  - Creation of the timestamped report folder under `_condamad/reports`.
  - Synthesis of current LLM injection state, historical surfaces, recent
    refonte surfaces and unused available data.
  - Recommendation of target architecture, injection contract and refactor
    sequence.
  - Identification of remaining product or technical decisions.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling,
    migrations, prompt edits, LLM generator edits, public endpoints and app
    code.
- Explicit non-goals:
  - No implementation of refactors.
  - No prompt modification.
  - No LLM generator modification.
  - No public endpoint modification.
  - No security, CI or astrologer domain modification.
  - No real LLM call.

Named brief primitives in scope:

- `rapport-transition-injection-prompts-llm.md`
- `calculs astrologiques`
- `interpretations pre-narratives`
- `injection structuree`
- `prompts LLM`
- `chart_json`
- `structured_facts_v1`
- `AINarrativeInput`
- `NatalExecutionInput`
- `ExecutionContext`
- `legacy`
- `recent-refonte`
- `contrat cible`
- `Stories de refactor recommandees`

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this architecture report and synthesis contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Create only report and story evidence artifacts.
  - Keep backend application files unchanged.
  - Keep backend test files unchanged.
  - Keep frontend files unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: required CS-324 to CS-328 deliverables are unavailable during implementation.
- Additional validation rules:
  - `AST guard` or bounded `rg` evidence must prove no application source was modified.
  - `python` path checks must prove the report, source evidence file and validation output exist.
  - `rg` evidence must prove the report contains the mandatory sections, questions and refactor story families.
  - The report must separate synthesis conclusions from future implementation work.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Source deliverables and optional code-owner rereads prove the synthesis base. |
| Baseline Snapshot | yes | The evidence file records source availability before final report conclusions. |
| Ownership Routing | yes | Report artifacts must stay under `_condamad/reports` and not app owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this report-only story. |
| Contract Shape | yes | The report has exact required sections, questions and refactor families. |
| Batch Migration | no | No multi-file conversion is in scope. |
| Reintroduction Guard | yes | App, prompt, endpoint, frontend, DB and migration surfaces must stay unchanged. |
| Persistent Evidence | yes | Report, source evidence and validation output must persist for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The final report exists. | Evidence profile: baseline_before_after_diff; `python` checks `rapport-transition-injection-prompts-llm.md`. |
| AC2 | CS-324 to CS-328 are cited. | Evidence profile: baseline_before_after_diff; `rg -n "CS-324|CS-325|CS-326|CS-327|CS-328"` in report folder. |
| AC3 | Mandatory report sections are present. | Evidence profile: json_contract_shape; `rg` checks section names in the final report. |
| AC4 | The transition diagnostic is answered. | Evidence profile: ast_architecture_guard; `rg` checks `diagnostic final` and `contrat cible`. |
| AC5 | Injection data mapping is present. | Evidence profile: json_contract_shape; `rg` checks `chart_json`, `structured_facts_v1` and `AINarrativeInput`. |
| AC6 | Refactor stories are recommended. | Evidence profile: batch_migration_mapping; `rg` checks `Stories de refactor recommandees`. |
| AC7 | Application code remains unchanged. | Evidence profile: repo_wide_negative_scan; `python` checks `git status --short -- backend/app backend/tests frontend/src`. |
| AC8 | Source evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks `evidence-sources.md` and `validation-output.md`. |
| AC9 | Critical source rereads are bounded. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks backend paths in `evidence-sources.md`. |

## Implementation Tasks

- [ ] Task 1: Verify the availability of CS-324 to CS-328 deliverables and record paths in `evidence-sources.md`. (AC: AC2, AC8)
- [ ] Task 2: Read the available CS-324 to CS-328 deliverables and cite each source in the final report. (AC: AC2, AC3)
- [ ] Task 3: Reread the critical backend files only to resolve contradictions found in the source deliverables. (AC: AC5, AC9)
- [ ] Task 4: Write the twelve mandatory report sections in `rapport-transition-injection-prompts-llm.md`. (AC: AC1, AC3, AC4)
- [ ] Task 5: Answer the seven mandatory questions with evidence-backed conclusions. (AC: AC4, AC5)
- [ ] Task 6: Write the target injection contract and withdrawal strategy for historical surfaces. (AC: AC4, AC5)
- [ ] Task 7: Add the six required refactor story families under `Stories de refactor recommandees`. (AC: AC6)
- [ ] Task 8: Run validation commands and persist command output in `validation-output.md`. (AC: AC7, AC8)

## Files to Inspect First

- `_story_briefs/cs-329-rapport-synthese-transition-injection-prompts-llm.md`
- `_condamad/stories/CS-324-audit-calculs-interpretations-llm/00-story.md`
- `_condamad/stories/CS-325-audit-pipeline-prompt-llm-natal/00-story.md`
- `_condamad/stories/CS-326-audit-projections-interpretatives-llm-input-readiness/00-story.md`
- `_condamad/stories/CS-327-audit-configuration-prompts-placeholders-input-schema/00-story.md`
- `_condamad/stories/CS-328-architecture-transition-calculs-interpretations-injection-llm/00-story.md`
- `_condamad/audits/calculs-interpretations-vers-llm/**`
- `_condamad/audits/pipeline-prompt-llm-natal/**`
- `_condamad/audits/projections-interpretatives-llm-input-readiness/**`
- `_condamad/audits/configuration-prompts-placeholders-input-schema/**`
- `_condamad/architecture/calculs-interpretations-injection-llm/**`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/services/chart/json_builder.py`

## Runtime Source of Truth

- Primary source of truth:
  - Completed deliverables from CS-324, CS-325, CS-326, CS-327 and CS-328.
  - Critical backend source rereads only for contradictions in source
    deliverables.
  - `AST guard` or bounded `rg` scans over report artifacts.
- Secondary evidence:
  - `git status --short -- _condamad _story_briefs backend/app backend/tests frontend/src`.
  - `evidence-sources.md` citations with source path and conclusion mapping.
- Static scans alone are not sufficient for this story because:
  - The report must prove its conclusions from prior deliverables before
    recommending refactor stories.

## Contract Shape

- Contract type:
  - Report artifact set and synthesis contract.
- Fields:
  - `Section`: mandatory report section name.
  - `Source`: CS-324 to CS-328 source deliverable or bounded code reread.
  - `Conclusion`: evidence-backed synthesis finding.
  - `Action`: recommended refactor, decision or no-change result.
  - `Validation attendue`: deterministic check for future story or report
    completeness.
- Required fields:
  - `Section`
  - `Source`
  - `Conclusion`
  - `Action`
  - `Validation attendue`
- Optional fields:
  - none
- Serialization names:
  - Matrix headings are emitted exactly as listed in this contract shape.
- Required files:
  - `rapport-transition-injection-prompts-llm.md`
  - `evidence-sources.md`
  - `validation-output.md`
- Required report sections:
  - `Executive summary`
  - `Etat actuel de l'injection LLM`
  - `Carte des surfaces legacy`
  - `Carte des surfaces issues de la refonte recente`
  - `Carte des donnees disponibles mais non exploitees`
  - `Architecture cible recommandee`
  - `Contrat cible d'injection LLM recommande`
  - `Strategie de retrait du legacy`
  - `Priorisation des refactors`
  - `Liste des futures stories recommandees`
  - `Risques et limites`
  - `Annexes de preuves`
- Required refactor story families:
  - Definition du contrat cible d'injection.
  - Branchement du contrat cible dans `NatalExecutionInput` et `ExecutionContext`.
  - Migration des use cases natals hors `chart_json`.
  - Preservation hash, audit et evidence.
  - Tests de non-invention et de non-regression.
  - Retrait progressif des surfaces historiques.
- Status codes:
  - none; no API route is created or changed.
- Frontend type impact:
  - none; no frontend generated client or UI surface is in scope.
- Generated contract impact:
  - none; no OpenAPI or generated manifest change is in scope.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `evidence-sources.md` records CS-324 to CS-328 source availability and any
    bounded backend rereads.
- Comparison after implementation:
  - `rapport-transition-injection-prompts-llm.md` contains final conclusions,
    roadmap and source-backed future story recommendations.
- Expected invariant:
  - The only intended repository delta is the report artifact directory plus
    story execution evidence.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Audit synthesis evidence | CS-324 to CS-327 completed deliverables | Backend app or prompt files |
| Architecture synthesis evidence | CS-328 completed architecture deliverables | Backend app or frontend code |
| Contradiction reread evidence | Critical backend files named in the brief | Report conclusions without citation |
| Report deliverables | `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/**` | Backend app or tests |

## Mandatory Reuse / DRY Constraints

- Reuse the CS-324 to CS-328 deliverables as the canonical evidence base.
- Keep one final synthesis report and one source evidence file.
- Reference report sections instead of duplicating full matrices across files.
- Use one classification vocabulary for `legacy`, `recent-refonte`, `a
  conserver`, `a refactoriser` and `a supprimer`.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy route, prompt, provider, projection or payload path may be added.
- No compatibility route, prompt, provider, projection or payload path may be added.
- No fallback route, prompt, provider, projection or payload path may be added.
- Do not move application logic into report artifacts.
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
  - `backend/migrations/**`
  - `_condamad/reports/calculs-interpretations-vers-prompts-llm/**`
- Required guard:
  - `python` checks that `git status --short -- backend/app backend/tests frontend/src backend/migrations` returns no changed app surfaces.
  - `rg` checks the report contains the required section names, source IDs and refactor story families.
  - `AST guard` checks report generation does not introduce prompt, runtime or endpoint changes.

## Regression Guardrails

Scope vector: operation `create`, domain `architecture-report`, paths
`_condamad/reports`, `_condamad/stories`, `backend/app/services/llm_generation/natal`,
`backend/app/domain/llm/runtime`, `backend/app/domain/astrology/interpretation`,
contracts `report-artifact`, `persistent-evidence` and `no-app-change`.

| Guardrail | Local invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend ownership must not drift into report or API files. | `python` status guard; owner `rg`. |
| Registry gap | No exact synthesis-report guardrail was returned by the scoped resolver. | `python` resolver output. |
| RG-041 non-applicable | Entitlement documentation is outside this synthesis report scope. | Manual check: no entitlement docs. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Final report | `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md` | Keep the final synthesis and roadmap. |
| Source evidence | `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/evidence-sources.md` | Keep source citations and rereads. |
| Validation output | `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/validation-output.md` | Keep command output. |
| Review output | `_condamad/stories/CS-329-rapport-synthese-transition-injection-prompts-llm/generated/11-code-review.md` | Keep automatic review output. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this report-only story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md` - final report.
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/evidence-sources.md` - source citations.
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/validation-output.md` - validation output.

Likely tests:

- No new tests are expected because the story is report-only.
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
  `python -c "from pathlib import Path; root=Path('_condamad/reports/calculs-interpretations-vers-prompts-llm'); assert root.exists()"`
- VC2:
  From `_condamad/reports/calculs-interpretations-vers-prompts-llm`, run
  `python -c "from pathlib import Path; assert Path('2026-05-26-0000/rapport-transition-injection-prompts-llm.md').exists()"`
- VC3:
  `rg -n "CS-324|CS-325|CS-326|CS-327|CS-328" _condamad/reports/calculs-interpretations-vers-prompts-llm`
- VC4:
  `rg -n "legacy|recent-refonte|contrat cible|chart_json|structured_facts_v1" _condamad/reports/calculs-interpretations-vers-prompts-llm`
- VC5:
  `rg -n "AINarrativeInput|NatalExecutionInput|ExecutionContext|Stories de refactor recommandees" _condamad/reports/calculs-interpretations-vers-prompts-llm`
- VC6:
  `rg -n "Executive summary|Etat actuel de l'injection LLM|Annexes de preuves" _condamad/reports/calculs-interpretations-vers-prompts-llm`
- VC7:
  From `_condamad/reports/calculs-interpretations-vers-prompts-llm`, run
  `python -c "from pathlib import Path; r=Path('2026-05-26-0000'); assert (r/'evidence-sources.md').exists() and (r/'validation-output.md').exists()"`
- VC8:
  `git status --short -- backend/app backend/tests frontend/src backend/migrations`
- VC9: `git status --short -- _condamad _story_briefs backend/app backend/tests`

## Regression Risks

- The report may summarize too broadly and fail to identify concrete refactor
  stories.
- The report may promote a product projection as internal LLM input without
  preserving facts, evidence and limits.
- The report may hide source deliverable gaps instead of recording blockers.
- The report may suggest changes that actually require prompt, provider,
  endpoint or application implementation in this story.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the repository Python venv before every Python command.
- Keep report citations short and path-based; do not paste long source blocks.
- Stop and record a blocker if required CS-324 to CS-328 deliverables are missing.
- Keep `backend/app`, `backend/tests`, `frontend/src` and `backend/migrations` unchanged.
- Use one timestamped report folder for all deliverables.
- Do not execute real LLM calls.

## References

- `_story_briefs/cs-329-rapport-synthese-transition-injection-prompts-llm.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-324-audit-calculs-interpretations-llm/00-story.md`
- `_condamad/stories/CS-325-audit-pipeline-prompt-llm-natal/00-story.md`
- `_condamad/stories/CS-326-audit-projections-interpretatives-llm-input-readiness/00-story.md`
- `_condamad/stories/CS-327-audit-configuration-prompts-placeholders-input-schema/00-story.md`
- `_condamad/stories/CS-328-architecture-transition-calculs-interpretations-injection-llm/00-story.md`
