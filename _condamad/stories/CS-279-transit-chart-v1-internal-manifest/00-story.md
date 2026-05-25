# Story CS-279 transit-chart-v1-internal-manifest: Define transit_chart_v1 Internal Manifest
Status: done

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-279-define-transit-chart-v1-internal-manifest.md`.
- Required dependency: CS-250 astronomical proof before public temporal runtime.
- Required dependency: CS-252 astrology doctrine school governance model.
- Prior decision: CS-253 selected `transit_chart_v1` as the first temporal family without public exposure.
- Existing owner found: `backend/app/domain/astrology/runtime/temporal_technique_selection.py` already owns the selected temporal path.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: `transit_chart_v1` needs one internal manifest before runtime work, while public exposure remains blocked.
- Source-alignment evidence: PASS; this story preserves internal manifest, proof dependencies, doctrine limits, traces and public denial.

## Objective

Define one canonical backend-domain manifest for `transit_chart_v1` as an internal runtime preparation contract.

The implementation must reuse the existing temporal selection owner, document inputs, outputs, astronomical proof dependencies,
doctrine limits, trace requirements and follow-up runtime stories, without adding a public route, frontend surface or product promise.

## Target State

- `transit_chart_v1` has one internal manifest represented by a typed backend-domain contract.
- The manifest names required inputs: natal chart reference, transit date or bounded period, timezone, location policy and proof reference.
- The manifest names internal outputs: transiting chart objects, transit-to-natal relationships, diagnostic trace keys and blocked public status.
- The manifest lists CS-250 astronomical proof prerequisites before public temporal runtime claims.
- The manifest lists CS-252 doctrine prerequisites before doctrine-heavy transit interpretation or forecasting semantics.
- The manifest records trace requirements without implying replay storage, public API availability or frontend consumption.
- Public exposure is explicitly blocked through runtime-neutrality tests using `app.routes`, `app.openapi()`, `pytest` and `TestClient`.
- Future runtime stories are identified as internal graph manifest, calculation runner integration, projection contract and public API gate work.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-279-define-transit-chart-v1-internal-manifest.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-279`.
- Evidence 3: `backend/app/domain/astrology/runtime/temporal_technique_selection.py` - existing temporal selection owner found.
- Evidence 4: `docs/architecture/product-architecture-current-state-2026-05-24.md` - current state says `transit_chart_v1` is selected and non-public.
- Evidence 5: `_condamad/stories/CS-253-first-temporal-technique-implementation-path/00-story.md` - dependency story confirms non-public selection.
- Evidence 6: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output only.
- Evidence 7: `resolve_guardrails.py` - scoped resolver run for backend-domain, manifest, internal-contract and public-exposure-block scope.
- Repository structure alert: backend, backend/app, backend/tests, frontend, frontend/src and docs exist in this workspace.
- Source-alignment evidence: PASS; no brief criterion was replaced by public API, frontend, product copy or runtime implementation work.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Internal backend-domain manifest for `transit_chart_v1`.
  - Reuse of `temporal_technique_selection.py` as the selected temporal path owner.
  - Input, output, proof, doctrine, trace and follow-up story definitions.
  - Runtime-neutrality proof with `app.routes`, `app.openapi()`, `TestClient`, `pytest`, targeted `rg` and scoped `git status`.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling, migrations, seeds, generated clients and public API changes.
  - Transit calculation algorithms, projection builders, client projections, commercial promise, replay storage and durable cache.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation or UI validation.
  - No public endpoint, public serializer, OpenAPI schema, generated client or product-facing transit promise.
  - No transit calculation runner, projection builder, DB model, migration, replay snapshot or durable cache.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits an internal backend-domain manifest for a non-public temporal runtime path.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the canonical internal `transit_chart_v1` manifest contract, targeted tests and story evidence artifacts.
  - Extend or reuse `temporal_technique_selection.py` rather than creating a parallel temporal selection owner.
  - Keep backend API routes, OpenAPI output, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Keep public exposure blocked until proof, doctrine, projection and API gate stories explicitly authorize it.
  - Keep trace requirements redacted and separate from replay storage.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product asks for public transit exposure before proof, doctrine, projection and API gate closure.
- Additional validation rules:
  - The manifest must name `transit_chart_v1` exactly.
  - The manifest must state that the contract is internal, non-public and blocked from public exposure.
  - The manifest must define internal inputs and outputs.
  - The manifest must list CS-250 astronomical proof prerequisites.
  - The manifest must list CS-252 doctrine prerequisites.
  - The manifest must define trace keys without replay storage.
  - The manifest must identify follow-up runtime stories without implementing them.
  - `app.routes`, `app.openapi()`, `TestClient`, `pytest`, `python`, `rg` and scoped `git status` must prove runtime neutrality.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Manifest tests, `app.routes`, `app.openapi()` and `TestClient` prove internal behavior and no public exposure. |
| Baseline Snapshot | yes | Before and after artifacts prove the only allowed surface delta is manifest, tests and story evidence. |
| Ownership Routing | yes | Manifest ownership must stay in backend astrology runtime, not API, frontend, DB or prediction owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this internal manifest story. |
| Contract Shape | yes | The manifest has exact family code, status, inputs, outputs, proof, doctrine, trace and follow-up fields. |
| Batch Migration | no | No batch migration, public rollout or multi-family conversion is in scope. |
| Reintroduction Guard | yes | Public routes, OpenAPI exposure, frontend and runtime shortcut paths must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The internal manifest exists. | Evidence profile: baseline_before_after_diff; `pytest -q backend/tests/unit/domain/astrology/test_transit_chart_manifest.py`; AST guard. |
| AC2 | `transit_chart_v1` is the manifest family. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_transit_chart_manifest.py`. |
| AC3 | Internal inputs are declared. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_transit_chart_manifest.py`. |
| AC4 | Internal outputs are declared. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_transit_chart_manifest.py`. |
| AC5 | Proof prerequisites are listed. | Evidence profile: json_contract_shape; `pytest`; `rg` checks CS-250 and proof wording. |
| AC6 | Doctrine prerequisites are listed. | Evidence profile: json_contract_shape; `pytest`; `rg` checks CS-252 and doctrine wording. |
| AC7 | Trace requirements are bounded. | Evidence profile: json_contract_shape; `pytest`; `rg` checks trace and replay wording. |
| AC8 | Public API runtime is unchanged. | Evidence profile: runtime_openapi_contract; `pytest`; `TestClient`; `app.routes`; `app.openapi()`. |
| AC9 | Future runtime stories are identified. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_transit_chart_manifest.py`; AST guard. |
| AC10 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-279 evidence paths. |

## Implementation Tasks

- [x] Task 1: Inspect the brief, current architecture document and CS-253 temporal selection owner before edits. (AC: AC1, AC2)
- [x] Task 2: Create or extend the canonical backend-domain manifest module with French file comment and docstrings. (AC: AC1)
- [x] Task 3: Encode `transit_chart_v1` as the exact internal manifest family code. (AC: AC2)
- [x] Task 4: Define internal inputs for natal source, transit target time, timezone, location policy and proof reference. (AC: AC3)
- [x] Task 5: Define internal outputs for transiting objects, transit-to-natal relationships, diagnostics and blocked exposure status. (AC: AC4)
- [x] Task 6: Attach CS-250 proof prerequisites and CS-252 doctrine prerequisites to the manifest. (AC: AC5, AC6)
- [x] Task 7: Define trace keys with redaction boundaries and no replay storage claim. (AC: AC7)
- [x] Task 8: Add manifest tests and reuse API neutrality tests with `app.routes`, `app.openapi()` and `TestClient`. (AC: AC2, AC8)
- [x] Task 9: Record follow-up runtime stories for graph manifest, runner integration, projection contract and API gate. (AC: AC9)
- [x] Task 10: Persist validation, manifest snapshot and application-surface evidence under the CS-279 folder. (AC: AC10)

## Files to Inspect First

- `_story_briefs/cs-279-define-transit-chart-v1-internal-manifest.md` - source brief.
- `backend/app/domain/astrology/runtime/temporal_technique_selection.py` - existing selected temporal path owner.
- `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py` - existing graph family registry owner.
- `backend/app/domain/astrology/runtime/astronomical_proof.py` - CS-250 proof gate implementation owner.
- `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py` - CS-252 doctrine governance implementation owner.
- `_condamad/stories/CS-253-first-temporal-technique-implementation-path/00-story.md` - selected non-public temporal path contract.
- `_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/00-story.md` - proof prerequisite contract.
- `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/00-story.md` - doctrine prerequisite contract.
- `docs/architecture/product-architecture-current-state-2026-05-24.md` - architecture current-state source for transit status.
- `backend/tests/architecture/test_api_contract_neutrality.py` - existing public exposure guard owner.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output only.

## Runtime Source of Truth

- Primary source of truth:
  - `backend/app/domain/astrology/runtime/temporal_technique_selection.py` for selected temporal path ownership.
  - `backend/app/domain/astrology/runtime/transit_chart_manifest.py` for the new internal manifest contract.
  - `backend/app/domain/astrology/runtime/astronomical_proof.py` for proof gate vocabulary.
  - `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py` for doctrine governance vocabulary.
  - `app.routes`, `app.openapi()`, `TestClient`, `pytest`, scoped `git status` and targeted `rg` scans for runtime neutrality.
- Runtime/domain artifacts:
  - family code;
  - internal exposure status;
  - input descriptors;
  - output descriptors;
  - proof prerequisites;
  - doctrine prerequisites;
  - trace descriptors;
  - follow-up story descriptors.
- Secondary evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_transit_chart_manifest.py`.
  - `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`.
  - targeted `rg` scans for public transit surfaces and manifest fields.
- Static scans alone are not sufficient because:
  - manifest construction and public API neutrality must be proven from executable tests and the loaded app.

## Contract Shape

- Contract type:
  - internal backend-domain manifest for `transit_chart_v1`;
  - no HTTP endpoint, public serializer, OpenAPI schema or frontend type.
- Fields:
  - `family_code`: exact value `transit_chart_v1`.
  - `classification`: internal and non-public.
  - `public_exposure_status`: blocked until proof, doctrine, projection and API gates are closed.
  - `inputs`: natal chart source, transit target datetime or bounded period, timezone, location policy and proof reference.
  - `outputs`: transiting objects, transit-to-natal relationships, diagnostic trace keys and blocked public status.
  - `proof_prerequisites`: CS-250 proof gate, ephemeris source metadata, tolerance posture and evidence artifact reference.
  - `doctrine_prerequisites`: CS-252 doctrine owner, school policy, rule source ownership and unresolved decision markers.
  - `trace_requirements`: run id, graph code, graph version, node status, redacted input and output keys.
  - `follow_up_runtime_stories`: graph manifest, calculation runner, projection contract and API gate work.
- Required fields:
  - `family_code`
  - `classification`
  - `public_exposure_status`
  - `inputs`
  - `outputs`
  - `proof_prerequisites`
  - `doctrine_prerequisites`
  - `trace_requirements`
  - `follow_up_runtime_stories`
- Optional fields:
  - none.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - internal evidence artifacts use snake_case field names.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose `transit_chart_v1` from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-279-define-transit-chart-v1-internal-manifest.md`
  - `backend/app/domain/astrology/runtime/temporal_technique_selection.py`
  - `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py`
  - `docs/architecture/product-architecture-current-state-2026-05-24.md`
  - `_condamad/stories/CS-253-first-temporal-technique-implementation-path/00-story.md`
- Comparison after implementation:
  - `backend/app/domain/astrology/runtime/transit_chart_manifest.py`
  - `backend/tests/unit/domain/astrology/test_transit_chart_manifest.py`
  - `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/manifest-after.json`
  - `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/api-neutrality.md`
  - `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/validation.txt`
- Expected invariant:
  - The only intended repository delta is one internal manifest contract, targeted tests and story evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Transit internal manifest | `backend/app/domain/astrology/runtime/transit_chart_manifest.py` | API routers or frontend clients |
| Temporal selection owner | `backend/app/domain/astrology/runtime/temporal_technique_selection.py` | duplicate temporal selector |
| Graph family registry | `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py` | manifest-only registry copy |
| Astronomical proof gate | `backend/app/domain/astrology/runtime/astronomical_proof.py` | public API shortcut |
| Doctrine governance | `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py` | transit manifest as doctrine owner |
| API neutrality proof | `backend/tests/architecture/test_api_contract_neutrality.py` | public route tests only |
| Story evidence artifacts | `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse `temporal_technique_selection.py` as the selected temporal path owner.
- Reuse the graph family registry instead of creating a second `transit_chart_v1` registry.
- Reuse CS-250 proof gate vocabulary instead of inventing a parallel proof policy.
- Reuse CS-252 doctrine governance vocabulary instead of declaring transit-specific doctrine ownership.
- Reuse CS-248 trace vocabulary for redacted graph trace keys.
- Keep one canonical manifest module and one manifest family code.
- Do not add external packages, generated clients, builders, services, routes, serializers or database objects.

## No Legacy / Forbidden Paths

- No legacy transit manifest path may be added outside the canonical astrology runtime owner.
- No compatibility route path may expose `transit_chart_v1` publicly.
- No fallback branch may bypass CS-250 proof or CS-252 doctrine gates.
- Do not create aliases, shims, compatibility wrappers or parallel manifest documents.
- Do not promote existing prediction temporal code as the canonical transit runtime path.
- Do not add a public API route, serializer, OpenAPI schema, frontend file, DB model, seed or migration.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/**`
  - `backend/app/infra/db/**`
  - `backend/migrations/**`
  - generated OpenAPI clients
  - public transit projection contracts

## Reintroduction Guard

- Guard target:
  - `transit_chart_v1` remains internal and non-public;
  - `transit_chart_v1` cannot appear in public `app.openapi()` output;
  - `transit_chart_v1` cannot be registered as a public route in `app.routes`;
  - CS-250 proof and CS-252 doctrine gates cannot be bypassed;
  - trace requirements cannot become replay storage or public diagnostics.
- Guard mechanism:
  - targeted unit tests for manifest fields and gate references;
  - architecture tests proving API neutrality;
  - targeted `rg` scans for public route, UI and migration surfaces;
  - `TestClient`, `app.routes` and `app.openapi()` runtime neutrality evidence;
  - scoped `git status --short` for application roots.
- Guard owner:
  - `backend/tests/unit/domain/astrology/test_transit_chart_manifest.py`;
  - `backend/tests/architecture/test_api_contract_neutrality.py`;
  - `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/validation.txt`.
- Guard evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_transit_chart_manifest.py`;
  - `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`;
  - `python -c "from app.main import app; assert 'transit_chart_v1' not in str(app.openapi())"`;
  - `python -c "from app.main import app; assert all('transit' not in getattr(r, 'path', '') for r in app.routes)"`;
  - `rg -n "transit_chart_v1|transit_chart|transits" backend/app/api frontend/src backend/migrations`.

## Regression Guardrails

Scope vector:

- backend-domain manifest: yes;
- astrology runtime contract: yes;
- public API runtime exposure: read-only;
- backend tests: yes;
- frontend implementation: no;
- DB, auth implementation, i18n, style, build and migration: no.

Selected guardrails:

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `Routeurs API v1` | Backend API ownership remains untouched by the manifest story. | scoped `git status`; `python`. |
| RG-022 `Plans de validation des stories prompt-generation` | Validation evidence must stay targeted and executable. | `rg`; targeted `pytest`. |
| Registry gap | No exact `transit_chart_v1` manifest guardrail exists in resolver output. | Story-local manifest and API guards. |

Non-applicable examples:

- RG-041 entitlement documentation is out of scope because no product entitlement surface is touched.
- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 frontend CSS namespace migration is out of scope because no style or build output is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Manifest snapshot | `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/manifest-after.json` | Keep the internal manifest payload. |
| API neutrality | `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/api-neutrality.md` | Prove routes and OpenAPI stay non-public. |
| Validation output | `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/validation.txt` | Keep validation transcript. |
| Application surface status | `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/app-surface-status.txt` | Prove scoped app roots stayed controlled. |
| Source checklist | `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/source-checklist.md` | Record source coverage. |
| Review output | `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this internal manifest story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/transit_chart_manifest.py` - define the canonical internal manifest contract.
- `backend/app/domain/astrology/runtime/__init__.py` - export manifest helpers from the existing runtime package.
- `backend/tests/unit/domain/astrology/test_transit_chart_manifest.py` - cover manifest content and gate references.
- `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/manifest-after.json` - persist manifest payload.
- `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/api-neutrality.md` - persist runtime neutrality proof.
- `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/validation.txt` - persist validation output.
- `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/app-surface-status.txt` - persist scoped status output.
- `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/source-checklist.md` - persist source coverage.

Likely tests:

- `backend/tests/unit/domain/astrology/test_transit_chart_manifest.py` - manifest, proof, doctrine, trace and follow-up checks.
- `backend/tests/architecture/test_api_contract_neutrality.py` - existing public OpenAPI and route neutrality checks.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no route path, router registration or auth dependency is touched.
- `backend/app/infra/**` - out of scope; no persistence or external adapter is touched.
- `backend/migrations/**` - out of scope; no database migration is touched.
- `docs/db_seeder/**` - out of scope; no seed artifact is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `rg -n "transit_chart_v1|internal|non-public|blocked|CS-250|CS-252" backend/app/domain/astrology/runtime backend/tests`
- VC2: `rg -n "natal_chart|target_date|timezone|location|proof" backend/app/domain/astrology/runtime/transit_chart_manifest.py`
- VC3: `rg -n "transiting|relationship|diagnostic|trace|replay" backend/app/domain/astrology/runtime/transit_chart_manifest.py`
- VC4: `rg -n "graph manifest|runner|projection contract|API gate" backend/app/domain/astrology/runtime/transit_chart_manifest.py`
- VC5: `pytest -q backend/tests/unit/domain/astrology/test_transit_chart_manifest.py`
- VC6: `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`
- VC7: `python -c "from app.main import app; assert 'transit_chart_v1' not in str(app.openapi())"`
- VC8: `python -c "from app.main import app; assert all('transit' not in getattr(r, 'path', '') for r in app.routes)"`
- VC9: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/manifest-after.json').exists()"`
- VC10: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-279-transit-chart-v1-internal-manifest/evidence/validation.txt').exists()"`
- VC11: `rg -n "transit_chart_v1|transit_chart|transits" backend/app/api frontend/src backend/migrations`
- VC12: `git status --short -- backend/app frontend/src backend/migrations`
- VC13: `ruff format .`
- VC14: `ruff check .`
- VC15: `pytest -q`

Before VC5 through VC10, VC13, VC14 and VC15, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The internal manifest may be mistaken for a public API contract.
- Existing prediction temporal code may become a second canonical transit owner.
- CS-250 proof requirements may be softened into a generic confidence statement.
- CS-252 doctrine ownership may be bypassed by embedding transit interpretation policy in the manifest.
- Trace requirements may drift into replay storage or raw public diagnostics.
- A frontend or OpenAPI surface may be introduced while documenting the internal manifest.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the Python virtual environment before every Python command.
- Keep backend runtime behavior public-neutral.
- Keep existing route paths, router registrations, public OpenAPI output and frontend source unchanged.
- Reuse `temporal_technique_selection.py` and existing proof or doctrine modules instead of creating parallel owners.
- Keep `transit_chart_v1` internal and non-public.
- Persist validation output under the CS-279 evidence folder before requesting review.

## References

- `_story_briefs/cs-279-define-transit-chart-v1-internal-manifest.md`
- `_condamad/stories/story-status.md`
- `backend/app/domain/astrology/runtime/temporal_technique_selection.py`
- `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py`
- `backend/app/domain/astrology/runtime/astronomical_proof.py`
- `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py`
- `_condamad/stories/CS-253-first-temporal-technique-implementation-path/00-story.md`
- `_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/00-story.md`
- `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/00-story.md`
- `docs/architecture/product-architecture-current-state-2026-05-24.md`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `_condamad/stories/regression-guardrails.md`
