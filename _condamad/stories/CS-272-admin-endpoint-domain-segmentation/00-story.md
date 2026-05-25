# Story CS-272 admin-endpoint-domain-segmentation: Define Admin Endpoint Domain Segmentation
Status: done

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-272-split-admin-endpoints-by-domain-business-technical-astrology.md`.
- Required dependency: CS-271 admin data permission matrix.
- Required dependency: CS-266 OpenAPI internal/public exposure guards.
- Existing owner found: `docs/admin-implementation-overview.md` describes current admin route families and backend routers.
- Existing owner found: `backend/app/core/rbac.py` exposes active runtime roles and does not activate target staff roles.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: future admin APIs need domain-segmented endpoint families before more back-office surfaces are added.
- Source-alignment evidence: PASS; the story preserves domain, role, logging, OpenAPI and client-exclusion stakes.

## Objective

Define one canonical admin endpoint segmentation contract for business, technical and astrology domain families.

The implementation must document route-family ownership, target roles, sensitive logging, internal OpenAPI rules and client exclusions without
refactoring existing endpoints, activating RBAC, adding screens or exposing internal projections publicly.

## Target State

- `docs/architecture/admin-endpoint-domain-segmentation.md` exists and starts with a French global file comment.
- The document defines admin endpoint families for business, technical and astrology domains.
- Each endpoint family is mapped to target roles from CS-271 without granting access to inactive roles.
- Sensitive admin surfaces define access-log expectations with actor, route family, action and correlation fields.
- Internal OpenAPI rules distinguish public client OpenAPI from admin/internal contracts.
- Client endpoints are explicitly barred from debug, replay, trace and full astrology runtime surfaces.
- Existing backend admin route families are inventoried through `app.routes`.
- Public OpenAPI exposure is checked with `app.openapi()` so internal projections remain outside public schemas.
- No RBAC implementation, route refactor, frontend UI, database migration, replay system or diagnostics expansion is introduced.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-272-split-admin-endpoints-by-domain-business-technical-astrology.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-272`.
- Evidence 3: `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md` - permission dependency read.
- Evidence 4: `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/00-story.md` - OpenAPI dependency read.
- Evidence 5: `docs/admin-implementation-overview.md` - current admin routes and frontend admin sections inspected.
- Evidence 6: `backend/app/core/rbac.py` - current active backend role registry inspected.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output only.
- Evidence 8: `resolve_guardrails.py` - scoped resolver run for backend-domain, admin endpoints, OpenAPI and logging scope.
- Repository structure alert: backend, backend/app, backend/tests, frontend, frontend/src and docs exist in this workspace.
- Source-alignment evidence: PASS; no brief criterion was dropped or replaced by generic backend cleanup.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Canonical admin endpoint segmentation documentation under `docs/architecture`.
  - Business, technical and astrology admin route-family taxonomy.
  - Role-family attachment using CS-271 as the permission source.
  - Access-log expectations for sensitive admin families.
  - Internal OpenAPI rules for admin-only contracts.
  - Client endpoint exclusions for debug, replay, trace and full astrology runtime surfaces.
  - Runtime route inventory with `app.routes`, `app.openapi()`, `pytest` and `TestClient`.
- Out of scope:
  - Frontend UI, DB schema, auth redesign, i18n, styling, build tooling, migrations, seeds, generated clients and public API changes.
  - Full RBAC implementation, account creation, route protection changes, replay implementation and diagnostic endpoint expansion.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No endpoint move, endpoint rename, serializer, model, repository, migration, user seed, token claim redesign or admin screen.
  - No activation of `MARKETER`, `TECHNO` or `ASTRO_EXPERT`.
  - No client route carrying debug, replay, trace, prompt or full astrology runtime data.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a documentation-first admin endpoint segmentation contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only `docs/architecture/admin-endpoint-domain-segmentation.md`, targeted contract tests and story evidence artifacts.
  - Keep existing route paths, response payloads, authorization behavior and public OpenAPI behavior unchanged.
  - Keep role permissions attached to CS-271 instead of creating a parallel permission matrix.
  - Keep business, technical and astrology families separate in documentation and test assertions.
  - Keep client endpoints outside debug, replay, trace, prompt and full astrology runtime surfaces.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product asks to refactor current admin route paths before the segmentation contract is approved.
- Additional validation rules:
  - The document must define business, technical and astrology admin endpoint families.
  - The document must map each family to target roles through CS-271.
  - The document must define access-log fields for sensitive admin surfaces.
  - The document must define internal OpenAPI rules without changing public OpenAPI output.
  - The document must exclude client endpoints from debug, replay, trace, prompt and full astrology runtime surfaces.
  - `app.routes`, `app.openapi()`, `TestClient`, `pytest`, `python` and `rg` must prove the contract and unchanged route behavior.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, `TestClient` and `pytest` prove admin route inventory and public exposure. |
| Baseline Snapshot | yes | Before and after evidence prove documentation and tests do not refactor endpoint surfaces. |
| Ownership Routing | yes | Admin endpoint families, permission matrix, logs and OpenAPI rules need separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this segmentation story. |
| Contract Shape | yes | The segmentation has exact domains, role links, logging fields, OpenAPI rules and exclusions. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Client debug exposure and broad admin route mixing must stay out. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The segmentation document exists. | Evidence profile: baseline_before_after_diff; `python` checks `docs/architecture/admin-endpoint-domain-segmentation.md`. |
| AC2 | Admin route domains are separated. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes`; `rg` checks domain headings. |
| AC3 | Domain families map to CS-271 roles. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_admin_endpoint_segmentation_contract.py`. |
| AC4 | Sensitive access-log fields are specified. | Evidence profile: json_contract_shape; `rg` checks actor, route family, action and correlation fields. |
| AC5 | Internal OpenAPI rules are documented. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and document rules. |
| AC6 | Client debug surfaces are excluded. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks debug, replay, trace, prompt and runtime exclusions. |
| AC7 | Runtime admin routes are inventoried. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes`; `TestClient` is named in tests. |
| AC8 | Existing route surfaces stay unchanged. | Evidence profile: ast_architecture_guard; `AST guard`; `python` records scoped route status. |
| AC9 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-272 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect the brief, CS-266, CS-271, current RBAC roles and admin overview before writing the contract. (AC: AC1, AC3)
- [ ] Task 2: Create `docs/architecture/admin-endpoint-domain-segmentation.md` with a French global file comment. (AC: AC1)
- [ ] Task 3: Define business, technical and astrology admin endpoint families. (AC: AC2)
- [ ] Task 4: Attach each family to CS-271 role targets without activating inactive roles. (AC: AC3)
- [ ] Task 5: Define access-log fields for sensitive admin route families. (AC: AC4)
- [ ] Task 6: Define internal OpenAPI rules and public OpenAPI exclusion rules. (AC: AC5)
- [ ] Task 7: Exclude client endpoints from debug, replay, trace, prompt and full astrology runtime surfaces. (AC: AC6)
- [ ] Task 8: Add a targeted contract test for document content, `app.routes`, `app.openapi()` and route-surface neutrality. (AC: AC3, AC5, AC7)
- [ ] Task 9: Persist validation, route inventory and scoped status evidence under the CS-272 evidence folder. (AC: AC8, AC9)

## Files to Inspect First

- `_story_briefs/cs-272-split-admin-endpoints-by-domain-business-technical-astrology.md` - source brief.
- `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md` - permission matrix dependency.
- `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/00-story.md` - OpenAPI exposure dependency.
- `docs/admin-implementation-overview.md` - current admin route families and frontend sections.
- `backend/app/core/rbac.py` - current active backend role registry.
- `backend/app/main.py` - loaded FastAPI app, `app.routes` and `app.openapi()` source.
- `backend/app/api/v1/routers/registry.py` - canonical API v1 route registry.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output only.

## Runtime Source of Truth

- Primary source of truth:
  - `app.routes` for current route-family inventory.
  - `app.openapi()` for public OpenAPI exposure state.
  - `TestClient`, `pytest`, `python`, scoped `git status` and targeted `rg` scans for route-surface neutrality.
- Secondary evidence:
  - Targeted `rg` scans over `docs/architecture/admin-endpoint-domain-segmentation.md`.
  - `pytest -q backend/tests/unit/test_admin_endpoint_segmentation_contract.py` for contract content and runtime inventory.
- Static scans alone are not sufficient because:
  - Current admin route inventory and public OpenAPI exposure must be checked from the loaded FastAPI app.

## Contract Shape

- Contract type:
  - Markdown architecture governance document for admin endpoint domain segmentation.
- Fields:
  - `domain_family`: business, technical or astrology.
  - `route_family`: canonical admin route prefix or planned route-family owner.
  - `target_roles`: role references from CS-271.
  - `current_access_state`: current admin-only behavior or future target state.
  - `logging_rule`: required access-log intent for sensitive operations.
  - `openapi_visibility`: public, internal-admin or internal-technical.
  - `client_exclusion`: forbidden client exposure category.
  - `source_dependency`: CS-266 or CS-271 link.
- Required fields:
  - `domain_family`
  - `route_family`
  - `target_roles`
  - `current_access_state`
  - `logging_rule`
  - `openapi_visibility`
  - `client_exclusion`
  - `source_dependency`
- Optional fields:
  - none.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - none; this story writes documentation and contract tests only.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must remain unchanged for public client exposure.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-272-split-admin-endpoints-by-domain-business-technical-astrology.md`
  - `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md`
  - `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/00-story.md`
  - `docs/admin-implementation-overview.md`
  - `backend/app/core/rbac.py`
- Comparison after implementation:
  - `docs/architecture/admin-endpoint-domain-segmentation.md`
  - `backend/tests/unit/test_admin_endpoint_segmentation_contract.py`
  - `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/evidence/validation.txt`
  - `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/evidence/route-inventory.txt`
  - `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended repository delta is one architecture document, one targeted contract test and CONDAMAD evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Admin endpoint segmentation | `docs/architecture/admin-endpoint-domain-segmentation.md` | route code or frontend guards |
| Admin permission source | `docs/architecture/admin-permission-matrix.md` from CS-271 | duplicated role matrix |
| Public/internal OpenAPI exposure | CS-266 contract and backend OpenAPI tests | story-only prose |
| Current admin surface inventory | `docs/admin-implementation-overview.md` and `app.routes` | duplicated UI route registry |
| Story evidence artifacts | `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse CS-271 as the single permission source instead of creating a parallel matrix.
- Reuse CS-266 OpenAPI exposure rules instead of inventing a second internal/public OpenAPI policy.
- Reuse `docs/admin-implementation-overview.md` for current admin surfaces before adding new route-family wording.
- Reuse `app.routes`, `app.openapi()` and `TestClient` for runtime proof instead of duplicating route discovery logic.
- Keep one canonical admin endpoint segmentation document.
- Do not add external packages, generated clients, duplicate admin catalogs or parallel permission registries.

## No Legacy / Forbidden Paths

- No legacy admin endpoint family may be added.
- No compatibility route family may be added.
- No fallback branch may expose debug, replay, trace, prompt or full astrology runtime data to clients.
- Do not create aliases, shims, compatibility wrappers or parallel segmentation documents.
- Do not add `MARKETER`, `TECHNO` or `ASTRO_EXPERT` to active backend role constants in this story.
- Do not modify auth dependencies, route guards, endpoint paths, migrations, seeds, frontend admin guards or account creation flows.

## Reintroduction Guard

- Forbidden client exposure categories:
  - debug surfaces
  - replay surfaces
  - technical traces
  - prompts and LLM payloads
  - full astrology runtime projections
- Forbidden implementation changes:
  - endpoint path moves or renames
  - auth dependency changes
  - public OpenAPI expansion for admin/internal projections
  - frontend admin routing changes
  - migration or seed changes
- Required guards:
  - `python` checks `app.routes` for route-family inventory.
  - `python` checks `app.openapi()` for public exposure state.
  - `pytest -q backend/tests/unit/test_admin_endpoint_segmentation_contract.py` proves the document and runtime contract.
  - `rg` checks the document for domain families, CS-271 role links, OpenAPI rules, logging fields and client exclusions.
  - `git status --short -- backend/app frontend/src` proves scoped application surface neutrality.

## Regression Guardrails

Scope vector:

- backend-domain: yes;
- documentation architecture: yes;
- admin endpoint segmentation: yes;
- backend API route inventory: read-only;
- public OpenAPI exposure: read-only;
- frontend implementation: no;
- DB/migration/auth/i18n/style/build: no;
- admin route refactor: forbidden.

Selected guardrails:

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `Routeurs API v1` | Backend API ownership remains untouched by the documentation story. | scoped `git status`; `python`. |
| RG-003 `Architecture des routes API v1` | Runtime route inventory must remain tied to canonical API registration. | `app.routes`; targeted `pytest`. |
| RG-007 `Endpoints admin LLM observability` | Sensitive admin observability stays in admin/internal families. | `app.openapi()`; `rg`. |
| RG-022 `Plans de validation des stories prompt-generation` | Prompt and replay exposure must have targeted validation evidence. | `rg`; targeted `pytest`. |
| Registry gap | No exact admin endpoint segmentation guardrail exists in resolver output. | Story-local endpoint guards. |

Non-applicable examples:

- RG-041 entitlement documentation is out of scope because this story segments admin endpoint families, not product entitlements.
- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 frontend CSS namespace migration is out of scope because no style or build output is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation output | `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/evidence/validation.txt` | Keep validation transcript. |
| Route inventory | `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/evidence/route-inventory.txt` | Capture `app.routes` family evidence. |
| Application surface status | `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/evidence/app-surface-status.txt` | Prove scoped app changes. |
| Source checklist | `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/evidence/source-checklist.md` | Record source coverage. |
| Review output | `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this segmentation story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/admin-endpoint-domain-segmentation.md` - define the canonical admin endpoint segmentation contract.
- `backend/tests/unit/test_admin_endpoint_segmentation_contract.py` - cover document content, `app.routes` and `app.openapi()`.
- `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/evidence/validation.txt` - persist validation output.
- `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/evidence/route-inventory.txt` - persist route inventory output.
- `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/evidence/app-surface-status.txt` - persist scoped status output.
- `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/evidence/source-checklist.md` - persist source coverage.

Likely tests:

- `backend/tests/unit/test_admin_endpoint_segmentation_contract.py` - document, runtime route inventory and OpenAPI neutrality checks.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no persistence schema is created.
- `backend/app/api/**` - out of scope; no route path, router registration or auth dependency is touched.
- `backend/app/core/security.py` - out of scope; no token or auth behavior is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `rg -n "admin|business|technical|astrology|endpoint|OpenAPI interne|client" .\docs .\_story_briefs`
- VC2: `rg -n "business|technical|astrology|CS-271|MARKETER|TECHNO|ASTRO_EXPERT" docs/architecture/admin-endpoint-domain-segmentation.md`
- VC3: `rg -n "acteur|actor|route family|famille|action|correlation" docs/architecture/admin-endpoint-domain-segmentation.md`
- VC4: `rg -n "OpenAPI interne|app.openapi|public OpenAPI|internal-admin" docs/architecture/admin-endpoint-domain-segmentation.md`
- VC5: `rg -n "debug|replay|trace|prompt|runtime|client" docs/architecture/admin-endpoint-domain-segmentation.md`
- VC6: `pytest -q backend/tests/unit/test_admin_endpoint_segmentation_contract.py`
- VC7: `python -c "from app.main import app; assert any('/v1/admin' in getattr(r, 'path', '') for r in app.routes)"`
- VC8: `python -c "from app.main import app; data=str(app.openapi()); assert 'admin_chart_diagnostics' not in data"`
- VC9: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-272-admin-endpoint-domain-segmentation/evidence/validation.txt').exists()"`
- VC10: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-272-admin-endpoint-domain-segmentation/evidence/route-inventory.txt').exists()"`
- VC11: `git status --short -- backend/app frontend/src`
- VC12: `ruff format .`
- VC13: `ruff check .`
- VC14: `pytest -q`

Before VC6 through VC10, VC12, VC13 and VC14, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- Admin route families may remain documented as one broad admin surface.
- Target roles may be interpreted as active access grants.
- Sensitive logs may miss actor, action or correlation fields.
- Internal OpenAPI rules may drift away from CS-266 public exposure guards.
- Client endpoints may inherit debug, replay, trace, prompt or full astrology runtime surfaces.
- Application files may change while trying to prove the documentation contract.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the Python virtual environment before every Python command.
- Keep backend runtime behavior unchanged.
- Keep existing route paths and router registrations unchanged.
- Keep `MARKETER`, `TECHNO` and `ASTRO_EXPERT` out of active backend role constants.
- Keep client endpoints outside debug, replay, trace, prompt and full astrology runtime surfaces.
- Persist validation output under the CS-272 evidence folder before requesting review.

## References

- `_story_briefs/cs-272-split-admin-endpoints-by-domain-business-technical-astrology.md`
- `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md`
- `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/00-story.md`
- `docs/admin-implementation-overview.md`
- `backend/app/core/rbac.py`
- `backend/app/main.py`
- `backend/app/api/v1/routers/registry.py`
- `_condamad/stories/regression-guardrails.md`
