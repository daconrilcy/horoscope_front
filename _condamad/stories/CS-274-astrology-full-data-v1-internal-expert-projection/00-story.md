# Story CS-274 astrology-full-data-v1-internal-expert-projection: Define astrology_full_data_v1 Internal Expert Projection
Status: done

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-274-define-astrology-full-data-v1-internal-expert-projection.md`.
- Required dependency: CS-273 expert technical projection internal contract.
- Required dependency: CS-271 admin data permission matrix.
- Required dependency: CS-256 structured facts contract.
- Existing owner found: `docs/architecture/official-product-primitives-public-projections.md` owns product projection registry decisions.
- Existing owner found: `docs/architecture/product-architecture-current-state-2026-05-24.md` documents internal runtime and projection boundaries.
- Existing owner found: CS-273 separates expert technical projection from B2C and raw debug payloads.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: `astrology_full_data_v1` lacks a canonical internal expert projection contract distinct from technical diagnostics.
- Source-alignment evidence: PASS; the story preserves internal audience, full astrology families, masking, dependencies, access and logs.

## Objective

Define one canonical backend-domain contract for `astrology_full_data_v1` as an internal full astrology projection for expert use.

The implementation must document complete astrology data families, source dependencies, masking policy, access rules and audit logging without creating
runtime builders, routes, persistence, frontend UI or technical debug exposure.

## Target State

- `docs/architecture/astrology-full-data-v1-contract.md` exists and starts with a French global file comment.
- `astrology_full_data_v1` is documented as an internal projection for current `ADMIN` and future target-only `ASTRO_EXPERT`.
- The contract distinguishes astrology business/expert data from `admin_chart_diagnostics_v1` and technical calculation debug data.
- Full astrology families are named: chart objects summary, positions, houses, dignities, conditions, aspects, dominance, fixed-star policy and sources.
- Personal data masking rules cover birth date/time/place, user identifiers, chart identifiers and justification for retained sensitive fields.
- Dependencies on `structured_facts_v1`, source versions, doctrine/school metadata and evidence references are explicit.
- Access conditions and log fields are specified without activating new RBAC behavior.
- No route, OpenAPI exposure, RBAC activation, frontend file, DB object, migration, builder, service or replay/log technical payload is created.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-274-define-astrology-full-data-v1-internal-expert-projection.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-274`.
- Evidence 3: `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/00-story.md` - expert projection dependency read.
- Evidence 4: `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md` - permission matrix dependency read.
- Evidence 5: `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md` - structured facts dependency read.
- Evidence 6: `docs/architecture/official-product-primitives-public-projections.md` - existing projection registry inspected.
- Evidence 7: `docs/architecture/product-architecture-current-state-2026-05-24.md` - internal runtime and projection boundaries inspected.
- Evidence 8: `backend/app/domain/astrology/runtime/**` - canonical runtime source area found by scoped backend inventory.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output and targeted ID lookup only.
- Evidence 10: `resolve_guardrails.py` - scoped resolver run for backend-domain, projection contract, access policy, privacy masking and documentation.
- Repository structure alert: backend, backend/app, backend/tests, frontend, frontend/src and docs exist in this workspace.
- Source-alignment evidence: PASS; no source concern was deferred, softened or replaced by generic documentation cleanup.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Canonical contract documentation for `astrology_full_data_v1` under `docs/architecture`.
  - Internal expert projection scope for `ADMIN` and future target-only `ASTRO_EXPERT`.
  - Full astrology data family taxonomy and separation from technical diagnostics.
  - Personal data masking and retained-field justification rules.
  - Dependencies on `structured_facts_v1`, source versions, doctrine metadata and evidence references.
  - Access-condition and journalisation fields for protected internal use.
  - Runtime-neutrality checks using `app.routes`, `app.openapi()`, `pytest`, scoped `git status` and targeted `rg`.
- Out of scope:
  - Frontend UI, DB schema, auth redesign, i18n, styling, build tooling, migrations, seeds, generated clients and public API changes.
  - Projection implementation, builder service, runtime model, serializer, persistence, replay, route implementation and full technical logs.
  - Public fixed-star exposure and client-facing expert panels.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No client B2C endpoint, serializer, OpenAPI schema, generated client, screen, model, migration, seed, token claim redesign or access grant.
  - No activation of `ASTRO_EXPERT`.
  - No `admin_chart_diagnostics_v1` replay payload, calculation trace bundle, raw provider dump or unrestricted technical diagnostics.
  - No direct client exposure of fixed stars or raw fixed-star catalog data.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a documentation-first internal expert astrology projection contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only `docs/architecture/astrology-full-data-v1-contract.md`, targeted contract tests and story evidence artifacts.
  - Extend or align existing projection governance documents instead of creating a parallel projection registry.
  - Keep backend runtime code, API routes, OpenAPI output, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Keep permission ownership attached to CS-271 instead of defining a parallel access matrix.
  - Keep `ASTRO_EXPERT` as target-only role vocabulary until RBAC exists.
  - Keep `admin_chart_diagnostics_v1` as a separate technical diagnostics surface.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product asks to expose `astrology_full_data_v1` to B2C or merge it with technical diagnostics.
- Additional validation rules:
  - The contract must name `astrology_full_data_v1` exactly.
  - The contract must state that the projection is internal, protected and expert-oriented.
  - The contract must limit authorized consumers to `ADMIN` and future target-only `ASTRO_EXPERT`.
  - The contract must separate astrology expert data from `admin_chart_diagnostics_v1` and calculation debug payloads.
  - The contract must list full astrology data families including positions, houses, dignities, conditions, aspects and dominance.
  - The contract must document fixed-star handling as internal policy-bound data with no client exposure from this story.
  - The contract must document masking or justification for birth date/time/place, user ids and chart ids.
  - The contract must depend on `structured_facts_v1`, source versions, doctrine/school metadata and evidence references.
  - The contract must define access-log fields for every access decision.
  - `app.routes`, `app.openapi()`, `pytest`, `python`, `rg` and scoped `git status` must prove public/runtime neutrality.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, `pytest` and runtime source owners prove no public exposure is introduced. |
| Baseline Snapshot | yes | Before and after evidence prove the only allowed surface delta is documentation, tests and story evidence. |
| Ownership Routing | yes | Projection contract, registry, permission matrix, diagnostics and evidence refs need separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this internal projection contract story. |
| Contract Shape | yes | The projection has exact audience, data families, masking, dependencies, exclusions and log fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | B2C exposure, technical diagnostics merge and raw debug payloads must stay out. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The full astrology contract exists. | Evidence profile: baseline_before_after_diff; `python` checks the contract document path. |
| AC2 | The projection is internal. | Evidence profile: json_contract_shape; `rg` checks `astrology_full_data_v1`, interne, protected and expert wording. |
| AC3 | Authorized consumers are explicit. | Evidence profile: json_contract_shape; `rg` checks `ADMIN`, `ASTRO_EXPERT` and target-only wording. |
| AC4 | Technical diagnostics stay separate. | Evidence profile: targeted_forbidden_symbol_scan; `pytest -q backend/tests/unit/test_astrology_full_data_contract.py`. |
| AC5 | Full astrology families are defined. | Evidence profile: json_contract_shape; `rg` checks positions, houses, dignities, conditions, aspects and dominance. |
| AC6 | Fixed-star client exposure is denied. | Evidence profile: external_usage_blocker; `pytest -q backend/tests/unit/test_astrology_full_data_contract.py`. |
| AC7 | Personal data masking is specified. | Evidence profile: json_contract_shape; `rg` checks birth date, birth time, birth place, user id and chart id masking. |
| AC8 | Source dependencies are explicit. | Evidence profile: json_contract_shape; `rg` checks `structured_facts_v1`, source versions, doctrine and evidence refs. |
| AC9 | Access-log fields are specified. | Evidence profile: json_contract_shape; `rg` checks actor, role, projection id, action, decision and correlation fields. |
| AC10 | Public runtime exposure is absent. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`; `pytest` uses TestClient. |
| AC11 | Application source surfaces remain unchanged. | Evidence profile: repo_wide_negative_scan; `python` records scoped `git status --short` output for app roots. |
| AC12 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-274 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect the brief, projection registry, product architecture and CS-256, CS-271 and CS-273 before writing. (AC: AC1, AC8)
- [ ] Task 2: Create `docs/architecture/astrology-full-data-v1-contract.md` with a French global file comment. (AC: AC1)
- [ ] Task 3: Define `astrology_full_data_v1` as an internal protected projection for expert astrology use. (AC: AC2)
- [ ] Task 4: Limit authorized consumers to current `ADMIN` and future target-only `ASTRO_EXPERT`. (AC: AC3)
- [ ] Task 5: Separate expert astrology data from `admin_chart_diagnostics_v1` and calculation debug payloads. (AC: AC4)
- [ ] Task 6: Define complete astrology families for positions, houses, dignities, conditions, aspects and dominance. (AC: AC5)
- [ ] Task 7: Document fixed-star handling as internal and not client-exposed by this story. (AC: AC6)
- [ ] Task 8: Define personal data masking or retained-field justification rules. (AC: AC7)
- [ ] Task 9: Link `structured_facts_v1`, source versions, doctrine/school metadata and evidence references. (AC: AC8)
- [ ] Task 10: Define access-log fields for protected projection access decisions. (AC: AC9)
- [ ] Task 11: Add targeted contract tests for document content and runtime neutrality. (AC: AC4, AC6, AC10)
- [ ] Task 12: Persist validation, scoped status and source checklist evidence under the CS-274 evidence folder. (AC: AC11, AC12)

## Files to Inspect First

- `_story_briefs/cs-274-define-astrology-full-data-v1-internal-expert-projection.md` - source brief.
- `docs/architecture/official-product-primitives-public-projections.md` - existing projection registry.
- `docs/architecture/product-architecture-current-state-2026-05-24.md` - current internal runtime and projection boundaries.
- `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md` - structured facts dependency.
- `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md` - permission matrix dependency.
- `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/00-story.md` - nearest expert projection dependency.
- `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/00-story.md` - public OpenAPI exposure guard dependency.
- `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/00-story.md` - admin domain segmentation and log dependency.
- `backend/app/main.py` - loaded FastAPI app, `app.routes` and `app.openapi()` source.
- `backend/tests/architecture/test_api_contract_neutrality.py` - existing public exposure guard owner.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `docs/architecture/official-product-primitives-public-projections.md` for projection registry ownership.
  - CS-256 for `structured_facts_v1`, evidence references and fact boundary.
  - CS-271 for protected admin permission ownership.
  - CS-273 for expert-only projection governance and technical payload exclusions.
  - `backend/app/domain/astrology/runtime/**` for canonical astrology runtime source ownership.
  - `app.routes`, `app.openapi()`, `TestClient`, `pytest`, scoped `git status` and targeted `rg` scans for runtime neutrality.
- Secondary evidence:
  - Targeted `rg` scans over `docs/architecture/astrology-full-data-v1-contract.md`.
  - `pytest -q backend/tests/unit/test_astrology_full_data_contract.py` for contract content and runtime-neutrality checks.
- Static scans alone are not sufficient because:
  - public OpenAPI neutrality and route absence must be checked from the loaded FastAPI app.

## Contract Shape

- Contract type:
  - Markdown backend-domain contract for an internal full astrology expert projection.
- Fields:
  - `projection_id`: exact value `astrology_full_data_v1`.
  - `classification`: internal, protected, expert-oriented and non client.
  - `authorized_consumers`: `ADMIN` and future target-only `ASTRO_EXPERT`.
  - `denied_consumers`: B2C clients, public-user surfaces and generated public clients.
  - `data_families`: chart summary, positions, houses, dignities, conditions, aspects, dominance, fixed-star policy and source metadata.
  - `diagnostics_boundary`: separation from `admin_chart_diagnostics_v1`, replay payloads and calculation debug data.
  - `privacy_policy`: masked or justified birth date/time/place, user id, chart id and location precision.
  - `source_dependencies`: `structured_facts_v1`, source versions, doctrine/school metadata and evidence references.
  - `access_policy`: CS-271 permission matrix plus no active `ASTRO_EXPERT` grant.
  - `access_log_fields`: actor, role, projection id, chart or answer reference, action, decision, timestamp and correlation id.
- Required fields:
  - `projection_id`
  - `classification`
  - `authorized_consumers`
  - `denied_consumers`
  - `data_families`
  - `diagnostics_boundary`
  - `privacy_policy`
  - `source_dependencies`
  - `access_policy`
  - `access_log_fields`
- Optional fields:
  - none.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - documentation only; no runtime JSON serializer is added.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose `astrology_full_data_v1` from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-274-define-astrology-full-data-v1-internal-expert-projection.md`
  - `docs/architecture/official-product-primitives-public-projections.md`
  - `docs/architecture/product-architecture-current-state-2026-05-24.md`
  - `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md`
  - `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md`
  - `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/00-story.md`
- Comparison after implementation:
  - `docs/architecture/astrology-full-data-v1-contract.md`
  - `backend/tests/unit/test_astrology_full_data_contract.py`
  - `_condamad/stories/CS-274-astrology-full-data-v1-internal-expert-projection/evidence/validation.txt`
  - `_condamad/stories/CS-274-astrology-full-data-v1-internal-expert-projection/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended repository delta is one architecture contract document, one targeted test and CONDAMAD evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Full astrology projection contract | `docs/architecture/astrology-full-data-v1-contract.md` | API routers or frontend clients |
| Projection primitive registry | `docs/architecture/official-product-primitives-public-projections.md` | duplicated projection registry |
| Permission ownership | `docs/architecture/admin-permission-matrix.md` from CS-271 | projection contract as access matrix |
| Structured fact source | `docs/architecture/structured-facts-v1-contract.md` from CS-256 | raw runtime payload contract |
| Technical diagnostics | future `admin_chart_diagnostics_v1` contract | `astrology_full_data_v1` contract |
| Public OpenAPI exposure guard | CS-266 tests and documentation | public projection registry wording |
| Access-log expectations | CS-272 admin segmentation plus this contract | route implementation in this story |
| Story evidence artifacts | `_condamad/stories/CS-274-astrology-full-data-v1-internal-expert-projection/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse the existing projection primitive registry instead of creating a second registry for full astrology projections.
- Reuse CS-256 `structured_facts_v1`, source versions and evidence references instead of inventing a separate factual base.
- Reuse CS-271 role/domain/action and masking vocabulary instead of defining parallel permission rules.
- Reuse CS-273 internal expert projection wording for audience and B2C denial.
- Reuse CS-266 public exposure guard wording for OpenAPI neutrality.
- Keep `admin_chart_diagnostics_v1` separate instead of making debug data a field family inside `astrology_full_data_v1`.
- Keep one canonical `astrology_full_data_v1` contract document and one projection identifier.
- Do not add external packages, generated clients, builders, services, routes, serializers or database objects.

## No Legacy / Forbidden Paths

- No legacy public projection path may be added for this contract.
- No compatibility projection path may expose this contract to B2C clients.
- No fallback branch may merge expert astrology projection data with technical diagnostics.
- Do not create aliases, shims, compatibility wrappers or parallel projection documents.
- Do not add `ASTRO_EXPERT` to active backend role constants in this story.
- Do not expose raw runtime traces, prompt internals, replay payloads, provider debug dumps or unrestricted diagnostics through this projection.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/**`
  - `backend/app/infra/db/**`
  - `backend/migrations/**`
  - generated OpenAPI clients
  - public B2C projection contracts

## Reintroduction Guard

- Guard target:
  - `astrology_full_data_v1` cannot become a B2C projection type;
  - `astrology_full_data_v1` cannot appear in public `app.openapi()` output;
  - `astrology_full_data_v1` cannot be registered as a public route in `app.routes`;
  - `admin_chart_diagnostics_v1` cannot be merged into this expert astrology projection;
  - raw debug traces, replay payloads and provider dumps cannot enter the contract;
  - `ASTRO_EXPERT` cannot become an active backend role through this story.
- Guard mechanism:
  - targeted `rg` checks for required contract terms and denied public wording;
  - `app.routes`, `app.openapi()` and `TestClient` neutrality checks;
  - scoped `git status --short` for application roots;
  - persisted evidence under the CS-274 evidence folder.
- Guard owner:
  - `docs/architecture/astrology-full-data-v1-contract.md`;
  - `backend/tests/unit/test_astrology_full_data_contract.py`;
  - `_condamad/stories/CS-274-astrology-full-data-v1-internal-expert-projection/evidence/validation.txt`.
- Guard evidence:
  - `rg -n "astrology_full_data_v1|expert astro|interne|diagnostics|structured_facts" .\docs .\_story_briefs`;
  - `python -c "from app.main import app; assert 'astrology_full_data_v1' not in str(app.openapi())"`;
  - `python -c "from app.main import app; assert all('astrology_full_data' not in getattr(r, 'path', '') for r in app.routes)"`;
  - `git status --short -- backend/app frontend/src`.

## Regression Guardrails

Scope vector:

- backend-domain contract documentation: yes;
- projection primitive registry: yes;
- internal admin/expert access policy: yes;
- privacy masking policy: yes;
- public OpenAPI runtime exposure: read-only;
- frontend implementation: no;
- DB, auth implementation, i18n, style, build and migration: no.

Selected guardrails:

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend API ownership remains untouched by the documentation story. | scoped `git status`; `python`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Validation evidence must stay targeted and executable. | `rg`; targeted `pytest`. |
| Registry gap | No exact `astrology_full_data_v1` guardrail exists in resolver output. | Story-local OpenAPI and diagnostics guards. |

Non-applicable examples:

- RG-041 entitlement documentation is out of scope because this story uses admin permissions, not product entitlement docs.
- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 frontend CSS namespace migration is out of scope because no style or build output is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Contract document | `docs/architecture/astrology-full-data-v1-contract.md` | Keep the canonical internal full astrology projection contract. |
| Validation output | `_condamad/stories/CS-274-astrology-full-data-v1-internal-expert-projection/evidence/validation.txt` | Keep validation transcript. |
| Application surface status | `_condamad/stories/CS-274-astrology-full-data-v1-internal-expert-projection/evidence/app-surface-status.txt` | Prove app roots stayed untouched. |
| Source checklist | `_condamad/stories/CS-274-astrology-full-data-v1-internal-expert-projection/evidence/source-checklist.md` | Record source coverage. |
| Review output | `_condamad/stories/CS-274-astrology-full-data-v1-internal-expert-projection/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this internal projection contract story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/astrology-full-data-v1-contract.md` - define the canonical internal full astrology projection contract.
- `docs/architecture/official-product-primitives-public-projections.md` - register or align the projection without public client exposure.
- `backend/tests/unit/test_astrology_full_data_contract.py` - cover document content, diagnostics separation and runtime neutrality.
- `_condamad/stories/CS-274-astrology-full-data-v1-internal-expert-projection/evidence/validation.txt` - persist validation output.
- `_condamad/stories/CS-274-astrology-full-data-v1-internal-expert-projection/evidence/app-surface-status.txt` - persist scoped status output.
- `_condamad/stories/CS-274-astrology-full-data-v1-internal-expert-projection/evidence/source-checklist.md` - persist source coverage.

Likely tests:

- `backend/tests/unit/test_astrology_full_data_contract.py` - contract, masking, diagnostics separation and runtime-neutrality checks.
- `backend/tests/architecture/test_api_contract_neutrality.py` - existing public OpenAPI forbidden-token guard remains relevant.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no persistence schema is created.
- `backend/app/api/**` - out of scope; no route path, router registration or auth dependency is touched.
- `backend/app/core/security.py` - out of scope; no token or auth behavior is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `rg -n "astrology_full_data_v1|expert astro|interne|diagnostics|structured_facts" .\docs .\_story_briefs`
- VC2: `rg -n "astrology_full_data_v1|internal|interne|protected|expert|non client" docs/architecture/astrology-full-data-v1-contract.md`
- VC3: `rg -n "ADMIN|ASTRO_EXPERT|target-only|CS-271|permission matrix" docs/architecture/astrology-full-data-v1-contract.md`
- VC4: `rg -n "admin_chart_diagnostics_v1|debug|diagnostics|replay|trace" docs/architecture/astrology-full-data-v1-contract.md`
- VC5: `rg -n "positions|houses|dignities|conditions|aspects|dominance|fixed-star" docs/architecture/astrology-full-data-v1-contract.md`
- VC6: `rg -n "birth date|birth time|birth place|user id|chart id|mask" docs/architecture/astrology-full-data-v1-contract.md`
- VC7: `rg -n "structured_facts_v1|source versions|doctrine|school|evidence refs" docs/architecture/astrology-full-data-v1-contract.md`
- VC8: `rg -n "actor|role|projection id|action|decision|correlation" docs/architecture/astrology-full-data-v1-contract.md`
- VC9: `pytest -q backend/tests/unit/test_astrology_full_data_contract.py`
- VC10: `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`
- VC11: `python -c "from app.main import app; assert 'astrology_full_data_v1' not in str(app.openapi())"`
- VC12: `python -c "from app.main import app; assert all('astrology_full_data' not in getattr(r, 'path', '') for r in app.routes)"`
- VC13: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-274-astrology-full-data-v1-internal-expert-projection/evidence/validation.txt').exists()"`
- VC14: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-274-astrology-full-data-v1-internal-expert-projection/evidence/app-surface-status.txt').exists()"`
- VC15: `git status --short -- backend/app frontend/src`
- VC16: `ruff format .`
- VC17: `ruff check .`
- VC18: `pytest -q`

Before VC9 through VC14, VC16, VC17 and VC18, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The full astrology projection may be confused with technical diagnostics or replay/debug payloads.
- `ASTRO_EXPERT` may be interpreted as an active role instead of target-only vocabulary.
- B2C clients may receive full expert astrology data through a generic projection path.
- Birth date/time/place or identifiers may be exposed without masking or documented justification.
- Fixed-star data may be exposed to clients before a separate product policy authorizes it.
- Source versions and `structured_facts_v1` dependencies may be omitted, weakening auditability.
- Application files may change while trying to prove a documentation and contract story.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the Python virtual environment before every Python command.
- Keep backend runtime behavior unchanged.
- Keep existing route paths, router registrations, public OpenAPI output and frontend source unchanged.
- Keep `ASTRO_EXPERT` out of active backend role constants.
- Keep B2C clients denied for `astrology_full_data_v1`.
- Keep `admin_chart_diagnostics_v1` separate from full astrology expert data.
- Persist validation output under the CS-274 evidence folder before requesting review.

## References

- `_story_briefs/cs-274-define-astrology-full-data-v1-internal-expert-projection.md`
- `docs/architecture/official-product-primitives-public-projections.md`
- `docs/architecture/product-architecture-current-state-2026-05-24.md`
- `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md`
- `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md`
- `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/00-story.md`
- `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/00-story.md`
- `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/00-story.md`
- `backend/app/main.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `_condamad/stories/regression-guardrails.md`
