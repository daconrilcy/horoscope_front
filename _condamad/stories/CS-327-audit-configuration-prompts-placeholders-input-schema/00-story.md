# Story CS-327 audit-configuration-prompts-placeholders-input-schema: Audit Configuration Prompts Placeholders Input Schema
Status: ready-to-dev

## Trigger / Source

Audit-to-story source:
`_story_briefs/cs-327-audit-configuration-prompts-placeholders-input-schema.md`.

Problem statement: la configuration LLM natale peut encore imposer une entree
astrologique historique comme `chart_json`, alors que les prochains contrats
doivent pouvoir injecter des faits, signaux, limites et preuves structures.

Source stakes:

- User impact: eviter une narration LLM fondee sur une entree appauvrie ou
  inventee par manque de schema d'injection explicite.
- Technical risk: confondre placeholders, assemblies, schemas d'entree,
  renderer et payload runtime dans une seule hypothese non prouvee.
- Closure expectation: produire un audit reproductible et cite de la
  configuration LLM, sans implementation du nouveau contrat.
- Forbidden regression: aucune modification de prompt, provider, astrologue,
  securite, CI, frontend, schema DB ou contrat public.

Source-alignment evidence: the objective, ACs, tasks, evidence artifacts,
validation plan, non-goals and guardrails map back to the brief's required
questions, mandatory sources and audit deliverables.

## Objective

Produire un audit cible de la capacite des configurations LLM natales a
recevoir une entree astrologique structuree moderne.

L'audit doit inventorier les placeholders, schemas d'entree, assemblies, use
cases, renderer et chemins `chart_json`, puis classer chaque point comme
`compatible`, `partiel`, `bloquant` ou `legacy fallback`.

## Target State

Un dossier d'audit est cree sous:
`_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000/`.

Il contient:

- `00-audit.md` avec la synthese, les reponses aux questions obligatoires et
  les conclusions actionnables.
- `01-use-case-matrix.md` avec la matrice des use cases natals actifs et
  modules thematiques.
- `02-placeholder-schema-matrix.md` avec la matrice placeholders, input
  schemas et validations.
- `03-legacy-fallbacks.md` avec les chemins `chart_json` et fallback qui
  impactent l'injection cible.
- `04-readiness.md` avec la capacite a recevoir un contrat
  `llm_astrology_input` ou equivalent.

Les artefacts citent explicitement les fichiers obligatoires du brief,
separent blockers de configuration et blockers de donnees, puis concluent sans
modifier la configuration applicative.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-327-audit-configuration-prompts-placeholders-input-schema.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign the story number.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `backend/app/domain/llm/configuration/assemblies.py` - mandatory configuration source exists.
- Evidence 5: `backend/app/domain/llm/prompting/prompt_renderer.py` - mandatory renderer source exists.
- Evidence 6: `backend/app/domain/llm/runtime/input_validation.py` - mandatory runtime validation source exists.
- Evidence 7: `backend/app/ops/llm/bootstrap` and `backend/tests/llm_orchestration` - mandatory audit roots exist.
- Evidence 8: `_condamad/stories/CS-324-audit-calculs-interpretations-llm/00-story.md` - sibling LLM audit story inspected.
- Evidence 9: `_condamad/stories/CS-325-audit-pipeline-prompt-llm-natal/00-story.md` - sibling prompt audit story inspected.
- Evidence 10: `_condamad/stories/CS-326-audit-projections-interpretatives-llm-input-readiness/00-story.md` - sibling readiness story inspected.
- Evidence 11: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Audit of LLM use-case registry, prompt versions, assemblies and assembly
    resolution.
  - Audit of prompt placeholders, input schemas, input validation and
    `PromptRenderer` rendering constraints.
  - Audit of `build_user_payload`, `chart_json`, `natal_data`, `astro_context`
    and possible `llm_astrology_input` injection readiness.
  - Creation of the audit artifacts under the target `_condamad/audits` path.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling,
    migrations, provider changes, prompt copy edits and new injection runtime.
- Explicit non-goals:
  - No prompt text rewrite.
  - No provider modification.
  - No astrologer or persona modification.
  - No security, CI or release governance work.
  - No implementation of the target injection contract.
  - No application source or test modification.

Named brief primitives in scope:

- `required_prompt_placeholders`
- `input_schema`
- `PromptRenderer`
- `build_user_payload`
- `chart_json`
- `natal_data`
- `astro_context`
- `llm_astrology_input`
- `prompt_version`
- `assembly`
- `natal_interpretation`
- `natal_long_free`
- use-case registry
- prompt versions
- assemblies
- prompt renderer
- input validation
- output schemas
- placeholders requis
- legacy fallback

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend audit of
  LLM configuration, prompt placeholders and input-schema readiness.
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
  - Runtime-source references must distinguish configuration support from
    actual prompt payload injection.
  - `pytest -q backend/tests/llm_orchestration` is validation evidence for
    unchanged LLM orchestration behavior, not a request to change tests.
  - The audit must classify configuration blockers separately from data
    blockers.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Code owners and orchestration tests prove current configuration behavior. |
| Baseline Snapshot | yes | The audit compares current placeholders and schemas with target injection needs. |
| Ownership Routing | yes | Each config surface must map to a precise owner path. |
| Allowlist Exception | no | No allowlist handling is authorized for this audit-only story. |
| Contract Shape | yes | The audit deliverables have fixed files, matrices and readiness values. |
| Batch Migration | no | No multi-file conversion is in scope. |
| Reintroduction Guard | yes | Prompt, provider, runtime and app code surfaces must stay unchanged. |
| Persistent Evidence | yes | Audit outputs and evidence logs must persist for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Active natal use cases are listed. | Evidence profile: baseline_before_after_diff; `rg` checks use-case names in `01-use-case-matrix.md`. |
| AC2 | Astrology placeholders are inventoried. | Evidence profile: json_contract_shape; `rg` checks placeholder tokens in `02-placeholder-schema-matrix.md`. |
| AC3 | Input schemas are documented. | Evidence profile: ast_architecture_guard; `rg` checks `input_schema` and validation owners in `02-placeholder-schema-matrix.md`. |
| AC4 | `chart_json` dependencies are identified. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks `chart_json` in `03-legacy-fallbacks.md`. |
| AC5 | Blocker classes are separated. | Evidence profile: json_contract_shape; `rg` checks `configuration-blocker` and `data-blocker` in `04-readiness.md`. |
| AC6 | Application code remains unchanged. | Evidence profile: repo_wide_negative_scan; `python` checks `git status --short -- backend/app backend/tests`. |
| AC7 | Audit artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks all five audit files exist. |
| AC8 | Renderer constraints are documented. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/llm_orchestration`; `rg` checks renderer constraints. |
| AC9 | Target injection readiness is classified. | Evidence profile: json_contract_shape; `rg` checks `compatible|partiel|bloquant|legacy fallback` in `04-readiness.md`. |

## Implementation Tasks

- [ ] Task 1: Read every mandatory source file and record bounded citations in `00-audit.md`. (AC: AC1, AC2, AC3)
- [ ] Task 2: Build `01-use-case-matrix.md` for active natal use cases and thematic modules. (AC: AC1)
- [ ] Task 3: Build `02-placeholder-schema-matrix.md` for placeholders, schemas and validation owners. (AC: AC2, AC3)
- [ ] Task 4: Trace `chart_json`, `natal_data`, `astro_context` and fallback paths in `03-legacy-fallbacks.md`. (AC: AC4)
- [ ] Task 5: Classify readiness for `llm_astrology_input` or equivalent in `04-readiness.md`. (AC: AC5, AC9)
- [ ] Task 6: Document renderer constraints for multiple blocks: facts, signals, limits and proofs. (AC: AC8)
- [ ] Task 7: Run validation commands and persist command output in the audit folder. (AC: AC6, AC7, AC8)

## Files to Inspect First

- `_story_briefs/cs-327-audit-configuration-prompts-placeholders-input-schema.md`
- `backend/app/domain/llm/configuration/assemblies.py`
- `backend/app/domain/llm/configuration/assembly_registry.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/configuration/prompt_versions.py`
- `backend/app/domain/llm/configuration/prompt_version_lookup.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/domain/llm/prompting/catalog.py`
- `backend/app/domain/llm/runtime/input_validation.py`
- `backend/app/domain/llm/runtime/input_validator.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/ops/llm/bootstrap/**`
- `backend/tests/llm_orchestration/**`
- `_condamad/stories/CS-324-audit-calculs-interpretations-llm/00-story.md`
- `_condamad/stories/CS-325-audit-pipeline-prompt-llm-natal/00-story.md`
- `_condamad/stories/CS-326-audit-projections-interpretatives-llm-input-readiness/00-story.md`

## Runtime Source of Truth

- Primary source of truth:
  - The listed backend configuration, prompting and runtime source files.
  - `backend/tests/llm_orchestration/**` for runtime orchestration behavior.
  - `AST guard` or targeted `rg` scans over owners named in the brief.
- Secondary evidence:
  - `git status --short -- _condamad _story_briefs backend/app backend/tests`.
  - Audit citations with file paths, symbols and short line references.
- Static scans alone are not sufficient for this story because:
  - The audit must prove schema, placeholder and renderer relationships from
    the actual runtime configuration path.

## Contract Shape

- Contract type:
  - Audit artifact set, use-case matrix, placeholder-schema matrix and
    readiness classification.
- Fields:
  - `use case`: canonical use-case identifier or thematic module.
  - `prompt config`: prompt version, assembly or catalog owner.
  - `input schema`: schema owner and expected astrology fields.
  - `placeholders`: required prompt placeholders tied to astrology data.
  - `readiness injection`: `compatible`, `partiel`, `bloquant` or `legacy fallback`.
  - `blocker type`: `configuration-blocker`, `data-blocker` or `none`.
- Required fields:
  - `use case`
  - `prompt config`
  - `input schema`
  - `placeholders`
  - `readiness injection`
  - `blocker type`
- Optional fields:
  - none
- Status codes:
  - none; no API route is created or changed.
- Serialization names:
  - Audit matrix headings are emitted exactly as listed under required fields.
- Required files:
  - `00-audit.md`
  - `01-use-case-matrix.md`
  - `02-placeholder-schema-matrix.md`
  - `03-legacy-fallbacks.md`
  - `04-readiness.md`
- Required classification values:
  - `compatible`
  - `partiel`
  - `bloquant`
  - `legacy fallback`
  - `configuration-blocker`
  - `data-blocker`
  - `none`
- Frontend type impact:
  - none; no frontend generated client or UI surface is in scope.
- Generated contract impact:
  - none; no OpenAPI or generated manifest change is in scope.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `00-audit.md` records the source files and commands read for the audit.
- Comparison after implementation:
  - `01-use-case-matrix.md`, `02-placeholder-schema-matrix.md`,
    `03-legacy-fallbacks.md` and `04-readiness.md` contain the classified
    audit conclusions.
- Expected invariant:
  - The only intended repository delta is the audit artifact directory plus
    story execution evidence.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Use-case registry evidence | `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | Audit-only invented registry |
| Assembly evidence | `backend/app/domain/llm/configuration/assemblies.py` | Prompt renderer code |
| Assembly resolution evidence | `backend/app/domain/llm/configuration/assembly_resolver.py` | Provider adapters |
| Prompt version evidence | `backend/app/domain/llm/configuration/prompt_versions.py` | Runtime gateway code |
| Placeholder rendering evidence | `backend/app/domain/llm/prompting/prompt_renderer.py` | Frontend code |
| Runtime validation evidence | `backend/app/domain/llm/runtime/input_validation.py` | Prompt text files |
| Audit deliverables | `_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000/**` | Backend app or tests |

## Mandatory Reuse / DRY Constraints

- Reuse existing use-case, prompt version, assembly and placeholder names from
  source owners.
- Keep one canonical use-case matrix in `01-use-case-matrix.md`; other audit
  files may reference it without duplicating every row.
- Keep one canonical placeholder-schema matrix in
  `02-placeholder-schema-matrix.md`.
- Use the same readiness and blocker classification values across all audit
  files.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy route, prompt or payload path may be added.
- No compatibility route, prompt or payload path may be added.
- No fallback route, prompt or payload path may be added.
- The audit must classify existing `chart_json` and fallback behavior from
  evidence before recommending a target contract.
- Do not move application logic into audit artifacts.
- Do not add source aliases, shims or broad allowlists.
- Forbidden app surfaces for edits:
  - `backend/app/**`
  - `backend/tests/**`
  - `frontend/**`
  - prompt files, provider adapters and runtime gateway code

## Reintroduction Guard

- Guarded surfaces:
  - `backend/app/domain/llm/configuration/**`
  - `backend/app/domain/llm/prompting/**`
  - `backend/app/domain/llm/runtime/**`
  - `backend/app/ops/llm/bootstrap/**`
  - `backend/tests/llm_orchestration/**`
- Required guard:
  - `AST architecture guard` checks forbidden symbols before prompt,
    configuration or runtime changes are introduced.
  - `python` checks that `git status --short -- backend/app backend/tests`
    returns no changed application or test files.
  - `rg` checks audit artifacts contain required placeholders, schemas,
    readiness classifications and blocker classes.

## Regression Guardrails

Scope vector: operation `audit`, domain `backend-domain`, paths
`backend/app/domain/llm/configuration`, `backend/app/domain/llm/prompting`,
`backend/app/domain/llm/runtime`, `backend/app/ops/llm/bootstrap`,
`backend/tests/llm_orchestration`, contracts `llm-input-schema`,
`prompt-placeholders` and `audit-artifacts`.

| Guardrail | Local invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend ownership must not drift into audit or API files. | `python` status guard; owner `rg`. |
| RG-022 `prompt-generation-validation-plans` | LLM config validation must keep orchestration tests explicit. | `pytest`; `rg` test references. |
| RG-047 non-applicable | Frontend inline style rules are outside this backend audit scope. | Manual check: no `frontend` edits. |
| RG-052 non-applicable | Frontend CSS namespace rules are outside this backend audit scope. | Manual check: no style edits. |
| RG-041 non-applicable | Entitlement documentation is outside the LLM configuration audit. | Manual check: no entitlement docs. |

Registry gap: no exact guardrail was found for prompt placeholder and input
schema readiness audit artifacts; the story records local invariants without
editing the global registry.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Audit synthesis | `_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000/00-audit.md` | Keep findings and answers. |
| Use-case matrix | `_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000/01-use-case-matrix.md` | Keep use-case mapping. |
| Placeholder matrix | `_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000/02-placeholder-schema-matrix.md` | Keep schema mapping. |
| Legacy register | `_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000/03-legacy-fallbacks.md` | Keep legacy findings. |
| Readiness report | `_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000/04-readiness.md` | Keep readiness result. |
| Validation output | `_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000/validation-output.md` | Keep command output. |
| Review output | `_condamad/stories/CS-327-audit-configuration-prompts-placeholders-input-schema/generated/11-code-review.md` | Keep automatic review output. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this audit-only story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000/00-audit.md` - synthesis and required answers.
- `_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000/01-use-case-matrix.md` - use-case matrix.
- `_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000/02-placeholder-schema-matrix.md` - placeholder schema matrix.
- `_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000/03-legacy-fallbacks.md` - legacy and fallback register.
- `_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000/04-readiness.md` - readiness report.
- `_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000/validation-output.md` - validation output.

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
  `rg -n "required_prompt_placeholders|input_schema|PromptRenderer" _condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000`
- VC2:
  `rg -n "chart_json|natal_data|astro_context|llm_astrology_input" _condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000`
- VC3:
  `rg -n "compatible|partiel|bloquant|legacy fallback" _condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000`
- VC4:
  `rg -n "configuration-blocker|data-blocker|facts|signals|limits|proofs" _condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000`
- VC5:
  `python -c "from pathlib import Path; root=Path('_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000'); assert root.exists()"`
- VC6:
  `python -c "import subprocess; out=subprocess.check_output(['git','status','--short','--','backend/app','backend/tests'], text=True); assert out.strip() == ''"`
- VC7:
  `rg -n "required_prompt_placeholders|input_schema|chart_json|natal_data|astro_context" .\backend\app .\backend\tests`
  puis `rg -n "prompt_version|assembly|natal_interpretation|natal_long_free|PromptRenderer" .\backend\app .\backend\tests`.
- VC8: `git status --short -- _condamad _story_briefs backend/app backend/tests`
- VC9: `pytest -q backend/tests/llm_orchestration`
- VC10: `ruff format .`
- VC11: `ruff check .`

## Regression Risks

- The audit may treat placeholder presence as proof that structured
  astrology data can be injected.
- The audit may miss an assembly branch that bypasses prompt input validation.
- The audit may confuse output schemas with input schemas and overstate
  readiness.
- The audit may create application changes while trying to prove current
  configuration behavior.

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

- `_story_briefs/cs-327-audit-configuration-prompts-placeholders-input-schema.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-324-audit-calculs-interpretations-llm/00-story.md`
- `_condamad/stories/CS-325-audit-pipeline-prompt-llm-natal/00-story.md`
- `_condamad/stories/CS-326-audit-projections-interpretatives-llm-input-readiness/00-story.md`
