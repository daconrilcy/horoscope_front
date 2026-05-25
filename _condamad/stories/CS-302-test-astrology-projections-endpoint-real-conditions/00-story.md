# Story CS-302 test-astrology-projections-endpoint-real-conditions: Test Astrology Projections Endpoint In Real Conditions
Status: ready-to-review

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-302-test-astrology-projections-endpoint-real-conditions.md`.
- Selected mode: Repo-informed story with Fast Story Writer Mode.
- Problem statement: `POST /v1/astrology/projections` is delivered, but B2C frontend readiness needs realistic HTTP proof.
- Source stakes: prove supported projections, entitlement behavior, degraded birth data, errors, persistence, and OpenAPI before frontend wiring.
- Source-alignment evidence: PASS; objective, ACs, tasks, evidence, and guardrails preserve the brief without adding UI or builders.

## Objective

Prove `POST /v1/astrology/projections` under representative B2C HTTP conditions with `TestClient`, OpenAPI checks, persisted artifacts,
and backend validation evidence usable before frontend integration.

## Target State

- The existing public endpoint is exercised with realistic authenticated B2C HTTP scenarios.
- `structured_facts_v1`, `beginner_summary_v1`, and `client_interpretation_projection_v1` each have response-shape proof.
- Free, basic, and premium plans have explicit runtime evidence, including controlled entitlement denials.
- Invalid payloads and missing chart sources return stable public error envelopes.
- Missing optional birth data such as birth time is represented in payload evidence as degraded or approximate data.
- Optional persistence is proven only through the existing projection persistence path.
- `app.openapi()` and `app.routes` prove the canonical public route without introducing alternate public projection paths.
- Story evidence contains OpenAPI, JSON response, validation, and limitation artifacts for review handoff.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-302-test-astrology-projections-endpoint-real-conditions.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-302` after `CS-301`.
- Evidence 3: `_condamad/reports/CS-256-CS-291-delivery-report.md` - delivery report confirms CS-291 endpoint runtime exists.
- Evidence 4: `backend/app/api/v1/routers/public/projections.py` - canonical route and HTTP status mapping inspected.
- Evidence 5: `backend/app/services/projections/projection_endpoint_service.py` - orchestration, entitlement, builders, and persistence inspected.
- Evidence 6: `backend/app/services/api_contracts/public/projections.py` - request and response contracts inspected.
- Evidence 7: `backend/tests/api/test_projection_endpoint.py` - current API tests use service doubles for route-level proof.
- Evidence 8: `backend/tests/api/test_projection_authorization.py` - current authorization tests cover controlled denial envelopes.
- Evidence 9: `backend/tests/api/test_projection_persistence_endpoint.py` - current persistence API test covers persisted response metadata.
- Evidence 10: `backend/tests/api/test_projection_openapi.py` - current OpenAPI test covers route presence and internal-surface denial.
- Evidence 11: `_condamad/stories/regression-guardrails.md` - scoped resolver output selected local backend API guardrails only.
- Source-alignment evidence: PASS; this story strengthens runtime proof and does not alter frontend, builders, or entitlement policy.

## Domain Boundary

- Domain: backend-api
- In scope:
  - Runtime API tests for `POST /v1/astrology/projections` using `TestClient`.
  - Realistic B2C payload scenarios for the three supported public projection types.
  - Plan matrix evidence for `free`, `basic`, and `premium`.
  - Controlled error envelope tests for entitlement, payload, and chart-source failures.
  - Optional persistence proof through the existing persistence service.
  - OpenAPI, `app.routes`, JSON response, validation, and limitation evidence artifacts.
- Out of scope:
  - Frontend UI, generated clients, DB schema changes, auth redesign, i18n, styling, build tooling, migrations, and payment flows.
  - New projection builders, new entitlement policy, admin endpoints, B2B endpoints, prompt/provider work, and replay/audit admin features.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS, or browser validation.
  - No builder rewrite, no entitlement-model change, no persistence schema migration, and no new public endpoint.
  - No replay feature, no admin audit surface, and no provider or LLM integration change.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend API runtime proof contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add or update backend tests and CONDAMAD evidence for the existing endpoint only.
  - Keep `POST /v1/astrology/projections` request and response semantics unchanged unless a failing test proves an existing defect.
  - Reuse CS-291 route, schema, service, builder, entitlement, and persistence owners.
  - Keep frontend, DB migration, auth model, entitlement model, builder, prompt, provider, style, and build surfaces unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: realistic runtime scenarios expose a product-policy gap not covered by the current B2C projection contract.
- Additional validation rules:
  - Runtime evidence must include `pytest` with `TestClient` for realistic HTTP scenarios.
  - Runtime evidence must include `app.routes` and `app.openapi()` checks for the canonical route.
  - Evidence must include JSON response artifacts for at least one successful projection and one controlled error.
  - Evidence must document remaining limits before frontend wiring instead of silently passing weak fixtures.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, `TestClient`, `app.routes`, and `app.openapi()` prove endpoint behavior. |
| Baseline Snapshot | yes | OpenAPI and JSON artifacts prove the validated public API surface and payload shapes. |
| Ownership Routing | yes | Tests and evidence must reuse the existing router, schemas, service, builders, entitlement, and persistence owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this runtime proof story. |
| Contract Shape | yes | The evidence must name method, path, status codes, JSON fields, projection types, and plan matrix. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Alternate projection paths and internal projection identifiers must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `structured_facts_v1` has HTTP proof. | Evidence profile: json_contract_shape; `pytest -q backend/tests/api/test_projection_real_conditions.py`. |
| AC2 | `beginner_summary_v1` has HTTP proof. | Evidence profile: json_contract_shape; `pytest -q backend/tests/api/test_projection_real_conditions.py`. |
| AC3 | `client_interpretation_projection_v1` has HTTP proof. | Evidence profile: json_contract_shape; `pytest -q backend/tests/api/test_projection_real_conditions.py`. |
| AC4 | The B2C plan matrix is proven. | Evidence profile: api_error_shape_contract; `pytest -q backend/tests/api/test_projection_authorization.py`. |
| AC5 | Entitlement refusal is stable. | Evidence profile: api_error_shape_contract; `TestClient`; `pytest -q backend/tests/api/test_projection_authorization.py`. |
| AC6 | Invalid payload errors are explicit. | Evidence profile: api_error_shape_contract; `pytest -q backend/tests/api/test_projection_real_conditions.py`. |
| AC7 | Missing chart data returns a public error. | Evidence profile: api_error_shape_contract; `pytest -q backend/tests/api/test_projection_real_conditions.py`. |
| AC8 | Missing birth time is visible. | Evidence profile: json_contract_shape; `TestClient`; `pytest -q backend/tests/api/test_projection_real_conditions.py`. |
| AC9 | Optional persistence is proven. | Evidence profile: json_contract_shape; `pytest -q backend/tests/api/test_projection_persistence_endpoint.py`. |
| AC10 | OpenAPI exposes only the public endpoint. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`. |
| AC11 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-302 evidence paths. |

## Implementation Tasks

- [x] Task 1: Inspect the CS-291 route, service, schemas, and existing projection API tests before editing. (AC: AC1, AC2, AC3, AC9)
- [x] Task 2: Add realistic `TestClient` scenarios for all three public projection types. (AC: AC1, AC2, AC3)
- [x] Task 3: Add plan matrix and entitlement denial proof using current resolver or service doubles. (AC: AC4, AC5)
- [x] Task 4: Add invalid payload and no-chart response tests with the shared public error envelope. (AC: AC6, AC7)
- [x] Task 5: Add degraded birth-input evidence for missing optional birth time. (AC: AC8)
- [x] Task 6: Preserve optional persistence proof through the existing persistence endpoint test path. (AC: AC9)
- [x] Task 7: Capture OpenAPI and runtime route evidence from `app.openapi()` and `app.routes`. (AC: AC10)
- [x] Task 8: Persist JSON response samples, OpenAPI snapshot, validation output, and limits notes under the CS-302 evidence folder. (AC: AC11)

## Files to Inspect First

- `_story_briefs/cs-302-test-astrology-projections-endpoint-real-conditions.md` - source brief.
- `_condamad/reports/CS-256-CS-291-delivery-report.md` - delivery status for CS-291 and projection builders.
- `backend/app/api/v1/routers/public/projections.py` - canonical route and status-code mapping.
- `backend/app/services/projections/projection_endpoint_service.py` - runtime orchestration owner.
- `backend/app/services/api_contracts/public/projections.py` - public request and response schema owner.
- `backend/tests/api/test_projection_endpoint.py` - current route-level success coverage.
- `backend/tests/api/test_projection_authorization.py` - current denial coverage.
- `backend/tests/api/test_projection_persistence_endpoint.py` - current persistence response coverage.
- `backend/tests/api/test_projection_openapi.py` - current OpenAPI exposure coverage.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `pytest`, `TestClient`, `app.routes`, and `app.openapi()`.
  - Current CS-291 route, schema, service, builders, entitlement resolver, and persistence service.
- Secondary evidence:
  - Targeted `rg` scans for alternate route paths and internal projection identifiers.
  - Persisted OpenAPI and JSON response artifacts under the CS-302 evidence folder.
- Static scans alone are not sufficient because:
  - Realistic endpoint behavior, entitlement denial, degraded birth data, and persistence status require loaded runtime checks.

## Contract Shape

- Contract type:
  - Existing API route runtime proof and evidence contract.
- Method and path:
  - `POST /v1/astrology/projections`.
- Fields:
  - `chart_id`: optional existing chart identifier owned by the authenticated user.
  - `birth_input`: optional birth payload used when a new chart is calculated.
  - `projection_type`: public projection identifier.
  - `projection_version`: public projection contract version.
  - `persist`: optional boolean for existing persistence behavior.
  - `projection_hash`: stable response hash.
  - `payload`: projection-specific JSON object.
  - `metadata`: public metadata containing source, plan, request id, and optional persisted identity.
- Required fields:
  - `projection_type`
  - `projection_version`
- Conditional fields:
  - exactly one accepted chart source is used from `chart_id` or `birth_input`.
- Optional fields:
  - `chart_id`
  - `birth_input`
  - `persist`
- Status codes:
  - `200` for successful non-persisted projection response.
  - `201` for successful persisted projection response.
  - `400` for invalid chart source selection.
  - `401` for unauthenticated access.
  - `403` for unauthorized projection or plan denial.
  - `404` for unknown or inaccessible `chart_id`.
  - `409` for unavailable calculation, builder, or persistence dependency.
  - `422` for invalid payload shape or unsupported version.
- Serialization names:
  - JSON keys are emitted as `chart_id`, `projection_type`, `projection_version`, `persisted`, `projection_hash`, `payload`, and `metadata`.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must keep the existing public endpoint and must not expose internal projection contracts.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/openapi-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/openapi-after.json`
  - `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/response-samples.json`
  - `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/validation.txt`
- Expected invariant:
  - The intended delta is stronger runtime proof and persisted evidence for the existing public endpoint.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Projection route | `backend/app/api/v1/routers/public/projections.py` | New public, admin, internal, or B2B router. |
| API schemas | `backend/app/services/api_contracts/public/projections.py` | Test-local contract dictionaries. |
| Endpoint orchestration | `backend/app/services/projections/projection_endpoint_service.py` | Route-local business logic. |
| Public builders | CS-285 to CS-287 builder modules | Test-only builders replacing canonical owners. |
| Entitlement policy | Existing entitlement resolver and CS-283 policy | Client payload fields or frontend assumptions. |
| Persistence | Existing projection persistence service | Test-only write path or route-local SQL. |
| Runtime evidence | `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/` | Application source folders. |

## Mandatory Reuse / DRY Constraints

- Reuse CS-291 endpoint owners instead of adding a second route, schema, or service path.
- Reuse current projection builders instead of copying projection payload construction into API tests.
- Reuse existing entitlement and persistence abstractions; test doubles may isolate HTTP cases but must preserve owner boundaries.
- Reuse existing projection API test files when that keeps coverage clear, or add one focused real-conditions API test file.
- Do not add external packages, frontend helpers, generated clients, migrations, prompt/provider code, or duplicate builders.

## No Legacy / Forbidden Paths

- No legacy route path may be added for projection validation.
- No compatibility route path may be added for projection validation.
- No fallback route path may be added for projection validation.
- Do not create aliases, shims, wrappers, or parallel routes for the endpoint.
- Do not expose internal projection identifiers or raw runtime payloads to B2C clients.
- Forbidden route paths:
  - `/v1/projections`
  - `/v1/astrology/projection`
  - `/v1/astrology/projections/internal`
  - `/v1/b2b/astrology/projections`
  - `/v1/admin/astrology/projections`
- Forbidden surfaces:
  - `frontend/src/**`
  - generated OpenAPI clients
  - DB migrations
  - prompt and provider files
  - new public projection builders

## Reintroduction Guard

- Guard exact forbidden route paths:
  - `/v1/projections`
  - `/v1/astrology/projection`
  - `/v1/astrology/projections/internal`
  - `/v1/b2b/astrology/projections`
  - `/v1/admin/astrology/projections`
- Guard exact forbidden projection identifiers in public OpenAPI:
  - `expert_technical_projection_v1`
  - `astrology_full_data_v1`
  - `admin_chart_diagnostics_v1`
  - `provider_response`
- Required deterministic guard:
  - `python -c "from app.main import app; assert '/v1/astrology/projections' in app.openapi()['paths']"`
  - `python -c "from app.main import app; assert '/v1/astrology/projections' in {getattr(r, 'path', '') for r in app.routes}"`
  - `rg -n "/v1/projections|/v1/astrology/projection|/v1/b2b/astrology/projections|/v1/admin/astrology/projections" app tests`

## Regression Guardrails

Scope vector:

- backend-api runtime proof: yes;
- existing public projection endpoint: yes;
- OpenAPI public contract: yes;
- B2C authorization and entitlement checks: yes;
- optional projection persistence through existing service: yes;
- frontend, DB migration, i18n, style, build, and B2B implementation: no.

Selected guardrails:

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | API tests must not move business logic into route files. | router diff review; targeted `pytest`. |
| RG-003 `converge-api-v1-route-architecture` | Route inventory must preserve the canonical public path. | `app.routes`; `app.openapi()`. |
| RG-007 `converge-admin-llm-observability-router` | Internal/admin projection surfaces stay out of public OpenAPI. | OpenAPI scan; `TestClient`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Validation paths must point to collected backend pytest files. | Explicit `pytest` commands. |
| Registry gap | No exact `/v1/astrology/projections` guardrail exists in resolver output. | Story-local route and OpenAPI guards. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 frontend CSS namespace migration is out of scope because no styling or build output is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Guardrail resolver output | `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/guardrails.txt` | Preserve scoped guardrail selection. |
| OpenAPI before | `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/openapi-before.json` | Capture baseline OpenAPI. |
| OpenAPI after snapshot | `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/openapi-after.json` | Capture public OpenAPI after test proof. |
| JSON response samples | `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/response-samples.json` | Keep success and error samples. |
| Validation output | `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/validation.txt` | Preserve lint, tests, route checks, and scans. |
| Frontend readiness limits | `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/frontend-readiness-limits.md` | Document residual limits. |
| Review output | `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this runtime proof story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/tests/api/test_projection_real_conditions.py` - add realistic B2C HTTP scenarios for projection response proof.
- `backend/tests/api/test_projection_endpoint.py` - extend route-level source tests only when clearer than a new focused file.
- `backend/tests/api/test_projection_authorization.py` - extend entitlement plan and denial tests.
- `backend/tests/api/test_projection_persistence_endpoint.py` - preserve or extend optional persistence proof.
- `backend/tests/api/test_projection_openapi.py` - preserve or extend OpenAPI public exposure proof.
- `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/guardrails.txt` - scoped guardrail selection.
- `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/openapi-before.json` - OpenAPI baseline.
- `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/openapi-after.json` - OpenAPI after proof.
- `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/response-samples.json` - JSON samples.
- `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/frontend-readiness-limits.md` - residual limits.

Likely tests:

- `backend/tests/api/test_projection_real_conditions.py`
- `backend/tests/api/test_projection_endpoint.py`
- `backend/tests/api/test_projection_authorization.py`
- `backend/tests/api/test_projection_persistence_endpoint.py`
- `backend/tests/api/test_projection_openapi.py`

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/domain/astrology/interpretation/**` - out of scope; delivered builders are reused.
- `backend/app/services/entitlement/**` - out of scope; entitlement model is not redesigned.
- `backend/alembic/**` - out of scope; no schema migration is authorized.
- `backend/app/api/v1/routers/admin/**` - out of scope; no admin route is touched.
- prompt and provider files - out of scope; no LLM generation behavior changes.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff check .`
- VC4: `python -B -m pytest -q tests\api\test_projection_real_conditions.py --tb=short`
- VC5: `python -B -m pytest -q tests\api\test_projection_endpoint.py --tb=short`
- VC6: `python -B -m pytest -q tests\api\test_projection_authorization.py --tb=short`
- VC7: `python -B -m pytest -q tests\api\test_projection_persistence_endpoint.py --tb=short`
- VC8: `python -B -m pytest -q tests\api\test_projection_openapi.py --tb=short`
- VC9: `python -B -c "from app.main import app; assert '/v1/astrology/projections' in app.openapi()['paths']"`
- VC10: `python -B -c "from app.main import app; assert '/v1/astrology/projections' in {getattr(r, 'path', '') for r in app.routes}"`
- VC11: `rg -n "/v1/projections|/v1/astrology/projection|/v1/b2b/astrology/projections|/v1/admin/astrology/projections" app tests`
- VC12: `rg -n "expert_technical_projection_v1|astrology_full_data_v1|admin_chart_diagnostics_v1|provider_response" app tests`
- VC13: `python -B -c "from pathlib import Path as P; assert P('../_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence').exists()"`
- VC14: `python -B -m pytest -q --tb=short`

Before VC3 through VC14, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- Realistic tests could still rely on weak service doubles and miss current builder output shapes.
- Plan evidence could prove only denial and omit successful `free`, `basic`, and `premium` payload behavior.
- Degraded birth data could be invisible in the captured payload, leaving frontend assumptions unverified.
- OpenAPI evidence could pass while alternate route paths appear in `app.routes`.
- Persistence proof could assert response metadata without proving the existing persistence owner is used.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python, Ruff, or pytest command.
- Run backend validation from `backend` after activation unless a command explicitly uses a repository-root path.
- Keep file-level comments and public or non-trivial docstrings in French for new or significantly modified backend files.
- Persist JSON response samples and validation output before moving the story beyond implementation.

## References

- `_story_briefs/cs-302-test-astrology-projections-endpoint-real-conditions.md`
- `_condamad/reports/CS-256-CS-291-delivery-report.md`
- `_condamad/stories/CS-291-generic-projection-endpoint-runtime/00-story.md`
- `_condamad/stories/CS-291-generic-projection-endpoint-runtime/generated/10-final-evidence.md`
- `backend/app/api/v1/routers/public/projections.py`
- `backend/app/services/projections/projection_endpoint_service.py`
- `backend/app/services/api_contracts/public/projections.py`
- `backend/tests/api/test_projection_endpoint.py`
- `backend/tests/api/test_projection_authorization.py`
- `backend/tests/api/test_projection_persistence_endpoint.py`
- `backend/tests/api/test_projection_openapi.py`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/story-status.md`
