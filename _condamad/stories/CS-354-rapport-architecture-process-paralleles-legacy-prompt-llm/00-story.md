# Story CS-354 rapport-architecture-process-paralleles-legacy-prompt-llm: Rapport Architecture Process Paralleles Legacy Prompt LLM
Status: ready-to-dev

## Trigger / Source

Brief direct source: `_story_briefs/cs-354-archi-rapport-process-paralleles-legacy-generation-prompt-llm.md`.

Problem statement: les audits CS-351 a CS-353 et le document CS-350 doivent aboutir a une decision architecture claire sur les
processus paralleles, legacy, bootstrap, test, admin et non nominaux de generation des prompts LLM.

Source stakes:

- User impact: disposer d'une classification exploitable pour savoir quels chemins sont supportes, toleres, a migrer, a tester ou a eteindre.
- Technical risk: laisser des chemins provider-capable non nominaux redevenir prompt-visibles sans decision explicite.
- Closure expectation: creer un rapport architecture timestamp sous `_condamad/architecture/prompt-generation-document-review/`.
- Forbidden regression: aucune modification de code, du document CS-350, de prompt, de provider, de frontend, de DB ou de migration.

Source-alignment evidence: objective, target state, ACs, tasks, validation plan, non-goals and guardrails map to the brief's report-only
scope, mandatory source set, decision matrix, provider-capable decisions, guardrail expectations and product-decision questions.

## Objective

Produire un rapport architectural decisionnel qui classe les chemins de generation des prompts LLM identifies par CS-351, CS-352 et CS-353.

Le rapport doit statuer sur le flux nominal, les flux paralleles supportes, les chemins legacy toleres, les chemins bootstrap/test/admin,
les fallbacks ou repairs non nominaux, les impacts CS-350 et les guardrails d'anti-retour.

## Target State

Un dossier timestamp est cree sous:
`_condamad/architecture/prompt-generation-document-review/YYYY-MM-DD-HHMM/`.

Il contient:

- `archi-parallel-legacy-prompt-generation-report.md` avec les neuf sections demandees par le brief.
- Une source map des audits CS-351, CS-352, CS-353, du document CS-350, de l'architecture CS-348 et du rapport CS-349.
- Une taxonomy distinguant nominal, parallele supporte, legacy tolere, fallback, repair, bootstrap, test, admin, archive et non runtime truth.
- Une matrice decisionnelle par processus audite en CS-353.
- Une roadmap courte de corrections documentaires, guardrails ou stories d'extinction.
- Des questions produit ou techniques pour tout chemin provider-capable non nominal sans decision suffisante.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-354-archi-rapport-process-paralleles-legacy-generation-prompt-llm.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-354`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - CS-350 final document exists.
- Evidence 5: `_condamad/architecture/prompt-generation-cartography/2026-05-27-0000/architecture-prompt-generation-llm.md` exists.
- Evidence 6: `_condamad/reports/prompt-generation-cartography/2026-05-27-0000/report-prompt-generation-cartography.md` exists.
- Evidence 7: `_condamad/stories/CS-351-audit-revue-adversariale-document-cartographie-prompt-llm/00-story.md` exists.
- Evidence 8: `_condamad/stories/CS-352-audit-concordance-code-document-generation-prompt-llm/00-story.md` exists.
- Evidence 9: `_condamad/stories/CS-353-audit-process-paralleles-generation-prompt-llm/00-story.md` exists.
- Evidence 10: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver and targeted ID lookup.
- Evidence 11: `resolve_guardrails.py` returned no locally applicable guardrail for this architecture-report scope.
- Repository structure alert: `_condamad/architecture/prompt-generation-document-review` is absent in this workspace.
- Repository structure alert: implementation must create the timestamp folder and report file.

## Domain Boundary

- Domain: condamad-architecture-documentation
- In scope:
  - Reading CS-351 adversarial document review audit output.
  - Reading CS-352 code-document concordance audit output.
  - Reading CS-353 parallel legacy process audit output.
  - Reading the final CS-350 prompt generation document.
  - Reading CS-348 architecture and CS-349 report as supporting source context.
  - Creating one architecture report under `_condamad/architecture/prompt-generation-document-review/`.
  - Classifying prompt-generation process families and recording decisions.
  - Recording guardrails, candidate stories and product or technical open questions.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling, migrations, prompt edits, provider calls and app code.
  - Direct edits to CS-350 final documentation.
  - Implementation of migration, extinction, tests or runtime guardrails.
- Explicit non-goals:
  - No implementation code change.
  - No rewrite of CS-351, CS-352 or CS-353 audit reports.
  - No edit to the final CS-350 document.
  - No real LLM or provider call.
  - No new runtime route, prompt path, repair path or provider path.

Named brief primitives in scope:

- `flux nominal de reference`
- `flux paralleles officiellement supportes`
- `chemins legacy toleres temporairement`
- `chemins bootstrap/test/admin`
- `fallbacks`
- `repairs`
- `provider-capable`
- `taxonomy`
- `matrice decisionnelle`
- `guardrails`
- `stories candidates`
- `open questions produit ou technique`

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this architecture report contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Create only architecture report and story evidence artifacts.
  - Keep backend application files unchanged.
  - Keep backend test files unchanged.
  - Keep frontend files unchanged.
  - Keep CS-350 documentation unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: a provider-capable non nominal process cannot be classified from CS-351 to CS-353 evidence.
- Additional validation rules:
  - `python` path checks must prove the architecture report and evidence artifacts exist.
  - `rg` evidence must prove the report contains the required taxonomy, decision matrix, guardrails and provider-capable terms.
  - `AST guard` or bounded `git status` evidence must prove no application source was modified.
  - The report must label unresolved source gaps as `Evidence gap` or `Open question` instead of implying false closure.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Source artifacts and bounded rereads prove the architecture report base. |
| Baseline Snapshot | yes | Source availability before architecture conclusions must be persisted. |
| Ownership Routing | yes | Architecture artifacts must stay under `_condamad/architecture` and story evidence. |
| Allowlist Exception | no | No allowlist handling is authorized for this report-only story. |
| Contract Shape | yes | The report has exact sections, taxonomy, decisions, guardrails and open questions. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Legacy, fallback, repair and provider-capable paths must stay classified, not implemented. |
| Persistent Evidence | yes | Report, source evidence and validation output must persist for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The architecture report exists. | Evidence profile: baseline_before_after_diff; `python` checks the report path. |
| AC2 | Mandatory sections are present. | Evidence profile: json_contract_shape; `rg` checks section headings in the report folder. |
| AC3 | CS-353 processes have decisions. | Evidence profile: json_contract_shape; `rg` checks `Decision par processus` and process terms. |
| AC4 | Path classes are not confused. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks nominal, fallback, bootstrap, test and admin terms. |
| AC5 | Provider-capable paths have decisions. | Evidence profile: ast_architecture_guard; `rg` checks `provider-capable` decision terms. |
| AC6 | CS-350 impacts are actionnable. | Evidence profile: json_contract_shape; `rg` checks impact and documentation terms. |
| AC7 | Guardrail proposals are concrete. | Evidence profile: reintroduction_guard; `rg` checks guardrail and verification terms. |
| AC8 | Application code remains unchanged. | Evidence profile: repo_wide_negative_scan; `python` checks bounded `git status` app surfaces. |
| AC9 | Story evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks evidence paths. |

## Implementation Tasks

- [ ] Task 1: Read CS-351, CS-352, CS-353 audit outputs and record source availability evidence. (AC: AC1, AC3, AC9)
- [ ] Task 2: Read CS-350, CS-348 and CS-349 source documents for architecture context. (AC: AC2, AC4, AC6)
- [ ] Task 3: Build the taxonomy for nominal, parallel, legacy, fallback, repair, bootstrap, test, admin and archive paths. (AC: AC4)
- [ ] Task 4: Create the decision matrix for every process listed by CS-353. (AC: AC3, AC5)
- [ ] Task 5: Record CS-350 impacts without editing the CS-350 document. (AC: AC6, AC8)
- [ ] Task 6: Define guardrail proposals and candidate follow-up stories ordered by risk. (AC: AC7)
- [ ] Task 7: Record open questions for provider-capable non nominal paths without a final product decision. (AC: AC5)
- [ ] Task 8: Persist validation output and bounded app-surface status evidence. (AC: AC8, AC9)

## Files to Inspect First

- `_story_briefs/cs-354-archi-rapport-process-paralleles-legacy-generation-prompt-llm.md`
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/audits/prompt-generation-document-review/**/01-adversarial-document-review-audit.md`
- `_condamad/audits/prompt-generation-document-review/**/02-code-document-concordance-audit.md`
- `_condamad/audits/prompt-generation-document-review/**/03-parallel-legacy-processes-audit.md`
- `_condamad/architecture/prompt-generation-cartography/**/architecture-prompt-generation-llm.md`
- `_condamad/reports/prompt-generation-cartography/**/report-prompt-generation-cartography.md`
- `_condamad/stories/CS-351-audit-revue-adversariale-document-cartographie-prompt-llm/00-story.md`
- `_condamad/stories/CS-352-audit-concordance-code-document-generation-prompt-llm/00-story.md`
- `_condamad/stories/CS-353-audit-process-paralleles-generation-prompt-llm/00-story.md`
- `_condamad/architecture/prompt-generation-document-review/**` - expected implementation-created path.

## Runtime Source of Truth

- Primary source of truth:
  - CS-351, CS-352 and CS-353 audit deliverables.
  - CS-350 final prompt-generation document.
  - CS-348 architecture and CS-349 report for supporting context.
  - `AST guard` or bounded status guard proving report-only changes.
- Secondary evidence:
  - `rg` scans over `_condamad/architecture/prompt-generation-document-review`.
  - Source availability evidence under this story's `evidence/` folder.
- Static scans alone are not sufficient for this story because:
  - The report must tie each architecture decision back to source artifacts and label unavailable evidence.

## Contract Shape

- Contract type:
  - Architecture report artifact and decision matrix contract.
- Fields:
  - `Process`: audited prompt-generation path or family.
  - `Category`: nominal, parallel, legacy, fallback, repair, bootstrap, test, admin or archive.
  - `Provider capability`: whether the process can reach a provider handoff.
  - `Runtime truth status`: supported, non nominal, seed-only, test-only, admin-only, archival or unknown.
  - `Decision`: document, conserve, migrate, deprecate, test or delete by follow-up story.
  - `CS-350 impact`: documentation update or no update.
  - `Guardrail`: concrete verification proposal.
  - `Next action`: candidate story or product decision.
- Required fields:
  - `Process`
  - `Category`
  - `Provider capability`
  - `Runtime truth status`
  - `Decision`
  - `CS-350 impact`
  - `Guardrail`
  - `Next action`
- Optional fields:
  - none
- Serialization names:
  - Matrix headings are emitted exactly as listed in this contract shape.
- Required report sections:
  - `Executive architecture summary`
  - `Source map`
  - `Taxonomy des chemins de prompt generation`
  - `Matrice nominal/parallele/legacy/fallback/bootstrap/test/admin`
  - `Decision par processus`
  - `Impacts sur le document final CS-350`
  - `Guardrails requis`
  - `Stories candidates ordonnees par risque`
  - `Open questions produit ou technique`
- Status codes:
  - none; no API route is created or changed.
- Frontend type impact:
  - none; no frontend generated client or UI surface is in scope.
- Generated contract impact:
  - none; no OpenAPI or generated manifest change is in scope.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-354-rapport-architecture-process-paralleles-legacy-prompt-llm/evidence/source-availability.txt`
- Comparison after implementation:
  - `_condamad/architecture/prompt-generation-document-review/YYYY-MM-DD-HHMM/archi-parallel-legacy-prompt-generation-report.md`
- Expected invariant:
  - The only intended repository delta is the architecture report directory plus story execution evidence.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Architecture report | `_condamad/architecture/prompt-generation-document-review/YYYY-MM-DD-HHMM/**` | Backend app or frontend code |
| Source evidence | `_condamad/stories/CS-354-rapport-architecture-process-paralleles-legacy-prompt-llm/evidence/**` | Application source files |
| Validation output | `_condamad/stories/CS-354-rapport-architecture-process-paralleles-legacy-prompt-llm/evidence/validation.txt` | App tests or CI config |
| Automatic review handoff | `_condamad/stories/CS-354-rapport-architecture-process-paralleles-legacy-prompt-llm/generated/**` | Architecture report source matrix |

## Mandatory Reuse / DRY Constraints

- Reuse CS-351, CS-352, CS-353 and CS-350 as the canonical evidence base.
- Reference source paths instead of duplicating full audit or documentation blocks.
- Keep one taxonomy and one decision vocabulary across the report.
- Use the same process names as CS-353 unless the report records an explicit source naming correction.
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
  - `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`

## Reintroduction Guard

- Guarded surfaces:
  - `backend/app/**`
  - `backend/tests/**`
  - `frontend/src/**`
  - `backend/migrations/**`
  - `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- Required guard:
  - `python` checks that bounded `git status --short` over app, test, frontend, migration and CS-350 document surfaces has no story changes.
  - `rg` checks the report contains taxonomy, decision, provider-capable, guardrail and open-question terms.
  - `AST guard` or bounded status evidence proves no prompt, runtime, endpoint, DB or frontend implementation was changed.

## Regression Guardrails

Scope vector: operation `create`, domain `condamad-architecture-documentation`, paths `_condamad/architecture/prompt-generation-document-review`,
`_condamad/audits/prompt-generation-document-review`, `_condamad/docs/prompt-generation-cartography`, contracts `architecture-report`,
`persistent-evidence` and `no-app-change`.

| Guardrail | Local invariant | Evidence |
|---|---|---|
| Registry gap | No exact architecture-report guardrail was returned by the scoped resolver. | `python` resolver output. |
| RG-047 non-applicable | Frontend TSX inline styles are outside this report-only scope. | Manual check: no frontend edits. |
| RG-052 non-applicable | Frontend CSS namespace migration is outside this report-only scope. | Manual check: no CSS edits. |
| RG-041 non-applicable | Entitlement documentation is outside this prompt-generation report. | Manual check: no entitlement docs. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Source availability | `_condamad/stories/CS-354-rapport-architecture-process-paralleles-legacy-prompt-llm/evidence/source-availability.txt` | Keep source checks. |
| Validation output | `_condamad/stories/CS-354-rapport-architecture-process-paralleles-legacy-prompt-llm/evidence/validation.txt` | Keep command output. |
| Final report | `_condamad/architecture/prompt-generation-document-review/YYYY-MM-DD-HHMM/archi-parallel-legacy-prompt-generation-report.md` | Keep decisions. |
| Review output | `_condamad/stories/CS-354-rapport-architecture-process-paralleles-legacy-prompt-llm/generated/11-code-review.md` | Keep automatic review output. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this report-only story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/architecture/prompt-generation-document-review/YYYY-MM-DD-HHMM/archi-parallel-legacy-prompt-generation-report.md` - final report.
- `_condamad/stories/CS-354-rapport-architecture-process-paralleles-legacy-prompt-llm/evidence/source-availability.txt` - source checks.
- `_condamad/stories/CS-354-rapport-architecture-process-paralleles-legacy-prompt-llm/evidence/validation.txt` - validation output.
- `_condamad/stories/CS-354-rapport-architecture-process-paralleles-legacy-prompt-llm/generated/11-code-review.md` - generated review handoff.

Likely tests:

- `_condamad/stories/CS-354-rapport-architecture-process-paralleles-legacy-prompt-llm/evidence/validation.txt` - assumption risk:
  report-only validation evidence replaces a new test file.
- Existing validation may run bounded `rg`, `python` and `git status` checks.

Files not expected to change:

- `backend/app/**` - out of scope; application runtime and service code remain unchanged.
- `backend/tests/**` - out of scope; tests are read or checked only.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no schema or migration work is touched.
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - out of scope for direct edits.
- `_condamad/stories/regression-guardrails.md` - out of scope for normal story implementation.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1:
  `python -c "from pathlib import Path; root=Path('_condamad/architecture/prompt-generation-document-review'); assert root.exists()"`
- VC2:
  `python -c "from pathlib import Path as P; root=P('_condamad/architecture/prompt-generation-document-review'); assert list(root.glob('*/archi-*.md'))"`
- VC3:
  `rg -n "archi-parallel-legacy-prompt-generation-report|Taxonomy|Decision par processus|Guardrails|provider-capable" _condamad/architecture/prompt-generation-document-review`
- VC4:
  `rg -n "nominal|parallele|legacy|fallback|bootstrap|test|admin" _condamad/architecture/prompt-generation-document-review`
- VC5:
  `rg -n "Executive architecture summary|Source map|Open questions produit ou technique" _condamad/architecture/prompt-generation-document-review`
- VC6:
  `rg -n "documenter|migrer|deprecier|supprimer|conserver|tester" _condamad/architecture/prompt-generation-document-review`
- VC7:
  `rg -n "CS-350|CS-351|CS-352|CS-353|Evidence gap|Open question" _condamad/architecture/prompt-generation-document-review`
- VC8:
  `python -c "from pathlib import Path; p=Path('_condamad/stories/CS-354-rapport-architecture-process-paralleles-legacy-prompt-llm/evidence/validation.txt'); assert p.exists()"`
- VC9:
  `git status --short -- backend/app backend/tests frontend/src backend/migrations`
- VC10:
  `git status --short -- _condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`

## Regression Risks

- The report may describe process families without making decisions.
- The report may confuse supported runtime paths with fallback, seed, test, admin or archive paths.
- The report may omit provider-capable non nominal paths from product decision questions.
- The report may propose vague guardrails that cannot be verified.
- The report may imply changes to CS-350 or runtime code, which are outside this story.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the repository Python venv before every Python command.
- Keep report citations short and path-based; do not paste long source blocks.
- Keep `backend/app`, `backend/tests`, `frontend/src`, `backend/migrations` and CS-350 documentation unchanged.
- Do not execute real LLM calls.
- Record unresolved source gaps as `Evidence gap` or `Open question`.

## References

- `_story_briefs/cs-354-archi-rapport-process-paralleles-legacy-generation-prompt-llm.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/audits/prompt-generation-document-review/**/01-adversarial-document-review-audit.md`
- `_condamad/audits/prompt-generation-document-review/**/02-code-document-concordance-audit.md`
- `_condamad/audits/prompt-generation-document-review/**/03-parallel-legacy-processes-audit.md`
- `_condamad/architecture/prompt-generation-cartography/**/architecture-prompt-generation-llm.md`
- `_condamad/reports/prompt-generation-cartography/**/report-prompt-generation-cartography.md`
