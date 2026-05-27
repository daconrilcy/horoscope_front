# Story CS-337 supprimer-tests-mocks-legacy-injection-llm: Remove Legacy LLM Injection Tests And Mocks
Status: done

## Trigger / Source

- Mode selected: Repo-informed story.
- Source brief: `_story_briefs/cs-337-supprimer-tests-et-mocks-legacy-injection-llm.md`.
- Upstream story: CS-335 adds payload-boundary guards for modern natal prompt generation.
- Upstream story: CS-336 removes old natal LLM injection surfaces.
- Source report: `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`.
- Problem statement: legacy-oriented tests and mocks can force deleted LLM injection surfaces to survive in the test corpus.
- Source-alignment evidence: objective, ACs, tasks and validation preserve the brief stakes without changing product runtime behavior.

## Objective

Remove backend tests, fixtures, snapshots and mocks whose only value is preserving old natal LLM injection behavior after CS-336.

## Target State

- Backend tests validate `llm_astrology_input_v1` as the single modern natal LLM astrology input path.
- Tests no longer require a natal LLM payload based on `chart_json`, `natal_data` or chart-derived `evidence_catalog`.
- Mocks no longer recreate an old natal LLM prompt fallback, placeholder flow or adapter handoff.
- Useful assertions are migrated to the modern payload boundary instead of kept through old fixtures.
- Negative guards remain and prove old keys do not return in the natal LLM prompt path.
- The delivery evidence documents removed tests, adapted tests and accepted residual hits.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-337-supprimer-tests-et-mocks-legacy-injection-llm.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number CS-337.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - scoped guardrails resolved for backend tests and prompt-generation cleanup.
- Evidence 4: `_story_briefs/cs-336-supprimer-surfaces-legacy-injection-llm-natale.md` - prerequisite removal scope read.
- Evidence 5: `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md` - modern guard scope read.
- Evidence 6: targeted `rg` found old-key tests in `backend/app/tests/unit/legacy_services`.
- Evidence 7: targeted `rg` found old-key prompt tests in `backend/tests/llm_orchestration`.
- Evidence 8: targeted `rg` found old-key admin prompt catalog tests in `backend/tests/integration`.
- Evidence 9: source-alignment review confirms this story removes test pressure to preserve deleted old natal LLM injection behavior.

## Domain Boundary

- Domain: backend-tests
- In scope:
  - Backend tests, fixtures, factories, snapshots and mocks tied to natal LLM injection behavior.
  - Classification of old-key hits in backend tests using `chart_json`, `natal_data`, `evidence_catalog`, fallback or transition markers.
  - Deletion of tests whose only purpose is old natal LLM compatibility.
  - Adaptation of useful assertions to `llm_astrology_input_v1`.
  - Preservation of negative guards proving old keys stay absent from the modern natal LLM path.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling, migrations, CI policy, providers and prompt editorial rewriting.
  - Deleting valid non-LLM tests for public `chart_json` projections or unrelated fallback behavior.
  - Changing product runtime code beyond minimal test-owned helpers required by classification.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or UI validation.
  - No public API contract change.
  - No skip or xfail to hide an obsolete test.
  - No recreation of old natal LLM payloads through renamed fixtures or mocks.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: the story deletes historical test facades after the canonical natal LLM input path exists.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Remove only backend test corpus surfaces that preserve old natal LLM injection behavior.
  - Keep negative guards proving old keys remain absent from the modern natal LLM path.
  - Keep unrelated non-LLM `chart_json` tests unchanged after classification.
  - Keep public routes, OpenAPI paths, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: a test hit cannot be classified as old LLM compatibility, modern behavior, negative guard or non-LLM ownership.
- Additional validation rules:
  - Runtime evidence must use `pytest` to inspect modern natal LLM prompt payload tests.
  - Architecture evidence must include `AST guard` or targeted `rg` scans for old mocks, fixtures and placeholders.
  - Public boundary evidence must name `app.routes`, `app.openapi()` and `TestClient` to prove no endpoint contract delta.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, modern prompt tests, `app.routes`, `app.openapi()` and `TestClient` prove behavior and public neutrality. |
| Baseline Snapshot | yes | Before and after scan artifacts prove the only allowed surface delta is backend test cleanup. |
| Ownership Routing | yes | Test ownership prevents moving old payload mocks into production or unrelated test helpers. |
| Allowlist Exception | no | No broad allowlist handling is authorized for this cleanup. |
| Contract Shape | yes | Modern test payload shape must assert `llm_astrology_input_v1` instead of old keys. |
| Batch Migration | yes | Several test files, fixtures and mocks must be classified and changed together. |
| Reintroduction Guard | yes | Old LLM injection tests and mocks must not return under renamed helpers. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Every old-key test hit is classified. | Evidence profile: targeted_forbidden_symbol_scan; `rg -n "chart_json|natal_data|evidence_catalog" tests app/tests`. |
| AC2 | Old LLM compatibility tests are deleted. | Evidence profile: route_removed; `pytest -q tests/llm_orchestration tests/integration tests/unit`. |
| AC3 | Old fallback mocks are absent. | Evidence profile: no_legacy_contract; `rg -n "fallback|legacy|PromptRenderer|LLMGateway|NatalExecutionInput" tests app/tests`. |
| AC4 | Modern payload tests cover `llm_astrology_input_v1`. | Evidence profile: json_contract_shape; `pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py`. |
| AC5 | Negative old-key guards remain. | Evidence profile: no_legacy_contract; `pytest -q tests/architecture/test_llm_legacy_extinction.py`. |
| AC6 | No opportunistic skip remains. | Evidence profile: targeted_forbidden_symbol_scan; `rg -n "skip|xfail" tests app/tests`. |
| AC7 | Public API surface stays unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`; `TestClient`. |
| AC8 | Removal evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |

## Implementation Tasks

- [ ] Task 1: Build the test removal audit from targeted scans over backend test roots. (AC: AC1)
- [ ] Task 2: Classify each hit as old LLM compatibility, modern behavior, negative guard or non-LLM ownership. (AC: AC1)
- [ ] Task 3: Delete tests, snapshots and fixtures that only preserve old natal LLM injection behavior. (AC: AC2)
- [ ] Task 4: Delete mocks that recreate old prompt fallback, placeholder or adapter behavior. (AC: AC3)
- [ ] Task 5: Adapt useful assertions to `llm_astrology_input_v1` using existing modern payload helpers. (AC: AC4)
- [ ] Task 6: Preserve or strengthen negative guards that reject `chart_json` and `natal_data` in the natal LLM path. (AC: AC5)
- [ ] Task 7: Prove no skip or xfail was introduced to hide obsolete test failures. (AC: AC6)
- [ ] Task 8: Persist before and after scans, removal audit, OpenAPI snapshots and validation output. (AC: AC7, AC8)
- [ ] Task 9: Run targeted and full backend validation from the activated venv. (AC: AC2, AC3, AC4, AC5, AC6, AC7, AC8)

## Files to Inspect First

- `_story_briefs/cs-337-supprimer-tests-et-mocks-legacy-injection-llm.md`
- `_story_briefs/cs-336-supprimer-surfaces-legacy-injection-llm-natale.md`
- `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md`
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`
- `backend/app/tests/unit/legacy_services/test_natal_interpretation_service_v2_refacto.py`
- `backend/app/tests/unit/legacy_services/legacy_natal_interpretation_service.py`
- `backend/app/tests/integration/test_admin_llm_natal_prompts.py`
- `backend/tests/llm_orchestration/test_assembly_resolution.py`
- `backend/tests/llm_orchestration/test_llm_execution_request.py`
- `backend/tests/llm_orchestration/test_llm_gateway_compose.py`
- `backend/tests/llm_orchestration/test_placeholder_validation.py`
- `backend/tests/integration/test_llm_golden_regression.py`
- `backend/tests/integration/test_admin_llm_catalog.py`
- `backend/tests/integration/test_admin_llm_sample_payloads.py`
- `backend/tests/evaluation/conftest.py`
- `backend/tests/evaluation/test_prompt_resolution.py`

## Runtime Source of Truth

- Primary source of truth:
  - `pytest` tests for the modern natal LLM payload, negative old-key guards and backend test suite collection.
  - `app.routes`, `app.openapi()` and `TestClient` proving endpoint neutrality.
- Secondary evidence:
  - `AST guard` checks and targeted `rg` scans for old-key fixtures, mocks, placeholders and skip markers.
- Static scans alone are not sufficient for this story because:
  - The risk is a collected test or mock still requiring deleted old natal LLM injection behavior.

## Contract Shape

- Contract type:
  - Backend test corpus contract for modern natal LLM injection.
- Fields:
  - `llm_astrology_input_v1`: required modern astrology input asserted by retained or adapted natal LLM tests.
- Required fields:
  - `llm_astrology_input_v1`
- Optional fields:
  - none for old-carrier compatibility tests.
- Forbidden fields in modern natal LLM test payload requirements:
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
  - `_condamad/stories/CS-337-supprimer-tests-mocks-legacy-injection-llm/evidence/test-legacy-scan-before.txt`
  - `_condamad/stories/CS-337-supprimer-tests-mocks-legacy-injection-llm/evidence/openapi-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-337-supprimer-tests-mocks-legacy-injection-llm/evidence/test-legacy-scan-after.txt`
  - `_condamad/stories/CS-337-supprimer-tests-mocks-legacy-injection-llm/evidence/openapi-after.json`
- Expected invariant:
  - The only intended application surface delta is deletion or adaptation of backend tests, fixtures, snapshots and mocks.
  - `app.openapi()` before and after must be identical for public API paths.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Modern natal LLM payload tests | `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` | old legacy-service tests |
| Negative old-key guards | `backend/tests/architecture/test_llm_legacy_extinction.py` | skipped tests or manual notes |
| Test cleanup audit | `_condamad/stories/CS-337-supprimer-tests-mocks-legacy-injection-llm/evidence/test-cleanup-audit.md` | production code |
| Non-LLM chart projection tests | existing domain-specific chart tests | natal LLM prompt tests |

## Removal Classification Rules

- `canonical-active`: test validates `llm_astrology_input_v1` or a valid non-LLM chart projection owner.
- `external-active`: test documents public docs, generated clients or explicit product evidence outside this story.
- `historical-facade`: test, fixture or mock exists only to preserve old natal LLM injection compatibility.
- `dead`: test, fixture, snapshot or mock has no useful modern assertion after CS-336.
- `needs-user-decision`: classification remains ambiguous after required scans and local test inspection.

## Removal Audit Format

The implementation must persist this table in
`_condamad/stories/CS-337-supprimer-tests-mocks-legacy-injection-llm/evidence/test-cleanup-audit.md`.

Allowed decisions are `keep`, `delete`, `replace-consumer` and `needs-user-decision`.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| old natal LLM `chart_json` tests | test | historical-facade | backend tests | `llm_astrology_input_v1` tests | delete | `rg`, `pytest` | test forces old payload |
| old natal LLM `natal_data` fixtures | fixture | historical-facade | backend tests | modern payload fixture | delete | `rg`, `pytest` | mock recreates old path |
| old prompt fallback mocks | mock | historical-facade | backend tests | negative guard or modern mock | delete | `rg`, `pytest` | false compatibility |

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Modern natal LLM test payload | `llm_astrology_input_v1` boundary tests | `chart_json`, `natal_data`, chart-derived evidence fixtures |
| Prompt renderer behavior tests | modern renderer tests using canonical payloads | old placeholder-only prompt tests |
| LLM gateway behavior tests | local gateway tests without provider calls | mocks that rebuild old fallback input |
| Negative extinction coverage | architecture or orchestration guards | deleted compatibility tests |

## Delete-Only Rule

- Items classified as `historical-facade` or `dead` must be deleted.
- Removable old tests must be deleted, not repointed.
- Removable old tests must not be converted into skipped, xfailed or renamed compatibility coverage.
- Do not repoint an old fixture to `llm_astrology_input_v1` while keeping old field names.
- Do not preserve a wrapper, compatibility alias, shim fixture, old-key serializer, re-export or soft-disabled test branch.
- Do not add `chart_json_v2`, `natal_data_v2`, `legacy_astrology_input` or wildcard prompt placeholders in tests.

## External Usage Blocker

- Any `external-active` item must not be deleted.
- Any `external-active` item must block deletion until the user records an explicit decision.
- The required escalation is a user decision with the exact consumer evidence and deletion risk.
- The blocker must name the item, consumer, proof command, deletion risk and safest next action.
- No item may be classified as `needs-user-decision` without `rg`, `pytest` or generated-contract proof.

## Mandatory Reuse / DRY Constraints

- Reuse CS-335 modern boundary tests and helpers instead of creating duplicate prompt rendering assertions.
- Reuse CS-336 extinction guards instead of preserving old compatibility tests.
- Reuse existing backend pytest fixtures only when they express modern `llm_astrology_input_v1` behavior.
- Keep a single canonical modern natal LLM input fixture shape.
- Do not duplicate old payload reconstruction under a renamed helper.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy test may require old natal LLM prompt input behavior after cleanup.
- No compatibility test may preserve old natal LLM `chart_json` or `natal_data` payload requirements.
- No fallback mock may rebuild old natal LLM prompt input for a modern use case.
- Forbidden test payload keys for modern natal LLM compatibility: `chart_json`, `natal_data`, chart-derived `evidence_catalog`.
- Forbidden replacement names: `chart_json_v2`, `natal_data_v2`, `legacy_astrology_input`, wildcard astrology placeholders.
- Forbidden implementation surfaces: `frontend/src/**`, public API routers, DB migrations, provider policy and prompt editorial rewrite.

## Reintroduction Guard

- Add or keep deterministic `pytest` tests that fail when old keys return as modern natal LLM prompt inputs.
- Add an architecture guard against reintroduction of old-key fixtures, mocks, snapshots and placeholder tests.
- Add or update an architecture guard that fails if the removed test surface is reintroduced.
- Deterministic sources: collected pytest files, `AST guard`, generated OpenAPI paths and forbidden symbols or states.
- Required guard commands:
  - `pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
  - `pytest -q tests/architecture/test_llm_legacy_extinction.py`
  - `rg -n "chart_json|natal_data|evidence_catalog|legacy|fallback|transition|skip|xfail" tests app/tests`

## Generated Contract Check

- Generated contract check: applicable
- Required generated evidence:
  - `python -c "from app.main import app; assert app.routes; assert app.openapi()['paths']"`
  - `python -c "from app.main import app; assert 'chart_json' not in str(app.openapi())"`
  - `python -c "from app.main import app; assert 'natal_data' not in str(app.openapi())"`
- Expected result:
  - Public OpenAPI paths are unchanged by this backend test cleanup.

## Regression Guardrails

Scope vector:

- Operation: remove.
- Domain: backend-tests.
- Paths: `backend/tests`, `backend/app/tests`, `backend/tests/llm_orchestration`, `backend/tests/integration`.
- Contracts: no-legacy, pytest, prompt-generation, `llm_astrology_input_v1`.

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Active only for proving public API neutrality. | `python` checks `app.routes`; `app.openapi()`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Active; prompt-generation tests must point to collected pytest files. | targeted `pytest`; bounded `rg`. |
| Registry gap | No exact legacy-test cleanup guardrail was returned. | Story-local `pytest`, `AST guard` and `rg`. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS surface is touched.
- RG-052 frontend CSS namespace migration is out of scope because no frontend style migration is touched.
- RG-041 entitlement documentation is out of scope because this story changes backend tests only.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Test cleanup audit | `_condamad/stories/CS-337-supprimer-tests-mocks-legacy-injection-llm/evidence/test-cleanup-audit.md` | Classify test hits. |
| Before test scan | `_condamad/stories/CS-337-supprimer-tests-mocks-legacy-injection-llm/evidence/test-legacy-scan-before.txt` | Capture old hits. |
| After test scan | `_condamad/stories/CS-337-supprimer-tests-mocks-legacy-injection-llm/evidence/test-legacy-scan-after.txt` | Classify residual hits. |
| Before OpenAPI snapshot | `_condamad/stories/CS-337-supprimer-tests-mocks-legacy-injection-llm/evidence/openapi-before.json` | Prove public baseline. |
| After OpenAPI snapshot | `_condamad/stories/CS-337-supprimer-tests-mocks-legacy-injection-llm/evidence/openapi-after.json` | Prove public neutrality. |
| Validation output | `_condamad/stories/CS-337-supprimer-tests-mocks-legacy-injection-llm/evidence/validation.txt` | Store final command output. |
| Review output | `_condamad/stories/CS-337-supprimer-tests-mocks-legacy-injection-llm/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no broad allowlist, wildcard bypass or residual compatibility register is authorized for this deletion story.

## Batch Migration Plan

- Batch migration plan: applicable

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| legacy-service-tests | old natal LLM service tests | modern boundary tests | backend tests | pytest | `pytest`, `rg` | unclear owner |
| prompt-fixtures | old prompt payload fixtures | `llm_astrology_input_v1` fixtures | backend tests | pytest | `pytest`, `rg` | non-LLM owner |
| gateway-mocks | old fallback mocks | local modern gateway doubles | backend tests | pytest | `pytest`, `AST guard` | hidden consumer |
| snapshots | old expected payload snapshots | modern payload snapshots | backend tests | pytest | `pytest`, `rg` | product ambiguity |

- Stop condition:
  - Every old-key test hit is deleted, adapted to the modern path, classified as a negative guard, classified outside scope or blocked by decision.
  - The backend suite passes without skip or xfail introduced to preserve obsolete old LLM injection behavior.

## Expected Files to Modify

Likely files:

- `backend/app/tests/unit/legacy_services/test_natal_interpretation_service_v2_refacto.py` - apply audited deletion or consumer adaptation.
- `backend/app/tests/unit/legacy_services/legacy_natal_interpretation_service.py` - delete old fixture helper usage.
- `backend/app/tests/integration/test_admin_llm_natal_prompts.py` - replace old placeholder assertions with modern payload assertions.
- `backend/tests/llm_orchestration/test_assembly_resolution.py` - adapt old placeholder validation coverage.
- `backend/tests/llm_orchestration/test_llm_execution_request.py` - adapt old execution context payload assertions.
- `backend/tests/llm_orchestration/test_llm_gateway_compose.py` - adapt old gateway compose payload assertions.
- `backend/tests/llm_orchestration/test_placeholder_validation.py` - delete old placeholder compatibility requirement.
- `backend/tests/integration/test_llm_golden_regression.py` - adapt old golden context projection tests.
- `backend/tests/evaluation/conftest.py` - delete old natal fixture payloads used only by LLM compatibility tests.
- `_condamad/stories/CS-337-supprimer-tests-mocks-legacy-injection-llm/evidence/**` - persist cleanup and validation evidence.

Likely tests:

- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- `backend/tests/architecture/test_llm_legacy_extinction.py`
- `backend/tests/llm_orchestration/test_assembly_resolution.py`
- `backend/tests/llm_orchestration/test_llm_execution_request.py`
- `backend/tests/llm_orchestration/test_llm_gateway_compose.py`
- `backend/tests/integration/test_llm_golden_regression.py`

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
- VC5: `pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- VC6: `pytest -q tests/architecture/test_llm_legacy_extinction.py`
- VC7: `pytest -q tests/llm_orchestration/test_assembly_resolution.py`
- VC8: `pytest -q tests/llm_orchestration/test_llm_execution_request.py`
- VC9: `pytest -q tests/llm_orchestration/test_llm_gateway_compose.py`
- VC10: `pytest -q tests/integration/test_llm_golden_regression.py`
- VC11: `pytest -q tests --tb=short`
- VC12: `python -c "from app.main import app; assert app.routes; assert app.openapi()['paths']"`
- VC13: `python -c "from app.main import app; assert 'chart_json' not in str(app.openapi()) and 'natal_data' not in str(app.openapi())"`
- VC14: `rg -n "chart_json|natal_data|evidence_catalog|legacy|fallback|transition|skip|xfail" tests app/tests`
- VC15: `rg -n "llm_astrology_input_v1" tests app/tests`
- VC16: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-337-supprimer-tests-mocks-legacy-injection-llm/evidence/validation.txt').exists()"`

## Regression Risks

- Useful modern prompt coverage could be deleted instead of adapted.
- Valid non-LLM `chart_json` tests could be misclassified as old natal LLM compatibility.
- Mock removal could hide a provider-isolation gap unless modern gateway doubles remain explicit.
- Residual scans may include negative guards or unrelated domains; every accepted residual hit must be classified.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\\.venv\\Scripts\\Activate.ps1` before every Python, Ruff or Pytest command.
- Work from `backend` for VC3 through VC15 after venv activation.
- Keep every residual old-key test occurrence classified as non-LLM owner, negative guard, historical docs or blocker.
- Persist final evidence under `_condamad/stories/CS-337-supprimer-tests-mocks-legacy-injection-llm/evidence`.

## References

- `_story_briefs/cs-337-supprimer-tests-et-mocks-legacy-injection-llm.md`
- `_story_briefs/cs-336-supprimer-surfaces-legacy-injection-llm-natale.md`
- `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md`
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`
- `_condamad/stories/regression-guardrails.md`
