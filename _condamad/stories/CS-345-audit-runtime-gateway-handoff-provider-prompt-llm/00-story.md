# Story CS-345 audit-runtime-gateway-handoff-provider-prompt-llm: Audit Runtime Gateway Handoff Provider Prompt LLM
Status: ready-to-dev

## Trigger / Source

- Mode: Audit-to-story with repo-informed evidence.
- Source brief: `_story_briefs/cs-345-audit-runtime-gateway-handoff-provider-prompt-llm.md`.
- Source problem: CS-344 maps prompt configuration; this story must map the executed runtime path that turns that configuration into provider messages.
- Source stakes:
  - The last payload before provider must be identified from runtime code, not inferred from configuration.
  - System, developer, persona, history, user payload, provider parameters, output schema, and metadata must be separated.
  - Audit-only and validation-only fields must remain outside provider prompt material.
  - Structured and chat message paths must be compared without testing a real provider.
  - Recovery paths must be classified as non nominal rather than treated as the normal handoff.
- Source-alignment review: PASS. Objective, target state, ACs, tasks, evidence, non-goals, and guardrails map to the source stakes.

## Objective

Produce the third timestamped prompt-generation cartography audit focused on runtime gateway execution and provider handoff. The story creates
documentation and evidence artifacts only; it does not modify runtime code, prompt templates, tests, provider clients, schemas, or public behavior.

## Target State

- A report exists at `_condamad/audits/prompt-generation-cartography/YYYY-MM-DD-HHMM/03-runtime-gateway-handoff-audit.md`.
- The report contains a sequenced runtime trace from `LLMGateway.execute_request` to the final provider call boundary.
- The report identifies the last payload before provider for both `structured` and `chat` modes.
- The report differentiates system core, developer prompt, persona block, chat history, user payload, provider parameters, output schema, and metadata.
- The report includes the exact provider message shapes produced by `_build_messages`, `compose_chat_messages`, and `compose_structured_messages`.
- The report contains an include/exclude matrix for `llm_astrology_input_v1` prompt-visible, runtime-only, validation-only, and audit-only fields.
- The report maps input validation, output validation, repair, fallback, call logs, snapshots, usage, and observability metadata.
- The report lists tests and gaps without changing gateway, provider, validation, repair, or observability code.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-345-audit-runtime-gateway-handoff-provider-prompt-llm.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-345`.
- Evidence 3: `_condamad/stories/CS-343-prompt-generation-surface-inventory/00-story.md` - sibling inventory story read for sequence context.
- Evidence 4: `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/00-story.md` - preceding configuration audit story read.
- Evidence 5: `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md` - payload boundary guard brief read.
- Evidence 6: `_story_briefs/cs-339-aligner-provenance-audit-only-hors-prompt-llm-natal.md` - audit-only provenance boundary brief read.
- Evidence 7: `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md` - validation-only evidence boundary brief read.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - guardrail registry consulted through scoped resolver output only.
- Evidence 9: `resolve_guardrails.py` returned RG-002 and RG-022 for the backend runtime handoff audit scope.
- Evidence 10: targeted path checks confirmed `backend`, `backend/app`, `backend/tests`, `frontend`, and `frontend/src` exist.
- Evidence 11: targeted path checks confirmed all priority runtime files named by the brief exist in this workspace.
- Repository structure alert: `_condamad/audits/prompt-generation-cartography` is absent; implementation must create the audit folder.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Audit of `LLMGateway.execute_request`, `_resolve_plan`, `_build_messages`, and `_call_provider`.
  - Audit of `build_user_payload`, `compose_chat_messages`, and `compose_structured_messages`.
  - Audit of `_prompt_visible_llm_astrology_input` and prompt provider field exclusions.
  - Audit of `ProviderRuntimeManager`, `ProviderParameterMapper`, and provider parameter derivation.
  - Audit of input validation, output validation, repair, fallback, call logs, snapshots, usage, and observability metadata.
  - Creation of the timestamped audit report and story evidence artifacts only.
- Out of scope:
  - Frontend UI, database schema change, auth, i18n, styling, build tooling, migrations, and public API behavior.
  - Gateway code changes, provider client changes, prompt rewrite, validation fix, real provider calls, and CS-346 input production audit.
  - Guardrail registry maintenance or enrichment.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
  - No runtime code change, prompt text rewrite, schema migration, provider integration, or test source change.
  - No audit of `llm_astrology_input_v1` production; that belongs to CS-346.
  - No correction of output validation gaps; those become CS-347 only when the audit confirms a gap.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend LLM runtime handoff audit contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Create only audit, evidence, validation, and generated review artifacts.
  - Do not change application code, prompt text, seed definitions, migrations, tests, provider clients, or runtime behavior.
  - Preserve the distinction between final provider payload, resolved plan, recovery path, audit metadata, and validation-only data.
  - Classify recovery and fallback behavior as non nominal paths.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the last provider payload cannot be identified from source, tests, or deterministic instrumentation evidence.
- Additional validation rules:
  - The audit must cite concrete file paths and symbol names for every runtime step it classifies.
  - Runtime claims must use `AST guard`, targeted `rg`, full backend `pytest` paths, or bounded source-trace evidence.
  - Provider handoff claims must identify the final data structure passed into `_call_provider` or provider runtime manager code.
  - `structured` and `chat` modes must be compared in separate report sections.
  - Prompt field inclusion and exclusion must be traced from `_prompt_visible_llm_astrology_input`.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `AST guard`, source traces, and targeted `pytest` paths prove executed gateway handoff behavior. |
| Baseline Snapshot | yes | Scan outputs and symbol maps create a reproducible before-state for later runtime stories. |
| Ownership Routing | yes | Gateway, payload builder, message composer, provider manager, mapper, validators, repair, and observability owners must stay separated. |
| Allowlist Exception | no | No allowlist handling is authorized for this audit story. |
| Contract Shape | yes | The audit report has required runtime trace, message-shape, field-matrix, recovery, metadata, tests, and gaps sections. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Audit-only and validation-only fields must not be reclassified as provider prompt material. |
| Persistent Evidence | yes | Report, scan output, validation output, final evidence, and review handoff must be kept. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The handoff audit report exists. | Evidence profile: baseline_before_after_diff; `python` checks the report path under `_condamad/audits`. |
| AC2 | `execute_request` is sequenced. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks `execute_request` in the report. |
| AC3 | The final provider payload is identified. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks `_call_provider` and handoff labels. |
| AC4 | Structured mode messages are described. | Evidence profile: json_contract_shape; `rg` checks `compose_structured_messages` in the report. |
| AC5 | Chat mode messages are described. | Evidence profile: json_contract_shape; `rg` checks `compose_chat_messages` in the report. |
| AC6 | Provider parameters are mapped. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks `ProviderParameterMapper` in the report. |
| AC7 | Prompt exclusions are explicit. | Evidence profile: targeted_forbidden_symbol_scan; `pytest -q backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`. |
| AC8 | Recovery paths are classified. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks validator and repair symbols in the report. |
| AC9 | Observability metadata is mapped. | Evidence profile: json_contract_shape; `rg` checks call log, snapshot, usage, and metadata labels. |
| AC10 | Boundary tests are evaluated. | Evidence profile: baseline_before_after_diff; `pytest -q backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`. |
| AC11 | Backend source files are unchanged. | Evidence profile: ast_architecture_guard; `python` checks git status for backend app and backend tests. |
| AC12 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence and generated paths. |

## Implementation Tasks

- [ ] Task 1: Create the timestamped audit folder and story evidence artifact set. (AC: AC1, AC12)
- [ ] Task 2: Trace `LLMGateway.execute_request`, `_resolve_plan`, `_build_messages`, and `_call_provider`. (AC: AC2, AC3)
- [ ] Task 3: Map `build_user_payload` and `_prompt_visible_llm_astrology_input` field inclusion and exclusion. (AC: AC3, AC7)
- [ ] Task 4: Compare `compose_structured_messages` and `compose_chat_messages` message shapes. (AC: AC4, AC5)
- [ ] Task 5: Map `ProviderRuntimeManager` and `ProviderParameterMapper` parameter derivation. (AC: AC6)
- [ ] Task 6: Classify input validation, output validation, repair, and fallback paths as nominal or non nominal. (AC: AC8)
- [ ] Task 7: Map call logs, snapshots, usage, audit metadata, and observability propagation. (AC: AC9)
- [ ] Task 8: Evaluate existing runtime handoff and payload boundary tests, then record gaps. (AC: AC7, AC10)
- [ ] Task 9: Persist validation outputs and prove backend app and backend tests remain unchanged. (AC: AC11, AC12)

## Files to Inspect First

- `_story_briefs/cs-345-audit-runtime-gateway-handoff-provider-prompt-llm.md` - source scope and acceptance criteria.
- `_condamad/stories/CS-343-prompt-generation-surface-inventory/00-story.md` - prompt surface sequence context.
- `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/00-story.md` - preceding configuration audit context.
- `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md` - prompt payload boundary context.
- `_story_briefs/cs-339-aligner-provenance-audit-only-hors-prompt-llm-natal.md` - audit-only boundary context.
- `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md` - validation-only evidence context.
- `backend/app/domain/llm/runtime/gateway.py` - runtime gateway and provider handoff owner.
- `backend/app/domain/llm/runtime/contracts.py` - runtime request, message, provider, and result contracts.
- `backend/app/domain/llm/runtime/provider_runtime_manager.py` - provider call orchestration owner.
- `backend/app/domain/llm/runtime/provider_parameter_mapper.py` - provider parameter mapping owner.
- `backend/app/domain/llm/runtime/providers.py` - provider adapter contract owner.
- `backend/app/domain/llm/runtime/output_validator.py` - output validation owner.
- `backend/app/domain/llm/runtime/input_validation.py` - input validation owner.
- `backend/app/domain/llm/runtime/repair.py` - repair path owner.
- `backend/app/domain/llm/runtime/observability.py` - call log, snapshot, usage, and metadata owner.
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` - prompt boundary test evidence.
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` - architecture boundary test evidence.

## Runtime Source of Truth

- Primary source of truth:
  - Source traces from backend LLM runtime gateway, provider manager, parameter mapper, providers, validators, repair, and observability files.
  - `AST guard` checks for call order, function ownership, message constructors, and final provider handoff classification.
  - `pytest -q backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` for prompt-visible boundary evidence.
  - `pytest -q backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` for architecture boundary evidence.
- Secondary evidence:
  - Targeted `rg` scans for gateway, message composition, provider calls, validation, repair, snapshot, usage, and metadata symbols.
- Static scans alone are not sufficient for this story because:
  - The audit must prove which runtime object is handed to the provider after resolution, composition, validation, and parameter mapping.

## Contract Shape

- Contract type:
  - Timestamped backend runtime audit report and persistent evidence bundle.
- Fields:
  - `step`: sequenced gateway or provider handoff step.
  - `owner`: canonical source module or artifact owner.
  - `symbol or function`: concrete class, function, method, test, or helper symbol.
  - `input`: runtime value or data structure entering the step.
  - `output`: runtime value or data structure produced by the step.
  - `provider visibility`: prompt-visible, runtime-only, validation-only, audit-only, or not provider prompt.
  - `evidence`: short source, scan, `AST guard`, or `pytest` evidence.
  - `gap or next story marker`: CS-346, CS-347, needs-investigation, or no gap.
- Required report sections:
  - Executive summary.
  - Sequenced runtime trace.
  - Last payload before provider.
  - Structured message shape.
  - Chat message shape.
  - Provider parameter derivation.
  - `llm_astrology_input_v1` include and exclude matrix.
  - Input validation, output validation, repair, and fallback classification.
  - Observability metadata, call logs, snapshots, and usage.
  - Existing tests and gaps.
- Required fields:
  - step
  - owner
  - symbol or function
  - input
  - output
  - provider visibility
  - evidence
  - gap or next story marker
- Optional fields:
  - none for runtime handoff rows; non nominal recovery rows may use `not provider prompt` as visibility.
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
  - `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/evidence/runtime-handoff-scan-baseline.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/evidence/runtime-handoff-scan-after.txt`
- Expected invariant:
  - The only intended repository delta is the audit report, story evidence artifacts, generated review handoff, and validation output.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Runtime request execution | `backend/app/domain/llm/runtime/gateway.py` | prompt bootstrap or provider adapter |
| User payload construction | `backend/app/domain/llm/runtime/gateway.py` | output validator or observability code |
| Message composition | `backend/app/domain/llm/runtime/gateway.py` | provider runtime manager |
| Provider call orchestration | `backend/app/domain/llm/runtime/provider_runtime_manager.py` | prompt renderer or tests |
| Provider parameter mapping | `backend/app/domain/llm/runtime/provider_parameter_mapper.py` | gateway inline assumptions |
| Provider adapter contract | `backend/app/domain/llm/runtime/providers.py` | audit report prose |
| Input validation | `backend/app/domain/llm/runtime/input_validation.py` | provider adapter |
| Output validation | `backend/app/domain/llm/runtime/output_validator.py` | prompt composer |
| Repair behavior | `backend/app/domain/llm/runtime/repair.py` | provider parameter mapper |
| Observability metadata | `backend/app/domain/llm/runtime/observability.py` | prompt-visible payload |

## Mandatory Reuse / DRY Constraints

- Reuse the timestamped audit folder pattern from CS-343 and CS-344.
- Reuse the existing evidence artifact pattern under the story folder.
- Reuse source symbols and existing tests as evidence instead of copying gateway or provider code into the report.
- Reuse CS-335, CS-339, and CS-341 boundary terms for prompt-visible, runtime-only, validation-only, and audit-only data.
- Do not duplicate the CS-343 surface inventory or CS-344 configuration matrix; reference them and focus on runtime provider handoff.
- Do not introduce new dependencies.

## No Legacy / Forbidden Paths

- No legacy prompt handoff path may be accepted as a target implementation path.
- No compatibility provider handoff path may be added for this audit.
- No fallback implementation path may be added for this audit.
- Do not edit gateway, provider runtime, validators, repair, observability, tests, migrations, or frontend files.
- Do not treat recovery or fallback paths as the nominal provider handoff.
- Do not describe audit-only or validation-only fields as provider prompt material.

## Reintroduction Guard

- Exact forbidden implementation surfaces:
  - `backend/app/domain/llm/runtime/**` code edits.
  - `backend/tests/**` edits outside persisted validation evidence.
  - `frontend/src/**` edits.
  - `_condamad/stories/regression-guardrails.md` edits.
- Required deterministic guards:
  - `python` checks `git status --short -- backend/app/domain/llm/runtime backend/tests frontend/src`.
  - `rg` verifies the audit report contains structured, chat, provider parameters, exclusions, repair, and observability sections.
  - `AST guard` verifies the audit evidence references existing source symbols rather than new implementation changes.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Applicable only as backend boundary control; no API routing logic may move during audit. | `python` git-status guard; targeted `rg`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Applicable; validation plans must use collected backend pytest paths. | `pytest` paths in VC6 and VC7. |
| Registry gap | No exact guardrail exists for runtime provider handoff cartography. | Resolver output recorded in evidence. |

Non-applicable examples: RG-047, RG-052, and RG-041 are frontend or entitlement-documentation guardrails and remain out of scope.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline scan | `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/evidence/runtime-handoff-scan-baseline.txt` | Keep pre-audit source scan evidence. |
| After scan | `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/evidence/runtime-handoff-scan-after.txt` | Keep post-audit source scan evidence. |
| Symbol map | `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/evidence/runtime-handoff-symbol-map.md` | Keep runtime path and symbol evidence. |
| Audit report | `_condamad/audits/prompt-generation-cartography/YYYY-MM-DD-HHMM/03-runtime-gateway-handoff-audit.md` | Deliver the runtime gateway handoff audit. |
| Validation output | `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/evidence/validation.txt` | Keep validation command output. |
| Final evidence | `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/evidence/final-evidence.md` | Summarize final proof and residual gaps. |
| Review output | `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this runtime handoff audit story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/prompt-generation-cartography/YYYY-MM-DD-HHMM/03-runtime-gateway-handoff-audit.md` - audit deliverable.
- `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/evidence/runtime-handoff-scan-baseline.txt` - baseline scan artifact.
- `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/evidence/runtime-handoff-scan-after.txt` - after scan artifact.
- `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/evidence/runtime-handoff-symbol-map.md` - runtime symbol map.
- `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/evidence/validation.txt` - validation output artifact.
- `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/evidence/final-evidence.md` - final evidence summary.
- `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/generated/11-code-review.md` - generated review handoff.

Likely tests:

- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` - proves prompt-visible boundary behavior already covered by existing tests.
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` - proves payload architecture boundaries already covered by existing tests.

Files not expected to change:

- `backend/app/**` - out of scope; no runtime, provider, validation, repair, or observability code is edited.
- `backend/tests/**` - out of scope; existing tests may be executed or cited but not edited.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `_condamad/stories/regression-guardrails.md` - out of scope; registry enrichment is not authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `python -c "from pathlib import Path; p=Path('_condamad/audits/prompt-generation-cartography'); assert any(p.glob('*/03-runtime-gateway-handoff-audit.md'))"`
- VC2: `rg -n "execute_request|_resolve_plan|_build_messages|_call_provider" backend/app/domain/llm/runtime backend/tests`
- VC3: `rg -n "build_user_payload|compose_chat_messages|compose_structured_messages|_prompt_visible_llm_astrology_input" backend/app/domain/llm/runtime backend/tests`
- VC4: `rg -n "ProviderRuntimeManager|ProviderParameterMapper|response_format|temperature|max_tokens|metadata" backend/app/domain/llm/runtime backend/tests`
- VC5: `rg -n "runtime-gateway-handoff-audit|Last payload before provider|Structured message shape|Chat message shape" _condamad`
- VC6: `pytest -q backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- VC7: `pytest -q backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`
- VC8: `python -c "import subprocess; subprocess.run(['git','diff','--quiet','--','backend/app','backend/tests','frontend/src'], check=True)"`
- VC9 evidence paths:
  `python -c "from pathlib import Path; p='_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm'; r=Path(p); assert (r/'evidence').exists()"`
  Run `python` with the same `p` value to assert `(r/'generated').exists()`.
- VC10: `ruff format .`
- VC11: `ruff check .`
- VC12: `pytest -q`

## Regression Risks

- Risk: the audit could describe the resolved plan instead of the final provider payload.
  - Mitigation: AC3 and the Runtime Source of Truth require tracing the object passed to provider handoff code.
- Risk: structured and chat modes could be merged into one generic message description.
  - Mitigation: AC4 and AC5 require separate report sections and symbol evidence.
- Risk: audit-only or validation-only fields could be treated as prompt material.
  - Mitigation: AC7 requires existing boundary tests and an explicit include/exclude matrix.
- Risk: recovery behavior could be documented as nominal runtime.
  - Mitigation: AC8 and the Operation Contract require non nominal classification for recovery and fallback paths.
- Risk: the report could duplicate CS-344 configuration mapping instead of documenting runtime execution.
  - Mitigation: DRY constraints require CS-344 as context while focusing this story on gateway execution and provider handoff.

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
- Record any missing runtime-provider-handoff guardrail as `Registry gap` in story evidence, not in the registry.

## References

- `_story_briefs/cs-345-audit-runtime-gateway-handoff-provider-prompt-llm.md`
- `_condamad/stories/CS-343-prompt-generation-surface-inventory/00-story.md`
- `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/00-story.md`
- `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md`
- `_story_briefs/cs-339-aligner-provenance-audit-only-hors-prompt-llm-natal.md`
- `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md`
- `_condamad/stories/regression-guardrails.md`
