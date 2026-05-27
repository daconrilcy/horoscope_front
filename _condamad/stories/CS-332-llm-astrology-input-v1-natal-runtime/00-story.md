# Story CS-332 llm-astrology-input-v1-natal-runtime: Wire llm_astrology_input_v1 Into Natal Runtime
Status: done

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-332-brancher-llm-astrology-input-dans-execution-natale.md`.
- Upstream story: CS-330 defines the `llm_astrology_input_v1` internal contract.
- Upstream story: CS-331 defines the mapper that feeds `llm_astrology_input_v1`.
- Transition report: `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`.
- Transition register: `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/03-legacy-transition.md`.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: the natal LLM path still passes prompt-visible chart carriers while the schema-owned LLM input is not wired.
- Source-alignment evidence: PASS; ACs preserve runtime transport, prompt visibility, context ownership and transition compatibility stakes.

## Objective

Wire `llm_astrology_input_v1` into the backend natal LLM execution path so the prompt runtime consumes the schema-owned rich input.

The implementation must make the rich contract prompt-visible and keep current chart carriers as named transition inputs only.

## Target State

- `NatalExecutionInput` carries `llm_astrology_input_v1` as an explicit versioned field or wrapper.
- The natal interpretation service builds or receives `llm_astrology_input_v1` before calling `AIEngineAdapter.generate_natal_interpretation`.
- `ExecutionContext` carries control metadata, request metadata and prompt runtime flags without becoming the owner of astrology facts.
- `LLMGateway` and `PromptRenderer` can render `llm_astrology_input_v1` through a schema-owned placeholder or explicit input entry.
- The final user message or rendered prompt payload contains the structured `llm_astrology_input_v1` content.
- When `llm_astrology_input_v1` is present, `chart_json` is not used as silent prompt-visible replacement material.
- Remaining transition branches for `chart_json`, `natal_data` and prompt fallback behavior are named and bounded in code or tests.
- No public API route, frontend, provider, DB schema, migration, auth, i18n, style or build surface changes.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-332-brancher-llm-astrology-input-dans-execution-natale.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-332`.
- Evidence 3: `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md` - upstream contract brief read.
- Evidence 4: `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md` - upstream mapper brief read.
- Evidence 5: `interpretation_service.py` currently builds `chart_json_dict` and passes `chart_json` plus `natal_data`.
- Evidence 6: `backend/app/domain/llm/runtime/contracts.py` contains `NatalExecutionInput` and `ExecutionContext`.
- Evidence 7: `backend/app/domain/llm/runtime/adapter.py` currently maps natal input into `ExecutionContext`.
- Evidence 8: `backend/app/domain/llm/prompting/prompt_renderer.py` is the current renderer file for `PromptRenderer`.
- Evidence 9: `_condamad/stories/regression-guardrails.md` was consulted through scoped resolver output and targeted ID lookup.
- Repository structure alert: `backend/app/domain/llm/runtime/prompt_renderer.py` is absent; renderer ownership is under `domain/llm/prompting`.
- Repository structure alert: `backend/app/domain/llm/runtime/models.py` is absent; runtime models are in `domain/llm/runtime/contracts.py`.
- Source-alignment evidence: PASS; the story covers every named brief primitive and keeps chart carrier retirement out of scope.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend natal LLM runtime wiring for `llm_astrology_input_v1`.
  - `NatalExecutionInput` transport of the schema-owned rich input.
  - Adapter and gateway propagation into the prompt rendering variables or input payload.
  - `ExecutionContext` ownership cleanup so astrology facts remain in the schema-owned contract.
  - Tests proving prompt-visible structured content and no silent chart carrier substitution.
  - Bounded classification of remaining transition compatibility branches.
- Out of scope:
  - Frontend UI, public API route, DB schema, migrations, auth, i18n, styling, build tooling and generated clients.
  - Provider selection, retry policy, model policy, workflow orchestration and real LLM network calls.
  - Rewriting editorial prompt wording on the merits of the astrology content.
  - Physical retirement of `chart_json`, `natal_data` or existing public projection fields.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No public endpoint, OpenAPI response model or generated API client.
  - No database table, migration, repository write path or persistence backfill.
  - No provider call, live LLM execution or prompt prose rewrite.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend-domain natal runtime wiring contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add `llm_astrology_input_v1` only to the natal LLM execution path.
  - Reuse the CS-330 contract and CS-331 mapper instead of creating a parallel prompt input schema.
  - Keep `ExecutionContext` limited to control metadata, request metadata and renderer flags.
  - Keep public routes, OpenAPI exposure, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Keep historical chart carriers only as named transition compatibility surfaces.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the runtime cannot use CS-330 and CS-331 artifacts without changing prompt ownership or provider policy.
- Additional validation rules:
  - `NatalExecutionInput` must expose a typed or schema-owned `llm_astrology_input_v1` entry.
  - `AIEngineAdapter.generate_natal_interpretation` must propagate the field to runtime request construction.
  - `ExecutionContext` must not duplicate facts from `llm_astrology_input_v1`.
  - Prompt rendering must receive the contract through an explicit variable or payload key named `llm_astrology_input_v1`.
  - Tests must inspect the final rendered message or payload passed toward gateway/provider composition.
  - `chart_json` and `natal_data` must not be selected as prompt-visible substitutes when the rich contract is present.
  - `app.routes`, `app.openapi()`, `pytest` and `TestClient` evidence must prove public API neutrality.
  - An AST guard or targeted `rg` scan must classify remaining transition branches.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Runtime request construction, rendered payload, `app.routes`, `app.openapi()` and `TestClient` prove behavior. |
| Baseline Snapshot | yes | Before and after artifacts prove prompt input ownership and public surface neutrality. |
| Ownership Routing | yes | Facts, control metadata, renderer variables and transition carriers need distinct owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this natal runtime story. |
| Contract Shape | yes | `llm_astrology_input_v1` has exact transport, rendering and transition rules. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Chart carriers must not regain prompt-visible ownership when the rich contract is present. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `NatalExecutionInput` transports the rich contract. | Evidence profile: json_contract_shape; `pytest` unit runtime test path. |
| AC2 | The adapter propagates the rich contract. | Evidence profile: ast_architecture_guard; `python` AST guard checks adapter construction. |
| AC3 | `ExecutionContext` keeps fact ownership out. | Evidence profile: ast_architecture_guard; `python` AST guard checks context fields. |
| AC4 | The rendered prompt payload includes the rich contract. | Evidence profile: json_contract_shape; `pytest` unit runtime test path. |
| AC5 | `chart_json` is not selected when rich input exists. | Evidence profile: no_legacy_contract; `pytest` negative assertions; targeted `rg` scan. |
| AC6 | Remaining transition branches are bounded. | Evidence profile: targeted_forbidden_symbol_scan; `rg` classifies `chart_json`, `natal_data` and `fallback`. |
| AC7 | Public API surface stays unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`; `TestClient` smoke. |
| AC8 | No real LLM call is required. | Evidence profile: json_contract_shape; `pytest` uses gateway or provider doubles only. |
| AC9 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-332 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-330, CS-331, the transition report and current natal runtime files before editing. (AC: AC1, AC2, AC3)
- [ ] Task 2: Add `llm_astrology_input_v1` transport to `NatalExecutionInput`. (AC: AC1)
- [ ] Task 3: Build or pass `llm_astrology_input_v1` in the natal interpretation service before adapter execution. (AC: AC1, AC4)
- [ ] Task 4: Propagate the contract through `AIEngineAdapter.generate_natal_interpretation`. (AC: AC2)
- [ ] Task 5: Keep `ExecutionContext` limited to control metadata and renderer flags. (AC: AC3)
- [ ] Task 6: Expose `llm_astrology_input_v1` to prompt rendering through one explicit schema-owned key. (AC: AC4)
- [ ] Task 7: Add negative tests for chart carrier prompt substitution when rich input exists. (AC: AC5)
- [ ] Task 8: Classify remaining transition branches in tests or a bounded runtime register. (AC: AC6)
- [ ] Task 9: Add loaded-app guards proving no public API or OpenAPI exposure changed. (AC: AC7)
- [ ] Task 10: Use provider or gateway doubles so tests never call a real LLM. (AC: AC8)
- [ ] Task 11: Persist rendered-payload, transition-scan and validation evidence under the CS-332 evidence folder. (AC: AC9)

## Files to Inspect First

- `_story_briefs/cs-332-brancher-llm-astrology-input-dans-execution-natale.md` - source brief.
- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md` - upstream contract brief.
- `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md` - upstream mapper brief.
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md` - transition report.
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/03-legacy-transition.md` - transition register.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - natal runtime entry point.
- `backend/app/domain/llm/runtime/contracts.py` - current `NatalExecutionInput` and `ExecutionContext` owner.
- `backend/app/domain/llm/runtime/adapter.py` - runtime request adapter.
- `backend/app/domain/llm/runtime/gateway.py` - gateway payload assembly and validation.
- `backend/app/domain/llm/prompting/prompt_renderer.py` - actual renderer owner found in repository.
- `backend/app/domain/llm/runtime/prompt_renderer.py` - absent brief path; inspect only after implementation creates it by decision.
- `backend/app/domain/llm/runtime/models.py` - absent brief path; inspect only after implementation creates it by decision.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `backend/app/domain/llm/runtime/contracts.py` for `NatalExecutionInput` and `ExecutionContext`.
  - `backend/app/services/llm_generation/natal/interpretation_service.py` for natal execution input construction.
  - `backend/app/domain/llm/runtime/adapter.py` for request propagation into runtime context.
  - `backend/app/domain/llm/runtime/gateway.py` and `backend/app/domain/llm/prompting/prompt_renderer.py` for rendered payload visibility.
  - `app.routes`, `app.openapi()`, `TestClient`, AST guard and targeted `rg` scans for public API and transition neutrality.
- Secondary evidence:
  - `pytest -q backend/tests/unit/domain/llm/runtime/test_natal_llm_astrology_input.py`.
  - `pytest -q backend/tests/integration/llm/test_natal_llm_astrology_input_runtime.py`.
  - Targeted scans over runtime contracts, adapter, gateway, renderer and natal service.
- Static scans alone are not sufficient because:
  - request transport, rendered prompt payload and public-surface neutrality must be proven from runtime behavior.

## Contract Shape

- Contract type:
  - Backend-domain runtime wiring for schema-owned natal LLM prompt input.
- Fields:
  - `llm_astrology_input_v1`: exact schema-owned key carrying the rich contract from CS-330 and CS-331.
  - `facts`: transported inside the rich contract, not copied into `ExecutionContext`.
  - `signals`: transported inside the rich contract, not copied into prompt-side ad hoc fields.
  - `limits`: transported inside the rich contract and visible to renderer.
  - `evidence`: transported inside the rich contract as compact references.
  - `shaping`: transported inside the rich contract while plan/module controls stay runtime metadata.
  - `provenance`: transported inside the rich contract for version and hash proof.
  - `exclusions`: transported inside the rich contract for forbidden-source proof.
  - `chart_json`: transition carrier only, never prompt-visible substitute when the rich contract exists.
  - `natal_data`: transition carrier only, never fact owner for the rich contract.
- Required fields:
  - `llm_astrology_input_v1`
- Optional fields:
  - none for the new transport field; unavailable source data must be represented inside contract `limits`.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - emitted runtime and renderer key must be `llm_astrology_input_v1`.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose `llm_astrology_input_v1` from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-332-brancher-llm-astrology-input-dans-execution-natale.md`
  - `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
  - `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md`
  - targeted search output showing current `NatalExecutionInput`, `ExecutionContext`, `chart_json` and `natal_data` wiring.
- Comparison after implementation:
  - `_condamad/stories/CS-332-llm-astrology-input-v1-natal-runtime/evidence/rendered-payload.json`
  - `_condamad/stories/CS-332-llm-astrology-input-v1-natal-runtime/evidence/transition-scan.txt`
  - `_condamad/stories/CS-332-llm-astrology-input-v1-natal-runtime/evidence/public-surface-guard.txt`
  - `_condamad/stories/CS-332-llm-astrology-input-v1-natal-runtime/evidence/validation.txt`
- Expected invariant:
  - The only intended application delta is natal runtime transport and prompt visibility of `llm_astrology_input_v1`.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Natal execution transport | `backend/app/domain/llm/runtime/contracts.py` | frontend, API routers or provider code |
| Rich contract construction | CS-331 mapper owner | gateway ad hoc dict assembly |
| Runtime propagation | `backend/app/domain/llm/runtime/adapter.py` | duplicated service-only payloads |
| Prompt rendering variable | `gateway.py` plus `prompt_renderer.py` | hidden `ExecutionContext` fact copies |
| Control metadata | `ExecutionContext` | schema-owned astrology facts |
| Transition chart carriers | named compatibility branch | prompt-visible owner when rich input exists |
| Evidence artifacts | `_condamad/stories/CS-332-llm-astrology-input-v1-natal-runtime/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse the CS-330 `llm_astrology_input_v1` contract shape.
- Reuse the CS-331 mapper or canonical builder output for rich input construction.
- Reuse `NatalExecutionInput` and `ExecutionContext` in `runtime/contracts.py`; do not create parallel runtime model owners.
- Reuse `AIEngineAdapter.generate_natal_interpretation` and `LLMGateway` request construction paths.
- Reuse `PromptRenderer` under `backend/app/domain/llm/prompting/prompt_renderer.py`.
- Keep one schema-owned renderer key named `llm_astrology_input_v1`.
- Do not add external packages, public routes, frontend helpers, DB models, migrations, LLM providers or generated clients.

## No Legacy / Forbidden Paths

- No legacy prompt input path may become the owner for `llm_astrology_input_v1`.
- No compatibility route path may expose this internal runtime field.
- No fallback branch may promote chart carriers as canonical prompt input when the rich contract exists.
- Do not create aliases, shims, wrappers or parallel schemas for the same runtime input.
- Do not hide astrology facts inside `ExecutionContext.extra_context` as a second source of truth.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/**`
  - `backend/app/infra/db/**`
  - `backend/migrations/**`
  - generated OpenAPI clients
  - provider implementations as prompt input owners

## Reintroduction Guard

- Guard target:
  - `llm_astrology_input_v1` cannot be bypassed by `chart_json` or `natal_data` when present;
  - `ExecutionContext` cannot become a duplicate fact owner;
  - prompt renderer variables cannot depend on broad chart carriers for the new runtime path;
  - public API routes and OpenAPI schemas cannot expose this internal field;
  - transition compatibility branches must stay named and bounded.
- Guard mechanism:
  - focused unit tests for transport, renderer payload visibility and negative chart substitution;
  - integration test with gateway/provider doubles for final message composition;
  - architecture guard against reintroduced bypasses, plus AST guard or targeted `rg` scan for transition branch classification;
  - `app.routes`, `app.openapi()` and `TestClient` neutrality checks;
  - persisted rendered payload and validation transcript under the CS-332 evidence folder.
- Guard owner:
  - final `NatalExecutionInput` and adapter changes;
  - `backend/tests/unit/domain/llm/runtime/test_natal_llm_astrology_input.py`;
  - `backend/tests/integration/llm/test_natal_llm_astrology_input_runtime.py`;
  - `_condamad/stories/CS-332-llm-astrology-input-v1-natal-runtime/evidence/validation.txt`.
- Guard evidence:
  - `pytest -q backend/tests/unit/domain/llm/runtime/test_natal_llm_astrology_input.py`;
  - `pytest -q backend/tests/integration/llm/test_natal_llm_astrology_input_runtime.py`;
  - `python -c "from app.main import app; assert 'llm_astrology_input_v1' not in str(app.openapi())"`;
  - `python -c "from app.main import app; assert all('llm_astrology' not in getattr(r, 'path', '') for r in app.routes)"`;
  - `rg -n "llm_astrology_input_v1|NatalExecutionInput|ExecutionContext|PromptRenderer|chart_json|natal_data|fallback" app tests`.

## Regression Guardrails

Scope vector:

- backend-domain runtime update: yes;
- backend LLM natal service: yes;
- backend runtime contracts and adapter: yes;
- backend prompt rendering path: yes;
- public API route change: no;
- frontend implementation: no;
- DB, auth, i18n, style, build and migration: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | API v1 router ownership must remain outside the runtime wiring delta. | `app.routes`, OpenAPI and no `backend/app/api/**` changes. |
| Registry gap | No exact natal LLM input runtime guardrail exists in scoped resolver output. | Story-local `rg`; rendered payload tests. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is out of scope because this story wires a backend LLM runtime input.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Rendered payload | `_condamad/stories/CS-332-llm-astrology-input-v1-natal-runtime/evidence/rendered-payload.json` | Keep prompt-visible proof. |
| Transition scan | `_condamad/stories/CS-332-llm-astrology-input-v1-natal-runtime/evidence/transition-scan.txt` | Classify chart carrier uses. |
| Public surface guard | `_condamad/stories/CS-332-llm-astrology-input-v1-natal-runtime/evidence/public-surface-guard.txt` | Prove API neutrality. |
| Validation output | `_condamad/stories/CS-332-llm-astrology-input-v1-natal-runtime/evidence/validation.txt` | Keep lint and test transcript. |
| Review output | `_condamad/stories/CS-332-llm-astrology-input-v1-natal-runtime/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this backend runtime story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/llm/runtime/contracts.py` - add `llm_astrology_input_v1` to natal execution transport.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - build or pass the rich contract before adapter execution.
- `backend/app/domain/llm/runtime/adapter.py` - propagate the rich contract into runtime request construction.
- `backend/app/domain/llm/runtime/gateway.py` - expose the rich contract to prompt payload assembly.
- `backend/app/domain/llm/prompting/prompt_renderer.py` - support the schema-owned renderer key only if renderer changes are required.
- `_condamad/stories/CS-332-llm-astrology-input-v1-natal-runtime/evidence/rendered-payload.json` - prompt-visible proof.
- `_condamad/stories/CS-332-llm-astrology-input-v1-natal-runtime/evidence/transition-scan.txt` - transition classification.
- `_condamad/stories/CS-332-llm-astrology-input-v1-natal-runtime/evidence/public-surface-guard.txt` - route and OpenAPI proof.
- `_condamad/stories/CS-332-llm-astrology-input-v1-natal-runtime/evidence/validation.txt` - validation transcript.

Likely tests:

- `backend/tests/unit/domain/llm/runtime/test_natal_llm_astrology_input.py` - transport, context and payload tests.
- `backend/tests/integration/llm/test_natal_llm_astrology_input_runtime.py` - final message composition with doubles.
- `backend/tests/architecture/test_llm_astrology_input_runtime_boundary.py` - owner and public exposure guard when the existing pattern fits.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no public or internal API route is touched.
- `backend/app/infra/db/**` - out of scope; no persistence adapter is touched.
- `backend/migrations/**` - out of scope; no database migration is touched.
- provider implementation files - out of scope; no provider policy or network call behavior is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `pytest -q tests/unit/domain/llm/runtime/test_natal_llm_astrology_input.py`
- VC6: `pytest -q tests/integration/llm/test_natal_llm_astrology_input_runtime.py`
- VC7: `pytest -q tests/architecture/test_llm_astrology_input_runtime_boundary.py`
- VC8: `pytest -q tests --tb=short`
- VC9: `python -c "from app.main import app; assert 'llm_astrology_input_v1' not in str(app.openapi())"`
- VC10: `python -c "from app.main import app; assert all('llm_astrology' not in getattr(r, 'path', '') for r in app.routes)"`
- VC11: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-332-llm-astrology-input-v1-natal-runtime/evidence/validation.txt').exists()"`
- VC12: `rg -n "llm_astrology_input_v1|NatalExecutionInput|ExecutionContext|PromptRenderer|chart_json|natal_data|fallback" app tests`

Before VC3 through VC12, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The rich contract could be transported but not rendered into the final prompt payload.
- `ExecutionContext` could become a hidden duplicate owner of astrology facts.
- Historical chart carriers could remain prompt-visible when the rich contract is available.
- Prompt renderer changes could create an ad hoc variable path instead of the schema-owned key.
- Transition branch classification could mask unbounded prompt ownership drift.
- The story could drift into public API, frontend, persistence, provider, prompt prose or carrier retirement work.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior as canonical or prompt-visible ownership.
- Keep only named, bounded chart-carrier transition compatibility.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments and public or non-trivial docstrings in French for new or significantly modified backend files.
- Reuse the CS-330 contract and CS-331 mapper before creating adjacent helpers.
- Persist the required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-332-brancher-llm-astrology-input-dans-execution-natale.md`
- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md`
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/03-legacy-transition.md`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/domain/llm/runtime/contracts.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `_condamad/stories/regression-guardrails.md`
