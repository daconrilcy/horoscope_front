# Story CS-324 audit-calculs-interpretations-llm: Audit Calculs Et Interpretations Vers LLM
Status: ready-to-dev

## Trigger / Source

Brief direct source:
`_story_briefs/cs-324-audit-surfaces-calculs-interpretations-vers-llm.md`.

Problem statement: les prompts LLM natals consomment des surfaces multiples
dont le statut canonique, historique ou de transition doit etre cartographie
avant toute evolution de prompt ou de runtime.

Source stakes:

- User impact: eviter une narration LLM fondee sur des donnees pauvres ou
  inventees.
- Technical risk: confondre projection publique historique et source de verite
  recente du runtime astrologique.
- Closure expectation: produire un audit actionnable, reproductible et cite,
  sans changement applicatif.
- Forbidden regression: aucune modification de prompt, generateur LLM, contrat
  public, securite, CI, astrologues ou runtime.

Source-alignment evidence: the objective, ACs, tasks, evidence artifacts,
validation plan, non-goals and guardrails map back to the brief's required
questions, mandatory sources and audit deliverables.

## Objective

Produire un audit cible des surfaces backend qui portent les calculs natals,
les enrichissements interpretatifs et les donnees effectivement injectees dans
la generation LLM natale.

L'audit doit appliquer toutes les classes demandees par le brief, puis expliquer
les ecarts entre calculs disponibles et entree LLM actuelle.

## Target State

Un dossier d'audit est cree sous:
`_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/`.

Il contient:

- `00-audit.md` avec la synthese, les reponses aux questions obligatoires et
  les conclusions actionnables.
- `01-evidence-log.md` avec les commandes, fichiers lus et extraits courts
  cites.
- `02-surface-matrix.md` avec la matrice `surface -> owner -> type -> contenu
  -> consommateur LLM actuel -> potentiel cible`.
- `03-gap-register.md` avec les ecarts entre donnees disponibles et donnees
  injectees LLM.
- `04-legacy-register.md` avec les surfaces `legacy` ou `transition` encore
  dans la chaine.

Les artefacts citent explicitement les owners code imposes par le brief,
enumerent les champs passes a `NatalExecutionInput`, et identifient les owners
recents non exploites par l'injection LLM.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-324-audit-surfaces-calculs-interpretations-vers-llm.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign the story number.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - mandatory runtime source exists.
- Evidence 5: `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` - mandatory narrative input source exists.
- Evidence 6: `backend/app/services/llm_generation/natal/interpretation_service.py` - mandatory LLM gateway source exists.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver and targeted ID lookup.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Audit of backend astrology runtime calculation surfaces.
  - Audit of interpretation input, structured facts, narrative input and client
    projection builders.
  - Audit of LLM natal execution inputs and evidence catalog construction.
  - Creation of `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/` artifacts.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling,
    migrations, prompt changes, LLM gateway changes and runtime changes.
- Explicit non-goals:
  - No prompt rewrite.
  - No generator modification.
  - No public contract change.
  - No new projection.
  - No source cleanup.
  - No security, CI or astrologer domain change.

Named brief primitives in scope:

- `ChartObjectRuntimeData`, `CalculationGraph`,
  `ChartInterpretationInputBuilder`, `structured_facts_v1`,
  `client_interpretation_projection_v1`, `AINarrativeInputContract`,
  `chart_json`, `natal_data`, `astro_context`, `evidence_catalog` and
  `NatalExecutionInput`.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend audit of
  calculation, interpretation and LLM input surfaces.
- Behavior change allowed: no
- Behavior change constraints:
  - Create only audit and story evidence artifacts.
  - Keep backend application files unchanged.
  - Keep backend test files unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: a mandatory source file from the brief cannot be
  read in the implementation workspace.
- Additional validation rules:
  - `AST guard` or bounded `rg` evidence must prove no application source was
    modified.
  - Runtime-source references must distinguish code owners from generated audit
    conclusions.
  - `pytest -q backend/tests/unit/domain/astrology` is validation evidence for
    unchanged astrology behavior, not a request to change tests.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Code owners and tests prove what data exists before LLM prompt entry. |
| Baseline Snapshot | yes | The audit compares available surfaces with current LLM inputs. |
| Ownership Routing | yes | The audit must assign every surface to a precise code owner. |
| Allowlist Exception | no | No allowlist handling is authorized for this audit-only story. |
| Contract Shape | yes | The audit deliverables have fixed files, matrices and registers. |
| Batch Migration | no | No multi-file conversion is in scope. |
| Reintroduction Guard | yes | Prompt, runtime and public contract surfaces must stay unchanged. |
| Persistent Evidence | yes | Audit outputs and evidence logs must persist for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The audit applies the required class vocabulary. | Evidence profile: baseline_before_after_diff; `rg` checks the five classes in `00-audit.md`. |
| AC2 | Every audited surface has a precise owner. | Evidence profile: ast_architecture_guard; `python` checks `02-surface-matrix.md` rows include owner paths. |
| AC3 | `NatalExecutionInput` fields are enumerated. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks `NatalExecutionInput` in `00-audit.md`. |
| AC4 | Recent unused owners are identified. | Evidence profile: ast_architecture_guard; `rg` checks `03-gap-register.md` for `recent-refonte`. |
| AC5 | Application code remains unchanged. | Evidence profile: repo_wide_negative_scan; `python` checks `git status --short -- backend/app backend/tests`. |
| AC6 | The audit artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks all five audit files exist. |
| AC7 | Source-alignment evidence is preserved. | Evidence profile: baseline_before_after_diff; `rg` checks required questions in `01-evidence-log.md`. |

## Implementation Tasks

- [ ] Task 1: Read every mandatory source file and record bounded citations in `01-evidence-log.md`. (AC: AC1, AC2, AC7)
- [ ] Task 2: Enumerate calculation, interpretation, projection and LLM input surfaces in `02-surface-matrix.md`. (AC: AC1, AC2)
- [ ] Task 3: Enumerate fields passed to `NatalExecutionInput` from the LLM natal service path. (AC: AC3)
- [ ] Task 4: Compare canonical runtime owners with current LLM input owners in `03-gap-register.md`. (AC: AC4)
- [ ] Task 5: Classify historical public projections and transition surfaces in `04-legacy-register.md`. (AC: AC1)
- [ ] Task 6: Write `00-audit.md` with answers to all mandatory questions and architecture-ready conclusions. (AC: AC1, AC4, AC7)
- [ ] Task 7: Run validation commands and persist command output in the audit evidence log. (AC: AC5, AC6)

## Files to Inspect First

- `_story_briefs/cs-324-audit-surfaces-calculs-interpretations-vers-llm.md`
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `backend/app/domain/astrology/runtime/calculation_graph_runner.py`
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py`
- `backend/app/domain/astrology/runtime/natal_result_assembler.py`
- `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py`
- `backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py`
- `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`
- `backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py`
- `backend/tests/unit/domain/astrology/interpretation/test_chart_interpretation_input_builder.py`
- `backend/tests/unit/domain/astrology/interpretation/test_ai_narrative_input_contract.py`
- `backend/tests/unit/domain/astrology/test_structured_facts_v1_builder.py`
- `backend/tests/unit/domain/astrology/test_client_interpretation_projection_v1_builder.py`

## Runtime Source of Truth

- Primary source of truth:
  - The listed backend source files and associated unit tests.
  - `AST guard` or targeted `rg` scans over owners named in the brief.
- Secondary evidence:
  - `git status --short -- _condamad _story_briefs backend/app backend/tests`.
  - Audit evidence log citations with file paths and line references.
- Static scans alone are not sufficient for this story because:
  - The audit must prove data ownership and consumer direction from the actual
    code owners before forming conclusions.

## Contract Shape

- Contract type:
  - Audit artifact set and evidence matrix.
- Fields:
  - `surface`: audited backend data surface name.
  - `owner`: precise source file or test owner path.
  - `type`: structural, pre-interpretative, narrative, public, debug or internal.
  - `contenu`: bounded description of available data.
  - `consommateur LLM actuel`: current LLM consumer status.
  - `potentiel cible`: target-candidate usage or out-of-scope reason.
- Required fields:
  - `surface`
  - `owner`
  - `type`
  - `contenu`
  - `consommateur LLM actuel`
  - `potentiel cible`
- Optional fields:
  - none
- Status codes:
  - none; no API route is created or changed.
- Serialization names:
  - Audit matrix headings are emitted exactly as listed under required fields.
- Required files:
  - `00-audit.md`
  - `01-evidence-log.md`
  - `02-surface-matrix.md`
  - `03-gap-register.md`
  - `04-legacy-register.md`
- Required classification values:
  - `legacy`
  - `recent-refonte`
  - `transition`
  - `target-candidate`
  - `out-of-scope`
- Required matrix columns:
  - `surface`
  - `owner`
  - `type`
  - `contenu`
  - `consommateur LLM actuel`
  - `potentiel cible`
- Frontend type impact:
  - none; no frontend generated client or UI surface is in scope.
- Generated contract impact:
  - none; no OpenAPI or generated manifest change is in scope.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `01-evidence-log.md` records the initial source files and commands read for
    the audit.
- Comparison after implementation:
  - `02-surface-matrix.md`, `03-gap-register.md` and `04-legacy-register.md`
    contain the classified audit conclusions.
- Expected invariant:
  - The only intended repository delta is the audit artifact directory plus
    story execution evidence.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Runtime calculation evidence | `backend/app/domain/astrology/runtime/**` | Prompt templates or frontend code |
| Interpretation input evidence | `backend/app/domain/astrology/interpretation/**` | LLM provider adapters |
| Chart JSON projection evidence | `backend/app/services/chart/json_builder.py` | New projection modules |
| Natal LLM input evidence | `backend/app/services/llm_generation/natal/interpretation_service.py` | Prompt text files |
| Audit deliverables | `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/**` | Backend app or tests |

## Mandatory Reuse / DRY Constraints

- Reuse the existing owners and tests as evidence sources instead of creating a
  second audit vocabulary.
- Keep one canonical surface matrix in `02-surface-matrix.md`; other artifacts
  may reference it without duplicating all rows.
- Use the same classification values across all audit files.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy route, prompt or projection path may be added.
- No compatibility route, prompt or projection path may be added.
- No fallback route, prompt or projection path may be added.
- Do not move application logic into audit artifacts.
- Do not add source aliases, shims or broad allowlists.
- Forbidden app surfaces for edits:
  - `backend/app/**`
  - `backend/tests/**`
  - `frontend/**`
  - prompt files and LLM gateway code

## Reintroduction Guard

- Guarded surfaces:
  - `backend/app/domain/astrology/runtime/**`
  - `backend/app/domain/astrology/interpretation/**`
  - `backend/app/services/chart/json_builder.py`
  - `backend/app/services/llm_generation/natal/interpretation_service.py`
- Required guard:
  - `AST architecture guard` checks forbidden symbols before prompt, runtime or
    public contract changes are reintroduced.
  - `python` checks that `git status --short -- backend/app backend/tests`
    returns no changed application or test files.
  - `rg` checks audit artifacts contain the mandatory classes and named LLM
    input surfaces.

## Regression Guardrails

Scope vector: operation `audit`, domain `backend-domain`, paths
`backend/app/domain/astrology/runtime`, `backend/app/domain/astrology/interpretation`,
`backend/app/services/chart`, `backend/app/services/llm_generation/natal`,
contract `llm-input`.

| Guardrail | Local invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend app ownership must not be blurred into API or audit files. | `rg` owner scan; `python` status guard. |
| RG-047 non-applicable | Frontend inline style rules are outside this backend audit scope. | Manual check: no `frontend` edits. |
| RG-052 non-applicable | Frontend CSS namespace convergence is outside this backend audit scope. | Manual check: no style edits. |
| RG-041 non-applicable | Entitlement documentation is outside the LLM astrology audit scope. | Manual check: no entitlement docs. |

Registry gap: no exact guardrail was found for natal LLM calculation-surface
audit artifacts; the story records local invariants without editing the global
registry.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Audit synthesis | `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/00-audit.md` | Keep findings and answers to mandatory questions. |
| Evidence log | `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/01-evidence-log.md` | Keep commands, files and short cited extracts. |
| Surface matrix | `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/02-surface-matrix.md` | Keep owner and classification matrix. |
| Gap register | `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/03-gap-register.md` | Keep unavailable or unused target data gaps. |
| Legacy register | `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/04-legacy-register.md` | Keep historical and transition surfaces. |
| Validation output | `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/validation-output.md` | Keep validation command output for review. |
| Review output | `_condamad/stories/CS-324-audit-calculs-interpretations-llm/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this audit-only story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/00-audit.md` - audit synthesis and required answers.
- `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/01-evidence-log.md` - commands, files and cited excerpts.
- `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/02-surface-matrix.md` - surface matrix.
- `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/03-gap-register.md` - gap register.
- `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/04-legacy-register.md` - historical and transition register.
- `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/validation-output.md` - validation output.

Likely tests:

- No new tests are expected because the story is audit-only.
- Existing validation may run `pytest -q backend/tests/unit/domain/astrology`.

Files not expected to change:

- `backend/app/**` - out of scope; application runtime and service code remain unchanged.
- `backend/tests/**` - out of scope; tests are read or run only.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `_condamad/stories/regression-guardrails.md` - out of scope for normal story implementation.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `rg -n "legacy|recent-refonte|transition|target-candidate|out-of-scope" _condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000`
- VC2: `rg -n "NatalExecutionInput|chart_json|natal_data|astro_context|evidence_catalog" _condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000`
- VC3:
  `python -c "from pathlib import Path; root=Path('_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000'); assert root.exists()"`
  puis verifier les cinq fichiers d'audit avec le meme controle `python`.
- VC4: `python -c "import subprocess; out=subprocess.check_output(['git','status','--short','--','backend/app','backend/tests'], text=True); assert out.strip() == ''"`
- VC5:
  `rg -n "build_chart_json|build_enriched_evidence_catalog|NatalExecutionInput|astro_context|structured_facts_v1" .\backend\app .\backend\tests`
  puis `rg` pour `AINarrativeInput`, `client_interpretation_projection_v1`,
  `ChartInterpretationInputBuilder`, `ChartObjectRuntimeData` et `CalculationGraph`.
- VC6: `git status --short -- _condamad _story_briefs backend/app backend/tests`
- VC7: `pytest -q backend/tests/unit/domain/astrology`
- VC8: `ruff format .`
- VC9: `ruff check .`

## Regression Risks

- The audit may overstate a projection as canonical without proving owner
  direction from code.
- The audit may duplicate classifications across files and create conflicting
  conclusions.
- The audit may miss a LLM input field that is assembled indirectly before
  `NatalExecutionInput`.
- The audit may create app or test changes while trying to prove current state.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the repository Python venv before every Python, pytest or ruff
  command.
- Keep audit citations short and path-based; do not paste long source blocks.
- Record any source file that cannot be read as an explicit blocker in
  `01-evidence-log.md`.
- Keep `backend/app`, `backend/tests` and `frontend` unchanged.

## References

- `_story_briefs/cs-324-audit-surfaces-calculs-interpretations-vers-llm.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/regression-guardrails.md`
