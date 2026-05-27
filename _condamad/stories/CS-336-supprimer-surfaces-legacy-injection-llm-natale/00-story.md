# Story CS-336 supprimer-surfaces-legacy-injection-llm-natale: Remove Natal LLM Legacy Injection Surfaces
Status: done

## Trigger / Source

- Mode selected: Repo-informed story.
- Source brief: `_story_briefs/cs-336-supprimer-surfaces-legacy-injection-llm-natale.md`.
- Source report: `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`.
- Source architecture: `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/03-legacy-transition.md`.
- Upstream story: CS-334 migrates modern natal use cases toward `llm_astrology_input_v1`.
- Upstream story: CS-335 adds payload-boundary guards for modern natal prompt generation.
- Problem statement: the natal LLM path still exposes old prompt carriers that can compete with `llm_astrology_input_v1`.
- Source-alignment evidence: objective, ACs, tasks and validation preserve the brief stakes without touching frontend or public endpoints.

## Objective

Remove backend natal LLM injection surfaces that still let `chart_json`, `natal_data` or chart-derived evidence act as parallel prompt carriers.

## Target State

- `llm_astrology_input_v1` is the only active astrology payload carrier for modern natal LLM prompt generation.
- `chart_json` and `natal_data` are not accepted by the natal LLM path as prompt input owners.
- Chart-derived evidence is not rebuilt as a prompt payload carrier.
- Prompt placeholders and input schemas for modern natal use cases expose only the modern astrology input key.
- Transition branches and adapters that only maintain the double path are deleted.
- Remaining `chart_json` references are outside the natal LLM path or recorded as user-decision blockers.
- Tests prove absence of old carriers rather than compatibility with them.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-336-supprimer-surfaces-legacy-injection-llm-natale.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number CS-336.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - scoped guardrails resolved for backend prompt-generation removal.
- Evidence 4: `backend/app/domain/llm/runtime/contracts.py` - targeted search found `ExecutionContext` and `NatalExecutionInput` old carriers.
- Evidence 5: `backend/app/domain/llm/runtime/gateway.py` - targeted search found prompt payload reconstruction from old keys.
- Evidence 6: `backend/app/domain/llm/runtime/adapter.py` - targeted search found runtime transport of old carriers.
- Evidence 7: `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - targeted search found old prompt schema declarations.
- Evidence 8: `backend/app/domain/llm/configuration/assembly_resolver.py` - targeted search found preview variables for old prompt keys.
- Evidence 9: `backend/app/ops/llm/**` and `backend/tests/**` - targeted search found historical prompt seeds, fixtures and guards.
- Evidence 10: source-alignment review confirmed this story closes the withdrawal step after CS-330 to CS-335 prerequisites.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend natal LLM runtime contracts, gateway payload assembly, adapter handoff, prompt schemas and modern natal use-case declarations.
  - Deletion of old prompt carriers, wrappers, aliases, placeholder declarations and transition branches in the natal LLM path.
  - Classification of every remaining `chart_json`, `natal_data` and `evidence_catalog` occurrence touched by bounded scans.
  - Tests and evidence proving the old carriers cannot feed modern natal LLM prompt generation.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling, migrations, providers, retries and public endpoint behavior.
  - Fine editorial prompt copy changes.
  - Deletion of public non-LLM `chart_json` projection ownership.
  - Security policy, CI policy and astrologer profile changes.
- Explicit non-goals:
  - No frontend route, screen, client generation or UI validation.
  - No public API contract change.
  - No provider call in validation.
  - No replacement of deleted old carriers with aliases, wrappers or alternate old-key names.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: the story deletes historical prompt-carrier facades after the canonical LLM input path exists.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Remove only old natal LLM prompt-carrier surfaces superseded by `llm_astrology_input_v1`.
  - Keep public non-LLM `chart_json` projection ownership unchanged unless classification proves it only feeds the natal LLM path.
  - Keep public routes, OpenAPI paths, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Keep prompt editorial substance unchanged outside old carrier key deletion.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: an old surface has external or public non-LLM ownership that cannot be classified from repository evidence.
- Additional validation rules:
  - Runtime evidence must use `pytest` to inspect final natal LLM prompt payload or gateway-bound request objects.
  - Architecture evidence must include `AST guard` or targeted `rg` scans for old carrier imports, placeholders and branches.
  - Public boundary evidence must name `app.routes`, `app.openapi()` and `TestClient` to prove no endpoint contract delta.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, gateway payload inspection, `app.routes`, `app.openapi()` and `TestClient` prove runtime boundaries. |
| Baseline Snapshot | yes | Before and after artifacts prove the only allowed surface delta is old carrier extinction in natal LLM code. |
| Ownership Routing | yes | Canonical ownership prevents moving old payload logic into a different backend layer. |
| Allowlist Exception | no | No broad allowlist handling is authorized for this deletion story. |
| Contract Shape | yes | Modern natal LLM payload shape must expose `llm_astrology_input_v1` only for astrology input. |
| Batch Migration | yes | Several old fields, placeholders, branches and tests must be removed under one closure map. |
| Reintroduction Guard | yes | Old keys, aliases and transition branches must fail deterministic guards. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Natal runtime input excludes old carriers. | Evidence profile: field_removed; `pytest -q backend/tests/llm_orchestration/test_llm_legacy_extinction.py`. |
| AC2 | Gateway cannot rebuild from old carriers. | Evidence profile: no_legacy_contract; `pytest -q backend/tests/llm_orchestration/test_llm_legacy_extinction.py`. |
| AC3 | Modern natal schemas exclude old keys. | Evidence profile: field_removed; `pytest -q backend/tests/unit/test_natal_llm_use_case_input_contract.py`; `rg`. |
| AC4 | Transition branches are deleted. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/architecture/test_llm_legacy_extinction.py`. |
| AC5 | Remaining old-key hits are classified. | Evidence profile: targeted_forbidden_symbol_scan; `rg -n "chart_json|natal_data|evidence_catalog" backend/app backend/tests`. |
| AC6 | Modern prompt payload uses the canonical key. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`. |
| AC7 | Public API surface stays unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`; `TestClient`. |
| AC8 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |

## Implementation Tasks

- [ ] Task 1: Build the removal audit for old fields, placeholders, schemas, branches, adapters and tests. (AC: AC1, AC2, AC3, AC5)
- [ ] Task 2: Delete old carrier fields from natal LLM runtime input contracts after classification. (AC: AC1)
- [ ] Task 3: Delete gateway payload reconstruction from `chart_json`, `natal_data` and chart-derived evidence. (AC: AC2)
- [ ] Task 4: Delete modern natal prompt placeholders and input schema declarations for old carrier keys. (AC: AC3)
- [ ] Task 5: Delete transition branches and adapters whose only role is the old parallel carrier path. (AC: AC4)
- [ ] Task 6: Classify every remaining old-key occurrence as non-LLM owner, negative guard, historical docs or blocker. (AC: AC5)
- [ ] Task 7: Update tests so they assert absence of old carriers and continued canonical prompt payload use. (AC: AC1, AC2, AC3, AC6)
- [ ] Task 8: Persist before and after scans, payload snapshots, OpenAPI snapshots and validation output. (AC: AC7, AC8)
- [ ] Task 9: Run targeted validation and full backend validation from the activated venv. (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8)

## Files to Inspect First

- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/03-legacy-transition.md`
- `_story_briefs/cs-334-migrer-use-cases-natals-hors-chart-json-legacy.md`
- `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md`
- `backend/app/domain/llm/runtime/contracts.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/governance/data/prompt_governance_registry.json`
- `backend/app/domain/llm/governance/data/legacy_residual_registry.json`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- `backend/tests/unit/test_natal_llm_use_case_input_contract.py`
- `backend/tests/architecture/test_llm_legacy_extinction.py`

## Runtime Source of Truth

- Primary source of truth:
  - `pytest` tests that inspect final natal LLM payloads, `PromptRenderer` output and gateway-bound request objects.
  - `app.routes`, `app.openapi()` and `TestClient` proving endpoint neutrality.
- Secondary evidence:
  - `AST guard` checks and targeted `rg` scans for old carrier symbols in backend app and test paths.
- Static scans alone are not sufficient for this story because:
  - The risk is a live runtime branch silently feeding the prompt from an old carrier.

## Contract Shape

- Contract type:
  - Backend internal natal LLM prompt payload contract.
- Fields:
  - `llm_astrology_input_v1`: required object and only astrology input carrier for modern natal LLM prompt generation.
  - `locale`: preserved runtime control field.
  - `persona_name`: preserved persona control field for use cases that already require it.
- Required fields:
  - `llm_astrology_input_v1`
- Optional fields:
  - `locale`
  - `persona_name`
- Forbidden fields in modern natal prompt-carrier contracts:
  - `chart_json`
  - `natal_data`
  - `evidence_catalog` derived from `chart_json`
- Status codes:
  - none; this story does not add or change an API route.
- Serialization names:
  - `llm_astrology_input_v1` is emitted as `llm_astrology_input_v1`.
- Frontend type impact:
  - none; frontend generated clients and UI are out of scope.
- Generated contract impact:
  - `app.openapi()` must remain unchanged for public API paths.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/evidence/legacy-carrier-scan-before.txt`
  - `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/evidence/natal-llm-payload-before.json`
  - `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/evidence/openapi-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/evidence/legacy-carrier-scan-after.txt`
  - `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/evidence/natal-llm-payload-after.json`
  - `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/evidence/openapi-after.json`
- Expected invariant:
  - The only intended application surface delta is deletion of old natal LLM prompt-carrier surfaces.
  - `app.openapi()` before and after must be identical for public API paths.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Modern astrology LLM input | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | old prompt carrier fields |
| Natal LLM runtime input | `backend/app/domain/llm/runtime/contracts.py` | API router or frontend code |
| Prompt rendering | `backend/app/domain/llm/prompting/prompt_renderer.py` | natal service string assembly |
| Use-case input declarations | `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | provider code |
| Legacy extinction guards | `backend/tests/llm_orchestration` and `backend/tests/architecture` | manual-only review notes |

## Removal Classification Rules

- `canonical-active`: owned by `llm_astrology_input_v1` or by a public non-LLM projection explicitly outside this story.
- `external-active`: used by public docs, generated clients, external contracts or explicit product owner surfaces.
- `historical-facade`: delegates to or reconstructs the old prompt carrier path only to preserve transition behavior.
- `dead`: has zero active consumers after bounded app, tests, docs and generated-contract scans.
- `needs-user-decision`: unresolved external or public non-LLM ownership after the required scans.

## Removal Audit Format

The implementation must persist this table in
`_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/evidence/removal-audit.md`.

Allowed decisions are `keep`, `delete`, `replace-consumer` and `needs-user-decision`.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `chart_json` natal LLM carrier | field | historical-facade | natal LLM path | `llm_astrology_input_v1` | delete | `rg`, `pytest` | prompt owner drift |
| `natal_data` natal LLM carrier | field | historical-facade | natal LLM path | `llm_astrology_input_v1` | delete | `rg`, `pytest` | duplicate prompt input |
| chart-derived `evidence_catalog` prompt carrier | field | historical-facade | validation bridge | `evidence_refs` in modern contract | delete | `rg`, `pytest` | false grounding |

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Natal LLM astrology prompt input | `llm_astrology_input_v1` contract and mapper | `chart_json`, `natal_data`, old aliases |
| Prompt-visible evidence refs | modern evidence refs from CS-333 lineage | chart-derived `evidence_catalog` prompt carrier |
| Public non-LLM chart projection | existing chart projection owner | natal LLM runtime contracts or gateway fallback branches |

## Delete-Only Rule

- Items classified as `historical-facade` or `dead` must be deleted.
- Items classified as removable are deleted, not repointed.
- Do not repoint an old field to `llm_astrology_input_v1`.
- Do not preserve a wrapper, compatibility alias, shim module, old-key serializer, re-export or soft-disabled branch.
- Do not add `chart_json_v2`, `natal_data_v2`, `legacy_astrology_input` or wildcard prompt placeholders.

## External Usage Blocker

- Any `external-active` item must not be deleted.
- Any `external-active` item must block deletion until the user records an explicit decision.
- The required escalation is a user decision with the exact consumer evidence and deletion risk.
- The blocker must name the item, consumer, proof command, deletion risk and safest next action.
- No item may be classified as `needs-user-decision` without `rg`, `pytest` or generated-contract proof.

## Mandatory Reuse / DRY Constraints

- Reuse the CS-330 to CS-333 `llm_astrology_input_v1` contract, mapper, hash and evidence semantics.
- Reuse CS-334 use-case classification instead of creating a second classification model.
- Reuse CS-335 payload-boundary guards instead of duplicating prompt rendering logic in tests.
- Keep a single canonical astrology input key for modern natal LLM use cases.
- Do not duplicate old payload reconstruction under a renamed helper.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy prompt input path may remain active for modern natal LLM prompt generation.
- No compatibility prompt input path may remain active for modern natal LLM prompt generation.
- No fallback prompt input path may remain active for modern natal LLM prompt generation.
- Forbidden prompt-carrier keys: `chart_json`, `natal_data`, chart-derived `evidence_catalog`.
- Forbidden replacement names: `chart_json_v2`, `natal_data_v2`, `legacy_astrology_input`, wildcard astrology placeholders.
- Forbidden implementation surfaces: `frontend/src/**`, public API routers, DB migrations, provider policy and prompt editorial rewrite.

## Reintroduction Guard

- Add deterministic `pytest` tests that fail when old carrier fields are accepted by modern natal LLM runtime input.
- Add an architecture guard against reintroduction of old carrier fields, imports, aliases and prompt placeholders.
- Add or update an architecture guard that fails if the removed surface is reintroduced.
- Deterministic sources: generated OpenAPI paths and forbidden symbols or states.
- Add deterministic `AST guard` coverage that fails when gateway or adapters reconstruct prompt payloads from old carriers.
- Add targeted scans over `backend/app` and `backend/tests` for old carrier keys, aliases and transition branch labels.
- Required guard commands:
  - `pytest -q backend/tests/llm_orchestration/test_llm_legacy_extinction.py`
  - `pytest -q backend/tests/architecture/test_llm_legacy_extinction.py`
  - `rg -n "chart_json|natal_data|evidence_catalog|fallback|transition-condition" backend/app backend/tests`

## Generated Contract Check

- Generated contract check: applicable
- Required generated evidence:
  - `python -c "from app.main import app; assert app.routes; assert app.openapi()['paths']"`
  - `python -c "from app.main import app; assert 'chart_json' not in str(app.openapi())"`
  - `python -c "from app.main import app; assert 'natal_data' not in str(app.openapi())"`
- Expected result:
  - Public OpenAPI paths are unchanged by this backend internal removal.

## Regression Guardrails

Scope vector:

- Operation: remove.
- Domain: backend-domain.
- Paths: `backend/app/domain/llm`, `backend/app/services/llm_generation/natal`, `backend/tests`.
- Contracts: no-legacy, runtime-boundary, prompt-rendering, generated-contract.

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Active; public API router behavior must remain unchanged. | `python` checks `app.routes`; `app.openapi()`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Active; prompt-generation validation must target collected pytest files. | targeted `pytest`; bounded `rg`. |
| Registry gap | No exact natal LLM legacy-injection extinction guardrail was returned. | Story-local `pytest`, `AST guard` and `rg`. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS surface is touched.
- RG-052 frontend CSS namespace migration is out of scope because no frontend style migration is touched.
- RG-041 entitlement documentation is out of scope because this story changes internal natal LLM prompt carriers only.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Removal audit | `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/evidence/removal-audit.md` | Classify old carriers. |
| Before carrier scan | `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/evidence/legacy-carrier-scan-before.txt` | Capture old hits. |
| After carrier scan | `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/evidence/legacy-carrier-scan-after.txt` | Classify residual hits. |
| Before payload snapshot | `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/evidence/natal-llm-payload-before.json` | Capture payload baseline. |
| After payload snapshot | `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/evidence/natal-llm-payload-after.json` | Prove canonical payload. |
| Before OpenAPI snapshot | `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/evidence/openapi-before.json` | Prove public baseline. |
| After OpenAPI snapshot | `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/evidence/openapi-after.json` | Prove public neutrality. |
| Validation output | `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/evidence/validation.txt` | Store final command output. |
| Review output | `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no broad allowlist, wildcard bypass or residual compatibility register is authorized for this deletion story.

## Batch Migration Plan

- Batch migration plan: applicable

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| runtime-contracts | `chart_json`, `natal_data`, `evidence_catalog` | `llm_astrology_input_v1` | contracts, adapters | runtime tests | `pytest`, `AST guard` | public owner |
| gateway-payload | old payload rebuild branches | `llm_astrology_input_v1` | gateway | orchestration tests | `pytest`, `rg` | hidden consumer |
| prompt-config | old placeholders and schemas | `llm_astrology_input_v1` | registry, resolver | config tests | `pytest`, `rg` | unclassified use case |
| tests-fixtures | old compatibility fixtures | canonical payload fixtures | backend tests | guard tests | `pytest`, `rg` | external docs proof |

- Stop condition:
  - Every old carrier in the natal LLM path is deleted, classified outside scope or blocked by an explicit user-decision row.
  - Tests fail when a modern natal LLM prompt can be fed from the old carrier path.

## Expected Files to Modify

Likely files:

- `backend/app/domain/llm/runtime/contracts.py` - remove old carrier fields from modern natal LLM runtime input.
- `backend/app/domain/llm/runtime/gateway.py` - delete payload reconstruction from old carrier keys.
- `backend/app/domain/llm/runtime/adapter.py` - remove old carrier transport into gateway requests.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - delete old modern natal placeholders and schemas.
- `backend/app/domain/llm/configuration/assembly_resolver.py` - delete old preview variables for modern natal prompt assembly.
- `backend/app/domain/llm/governance/data/prompt_governance_registry.json` - delete old modern natal prompt placeholders.
- `backend/app/domain/llm/governance/data/legacy_residual_registry.json` - remove or update resolved old carrier entries.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - remove old carrier assembly in the natal LLM path.
- `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/evidence/**` - persist removal and validation evidence.

Likely tests:

- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- `backend/tests/unit/test_natal_llm_use_case_input_contract.py`
- `backend/tests/architecture/test_llm_legacy_extinction.py`
- `backend/tests/integration/test_llm_runtime_suppression.py`

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no public endpoint is changed.
- `backend/app/infra/**` - out of scope; no persistence or external adapter is touched.
- `backend/alembic/**` - out of scope; no migration is touched.
- `backend/app/domain/llm/runtime/supported_providers.py` - out of scope; provider policy is unchanged.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

Run all Python commands after activating the venv.

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `pytest -q tests/llm_orchestration/test_llm_legacy_extinction.py`
- VC6: `pytest -q tests/architecture/test_llm_legacy_extinction.py`
- VC7: `pytest -q tests/unit/test_natal_llm_use_case_input_contract.py`
- VC8: `pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- VC9: `pytest -q tests/integration/test_llm_runtime_suppression.py`
- VC10: `pytest -q tests --tb=short`
- VC11: `python -c "from app.main import app; assert app.routes; assert app.openapi()['paths']"`
- VC12: `python -c "from app.main import app; assert 'chart_json' not in str(app.openapi()) and 'natal_data' not in str(app.openapi())"`
- VC13: `rg -n "chart_json|natal_data|evidence_catalog|legacy|fallback|transition-condition" app tests`
- VC14: `rg -n "llm_astrology_input_v1" app tests`
- VC15: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/evidence/validation.txt').exists()"`

## Regression Risks

- A deleted field may be recreated as a renamed alias in gateway or adapter code.
- Residual `chart_json` usage may be valid for public non-LLM projection but misclassified as a natal LLM prompt carrier.
- Prompt fixtures may keep old placeholders and hide a production branch that still accepts old carriers.
- Over-broad scans may fail on negative guards or historical docs; residual occurrences must be classified instead of ignored.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\\.venv\\Scripts\\Activate.ps1` before every Python, Ruff or Pytest command.
- Work from `backend` for VC3 through VC14 after venv activation.
- Keep every residual old-key occurrence classified as non-LLM owner, negative guard, historical docs or blocker.
- Persist final evidence under `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/evidence`.

## References

- `_story_briefs/cs-336-supprimer-surfaces-legacy-injection-llm-natale.md`
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/03-legacy-transition.md`
- `_story_briefs/cs-334-migrer-use-cases-natals-hors-chart-json-legacy.md`
- `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md`
- `_condamad/stories/regression-guardrails.md`
