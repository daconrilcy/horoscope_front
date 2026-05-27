# Story CS-355 audit-cloture-validation-document-cartographie-prompt-llm: Audit Cloture Validation Document Cartographie Prompt LLM
Status: ready-to-dev

## Trigger / Source

- Mode: Audit-to-story with repo-informed evidence.
- Source brief: `_story_briefs/cs-355-audit-cloture-validation-document-cartographie-prompt-llm.md`.
- Source problem: the prompt-generation cartography chain must not close while required corrections or residual risks remain implicit.
- Source stakes:
  - User impact: future agents need a final unambiguous verdict on the CS-350 cartography document.
  - Technical risk: CS-351 to CS-354 findings can be softened or left unresolved without a documented closure decision.
  - Closure expectation: create a short timestamped closure audit under `_condamad/audits/prompt-generation-document-review/`.
  - Forbidden regression: no code, test, prompt, provider, frontend, DB, migration, architecture, or CS-350 document edit.
- Source-alignment review: PASS. Objective, ACs, tasks, evidence, non-goals, and guardrails map to the brief stakes.

## Objective

Produce a final documentary closure audit for the prompt-generation cartography review chain.

The audit must give one clear verdict on the current final document: valid, valid with accepted residual risks, or invalid until named
corrections are applied.

## Target State

A timestamped report exists at:
`_condamad/audits/prompt-generation-document-review/YYYY-MM-DD-HHMM/04-document-validation-closure-audit.md`.

The report contains:

- A closure verdict.
- A matrix of expected corrections and their status.
- A matrix of parallel or legacy processes and their documentation status.
- Accepted residual risks.
- Remaining blocking risks.
- Executed validation commands.
- A final decision.

Every CS-351 to CS-353 finding is closed, accepted as residual risk, or converted to a story candidate.
Every CS-354 architecture decision is reflected in the closure decision.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-355-audit-cloture-validation-document-cartographie-prompt-llm.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-355`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` exists.
- Evidence 5: `_condamad/stories/CS-351-audit-revue-adversariale-document-cartographie-prompt-llm/00-story.md` exists.
- Evidence 6: `_condamad/stories/CS-352-audit-concordance-code-document-generation-prompt-llm/00-story.md` exists.
- Evidence 7: `_condamad/stories/CS-353-audit-process-paralleles-generation-prompt-llm/00-story.md` exists.
- Evidence 8: `_condamad/stories/CS-354-rapport-architecture-process-paralleles-legacy-prompt-llm/00-story.md` exists.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver and targeted ID lookup.
- Evidence 10: `resolve_guardrails.py` returned no locally applicable guardrail for this closure-audit scope.
- Repository structure alert: `_condamad/audits/prompt-generation-document-review` is absent in this workspace.
- Repository structure alert: `_condamad/architecture/prompt-generation-document-review` is absent in this workspace.
- Repository structure alert: implementation must create timestamp folders or record source blockers after CS-351 to CS-354 execute.

## Domain Boundary

- Domain: condamad-audit-documentation
- In scope:
  - Reading the current final prompt-generation cartography document.
  - Reading CS-351, CS-352 and CS-353 audit deliverables.
  - Reading CS-354 architecture decision report.
  - Creating one closure audit report under `_condamad/audits/prompt-generation-document-review/`.
  - Classifying each correction, parallel process, residual risk, blocking risk and final decision.
  - Persisting story evidence and validation output.
- Out of scope:
  - Backend runtime changes, backend tests, frontend UI, database schema, auth, i18n, styling, build tooling and migrations.
  - Direct edits to `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`.
  - Redeciding architecture, modifying prompts, executing provider calls, or creating automated tests.
  - Guardrail registry maintenance or enrichment.
- Explicit non-goals:
  - No implementation code change.
  - No source document rewrite.
  - No architecture decision rewrite.
  - No real LLM or provider call.
  - No frontend route, screen, client generation, or UI validation.

Named brief primitives in scope:

- `document final courant`
- `livrables CS-351 a CS-354`
- `corrections documentaires recommandees`
- `processus paralleles ou legacy`
- `risques residuels acceptes`
- `risques bloquants restants`
- `verdict de cloture`
- `decision finale`

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this documentary closure audit contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Create only the closure audit report and story evidence artifacts.
  - Keep backend application files unchanged.
  - Keep backend test files unchanged.
  - Keep frontend files unchanged.
  - Keep CS-350 final documentation unchanged.
  - Keep CS-354 architecture decisions unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-351, CS-352, CS-353 or CS-354 deliverables are unavailable at implementation time.
- Additional validation rules:
  - `python` path checks must prove the closure audit report and evidence artifacts exist.
  - `rg` evidence must prove the report contains verdict, corrections, parallel processes, blocking risks and final decision terms.
  - `AST guard` or bounded `git status` evidence must prove no application source was modified.
  - The report must label unresolved source gaps as `Evidence gap`, `Accepted residual risk`, `Blocking risk`, or `Story candidate`.
  - The final verdict must be exactly one of `valid`, `valid with accepted residual risks`, or `invalid until corrections`.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Source artifacts and bounded rereads prove the closure report base. |
| Baseline Snapshot | yes | Source availability before closure conclusions must be persisted. |
| Ownership Routing | yes | Closure artifacts must stay under `_condamad/audits` and story evidence. |
| Allowlist Exception | no | No allowlist handling is authorized for this closure-audit story. |
| Contract Shape | yes | The report has exact sections, matrices, verdict, validation commands and final decision. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Parallel, legacy and residual-risk paths must stay classified, not implemented. |
| Persistent Evidence | yes | Report, source evidence and validation output must persist for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The closure audit report exists. | Evidence profile: baseline_before_after_diff; `python` checks the report path. |
| AC2 | Mandatory sections are present. | Evidence profile: json_contract_shape; `rg` checks closure report headings. |
| AC3 | CS-351 to CS-353 findings are closed. | Evidence profile: json_contract_shape; `rg` checks `CS-351`, `CS-352`, `CS-353` and closure statuses. |
| AC4 | CS-354 decisions are reflected. | Evidence profile: json_contract_shape; `rg` checks `CS-354`, decision and architecture terms. |
| AC5 | Process status is explicit. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks process status terms. |
| AC6 | The final verdict is unambiguous. | Evidence profile: json_contract_shape; `python` checks the allowed verdict labels. |
| AC7 | Blocking risks are explicit. | Evidence profile: json_contract_shape; `rg` checks blocking risk and residual risk labels. |
| AC8 | Application code remains unchanged. | Evidence profile: repo_wide_negative_scan; `python` checks bounded `git status` app surfaces. |
| AC9 | Story evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks evidence paths. |

## Implementation Tasks

- [ ] Task 1: Read the final cartography document and record source availability evidence. (AC: AC1, AC2, AC9)
- [ ] Task 2: Read CS-351, CS-352 and CS-353 audit reports after their implementation outputs exist. (AC: AC3, AC5)
- [ ] Task 3: Read the CS-354 architecture report after its implementation output exists. (AC: AC4)
- [ ] Task 4: Build the expected-corrections matrix and mark each item closed, accepted residual risk, or story candidate. (AC: AC3, AC7)
- [ ] Task 5: Build the parallel and legacy process matrix with one documentation status per process. (AC: AC5)
- [ ] Task 6: Record accepted residual risks and blocking risks with source references. (AC: AC6, AC7)
- [ ] Task 7: Write the final verdict using the allowed verdict vocabulary. (AC: AC6)
- [ ] Task 8: Run validation scans, persist command output and bounded app-surface status evidence. (AC: AC2, AC8, AC9)

## Files to Inspect First

- `_story_briefs/cs-355-audit-cloture-validation-document-cartographie-prompt-llm.md`
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/audits/prompt-generation-document-review/**/01-adversarial-document-review-audit.md`
- `_condamad/audits/prompt-generation-document-review/**/02-code-document-concordance-audit.md`
- `_condamad/audits/prompt-generation-document-review/**/03-parallel-legacy-processes-audit.md`
- `_condamad/architecture/prompt-generation-document-review/**/archi-parallel-legacy-prompt-generation-report.md`
- `_condamad/stories/CS-351-audit-revue-adversariale-document-cartographie-prompt-llm/00-story.md`
- `_condamad/stories/CS-352-audit-concordance-code-document-generation-prompt-llm/00-story.md`
- `_condamad/stories/CS-353-audit-process-paralleles-generation-prompt-llm/00-story.md`
- `_condamad/stories/CS-354-rapport-architecture-process-paralleles-legacy-prompt-llm/00-story.md`
- `_condamad/audits/prompt-generation-document-review/**` - expected implementation-created path.
- `_condamad/architecture/prompt-generation-document-review/**` - expected implementation-created path.

## Runtime Source of Truth

- Primary source of truth:
  - CS-351, CS-352 and CS-353 audit deliverables.
  - CS-354 architecture report.
  - Current final prompt-generation cartography document.
  - `AST guard` or bounded status guard proving report-only changes.
- Secondary evidence:
  - `rg` scans over `_condamad/audits/prompt-generation-document-review`.
  - `rg` scans over `_condamad/architecture/prompt-generation-document-review`.
  - Source availability evidence under this story's `evidence/` folder.
- Static scans alone are not sufficient for this story because:
  - The closure verdict must tie every correction and residual risk back to source artifacts.

## Contract Shape

- Contract type:
  - Closure audit artifact and final verdict contract.
- Fields:
  - `Source`: CS-351, CS-352, CS-353, CS-354, or final document source.
  - `Item`: finding, correction, decision, parallel process, residual risk, or blocking risk.
  - `Status`: closed, accepted residual risk, story candidate, blocking risk, or not in closure scope.
  - `Evidence`: source path plus section, heading, row marker, process name, or bounded note.
  - `Decision`: valid, valid with accepted residual risks, invalid until corrections, or deferred to named story.
  - `Owner`: documentation closure, product decision, architecture decision, or follow-up story.
- Required fields:
  - `Source`
  - `Item`
  - `Status`
  - `Evidence`
  - `Decision`
  - `Owner`
- Optional fields:
  - none
- Serialization names:
  - Matrix headings are emitted exactly as listed in this contract shape.
- Required report sections:
  - `Verdict de cloture`
  - `Corrections attendues et statut`
  - `Processus paralleles ou legacy et statut documentaire`
  - `Risques residuels acceptes`
  - `Risques bloquants restants`
  - `Commandes de validation executees`
  - `Decision finale`
- Status codes:
  - none; no API route is created or changed.
- Frontend type impact:
  - none; no frontend generated client or UI surface is in scope.
- Generated contract impact:
  - none; no OpenAPI or generated manifest change is in scope.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-355-audit-cloture-validation-document-cartographie-prompt-llm/evidence/source-availability.txt`
- Comparison after implementation:
  - `_condamad/audits/prompt-generation-document-review/YYYY-MM-DD-HHMM/04-document-validation-closure-audit.md`
- Expected invariant:
  - The only intended repository delta is the closure audit report directory plus story execution evidence.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Closure audit report | `_condamad/audits/prompt-generation-document-review/YYYY-MM-DD-HHMM/**` | Backend app or frontend code |
| Source evidence | `_condamad/stories/CS-355-audit-cloture-validation-document-cartographie-prompt-llm/evidence/**` | Application source files |
| Validation output | `_condamad/stories/CS-355-audit-cloture-validation-document-cartographie-prompt-llm/evidence/validation.txt` | App tests or CI config |
| Automatic review handoff | `_condamad/stories/CS-355-audit-cloture-validation-document-cartographie-prompt-llm/generated/**` | Closure report source matrix |

## Mandatory Reuse / DRY Constraints

- Reuse CS-351, CS-352, CS-353, CS-354 and CS-350 as the canonical evidence base.
- Reference source paths, headings and row markers instead of duplicating full audit or documentation blocks.
- Keep one status vocabulary across findings, corrections, processes and risks.
- Keep one final verdict vocabulary across the report and validation evidence.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy route, prompt, provider, projection or payload path may be added.
- No compatibility route, prompt, provider, projection or payload path may be added.
- No fallback route, prompt, provider, projection or payload path may be added.
- Do not move application logic into audit artifacts.
- Do not add source aliases, shims or broad allowlists.
- Forbidden app surfaces for edits:
  - `backend/app/**`
  - `backend/tests/**`
  - `frontend/**`
  - `backend/migrations/**`
  - `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
  - `_condamad/architecture/prompt-generation-document-review/**/archi-parallel-legacy-prompt-generation-report.md`

## Reintroduction Guard

- Guarded surfaces:
  - `backend/app/**`
  - `backend/tests/**`
  - `frontend/src/**`
  - `backend/migrations/**`
  - `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
  - `_condamad/architecture/prompt-generation-document-review/**/archi-parallel-legacy-prompt-generation-report.md`
- Required guard:
  - `python` checks that bounded `git status --short` over app, test, frontend, migration and CS-350 document surfaces has no story changes.
  - `rg` checks the report contains verdict, correction status, process status, residual risk, blocking risk and final decision terms.
  - `AST guard` or bounded status evidence proves no prompt, runtime, endpoint, DB or frontend implementation was changed.

## Regression Guardrails

Scope vector: operation `create`, domain `condamad-audit-documentation`, paths `_condamad/audits/prompt-generation-document-review`,
`_condamad/docs/prompt-generation-cartography`, `_condamad/architecture/prompt-generation-document-review`, contracts `closure-audit`,
`source-alignment`, `persistent-evidence` and `no-app-change`.

| Guardrail | Local invariant | Evidence |
|---|---|---|
| Registry gap | No exact closure-audit guardrail was returned by the scoped resolver. | `python` resolver output. |
| RG-047 non-applicable | Frontend TSX inline styles are outside this report-only scope. | Manual check: no frontend edits. |
| RG-052 non-applicable | Frontend CSS namespace migration is outside this report-only scope. | Manual check: no CSS edits. |
| RG-041 non-applicable | Entitlement documentation is outside this prompt-generation closure. | Manual check: no entitlement docs. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Source availability | `_condamad/stories/CS-355-audit-cloture-validation-document-cartographie-prompt-llm/evidence/source-availability.txt` | Keep source checks. |
| Validation output | `_condamad/stories/CS-355-audit-cloture-validation-document-cartographie-prompt-llm/evidence/validation.txt` | Keep command output. |
| Final report | `_condamad/audits/prompt-generation-document-review/YYYY-MM-DD-HHMM/04-document-validation-closure-audit.md` | Keep verdict. |
| Review output | `_condamad/stories/CS-355-audit-cloture-validation-document-cartographie-prompt-llm/generated/11-code-review.md` | Keep automatic review output. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this closure-audit story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/prompt-generation-document-review/YYYY-MM-DD-HHMM/04-document-validation-closure-audit.md` - final closure audit.
- `_condamad/stories/CS-355-audit-cloture-validation-document-cartographie-prompt-llm/evidence/source-availability.txt` - source checks.
- `_condamad/stories/CS-355-audit-cloture-validation-document-cartographie-prompt-llm/evidence/validation.txt` - validation output.
- `_condamad/stories/CS-355-audit-cloture-validation-document-cartographie-prompt-llm/generated/11-code-review.md` - generated review handoff.

Likely tests:

- `_condamad/stories/CS-355-audit-cloture-validation-document-cartographie-prompt-llm/evidence/validation.txt` - assumption risk:
  report-only validation evidence replaces a new test file.
- Existing validation may run bounded `rg`, `python` and `git status` checks.

Files not expected to change:

- `backend/app/**` - out of scope; application runtime and service code remain unchanged.
- `backend/tests/**` - out of scope; tests are read or checked only.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no schema or migration work is touched.
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - out of scope for direct edits.
- `_condamad/architecture/prompt-generation-document-review/**/archi-parallel-legacy-prompt-generation-report.md` - read-only source.
- `_condamad/stories/regression-guardrails.md` - out of scope for normal story implementation.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1:
  `python -c "from pathlib import Path; root=Path('_condamad/audits/prompt-generation-document-review'); assert root.exists()"`
- VC2:
  `python -c "from pathlib import Path as P; root=P('_condamad/audits/prompt-generation-document-review'); assert list(root.glob('*/04-document-validation-closure-audit.md'))"`
- VC3:
  `rg -n "document-validation-closure-audit|Verdict|Corrections attendues|Processus paralleles|Risques bloquants" _condamad/audits/prompt-generation-document-review`
- VC4:
  `rg -n "prompt-generation-current-implementation|parallel-legacy|archi-parallel-legacy" _condamad`
- VC5:
  `rg -n "CS-351|CS-352|CS-353|CS-354|Accepted residual risk|Blocking risk|Story candidate" _condamad/audits/prompt-generation-document-review`
- VC6:
  `rg -n "valid|valid with accepted residual risks|invalid until corrections|Decision finale" _condamad/audits/prompt-generation-document-review`
- VC7:
  `python -c "from pathlib import Path; p=Path('_condamad/stories/CS-355-audit-cloture-validation-document-cartographie-prompt-llm/evidence/validation.txt'); assert p.exists()"`
- VC8:
  `git status --short -- backend/app backend/tests frontend/src backend/migrations`
- VC9:
  `git status --short -- _condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`

## Regression Risks

- The closure report may approve the document while unresolved corrections remain implicit.
- The closure report may omit one of the CS-351 to CS-353 findings.
- The closure report may ignore a CS-354 architecture decision or provider-capable open question.
- Parallel or legacy process status may become vague instead of tied to a source row.
- The report may imply changes to CS-350 or runtime code, which are outside this story.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the repository Python venv before every Python command.
- Execute this story only after CS-351, CS-352, CS-353 and CS-354 implementation outputs exist.
- Keep report citations short and path-based; do not paste long source blocks.
- Keep `backend/app`, `backend/tests`, `frontend/src`, `backend/migrations`, CS-350 documentation and CS-354 architecture unchanged.
- Do not execute real LLM calls.
- Record unresolved source gaps as `Evidence gap`, `Blocking risk` or `Story candidate`.

## References

- `_story_briefs/cs-355-audit-cloture-validation-document-cartographie-prompt-llm.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/audits/prompt-generation-document-review/**/01-adversarial-document-review-audit.md`
- `_condamad/audits/prompt-generation-document-review/**/02-code-document-concordance-audit.md`
- `_condamad/audits/prompt-generation-document-review/**/03-parallel-legacy-processes-audit.md`
- `_condamad/architecture/prompt-generation-document-review/**/archi-parallel-legacy-prompt-generation-report.md`
- `_condamad/stories/CS-351-audit-revue-adversariale-document-cartographie-prompt-llm/00-story.md`
- `_condamad/stories/CS-352-audit-concordance-code-document-generation-prompt-llm/00-story.md`
- `_condamad/stories/CS-353-audit-process-paralleles-generation-prompt-llm/00-story.md`
- `_condamad/stories/CS-354-rapport-architecture-process-paralleles-legacy-prompt-llm/00-story.md`
