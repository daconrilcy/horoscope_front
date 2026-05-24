# Story CS-263 generic-projection-endpoint-contract: Define Generic Projection Endpoint Contract
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-263-define-generic-projection-endpoint-contract.md`.
- Related dependency: CS-256 to CS-258 define initial projection contracts expected by this endpoint contract.
- Related dependency: CS-259 defines the narrative answer audit projection contract.
- Existing owner found: `docs/architecture/official-product-primitives-public-projections.md` owns public projection governance.
- Existing owner found: `backend/app/infra/db/repositories/chart_result_repository.py` owns existing `chart_id` lookup semantics.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: `POST /v1/astrology/projections` lacks a canonical contract for consolidated B2C projection commands.
- Source-alignment evidence: PASS; ACs preserve endpoint contract, separated calculation/projection services, B2C access rules and B2B exclusion.

## Objective

Define one canonical backend API contract document for `POST /v1/astrology/projections` without implementing the route.

The implementation must document payload fields, chart selection rules, controlled errors, projection access policy, internal projection exclusions,
service separation, unavailable dependency handling and B2B API exclusion while leaving OpenAPI, routers, persistence, frontend and runtime services unchanged.

## Target State

- `POST /v1/astrology/projections` is documented as a future B2C command that may consolidate theme calculation and projection construction.
- The contract defines request fields `chart_id`, `birth_input`, `projection_type`, `projection_version` and `persist`.
- `projection_version` is mandatory for every request.
- The contract defines the rule for an existing `chart_id` versus a supplied `birth_input`.
- Calculation of the chart and construction of the projection remain conceptually separated services.
- Controlled error cases cover invalid input, unknown chart, unauthorized projection, unavailable projection and unavailable calculation.
- B2C projection access is explicit by `projection_type`, plan or entitlement policy, and internal technical projections are denied to clients.
- Unavailable calculation or projection dependencies are blocking outcomes and must be logged by the future implementation.
- The B2B API remains out of scope and is not defined, exposed or implied by this contract.
- No route, OpenAPI mutation, persistence object, frontend screen, generated client, builder, service or test runtime implementation is created by this story.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-263-define-generic-projection-endpoint-contract.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-263`.
- Evidence 3: `docs/architecture/official-product-primitives-public-projections.md` - public projection governance owner found.
- Evidence 4: `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md` - upstream projection dependency read.
- Evidence 5: `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/00-story.md` - B2C projection dependency read.
- Evidence 6: `backend/app/infra/db/repositories/chart_result_repository.py` - existing `chart_id` lookup owner found by targeted search.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output and targeted ID lookup only.
- Source-alignment evidence: PASS; the story answers every brief AC without turning the contract into runtime API implementation work.

## Domain Boundary

- Domain: backend-api
- In scope:
  - Canonical contract documentation for `POST /v1/astrology/projections`.
  - Request payload, source selection, projection access and controlled error rules.
  - Conceptual separation between chart calculation and projection construction services.
  - Negative checks for route, OpenAPI, persistence, frontend, B2B and internal projection drift.
  - Persistent evidence artifacts for source coverage, contract scans and runtime-neutrality checks.
- Out of scope:
  - Frontend UI, database schema, auth implementation, i18n, styling, build tooling, migrations and generated clients.
  - Route implementation, router registration, OpenAPI mutation, service builder, model, serializer, persistence and B2B API definition.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No FastAPI route, `app.openapi()` path, response serializer or generated OpenAPI client for `POST /v1/astrology/projections`.
  - No runtime projection builder, calculation orchestration service, database table or migration.
  - No B2B endpoint, partner contract, admin endpoint, internal technical projection exposure or entitlement implementation.

## Operation Contract

- Operation type: create
- Primary archetype: api-contract-change
- Archetype reason: the story defines a public API endpoint contract with request, error and access rules.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the `POST /v1/astrology/projections` contract documentation, related registry alignment and story evidence artifacts.
  - Reuse existing public projection governance, CS-256 to CS-259 terminology and existing `chart_id` source ownership.
  - Keep backend runtime code, API routes, OpenAPI output, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Keep calculation service responsibility separate from projection construction responsibility.
  - Keep internal technical projections unavailable to B2C clients.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product asks to expose B2B API behavior or internal technical projections through this B2C contract.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, `pytest` and `TestClient` prove no route is implemented by this contract story. |
| Baseline Snapshot | yes | Before and after artifacts prove the only allowed surface delta is documentation and CONDAMAD evidence. |
| Ownership Routing | yes | Endpoint contract, chart lookup, calculation services and projection services need separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this B2C endpoint contract documentation story. |
| Contract Shape | yes | The endpoint has exact method, path, payload, status categories, errors and access rules. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Unauthorized paths, B2B API scope and internal projections must stay out. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `POST /v1/astrology/projections` is documented. | Evidence profile: baseline_before_after_diff; `python` checks the contract document path. |
| AC2 | Request payload fields are explicit. | Evidence profile: json_contract_shape; `rg` checks `chart_id`, `birth_input`, `projection_type`, `projection_version`, `persist`. |
| AC3 | `projection_version` is mandatory. | Evidence profile: json_contract_shape; `rg` checks mandatory version wording in the contract document. |
| AC4 | Chart source selection is explicit. | Evidence profile: json_contract_shape; `rg` checks existing `chart_id` versus `birth_input` rules. |
| AC5 | Service ownership stays separated. | Evidence profile: ast_architecture_guard; `rg` checks separate service responsibility wording. |
| AC6 | Controlled error cases are explicit. | Evidence profile: api_error_shape_contract; `rg` checks invalid, unauthorized and unavailable error cases. |
| AC7 | B2C access rules are explicit. | Evidence profile: json_contract_shape; `rg` checks projection access by type and plan or entitlement policy. |
| AC8 | Internal projections are denied to clients. | Evidence profile: external_usage_blocker; `rg` checks internal technical projection denial wording. |
| AC9 | Public runtime API surface stays unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`; `TestClient` stays neutral. |
| AC10 | B2B API remains out of scope. | Evidence profile: route_absence_runtime; `python` checks `app.routes`; `rg` checks B2B exclusion wording. |
| AC11 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-263 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect existing projection governance, CS-256 to CS-259 stories and chart lookup owner before writing the contract. (AC: AC1, AC4)
- [ ] Task 2: Create `docs/architecture/generic-projection-endpoint-contract.md` with a French global file comment. (AC: AC1)
- [ ] Task 3: Define method, path, B2C audience and no-runtime-implementation policy for `POST /v1/astrology/projections`. (AC: AC1, AC9)
- [ ] Task 4: Document request fields `chart_id`, `birth_input`, `projection_type`, `projection_version` and `persist`. (AC: AC2, AC3)
- [ ] Task 5: Document the existing `chart_id` versus `birth_input` source selection rule. (AC: AC4)
- [ ] Task 6: Document separate responsibilities for chart calculation and projection construction. (AC: AC5)
- [ ] Task 7: Document controlled error categories for validation, access, missing chart and unavailable dependencies. (AC: AC6)
- [ ] Task 8: Document B2C projection access rules and internal technical projection denial. (AC: AC7, AC8)
- [ ] Task 9: Document that unavailable calculation or projection dependencies are blocking and logged outcomes. (AC: AC6)
- [ ] Task 10: Document that B2B API behavior is not defined or exposed by this story. (AC: AC10)
- [ ] Task 11: Persist validation, scoped status and source checklist evidence under the CS-263 evidence folder. (AC: AC9, AC11)

## Files to Inspect First

- `_story_briefs/cs-263-define-generic-projection-endpoint-contract.md` - source contract.
- `docs/architecture/official-product-primitives-public-projections.md` - existing public projection governance owner.
- `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md` - upstream structured facts dependency.
- `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/00-story.md` - beginner B2C projection dependency.
- `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/00-story.md` - client interpretation projection dependency.
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md` - audit projection dependency.
- `backend/app/infra/db/repositories/chart_result_repository.py` - existing chart lookup owner for `chart_id`.
- `backend/app/api/v1/routers/` - route inventory only; no route implementation is authorized.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `docs/architecture/official-product-primitives-public-projections.md` for projection governance.
  - CS-256 to CS-259 story contracts for initial projection terminology.
  - `backend/app/infra/db/repositories/chart_result_repository.py` for existing `chart_id` lookup semantics.
  - `app.routes`, `app.openapi()`, `TestClient`, scoped `git status` and targeted `rg` scans for no public API or app-source drift.
- Secondary evidence:
  - Targeted `rg` scans over `docs/architecture/generic-projection-endpoint-contract.md`.
- Static scans alone are not sufficient because:
  - route neutrality and OpenAPI neutrality must be proven from the loaded app object.

## Contract Shape

- Contract type:
  - Markdown backend API contract for a future B2C projection command.
- Method and path:
  - `POST /v1/astrology/projections`.
- Fields:
  - `chart_id`: optional existing chart identifier owned by the authenticated B2C user.
  - `birth_input`: optional birth payload used when no reusable existing chart is selected.
  - `projection_type`: required projection identifier selected from authorized B2C projection types.
  - `projection_version`: required projection contract version.
  - `persist`: optional boolean controlling whether the future command may persist eligible outputs.
- Required fields:
  - `projection_type`
  - `projection_version`
- Conditional fields:
  - exactly one accepted chart source rule must be documented for `chart_id` and `birth_input`.
- Optional fields:
  - `persist`.
- Status codes:
  - `200` for successful non-created projection response.
  - `201` for successful response that creates a newly persisted eligible artifact.
  - `400` for invalid chart source selection.
  - `401` for unauthenticated access.
  - `403` for unauthorized projection type or plan.
  - `404` for unknown or inaccessible `chart_id`.
  - `409` for unavailable calculation or projection dependency.
  - `422` for invalid payload shape or unsupported `projection_version`.
- Serialization names:
  - JSON keys are emitted exactly as `chart_id`, `birth_input`, `projection_type`, `projection_version` and `persist`.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose `/v1/astrology/projections` from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-263-define-generic-projection-endpoint-contract.md`
  - `docs/architecture/official-product-primitives-public-projections.md`
  - `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md`
  - `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/00-story.md`
- Comparison after implementation:
  - `docs/architecture/generic-projection-endpoint-contract.md`
  - `_condamad/stories/CS-263-generic-projection-endpoint-contract/evidence/validation.txt`
  - `_condamad/stories/CS-263-generic-projection-endpoint-contract/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended repository delta is one architecture contract document, optional registry alignment and CONDAMAD story/evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Endpoint contract | `docs/architecture/generic-projection-endpoint-contract.md` | API routers or generated clients |
| Projection governance | `docs/architecture/official-product-primitives-public-projections.md` | duplicated registry document |
| Existing chart lookup | `backend/app/infra/db/repositories/chart_result_repository.py` | endpoint contract document as repository owner |
| Chart calculation | existing backend calculation services | projection builder or API router |
| Projection construction | future projection service contract | chart calculation service |
| Evidence artifacts | `_condamad/stories/CS-263-generic-projection-endpoint-contract/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse existing public projection governance instead of creating a second projection registry.
- Reuse CS-256 to CS-259 projection identifiers and access terminology instead of inventing parallel names.
- Reuse existing `chart_id` lookup ownership for documented source selection.
- Keep one canonical `POST /v1/astrology/projections` contract document and one route path.
- Do not add external packages, scripts, API schemas, frontend helpers, builders, services, prompts or generated clients.
- Do not duplicate calculation logic inside projection construction wording.

## No Legacy / Forbidden Paths

- No legacy public route path may be added for this endpoint contract.
- No compatibility route path may be added for this endpoint contract.
- No fallback route path may be added for this endpoint contract.
- Do not create aliases, shims, wrappers or parallel documents for the same endpoint contract.
- Do not expose internal technical projections, raw runtime payloads, debug traces, B2B API rules or partner-only behavior to B2C clients.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/**`
  - `backend/app/infra/db/**`
  - `backend/migrations/**`
  - generated OpenAPI clients
  - B2B API or partner endpoint contracts

## Reintroduction Guard

- Guard target:
  - `/v1/astrology/projections` cannot appear in `app.routes` or `app.openapi()` from this story;
  - `/v1/b2b`, `/v1/partners` or alternate projection endpoint paths cannot be introduced by this contract;
  - internal technical projections cannot become B2C-accessible projection types;
  - chart calculation and projection construction cannot collapse into one documented service owner.
- Guard mechanism:
  - targeted `rg` checks for required contract terms and unauthorized route paths;
  - `app.routes`, `app.openapi()` and `TestClient` neutrality checks;
  - scoped `git status --short` for application roots;
  - persisted evidence under the CS-263 evidence folder.
- Guard owner:
  - `docs/architecture/generic-projection-endpoint-contract.md`;
  - `_condamad/stories/CS-263-generic-projection-endpoint-contract/evidence/validation.txt`;
  - `_condamad/stories/CS-263-generic-projection-endpoint-contract/evidence/app-surface-status.txt`.
- Guard evidence:
  - `rg -n "/v1/astrology/projections|projection_type|projection_version|birth_input|chart_id|persist" .\docs .\_story_briefs`;
  - `python -c "from app.main import app; assert '/v1/astrology/projections' not in app.openapi().get('paths', {})"`;
  - `python -c "from app.main import app; assert all(getattr(r, 'path', '') != '/v1/astrology/projections' for r in app.routes)"`;
  - `git status --short -- backend/app frontend/src`.

## Regression Guardrails

Scope vector:

- backend-api contract documentation: yes;
- docs architecture contract: yes;
- API route implementation: no;
- OpenAPI runtime change: no;
- frontend implementation: no;
- DB, auth implementation, i18n, style, build and migration: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | API route owners stay canonical because the story forbids router changes. | `git status`; targeted `rg`. |
| RG-003 | Runtime route inventory and OpenAPI stay unchanged for this contract-only story. | `app.routes`; `app.openapi()`. |
| RG-022 | Validation paths must be executable and not obsolete. | `pytest`; targeted contract scans. |
| Registry gap | No exact `/v1/astrology/projections` guardrail exists in resolver output. | Story-local runtime-neutrality guards. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-007 admin LLM observability is out of scope because this endpoint contract concerns astrology projections.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Contract document | `docs/architecture/generic-projection-endpoint-contract.md` | Keep the canonical B2C generic projection endpoint contract. |
| Validation output | `_condamad/stories/CS-263-generic-projection-endpoint-contract/evidence/validation.txt` | Keep content scans and story validation. |
| Application surface status | `_condamad/stories/CS-263-generic-projection-endpoint-contract/evidence/app-surface-status.txt` | Prove app roots stayed untouched. |
| Source checklist | `_condamad/stories/CS-263-generic-projection-endpoint-contract/evidence/source-checklist.md` | Record mandatory source coverage. |
| Review output | `_condamad/stories/CS-263-generic-projection-endpoint-contract/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this endpoint contract documentation story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/generic-projection-endpoint-contract.md` - new canonical endpoint contract document.
- `docs/architecture/official-product-primitives-public-projections.md` - align the registry with the CS-263 endpoint contract.
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/evidence/app-surface-status.txt` - application non-change proof.
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/evidence/source-checklist.md` - source coverage evidence.

Likely tests:

- `docs/architecture/generic-projection-endpoint-contract.md` - checked by `rg` and `python` validation commands.
- `backend/tests/architecture/test_api_contract_neutrality.py` - targeted architecture regression check for route and OpenAPI neutrality.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/**` - out of scope; no backend application source is touched.
- `backend/tests/**` - out of scope except existing architecture tests executed as evidence.
- `backend/migrations/**` - out of scope; no database migration is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `python -c "from pathlib import Path; assert Path('docs/architecture/generic-projection-endpoint-contract.md').exists()"`
- VC3: `rg -n "/v1/astrology/projections|projection_type|projection_version|birth_input|chart_id|persist" .\docs .\_story_briefs`
- VC4: `rg -n "mandatory|projection_version|existing chart_id|birth_input" docs/architecture/generic-projection-endpoint-contract.md`
- VC5: `rg -n "calculation service|projection construction|separate" docs/architecture/generic-projection-endpoint-contract.md`
- VC6: `rg -n "invalid input|unknown chart|unauthorized projection|unavailable calculation|unavailable projection" docs/architecture/generic-projection-endpoint-contract.md`
- VC7: `rg -n "B2C|internal technical projections|B2B API is out of scope" docs/architecture/generic-projection-endpoint-contract.md`
- VC8: `python -c "from app.main import app; assert '/v1/astrology/projections' not in app.openapi().get('paths', {})"`
- VC9: `python -c "from app.main import app; assert all(getattr(r, 'path', '') != '/v1/astrology/projections' for r in app.routes)"`
- VC10: `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`
- VC11: `git status --short -- backend/app frontend/src`
- VC12: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-263-generic-projection-endpoint-contract/evidence/validation.txt').exists()"`
- VC13: `ruff format .`
- VC14: `ruff check .`
- VC15: `pytest -q`
- VC16: `git status --short -- backend/app frontend/src`

Before VC2, VC8, VC9 and VC12, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- A contract-only story could drift into FastAPI route or OpenAPI implementation.
- A consolidated endpoint could collapse calculation and projection ownership into one service.
- Internal technical projections could become B2C-accessible by omission in the access matrix.
- `projection_version` could become optional, making future payload evolution ambiguous.
- Unavailable calculation or projection dependencies could become silent degraded responses.
- B2B API behavior could be implied by a generic endpoint contract without a separate product and security decision.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments and public or non-trivial docstrings in French for new or significantly modified backend files.
- Keep the implementation documentation-only unless a separate user decision authorizes route implementation work.
- Persist the required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-263-define-generic-projection-endpoint-contract.md`
- `docs/architecture/official-product-primitives-public-projections.md`
- `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md`
- `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/00-story.md`
- `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/00-story.md`
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md`
- `backend/app/infra/db/repositories/chart_result_repository.py`
- `backend/app/api/v1/routers/`
- `_condamad/stories/regression-guardrails.md`
