# Story CS-251 official-product-primitives-public-projection-roadmap: Define Official Product Primitives And Public Projection Roadmap
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-251-official-product-primitives-public-projection-roadmap.md`.
- Related audits: CS-238 states `chart_objects` and `ChartObjectRuntimeData` stay internal raw runtime surfaces.
- Related audit: CS-244 maps beginner, expert, astrologer, debug, AI interpretation, PDF, and public-user product data needs.
- Related dependency: CS-249 defines the chart object capability taxonomy used to reason about public projection eligibility.
- Related dependency: CS-250 blocks public temporal runtime promotion without astronomical proof.
- Remapped architecture item: `SC-ARCH-005`.
- Problem statement: decide official product primitives and public projection sequencing without exposing raw runtime payloads.
- Source-alignment evidence: PASS; all CS-244 audiences, fixed-star policy, raw-runtime bans, OpenAPI compatibility, and roadmap split are preserved.

## Objective

Define one canonical product primitive and projection roadmap document for astrology public data surfaces.

The implementation must name approved public primitives, reject internal-only runtime surfaces for public exposure, decide or block fixed-star exposure policy,
and produce a sequenced roadmap that separates API contracts, frontend clients, and UI components.

## Target State

- Official product primitives are documented with one canonical owner, audience, exposure level, and public contract status.
- `chart_objects`, `ChartObjectRuntimeData`, raw calculation graph payloads, and `interpretation_input` remain internal or LLM-only surfaces.
- Beginner, expert, astrologer, debug, AI interpretation, PDF, and public-user needs from CS-244 map to a named primitive or explicit product rejection.
- Fixed-star contacts are classified as public, gated, or `needs-user-decision` with exact consequence for CS-257.
- Future implementation stories are sequenced by API contract, frontend client, and UI component surface.
- Public projection plans remain compatible with FastAPI OpenAPI generation through `app.openapi()` and registered routes through `app.routes`.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-251-official-product-primitives-public-projection-roadmap.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to convert `CS-251` from `brief-ready` to `ready-to-dev`.
- Evidence 3: `_condamad/stories/CS-238-audit-runtime-surface-exposure/00-story.md` - raw runtime exposure decision source.
- Evidence 4: `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919/00-audit-report.md` - exposure matrix source.
- Evidence 5: `_condamad/stories/CS-244-audit-product-data-needs/00-story.md` - product data needs audit contract source.
- Evidence 6: `_condamad/audits/astro-product-data-needs/2026-05-23-2024/00-audit-report.md` - audience and screen needs source.
- Evidence 7: `_condamad/audits/astro-product-data-needs/2026-05-23-2024/03-story-candidates.md` - CS-255 through CS-257 roadmap source.
- Evidence 8: `backend/tests/integration/astrology/test_natal_public_contract_compatibility.py` - existing public contract guard exists.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped guardrail resolver output.

## Domain Boundary

- Domain: backend-product-contract
- In scope:
  - Product primitive governance for astrology public projections.
  - Canonical decision document for structured facts, beginner summary, expert projection, fixed-star contacts, astrologer/debug data, and LLM input.
  - Roadmap entries that split API contract, frontend client, and UI component work.
  - Backend architecture guards or tests preventing raw runtime exposure through public API or frontend-facing contracts.
  - OpenAPI-neutrality or OpenAPI-readiness evidence through `app.openapi()`, `app.routes`, `pytest`, and `TestClient`.
- Out of scope:
  - Frontend UI implementation, generated client changes, database schema, auth, i18n implementation, styling, build tooling, and migrations.
  - Direct public exposure of `chart_objects`, `ChartObjectRuntimeData`, raw calculation graph nodes, or raw `interpretation_input`.
  - LLM narration creation, temporal technique implementation, new calculators, and PDF rendering changes.
- Explicit non-goals:
  - No frontend route, screen, component, CSS, or browser validation.
  - No endpoint implementation or serializer expansion beyond guard-ready product contract documentation.
  - No temporal public runtime promotion.
  - No registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend product primitive and public projection roadmap contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add one canonical product primitive roadmap and targeted guards only.
  - Keep public API payloads unchanged unless a guard records the current public non-exposure contract.
  - Keep frontend, DB, auth, i18n, style, build, migrations, calculators, and LLM narration unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: fixed-star contacts or astrologer/debug surfaces cannot be classified without a product exposure decision.
- Additional validation rules:
  - Every CS-244 audience need maps to a named projection, a rejected public surface, or `needs-user-decision`.
  - `chart_objects` and `ChartObjectRuntimeData` are forbidden as public primitives.
  - `interpretation_input` is classified as non-public LLM input, not frontend API payload.
  - Fixed-star contacts must be classified as public, gated, or `needs-user-decision`.
  - Roadmap rows must separate API contract, frontend client, and UI component work.
  - `app.openapi()`, `app.routes`, `pytest`, and `TestClient` must prove no raw runtime API exposure.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Product primitive decisions must cite audits, architecture docs, API tests, `app.routes`, and `app.openapi()`. |
| Baseline Snapshot | yes | Before and after evidence must show governance and guard delta without public payload drift. |
| Ownership Routing | yes | Product contract docs, backend guards, API contracts, frontend clients, and UI components need separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for product primitive governance. |
| Contract Shape | yes | The roadmap has exact primitive fields, exposure statuses, audience mappings, and sequencing columns. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Raw runtime surfaces must stay out of public API and frontend-facing contracts. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Official primitives are documented. | Evidence profile: json_contract_shape; `rg` checks the roadmap document for required primitive names. |
| AC2 | Every CS-244 audience is mapped. | Evidence profile: baseline_before_after_diff; `rg` checks beginner, expert, astrologer, debug, AI, PDF, and public-user rows. |
| AC3 | Internal surfaces are rejected. | Evidence profile: no_legacy_contract; `pytest -q backend/tests/integration/astrology/test_natal_public_contract_compatibility.py` |
| AC4 | Fixed-star exposure policy is explicit. | Evidence profile: json_contract_shape; `rg` checks fixed-star policy and `needs-user-decision` markers. |
| AC5 | Roadmap splits implementation layers. | Evidence profile: baseline_before_after_diff; `rg` checks API contract, frontend client, and UI component roadmap columns. |
| AC6 | Public projection remains OpenAPI-ready. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`; `TestClient` stays usable. |
| AC7 | Raw runtime exposure cannot reappear. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py`. |
| AC8 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-251 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Create the canonical product primitive roadmap with French file comment and concise governance notes. (AC: AC1)
- [ ] Task 2: Define structured facts, beginner summary, expert projection, fixed-star contacts, astrologer/debug data, and LLM input. (AC: AC1, AC2)
- [ ] Task 3: Map every CS-244 audience to an approved projection, rejected public surface, or `needs-user-decision`. (AC: AC2)
- [ ] Task 4: Record `chart_objects`, `ChartObjectRuntimeData`, raw graph payloads, and `interpretation_input` as non-public raw surfaces. (AC: AC3)
- [ ] Task 5: Decide fixed-star public or gated policy, or record the exact user decision blocker. (AC: AC4)
- [ ] Task 6: Write the roadmap with separate API contract, frontend client, and UI component story rows. (AC: AC5)
- [ ] Task 7: Add or reuse backend architecture guards proving raw runtime names stay out of public contracts. (AC: AC3, AC7)
- [ ] Task 8: Add OpenAPI/readiness proof using `app.openapi()`, `app.routes`, `pytest`, and `TestClient`. (AC: AC6)
- [ ] Task 9: Persist roadmap, validation, OpenAPI, route, and guard evidence under the CS-251 evidence folder. (AC: AC8)

## Files to Inspect First

- `_story_briefs/cs-251-official-product-primitives-public-projection-roadmap.md` - source contract.
- `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919/00-audit-report.md` - raw runtime exposure decisions.
- `_condamad/audits/astro-product-data-needs/2026-05-23-2024/00-audit-report.md` - CS-244 audience and screen needs.
- `_condamad/audits/astro-product-data-needs/2026-05-23-2024/03-story-candidates.md` - roadmap candidates CS-255 through CS-257.
- `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/00-story.md` - capability taxonomy dependency.
- `_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/00-story.md` - temporal public runtime gate.
- `docs/architecture/astrology-runtime-surfaces.md` - existing runtime surface architecture source.
- `backend/app/services/chart/json_builder.py` - current public natal projection owner.
- `backend/app/api/v1/routers/public/natal_interpretation.py` - public interpretation and PDF route owner.
- `backend/tests/integration/astrology/test_natal_public_contract_compatibility.py` - public non-exposure guard.
- `backend/tests/architecture/test_chart_runtime_surface_guardrails.py` - runtime boundary guard.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - CS-238 and CS-244 audit artifacts, `docs/architecture/astrology-runtime-surfaces.md`, `AST guard`, `app.routes`, `app.openapi()`, and `TestClient`.
- Secondary evidence:
  - Targeted `rg` scans for official primitive names, audience mappings, raw runtime ban terms, and roadmap layer columns.
- Static scans alone are not sufficient because:
  - Public API neutrality and runtime non-exposure must be proven from the loaded app and deterministic tests.

## Contract Shape

- Contract type:
  - backend product primitive governance document and public projection roadmap.
- Fields:
  - `primitive_id`: stable primitive identifier.
  - `audience`: beginner, expert, astrologer, debug, AI, PDF, or public-user.
  - `public_status`: public, gated, internal, LLM-only, rejected, or `needs-user-decision`.
  - `source_runtime`: current internal owner or audit source.
  - `public_projection_owner`: planned API projection owner or `none`.
  - `forbidden_raw_surfaces`: raw fields that must not be public.
  - `api_contract_story`: future API contract story or `none`.
  - `frontend_client_story`: future frontend client story or `none`.
  - `ui_component_story`: future UI component story or `none`.
  - `openapi_policy`: OpenAPI-ready, OpenAPI-neutral, or blocked.
- Required fields:
  - `primitive_id`
  - `audience`
  - `public_status`
  - `source_runtime`
  - `public_projection_owner`
  - `forbidden_raw_surfaces`
  - `api_contract_story`
  - `frontend_client_story`
  - `ui_component_story`
  - `openapi_policy`
- Required primitive decisions:
  - structured facts
  - beginner summary
  - expert technical projection
  - fixed-star contacts
  - astrologer/debug data
  - LLM input
- Optional fields:
  - none.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - Future public schemas must use product primitive names, not raw runtime object names.
- Frontend type impact:
  - none in this story; future frontend client stories must consume only approved API contracts.
- Generated contract impact:
  - `app.openapi()` must not expose `chart_objects`, `ChartObjectRuntimeData`, raw graph payloads, or raw `interpretation_input`.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-251-official-product-primitives-public-projection-roadmap.md`
  - `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919/00-audit-report.md`
  - `_condamad/audits/astro-product-data-needs/2026-05-23-2024/00-audit-report.md`
  - `docs/architecture/astrology-runtime-surfaces.md`
- Comparison after implementation:
  - `docs/architecture/official-product-primitives-public-projections.md`
  - `_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap/evidence/validation.txt`
  - `_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap/evidence/openapi-routes.md`
- Expected invariant:
  - The only intended behavior delta is stronger governance and guards for product projection planning without raw runtime exposure.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Product primitive roadmap | `docs/architecture/official-product-primitives-public-projections.md` | `frontend/src/**` |
| Public projection guard | `backend/tests/integration/astrology/test_natal_public_contract_compatibility.py` | UI component tests only |
| Runtime boundary guard | `backend/tests/architecture/test_chart_runtime_surface_guardrails.py` | frontend scans only |
| Future API contract stories | `_condamad/stories/CS-255*`, `_condamad/stories/CS-256*`, `_condamad/stories/CS-257*` | one mixed implementation story |
| Story evidence artifacts | `_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse the exposure decisions from CS-238 and product needs from CS-244 instead of creating a second product matrix vocabulary.
- Reuse existing public projection owners, architecture guards, and public contract tests before adding new guard files.
- Use one canonical primitive identifier per product projection across docs, tests, roadmap, and future story names.
- Keep raw runtime names only in forbidden-surface columns, negative scans, and guard evidence.
- Do not add external packages or custom roadmap tooling.

## No Legacy / Forbidden Paths

- No legacy route path may be added for product primitive exposure.
- No compatibility route path may expose raw runtime payloads.
- No fallback branch may convert raw runtime data into public payloads.
- Do not create aliases, shims, compatibility wrappers, or parallel primitive registries.
- Do not expose `chart_objects`, `ChartObjectRuntimeData`, raw calculation graph payloads, or raw `interpretation_input` publicly.
- Do not modify frontend screens, CSS, DB migrations, seed data, auth, i18n, temporal calculators, or LLM narration.

## Reintroduction Guard

- Guard scope:
  - Raw runtime names must stay out of public API responses, OpenAPI schemas, frontend API contracts, and UI component data needs.
  - Future public projection work must use named product primitives and separated story layers.
- Deterministic guard:
  - `pytest -q backend/tests/integration/astrology/test_natal_public_contract_compatibility.py`
  - `pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py`
  - `python` checks `app.openapi()` and `app.routes` for forbidden raw runtime names.
  - `rg` checks roadmap fields and future story layer separation.
- Forbidden alternate route:
  - Do not satisfy the roadmap by exposing raw runtime payloads, adding a broad public serializer, or merging API, client, and UI work into one future story.

## Regression Guardrails

Scope vector:

- backend-product-contract: yes;
- public projection roadmap: yes;
- API/OpenAPI neutrality: yes;
- frontend implementation: no;
- DB/migration/auth/i18n/style/build: no;
- raw runtime exposure: forbidden.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | local | Backend API ownership stays separate from product roadmap governance. |
| RG-003 | local | Route architecture remains unchanged while public projection policy is defined. |

Registry gap:

- No exact official product primitive roadmap invariant was returned by the scoped resolver.
- No separate generic OpenAPI guardrail ID was found beyond RG-003 route and OpenAPI inventory proof.
- Do not enrich `_condamad/stories/regression-guardrails.md` during this normal story generation.

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 frontend CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is out of scope because astrology projection governance is the domain.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Product primitive roadmap | `docs/architecture/official-product-primitives-public-projections.md` | Keep official primitive decisions and projection roadmap. |
| Validation output | `_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap/evidence/validation.txt` | Keep lint, tests, and scan transcript. |
| OpenAPI route proof | `evidence/openapi-routes.md` | Keep `app.routes` and `app.openapi()` evidence. |
| Primitive snapshot | `evidence/product-primitives.json` | Keep machine-readable primitive decisions. |
| Review output | `generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this product primitive roadmap story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/official-product-primitives-public-projections.md` - canonical primitive and projection roadmap.
- `backend/tests/integration/astrology/test_natal_public_contract_compatibility.py` - public raw-runtime non-exposure guard.
- `backend/tests/architecture/test_chart_runtime_surface_guardrails.py` - architecture guard for raw runtime boundaries.
- `_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap/evidence/openapi-routes.md` - OpenAPI and route proof.
- `_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap/evidence/product-primitives.json` - primitive decision snapshot.

Likely tests:

- `backend/tests/integration/astrology/test_natal_public_contract_compatibility.py`
- `backend/tests/architecture/test_chart_runtime_surface_guardrails.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no public API route is added.
- `backend/app/domain/astrology/**` - out of scope unless a guard needs a read-only source reference.
- `backend/migrations/**` - out of scope; no database migration is touched.
- `docs/db_seeder/**` - out of scope; no seed artifact is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `ruff format backend`
- VC3: `ruff check backend`
- VC4: `pytest -q backend/tests/integration/astrology/test_natal_public_contract_compatibility.py`
- VC5: `pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py`
- VC6: `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`
- VC7: `pytest -q`
- VC8: `rg -n "structured facts|beginner summary|expert technical projection|fixed-star contacts|LLM input" docs/architecture`
- VC9: `rg -n "API contract|frontend client|UI component|needs-user-decision" docs/architecture/official-product-primitives-public-projections.md`
- VC10: `$env:PYTHONPATH='backend'; python -c "from app.main import app; assert 'ChartObjectRuntimeData' not in str(app.openapi())"`
- VC11: `$env:PYTHONPATH='backend'; python -c "from app.main import app; assert all('chart_objects' not in getattr(r, 'path', '') for r in app.routes)"`
- VC12: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap/evidence/validation.txt').exists()"`

Before VC2 through VC12, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- Product primitives may become a renamed mirror of raw runtime payloads.
- Beginner, expert, astrologer, debug, AI, PDF, and public-user audiences may be merged into one ambiguous public contract.
- Fixed-star contacts may be exposed before product decides public versus gated access.
- API, frontend client, and UI component work may be bundled into one broad future story.
- OpenAPI compatibility may be claimed from documentation without loaded-app proof.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all Python commands inside the activated venv.
- Treat CS-238 and CS-244 audit artifacts as the source of product and exposure decisions.
- Treat `chart_objects`, `ChartObjectRuntimeData`, raw graph payloads, and raw `interpretation_input` as forbidden public surfaces.
- Treat fixed-star contacts as blocked by explicit `needs-user-decision` until public or gated policy is selected.
- Keep frontend implementation, DB, auth, i18n, style, build, migrations, temporal techniques, calculators, and LLM narration out of scope.

## References

- `_story_briefs/cs-251-official-product-primitives-public-projection-roadmap.md`
- `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919/00-audit-report.md`
- `_condamad/audits/astro-product-data-needs/2026-05-23-2024/00-audit-report.md`
- `_condamad/audits/astro-product-data-needs/2026-05-23-2024/03-story-candidates.md`
- `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/00-story.md`
- `_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/00-story.md`
- `docs/architecture/astrology-runtime-surfaces.md`
- `backend/tests/integration/astrology/test_natal_public_contract_compatibility.py`
- `backend/tests/architecture/test_chart_runtime_surface_guardrails.py`
- `_condamad/stories/regression-guardrails.md`
