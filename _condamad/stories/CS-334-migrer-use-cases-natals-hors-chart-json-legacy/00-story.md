# Story CS-334 migrer-use-cases-natals-hors-chart-json-legacy: Migrate Natal Use Cases To llm_astrology_input_v1
Status: done

## Trigger / Source

- Mode selected: Repo-informed story.
- Source brief: `_story_briefs/cs-334-migrer-use-cases-natals-hors-chart-json-legacy.md`.
- Upstream story: CS-330 defines the `llm_astrology_input_v1` internal contract.
- Upstream story: CS-331 defines the mapper feeding `llm_astrology_input_v1`.
- Upstream story: CS-332 wires `llm_astrology_input_v1` into the natal runtime.
- Upstream story: CS-333 aligns hash, evidence and audit around `llm_astrology_input_v1`.
- Source report: `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`.
- Source architecture: `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/03-legacy-transition.md`.
- Problem statement: modern natal LLM use cases still declare `chart_json` as normal prompt input in registry and schema surfaces.
- Source-alignment evidence: this story preserves the brief objective, included scope, validation expectations and non-goals.

## Objective

Make `llm_astrology_input_v1` the declared and tested astrology input for modern natal LLM use cases.

## Target State

- Modern natal use cases declare `llm_astrology_input_v1` in their required prompt placeholders.
- Modern natal input schemas require `llm_astrology_input_v1` as the astrology payload key.
- Migrated prompt rendering receives `llm_astrology_input_v1` as the structured astrology input.
- Residual `chart_json` or `natal_data` branches are explicitly labeled as legacy transition surfaces.
- Configuration tests prevent a new modern natal use case from requiring `chart_json` as normal astrology input.
- Rendering tests prove the migrated use cases consume the modern payload in final prompt material.
- Editorial prompt wording remains unchanged outside the schema-owned input key migration.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-334-migrer-use-cases-natals-hors-chart-json-legacy.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number CS-334.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - registry consulted through the scoped guardrail resolver.
- Evidence 4: `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - targeted search found natal use cases requiring `chart_json`.
- Evidence 5: `backend/app/domain/llm/runtime/contracts.py` - targeted search found `ExecutionContext` and `NatalExecutionInput` still carry old keys.
- Evidence 6: `backend/app/domain/llm/prompting/prompt_renderer.py` - current renderer owner found under prompting, not runtime.
- Evidence 7: `backend/app/domain/llm/runtime/gateway.py` - targeted search found `chart_json` prompt and payload projection logic.
- Evidence 8: `backend/app/services/llm_generation/natal/interpretation_service.py` - natal service still builds `chart_json_dict`.
- Evidence 9: `backend/tests/llm_orchestration/test_prompt_renderer.py` - existing renderer tests are available for focused coverage.
- Evidence 10: `backend/tests/integration/test_llm_runtime_suppression.py` - existing runtime guard tests are available for transition checks.
- Evidence 11: source-alignment review confirmed the story keeps public endpoints, frontend, providers and prompt editorial content out of scope.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend LLM configuration for modern natal use cases.
  - Input schema declarations for migrated natal use cases.
  - Prompt placeholder declarations for migrated natal use cases.
  - Renderer and gateway tests proving `llm_astrology_input_v1` prompt consumption.
  - Classification of residual `chart_json` and `natal_data` branches as bounded legacy transition surfaces.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling, migrations, providers and public endpoints.
  - Editorial rewriting of prompt substance.
  - Physical deletion of every old carrier.
  - General LLM orchestration policy, retries, provider selection or workflow changes.
- Explicit non-goals:
  - No frontend route, screen, client generation or UI validation.
  - No public API contract change.
  - No new astrology calculation.
  - No provider call in validation.
  - No broad cleanup of unrelated fallback behavior.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend-domain LLM use-case configuration migration.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Update only modern natal LLM use-case declarations and tests for `llm_astrology_input_v1`.
  - Keep the CS-330 to CS-333 contract, mapper, runtime and hash owners as the canonical source.
  - Keep editorial prompt substance unchanged while replacing the normal astrology input key.
  - Keep residual old carriers labeled as `legacy transition` only.
  - Keep public routes, OpenAPI exposure, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: a natal branch cannot be classified as modern, legacy transition or product-owner decision.
- Additional validation rules:
  - Every migrated modern natal use case must require `llm_astrology_input_v1`.
  - No migrated modern natal use case may require `chart_json` as normal astrology input.
  - The input schema for each migrated modern natal use case must declare `llm_astrology_input_v1`.
  - Residual `chart_json` or `natal_data` references must be documented as legacy transition, negative guard or non-migrated branch.
  - Rendering tests must inspect final prompt material, not only registry objects.
  - Configuration tests must fail on any new modern natal use case requiring `chart_json`.
  - Prompt editorial content may change only by replacing the schema-owned input key.
  - `app.routes`, `app.openapi()`, `pytest` and `TestClient` evidence must prove no public API surface was added.
  - An AST guard or targeted `rg` scan must prove no parallel prompt input owner bypasses `llm_astrology_input_v1`.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Registry, renderer, gateway, `app.routes`, `app.openapi()` and `TestClient` prove runtime and public boundaries. |
| Baseline Snapshot | yes | Before and after artifacts prove use-case declarations, prompt keys and public API neutrality. |
| Ownership Routing | yes | Prompt input ownership must stay with the canonical LLM input contract and LLM configuration owners. |
| Allowlist Exception | no | No broad allowlist handling is authorized for this migration story. |
| Contract Shape | yes | Modern natal use cases must expose exact schema and placeholder keys. |
| Batch Migration | yes | Multiple natal use-case declarations are migrated under one finite closure map. |
| Reintroduction Guard | yes | New modern natal use cases must not reintroduce `chart_json` as normal astrology input. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Modern natal use cases require the new key. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_natal_llm_use_case_input_contract.py`. |
| AC2 | Modern natal schemas declare `llm_astrology_input_v1`. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_natal_llm_use_case_input_contract.py`. |
| AC3 | Modern natal placeholders exclude the old key. | Evidence profile: no_legacy_contract; `pytest -q backend/tests/unit/test_natal_llm_use_case_input_contract.py`; `rg`. |
| AC4 | Rendered prompts consume the modern payload. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_prompt_renderer.py`. |
| AC5 | Residual old carriers are classified. | Evidence profile: targeted_forbidden_symbol_scan; `pytest -q backend/tests/integration/test_llm_runtime_suppression.py`; `rg`. |
| AC6 | Prompt wording delta is limited to input keys. | Evidence profile: baseline_before_after_diff; `python` checks prompt baseline artifacts. |
| AC7 | Public API surface remains unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`; `TestClient` smoke test. |
| AC8 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence directory. |

## Implementation Tasks

- [ ] Task 1: Build the finite list of modern natal use cases and legacy transition branches. (AC: AC1, AC5)
- [ ] Task 2: Update modern natal placeholder declarations to require `llm_astrology_input_v1`. (AC: AC1, AC3)
- [ ] Task 3: Update modern natal input schemas to declare `llm_astrology_input_v1`. (AC: AC2)
- [ ] Task 4: Keep non-migrated branches explicitly labeled as legacy transition or product-owner decision. (AC: AC5)
- [ ] Task 5: Update renderer or gateway wiring only where required to consume the migrated schema-owned key. (AC: AC4)
- [ ] Task 6: Add configuration tests blocking modern natal use cases that require `chart_json`. (AC: AC1, AC2, AC3)
- [ ] Task 7: Add prompt rendering tests proving final prompt material uses `llm_astrology_input_v1`. (AC: AC4)
- [ ] Task 8: Persist before and after evidence for use-case declarations, prompt key deltas and public API neutrality. (AC: AC6, AC7, AC8)
- [ ] Task 9: Run targeted and full backend validation commands from the activated venv. (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8)

## Files to Inspect First

- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md`
- `_story_briefs/cs-332-brancher-llm-astrology-input-dans-execution-natale.md`
- `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md`
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/03-legacy-transition.md`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/governance/data/prompt_governance_registry.json`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/runtime/contracts.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/tests/llm_orchestration/test_prompt_renderer.py`
- `backend/tests/integration/test_llm_runtime_suppression.py`
- `backend/tests/llm_orchestration/test_assembly_resolution.py`

## Runtime Source of Truth

- Primary source of truth:
  - `canonical_use_case_registry.py`, prompt governance registry, `PromptRenderer`, `LLMGateway`, `app.routes`, `app.openapi()` and `TestClient`.
- Secondary evidence:
  - Targeted `rg` scans for `llm_astrology_input_v1`, `chart_json`, `natal_data`, `input_schema`, `required_prompt_placeholders` and `legacy transition`.
- Static scans alone are not sufficient for this story because:
  - The final rendered prompt must prove the migrated key is consumed at runtime.
  - Loaded `app.routes` and `app.openapi()` must prove no public API surface changed.

## Contract Shape

- Contract type:
  - Backend LLM use-case input schema and prompt placeholder declaration.
- Fields:
  - `llm_astrology_input_v1`: structured object owned by CS-330 to CS-333 contract lineage.
  - `locale`: optional locale string preserved from existing natal input schema.
  - `persona_name`: prompt variable preserved only for use cases already requiring persona context.
- Required fields:
  - `llm_astrology_input_v1`
- Optional fields:
  - `locale`
  - existing non-astrology prompt variables already required by the use case, such as `persona_name`.
- Status codes:
  - none; no public API route behavior is changed.
- Serialization names:
  - `llm_astrology_input_v1` is emitted as `llm_astrology_input_v1`.
- Frontend type impact:
  - none.
- Generated contract impact:
  - `app.openapi()` must remain unchanged for this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/evidence/natal-use-cases-before.json`
  - `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/evidence/prompt-key-scan-before.txt`
  - `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/evidence/openapi-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/evidence/natal-use-cases-after.json`
  - `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/evidence/prompt-key-scan-after.txt`
  - `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/evidence/openapi-after.json`
- Expected invariant:
  - The only intended LLM configuration delta is the migration of modern natal astrology input ownership to `llm_astrology_input_v1`.
  - `app.openapi()` before and after must be identical for public API paths.
  - Prompt text deltas must be limited to schema-owned input key replacement and transition labeling.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| LLM astrology input contract | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | prompt template or provider code |
| Modern natal use-case declaration | `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | frontend or API router |
| Placeholder family policy | `backend/app/domain/llm/governance/data/prompt_governance_registry.json` | ad hoc renderer branch |
| Prompt rendering | `backend/app/domain/llm/prompting/prompt_renderer.py` | natal service payload string assembly |
| Runtime execution transport | `backend/app/domain/llm/runtime/contracts.py` | `ExecutionContext` duplicate fact owner |
| Legacy transition classification | existing LLM runtime and configuration owners | undocumented compatibility branch |

## Mandatory Reuse / DRY Constraints

- Reuse the CS-330 `llm_astrology_input_v1` contract shape.
- Reuse the CS-331 mapper output and CS-332 runtime key.
- Reuse the CS-333 hash and evidence semantics.
- Keep one canonical placeholder key for the modern astrology input.
- Do not create a second schema name for the same payload.
- Do not duplicate use-case classification logic between registry and tests.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy route path may be added for this work.
- No compatibility route path may be added for this work.
- No fallback route path may be added for this work.
- No legacy prompt input path may become the owner for `llm_astrology_input_v1`.
- No compatibility schema may silently map a modern natal use case back to `chart_json`.
- No fallback prompt branch may select `chart_json` when `llm_astrology_input_v1` is present.
- Do not add `chart_json_v2`, `natal_data_v2`, alias keys, shim modules or wildcard placeholders.
- Do not move prompt rendering ownership into `interpretation_service.py`.

## Reintroduction Guard

- Forbidden normal input keys for modern natal use cases:
  - `chart_json`
  - `natal_data`
- Forbidden replacement patterns:
  - `chart_json_v2`
  - `natal_data_v2`
  - wildcard prompt placeholders for astrology input.
- Required guard commands:
  - `pytest -q backend/tests/unit/test_natal_llm_use_case_input_contract.py`
  - `pytest -q backend/tests/llm_orchestration/test_prompt_renderer.py`
  - `rg -n "llm_astrology_input_v1|chart_json|natal_data|input_schema|placeholder|legacy|fallback" app tests`
- Guard expectation:
  - Residual old-key occurrences are classified as legacy transition, negative guard or non-migrated branch.

## Regression Guardrails

Scope vector:

- Operation: update.
- Domain: backend-domain.
- Paths: `backend/app/domain/llm`, `backend/app/services/llm_generation/natal`, `backend/tests`.
- Contracts: `llm_astrology_input_v1`, prompt rendering, no-legacy, runtime boundary.

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `api-v1-routers` | Public API route ownership stays unchanged. | `python` checks `app.routes`; `app.openapi()`. |
| RG-022 `prompt-generation-validation` | Prompt-generation changes require renderer and backend tests. | targeted `pytest`; `rg` prompt-key scan. |
| Registry gap | No exact natal LLM input migration guardrail was returned by the resolver. | Story-local `pytest`, `rg` and source-alignment review. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS surface is touched.
- RG-052 frontend CSS namespace migration is out of scope because no frontend style migration is touched.
- RG-041 entitlement documentation is out of scope because this story changes LLM use-case input ownership only.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before use-case snapshot | `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/evidence/natal-use-cases-before.json` | Capture current natal declarations. |
| After use-case snapshot | `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/evidence/natal-use-cases-after.json` | Prove migrated declarations. |
| Before prompt key scan | `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/evidence/prompt-key-scan-before.txt` | Capture current prompt keys. |
| After prompt key scan | `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/evidence/prompt-key-scan-after.txt` | Prove old keys are classified. |
| Before OpenAPI snapshot | `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/evidence/openapi-before.json` | Prove public API baseline. |
| After OpenAPI snapshot | `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/evidence/openapi-after.json` | Prove public API neutrality. |
| Validation output | `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/evidence/validation.txt` | Keep final command output. |
| Review output | `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no broad allowlist, wildcard or bypass register is authorized for this migration story.

## Batch Migration Plan

- Batch migration plan: applicable

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| `natal_interpretation` | `chart_json` | `llm_astrology_input_v1` | registry, renderer | config, render | `rg`, `pytest` | unclassified branch |
| `natal_interpretation_short` | `chart_json` | `llm_astrology_input_v1` | registry, renderer | config, render | `rg`, `pytest` | unclassified branch |
| `natal_psy_profile` | `chart_json` | `llm_astrology_input_v1` | registry, renderer | config, render | `rg`, `pytest` | unclassified branch |
| `natal_shadow_integration` | `chart_json` | `llm_astrology_input_v1` | registry, renderer | config, render | `rg`, `pytest` | unclassified branch |
| `natal_leadership_workstyle` | `chart_json` | `llm_astrology_input_v1` | registry, renderer | config, render | `rg`, `pytest` | unclassified branch |
| `natal_creativity_joy` | `chart_json` | `llm_astrology_input_v1` | registry, renderer | config, render | `rg`, `pytest` | unclassified branch |
| `natal_relationship_style` | `chart_json` | `llm_astrology_input_v1` | registry, renderer | config, render | `rg`, `pytest` | unclassified branch |
| `natal_community_networks` | `chart_json` | `llm_astrology_input_v1` | registry, renderer | config, render | `rg`, `pytest` | unclassified branch |
| `natal_values_security` | `chart_json` | `llm_astrology_input_v1` | registry, renderer | config, render | `rg`, `pytest` | unclassified branch |
| `natal_evolution_path` | `chart_json` | `llm_astrology_input_v1` | registry, renderer | config, render | `rg`, `pytest` | unclassified branch |

- Batch classification rule:
  - A use case is modern when its normal astrology input is intended to feed the natal prompt from CS-330 to CS-333 lineage.
  - A use case stays legacy transition only with an explicit reason and bounded owner label.
  - A use case blocked by product semantics must be recorded as product-owner decision, not silently migrated.
- Stop condition:
  - Every listed modern natal use case either requires `llm_astrology_input_v1` or has a documented non-migration reason.
  - Tests fail when a new modern natal use case requires `chart_json` as the normal astrology input.

## Expected Files to Modify

Likely files:

- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - migrate modern natal use-case placeholders and schemas.
- `backend/app/domain/llm/governance/data/prompt_governance_registry.json` - authorize the modern placeholder family.
- `backend/app/domain/llm/configuration/assembly_resolver.py` - update preview/sample variables for the modern key.
- `backend/app/domain/llm/runtime/contracts.py` - align declared input transport with CS-332 ownership if still pending.
- `backend/app/domain/llm/runtime/gateway.py` - keep final prompt consumption on the modern key.
- `backend/app/domain/llm/prompting/prompt_renderer.py` - render the modern key through the existing renderer.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - pass modern input without making service the prompt owner.
- `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/evidence/**` - persist before and after evidence.

Likely tests:

- `backend/tests/unit/test_natal_llm_use_case_input_contract.py` - configuration guard for modern natal use cases.
- `backend/tests/llm_orchestration/test_prompt_renderer.py` - rendering coverage for the modern payload key.
- `backend/tests/llm_orchestration/test_assembly_resolution.py` - assembly placeholder and sample payload coverage.
- `backend/tests/integration/test_llm_runtime_suppression.py` - runtime transition guard coverage.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no public endpoint is changed.
- `backend/app/infra/**` - out of scope; no persistence or external adapter is touched.
- `backend/alembic/**` - out of scope; no migration is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

Run all Python commands after activating the venv.

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `pytest -q tests/unit/test_natal_llm_use_case_input_contract.py`
- VC6: `pytest -q tests/llm_orchestration/test_prompt_renderer.py`
- VC7: `pytest -q tests/llm_orchestration/test_assembly_resolution.py`
- VC8: `pytest -q tests/integration/test_llm_runtime_suppression.py`
- VC9: `pytest -q tests --tb=short`
- VC10: `python -c "from app.main import app; assert app.routes; assert app.openapi()['paths']"`
- VC11: `python -c "from app.main import app; assert 'llm_astrology_input_v1' not in str(app.openapi())"`
- VC12: `rg -n "llm_astrology_input_v1|chart_json|natal_data|input_schema|placeholder|legacy|fallback" app tests`
- VC13: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/evidence/validation.txt').exists()"`

## Regression Risks

- A modern natal use case may keep `chart_json` in schema while only adding the modern key.
- Prompt rendering may pass tests at object level without proving final prompt material.
- Residual old-key branches may stay undocumented and become the de facto normal path.
- A broad registry change may affect chat, guidance or horoscope use cases outside the natal scope.
- Public API output may drift if runtime transport changes leak into FastAPI contracts.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep prompt editorial substance unchanged outside schema-owned input key replacement.
- Keep every residual old-key occurrence classified as transition, negative guard or non-migrated branch.
- Run commands from PowerShell and activate `.\.venv\Scripts\Activate.ps1` before Python, Ruff or Pytest.
- Update README only if the execution mode changes.

## References

- `_story_briefs/cs-334-migrer-use-cases-natals-hors-chart-json-legacy.md`
- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md`
- `_story_briefs/cs-332-brancher-llm-astrology-input-dans-execution-natale.md`
- `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md`
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/03-legacy-transition.md`
- `_condamad/stories/regression-guardrails.md`
