# Story CS-346 audit-natal-astrology-llm-input-sources: Audit Natal Astrology LLM Input Sources
Status: ready-to-dev

## Trigger / Source

- Mode: Audit-to-story with repo-informed evidence.
- Source brief: `_story_briefs/cs-346-audit-inputs-astrologiques-natals-prompt-llm.md`.
- Source problem: after CS-330 to CS-342, the project needs a block-by-block map of the astrology data that feeds the modern natal LLM prompt.
- Source stakes:
  - The gateway must not invent astrology context; prompt-visible data must be traced to internal builders and projections.
  - `facts`, `signals`, `limits`, `shaping`, `evidence`, `provenance`, `exclusions`, and `data_roles` need owners and sources.
  - Prompt-visible, runtime-only, validation-only, and audit-only roles must stay distinct after CS-341 and CS-342.
  - `chart_json` and `natal_data` must remain classified as forbidden legacy carriers for the modern natal prompt.
  - Hash and evidence policies must be explained from current code and tests, not inferred from intent.
- Source-alignment review: PASS. Objective, target state, ACs, tasks, evidence, non-goals, and guardrails map to the source stakes.

## Objective

Produce the fourth timestamped prompt-generation cartography audit focused on the builders and projections that produce
`llm_astrology_input_v1` for the modern natal LLM prompt. The story creates documentation and evidence artifacts only; it does not modify
runtime code, contracts, prompts, tests, hash policy, gateway behavior, or public behavior.

## Target State

- A report exists at `_condamad/audits/prompt-generation-cartography/YYYY-MM-DD-HHMM/04-natal-astrology-input-audit.md`.
- The report contains a source map for `LLMAstrologyInputV1Builder`, `StructuredFactsV1Builder`, `AINarrativeInputBuilder`,
  `ClientInterpretationProjectionV1Builder`, hash helpers, JSON conversion helpers, `NatalInterpretationService`, and `AIEngineAdapter`.
- Each block of `llm_astrology_input_v1` has one owner, source input, runtime role, prompt visibility, evidence, and gap classification.
- `facts`, `signals`, `limits`, `shaping`, `evidence`, `provenance`, `exclusions`, and `data_roles` are documented separately.
- Prompt-visible, runtime-only, validation-only, and audit-only roles are classified without moving evidence back into prompt material.
- The current hash policy lists prompt-influencing blocks and explains how `projection_hash` and `llm_input_hash` are produced or related.
- The current evidence policy explains evidence refs, grounding status, validation ownership, and audit persistence boundaries.
- Existing tests for hash, evidence, payload boundary, and legacy carrier guards are mapped to what they prove and what remains a gap.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-346-audit-inputs-astrologiques-natals-prompt-llm.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-346`.
- Evidence 3: `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md` - source contract brief read.
- Evidence 4: `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md` - source builder brief read.
- Evidence 5: `_story_briefs/cs-332-brancher-llm-astrology-input-dans-execution-natale.md` - runtime wiring brief read.
- Evidence 6: `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md` - hash and evidence brief read.
- Evidence 7: `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md` - evidence boundary brief read.
- Evidence 8: `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/00-story.md` - CS-342 implications read.
- Evidence 9: `_condamad/stories/CS-343-prompt-generation-surface-inventory/00-story.md` - prompt cartography sequence context read.
- Evidence 10: `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/00-story.md` - configuration audit context read.
- Evidence 11: `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/00-story.md` - runtime handoff context read.
- Evidence 12: `_condamad/stories/regression-guardrails.md` - guardrail registry consulted through scoped resolver output only.
- Evidence 13: `resolve_guardrails.py` returned RG-002 for the backend astrology input audit scope.
- Evidence 14: targeted path checks confirmed all priority backend files and tests named by the source brief exist in this workspace.
- Repository structure alert: `_condamad/audits/prompt-generation-cartography` is absent; implementation must create the audit folder.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Audit of `LLMAstrologyInputV1Builder` and the complete `llm_astrology_input_v1` block assembly.
  - Audit of `StructuredFactsV1Builder`, `AINarrativeInputBuilder`, `AINarrativeInputContract`, and `ClientInterpretationProjectionV1Builder`.
  - Audit of hash helpers, JSON conversion helpers, prompt-influencing block lists, and data role constants.
  - Audit of `NatalInterpretationService` and `AIEngineAdapter` branching into the natal LLM runtime.
  - Audit of prompt-visible, runtime-only, validation-only, and audit-only role boundaries.
  - Audit of tests for hash stability, evidence handling, payload boundaries, and legacy carrier guards.
  - Creation of the timestamped audit report and story evidence artifacts only.
- Out of scope:
  - Frontend UI, public API route changes, database schema changes, auth, i18n, styling, build tooling, migrations, and provider calls.
  - Astrology calculation changes, contract field additions, hash semantic changes, prompt edits, gateway edits, and runtime fixes.
  - Guardrail registry maintenance or enrichment.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
  - No runtime code change, prompt text rewrite, schema migration, provider integration, or test source change.
  - No addition of fields to `llm_astrology_input_v1`.
  - No change to `projection_hash`, `llm_input_hash`, evidence policy, or data role policy.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend astrology input audit contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Create only audit, evidence, validation, and generated review artifacts.
  - Do not change application code, prompt text, contract fields, hash policy, migrations, tests, provider clients, or runtime behavior.
  - Preserve the distinction between prompt-visible, runtime-only, validation-only, and audit-only data roles.
  - Classify missing source ownership, missing tests, or ambiguous boundaries as report gaps instead of implementing a correction.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: an owner or source for a required `llm_astrology_input_v1` block cannot be identified from repository evidence.
- Additional validation rules:
  - The audit must cite concrete file paths and symbol names for every block owner it classifies.
  - Runtime claims must use `AST guard`, targeted `rg`, full backend `pytest` paths, or bounded source-trace evidence.
  - Prompt-visible claims must name the data role constant or projection code that makes the field visible.
  - Hash claims must name `build_llm_input_hash_material`, `PROMPT_INFLUENCING_BLOCKS`, or the active hash helper used by current code.
  - Evidence claims must distinguish validation-only and audit-only material from prompt-visible payload material.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `AST guard`, source traces, targeted `rg`, and backend `pytest` paths prove builder and runtime branch behavior. |
| Baseline Snapshot | yes | Scan outputs and symbol maps create a reproducible before-state for later stories. |
| Ownership Routing | yes | Facts, signals, limits, shaping, evidence, provenance, exclusions, roles, hash, service, and adapter owners must stay separated. |
| Allowlist Exception | no | No allowlist handling is authorized for this audit story. |
| Contract Shape | yes | The audit report has required block map, role matrix, hash policy, evidence policy, legacy carrier, test, and gap sections. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Legacy carriers and backend-only evidence must not be reclassified as modern prompt material. |
| Persistent Evidence | yes | Report, scan output, validation output, final evidence, and review handoff must be kept. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The natal astrology input audit report exists. | Evidence profile: baseline_before_after_diff; `python` checks the report path under `_condamad/audits`. |
| AC2 | `LLMAstrologyInputV1Builder` is mapped. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks builder symbols in the report. |
| AC3 | `structured_facts_v1` source ownership is mapped. | Evidence profile: ast_architecture_guard; `rg` checks `StructuredFactsV1Builder` in the report. |
| AC4 | `AINarrativeInput` signal ownership is mapped. | Evidence profile: ast_architecture_guard; `rg` checks `AINarrativeInput` in the report. |
| AC5 | Client projection ownership is mapped. | Evidence profile: ast_architecture_guard; `rg` checks `client_interpretation_projection_v1` in the report. |
| AC6 | Data role boundaries are classified. | Evidence profile: json_contract_shape; `rg` checks prompt-visible and backend-only role labels in the report. |
| AC7 | Hash policy is explained. | Evidence profile: ast_architecture_guard; `rg` checks `build_llm_input_hash_material` and hash block labels. |
| AC8 | Evidence policy is explained. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py`. |
| AC9 | Legacy carriers are classified as forbidden. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks `chart_json` and `natal_data` labels in the report. |
| AC10 | Runtime branch points are mapped. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks `NatalInterpretationService` and `AIEngineAdapter`. |
| AC11 | Existing tests are evaluated. | Evidence profile: baseline_before_after_diff; `pytest` paths from VC7 through VC10. |
| AC12 | Backend source files are unchanged. | Evidence profile: ast_architecture_guard; `python` checks git status for backend app and backend tests. |
| AC13 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence and generated paths. |

## Implementation Tasks

- [ ] Task 1: Create the timestamped audit folder and story evidence artifact set. (AC: AC1, AC13)
- [ ] Task 2: Map `LLMAstrologyInputV1Builder` and every `llm_astrology_input_v1` block. (AC: AC2, AC6)
- [ ] Task 3: Map `StructuredFactsV1Builder` as the canonical source for `facts`. (AC: AC3)
- [ ] Task 4: Map `AINarrativeInputBuilder` and `AINarrativeInputContract` as the signal source. (AC: AC4)
- [ ] Task 5: Map `ClientInterpretationProjectionV1Builder` as client projection input, not canonical fact owner. (AC: AC5)
- [ ] Task 6: Classify prompt-visible, runtime-only, validation-only, and audit-only fields. (AC: AC6, AC8)
- [ ] Task 7: Explain hash helpers, prompt-influencing blocks, `projection_hash`, and `llm_input_hash`. (AC: AC7)
- [ ] Task 8: Explain evidence refs, grounding status, validation ownership, and audit persistence boundaries. (AC: AC8)
- [ ] Task 9: Trace `NatalInterpretationService` and `AIEngineAdapter` branch points into the natal LLM runtime. (AC: AC10)
- [ ] Task 10: Classify `chart_json` and `natal_data` as forbidden legacy carriers for the modern natal prompt. (AC: AC9)
- [ ] Task 11: Evaluate existing hash, evidence, payload boundary, and legacy guard tests, then record gaps. (AC: AC11)
- [ ] Task 12: Persist validation outputs and prove backend app and backend tests remain unchanged. (AC: AC12, AC13)

## Files to Inspect First

- `_story_briefs/cs-346-audit-inputs-astrologiques-natals-prompt-llm.md` - source scope and acceptance criteria.
- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md` - source contract context.
- `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md` - source builder context.
- `_story_briefs/cs-332-brancher-llm-astrology-input-dans-execution-natale.md` - runtime wiring context.
- `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md` - hash and evidence context.
- `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md` - evidence boundary context.
- `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/00-story.md` - final evidence boundary context.
- `_condamad/stories/CS-343-prompt-generation-surface-inventory/00-story.md` - prior prompt surface inventory.
- `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/00-story.md` - prior configuration audit context.
- `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/00-story.md` - prior provider handoff context.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - LLM astrology input contract, builder, roles, and hashes.
- `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py` - fact source builder.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` - narrative signal builder.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` - internal narrative contract owner.
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` - client projection builder.
- `backend/app/domain/astrology/projections/projection_hash.py` - projection hash helper owner.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - natal LLM service and audit persistence owner.
- `backend/app/domain/llm/runtime/adapter.py` - runtime adapter boundary owner.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` - contract and role tests.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py` - hash policy tests.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py` - evidence policy tests.
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` - prompt boundary tests.
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` - architecture boundary guards.
- `backend/tests/integration/test_llm_legacy_extinction.py` - legacy carrier guard tests.

## Runtime Source of Truth

- Primary source of truth:
  - Source traces from backend astrology interpretation builders, projection hash helpers, natal LLM service, and runtime adapter files.
  - `AST guard` checks for builder ownership, data role constants, prompt-influencing block constants, and branch point classification.
  - `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` for contract and role evidence.
  - `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py` for hash policy evidence.
  - `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py` for evidence policy evidence.
  - `pytest -q backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` for prompt boundary evidence.
- Secondary evidence:
  - Targeted `rg` scans for builder symbols, hash helpers, data roles, legacy carriers, service branch points, and report sections.
- Static scans alone are not sufficient for this story because:
  - The audit must distinguish source occurrence from runtime ownership, prompt visibility, validation-only use, and audit-only persistence.

## Contract Shape

- Contract type:
  - Timestamped backend astrology input audit report and persistent evidence bundle.
- Fields:
  - `block`: one of `facts`, `signals`, `limits`, `shaping`, `evidence`, `provenance`, `exclusions`, or `data_roles`.
  - `owner`: canonical source module, builder, helper, service, adapter, or test owner.
  - `source input`: upstream contract, projection, runtime object, helper output, or test fixture.
  - `runtime role`: prompt-visible, runtime-only, validation-only, audit-only, legacy carrier, or not active.
  - `prompt visibility`: visible, not visible, validation-only, audit-only, or forbidden carrier.
  - `hash impact`: included in `llm_input_hash`, excluded from `llm_input_hash`, projection hash only, or needs-investigation.
  - `evidence`: short source, scan, `AST guard`, or `pytest` evidence.
  - `gap`: no gap, test gap, owner ambiguity, source ambiguity, CS-341 dependency, CS-342 dependency, or needs-investigation.
- Required report sections:
  - Executive summary.
  - Builder source map.
  - Block-by-block ownership matrix.
  - Prompt-visible versus backend-only classification.
  - Hash policy.
  - Evidence policy.
  - Runtime branch points.
  - Legacy carrier classification.
  - Existing tests and gaps.
- Required fields:
  - block
  - owner
  - source input
  - runtime role
  - prompt visibility
  - hash impact
  - evidence
  - gap
- Optional fields:
  - none for required block rows; helper rows may use `not active` as prompt visibility.
- Status codes:
  - none; this story does not change a public API route.
- Serialization names:
  - Report column names must use the exact field names listed above.
- Frontend type impact:
  - none.
- Generated contract impact:
  - none.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/evidence/natal-astrology-input-scan-baseline.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/evidence/natal-astrology-input-scan-after.txt`
- Expected invariant:
  - The only intended repository delta is the audit report, story evidence artifacts, generated review handoff, and validation output.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| LLM astrology input block assembly | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | gateway ad hoc serializer |
| Facts source | `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py` | client projection owner |
| Signal source | `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` | raw chart carrier |
| Narrative contract | `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` | report-only schema |
| Client projection | `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` | canonical fact source |
| Projection hash | `backend/app/domain/astrology/projections/projection_hash.py` | prompt renderer |
| Natal generation branch | `backend/app/services/llm_generation/natal/interpretation_service.py` | adapter-only assumptions |
| Runtime adapter branch | `backend/app/domain/llm/runtime/adapter.py` | astrology builder |
| Audit report | `_condamad/audits/prompt-generation-cartography/*/04-natal-astrology-input-audit.md` | transient chat notes |

## Mandatory Reuse / DRY Constraints

- Reuse the timestamped audit folder pattern from CS-343, CS-344, and CS-345.
- Reuse the existing evidence artifact pattern under the story folder.
- Reuse `LLM_ASTROLOGY_INPUT_DATA_ROLES` and current hash constants as the role and hash source of truth.
- Reuse CS-341 and CS-342 boundary terms for prompt-visible, runtime-only, validation-only, and audit-only data.
- Reuse existing source symbols and tests as evidence instead of copying builder code into the report.
- Do not duplicate the CS-343 surface inventory, CS-344 configuration matrix, or CS-345 provider handoff trace.
- Do not introduce new dependencies.

## No Legacy / Forbidden Paths

- No legacy `chart_json` or `natal_data` prompt path may be accepted as a target implementation path.
- No compatibility prompt carrier may be added for this audit.
- No fallback prompt carrier may be added for this audit.
- Do not edit astrology builders, hash helpers, natal services, runtime adapter, gateway, tests, migrations, or frontend files.
- Do not treat evidence, provenance, hashes, grounding status, or validation owner as prompt-visible material.
- Do not treat client projection data as the canonical facts source when `structured_facts_v1` is the owner.

## Reintroduction Guard

- Exact forbidden implementation surfaces:
  - `backend/app/domain/astrology/interpretation/**` code edits.
  - `backend/app/domain/astrology/projections/**` code edits.
  - `backend/app/services/llm_generation/natal/**` code edits.
  - `backend/app/domain/llm/runtime/**` code edits.
  - `backend/tests/**` edits outside persisted validation evidence.
  - `frontend/src/**` edits.
  - `_condamad/stories/regression-guardrails.md` edits.
- Required deterministic guards:
  - `python` checks `git status --short -- backend/app backend/tests frontend/src`.
  - `rg` verifies the audit report contains all required block names, hash policy labels, evidence policy labels, and legacy carrier labels.
  - `AST guard` verifies the audit evidence references existing source symbols rather than new implementation changes.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Applicable only as backend boundary control; no API routing logic may move during audit. | `python` git-status guard; targeted `rg`. |
| Registry gap | No exact guardrail exists for natal astrology LLM input source cartography. | Resolver output recorded in evidence. |

Non-applicable examples: RG-047, RG-052, and RG-041 are frontend or entitlement-documentation guardrails and remain out of scope.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline scan | `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/evidence/natal-astrology-input-scan-baseline.txt` | Keep pre-audit source scan evidence. |
| After scan | `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/evidence/natal-astrology-input-scan-after.txt` | Keep post-audit source scan evidence. |
| Symbol map | `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/evidence/natal-astrology-input-symbol-map.md` | Keep block owner and symbol evidence. |
| Audit report | `_condamad/audits/prompt-generation-cartography/YYYY-MM-DD-HHMM/04-natal-astrology-input-audit.md` | Deliver the natal astrology input audit. |
| Validation output | `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/evidence/validation.txt` | Keep validation command output. |
| Final evidence | `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/evidence/final-evidence.md` | Summarize final proof and residual gaps. |
| Review output | `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this astrology input audit story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/prompt-generation-cartography/YYYY-MM-DD-HHMM/04-natal-astrology-input-audit.md` - audit deliverable.
- `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/evidence/natal-astrology-input-scan-baseline.txt` - baseline scan artifact.
- `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/evidence/natal-astrology-input-scan-after.txt` - after scan artifact.
- `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/evidence/natal-astrology-input-symbol-map.md` - source symbol map.
- `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/evidence/validation.txt` - validation output artifact.
- `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/evidence/final-evidence.md` - final evidence summary.
- `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/generated/11-code-review.md` - generated review handoff.

Likely tests:

- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` - proves contract shape and data role behavior.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py` - proves hash policy behavior.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py` - proves evidence policy behavior.
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` - proves provider payload boundary behavior.
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` - proves architecture prompt boundary guards.
- `backend/tests/integration/test_llm_legacy_extinction.py` - proves legacy carrier guard behavior.

Files not expected to change:

- `backend/app/**` - out of scope; no runtime, builder, hash, service, adapter, gateway, provider, or validation code is edited.
- `backend/tests/**` - out of scope; existing tests may be executed or cited but not edited.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no migration is touched.
- `_condamad/stories/regression-guardrails.md` - out of scope; registry enrichment is not authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

All Python commands must run after `.\.venv\Scripts\Activate.ps1`.
Run VC1, VC2, VC3, VC4, VC5, VC11, and VC12 from the repository root.
Run VC6, VC7, VC8, VC9, and VC10 from `backend`.

- VC1 report path:
  `python -c "from pathlib import Path; root=Path('_condamad/audits/prompt-generation-cartography'); assert any(root.glob('*/04-natal-astrology-input-audit.md'))"`
- VC2 report block coverage:
  `rg -n "facts|signals|limits|shaping|evidence|provenance|exclusions|data_roles" _condamad/audits/prompt-generation-cartography`
- VC3 builder coverage:
  `rg -n "LLMAstrologyInputV1Builder|StructuredFactsV1Builder|AINarrativeInput|ClientInterpretationProjectionV1Builder" _condamad`
- VC4 hash and role coverage:
  `rg -n "build_llm_input_hash_material|PROMPT_INFLUENCING_BLOCKS|LLM_ASTROLOGY_INPUT_DATA_ROLES|projection_hash|llm_input_hash" _condamad`
- VC5 legacy carrier coverage:
  `rg -n "chart_json|natal_data|legacy carrier|forbidden carrier" _condamad/audits/prompt-generation-cartography`
- VC6 source scan:
  `rg -n "LLMAstrologyInputV1Builder|build_llm_input_hash_material|PROMPT_INFLUENCING_BLOCKS|LLM_ASTROLOGY_INPUT_DATA_ROLES" app tests`
- VC7 builder tests:
  `pytest -q tests/unit/domain/astrology/test_llm_astrology_input_v1.py --tb=short`
- VC8 hash and evidence tests:
  `pytest -q tests/unit/domain/astrology/test_llm_astrology_input_hash.py tests/unit/domain/astrology/test_llm_astrology_input_evidence.py --tb=short`
- VC9 boundary tests:
  `pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py tests/architecture/test_llm_astrology_input_payload_boundaries.py --tb=short`
- VC10 legacy tests:
  `pytest -q tests/integration/test_llm_legacy_extinction.py --tb=short`
- VC11 no runtime source delta:
  `python -c "import subprocess; subprocess.run(['git','diff','--quiet','--','backend/app','backend/tests','frontend/src'], check=True)"`
- VC12 artifact paths:
  `python -c "from pathlib import Path; r=Path('_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources'); assert (r/'evidence').exists()"`
  Run `python` with the same `r` value to assert `(r/'generated').exists()`.
- VC13 format: `ruff format .`
- VC14 lint: `ruff check .`
- VC15 full backend tests: `pytest -q tests --tb=short`

## Regression Risks

- Risk: the audit could describe `client_interpretation_projection_v1` as canonical fact source.
  - Mitigation: AC3, AC5, and Ownership Routing require separate fact and client projection ownership.
- Risk: evidence could be described as prompt-visible despite CS-341 and CS-342.
  - Mitigation: AC6 and AC8 require explicit validation-only and audit-only classification.
- Risk: hash coverage could be inferred from block names instead of current helper behavior.
  - Mitigation: AC7 requires source evidence for hash helpers and prompt-influencing block constants.
- Risk: `chart_json` or `natal_data` could be treated as acceptable prompt carriers.
  - Mitigation: AC9 and the Reintroduction Guard require forbidden carrier classification.
- Risk: the report could duplicate CS-343 through CS-345 instead of focusing on astrology input production.
  - Mitigation: DRY constraints require using prior audits as context and focusing this story on builder and projection input production.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command.
- Keep the audit as documentation plus evidence only; application files remain unchanged.
- Create `_condamad/audits/prompt-generation-cartography/YYYY-MM-DD-HHMM/` before writing the audit report.
- Keep markdown table lines under 180 characters in generated evidence and final report.
- Record any missing natal-astrology-input guardrail as `Registry gap` in story evidence, not in the registry.

## References

- `_story_briefs/cs-346-audit-inputs-astrologiques-natals-prompt-llm.md`
- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md`
- `_story_briefs/cs-332-brancher-llm-astrology-input-dans-execution-natale.md`
- `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md`
- `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md`
- `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/00-story.md`
- `_condamad/stories/CS-343-prompt-generation-surface-inventory/00-story.md`
- `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/00-story.md`
- `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/00-story.md`
- `_condamad/stories/regression-guardrails.md`
