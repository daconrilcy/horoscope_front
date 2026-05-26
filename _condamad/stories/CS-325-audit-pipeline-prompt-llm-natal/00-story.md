# Story CS-325 audit-pipeline-prompt-llm-natal: Audit Pipeline Prompt LLM Natal
Status: ready-to-dev

## Trigger / Source

Audit-to-story source:
`_story_briefs/cs-325-audit-pipeline-prompt-llm-natal-legacy-vs-canonique.md`.

Problem statement: le pipeline natal peut transmettre des donnees astrologiques
au `LLMGateway` sans que toutes soient effectivement visibles dans le message
utilisateur envoye au provider LLM.

Source stakes:

- User impact: eviter une interpretation natale fondee sur un contexte moins
  riche que les donnees calculees ou refondues disponibles.
- Technical risk: confondre contexte runtime, validation par
  `evidence_catalog` et injection effective dans `build_user_payload`.
- Closure expectation: produire un audit reproductible du chemin
  `NatalInterpretationService` vers `LLMGateway`, sans modifier le prompt.
- Forbidden regression: aucune modification applicative, prompt, schema LLM,
  selection de modele, astrologues/personas, securite, CI ou cout provider.

Source-alignment evidence: the objective, ACs, tasks, evidence artifacts,
validation plan, non-goals and guardrails map back to the brief's required
questions, mandatory sources and audit deliverables.

## Objective

Produire un audit cible de la chaine d'injection LLM natale actuelle, avec une
separation explicite entre surfaces historiques et pipeline canonique cible.

L'audit doit expliquer quelles donnees entrent dans le `LLMGateway`, lesquelles
sont visibles par le message utilisateur, et comment `chart_json_in_prompt`
modifie la strategie d'injection de `chart_json`.

## Target State

Un dossier d'audit est cree sous:
`_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/`.

Il contient:

- `00-audit.md` avec la synthese, le flow runtime et les reponses aux questions
  obligatoires.
- `01-sequence.md` avec la sequence step-by-step depuis le service natal vers
  le gateway.
- `02-input-field-matrix.md` avec la matrice `input field -> producer ->
  consumer -> injection effective -> statut`.
- `03-branch-matrix.md` avec la comparaison `free/basic/premium`,
  `free_short`, `short`, `complete` et modules thematiques.
- `04-legacy-vs-canonical.md` avec la separation des surfaces historiques et
  du pipeline canonique cible.

Les artefacts citent explicitement les fichiers obligatoires du brief,
distinguent les champs visibles dans le prompt des champs seulement portes par
le runtime, et identifient les donnees aplaties, perdues ou converties en
labels.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-325-audit-pipeline-prompt-llm-natal-legacy-vs-canonique.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign the story number.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `backend/app/services/llm_generation/natal/interpretation_service.py` - mandatory natal service source exists.
- Evidence 5: `backend/app/domain/llm/runtime/adapter.py` - mandatory adapter source exists.
- Evidence 6: `backend/app/domain/llm/runtime/gateway.py` - mandatory gateway source exists.
- Evidence 7: `backend/tests/llm_orchestration` - mandatory LLM orchestration test root exists.
- Evidence 8: `_condamad/stories/CS-324-audit-calculs-interpretations-llm/00-story.md` - sibling LLM audit story inspected.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Audit of natal LLM input assembly in `NatalInterpretationService`.
  - Audit of `NatalExecutionInput` to `LLMExecutionRequest` mapping.
  - Audit of `LLMGateway._build_messages` and `build_user_payload` injection.
  - Audit of `free/basic/premium`, `free_short`, `short`, `complete` and
    thematic module branches.
  - Creation of `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/` artifacts.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling,
    migrations, prompt rewriting, prompt renderer changes and output schema changes.
- Explicit non-goals:
  - No prompt rewrite.
  - No `PromptRenderer` modification.
  - No LLM output schema change.
  - No use-case or model selection change.
  - No astrologer or persona domain change.
  - No security, CI or provider cost work.

Named brief primitives in scope:

- `NatalInterpretationService.interpret`
- `NatalExecutionInput`
- `AIEngineAdapter.generate_natal_interpretation`
- `LLMExecutionRequest`
- `LLMGateway._build_messages`
- `build_user_payload`
- `chart_json`
- `natal_data`
- `evidence_catalog`
- `astro_context`
- `plan`
- `level`
- `variant_code`
- `module`
- `chart_json_in_prompt`
- `Technical Data`
- `free_short`
- `short`
- `complete`
- thematic modules
- `free/basic/premium`
- routes `/users`
- simplified legacy payload
- fallback paths
- schema v1/v2/v3 compatibility

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend audit of
  natal LLM prompt injection and runtime data visibility.
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
  - Runtime-source references must distinguish producer, consumer and prompt
    injection visibility.
  - `pytest -q backend/tests/llm_orchestration` is validation evidence for
    unchanged LLM orchestration behavior, not a request to change tests.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Code owners and tests prove the actual natal LLM path before audit conclusions. |
| Baseline Snapshot | yes | The audit compares existing runtime fields with effective prompt injection. |
| Ownership Routing | yes | Each field must map to a precise producer and consumer owner. |
| Allowlist Exception | no | No allowlist handling is authorized for this audit-only story. |
| Contract Shape | yes | The audit deliverables have fixed files, matrices and classifications. |
| Batch Migration | no | No multi-file conversion is in scope. |
| Reintroduction Guard | yes | Prompt, runtime and gateway surfaces must stay unchanged. |
| Persistent Evidence | yes | Audit outputs and evidence logs must persist for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The runtime flow is documented. | Evidence profile: ast_architecture_guard; `AST guard`; `pytest -q backend/tests/llm_orchestration`. |
| AC2 | Prompt-visible fields are separated. | Evidence profile: json_contract_shape; `rg` checks `prompt-visible` in `02-input-field-matrix.md`. |
| AC3 | `chart_json_in_prompt` strategy is explained. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks `chart_json_in_prompt` in `00-audit.md`. |
| AC4 | Natal branches are compared. | Evidence profile: baseline_before_after_diff; `rg` checks branch and plan tiers in `03-branch-matrix.md`. |
| AC5 | Refactor data loss points are listed. | Evidence profile: ast_architecture_guard; `rg` checks `lost-or-flattened` in `04-legacy-vs-canonical.md`. |
| AC6 | Application code remains unchanged. | Evidence profile: repo_wide_negative_scan; `python` checks `git status --short -- backend/app backend/tests`. |
| AC7 | Audit artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks all five audit files exist. |
| AC8 | Orchestration tests stay green. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/llm_orchestration`. |

## Implementation Tasks

- [ ] Task 1: Read every mandatory source file and record bounded citations in the audit synthesis. (AC: AC1, AC2, AC3)
- [ ] Task 2: Trace the service-to-gateway sequence in `01-sequence.md`. (AC: AC1)
- [ ] Task 3: Build `02-input-field-matrix.md` for every named input field. (AC: AC2, AC3)
- [ ] Task 4: Compare `free/basic/premium`, `free_short`, `short`, `complete` and thematic module branches in `03-branch-matrix.md`. (AC: AC4)
- [ ] Task 5: Classify historical surfaces and canonical target candidates in `04-legacy-vs-canonical.md`. (AC: AC5)
- [ ] Task 6: Write `00-audit.md` with answers to all mandatory questions from the brief. (AC: AC1, AC2, AC3, AC4, AC5)
- [ ] Task 7: Run validation commands and persist command output in the audit folder. (AC: AC6, AC7, AC8)

## Files to Inspect First

- `_story_briefs/cs-325-audit-pipeline-prompt-llm-natal-legacy-vs-canonique.md`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/services/llm_generation/natal/prompt_context.py`
- `backend/app/services/llm_generation/shared/natal_context.py`
- `backend/app/domain/llm/runtime/contracts.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/domain/llm/prompting/context.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/tests/llm_orchestration/test_llm_gateway_compose.py`
- `backend/tests/llm_orchestration/test_llm_execution_request.py`
- `backend/tests/llm_orchestration/test_gateway_pipeline.py`
- `backend/tests/llm_orchestration/test_prompt_renderer.py`
- `backend/tests/llm_orchestration/test_placeholder_validation.py`
- `backend/app/tests/integration/test_llm_qa_runtime_contracts.py`

## Runtime Source of Truth

- Primary source of truth:
  - The listed backend source files and associated LLM orchestration tests.
  - `AST guard` or targeted `rg` scans over owners named in the brief.
- Secondary evidence:
  - `git status --short -- _condamad _story_briefs backend/app backend/tests`.
  - Audit citations with file paths, function names and short line references.
- Static scans alone are not sufficient for this story because:
  - The audit must prove data flow and prompt-message visibility from the
    actual runtime composition path.

## Contract Shape

- Contract type:
  - Audit artifact set, sequence and field-visibility matrix.
- Fields:
  - `input field`: field name passed through `NatalExecutionInput` or runtime context.
  - `producer`: precise source owner or function that creates the field.
  - `consumer`: precise source owner or function that consumes the field.
  - `injection effective`: `prompt-visible`, `runtime-only`, `validation-only` or `not-used`.
  - `statut`: `historical`, `canonical-target`, `transition`, `lost-or-flattened` or `out-of-scope`.
- Required fields:
  - `input field`
  - `producer`
  - `consumer`
  - `injection effective`
  - `statut`
- Optional fields:
  - none
- Status codes:
  - none; no API route is created or changed.
- Serialization names:
  - Audit matrix headings are emitted exactly as listed under required fields.
- Required files:
  - `00-audit.md`
  - `01-sequence.md`
  - `02-input-field-matrix.md`
  - `03-branch-matrix.md`
  - `04-legacy-vs-canonical.md`
- Required classification values:
  - `prompt-visible`
  - `runtime-only`
  - `validation-only`
  - `not-used`
  - `historical`
  - `canonical-target`
  - `transition`
  - `lost-or-flattened`
  - `out-of-scope`
- Frontend type impact:
  - none; no frontend generated client or UI surface is in scope.
- Generated contract impact:
  - none; no OpenAPI or generated manifest change is in scope.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `00-audit.md` records the source files and commands read for the audit.
- Comparison after implementation:
  - `02-input-field-matrix.md`, `03-branch-matrix.md` and
    `04-legacy-vs-canonical.md` contain the classified audit conclusions.
- Expected invariant:
  - The only intended repository delta is the audit artifact directory plus
    story execution evidence.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Natal input assembly evidence | `backend/app/services/llm_generation/natal/interpretation_service.py` | Prompt templates |
| Runtime contract evidence | `backend/app/domain/llm/runtime/contracts.py` | Audit-only conclusions without code owner |
| Adapter mapping evidence | `backend/app/domain/llm/runtime/adapter.py` | LLM provider clients |
| Prompt payload evidence | `backend/app/domain/llm/runtime/gateway.py` | Frontend code |
| Prompt rendering evidence | `backend/app/domain/llm/prompting/**` | Natal service code |
| Audit deliverables | `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/**` | Backend app or tests |

## Mandatory Reuse / DRY Constraints

- Reuse existing source owners as evidence instead of creating a second runtime vocabulary.
- Keep one canonical field matrix in `02-input-field-matrix.md`; other artifacts may reference it without duplicating all rows.
- Use the same branch names and classification values across all audit files.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy route, prompt or payload path may be added.
- No compatibility route, prompt or payload path may be added.
- No fallback route, prompt or payload path may be added.
- The audit must classify existing `/users`, simplified legacy payload,
  fallback and schema v1/v2/v3 compatibility behavior when present in the
  runtime evidence.
- Do not move application logic into audit artifacts.
- Do not add source aliases, shims or broad allowlists.
- Forbidden app surfaces for edits:
  - `backend/app/**`
  - `backend/tests/**`
  - `frontend/**`
  - prompt files and LLM gateway code

## Reintroduction Guard

- Guarded surfaces:
  - `backend/app/services/llm_generation/natal/**`
  - `backend/app/domain/llm/runtime/**`
  - `backend/app/domain/llm/prompting/**`
  - `backend/tests/llm_orchestration/**`
- Required guard:
  - `AST architecture guard` checks forbidden symbols before prompt, runtime or
    gateway changes are introduced.
  - `python` checks that `git status --short -- backend/app backend/tests`
    returns no changed application or test files.
  - `rg` checks audit artifacts contain required field names, branch names and
    prompt-visibility classifications.

## Regression Guardrails

Scope vector: operation `audit`, domain `backend-domain`, paths
`backend/app/services/llm_generation/natal`, `backend/app/domain/llm/runtime`,
`backend/app/domain/llm/prompting`, `backend/tests/llm_orchestration`, contracts
`llm-input` and `audit-artifacts`.

| Guardrail | Local invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend ownership must not drift into audit or API files. | `python` status guard; owner `rg`. |
| RG-022 `prompt-generation-validation-plans` | LLM validation plans must keep orchestration tests explicit. | `pytest`; `rg` test references. |
| RG-047 non-applicable | Frontend inline style rules are outside this backend audit scope. | Manual check: no `frontend` edits. |
| RG-052 non-applicable | Frontend CSS namespace rules are outside this backend audit scope. | Manual check: no style edits. |
| RG-041 non-applicable | Entitlement documentation is outside the natal LLM pipeline audit scope. | Manual check: no entitlement docs. |

Registry gap: no exact guardrail was found for natal prompt-injection audit
artifacts; the story records local invariants without editing the global
registry.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Audit synthesis | `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/00-audit.md` | Keep findings and answers. |
| Runtime sequence | `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/01-sequence.md` | Keep step-by-step flow. |
| Field matrix | `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/02-input-field-matrix.md` | Keep field visibility. |
| Branch matrix | `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/03-branch-matrix.md` | Keep branch comparison. |
| Legacy register | `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/04-legacy-vs-canonical.md` | Keep classification. |
| Validation output | `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/validation-output.md` | Keep command output. |
| Review output | `_condamad/stories/CS-325-audit-pipeline-prompt-llm-natal/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this audit-only story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/00-audit.md` - audit synthesis and required answers.
- `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/01-sequence.md` - service-to-gateway sequence.
- `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/02-input-field-matrix.md` - field matrix.
- `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/03-branch-matrix.md` - branch matrix.
- `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/04-legacy-vs-canonical.md` - historical and canonical register.
- `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/validation-output.md` - validation output.

Likely tests:

- No new tests are expected because the story is audit-only.
- Existing validation may run `pytest -q backend/tests/llm_orchestration`.

Files not expected to change:

- `backend/app/**` - out of scope; application runtime and service code remain unchanged.
- `backend/tests/**` - out of scope; tests are read or run only.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `_condamad/stories/regression-guardrails.md` - out of scope for normal story implementation.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1:
  `rg -n "NatalInterpretationService|NatalExecutionInput|AIEngineAdapter" _condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000`
  puis `rg -n "generate_natal_interpretation|LLMGateway._build_messages" _condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000`.
- VC2:
  `rg -n "chart_json|natal_data|evidence_catalog|astro_context|plan|level|variant_code|module" _condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000`
- VC3:
  `rg -n "prompt-visible|runtime-only|validation-only|not-used|lost-or-flattened" _condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000`
- VC3b:
  `rg -n "/users|simplified legacy payload|fallback|schema v1|schema v2|schema v3" _condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000`
- VC4:
  `python -c "from pathlib import Path; root=Path('_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000'); assert root.exists()"`
- VC5:
  `python -c "import subprocess; out=subprocess.check_output(['git','status','--short','--','backend/app','backend/tests'], text=True); assert out.strip() == ''"`
- VC6:
  `rg -n "NatalExecutionInput|generate_natal_interpretation|LLMExecutionRequest|build_user_payload" .\backend\app .\backend\tests`
  puis `rg -n "chart_json_in_prompt|Technical Data|astro_context|evidence_catalog|variant_code|module" .\backend\app .\backend\tests`.
- VC7: `git status --short -- _condamad _story_briefs backend/app backend/tests`
- VC8: `pytest -q backend/tests/llm_orchestration`
- VC9: `ruff format --check .`
- VC10: `ruff check .`

## Regression Risks

- The audit may treat every runtime field as prompt-visible without proving
  message composition.
- The audit may miss the `{{chart_json}}` placeholder branch and overstate
  automatic `Technical Data` injection.
- The audit may conflate `evidence_catalog` validation with generation
  constraint.
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
  `00-audit.md`.
- Keep `backend/app`, `backend/tests` and `frontend` unchanged.

## References

- `_story_briefs/cs-325-audit-pipeline-prompt-llm-natal-legacy-vs-canonique.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-324-audit-calculs-interpretations-llm/00-story.md`
