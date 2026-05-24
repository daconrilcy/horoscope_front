# Story CS-265 projection-versioning-incompatibility-policy: Define Projection Versioning And Incompatibility Policy
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-265-add-projection-versioning-and-incompatibility-policy.md`.
- Related dependency: CS-263 defines the generic projection endpoint contract and mandatory `projection_version` request semantics.
- Related dependency: CS-264 defines persisted projections, `projection_hash` and `source_versions` storage.
- Existing owner found: `docs/architecture/product-architecture-current-state-2026-05-24.md` already names versioning and invalidation.
- Existing owner found: `docs/architecture/official-product-primitives-public-projections.md` owns public projection governance.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: projection contracts need one explicit policy for version identity, source incompatibility and admin logging.
- Source-alignment evidence: PASS; ACs preserve mandatory versions, breaking-change v2 rules, blocking policy and no strong public stability promise.

## Objective

Define one canonical projection versioning and incompatibility policy document without changing projection builders, routes, models or persisted rows.

The implementation must document mandatory `projection_version`, breaking-change classification, unknown or deprecated version handling,
French deprecation wording such as `dépréciée`, `source_versions` incompatibility policy, recalculation or `recalcul` authorization,
admin logs and the accepted lack of strong backward compatibility before public stability.

## Target State

- A canonical architecture policy document defines `projection_version` as required for every projection contract and persisted projection.
- The policy defines which payload, semantic, source, masking, ordering or access changes force a new v2 projection contract.
- Unknown or deprecated projection versions are blocking outcomes and must be admin-logged by future runtime implementation.
- Incompatible `source_versions` are blocking unless the projection contract explicitly authorizes recalculation from approved canonical sources.
- The v1 to v2 transition is described as a new contract identity, not a silent mutation of v1 payload semantics.
- The policy states that strong backward compatibility is not promised while the product API is not stable or public B2B.
- Existing projection contracts, builders, persistence model, API route contracts, frontend and DB migrations remain unchanged.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-265-add-projection-versioning-and-incompatibility-policy.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-265`.
- Evidence 3: `_condamad/stories/CS-263-generic-projection-endpoint-contract/00-story.md` - endpoint dependency read.
- Evidence 4: `_condamad/stories/CS-264-projection-persistence-projection-hash/00-story.md` - persistence dependency read.
- Evidence 5: `docs/architecture/product-architecture-current-state-2026-05-24.md` - current versioning and invalidation owner found.
- Evidence 6: `docs/architecture/official-product-primitives-public-projections.md` - projection governance owner found.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output only.
- Source-alignment evidence: PASS; the story answers every brief AC without modifying existing projections.

## Domain Boundary

- Domain: backend-docs
- In scope:
  - Canonical architecture policy for projection versioning and incompatibility.
  - Mandatory `projection_version` rule for projection contracts and persisted projection rows.
  - Breaking-change taxonomy and v1 to v2 transition rule.
  - Unknown or deprecated version blocking policy and admin logging obligations.
  - `source_versions` incompatibility policy and recalculation authorization rule.
  - Negative checks proving no backend runtime, frontend, DB migration or public API behavior is changed by this story.
- Out of scope:
  - Frontend UI, database schema, auth implementation, i18n, styling, build tooling, migrations and generated clients.
  - Modifying existing projection payloads, builders, API routes, persistence model, historical rows or public B2B API contracts.
  - Maintaining five historical projection versions or performing any data migration.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No FastAPI route, `app.openapi()` path, response serializer or generated OpenAPI client change.
  - No database table, Alembic migration, projection row rewrite or historical backfill.
  - No silent mutation of a v1 projection contract to carry v2 semantics.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend documentation and policy contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the projection versioning and incompatibility policy document plus story evidence artifacts.
  - Reuse CS-263, CS-264 and existing architecture documents instead of creating a parallel projection governance system.
  - Keep backend runtime code, API routes, OpenAPI output, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Keep existing projection payloads and projection builders unchanged.
  - Treat a breaking v1 payload or semantic change as a new v2 contract identity.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product asks for strong backward compatibility or five-version historical support in this story.
- Additional validation rules:
  - The policy must state that `projection_version` is mandatory for every projection.
  - The policy must define breaking changes that force v2.
  - The policy must block unknown or deprecated versions and require admin logs.
  - The policy must block incompatible `source_versions` unless recalculation is explicitly authorized.
  - The policy must state that v1 cannot be silently mutated for breaking semantics.
  - `pytest`, `ruff`, `app.routes`, `app.openapi()` and scoped `git status` prove the intended documentation-only surface.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, `pytest` and scoped status prove documentation-only behavior. |
| Baseline Snapshot | yes | Before and after artifacts prove the only allowed surface delta is policy documentation and story evidence. |
| Ownership Routing | yes | Version policy, projection governance, endpoint contract and persistence contract need canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this projection policy story. |
| Contract Shape | yes | The policy has exact required topics: version, v2, deprecated versions, sources, recalculation and logs. |
| Batch Migration | no | No batch migration or data conversion is in scope. |
| Reintroduction Guard | yes | Silent v1 mutation, route drift, persistence drift and frontend drift must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `projection_version` is documented as mandatory. | Evidence profile: json_contract_shape; `rg` checks `projection_version` and mandatory wording in docs. |
| AC2 | Breaking changes force a v2 contract. | Evidence profile: json_contract_shape; `rg` checks `breaking`, `v1`, `v2` and silent mutation wording. |
| AC3 | Unknown versions are blocking. | Evidence profile: api_error_shape_contract; `rg` checks unknown-version blocking and admin log wording. |
| AC4 | Deprecated versions are blocking. | Evidence profile: api_error_shape_contract; `rg` checks deprecated or `dépréciée` blocking and admin log wording. |
| AC5 | Incompatible `source_versions` block use. | Evidence profile: json_contract_shape; `rg` checks `source_versions`, incompatible and recalculation policy. |
| AC6 | Recalculation requires authorization. | Evidence profile: json_contract_shape; `rg` checks recalculation or `recalcul` authorization in the policy document. |
| AC7 | Strong compatibility is not promised. | Evidence profile: external_usage_blocker; `rg` checks no strong backward compatibility and no public B2B stability. |
| AC8 | Existing runtime API surface stays unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`. |
| AC9 | Application source roots stay unchanged. | Evidence profile: repo_wide_negative_scan; `rg` checks policy terms outside app roots; scoped status. |
| AC10 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-265 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-263, CS-264 and existing projection architecture docs before writing the policy. (AC: AC1, AC5)
- [ ] Task 2: Create `docs/architecture/projection-versioning-incompatibility-policy.md` with a French global file comment. (AC: AC1)
- [ ] Task 3: Document `projection_version` as mandatory for every projection contract and persisted projection. (AC: AC1)
- [ ] Task 4: Define the breaking-change taxonomy that forces a new v2 projection contract. (AC: AC2)
- [ ] Task 5: Document blocking and admin logging for unknown projection versions. (AC: AC3)
- [ ] Task 6: Document blocking and admin logging for deprecated projection versions. (AC: AC4)
- [ ] Task 7: Document incompatible `source_versions` handling and recalculation authorization. (AC: AC5, AC6)
- [ ] Task 8: Document that strong backward compatibility is not promised before stable public API or B2B commitments. (AC: AC7)
- [ ] Task 9: Add targeted architecture tests or extend an existing docs test for the policy keywords and runtime neutrality. (AC: AC1, AC8)
- [ ] Task 10: Persist validation, scoped status and source checklist evidence under the CS-265 evidence folder. (AC: AC8, AC9, AC10)

## Files to Inspect First

- `_story_briefs/cs-265-add-projection-versioning-and-incompatibility-policy.md` - source brief.
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/00-story.md` - endpoint contract dependency.
- `_condamad/stories/CS-264-projection-persistence-projection-hash/00-story.md` - persistence and source-version dependency.
- `docs/architecture/product-architecture-current-state-2026-05-24.md` - current versioning, invalidation and projection registry context.
- `docs/architecture/official-product-primitives-public-projections.md` - public projection governance owner.
- `backend/tests/architecture/test_api_contract_neutrality.py` - likely docs architecture test owner.
- `backend/app/**` - inspect only with targeted searches; app source must remain unchanged unless a validation guard is required.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output only.

## Runtime Source of Truth

- Primary source of truth:
  - `docs/architecture/projection-versioning-incompatibility-policy.md` for the canonical policy.
  - CS-263 and CS-264 story contracts for endpoint and persistence dependencies.
  - `app.routes`, `app.openapi()`, scoped `git status`, `pytest` and targeted `rg` scans for runtime-neutrality checks.
- Secondary evidence:
  - Existing projection architecture docs and targeted architecture tests.
- Static scans alone are not sufficient because:
  - route and OpenAPI neutrality must be proven from the loaded app object.

## Contract Shape

- Contract type:
  - Markdown backend architecture policy for projection versioning and incompatibility.
- Fields:
  - `projection_version`: required projection contract version.
  - `source_versions`: structured source contract, runtime, reference and policy versions consumed by a projection.
  - `projection_hash`: persisted canonical payload hash governed by CS-264.
  - `version_status`: policy state for current, deprecated or unknown projection versions.
  - `admin_log`: required operational log for blocked unknown, deprecated or incompatible version outcomes.
- Required fields:
  - `projection_version`
  - `source_versions`
  - `version_status`
  - `admin_log`
- Optional fields:
  - `projection_hash` for non-persisted policy examples only.
- Required policy topics:
  - mandatory `projection_version`;
  - breaking-change taxonomy;
  - unknown projection version handling;
  - deprecated or `dépréciée` projection version handling;
  - incompatible `source_versions` handling;
  - recalculation authorization;
  - admin log obligations;
  - v1 to v2 transition rule;
  - no strong backward compatibility promise before stable public API or B2B commitments.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - policy terms stay `projection_version`, `source_versions`, `projection_hash`, `v1` and `v2`.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must remain unchanged by this policy story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-265-add-projection-versioning-and-incompatibility-policy.md`
  - `_condamad/stories/CS-263-generic-projection-endpoint-contract/00-story.md`
  - `_condamad/stories/CS-264-projection-persistence-projection-hash/00-story.md`
  - `docs/architecture/product-architecture-current-state-2026-05-24.md`
  - `docs/architecture/official-product-primitives-public-projections.md`
- Comparison after implementation:
  - `docs/architecture/projection-versioning-incompatibility-policy.md`
  - `_condamad/stories/CS-265-projection-versioning-incompatibility-policy/evidence/validation.txt`
  - `_condamad/stories/CS-265-projection-versioning-incompatibility-policy/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended application delta is one architecture policy document, targeted docs tests and CONDAMAD story evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Projection versioning policy | `docs/architecture/projection-versioning-incompatibility-policy.md` | API routers or frontend |
| Projection governance | `docs/architecture/official-product-primitives-public-projections.md` | duplicated registry document |
| Endpoint version request rule | `_condamad/stories/CS-263-generic-projection-endpoint-contract/00-story.md` | new route implementation |
| Persisted version fields | `_condamad/stories/CS-264-projection-persistence-projection-hash/00-story.md` | docs policy as DB schema owner |
| Architecture tests | `backend/tests/architecture/test_api_contract_neutrality.py` | ad hoc script outside tests |
| Evidence artifacts | `_condamad/stories/CS-265-projection-versioning-incompatibility-policy/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse existing public projection governance instead of creating a second projection registry.
- Reuse CS-263 `projection_version` request terminology and CS-264 persisted projection terminology.
- Reuse existing architecture docs for product state, invalidation and public projection ownership.
- Keep one canonical projection versioning policy document.
- Do not add external packages, scripts, API schemas, frontend helpers, builders, services, prompts or generated clients.
- Do not duplicate projection builder logic or persistence rules inside tests.

## No Legacy / Forbidden Paths

- No legacy versioning policy may be added beside the canonical document.
- No compatibility route path may be added for projection versioning.
- No fallback branch may allow unknown or deprecated projection versions.
- Do not create aliases, shims, wrappers or parallel documents for the same projection version policy.
- Do not silently mutate an existing v1 projection contract for breaking semantics.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/**`
  - `backend/app/infra/db/**`
  - `backend/migrations/**`
  - generated OpenAPI clients
  - existing projection builders and serializers

## Reintroduction Guard

- Guard target:
  - `projection_version` cannot become optional in projection contract policy;
  - unknown or deprecated projection versions cannot become permissive outcomes;
  - incompatible `source_versions` cannot be accepted without explicit recalculation authorization;
  - v1 projection semantics cannot be changed silently instead of creating v2;
  - backend app routes, OpenAPI output, frontend files, DB models and migrations cannot be changed by this story.
- Guard mechanism:
  - targeted `rg` checks for required policy terms;
  - `app.routes` and `app.openapi()` neutrality checks;
  - scoped `git status --short` for app roots;
  - targeted architecture tests;
  - persisted evidence under the CS-265 evidence folder.
- Guard owner:
  - `docs/architecture/projection-versioning-incompatibility-policy.md`;
  - `backend/tests/architecture/test_api_contract_neutrality.py`;
  - `_condamad/stories/CS-265-projection-versioning-incompatibility-policy/evidence/validation.txt`.
- Guard evidence:
  - `rg -n "projection_version|v1|v2|deprecated|source_versions|incompatible|recalculation" .\docs .\_story_briefs`;
  - `python -c "from app.main import app; assert '/v1/astrology/projections' not in app.openapi().get('paths', {})"`;
  - `python -c "from app.main import app; assert all(getattr(r, 'path', '') != '/v1/astrology/projections' for r in app.routes)"`;
  - `git status --short -- backend/app frontend/src`.

## Regression Guardrails

Scope vector:

- backend documentation policy: yes;
- docs architecture contract: yes;
- backend architecture tests: yes;
- public API route implementation: no;
- OpenAPI runtime change: no;
- frontend implementation: no;
- DB, auth implementation, i18n, style, build and migration: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | Backend ownership stays in canonical app paths and routes stay untouched. | `git status`; `app.routes`. |
| RG-022 | Validation paths must be executable and not obsolete. | `pytest`; persisted validation. |
| Registry gap | No exact projection versioning guardrail exists in resolver output. | Story-local policy and runtime-neutrality guards. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is out of scope because projection versioning does not change entitlements.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Policy document | `docs/architecture/projection-versioning-incompatibility-policy.md` | Keep the canonical projection versioning policy. |
| Validation output | `_condamad/stories/CS-265-projection-versioning-incompatibility-policy/evidence/validation.txt` | Keep test and lint transcript. |
| Application surface status | `_condamad/stories/CS-265-projection-versioning-incompatibility-policy/evidence/app-surface-status.txt` | Prove app roots stayed untouched. |
| Source checklist | `_condamad/stories/CS-265-projection-versioning-incompatibility-policy/evidence/source-checklist.md` | Record dependency and owner checks. |
| Review output | `_condamad/stories/CS-265-projection-versioning-incompatibility-policy/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this projection policy story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step data conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/projection-versioning-incompatibility-policy.md` - new canonical versioning and incompatibility policy.
- `backend/tests/architecture/test_api_contract_neutrality.py` - targeted architecture coverage for policy terms and route neutrality.
- `_condamad/stories/CS-265-projection-versioning-incompatibility-policy/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-265-projection-versioning-incompatibility-policy/evidence/app-surface-status.txt` - application non-change proof.
- `_condamad/stories/CS-265-projection-versioning-incompatibility-policy/evidence/source-checklist.md` - source coverage evidence.

Likely tests:

- `backend/tests/architecture/test_api_contract_neutrality.py` - checks policy keywords and no API route drift.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/**` - out of scope; no backend application source is touched.
- `backend/migrations/**` - out of scope; no database migration is touched.
- generated OpenAPI clients - out of scope; no generated client is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `python -c "from pathlib import Path; assert Path('docs/architecture/projection-versioning-incompatibility-policy.md').exists()"`
- VC3: `rg -n "projection_version|v1|v2|dépréciée|source_versions|incompatible|recalcul" .\docs .\_story_briefs`
- VC4: `rg -n "mandatory|required|projection_version" docs/architecture/projection-versioning-incompatibility-policy.md`
- VC5: `rg -n "breaking|v1|v2|silent" docs/architecture/projection-versioning-incompatibility-policy.md`
- VC6: `rg -n "unknown|deprecated|dépréciée|blocking|admin log" docs/architecture/projection-versioning-incompatibility-policy.md`
- VC7: `rg -n "source_versions|incompatible|recalculation|recalcul|authorized" docs/architecture/projection-versioning-incompatibility-policy.md`
- VC8: `rg -n "backward compatibility|stable public API|B2B" docs/architecture/projection-versioning-incompatibility-policy.md`
- VC9: `python -c "from app.main import app; assert '/v1/astrology/projections' not in app.openapi().get('paths', {})"`
- VC10: `python -c "from app.main import app; assert all(getattr(r, 'path', '') != '/v1/astrology/projections' for r in app.routes)"`
- VC11: `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`
- VC12: `git status --short -- backend/app frontend/src`
- VC13: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-265-projection-versioning-incompatibility-policy/evidence/validation.txt').exists()"`
- VC14: `ruff format .`
- VC15: `ruff check .`
- VC16: `pytest -q`

Before VC2, VC9, VC10, VC11, VC13, VC14, VC15 and VC16, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- A policy-only story could drift into API route, persistence, migration or frontend implementation.
- A breaking projection change could be documented as a v1 amendment instead of a v2 contract.
- Unknown or deprecated projection versions could be tolerated without admin logging.
- Incompatible `source_versions` could be accepted without an explicit recalculation decision.
- Strong backward compatibility could be implied before the product API is stable or public B2B commitments exist.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments and public or non-trivial docstrings in French for new or significantly modified backend files.
- Keep the implementation documentation-only unless a separate user decision authorizes runtime implementation work.
- Persist the required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-265-add-projection-versioning-and-incompatibility-policy.md`
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/00-story.md`
- `_condamad/stories/CS-264-projection-persistence-projection-hash/00-story.md`
- `docs/architecture/product-architecture-current-state-2026-05-24.md`
- `docs/architecture/official-product-primitives-public-projections.md`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `_condamad/stories/regression-guardrails.md`
