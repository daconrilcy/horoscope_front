# Story CS-376 validation-provider-smoke-theme-astral: Add Theme Astral Provider Smoke Validation
Status: done

## Trigger / Source

- Source brief: `_story_briefs/cs-376-ajouter-validation-provider-smoke-theme-astral-sans-production.md`.
- Selected mode: Repo-informed story.
- Reason for change: CS-368 and CS-369 leave a residual risk because no real LLM provider call proved acceptance of `theme_astral_llm_input_v1`.
- Source-alignment evidence: this story keeps the opt-in provider validation, schema verdict, cost limits, secret safety, and CI standard skip from the brief.

## Objective

Add one non-production provider smoke validation for `theme_astral_llm_input_v1` that is disabled by default and records safe proof metadata.

## Target State

- A pytest `provider_smoke` test uses one example `theme_astral_llm_input_v1` payload from the prompt-generation cartography examples.
- The provider call runs only with explicit `RUN_THEME_ASTRAL_PROVIDER_SMOKE=1` and valid provider credentials.
- The run performs one provider attempt with a timeout and validates output against `theme_astral_response_contract_v1`.
- The standard local and CI validation paths continue to run with `-m "not provider_smoke"`.
- The validation proof documents costs, prerequisites, limits, and non-sensitive metadata only.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-376-ajouter-validation-provider-smoke-theme-astral-sans-production.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-376`.
- Evidence 3: `backend/app/domain/llm/runtime/gateway.py` - provider handoff currently accepts `theme_astral_llm_input_v1`.
- Evidence 4: `backend/app/domain/llm/configuration/theme_astral_contracts.py` - response contract id and schema constants exist.
- Evidence 5: `backend/pyproject.toml` - pytest markers exist and `provider_smoke` is not declared yet.
- Evidence 6: `_condamad/stories/regression-guardrails.md` - targeted IDs `RG-002` and `RG-022` were consulted.
- Source-alignment review: PASS; every source AC maps to opt-in provider execution, schema validation, secret safety, or non-CI evidence.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend provider smoke validation for `theme_astral_llm_input_v1`.
  - Pytest marker registration for `provider_smoke`.
  - Non-sensitive proof artifact or README command for the smoke run.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling, migrations, and prompt engineering.
  - Changing the default provider, production execution behavior, or deterministic tests outside the smoke boundary.
- Explicit non-goals:
  - No CI requirement for real provider credentials.
  - No persisted full LLM response by default.
  - No new provider package or replacement provider.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only an opt-in non-production provider smoke validation.
  - Keep standard validation green without credentials.
  - Store only non-sensitive metadata and schema verdict artifacts.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: a real provider call must become mandatory in CI.
- Additional validation rules:
  - Runtime evidence must include `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_smoke.py`.
  - Runtime evidence must prove loaded config or env gating for `RUN_THEME_ASTRAL_PROVIDER_SMOKE`.
  - AST guard or static scan must prove no secret value is printed or persisted.
  - The provider smoke path must call the provider once per run.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, loaded env gating, and provider call count prove the runtime smoke behavior. |
| Baseline Snapshot | yes | Before and after proof artifacts show the smoke path is opt-in and non-sensitive. |
| Ownership Routing | yes | Smoke logic belongs in backend tests, not production gateway code unless a small helper is justified. |
| Allowlist Exception | no | No broad allowlist handling is authorized for this smoke validation. |
| Contract Shape | yes | The response must validate against `theme_astral_response_contract_v1`. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | The smoke test must stay disabled without explicit opt-in and credentials. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The smoke is disabled by default. | Evidence profile: json_contract_shape; `pytest` runs `tests/llm_orchestration/test_theme_astral_provider_smoke.py`. |
| AC2 | Missing opt-in causes a clean skip. | Evidence profile: runtime_openapi_contract; `pytest` runs `tests/llm_orchestration/test_theme_astral_provider_smoke.py`. |
| AC3 | Provider opt-in performs one call. | Evidence profile: ast_architecture_guard; `pytest` runs `tests/llm_orchestration/test_theme_astral_provider_smoke.py`. |
| AC4 | The response contract is validated. | Evidence profile: json_contract_shape; `pytest` runs `tests/llm_orchestration/test_theme_astral_provider_smoke.py`. |
| AC5 | Secrets are not logged. | Evidence profile: targeted_forbidden_symbol_scan; `rg -n "OPENAI_API_KEY|api_key|Authorization" backend/tests backend/app`. |
| AC6 | The marker is registered. | Evidence profile: targeted_forbidden_symbol_scan; `rg -n "provider_smoke" backend/pyproject.toml backend/tests`. |
| AC7 | Standard tests exclude the smoke. | Evidence profile: no_legacy_contract; `python -B -m pytest -q tests --tb=short -m "not provider_smoke"`. |
| AC8 | Smoke proof is persisted. | Evidence profile: baseline_before_after_diff; activated-venv `python` checks `evidence/provider-smoke-after.md`. |

## Implementation Tasks

- [ ] Task 1: Inspect current provider gateway, response schema constants, test layout, and example payloads. (AC: AC1, AC4)
- [ ] Task 2: Add a `provider_smoke` pytest covering skip behavior without opt-in or credentials. (AC: AC1, AC2)
- [ ] Task 3: Add the opt-in provider path with one attempt, timeout, and safe metadata capture. (AC: AC3, AC5)
- [ ] Task 4: Validate provider JSON output against `THEME_ASTRAL_RESPONSE_SCHEMA`. (AC: AC4)
- [ ] Task 5: Register the `provider_smoke` marker in `backend/pyproject.toml`. (AC: AC6, AC7)
- [ ] Task 6: Persist proof artifacts documenting commands, cost limit, preconditions, skip result, and schema verdict. (AC: AC8)
- [ ] Task 7: Run deterministic validation with the smoke excluded from standard tests. (AC: AC7)

## Files to Inspect First

- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/README.md`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/basic-provider-payload.json`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/premium-provider-payload.json`
- `backend/pyproject.toml`

## Runtime Source of Truth

- Primary source of truth:
  - `pytest`, `AST guard`, loaded config/env gating, provider client call count, and JSON schema validation.
- Secondary evidence:
  - Targeted `rg` scans for `provider_smoke`, `RUN_THEME_ASTRAL_PROVIDER_SMOKE`, and provider credential handling.
- Static scans alone are not sufficient for this story because:
  - Runtime skip, opt-in gating, one-call behavior, and output validation must be proven from executed pytest paths.

## Contract Shape

- Contract type:
  - Non-production provider smoke and JSON response validation.
- Fields:
  - `title`: non-empty string.
  - `summary`: non-empty string.
  - `sections`: array with one to eight items.
  - `evidence`: array of short non-empty strings.
  - `contract_trace`: object with exact contract ids.
- Required fields:
  - `title`, `summary`, `sections`, `evidence`, `contract_trace`.
- Optional fields:
  - none.
- Status codes:
  - none; this story does not create an API route.
- Serialization names:
  - JSON keys must match `THEME_ASTRAL_RESPONSE_SCHEMA`.
- Frontend type impact:
  - none.
- Generated contract impact:
  - none; the runtime validation imports `THEME_ASTRAL_RESPONSE_SCHEMA`.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-376-validation-provider-smoke-theme-astral/evidence/provider-smoke-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-376-validation-provider-smoke-theme-astral/evidence/provider-smoke-after.md`
- Expected invariant:
  - The only intended behavior delta is a new opt-in provider smoke validation outside standard CI tests.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Provider smoke test | `backend/tests/llm_orchestration/test_theme_astral_provider_smoke.py` | `frontend/src/**` |
| Response schema validation | `backend/app/domain/llm/configuration/theme_astral_contracts.py` | ad hoc duplicated schema in test |
| Example payload source | `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/**` | inline copied payload |
| Marker declaration | `backend/pyproject.toml` | unregistered pytest marker |

## Mandatory Reuse / DRY Constraints

- Reuse `THEME_ASTRAL_INPUT_CONTRACT_ID`, `THEME_ASTRAL_RESPONSE_CONTRACT_ID`, and `THEME_ASTRAL_RESPONSE_SCHEMA`.
- Reuse existing gateway/provider call conventions from `LLMGateway` or existing provider runtime tests.
- Reuse the existing example payload JSON instead of duplicating a full payload inside test code.
- Keep helper functions small and named for skip gating, payload loading, provider call, schema validation, and metadata redaction.
- New or significantly modified backend files must keep the required French file comment and French docstrings for public or non-trivial helpers.

## No Legacy / Forbidden Paths

- No legacy route path, endpoint, or provider path may be added for this validation.
- No compatibility route path or alternate smoke command may be added.
- No fallback provider behavior may make the smoke pass without the configured provider call.
- Do not store real provider output by default.
- Do not print credential values, request headers, raw API payload secrets, or authorization data.
- Do not add external packages or a second schema validation mechanism.

## Reintroduction Guard

- Guard target: opt-in execution and no secret persistence for `provider_smoke`.
- Forbidden surfaces:
  - Running provider smoke without `RUN_THEME_ASTRAL_PROVIDER_SMOKE=1`.
  - Running provider smoke as part of standard `pytest -q tests --tb=short -m "not provider_smoke"`.
  - Persisting full LLM response content by default.
- Required guard evidence:
  - `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_smoke.py -m provider_smoke`
  - `python -B -m pytest -q tests --tb=short -m "not provider_smoke"`
  - `rg -n "provider_smoke|RUN_THEME_ASTRAL_PROVIDER_SMOKE|OPENAI_API_KEY" tests pyproject.toml`

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend logic must not move into API router surfaces. | `rg` targeted paths; backend pytest. |
| RG-022 `align-prompt-generation-story-validation-paths` | Prompt-generation validation paths must remain collected pytest paths. | `pytest` targeted path; marker scan. |
| Not applicable: RG-041 | Entitlement docs are not touched. | Manual check: no entitlement docs in likely files. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before smoke proof | `_condamad/stories/CS-376-validation-provider-smoke-theme-astral/evidence/provider-smoke-before.md` | Capture current absence of provider smoke. |
| After smoke proof | `_condamad/stories/CS-376-validation-provider-smoke-theme-astral/evidence/provider-smoke-after.md` | Capture skip and schema verdict. |
| Validation output | `_condamad/stories/CS-376-validation-provider-smoke-theme-astral/generated/10-final-evidence.md` | Keep deterministic validation results. |
| Review output | `_condamad/stories/CS-376-validation-provider-smoke-theme-astral/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this single opt-in provider smoke validation.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/tests/llm_orchestration/test_theme_astral_provider_smoke.py` - add opt-in provider smoke validation.
- `backend/pyproject.toml` - declare the `provider_smoke` marker.
- `_condamad/stories/CS-376-validation-provider-smoke-theme-astral/evidence/provider-smoke-before.md` - baseline proof.
- `_condamad/stories/CS-376-validation-provider-smoke-theme-astral/evidence/provider-smoke-after.md` - final proof.

Likely tests:

- `backend/tests/llm_orchestration/test_theme_astral_provider_smoke.py` - skip, opt-in, one-attempt, schema validation, and redaction behavior.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no API route is touched.
- `backend/app/infra/db/**` - out of scope; no persistence schema is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1; cd backend; ruff format .`
- VC2: `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .`
- VC3: `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests --tb=short -m "not provider_smoke"`
- VC4: `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_smoke.py -m provider_smoke --tb=short`
- VC5: `.\.venv\Scripts\Activate.ps1; cd backend; rg -n "provider_smoke|RUN_THEME_ASTRAL_PROVIDER_SMOKE|OPENAI_API_KEY" tests pyproject.toml`
- VC6: provider opt-in manual command, only with explicit user authorization and valid credentials:
  - `.\.venv\Scripts\Activate.ps1; cd backend; $env:RUN_THEME_ASTRAL_PROVIDER_SMOKE='1'; python -B -m pytest -q tests -m provider_smoke --tb=short`
- VC7: from repository root, after `.\.venv\Scripts\Activate.ps1`, run:
  - `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-376-validation-provider-smoke-theme-astral/evidence/provider-smoke-after.md').exists()"`

## Regression Risks

- Risk: provider smoke becomes part of standard CI and creates fragile external-service failures.
- Mitigation: registered marker, explicit env gate, and standard validation command with `-m "not provider_smoke"`.
- Risk: provider response content or credentials are written into evidence.
- Mitigation: metadata-only artifact, redaction scan, and no full response persistence by default.
- Risk: the test validates a copied schema instead of the canonical contract.
- Mitigation: import `THEME_ASTRAL_RESPONSE_SCHEMA` from `theme_astral_contracts.py`.
- Risk: real provider use creates cost drift.
- Mitigation: one attempt per run, timeout, example payload only, and manual opt-in command.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep provider credentials in environment variables only.
- Keep the provider smoke disabled by default in local runs and CI standard validation.
- Use the existing venv activation rule before every Python command.

## References

- `_story_briefs/cs-376-ajouter-validation-provider-smoke-theme-astral-sans-production.md`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/pyproject.toml`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/README.md`
- `_condamad/stories/regression-guardrails.md#RG-002`
- `_condamad/stories/regression-guardrails.md#RG-022`
