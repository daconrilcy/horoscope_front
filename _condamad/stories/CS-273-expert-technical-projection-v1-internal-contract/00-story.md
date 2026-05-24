# Story CS-273 expert-technical-projection-v1-internal-contract: Define expert_technical_projection_v1 Internal Contract
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-273-define-expert-technical-projection-v1-admin-astro-expert-only.md`.
- Required dependency: CS-270 internal role model.
- Required dependency: CS-271 admin data permission matrix.
- Required dependency: CS-256 structured facts contract.
- Required dependency: CS-266 OpenAPI internal/public exposure guards.
- Required dependency: CS-272 admin endpoint domain segmentation.
- Existing owner found: `docs/architecture/official-product-primitives-public-projections.md` lists the previous expert projection primitive.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: `expert_technical_projection_v1` must be defined as an internal admin/expert projection, not a B2C client surface.
- Source-alignment evidence: PASS; the story preserves internal audience, B2C denial, data families, evidence links, trace exclusions and access logs.

## Objective

Define one canonical backend-domain contract for `expert_technical_projection_v1` as an internal projection for `ADMIN` and future
`ASTRO_EXPERT` usage only.

The implementation must reclassify the projection away from public client-safe wording, define authorized astrology data families, link facts, signals and
evidence, exclude raw technical/debug payloads, and document access-log expectations without exposing B2C, implementing `ASTRO_EXPERT`, or adding runtime code.

## Target State

- `docs/architecture/expert-technical-projection-v1-contract.md` exists and starts with a French global file comment.
- `expert_technical_projection_v1` is documented as internal, interne, non client and not client-safe.
- Authorized consumers are limited to current `ADMIN` and future target-only `ASTRO_EXPERT`.
- B2C clients are explicitly denied as consumers of this projection.
- Authorized astrology data families cover technical but meaningful astrology facts, structured signals and evidence references.
- Raw runtime traces, prompt internals, replay payloads, provider debug dumps and unrestricted technical diagnostics are excluded.
- Permission attachment references the CS-271 internal matrix rather than creating a parallel policy.
- Access logs define actor, role, projection id, chart or answer reference, action, decision and correlation metadata.
- No route, OpenAPI exposure, RBAC activation, frontend file, DB object, migration, builder or service implementation is created by this story.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-273-define-expert-technical-projection-v1-admin-astro-expert-only.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-273`.
- Evidence 3: `docs/architecture/official-product-primitives-public-projections.md` - previous expert projection public wording found.
- Evidence 4: `_condamad/stories/CS-270-internal-role-model/00-story.md` - role vocabulary dependency read.
- Evidence 5: `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md` - permission matrix dependency read.
- Evidence 6: `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md` - structured facts dependency read.
- Evidence 7: `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/00-story.md` - public exposure guard dependency read.
- Evidence 8: `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/00-story.md` - admin segmentation dependency read.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output only.
- Evidence 10: `resolve_guardrails.py` - scoped resolver run for backend-domain, projection contract, access policy and internal-only scope.
- Repository structure alert: backend, backend/app, backend/tests, frontend, frontend/src and docs exist in this workspace.
- Source-alignment evidence: PASS; no brief criterion was softened into generic cleanup or public projection implementation work.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Canonical contract documentation for `expert_technical_projection_v1` under `docs/architecture`.
  - Reclassification of the existing expert projection primitive from public/client-safe wording to internal admin/expert-only wording.
  - Authorized consumer policy for `ADMIN` and future target-only `ASTRO_EXPERT`.
  - B2C denial, authorized astrology data families, structured fact/signal/evidence links and access-log expectations.
  - Runtime-neutrality checks using `app.routes`, `app.openapi()`, `pytest`, scoped `git status` and targeted `rg`.
- Out of scope:
  - Frontend UI, DB schema, auth redesign, i18n, styling, build tooling, migrations, seeds, generated clients and public API changes.
  - `ASTRO_EXPERT` implementation, RBAC activation, route implementation, projection builder, replay implementation and public fixed-star exposure.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No client B2C endpoint, serializer, OpenAPI schema, generated client, screen, model, migration, seed, token claim redesign or access grant.
  - No activation of `ASTRO_EXPERT`.
  - No full replay payload, raw provider dump, unrestricted trace bundle or public fixed-star expansion.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a documentation-first internal projection governance contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only `docs/architecture/expert-technical-projection-v1-contract.md`, targeted contract tests and story evidence artifacts.
  - Align `docs/architecture/official-product-primitives-public-projections.md` so the expert projection is no longer public/client-safe.
  - Keep backend runtime code, API routes, OpenAPI output, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Keep permission ownership attached to CS-271 instead of creating a parallel matrix.
  - Keep `ASTRO_EXPERT` as target-only role vocabulary until RBAC exists.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product asks to expose this projection to B2C or activate `ASTRO_EXPERT` before RBAC implementation.
- Additional validation rules:
  - The contract must name `expert_technical_projection_v1` exactly.
  - The contract must state that the projection is internal, interne, non client and not client-safe.
  - The contract must limit authorized consumers to `ADMIN` and future target-only `ASTRO_EXPERT`.
  - The contract must deny B2C client access.
  - The contract must define authorized astrology data families.
  - The contract must link structured facts, signals and evidence references.
  - The contract must exclude raw runtime traces, prompt internals, replay payloads and provider debug dumps.
  - The contract must define access-log fields for every access decision.
  - `app.routes`, `app.openapi()`, `pytest`, `python`, `rg` and scoped `git status` must prove public/runtime neutrality.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, `pytest` and `TestClient` prove no public runtime exposure is introduced. |
| Baseline Snapshot | yes | Before and after evidence prove the only allowed surface delta is documentation, tests and story evidence. |
| Ownership Routing | yes | Projection contract, primitive registry, permission matrix, evidence refs and access logs need separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this internal projection contract story. |
| Contract Shape | yes | The projection has exact audience, data families, exclusions, evidence links and log fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | B2C access, public OpenAPI exposure and raw debug payloads must stay out. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The internal projection contract exists. | Evidence profile: baseline_before_after_diff; `python` checks the contract document path. |
| AC2 | The projection is internal. | Evidence profile: json_contract_shape; `rg` checks `expert_technical_projection_v1`, interne, non client and not client-safe wording. |
| AC3 | Authorized consumers are explicit. | Evidence profile: json_contract_shape; `rg` checks `ADMIN`, `ASTRO_EXPERT` and target-only wording. |
| AC4 | B2C access is denied. | Evidence profile: external_usage_blocker; `pytest -q backend/tests/unit/test_expert_technical_projection_contract.py`. |
| AC5 | Astrology data families are defined. | Evidence profile: json_contract_shape; `rg` checks dignity, conditions, dominance, aspects and houses. |
| AC6 | Evidence links are defined. | Evidence profile: json_contract_shape; `rg` checks structured facts, signals and evidence refs. |
| AC7 | Raw technical payloads are excluded. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`; `rg` checks exclusions. |
| AC8 | Permission ownership uses CS-271. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/unit/test_expert_technical_projection_contract.py`. |
| AC9 | Access-log fields are specified. | Evidence profile: json_contract_shape; `rg` checks actor, role, projection id, action, decision and correlation fields. |
| AC10 | Registry wording is reclassified. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks public/client wording no longer owns this projection. |
| AC11 | Application source surfaces remain unchanged. | Evidence profile: repo_wide_negative_scan; `python` records scoped `git status --short` output for app roots. |
| AC12 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-273 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect the brief, primitive registry and CS-270, CS-271, CS-256, CS-266 and CS-272 before writing the contract. (AC: AC1, AC8)
- [ ] Task 2: Create `docs/architecture/expert-technical-projection-v1-contract.md` with a French global file comment. (AC: AC1)
- [ ] Task 3: Define `expert_technical_projection_v1` as internal, interne, non client and not client-safe. (AC: AC2)
- [ ] Task 4: Limit authorized consumers to current `ADMIN` and future target-only `ASTRO_EXPERT`. (AC: AC3, AC8)
- [ ] Task 5: Deny B2C client access in the contract and primitive registry wording. (AC: AC4, AC10)
- [ ] Task 6: Define authorized astrology data families for expert technical usage. (AC: AC5)
- [ ] Task 7: Define links to structured facts, structured signals and evidence references. (AC: AC6)
- [ ] Task 8: Exclude raw runtime traces, prompt internals, replay payloads and provider debug dumps. (AC: AC7)
- [ ] Task 9: Define access-log fields for projection access decisions. (AC: AC9)
- [ ] Task 10: Add a targeted contract test for document content, registry reclassification and runtime neutrality. (AC: AC4, AC7, AC8, AC10)
- [ ] Task 11: Persist validation, scoped status and source checklist evidence under the CS-273 evidence folder. (AC: AC11, AC12)

## Files to Inspect First

- `_story_briefs/cs-273-define-expert-technical-projection-v1-admin-astro-expert-only.md` - source brief.
- `docs/architecture/official-product-primitives-public-projections.md` - existing projection primitive registry to reclassify.
- `_condamad/stories/CS-270-internal-role-model/00-story.md` - role vocabulary dependency.
- `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md` - permission ownership dependency.
- `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md` - structured facts dependency.
- `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/00-story.md` - public OpenAPI exposure guard dependency.
- `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/00-story.md` - admin route family and logging dependency.
- `backend/app/main.py` - loaded FastAPI app, `app.routes` and `app.openapi()` source.
- `backend/tests/architecture/test_api_contract_neutrality.py` - existing public exposure guard owner.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output only.

## Runtime Source of Truth

- Primary source of truth:
  - `docs/architecture/official-product-primitives-public-projections.md` for existing projection registry ownership.
  - CS-270 and CS-271 for role vocabulary and permission matrix ownership.
  - CS-256 for structured facts and evidence input boundaries.
  - CS-266 for public OpenAPI internal-token protection.
  - `app.routes`, `app.openapi()`, `TestClient`, `pytest`, scoped `git status` and targeted `rg` scans for runtime neutrality.
- Secondary evidence:
  - Targeted `rg` scans over `docs/architecture/expert-technical-projection-v1-contract.md`.
  - `pytest -q backend/tests/unit/test_expert_technical_projection_contract.py` for contract and runtime-neutrality checks.
- Static scans alone are not sufficient because:
  - Public OpenAPI neutrality and route absence must be checked from the loaded FastAPI app.

## Contract Shape

- Contract type:
  - Markdown backend-domain contract for an internal expert technical astrology projection.
- Fields:
  - `projection_id`: exact value `expert_technical_projection_v1`.
  - `classification`: internal, interne, non client, not client-safe.
  - `authorized_consumers`: `ADMIN` and future target-only `ASTRO_EXPERT`.
  - `denied_consumers`: B2C clients and public-user surfaces.
  - `data_families`: dignity, conditions, dominance, aspects, houses, evidence-backed fixed structures and source metadata.
  - `source_links`: `structured_facts_v1`, structured signals and `evidence_refs`.
  - `excluded_surfaces`: raw runtime traces, prompt internals, replay payloads, provider debug dumps and unrestricted diagnostics.
  - `permission_source`: CS-271 internal permission matrix.
  - `access_log_fields`: actor, role, projection id, chart or answer reference, action, decision, timestamp and correlation id.
- Required fields:
  - `projection_id`
  - `classification`
  - `authorized_consumers`
  - `denied_consumers`
  - `data_families`
  - `source_links`
  - `excluded_surfaces`
  - `permission_source`
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
  - `app.openapi()` must not expose `expert_technical_projection_v1` from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-273-define-expert-technical-projection-v1-admin-astro-expert-only.md`
  - `docs/architecture/official-product-primitives-public-projections.md`
  - `_condamad/stories/CS-270-internal-role-model/00-story.md`
  - `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md`
  - `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md`
  - `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/00-story.md`
  - `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/00-story.md`
- Comparison after implementation:
  - `docs/architecture/expert-technical-projection-v1-contract.md`
  - `docs/architecture/official-product-primitives-public-projections.md`
  - `backend/tests/unit/test_expert_technical_projection_contract.py`
  - `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/evidence/validation.txt`
  - `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended repository delta is one architecture contract document, one registry reclassification, one targeted test and story evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Expert technical projection contract | `docs/architecture/expert-technical-projection-v1-contract.md` | API routers or frontend clients |
| Projection primitive registry | `docs/architecture/official-product-primitives-public-projections.md` | duplicated projection registry |
| Permission ownership | `docs/architecture/admin-permission-matrix.md` from CS-271 | projection contract as access matrix |
| Structured fact source | `docs/architecture/structured-facts-v1-contract.md` from CS-256 | raw runtime payload contract |
| Public OpenAPI exposure guard | CS-266 tests and documentation | public projection registry wording |
| Access-log expectations | CS-272 admin segmentation plus this contract | route implementation in this story |
| Story evidence artifacts | `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse the existing projection primitive registry instead of creating a second registry for expert projections.
- Reuse CS-270 role vocabulary and CS-271 permission matrix instead of defining parallel access rules.
- Reuse CS-256 `structured_facts_v1` and `evidence_refs` terminology instead of inventing a separate factual base.
- Reuse CS-266 public exposure guard wording for OpenAPI neutrality.
- Reuse CS-272 access-log vocabulary for sensitive admin route families.
- Keep one canonical `expert_technical_projection_v1` contract document and one projection identifier.
- Do not add external packages, generated clients, builders, services, routes, serializers or database objects.

## No Legacy / Forbidden Paths

- No legacy public projection path may be added for this contract.
- No compatibility projection path may expose this contract to B2C clients.
- No fallback branch may grant access to target-only roles.
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
  - `expert_technical_projection_v1` cannot become a B2C projection type;
  - `expert_technical_projection_v1` cannot appear in public `app.openapi()` output;
  - `expert_technical_projection_v1` cannot be registered as a public route in `app.routes`;
  - raw runtime traces, prompt internals, replay payloads and provider debug dumps cannot enter the contract;
  - `ASTRO_EXPERT` cannot become an active backend role through this story.
- Guard mechanism:
  - targeted `rg` checks for required contract terms and denied public wording;
  - `app.routes`, `app.openapi()` and `TestClient` neutrality checks;
  - scoped `git status --short` for application roots;
  - persisted evidence under the CS-273 evidence folder.
- Guard owner:
  - `docs/architecture/expert-technical-projection-v1-contract.md`;
  - `backend/tests/unit/test_expert_technical_projection_contract.py`;
  - `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/evidence/validation.txt`.
- Guard evidence:
  - `rg -n "expert_technical_projection_v1|ADMIN|ASTRO_EXPERT|not client-safe|B2C" .\docs .\_story_briefs`;
  - `python -c "from app.main import app; assert 'expert_technical_projection_v1' not in str(app.openapi())"`;
  - `python -c "from app.main import app; assert all('expert_technical_projection' not in getattr(r, 'path', '') for r in app.routes)"`;
  - `git status --short -- backend/app frontend/src`.

## Regression Guardrails

Scope vector:

- backend-domain contract documentation: yes;
- projection primitive registry: yes;
- internal admin/expert access policy: yes;
- public OpenAPI runtime exposure: read-only;
- frontend implementation: no;
- DB, auth implementation, i18n, style, build and migration: no.

Selected guardrails:

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `Routeurs API v1` | Backend API ownership remains untouched by the documentation story. | scoped `git status`; `python`. |
| RG-022 `Plans de validation des stories prompt-generation` | Validation evidence must stay targeted and executable. | `rg`; targeted `pytest`. |
| Registry gap | No exact `expert_technical_projection_v1` guardrail exists in resolver output. | Story-local OpenAPI and B2C guards. |

Non-applicable examples:

- RG-041 entitlement documentation is out of scope because this story uses admin permissions, not product entitlement docs.
- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 frontend CSS namespace migration is out of scope because no style or build output is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Contract document | `docs/architecture/expert-technical-projection-v1-contract.md` | Keep the canonical internal projection contract. |
| Validation output | `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/evidence/validation.txt` | Keep validation transcript. |
| Application surface status | `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/evidence/app-surface-status.txt` | Prove app roots stayed untouched. |
| Source checklist | `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/evidence/source-checklist.md` | Record source coverage. |
| Review output | `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this internal projection contract story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/expert-technical-projection-v1-contract.md` - define the canonical internal projection contract.
- `docs/architecture/official-product-primitives-public-projections.md` - reclassify the expert projection away from public/client-safe status.
- `backend/tests/unit/test_expert_technical_projection_contract.py` - cover document content, registry reclassification and runtime neutrality.
- `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/evidence/validation.txt` - persist validation output.
- `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/evidence/app-surface-status.txt` - persist scoped status output.
- `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/evidence/source-checklist.md` - persist source coverage.

Likely tests:

- `backend/tests/unit/test_expert_technical_projection_contract.py` - document, registry, B2C denial and runtime neutrality checks.
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

- VC1: `rg -n "expert_technical_projection_v1|ADMIN|ASTRO_EXPERT|non client|interne|not client-safe|internal|B2C" .\docs .\_story_briefs`
- VC2: `rg -n "expert_technical_projection_v1|interne|non client|internal|not client-safe|B2C" docs/architecture/expert-technical-projection-v1-contract.md`
- VC3: `rg -n "ADMIN|ASTRO_EXPERT|target-only|CS-271|permission matrix" docs/architecture/expert-technical-projection-v1-contract.md`
- VC4: `rg -n "dignity|conditions|dominance|aspects|houses|structured facts|signals|evidence refs" docs/architecture/expert-technical-projection-v1-contract.md`
- VC5: `rg -n "raw runtime traces|prompt internals|replay payloads|provider debug dumps|diagnostics" docs/architecture/expert-technical-projection-v1-contract.md`
- VC6: `rg -n "actor|role|projection id|action|decision|correlation" docs/architecture/expert-technical-projection-v1-contract.md`
- VC7: `pytest -q backend/tests/unit/test_expert_technical_projection_contract.py`
- VC8: `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`
- VC9: `python -c "from app.main import app; assert 'expert_technical_projection_v1' not in str(app.openapi())"`
- VC10: `python -c "from app.main import app; assert all('expert_technical_projection' not in getattr(r, 'path', '') for r in app.routes)"`
- VC11: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/evidence/validation.txt').exists()"`
- VC12: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/evidence/app-surface-status.txt').exists()"`
- VC13: `git status --short -- backend/app frontend/src`
- VC14: `ruff format .`
- VC15: `ruff check .`
- VC16: `pytest -q`

Before VC7 through VC12, VC14, VC15 and VC16, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The expert technical projection may remain ambiguously documented as client-safe or public.
- `ASTRO_EXPERT` may be interpreted as an active role instead of target-only vocabulary.
- B2C clients may receive technical astrology data through a generic projection path.
- Raw runtime traces, prompt internals or replay payloads may enter the contract under broad technical wording.
- Access-log requirements may omit actor, action, decision or correlation fields.
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
- Keep B2C clients denied for `expert_technical_projection_v1`.
- Persist validation output under the CS-273 evidence folder before requesting review.

## References

- `_story_briefs/cs-273-define-expert-technical-projection-v1-admin-astro-expert-only.md`
- `docs/architecture/official-product-primitives-public-projections.md`
- `_condamad/stories/CS-270-internal-role-model/00-story.md`
- `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md`
- `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md`
- `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/00-story.md`
- `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/00-story.md`
- `backend/app/main.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `_condamad/stories/regression-guardrails.md`
