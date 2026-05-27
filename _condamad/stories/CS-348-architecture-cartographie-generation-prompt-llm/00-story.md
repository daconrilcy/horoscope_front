# Story CS-348 architecture-cartographie-generation-prompt-llm: Architecture Cartographie Generation Prompt LLM
Status: ready-to-dev

## Trigger / Source

Brief direct source:
`_story_briefs/cs-348-architecture-cartographie-generation-prompt-llm.md`.

Problem statement: les audits CS-343 a CS-347 doivent etre synthetises en une
architecture produit et technique de reference pour la generation des prompts
LLM, sans refaire les audits ni modifier le code applicatif.

Source stakes:

- User impact: eviter des futures stories de prompt generation fondees sur des
  owners, registres ou frontieres non prouves.
- Technical risk: melanger prompt-visible, runtime-only, validation-only et
  audit-only dans une architecture implicite.
- Closure expectation: produire une architecture citee, des matrices, des
  decisions de registres et une roadmap ordonnee pour les gaps restants.
- Forbidden regression: aucun changement applicatif, prompt, endpoint, DB,
  frontend, migration, build ou appel LLM reel.

Source-alignment evidence: the objective, target state, ACs, tasks, evidence,
validation plan, non-goals and guardrails map back to the source brief's
mandatory audit inputs, architecture sections, boundaries and no-code scope.

## Objective

Produire le document d'architecture de reference qui transforme les audits
CS-343 a CS-347 en decisions produit et techniques pour la generation des
prompts LLM.

Le document doit expliciter les owners, registres canoniques, frontieres,
surfaces nominales et non nominales, regles operationnelles et blockers.

## Target State

Un dossier timestamp est cree sous:
`_condamad/architecture/prompt-generation-cartography/2026-05-27-0000/`.

Il contient:

- `architecture-prompt-generation-llm.md` avec les dix sections obligatoires du
  brief et du skill `condamad-product-architecture`.
- `source-map.md` avec les audits CS-343 a CS-347 lus, les chemins exacts, les
  citations courtes et les assumptions.
- `validation-output.md` avec les commandes executees et leur resultat.

Le document final contient une capability matrix, une surface matrix, des
registry decisions, des entity/object decisions, des operational rules et une
ordered implementation roadmap.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-348-architecture-cartographie-generation-prompt-llm.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign the story number.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `.agents/skills/condamad-product-architecture/SKILL.md` - product architecture contract inspected.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver and targeted ID lookup.
- Repository structure alert: `_condamad/audits/prompt-generation-cartography` is absent in this workspace.
- Repository structure alert: implementation must record a blocker if required CS-343 to CS-347 audit deliverables are unavailable.

## Domain Boundary

- Domain: architecture-doc
- In scope:
  - Ingestion of CS-343, CS-344, CS-345, CS-346 and CS-347 audit outputs.
  - Creation of the timestamped architecture folder under `_condamad/architecture`.
  - Production of capability matrix, surface matrix and registry decisions.
  - Production of entity/object decisions and operational rules.
  - Production of blockers, decision owners, open questions and ordered roadmap.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling,
    migrations, prompt edits, LLM generator edits, public endpoints and app code.
- Explicit non-goals:
  - No new audit over the full codebase.
  - No application implementation.
  - No prompt modification.
  - No final Mermaid documentation, which belongs to CS-350.
  - No real LLM call.

Named brief primitives in scope:

- `condamad-product-architecture`
- `01-surface-inventory-audit.md`
- `02-configuration-assembly-placeholder-audit.md`
- `03-runtime-gateway-handoff-audit.md`
- `04-natal-astrology-input-audit.md`
- `05-output-validation-persistence-audit.md`
- `Capability matrix`
- `Surface matrix`
- `Canonical registry decisions`
- `Entity/object decisions`
- `Operational rules`
- `Blockers and decision owners`
- `Ordered implementation roadmap`

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this architecture synthesis contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Create only architecture and story evidence artifacts.
  - Keep backend application files unchanged.
  - Keep backend test files unchanged.
  - Keep frontend files unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: required CS-343 to CS-347 audit deliverables are unavailable during implementation.
- Additional validation rules:
  - `AST guard` or bounded `rg` evidence must prove no application source was modified.
  - `python` path checks must prove the architecture, source map and validation output exist.
  - `rg` evidence must prove the architecture contains all mandatory sections.
  - The architecture must separate observed audit facts, inferred decisions, blockers and assumptions.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Source audits and bounded evidence rereads prove the architecture base. |
| Baseline Snapshot | yes | The source map records audit availability before final decisions. |
| Ownership Routing | yes | Architecture artifacts must stay under `_condamad/architecture`. |
| Allowlist Exception | no | No allowlist handling is authorized for this architecture-only story. |
| Contract Shape | yes | The architecture has exact required sections and matrices. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | App, prompt, endpoint, frontend, DB and migration surfaces must stay unchanged. |
| Persistent Evidence | yes | Architecture, source map and validation output must persist for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The architecture document exists. | Evidence profile: baseline_before_after_diff; `python` checks `architecture-prompt-generation-llm.md`. |
| AC2 | CS-343 to CS-347 are cited. | Evidence profile: baseline_before_after_diff; `rg -n "CS-343|CS-344|CS-345|CS-346|CS-347"`. |
| AC3 | Mandatory architecture sections are present. | Evidence profile: json_contract_shape; `rg` checks required section headings. |
| AC4 | Prompt boundary surfaces are explicit. | Evidence profile: ast_architecture_guard; `rg` checks prompt/runtime/validation/audit boundaries. |
| AC5 | Registry decisions are complete. | Evidence profile: json_contract_shape; `rg` checks owner, versioning, trace and deprecation posture. |
| AC6 | Blockers remain visible. | Evidence profile: ast_architecture_guard; `rg` checks blockers, contradictions and decision owners. |
| AC7 | Roadmap is evidence-backed. | Evidence profile: batch_migration_mapping; `rg` checks ordered roadmap and source audit IDs. |
| AC8 | Application code remains unchanged. | Evidence profile: repo_wide_negative_scan; `python` checks `git status --short -- backend/app backend/tests frontend/src`. |
| AC9 | Source evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks `source-map.md` and `validation-output.md`. |

## Implementation Tasks

- [ ] Task 1: Verify CS-343 to CS-347 audit deliverables and record exact paths in `source-map.md`. (AC: AC2, AC9)
- [ ] Task 2: Load `condamad-product-architecture` and apply its output contract. (AC: AC3)
- [ ] Task 3: Ingest the five audit files as primary sources without starting a new code audit. (AC: AC2, AC4)
- [ ] Task 4: Write the executive architecture decision summary and audit source map. (AC: AC2, AC3)
- [ ] Task 5: Produce the capability matrix and surface matrix. (AC: AC3, AC4)
- [ ] Task 6: Produce canonical registry decisions with owner, versioning, trace and deprecation posture. (AC: AC5)
- [ ] Task 7: Produce entity/object decisions and operational rules for versioning, trace, cache, replay and invalidation. (AC: AC3, AC5)
- [ ] Task 8: Record blockers, contradictions, decision owners, open questions and validation plan. (AC: AC6)
- [ ] Task 9: Produce the ordered implementation roadmap from audit-backed gaps only. (AC: AC7)
- [ ] Task 10: Run validation commands and persist command output in `validation-output.md`. (AC: AC8, AC9)

## Files to Inspect First

- `_story_briefs/cs-348-architecture-cartographie-generation-prompt-llm.md`
- `.agents/skills/condamad-product-architecture/SKILL.md`
- `.agents/skills/condamad-product-architecture/references/output-contract.md`
- `.agents/skills/condamad-product-architecture/references/audit-bundle-ingestion.md`
- `.agents/skills/condamad-product-architecture/references/decision-rules.md`
- `.agents/skills/condamad-product-architecture/references/roadmap-rules.md`
- `_condamad/audits/prompt-generation-cartography/**/01-surface-inventory-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/02-configuration-assembly-placeholder-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/03-runtime-gateway-handoff-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/04-natal-astrology-input-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/05-output-validation-persistence-audit.md`

## Runtime Source of Truth

- Primary source of truth:
  - Completed audit deliverables from CS-343, CS-344, CS-345, CS-346 and CS-347.
  - `condamad-product-architecture` output contract and decision rules.
  - `AST guard` or bounded `rg` scans over architecture artifacts.
- Secondary evidence:
  - `git status --short -- _condamad _story_briefs backend/app backend/tests frontend/src`.
  - `source-map.md` citations with source path, source claim and decision mapping.
- Static scans alone are not sufficient for this story because:
  - The architecture must prove its decisions from completed audit evidence.

## Contract Shape

- Contract type:
  - Architecture artifact set and synthesis contract.
- Fields:
  - `Decision`: architecture decision or blocker.
  - `Source`: CS-343 to CS-347 audit path or explicit assumption.
  - `Owner`: product, architecture, security, data or technical owner.
  - `Boundary`: prompt-visible, runtime-only, validation-only or audit-only.
  - `Operational rule`: versioning, trace, cache, replay or invalidation rule.
  - `Roadmap order`: dependency-aware implementation sequence.
- Required fields:
  - `Decision`
  - `Source`
  - `Owner`
  - `Boundary`
  - `Operational rule`
  - `Roadmap order`
- Optional fields:
  - none
- Serialization names:
  - Matrix headings are emitted exactly as listed in this contract shape.
- Required files:
  - `architecture-prompt-generation-llm.md`
  - `source-map.md`
  - `validation-output.md`
- Required architecture sections:
  - `Executive architecture decision summary`
  - `Audit source map`
  - `Capability matrix`
  - `Surface matrix`
  - `Canonical registry decisions`
  - `Entity/object decisions`
  - `Operational rules`
  - `Blockers and decision owners`
  - `Ordered implementation roadmap`
  - `Open questions and validation plan`
- Status codes:
  - none; no API route is created or changed.
- Frontend type impact:
  - none; no frontend generated client or UI surface is in scope.
- Generated contract impact:
  - none; no OpenAPI or generated manifest change is in scope.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `source-map.md` records CS-343 to CS-347 source availability and missing evidence.
- Comparison after implementation:
  - `architecture-prompt-generation-llm.md` contains final matrices, decisions, blockers and roadmap.
- Expected invariant:
  - The only intended repository delta is the architecture artifact directory plus story execution evidence.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Audit evidence | CS-343 to CS-347 completed audit deliverables | Architecture claims without citation |
| Architecture synthesis | `_condamad/architecture/prompt-generation-cartography/**` | Backend app, frontend or prompt files |
| Source map evidence | Architecture artifact folder | Application source directories |
| Validation output | Architecture artifact folder | Backend tests or frontend tests |

## Mandatory Reuse / DRY Constraints

- Reuse CS-343 to CS-347 audit outputs as the canonical evidence base.
- Keep one final architecture document and one source map.
- Reference source IDs instead of duplicating full audit content across files.
- Use one vocabulary for `prompt-visible`, `runtime-only`, `validation-only` and `audit-only`.
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
  - `backend/migrations/**`
  - `_condamad/architecture/prompt-generation-cartography/**`
- Required guard:
  - `python` checks that `git status --short -- backend/app backend/tests frontend/src backend/migrations` returns no changed app surfaces.
  - `rg` checks the architecture contains required section names, source IDs and boundary terms.
  - `AST guard` checks architecture generation does not introduce prompt, runtime or endpoint changes.

## Regression Guardrails

Scope vector: operation `create`, domain `architecture-doc`, paths
`_condamad/architecture/prompt-generation-cartography`,
`_condamad/audits/prompt-generation-cartography` and contracts
`product-architecture`, `evidence-synthesis`, `persistent-evidence` and
`no-app-change`.

| Guardrail | Local invariant | Evidence |
|---|---|---|
| Registry gap | No exact prompt-generation architecture guardrail was returned by the scoped resolver. | `python` resolver output. |
| RG-041 non-applicable | Entitlement documentation is outside this architecture scope. | Manual check: no entitlement docs. |
| RG-047 non-applicable | Frontend inline style rules are outside this architecture scope. | Manual check: no frontend edits. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Architecture document | `_condamad/architecture/prompt-generation-cartography/2026-05-27-0000/architecture-prompt-generation-llm.md` | Keep final decisions. |
| Source map | `_condamad/architecture/prompt-generation-cartography/2026-05-27-0000/source-map.md` | Keep audit citations. |
| Validation output | `_condamad/architecture/prompt-generation-cartography/2026-05-27-0000/validation-output.md` | Keep command output. |
| Review output | `_condamad/stories/CS-348-architecture-cartographie-generation-prompt-llm/generated/11-code-review.md` | Keep automatic review output. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this architecture-only story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/architecture/prompt-generation-cartography/2026-05-27-0000/architecture-prompt-generation-llm.md` - final architecture.
- `_condamad/architecture/prompt-generation-cartography/2026-05-27-0000/source-map.md` - audit citations and assumptions.
- `_condamad/architecture/prompt-generation-cartography/2026-05-27-0000/validation-output.md` - validation output.

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
  `python -c "from pathlib import Path; root=Path('_condamad/architecture/prompt-generation-cartography'); assert root.exists()"`
- VC2:
  `python -c "from pathlib import Path; assert any(root.glob('*/architecture-prompt-generation-llm.md'))"`
  from `_condamad/architecture/prompt-generation-cartography` with `root=Path('.')`.
- VC3:
  `rg -n "Executive architecture|Capability|Surface|Canonical registry|Operational rules|Blockers" _condamad/architecture/prompt-generation-cartography`
- VC4:
  `rg -n "CS-343|CS-344|CS-345|CS-346|CS-347" _condamad/architecture/prompt-generation-cartography`
- VC5:
  `rg -n "prompt-visible|runtime-only|validation-only|audit-only" _condamad/architecture/prompt-generation-cartography`
- VC6:
  `rg -n "owner|versioning|trace|cache|replay|invalidation|deprecation" _condamad/architecture/prompt-generation-cartography`
- VC7:
  `rg -n "Ordered implementation roadmap|Open questions and validation plan" _condamad/architecture/prompt-generation-cartography`
- VC8:
  `rg -n "architecture-prompt-generation-llm" _condamad`
- VC9:
  `python -c "import subprocess; assert not subprocess.check_output(['git','status','--short','--','backend/app','backend/tests','frontend/src','backend/migrations']).strip()"`
- VC10:
  `git status --short -- _condamad _story_briefs backend/app backend/tests frontend/src`

## Regression Risks

- The architecture may summarize too broadly and hide contradictions from the
  audits.
- The architecture may turn audit-only evidence into prompt-visible input.
- The roadmap may introduce work not supported by source audits.
- The synthesis may start a new audit instead of using CS-343 to CS-347 as the
  evidence base.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the repository Python venv before every Python command.
- Load `condamad-product-architecture` before producing the architecture.
- Treat CS-343 to CS-347 audit deliverables as primary sources.
- Keep architecture claims cited by audit source path or explicit assumption.
- Stop and record a blocker if required CS-343 to CS-347 deliverables are missing.
- Keep `backend/app`, `backend/tests`, `frontend/src` and `backend/migrations` unchanged.
- Use one timestamped architecture folder for all deliverables.
- Do not execute real LLM calls.

## References

- `_story_briefs/cs-348-architecture-cartographie-generation-prompt-llm.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `.agents/skills/condamad-product-architecture/SKILL.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/audits/prompt-generation-cartography/**/01-surface-inventory-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/02-configuration-assembly-placeholder-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/03-runtime-gateway-handoff-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/04-natal-astrology-input-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/05-output-validation-persistence-audit.md`
