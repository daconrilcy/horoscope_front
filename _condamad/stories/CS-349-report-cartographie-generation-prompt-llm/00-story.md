# Story CS-349 report-cartographie-generation-prompt-llm: Report Cartographie Generation Prompt LLM
Status: ready-to-dev

## Trigger / Source

Brief direct source:
`_story_briefs/cs-349-report-cartographie-generation-prompt-llm.md`.

Problem statement: les briefs, audits, l'architecture et la documentation de
cartographie de generation des prompts LLM doivent etre consolides dans un
rapport unique evidence-based.

Source stakes:

- User impact: disposer d'une chaine de preuve lisible entre demande initiale,
  briefs, audits, architecture, documentation, validation et risques.
- Technical risk: produire une synthese narrative sans preuves concretes ou
  lisser les contradictions entre audits, architecture et documentation.
- Closure expectation: creer un rapport `.md` unique sous `_condamad/reports`
  avec claims ancres, gaps explicites, validations et prochaines actions.
- Forbidden regression: aucune modification de code applicatif, prompts,
  runtime LLM, endpoints, frontend, DB, migrations ou configuration.

Source-alignment evidence: objective, target state, ACs, tasks, validation plan,
non-goals and guardrails map to the brief's report-only scope, mandatory
sources, expected report sections and evidence gap policy.

## Objective

Produire le rapport de synthese final de la cartographie de generation des
prompts LLM en utilisant le skill `condamad-delivery-report`.

Le rapport doit prouver la chaine:
`demande initiale -> briefs -> audits -> architecture -> documentation finale
attendue -> validation -> risques residuels`.

## Target State

Un dossier de rapport timestamp est cree sous:
`_condamad/reports/prompt-generation-cartography/2026-05-27-0000/`.

Il contient:

- `report-prompt-generation-cartography.md` avec les sections obligatoires du
  brief.
- `evidence-sources.md` avec les sources lues, les chemins de preuve, les gaps
  et les contradictions.
- `validation-output.md` avec les commandes executees et leur resultat.

Le rapport distingue clairement audit, architecture, documentation et
implementation.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-349-report-cartographie-generation-prompt-llm.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign the story number.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `.agents/skills/condamad-delivery-report/SKILL.md` - required delivery report skill path exists.
- Evidence 5: `_condamad/stories/CS-343-prompt-generation-surface-inventory/00-story.md` - source audit story exists.
- Evidence 6: `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/00-story.md` - source audit story exists.
- Evidence 7: `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/00-story.md` - source audit story exists.
- Evidence 8: `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/00-story.md` - source audit story exists.
- Evidence 9: `_condamad/stories/CS-347-audit-output-validation-persistence-observabilite-prompt-llm/00-story.md` - source audit story exists.
- Evidence 10: `_condamad/stories/CS-348-architecture-cartographie-generation-prompt-llm/00-story.md` - source architecture story exists.
- Evidence 11: `_story_briefs/cs-350-documentation-cartographie-generation-prompt-llm-mermaid.md` - documentation brief exists.
- Evidence 12: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver and targeted ID lookup.
- Repository structure alert: `_condamad/audits/prompt-generation-cartography` is absent in this workspace.
- Repository structure alert: `_condamad/architecture/prompt-generation-cartography` is absent in this workspace.
- Repository structure alert: `_condamad/docs/prompt-generation-cartography` is absent in this workspace.
- Repository structure alert: implementation must record `Evidence gap` for unavailable CS-343 to CS-350 deliverables.

## Domain Boundary

- Domain: delivery-report
- In scope:
  - Loading and applying `.agents/skills/condamad-delivery-report/SKILL.md`.
  - Reading briefs CS-343 to CS-350.
  - Reading available audits CS-343 to CS-347.
  - Reading available architecture CS-348.
  - Reading CS-350 documentation output or recording its absence as a dependency.
  - Creating the timestamped report folder under `_condamad/reports`.
  - Listing residual risks, evidence gaps, contradictions and next actions.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling,
    migrations, prompt edits, LLM runtime edits, public endpoints and app code.
- Explicit non-goals:
  - No implementation code change.
  - No audit rewrite.
  - No architecture rewrite.
  - No Mermaid documentation production for CS-350.
  - No real LLM call.

Named brief primitives in scope:

- `condamad-delivery-report`
- `CS-343`
- `CS-344`
- `CS-345`
- `CS-346`
- `CS-347`
- `CS-348`
- `CS-350`
- `_condamad/reports/prompt-generation-cartography`
- `report-prompt-generation-cartography.md`
- `Evidence gap`
- `residual risk`
- `next actions`

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this delivery report contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Create only report and story evidence artifacts.
  - Keep backend application files unchanged.
  - Keep backend test files unchanged.
  - Keep frontend files unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the report cannot distinguish audit, architecture, documentation and implementation from available sources.
- Additional validation rules:
  - `AST guard` or bounded `rg` evidence must prove no application source was modified.
  - `python` path checks must prove the report, source evidence file and validation output exist.
  - `rg` evidence must prove the report contains source story IDs, validation terms, gaps, risks and next actions.
  - The report must mark missing proof as `Evidence gap` instead of smoothing over absent deliverables.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Source deliverables and bounded artifact rereads prove the report base. |
| Baseline Snapshot | yes | Source availability before conclusions must be persisted. |
| Ownership Routing | yes | Report artifacts must stay under `_condamad/reports` and story evidence. |
| Allowlist Exception | no | No allowlist handling is authorized for this report-only story. |
| Contract Shape | yes | The report has exact sections, source map, gaps and next actions. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | App, prompt, frontend, DB and migration surfaces must stay unchanged. |
| Persistent Evidence | yes | Report, source evidence and validation output must persist for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The final report exists. | Evidence profile: baseline_before_after_diff; `python` checks `report-prompt-generation-cartography.md`. |
| AC2 | CS-343 through CS-350 are mapped. | Evidence profile: baseline_before_after_diff; `rg -n "CS-343|CS-348|CS-350"` in report folder. |
| AC3 | Important claims have anchors. | Evidence profile: json_contract_shape; `rg -n "Evidence path|Source|Evidence gap"` in report folder. |
| AC4 | Missing proof is labeled. | Evidence profile: json_contract_shape; `rg -n "Evidence gap"` in report folder. |
| AC5 | Contradictions are visible. | Evidence profile: ast_architecture_guard; `rg -n "contradiction|Gaps"` in report folder. |
| AC6 | Validation evidence is included. | Evidence profile: baseline_before_after_diff; `rg -n "validation|Validation evidence"` in report folder. |
| AC7 | Residual risks are included. | Evidence profile: json_contract_shape; `rg -n "residual risk|Risques residuels"` in report folder. |
| AC8 | Application code remains unchanged. | Evidence profile: repo_wide_negative_scan; `python` checks `git status --short -- backend/app backend/tests frontend/src`. |
| AC9 | Source evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks `evidence-sources.md` and `validation-output.md`. |

## Implementation Tasks

- [ ] Task 1: Load `condamad-delivery-report` and record the skill path in `evidence-sources.md`. (AC: AC1, AC9)
- [ ] Task 2: Read briefs CS-343 to CS-350 and map each brief to the final report. (AC: AC2, AC3)
- [ ] Task 3: Read available CS-343 to CS-347 audit deliverables and record unavailable paths as `Evidence gap`. (AC: AC3, AC4)
- [ ] Task 4: Read available CS-348 architecture deliverables and record unavailable paths as `Evidence gap`. (AC: AC3, AC4)
- [ ] Task 5: Read CS-350 documentation output or record its absence as dependency evidence. (AC: AC2, AC4)
- [ ] Task 6: Write `report-prompt-generation-cartography.md` with source map, ACs, gaps, risks and next actions. (AC: AC1, AC5, AC7)
- [ ] Task 7: Run validation scans and persist command output in `validation-output.md`. (AC: AC6, AC9)
- [ ] Task 8: Prove app surfaces are unchanged through a bounded status guard. (AC: AC8)

## Files to Inspect First

- `.agents/skills/condamad-delivery-report/SKILL.md`
- `_story_briefs/cs-343-audit-inventaire-surfaces-generation-prompt-llm.md`
- `_story_briefs/cs-344-audit-configuration-assemblies-placeholders-prompts-llm.md`
- `_story_briefs/cs-345-audit-runtime-gateway-handoff-provider-prompt-llm.md`
- `_story_briefs/cs-346-audit-inputs-astrologiques-natals-prompt-llm.md`
- `_story_briefs/cs-347-audit-validation-output-persistence-observabilite-prompt-llm.md`
- `_story_briefs/cs-348-architecture-cartographie-generation-prompt-llm.md`
- `_story_briefs/cs-349-report-cartographie-generation-prompt-llm.md`
- `_story_briefs/cs-350-documentation-cartographie-generation-prompt-llm-mermaid.md`
- `_condamad/audits/prompt-generation-cartography/**` - expected implementation-created path when audits exist.
- `_condamad/architecture/prompt-generation-cartography/**` - expected implementation-created path when architecture exists.
- `_condamad/docs/prompt-generation-cartography/**` - expected implementation-created path when documentation exists.

## Runtime Source of Truth

- Primary source of truth:
  - Completed deliverables from CS-343, CS-344, CS-345, CS-346, CS-347,
    CS-348 and CS-350.
  - Required briefs CS-343 to CS-350.
  - `condamad-delivery-report` skill instructions for report format.
  - `AST guard` or bounded `rg` scans over report artifacts.
- Secondary evidence:
  - `git status --short -- _condamad _story_briefs backend/app backend/tests frontend/src`.
  - `evidence-sources.md` citations with source path, availability and claim mapping.
- Static scans alone are not sufficient for this story because:
  - The report must prove its conclusions from the source deliverables and
    explicitly label unavailable evidence.

## Contract Shape

- Contract type:
  - Report artifact set and delivery synthesis contract.
- Fields:
  - `Story`: CS identifier and source brief.
  - `Artifact`: audit, architecture, documentation or report path.
  - `Claim`: important statement included in the report.
  - `Evidence path`: concrete source backing the claim.
  - `Gap`: missing proof or contradiction.
  - `Validation evidence`: command or artifact proving the report claim.
  - `Next action`: follow-up story, dependency or user decision.
- Required fields:
  - `Story`
  - `Artifact`
  - `Claim`
  - `Evidence path`
  - `Gap`
  - `Validation evidence`
  - `Next action`
- Optional fields:
  - none
- Serialization names:
  - Matrix headings are emitted exactly as listed in this contract shape.
- Required files:
  - `report-prompt-generation-cartography.md`
  - `evidence-sources.md`
  - `validation-output.md`
- Required report sections:
  - `Trigger initial`
  - `Map des stories et briefs`
  - `Acceptance criteria par story`
  - `Evidence paths`
  - `Validation evidence`
  - `Gaps ou contradictions`
  - `Risques residuels`
  - `Next actions`
- Status codes:
  - none; no API route is created or changed.
- Frontend type impact:
  - none; no frontend generated client or UI surface is in scope.
- Generated contract impact:
  - none; no OpenAPI or generated manifest change is in scope.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `evidence-sources.md` records source availability for CS-343 to CS-350.
- Comparison after implementation:
  - `report-prompt-generation-cartography.md` contains final conclusions,
    validation evidence, gaps, residual risks and next actions.
- Expected invariant:
  - The only intended repository delta is the report artifact directory plus
    story execution evidence.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Delivery report | `_condamad/reports/prompt-generation-cartography/2026-05-27-0000/**` | Backend app or frontend code |
| Source evidence | `evidence-sources.md` in the report folder | Application source files |
| Validation output | `validation-output.md` in the report folder | App tests or CI config |
| Automatic review handoff | `_condamad/stories/CS-349-report-cartographie-generation-prompt-llm/generated/**` | Report source matrix |

## Mandatory Reuse / DRY Constraints

- Reuse CS-343 to CS-350 briefs and deliverables as the canonical evidence base.
- Keep one final synthesis report and one source evidence file.
- Reference source paths instead of duplicating full audit or architecture blocks.
- Use one vocabulary for `audit`, `architecture`, `documentation`,
  `implementation`, `Evidence gap`, `residual risk` and `next actions`.
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
  - `_condamad/reports/prompt-generation-cartography/**`
- Required guard:
  - `python` checks that `git status --short -- backend/app backend/tests frontend/src backend/migrations` returns no changed app surfaces.
  - `rg` checks the report contains source IDs, evidence gap markers, validation terms and residual risk terms.
  - `AST guard` checks report generation does not introduce prompt, runtime or endpoint changes.

## Regression Guardrails

Scope vector: operation `create`, domain `delivery-report`, paths
`_condamad/reports`, `_condamad/stories`, `_condamad/audits/prompt-generation-cartography`,
`_condamad/architecture/prompt-generation-cartography`, `_condamad/docs/prompt-generation-cartography`,
contracts `report-artifact`, `persistent-evidence` and `no-app-change`.

| Guardrail | Local invariant | Evidence |
|---|---|---|
| Registry gap | No exact delivery-report guardrail was returned by the scoped resolver. | `python` resolver output. |
| RG-047 non-applicable | Frontend TSX inline styles are outside this report-only scope. | Manual check: no frontend edits. |
| RG-052 non-applicable | Frontend CSS namespace migration is outside this report-only scope. | Manual check: no CSS edits. |
| RG-041 non-applicable | Entitlement documentation is outside this prompt cartography report. | Manual check: no entitlement docs. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Final report | `_condamad/reports/prompt-generation-cartography/2026-05-27-0000/report-prompt-generation-cartography.md` | Keep synthesis and closure map. |
| Source evidence | `_condamad/reports/prompt-generation-cartography/2026-05-27-0000/evidence-sources.md` | Keep source citations and gaps. |
| Validation output | `_condamad/reports/prompt-generation-cartography/2026-05-27-0000/validation-output.md` | Keep command output. |
| Review output | `_condamad/stories/CS-349-report-cartographie-generation-prompt-llm/generated/11-code-review.md` | Keep automatic review output. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this report-only story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/reports/prompt-generation-cartography/2026-05-27-0000/report-prompt-generation-cartography.md` - final report.
- `_condamad/reports/prompt-generation-cartography/2026-05-27-0000/evidence-sources.md` - source citations and gaps.
- `_condamad/reports/prompt-generation-cartography/2026-05-27-0000/validation-output.md` - validation output.

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
  `python -c "from pathlib import Path; p=Path('_condamad/reports/prompt-generation-cartography/2026-05-27-0000/report-prompt-generation-cartography.md'); assert p.exists()"`
- VC2:
- VC2a:
  `python -c "from pathlib import Path; p=Path('_condamad/reports/prompt-generation-cartography/2026-05-27-0000/evidence-sources.md'); assert p.exists()"`
- VC2b:
  `python -c "from pathlib import Path; p=Path('_condamad/reports/prompt-generation-cartography/2026-05-27-0000/validation-output.md'); assert p.exists()"`
- VC3:
  `rg -n "Evidence gap|residual risk|validation|CS-343|CS-348|CS-350" _condamad/reports/prompt-generation-cartography`
- VC4:
  `rg -n "report-prompt-generation-cartography" _condamad`
- VC5:
  `rg -n "Trigger initial|Map des stories et briefs|Acceptance criteria par story|Evidence paths" _condamad/reports/prompt-generation-cartography`
- VC6:
  `rg -n "Gaps ou contradictions|Risques residuels|Next actions|implementation" _condamad/reports/prompt-generation-cartography`
- VC7:
  `git status --short -- backend/app backend/tests frontend/src backend/migrations`
- VC8:
  `git status --short -- _condamad _story_briefs backend/app backend/tests`

## Regression Risks

- The report may summarize without concrete source anchors.
- The report may hide unavailable deliverables instead of writing `Evidence gap`.
- The report may blur audit, architecture, documentation and implementation.
- The report may imply application changes that are outside this story.
- The report may omit CS-350 documentation status and create false closure.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the repository Python venv before every Python command.
- Use `condamad-delivery-report` before writing the final report.
- Keep report citations short and path-based; do not paste long source blocks.
- Stop and record a blocker if the report cannot distinguish the required artifact types.
- Keep `backend/app`, `backend/tests`, `frontend/src` and `backend/migrations` unchanged.
- Do not execute real LLM calls.

## References

- `_story_briefs/cs-349-report-cartographie-generation-prompt-llm.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `.agents/skills/condamad-delivery-report/SKILL.md`
- `_condamad/stories/regression-guardrails.md`
- `_story_briefs/cs-343-audit-inventaire-surfaces-generation-prompt-llm.md`
- `_story_briefs/cs-344-audit-configuration-assemblies-placeholders-prompts-llm.md`
- `_story_briefs/cs-345-audit-runtime-gateway-handoff-provider-prompt-llm.md`
- `_story_briefs/cs-346-audit-inputs-astrologiques-natals-prompt-llm.md`
- `_story_briefs/cs-347-audit-validation-output-persistence-observabilite-prompt-llm.md`
- `_story_briefs/cs-348-architecture-cartographie-generation-prompt-llm.md`
- `_story_briefs/cs-350-documentation-cartographie-generation-prompt-llm-mermaid.md`
