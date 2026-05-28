# Story CS-358 generer-exemples-json-prompts-theme-astral-par-plan: Generate Natal Prompt JSON Examples By Plan
Status: ready-to-review

## Trigger / Source

- Source brief: `_story_briefs/cs-358-generer-exemples-json-prompts-theme-astral-par-plan.md`.
- Selected mode: Repo-informed story, because the examples must align with current prompt owners, tests, and upstream documentation stories.
- Source problem: prompt-generation documentation lacks concrete final provider-handoff payload examples for `free`, `basic`, and `premium`.
- Source stakes:
  - Readers must inspect final messages without a real LLM call.
  - The plan differences must be visible in versioned JSON payloads.
  - Prompt-visible content must stay separated from audit-only and validation-only data.
  - The missing birth time must be handled as an explicit demonstration convention.
  - The examples must not imply verified houses, Ascendant, MC, or provider output.
- Source-alignment evidence: objective, ACs, tasks, files, validation plan, non-goals, and guardrails preserve all mandatory brief deliverables.

## Objective

Create auditable example files showing final natal prompt payloads for `free`, `basic`, and `premium` plans.

The examples must use the birth case `1973-04-24`, Paris, France, timezone `Europe/Paris`, and a documented local time convention of `12:00:00`.
They must show normalized input, intermediate prompt signals, final messages, provider parameters, and excluded audit-only fields without provider access.

## Target State

- `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/README.md` exists.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/free-provider-payload.json` exists.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/basic-provider-payload.json` exists.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/premium-provider-payload.json` exists.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/intermediate-data.json` exists.
- The payloads represent final provider-handoff shape, not a provider response.
- The README states whether data came from runtime builders or from clearly marked `synthetic_example` fixtures.
- Backend runtime, prompt configuration, calculations, frontend UI, database schema, migrations, provider integration, and secrets remain unchanged.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-358-generer-exemples-json-prompts-theme-astral-par-plan.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-358`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - current CS-350 cartography exists.
- Evidence 5: `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md` - preferred CS-356 document is absent now.
- Evidence 6: `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/00-story.md` - upstream plan document story exists.
- Evidence 7: `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/00-story.md` - upstream diagram story exists.
- Evidence 8: `backend/app/domain/llm/runtime/gateway.py` - `LLMGateway` owns prompt filtering and provider message composition.
- Evidence 9: `backend/app/domain/llm/runtime/adapter.py` - `AIEngineAdapter` delegates business use cases to the gateway.
- Evidence 10: `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - prompt-visible and audit-only roles are defined.
- Evidence 11: `backend/app/services/llm_generation/natal/interpretation_service.py` - natal service builds `llm_astrology_input_v1`.
- Evidence 12: `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` - provider-boundary tests use local doubles.
- Evidence 13: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver.

Repository structure alert: no repository root is missing for this story. The preferred CS-356 generated document is absent and must be treated as upstream context.

## Domain Boundary

- Domain: documentation-examples
- In scope:
  - Example files under `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/`.
  - Final provider-handoff JSON examples for `free`, `basic`, and `premium`.
  - Intermediate data explaining normalized birth input, calculation assumptions, prompt signals, plan differences, and limits.
  - Documentation of the `12:00:00` local demonstration time convention.
  - Validation evidence proving valid JSON, distinct plan payloads, prompt-visible user content, and no provider call.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling, migrations, prompt seeds, output schemas, and provider calls.
  - Runtime code changes, production prompt changes, astrology calculation changes, persisted user interpretation, and branch creation.
- Explicit non-goals:
  - No real LLM call.
  - No provider response.
  - No secret, credential, token, or API key in examples.
  - No claim that houses, Ascendant, or MC are verified from a real birth time.
  - No frontend route, screen, client generation, or UI validation.

Named brief primitives in scope:

- `README.md`
- `free-provider-payload.json`
- `basic-provider-payload.json`
- `premium-provider-payload.json`
- `intermediate-data.json`
- `birth_input`
- `normalization`
- `calculation_assumptions`
- `structured_facts_v1_sample`
- `narrative_signals_sample`
- `client_projection_sample`
- `llm_astrology_input_v1_by_plan`
- `plan_differences`
- `provider_call_performed`
- `system`
- `developer`
- `persona`
- `user`
- `response_format`
- `provider_parameters`
- `audit_excluded_from_prompt`

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this documented example payload generation contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Create example documentation and JSON files only.
  - Create story execution evidence only.
  - Keep backend application files unchanged.
  - Keep backend test files unchanged unless a focused example validator is added under `backend/tests`.
  - Keep frontend files unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: runtime extraction requires external provider access or unavailable configuration secrets.
- Additional validation rules:
  - `python` JSON parsing must prove all four JSON files are valid.
  - `pytest -q backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py --tb=short` must remain green.
  - `rg` scans must prove `provider_call_performed`, all three plans, the birth case, and the synthetic/runtime marker are present.
  - `rg` scans must prove no secret, API key, provider response, or credential marker is present in the example folder.
  - `AST guard` or bounded `git status` evidence must prove backend runtime files are unchanged unless a focused validator test is added.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Backend owners and tests define the provider-handoff and prompt-visible boundaries. |
| Baseline Snapshot | yes | Before and after scans prove the only allowed surface delta is the example folder and story evidence. |
| Ownership Routing | yes | Examples belong under `_condamad/examples`, not backend runtime, frontend code, or prompt seeds. |
| Allowlist Exception | no | No allowlist handling is authorized for this example-generation story. |
| Contract Shape | yes | JSON files must follow the exact provider payload and intermediate-data structures from the brief. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Provider calls, secrets, provider responses, and audit-only fields must stay outside prompt messages. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The required example folder contains five deliverables. | Evidence profile: baseline_before_after_diff; `python` checks all expected paths. |
| AC2 | All example JSON files parse successfully. | Evidence profile: json_contract_shape; `python` loads the four JSON files. |
| AC3 | Each plan payload is distinct. | Evidence profile: json_contract_shape; `python` compares free, basic, premium payloads. |
| AC4 | Message roles follow provider handoff. | Evidence profile: json_contract_shape; `python` checks every payload message role list; `AST guard`. |
| AC5 | No provider call is represented. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scan; targeted `pytest` provider-boundary test. |
| AC6 | User messages contain prompt-visible blocks only. | Evidence profile: json_contract_shape; `python` rejects audit-only keys inside each user message JSON. |
| AC7 | Audit-only exclusions are listed outside prompt content. | Evidence profile: json_contract_shape; `python` checks `audit_excluded_from_prompt` on every payload. |
| AC8 | Missing birth time is documented as a convention. | Evidence profile: targeted_forbidden_symbol_scan; `rg` finds `12:00:00`, `Europe/Paris`, and `synthetic_example`. |
| AC9 | README explains generation method. | Evidence profile: targeted_forbidden_symbol_scan; `rg` finds `runtime-generated` or `synthetic_example` in README. |
| AC10 | Forbidden provider artifacts are absent. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks forbidden tokens in the example folder. |

## Implementation Tasks

- [x] Task 1: Inspect source documents and backend owners for provider-handoff shape and prompt-visible boundaries. (AC: AC4, AC6, AC7)
- [x] Task 2: Decide whether runtime builders can produce local data without provider access. (AC: AC5, AC9)
- [x] Task 3: Create `intermediate-data.json` with birth input, assumptions, samples, plan differences, limits, and `provider_call_performed: false`. (AC: AC1, AC2, AC8)
- [x] Task 4: Create `free-provider-payload.json` with the final prompt payload for the free plan. (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7)
- [x] Task 5: Create `basic-provider-payload.json` with a distinct final prompt payload for the basic plan. (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7)
- [x] Task 6: Create `premium-provider-payload.json` with a distinct final prompt payload for the premium plan. (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7)
- [x] Task 7: Create README generation notes, source citations, time convention notes, and no-provider-call proof. (AC: AC5, AC8, AC9, AC10)
- [x] Task 8: Persist validation evidence for path checks, JSON parsing, scans, test command output, and backend runtime unchanged proof. (AC: AC1, AC2, AC5, AC10)

## Files to Inspect First

- `_story_briefs/cs-358-generer-exemples-json-prompts-theme-astral-par-plan.md`
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/00-story.md`
- `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/00-story.md`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`
- `backend/tests/evaluation/test_differentiation.py`

Assumption-risk note: `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md` may be created by CS-356 before implementation starts.

## Runtime Source of Truth

- Primary source of truth:
  - `LLMGateway.build_user_payload`, `compose_structured_messages`, and `ProviderRuntimeManager` handoff call shape.
  - `LLM_ASTROLOGY_INPUT_DATA_ROLES` and `LLMAstrologyInputV1Builder`.
  - `NatalInterpretationService._build_llm_astrology_input_v1`.
  - `AST guard` over backend source files to prove example generation does not alter runtime owners.
  - `pytest -q backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py --tb=short`.
- Secondary evidence:
  - `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`.
  - CS-356 and CS-357 story contracts.
  - Targeted `rg` scans over the generated example folder.
- Static scans alone are not sufficient for this story because:
  - The provider-boundary test must prove the local double path still inspects messages without external provider access.

## Contract Shape

- Contract type:
  - Versioned documentation example JSON and README.
- Fields:
  - `use_case`: string beginning with `natal_`.
  - `plan`: one of `free`, `basic`, or `premium`.
  - `mode`: `structured`.
  - `provider_call_performed`: `false`.
  - `model`: configured value or documented placeholder.
  - `messages`: ordered list of provider messages.
  - `response_format`: JSON schema response contract.
  - `provider_parameters`: provider parameter object.
  - `audit_excluded_from_prompt`: audit-only field list.
- Required fields:
  - `use_case`, `plan`, `mode`, `provider_call_performed`, `model`, `messages`, `response_format`, `provider_parameters`, `audit_excluded_from_prompt`.
- Optional fields:
  - none for the minimum final provider payload files.
- Status codes:
  - none; this story creates static example artifacts and no HTTP route.
- Final provider payload files:
  - `use_case`: string beginning with `natal_`.
  - `plan`: one of `free`, `basic`, or `premium`.
  - `mode`: `structured`.
  - `provider_call_performed`: `false`.
  - `model`: configured value or documented placeholder.
  - `messages`: ordered list of `system`, `developer`, `developer`, `user`.
  - `response_format`: object with `type: json_schema` and `json_schema`.
  - `provider_parameters`: object with token, temperature, reasoning, and verbosity fields.
  - `audit_excluded_from_prompt`: list including `evidence`, `provenance`, `projection_hash`, `llm_input_hash`, `provider_response`, and `observability`.
- Intermediate data file:
  - Required keys: `birth_input`, `normalization`, `calculation_assumptions`, `structured_facts_v1_sample`, `narrative_signals_sample`.
  - Required keys: `client_projection_sample`, `llm_astrology_input_v1_by_plan`, `plan_differences`, `limits`, `data_quality_warnings`.
  - Required keys: `generation_method` and `provider_call_performed`.
- Serialization names:
  - JSON keys use snake_case exactly as listed in the source brief.
- Frontend type impact:
  - none.
- Generated contract impact:
  - no OpenAPI, frontend type, database, or generated client impact.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-358-generer-exemples-json-prompts-theme-astral-par-plan/evidence/baseline-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-358-generer-exemples-json-prompts-theme-astral-par-plan/evidence/baseline-after.txt`
- Expected invariant:
  - The only intended product artifact delta is `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/`.
- Runtime invariant:
  - Backend runtime files named in this story remain unchanged unless the implementer adds a focused validator test.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Example README | `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/README.md` | `backend/app/**` |
| Example payload JSON | `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/*-provider-payload.json` | `frontend/src/**` |
| Intermediate sample JSON | `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/intermediate-data.json` | `backend/app/domain/**` |
| Story execution evidence | `_condamad/stories/CS-358-generer-exemples-json-prompts-theme-astral-par-plan/evidence/**` | `_condamad/examples/**` |

## Mandatory Reuse / DRY Constraints

- Reuse the existing gateway, adapter, natal service, and `llm_astrology_input_v1` contracts as source truth.
- Reuse the existing provider-boundary tests for no-provider-call proof.
- Do not duplicate runtime prompt-building logic in application code.
- Do not introduce a second example folder for the same birth case.
- Do not create external packages or scripts solely to format static JSON.
- If synthetic fixtures are used, centralize repeated plan-neutral data in `intermediate-data.json` and keep plan-specific differences explicit.

## No Legacy / Forbidden Paths

- No legacy prompt carrier may be reintroduced into provider message `user` content.
- No compatibility route, API endpoint, or frontend screen may be added for these examples.
- No fallback provider behavior may be documented as a normal generation method.
- Forbidden prompt-visible fields inside the `user` message: `evidence`, `provenance`, `projection_hash`, `llm_input_hash`, `provider_response`, `observability`.
- Forbidden output content: real provider response, credential, API key, bearer token, `.env` value, or personal secret.
- Forbidden destinations: `frontend/src/**`, `backend/app/infra/**`, `backend/app/api/**`, migrations, prompt seeds, and production prompt configuration.

## Reintroduction Guard

- Guard exact forbidden provider-call claims:
  - `rg -n "provider_response|api_key|OPENAI_API_KEY|sk-|Bearer|credential|secret" _condamad/examples/prompt-generation-cartography/1973-04-24-paris`
- Guard prompt-only boundary:
  - `python` must parse each `messages[-1].content` JSON and reject audit-only keys.
- Guard no external provider access:
  - `pytest -q backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py --tb=short`
- Guard destination drift:
  - `git status --short backend/app frontend/src` must show no runtime or frontend source delta unless a focused test file is intentionally added.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `Routeurs API v1` | Backend API routing must stay out of this example story. | `git status`; targeted `rg`. |
| RG-022 `Plans de validation des stories prompt-generation` | Prompt-generation examples need explicit validation evidence. | `python` JSON checks; `pytest`. |
| Registry gap | No exact route-specific guardrail applies because no API route is in scope. | Scoped resolver output. |

Non-applicable examples:

- `RG-041` frontend entitlement documentation is out of scope because no frontend surface is touched.
- `RG-047` inline TSX styling is out of scope because no TSX file is touched.
- `RG-052` CSS namespace migration is out of scope because no CSS or frontend migration is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline before | `_condamad/stories/CS-358-generer-exemples-json-prompts-theme-astral-par-plan/evidence/baseline-before.txt` | Capture pre-change scope state. |
| Baseline after | `_condamad/stories/CS-358-generer-exemples-json-prompts-theme-astral-par-plan/evidence/baseline-after.txt` | Capture final changed paths. |
| JSON validation | `_condamad/stories/CS-358-generer-exemples-json-prompts-theme-astral-par-plan/evidence/json-validation.txt` | Prove generated JSON parses. |
| Provider test | `_condamad/stories/CS-358-generer-exemples-json-prompts-theme-astral-par-plan/evidence/provider-boundary-test.txt` | Prove no provider call. |
| Forbidden scan | `_condamad/stories/CS-358-generer-exemples-json-prompts-theme-astral-par-plan/evidence/forbidden-scan.txt` | Prove secrets and provider responses are absent. |
| Review output | `_condamad/stories/CS-358-generer-exemples-json-prompts-theme-astral-par-plan/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/README.md` - explain generation method and no-provider-call proof.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/free-provider-payload.json` - final free payload.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/basic-provider-payload.json` - final basic payload.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/premium-provider-payload.json` - final premium payload.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/intermediate-data.json` - shared normalized and intermediate sample data.
- `_condamad/stories/CS-358-generer-exemples-json-prompts-theme-astral-par-plan/evidence/**` - validation handoff artifacts.

Likely tests:

- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` - existing no-provider-call and prompt-boundary proof.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` - existing contract boundary proof.
- `backend/tests/evaluation/test_differentiation.py` - existing plan differentiation reference.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no API route is touched.
- `backend/app/infra/**` - out of scope; no persistence or external adapter is touched.
- `backend/app/domain/llm/runtime/gateway.py` - source truth to inspect, not an expected edit.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - source truth to inspect, not an expected edit.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - source truth to inspect, not an expected edit.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `rg -n "provider_call_performed|1973-04-24|Paris|free|basic|premium|synthetic_example|runtime-generated" _condamad/examples/prompt-generation-cartography/1973-04-24-paris`
- VC2: activate venv, then run `python -B -m json.tool` on each JSON file in the example folder.
- VC3: activate venv, then run this distinct-plan check:

```powershell
$root = "_condamad/examples/prompt-generation-cartography/1973-04-24-paris"
python -B -c @"
import json, pathlib
r = pathlib.Path('$root')
plans = ['free', 'basic', 'premium']
payloads = [json.loads((r / f'{plan}-provider-payload.json').read_text(encoding='utf-8')) for plan in plans]
assert len({json.dumps(payload, sort_keys=True) for payload in payloads}) == 3
"@
```

- VC4: activate venv, then run this prompt-boundary check:

```powershell
$root = "_condamad/examples/prompt-generation-cartography/1973-04-24-paris"
python -B -c @"
import json, pathlib
r = pathlib.Path('$root')
bad = {'evidence', 'provenance', 'projection_hash', 'llm_input_hash', 'provider_response', 'observability'}
for plan in ['free', 'basic', 'premium']:
    payload = json.loads((r / f'{plan}-provider-payload.json').read_text(encoding='utf-8'))
    assert bad.isdisjoint(json.loads(payload['messages'][-1]['content']))
"@
```
- VC5: `rg -n "provider_response|api_key|OPENAI_API_KEY|sk-|Bearer|credential|secret" _condamad/examples/prompt-generation-cartography/1973-04-24-paris`
- VC6: `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py --tb=short`
- VC7: `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py --tb=short`
- VC8: `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/evaluation/test_differentiation.py --tb=short`
- VC9: `.\.venv\Scripts\Activate.ps1; ruff format backend`
- VC10: `.\.venv\Scripts\Activate.ps1; ruff check backend`
- VC11: `git status --short backend/app frontend/src`

## Regression Risks

- The examples may look like real astrological results if synthetic data is not labeled.
- The missing birth time may make houses, Ascendant, or MC appear verified.
- The user message may accidentally include audit-only fields that backend code keeps outside provider prompt material.
- Plan examples may differ only by label rather than by visible prompt content or budget.
- A secret-like placeholder may be added to examples and later copied into documentation.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python, pip, pytest, or ruff command.
- Keep application source changes out of scope unless a focused test is required to prove this exact example contract.
- Use `12:00:00` local time only as a demonstration convention and state that dependent houses, Ascendant, and MC are not verified.
- Never call OpenAI, another LLM provider, or external provider runtime while producing these examples.

## References

- `_story_briefs/cs-358-generer-exemples-json-prompts-theme-astral-par-plan.md`
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/00-story.md`
- `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/00-story.md`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`
- `backend/tests/evaluation/test_differentiation.py`
