# Story CS-326 audit-projections-interpretatives-llm-input-readiness: Audit Projections Interpretatives LLM Input Readiness
Status: ready-to-dev

## Trigger / Source

Audit-to-story source:
`_story_briefs/cs-326-audit-projections-interpretatives-llm-input-readiness.md`.

Problem statement: les projections interpretatives recentes peuvent sembler
pretes pour l'injection LLM, mais leur statut exact doit etre audite avant de
les traiter comme entree canonique de prompt.

Source stakes:

- User impact: eviter une narration LLM fondee sur une projection client qui
  masque des faits utiles ou ajoute du shaping editorial.
- Technical risk: confondre contrat factuel, projection B2C, contrat IA,
  stockage d'audit et readiness flags.
- Closure expectation: produire un audit reproductible et cite, sans
  implementation applicative.
- Forbidden regression: aucune modification de projection, prompt, plan B2C,
  persistance d'audit, API publique, securite, CI ou frontend.

Source-alignment evidence: the objective, ACs, tasks, evidence artifacts,
validation plan, non-goals and guardrails map back to the brief's required
questions, mandatory sources and audit deliverables.

## Objective

Produire un audit de readiness des contrats `structured_facts_v1`,
`beginner_summary_v1`, `client_interpretation_projection_v1`,
`AINarrativeInputContract` et `narrative_answer_audit_v1` pour l'injection LLM.

L'audit doit separer faits exploitables, signaux interpretatifs, shaping
editorial, surfaces d'audit et exclusions avant toute decision de prompt.

## Target State

Un dossier d'audit est cree sous:
`_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/`.

Il contient:

- `00-audit.md` avec la synthese readiness et les reponses aux questions
  obligatoires.
- `01-contract-comparison.md` avec la comparaison des contrats et de leurs
  producteurs/consommateurs.
- `02-field-classification.md` avec la classification champ par champ.
- `03-llm-readiness-matrix.md` avec la matrice d'aptitude a l'injection LLM.
- `04-recommendations.md` avec la recommandation d'architecture sans
  implementation.

Les artefacts citent explicitement les sources obligatoires du brief,
documentent les garanties de hash, provenance, exclusion et readiness, puis
formulent une surface cible avec limites.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-326-audit-projections-interpretatives-llm-input-readiness.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign the story number.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py` - mandatory source exists.
- Evidence 5: `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` - mandatory source exists.
- Evidence 6: `backend/app/infra/db/models/user_natal_interpretation.py` - mandatory persistence source exists.
- Evidence 7: `_condamad/stories/CS-324-audit-calculs-interpretations-llm/00-story.md` - sibling LLM audit story inspected.
- Evidence 8: `_condamad/stories/CS-325-audit-pipeline-prompt-llm-natal/00-story.md` - sibling prompt audit story inspected.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Audit of recent backend interpretation projection and narrative input
    contracts.
  - Audit of hashability, provenance, exclusions, readiness flags and plan
    granularity.
  - Audit of current usage versus non-usage in the LLM pipeline.
  - Creation of the audit artifacts under the target `_condamad/audits` path.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling,
    migrations, prompt changes, projection changes and public API changes.
- Explicit non-goals:
  - No projection modification.
  - No prompt modification.
  - No field addition.
  - No B2C plan change.
  - No audit persistence change.
  - No internal surface exposure through public API.

Named brief primitives in scope:

- `structured_facts_v1`
- `beginner_summary_v1`
- `client_interpretation_projection_v1`
- `AINarrativeInputContract`
- `narrative_answer_audit_v1`
- `StructuredFactsV1Builder`
- `ClientInterpretationProjectionV1Builder`
- `AINarrativeInputBuilder`
- `readiness_flags`
- `evidence_refs`
- `projection_hash`
- `llm_input_hash`
- `prompt_version`
- `provider`
- `model`

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend audit of
  projection contracts and LLM input readiness.
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
  - Runtime-source references must distinguish projection product usage from
    prompt input readiness.
  - `pytest -q backend/tests/unit/domain/astrology` is validation evidence for
    unchanged projection behavior, not a request to change tests.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Code owners and tests prove contract fields before audit conclusions. |
| Baseline Snapshot | yes | The audit compares current projection contracts with LLM input needs. |
| Ownership Routing | yes | Each contract and field must map to a precise producer and consumer owner. |
| Allowlist Exception | no | No allowlist handling is authorized for this audit-only story. |
| Contract Shape | yes | The audit deliverables have fixed files, matrices and classifications. |
| Batch Migration | no | No multi-file conversion is in scope. |
| Reintroduction Guard | yes | Prompt, projection and public contract surfaces must stay unchanged. |
| Persistent Evidence | yes | Audit outputs and evidence logs must persist for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Candidate contracts are compared. | Evidence profile: baseline_before_after_diff; `rg` checks all candidate names in `01-contract-comparison.md`. |
| AC2 | Field classes are assigned. | Evidence profile: json_contract_shape; `rg` checks classification values in `02-field-classification.md`. |
| AC3 | Hash guarantees are documented. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks hash tokens in `00-audit.md`. |
| AC4 | Pipeline usage status is explicit. | Evidence profile: ast_architecture_guard; `rg` checks `current-llm-use` in `03-llm-readiness-matrix.md`. |
| AC5 | The target contract recommendation is stated. | Evidence profile: baseline_before_after_diff; `rg` checks `recommended-target` in `04-recommendations.md`. |
| AC6 | Application code remains unchanged. | Evidence profile: repo_wide_negative_scan; `python` checks `git status --short -- backend/app backend/tests`. |
| AC7 | Audit artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks all five audit files exist. |
| AC8 | Existing projection tests are cited. | Evidence profile: ast_architecture_guard; `rg` checks required test paths in `00-audit.md`. |
| AC9 | Provenance guarantees are documented. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks provenance tokens in `00-audit.md`. |

## Implementation Tasks

- [ ] Task 1: Read every mandatory source file and record bounded citations in `00-audit.md`. (AC: AC1, AC3, AC8)
- [ ] Task 2: Compare the candidate contracts in `01-contract-comparison.md`. (AC: AC1)
- [ ] Task 3: Classify fields as factuel, signal interpretatif, shaping editorial, audit, exclusion or debug. (AC: AC2)
- [ ] Task 4: Document hashability, provenance, exclusions and readiness flags in the audit synthesis. (AC: AC3, AC9)
- [ ] Task 5: Determine current LLM pipeline usage and non-usage in `03-llm-readiness-matrix.md`. (AC: AC4)
- [ ] Task 6: Recommend the target LLM input surface and limits in `04-recommendations.md`. (AC: AC5)
- [ ] Task 7: Run validation commands and persist command output in the audit folder. (AC: AC6, AC7, AC8)

## Files to Inspect First

- `_story_briefs/cs-326-audit-projections-interpretatives-llm-input-readiness.md`
- `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`
- `backend/app/domain/astrology/interpretation/beginner_summary_v1_builder.py`
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`
- `backend/app/domain/astrology/interpretation/evidence_refs_validation.py`
- `backend/app/infra/db/models/user_natal_interpretation.py`
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py`
- `backend/tests/unit/domain/astrology/test_structured_facts_v1_builder.py`
- `backend/tests/unit/domain/astrology/test_beginner_summary_v1_builder.py`
- `backend/tests/unit/domain/astrology/test_client_interpretation_projection_v1_builder.py`
- `backend/tests/unit/domain/astrology/interpretation/test_ai_narrative_input_contract.py`
- `backend/tests/unit/test_rejected_narrative_answer_workflow.py`

## Runtime Source of Truth

- Primary source of truth:
  - The listed backend source files and associated unit tests.
  - `AST guard` or targeted `rg` scans over owners named in the brief.
- Secondary evidence:
  - `git status --short -- _condamad _story_briefs backend/app backend/tests`.
  - Audit citations with file paths, symbols and short line references.
- Static scans alone are not sufficient for this story because:
  - The audit must prove producer, consumer and readiness semantics from actual
    source owners before recommending a prompt input surface.

## Contract Shape

- Contract type:
  - Audit artifact set, contract comparison, field classification and readiness
    recommendation.
- Fields:
  - `contract`: candidate contract or persisted audit surface name.
  - `producer`: precise source owner or builder.
  - `consumer`: current service, endpoint, persistence or test consumer.
  - `field`: contract field or grouped field family.
  - `classification`: `factuel`, `signal interpretatif`, `shaping editorial`,
    `audit`, `exclusion` or `debug`.
  - `hashable`: `yes`, `partial` or `no`.
  - `current-llm-use`: `injected`, `available-not-injected`, `product-only` or `audit-only`.
  - `readiness`: `ready`, `partial` or `missing`.
- Required fields:
  - `contract`
  - `producer`
  - `consumer`
  - `field`
  - `classification`
  - `hashable`
  - `current-llm-use`
  - `readiness`
- Optional fields:
  - none
- Status codes:
  - none; no API route is created or changed.
- Serialization names:
  - Audit matrix headings are emitted exactly as listed under required fields.
- Required files:
  - `00-audit.md`
  - `01-contract-comparison.md`
  - `02-field-classification.md`
  - `03-llm-readiness-matrix.md`
  - `04-recommendations.md`
- Required classification values:
  - `factuel`
  - `signal interpretatif`
  - `shaping editorial`
  - `audit`
  - `exclusion`
  - `debug`
  - `recommended-target`
  - `current-llm-use`
- Frontend type impact:
  - none; no frontend generated client or UI surface is in scope.
- Generated contract impact:
  - none; no OpenAPI or generated manifest change is in scope.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `00-audit.md` records the source files and commands read for the audit.
- Comparison after implementation:
  - `01-contract-comparison.md`, `02-field-classification.md` and
    `03-llm-readiness-matrix.md` contain the classified audit conclusions.
- Expected invariant:
  - The only intended repository delta is the audit artifact directory plus
    story execution evidence.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Structured facts evidence | `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py` | Prompt templates |
| Beginner summary evidence | `backend/app/domain/astrology/interpretation/beginner_summary_v1_builder.py` | LLM provider clients |
| Client projection evidence | `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` | Public API changes |
| Narrative input evidence | `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` | Frontend code |
| Narrative input contracts | `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` | Audit-only invented schema |
| Audit persistence evidence | `backend/app/infra/db/models/user_natal_interpretation.py` | Prompt payload storage |
| Audit deliverables | `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/**` | Backend app or tests |

## Mandatory Reuse / DRY Constraints

- Reuse existing contract and field names from the source owners.
- Keep one canonical field classification in `02-field-classification.md`;
  other artifacts may reference it without duplicating every row.
- Use the same classification and readiness values across all audit files.
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
  - prompt files, projection builders and persistence models

## Reintroduction Guard

- Guarded surfaces:
  - `backend/app/domain/astrology/interpretation/**`
  - `backend/app/services/llm_generation/natal/**`
  - `backend/app/infra/db/models/user_natal_interpretation.py`
  - `backend/tests/unit/domain/astrology/**`
- Required guard:
  - `AST architecture guard` checks forbidden symbols before prompt,
    projection or public contract changes are introduced.
  - `python` checks that `git status --short -- backend/app backend/tests`
    returns no changed application or test files.
  - `rg` checks audit artifacts contain candidate names, hash fields,
    readiness flags and classification values.

## Regression Guardrails

Scope vector: operation `audit`, domain `backend-domain`, paths
`backend/app/domain/astrology/interpretation`,
`backend/app/services/llm_generation/natal`,
`backend/app/infra/db/models/user_natal_interpretation.py`,
`backend/tests/unit/domain/astrology`, contracts `ai-narrative-input`,
`projection-readiness` and `persistent-audit-evidence`.

| Guardrail | Local invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend ownership must not drift into audit or API files. | `python` status guard; owner `rg`. |
| RG-022 `prompt-generation-validation-plans` | LLM readiness validation must keep backend tests explicit. | `pytest`; `rg` test references. |
| RG-047 non-applicable | Frontend inline style rules are outside this backend audit scope. | Manual check: no `frontend` edits. |
| RG-052 non-applicable | Frontend CSS namespace rules are outside this backend audit scope. | Manual check: no style edits. |
| RG-041 non-applicable | Entitlement documentation is outside this projection readiness audit. | Manual check: no entitlement docs. |

Registry gap: no exact guardrail was found for interpretation projection
readiness audit artifacts; the story records local invariants without editing
the global registry.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Audit synthesis | `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/00-audit.md` | Keep findings and answers. |
| Contract comparison | `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/01-contract-comparison.md` | Keep producer and consumer comparison. |
| Field classification | `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/02-field-classification.md` | Keep field classes. |
| Readiness matrix | `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/03-llm-readiness-matrix.md` | Keep injection readiness. |
| Recommendations | `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/04-recommendations.md` | Keep architecture recommendation. |
| Validation output | `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/validation-output.md` | Keep command output. |
| Review output | `_condamad/stories/CS-326-audit-projections-interpretatives-llm-input-readiness/generated/11-code-review.md` | Keep automatic review output. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this audit-only story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/00-audit.md` - synthesis and required answers.
- `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/01-contract-comparison.md` - contract comparison.
- `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/02-field-classification.md` - field classification.
- `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/03-llm-readiness-matrix.md` - readiness matrix.
- `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/04-recommendations.md` - recommendation.
- `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/validation-output.md` - validation output.

Likely tests:

- No new tests are expected because the story is audit-only.
- Existing validation may run `pytest -q backend/tests/unit/domain/astrology`.
- Existing validation may run `pytest -q backend/tests/unit/test_rejected_narrative_answer_workflow.py`.

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
  `rg -n "structured_facts_v1|beginner_summary_v1|AINarrativeInput" _condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000`
  puis `rg -n "client_interpretation_projection_v1" _condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000`.
- VC2:
  `rg -n "readiness_flags|evidence_refs|projection_hash|llm_input_hash" _condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000`
  puis `rg -n "prompt_version|provider|model" _condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000`.
- VC3:
  `rg -n "factuel|signal interpretatif|shaping editorial|audit|exclusion|debug" _condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000`
- VC4:
  `rg -n "current-llm-use|recommended-target|available-not-injected|product-only|audit-only" _condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000`
- VC5:
  `python -c "from pathlib import Path; root=Path('_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000'); assert root.exists()"`
- VC6:
  `python -c "import subprocess; out=subprocess.check_output(['git','status','--short','--','backend/app','backend/tests'], text=True); assert out.strip() == ''"`
- VC7:
  `rg -n "structured_facts_v1|beginner_summary_v1|client_interpretation_projection_v1" .\backend\app .\backend\tests`
  puis `rg -n "AINarrativeInput|readiness_flags|evidence_refs|projection_hash|llm_input_hash" .\backend\app .\backend\tests`.
- VC8: `git status --short -- _condamad _story_briefs backend/app backend/tests`
- VC9: `pytest -q backend/tests/unit/domain/astrology`
- VC10: `pytest -q backend/tests/unit/test_rejected_narrative_answer_workflow.py`
- VC11: `ruff format .`
- VC12: `ruff check .`

## Regression Risks

- The audit may promote a display-oriented client projection as canonical LLM
  input without proving hidden factual loss.
- The audit may treat readiness flags as proof of prompt readiness rather than
  proof of builder-local completeness.
- The audit may classify audit metadata as prompt input and blur evidence
  storage with generation context.
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

- `_story_briefs/cs-326-audit-projections-interpretatives-llm-input-readiness.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-324-audit-calculs-interpretations-llm/00-story.md`
- `_condamad/stories/CS-325-audit-pipeline-prompt-llm-natal/00-story.md`
