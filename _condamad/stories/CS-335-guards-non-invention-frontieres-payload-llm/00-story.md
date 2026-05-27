# Story CS-335 guards-non-invention-frontieres-payload-llm: Add LLM Payload Boundary Non-Invention Guards
Status: ready-to-dev

## Trigger / Source

- Mode: Repo-informed story.
- Source brief: `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md`.
- Upstream story: CS-330 defines the `llm_astrology_input_v1` internal contract.
- Upstream story: CS-331 maps rich astrology data into `llm_astrology_input_v1`.
- Upstream story: CS-332 wires `llm_astrology_input_v1` into natal runtime.
- Upstream story: CS-333 aligns hash, evidence and audit around `llm_astrology_input_v1`.
- Upstream story: CS-334 migrates modern natal use cases away from `chart_json` as prompt owner.
- Source report: `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`.
- Problem statement: the modern natal LLM path needs deterministic guards proving prompt-visible data richness and payload boundary roles.
- Source-alignment evidence: the objective, ACs, tasks and validation plan map to the brief stakes without changing prompts, providers or frontend.

## Objective

Add backend tests and static guards proving that modern natal LLM prompt payloads preserve rich astrology data, expose missing-data limits and keep
runtime-only, validation-only and audit-only surfaces out of prompt-visible material.

## Target State

- Modern natal prompt composition has deterministic tests for the final prompt payload or the object immediately before gateway/provider handoff.
- The prompt-visible payload contains `facts`, `signals`, `limits`, `evidence`, `shaping` and `provenance` when the representative profile supports them.
- A missing-data natal profile makes limits visible to prompt composition.
- Runtime raw surfaces stay out of the prompt payload.
- `chart_json` and `natal_data` cannot silently become the prompt owner when `llm_astrology_input_v1` is available.
- Validation evidence remains local and does not call an external LLM provider.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number CS-335.
- Evidence 3: `backend/app/domain/llm/runtime/gateway.py` - targeted search found prompt composition and gateway payload boundaries.
- Evidence 4: `backend/app/domain/llm/runtime/contracts.py` - targeted search found `ExecutionContext` and `NatalExecutionInput`.
- Evidence 5: `backend/app/services/llm_generation/natal/interpretation_service.py` - targeted search found natal runtime assembly.
- Evidence 6: `backend/tests/llm_orchestration/**` - targeted search found existing gateway and renderer tests.
- Evidence 7: `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py` - targeted search found facts owner.
- Evidence 8: `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` - targeted search found narrative signal owner.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - targeted ID lookup consulted scoped guardrails RG-002, RG-022 and RG-041.
- Evidence 10: guardrail classification keeps RG-022 active and records RG-002 plus RG-041 as non-applicable to this payload-boundary scope.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend tests for modern natal LLM prompt payload boundaries.
  - Static guards against raw runtime payload injection and unclassified prompt owner drift.
  - Evidence artifacts for final prompt payload shape, boundary roles and no-provider-call validation.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling, migrations, prompt copy rewrite and real LLM response quality.
  - Physical deletion of `chart_json`, `natal_data` or historical surfaces.
  - Security, CI, provider retry policy and endpoint contract changes.
- Explicit non-goals:
  - No frontend route, screen, generated client, CSS, browser workflow or UI validation.
  - No new astrology calculations, no astrologer profile changes and no editorial prompt rewrite.
  - No external LLM provider call.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits backend-domain guards for prompt payload role boundaries.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only tests, static guards and persisted evidence for modern natal LLM payload boundaries.
  - Keep runtime behavior unchanged unless a test harness needs a deterministic seam already present in the code.
  - Preserve existing public API and frontend behavior.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: final prompt payload cannot be observed without changing the production gateway contract.
- Additional validation rules:
  - Runtime evidence must name `pytest`, gateway message composition or `PromptRenderer`.
  - Architecture evidence must include `AST guard` or targeted `rg` scans for forbidden raw surfaces.
  - No AC may rely on a real provider call.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Gateway message composition, `PromptRenderer` and `pytest` prove the payload handed to the LLM path. |
| Baseline Snapshot | yes | Before and after artifacts prove the only allowed surface delta is added guards and evidence. |
| Ownership Routing | yes | Canonical owners prevent prompt payload tests from moving logic into gateway or providers. |
| Allowlist Exception | no | No broad allowlist handling is authorized for this guard story. |
| Contract Shape | yes | Prompt-visible role blocks and forbidden raw surfaces need exact JSON role rules. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Raw runtime and legacy owner paths must stay blocked for modern natal prompt payloads. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Payload role classes are tested. | Evidence profile: json_contract_shape; `pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py`. |
| AC2 | The representative prompt contains rich blocks. | Evidence profile: json_contract_shape; `pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py`. |
| AC3 | Missing-data limits are prompt-visible. | Evidence profile: json_contract_shape; `pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py`. |
| AC4 | Raw surfaces stay out. | Evidence profile: targeted_forbidden_symbol_scan; `pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py`. |
| AC5 | No `chart_json` prompt owner. | Evidence profile: no_legacy_contract; `tests/llm_orchestration/test_llm_astrology_input_boundaries.py`. |
| AC6 | Duplication guard exists. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_llm_astrology_input_v1.py`. |
| AC7 | Tests avoid external LLM provider calls. | Evidence profile: ast_architecture_guard; `pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py`. |
| AC8 | Guard evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect the final prompt payload boundary in gateway, renderer and natal service tests. (AC: AC1, AC2, AC4, AC5)
- [ ] Task 2: Add boundary-role tests for prompt-visible, runtime-only, validation-only and audit-only data. (AC: AC1)
- [ ] Task 3: Add representative natal payload tests for `facts`, `signals`, `limits`, `evidence`, `shaping` and `provenance`. (AC: AC2)
- [ ] Task 4: Add missing-data profile coverage proving limits reach prompt composition. (AC: AC3)
- [ ] Task 5: Add negative guards for `ChartObjectRuntimeData`, `CalculationGraph`, `chart_json` and `natal_data`. (AC: AC4, AC5)
- [ ] Task 6: Add a non-duplication guard between facts and signals in the canonical contract or mapper tests. (AC: AC6)
- [ ] Task 7: Add a provider isolation guard using mocks or local doubles for the LLM gateway path. (AC: AC7)
- [ ] Task 8: Persist before and after evidence artifacts for payload shape, scans and validation output. (AC: AC8)

## Files to Inspect First

- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - canonical contract and mapper owner from CS-330 and CS-331.
- `backend/app/domain/llm/runtime/contracts.py` - `ExecutionContext`, `NatalExecutionInput` and payload boundary types.
- `backend/app/domain/llm/runtime/adapter.py` - natal adapter handoff into gateway execution.
- `backend/app/domain/llm/runtime/gateway.py` - message construction, validation payload and provider handoff.
- `backend/app/domain/llm/prompting/prompt_renderer.py` - placeholder rendering and prompt-visible payload behavior.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - natal runtime assembly before gateway call.
- `backend/tests/llm_orchestration/test_assembly_resolution.py` - existing gateway composition coverage.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` - expected canonical contract or mapper tests.
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` - expected new boundary guard tests.

## Runtime Source of Truth

- Primary source of truth:
  - `pytest` tests that inspect final gateway messages, `PromptRenderer` output or the object immediately before provider handoff.
- Secondary evidence:
  - `AST guard` checks and targeted `rg` scans for raw runtime and legacy prompt owner symbols.
- Static scans alone are not sufficient for this story because:
  - The risk is a payload boundary regression in the rendered or gateway-bound prompt material.

## Contract Shape

- Contract type:
  - Backend prompt payload boundary for modern natal LLM use cases.
- Fields:
  - `facts`: prompt-visible structured facts from `structured_facts_v1`.
  - `signals`: prompt-visible pre-narrative signals from `AINarrativeInputContract`.
  - `limits`: prompt-visible missing-data and uncertainty markers.
  - `evidence`: prompt-visible refs selected for grounding or validation handoff.
  - `shaping`: prompt-visible editorial depth and plan/module controls, not facts.
  - `provenance`: prompt-visible or audit-linked versions and hashes required by CS-333.
- Required fields:
  - `facts`, `signals`, `limits`, `evidence`, `shaping`, `provenance`.
- Optional fields:
  - none for the representative modern natal profile.
- Forbidden prompt payload values:
  - `ChartObjectRuntimeData`, `CalculationGraph`, raw `chart_json` and raw `natal_data`.
- Status codes:
  - none; this story does not add or change an API route.
- Serialization names:
  - `llm_astrology_input_v1` is emitted as `llm_astrology_input_v1`.
- Frontend type impact:
  - none; frontend generated clients and UI are out of scope.
- Generated contract impact:
  - `app.openapi()` must remain unchanged for this backend internal guard story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-335-guards-non-invention-frontieres-payload-llm/evidence/payload-boundary-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-335-guards-non-invention-frontieres-payload-llm/evidence/payload-boundary-after.json`
- Expected invariant:
  - The only intended application surface delta is added tests, static guards and persisted evidence for the modern natal LLM payload boundary.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| LLM astrology input contract | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | gateway, provider or frontend code |
| Natal prompt boundary tests | `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` | production provider code |
| Facts and signals duplication guard | `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` | prompt template text |
| Static payload scans | `backend/tests/architecture/**` or focused backend test module | CI-only script outside tests |

## Mandatory Reuse / DRY Constraints

- Reuse the CS-330 `llm_astrology_input_v1` contract and CS-331 mapper fixtures.
- Reuse existing gateway, renderer and natal orchestration test helpers.
- Reuse existing `structured_facts_v1`, `AINarrativeInputContract`, `evidence_refs` and hash helpers.
- Do not duplicate prompt composition logic inside tests; inspect outputs through public testable boundaries.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy prompt input path may become the owner for `llm_astrology_input_v1`.
- No compatibility prompt branch may select `chart_json` when `llm_astrology_input_v1` is present.
- No fallback prompt branch may select `natal_data` when `llm_astrology_input_v1` is present.
- No raw runtime object may be serialized as prompt payload material.
- Forbidden prompt payload symbols: `ChartObjectRuntimeData`, `CalculationGraph`, `chart_json`, `natal_data`.
- Forbidden implementation surfaces: `frontend/src/**`, public API routers, DB migrations, provider policy and prompt editorial copy.

## Reintroduction Guard

- Add deterministic tests that fail when raw runtime symbols appear in modern natal prompt payload material.
- Add deterministic tests that fail when `chart_json` or `natal_data` becomes the prompt owner for migrated natal use cases.
- Add targeted scans over `backend/app` and `backend/tests` for boundary markers and forbidden prompt-owner paths.
- Required guard command:
  - `rg -n "prompt-visible|runtime-only|validation-only|audit-only|llm_astrology_input_v1|chart_json|natal_data|ChartObjectRuntimeData|CalculationGraph" app tests`

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-022 `align-prompt-generation-story-validation-paths` | Active; prompt-generation tests must point to collected pytest files. | Targeted `pytest`; validation plan paths. |
| Registry gap | No exact `llm_astrology_input_v1` prompt-boundary guardrail exists in resolver output. | Story-local `pytest`, `AST guard` and `rg`. |
| Non-applicable RG-002 | API router architecture is outside this backend domain guard scope. | Scope excludes API routers and public endpoint changes. |
| Non-applicable RG-041 | Documentation entitlement is outside this backend payload boundary scope. | Scope vector excludes docs entitlement. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before snapshot | `_condamad/stories/CS-335-guards-non-invention-frontieres-payload-llm/evidence/payload-boundary-before.json` | Before payload boundary. |
| After snapshot | `_condamad/stories/CS-335-guards-non-invention-frontieres-payload-llm/evidence/payload-boundary-after.json` | After payload boundary. |
| Validation output | `_condamad/stories/CS-335-guards-non-invention-frontieres-payload-llm/evidence/validation.txt` | Store final validation commands and results. |
| Guard scan output | `_condamad/stories/CS-335-guards-non-invention-frontieres-payload-llm/evidence/payload-boundary-scan.txt` | Store targeted prompt boundary scans. |
| Review output | `_condamad/stories/CS-335-guards-non-invention-frontieres-payload-llm/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no broad allowlist handling is authorized for this single backend guard story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` - final prompt payload role and no-provider-call guards.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` - non-duplication and contract-level boundary guards.
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` - optional AST guard for forbidden raw prompt surfaces.
- `_condamad/stories/CS-335-guards-non-invention-frontieres-payload-llm/evidence/payload-boundary-before.json` - before evidence.
- `_condamad/stories/CS-335-guards-non-invention-frontieres-payload-llm/evidence/payload-boundary-after.json` - after evidence.
- `_condamad/stories/CS-335-guards-non-invention-frontieres-payload-llm/evidence/validation.txt` - validation evidence.

Likely tests:

- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/infra/**` - out of scope; no persistence adapter or migration is touched.
- `backend/app/api/**` - out of scope; no public endpoint contract is touched.
- `backend/app/domain/llm/runtime/supported_providers.py` - out of scope; provider policy is unchanged.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- VC2: `pytest -q tests/unit/domain/astrology/test_llm_astrology_input_v1.py`
- VC3: `pytest -q tests/architecture/test_llm_astrology_input_payload_boundaries.py`
- VC4: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-335-guards-non-invention-frontieres-payload-llm/evidence/payload-boundary-after.json').exists()"`
- VC5: `python -c "from app.main import app; assert 'llm_astrology_input_v1' not in str(app.openapi())"`
- VC6: `ruff format .`
- VC7: `ruff check .`
- VC8: `pytest -q tests --tb=short`
- VC9: `rg -n "prompt-visible|runtime-only|validation-only|audit-only|llm_astrology_input_v1|chart_json|natal_data|ChartObjectRuntimeData|CalculationGraph" app tests`

## Regression Risks

- Tests may inspect only builders and miss the final gateway-bound prompt material.
- Over-broad scans could fail on intentional historical tests rather than modern natal payload boundaries.
- Provider mocking could hide message composition drift unless final message content is asserted before provider handoff.
- Non-duplication checks could become brittle; they must target gross duplicated sections, not legitimate shared identifiers.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\\.venv\\Scripts\\Activate.ps1` before every Python, pytest or ruff command.
- Work from `backend` for VC1, VC2, VC3, VC5, VC6, VC7, VC8 and VC9.
- Keep evidence artifacts under `_condamad/stories/CS-335-guards-non-invention-frontieres-payload-llm/evidence`.

## References

- `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md`
- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md`
- `_story_briefs/cs-332-brancher-llm-astrology-input-dans-execution-natale.md`
- `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md`
- `_story_briefs/cs-334-migrer-use-cases-natals-hors-chart-json-legacy.md`
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`
