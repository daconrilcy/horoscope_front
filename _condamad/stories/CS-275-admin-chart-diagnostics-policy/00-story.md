# Story CS-275 admin-chart-diagnostics-policy: Decide admin_chart_diagnostics Retention Redaction Replay Policy
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-275-decide-admin-chart-diagnostics-retention-redaction-replay-policy.md`.
- Required dependency: CS-271 permission matrix for admin data domains.
- Required dependency: CS-272 admin endpoint domain segmentation.
- Existing owner found: `docs/architecture/product-architecture-current-state-2026-05-24.md` tracks admin debug blockers.
- Existing owner found: `backend/app/core/sensitive_data.py` classifies birth data fields as sensitive domain data.
- Existing owner found: `backend/app/domain/astrology/runtime/calculation_graph_execution_trace.py` keeps trace separate from replay.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: `admin_chart_diagnostics_v1` lacks a formal retention, redaction and replay policy before implementation.
- Source-alignment evidence: PASS; this story preserves retention, redaction, replay separation, admin logs and client exclusion.

## Objective

Define one canonical backend-domain policy for `admin_chart_diagnostics_v1` before any diagnostic, replay, route, model or service is implemented.

The implementation must document retained diagnostic data, masked data, DPO-open retention decisions, replay prerequisites and admin consultation logs without
creating runtime diagnostics, replay snapshots, calculation changes, client exposure, persistence, migrations or frontend UI.

## Target State

- `docs/architecture/admin-chart-diagnostics-v1-policy.md` exists and starts with a French global file comment.
- The policy states what calculation diagnostic data can be retained for `admin_chart_diagnostics_v1`.
- Birth date, birth time, birth place, coordinates and user or chart identifiers are classified as sensitive and masked or justified.
- Retention is either decided with a concrete target or marked as a DPO-open decision with the exact blocked implementation surfaces.
- Replay is documented as separate from current diagnostics, with storage, input, version and retention prerequisites.
- Admin consultation logging is specified with actor, role, action, decision, timestamp, subject reference and correlation fields.
- Client surfaces, public OpenAPI, frontend files and generated clients remain out of scope.
- No diagnostic route, replay service, builder, database table, migration, calculation behavior or frontend screen is created.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-275-decide-admin-chart-diagnostics-retention-redaction-replay-policy.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-275`.
- Evidence 3: `docs/architecture/product-architecture-current-state-2026-05-24.md` - admin debug blockers and replay policy gaps inspected.
- Evidence 4: `backend/app/core/sensitive_data.py` - birth data field classification inspected.
- Evidence 5: `backend/app/domain/astrology/runtime/calculation_graph_execution_trace.py` - trace and replay separation inspected.
- Evidence 6: `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md` - permission dependency identified from tracker context.
- Evidence 7: `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/00-story.md` - admin endpoint segmentation dependency identified.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output only.
- Evidence 9: `resolve_guardrails.py` - scoped resolver run for document, backend-security, retention, redaction, replay and admin audit logs.
- Repository structure alert: backend, backend/app, backend/tests, frontend, frontend/src and docs exist in this workspace.
- Source-alignment evidence: PASS; no source concern was deferred, softened or replaced by generic documentation cleanup.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Canonical policy documentation for `admin_chart_diagnostics_v1` under `docs/architecture`.
  - Diagnostic data categories, sensitive data masking, retention decision state and DPO-open blockers.
  - Replay prerequisites for storage, input reconstruction, version identity and retention approval.
  - Admin consultation log fields and separation from AI answer audit.
  - Runtime-neutrality checks using `app.routes`, `app.openapi()`, `pytest`, scoped `git status` and targeted `rg`.
- Out of scope:
  - Frontend UI, database schema, auth redesign, i18n, styling, build tooling, migrations, seeds, generated clients and public API changes.
  - Diagnostic implementation, replay implementation, calculation changes, endpoint exposure and client-facing diagnostics.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No client route, screen, generated client, public OpenAPI exposure, model, migration, seed, builder, service or replay snapshot.
  - No change to calculation results, graph execution, narrative answer audit or LLM replay behavior.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a documentation-first backend security and diagnostics policy contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only `docs/architecture/admin-chart-diagnostics-v1-policy.md`, targeted contract tests and story evidence artifacts.
  - Extend existing product architecture or projection governance documents instead of creating a parallel debug roadmap.
  - Keep backend runtime code, API routes, OpenAPI output, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Keep permission ownership attached to CS-271 and endpoint segmentation attached to CS-272.
  - Keep replay snapshot design attached to a later storage and security model story.
  - Keep `admin_chart_diagnostics_v1` separate from narrative answer audit and LLM replay surfaces.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: DPO or security owners cannot decide retention or approved open blockers.
- Additional validation rules:
  - The policy must name `admin_chart_diagnostics_v1` exactly.
  - The policy must classify birth date, birth time, birth place, coordinates and identifiers as sensitive.
  - The policy must define retained diagnostic data or mark each undecided item as DPO-open.
  - The policy must state that replay is separate from current diagnostics.
  - The policy must list replay prerequisites for storage, input reconstruction, version identity and retention approval.
  - The policy must require admin consultation logs.
  - The policy must deny client surfaces and public OpenAPI exposure.
  - The policy must preserve narrative answer audit as a separate surface.
  - `app.routes`, `app.openapi()`, `pytest`, `python`, `rg` and scoped `git status` must prove runtime neutrality.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, `pytest` and source owners prove no runtime exposure is introduced. |
| Baseline Snapshot | yes | Before and after evidence prove the only allowed surface delta is documentation, tests and story evidence. |
| Ownership Routing | yes | Diagnostics policy, permissions, endpoint segmentation, replay and audit logs need separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this single policy story. |
| Contract Shape | yes | The policy has exact data categories, masking, retention, replay, log and client-exclusion fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Replay implementation, client exposure and raw birth data leakage must stay out. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The diagnostics policy exists. | Evidence profile: baseline_before_after_diff; `python` checks the contract document path. |
| AC2 | Diagnostic data categories are defined. | Evidence profile: json_contract_shape; `rg` checks calculation, graph, source version and diagnostic fields. |
| AC3 | Birth data is sensitive. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_admin_chart_diagnostics_policy.py`. |
| AC4 | Retention has a decision state. | Evidence profile: json_contract_shape; `rg` checks retention target, DPO-open status and blocked surfaces. |
| AC5 | Replay is separate from diagnostics. | Evidence profile: targeted_forbidden_symbol_scan; `pytest -q backend/tests/unit/test_admin_chart_diagnostics_policy.py`. |
| AC6 | Replay prerequisites are explicit. | Evidence profile: json_contract_shape; `rg` checks storage, input reconstruction, version identity and retention approval. |
| AC7 | Admin consultations are logged. | Evidence profile: json_contract_shape; `rg` checks actor, role, action, decision, timestamp and correlation fields. |
| AC8 | Client surfaces are denied. | Evidence profile: external_usage_blocker; `pytest -q backend/tests/unit/test_admin_chart_diagnostics_policy.py`. |
| AC9 | Public runtime exposure is absent. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`; `pytest` uses TestClient. |
| AC10 | Application source surfaces remain unchanged. | Evidence profile: repo_wide_negative_scan; `python` records scoped `git status --short` output. |
| AC11 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-275 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect the brief, product architecture, sensitive-data policy and trace contract before writing. (AC: AC1, AC2, AC3, AC5)
- [ ] Task 2: Create `docs/architecture/admin-chart-diagnostics-v1-policy.md` with a French global file comment. (AC: AC1)
- [ ] Task 3: Define retained calculation diagnostic data categories for `admin_chart_diagnostics_v1`. (AC: AC2)
- [ ] Task 4: Define masking or retained-field justification for birth data and identifiers. (AC: AC3)
- [ ] Task 5: Record retention target or DPO-open decision with blocked surfaces. (AC: AC4)
- [ ] Task 6: Separate current diagnostics from replay and narrative answer audit. (AC: AC5)
- [ ] Task 7: Define replay prerequisites for storage, input reconstruction, version identity and retention approval. (AC: AC6)
- [ ] Task 8: Define admin consultation log fields for every policy-protected access. (AC: AC7)
- [ ] Task 9: Add targeted contract tests for masking, replay separation, client exclusion and runtime neutrality. (AC: AC3, AC5, AC8, AC9)
- [ ] Task 10: Persist validation, scoped status and source checklist evidence under the CS-275 evidence folder. (AC: AC10, AC11)

## Files to Inspect First

- `_story_briefs/cs-275-decide-admin-chart-diagnostics-retention-redaction-replay-policy.md` - source brief.
- `docs/architecture/product-architecture-current-state-2026-05-24.md` - current admin debug and replay blockers.
- `docs/architecture/official-product-primitives-public-projections.md` - public projection boundary.
- `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md` - permission matrix dependency.
- `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/00-story.md` - admin segmentation dependency.
- `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/00-story.md` - public OpenAPI exposure guard dependency.
- `_condamad/stories/CS-268-answer-audit-access-logs/00-story.md` - nearest admin audit logging dependency.
- `_condamad/stories/CS-274-astrology-full-data-v1-internal-expert-projection/00-story.md` - adjacent diagnostics boundary.
- `backend/app/core/sensitive_data.py` - sensitive data policy owner.
- `backend/app/domain/astrology/runtime/calculation_graph_execution_trace.py` - trace and replay separation owner.
- `backend/app/main.py` - loaded FastAPI app, `app.routes` and `app.openapi()` source.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `docs/architecture/product-architecture-current-state-2026-05-24.md` for admin debug and replay blockers.
  - CS-271 for admin data permission ownership.
  - CS-272 for admin endpoint segmentation ownership.
  - `backend/app/core/sensitive_data.py` for sensitive birth-data classification.
  - `backend/app/domain/astrology/runtime/calculation_graph_execution_trace.py` for trace and replay separation.
  - `app.routes`, `app.openapi()`, `TestClient`, `pytest`, scoped `git status` and targeted `rg` scans for runtime neutrality.
- Secondary evidence:
  - Targeted `rg` scans over `docs/architecture/admin-chart-diagnostics-v1-policy.md`.
  - `pytest -q backend/tests/unit/test_admin_chart_diagnostics_policy.py` for policy content and runtime-neutrality checks.
- Static scans alone are not sufficient because:
  - public OpenAPI neutrality and route absence must be checked from the loaded FastAPI app.

## Contract Shape

- Contract type:
  - Markdown backend-domain policy for admin calculation diagnostics.
- Fields:
  - `policy_id`: exact value `admin_chart_diagnostics_v1_policy`.
  - `diagnostic_surface`: exact value `admin_chart_diagnostics_v1`.
  - `classification`: protected admin debug policy with no client exposure.
  - `retained_diagnostic_data`: calculation facts, graph node status, source versions, proof references and non-sensitive timings.
  - `sensitive_data`: birth date, birth time, birth place, coordinates, user id, chart id and raw input references.
  - `redaction_policy`: mask, truncate, hash or justify retained sensitive fields.
  - `retention_policy`: concrete retention target or DPO-open decision with blocked surfaces.
  - `replay_boundary`: current diagnostics are not replay snapshots.
  - `replay_prerequisites`: storage owner, input reconstruction, version identity, retention approval and purge rules.
  - `admin_access_log_fields`: actor, role, action, decision, timestamp, subject reference and correlation id.
  - `denied_surfaces`: clients, public OpenAPI, frontend, generated clients and narrative answer audit.
- Required fields:
  - `policy_id`
  - `diagnostic_surface`
  - `classification`
  - `retained_diagnostic_data`
  - `sensitive_data`
  - `redaction_policy`
  - `retention_policy`
  - `replay_boundary`
  - `replay_prerequisites`
  - `admin_access_log_fields`
  - `denied_surfaces`
- Optional fields:
  - none.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - documentation only; no runtime JSON serializer is added.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose `admin_chart_diagnostics_v1` from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-275-decide-admin-chart-diagnostics-retention-redaction-replay-policy.md`
  - `docs/architecture/product-architecture-current-state-2026-05-24.md`
  - `backend/app/core/sensitive_data.py`
  - `backend/app/domain/astrology/runtime/calculation_graph_execution_trace.py`
  - `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md`
  - `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/00-story.md`
- Comparison after implementation:
  - `docs/architecture/admin-chart-diagnostics-v1-policy.md`
  - `backend/tests/unit/test_admin_chart_diagnostics_policy.py`
  - `_condamad/stories/CS-275-admin-chart-diagnostics-policy/evidence/validation.txt`
  - `_condamad/stories/CS-275-admin-chart-diagnostics-policy/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended repository delta is one architecture policy document, one targeted test and CONDAMAD evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Diagnostics policy | `docs/architecture/admin-chart-diagnostics-v1-policy.md` | API routers or frontend clients |
| Permission matrix | CS-271 permission matrix contract | diagnostics policy as role matrix |
| Endpoint segmentation | CS-272 admin segmentation contract | diagnostics policy as router map |
| Sensitive data categories | `backend/app/core/sensitive_data.py` | ad hoc policy wording only |
| Trace boundary | `backend/app/domain/astrology/runtime/calculation_graph_execution_trace.py` | replay snapshot implementation |
| Replay storage model | later `replay_snapshot_v1` storage and security story | `admin_chart_diagnostics_v1` policy |
| Answer audit logs | CS-268 answer audit access logs | calculation diagnostics policy |
| Story evidence artifacts | `_condamad/stories/CS-275-admin-chart-diagnostics-policy/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse CS-271 permission vocabulary instead of defining a parallel admin role matrix.
- Reuse CS-272 endpoint segmentation vocabulary instead of defining route ownership in this policy.
- Reuse `backend/app/core/sensitive_data.py` sensitive data categories for birth data wording.
- Reuse the existing trace contract separation instead of turning trace into replay evidence.
- Reuse product architecture admin debug blocker wording instead of creating a second debug roadmap.
- Keep narrative answer audit and LLM replay surfaces separate from calculation diagnostics.
- Keep one canonical `admin_chart_diagnostics_v1` policy document and one policy identifier.
- Do not add external packages, generated clients, builders, services, routes, serializers or database objects.

## No Legacy / Forbidden Paths

- No legacy diagnostic route path may be added for this policy.
- No compatibility diagnostic route path may expose this policy to clients.
- No fallback branch may merge current diagnostics with replay snapshots.
- Do not create aliases, shims, compatibility wrappers or parallel diagnostic policy documents.
- Do not expose raw birth data, coordinates, raw graph payloads, replay inputs, provider debug dumps or unrestricted diagnostics.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/**`
  - `backend/app/infra/db/**`
  - `backend/migrations/**`
  - generated OpenAPI clients
  - public B2C projection contracts

## Reintroduction Guard

- Guard target:
  - `admin_chart_diagnostics_v1` cannot appear in public `app.openapi()` output;
  - `admin_chart_diagnostics_v1` cannot be registered as a route in `app.routes`;
  - replay snapshots cannot be implemented through this policy story;
  - birth data cannot be retained without masking or documented justification;
  - narrative answer audit and calculation diagnostics cannot be merged;
  - client surfaces cannot consume diagnostic payloads from this story.
- Guard mechanism:
  - targeted `rg` checks for required policy terms and denied client wording;
  - `app.routes`, `app.openapi()` and `TestClient` neutrality checks;
  - scoped `git status --short` for application roots;
  - persisted evidence under the CS-275 evidence folder.
- Guard owner:
  - `docs/architecture/admin-chart-diagnostics-v1-policy.md`;
  - `backend/tests/unit/test_admin_chart_diagnostics_policy.py`;
  - `_condamad/stories/CS-275-admin-chart-diagnostics-policy/evidence/validation.txt`.
- Guard evidence:
  - `rg -n "admin_chart_diagnostics|rétention|redaction|replay|données de naissance|DPO" .\docs .\_story_briefs`;
  - `python -c "from app.main import app; assert 'admin_chart_diagnostics' not in str(app.openapi())"`;
  - `python -c "from app.main import app; assert all('admin_chart_diagnostics' not in getattr(r, 'path', '') for r in app.routes)"`;
  - `git status --short -- backend/app frontend/src`.

## Regression Guardrails

Scope vector:

- backend-domain policy documentation: yes;
- admin diagnostics security policy: yes;
- retention, redaction and replay decision contract: yes;
- admin consultation logging policy: yes;
- public OpenAPI runtime exposure: read-only;
- frontend implementation: no;
- DB, auth implementation, i18n, style, build and migration: no.

Selected guardrails:

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend API ownership remains untouched by the policy story. | scoped `git status`; `python`. |
| Registry gap | No exact `admin_chart_diagnostics_v1` guardrail exists in resolver output. | Story-local runtime and client guards. |

Non-applicable examples:

- RG-041 entitlement documentation is out of scope because this story uses admin data policy, not product entitlement docs.
- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 frontend CSS namespace migration is out of scope because no style or build output is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Policy document | `docs/architecture/admin-chart-diagnostics-v1-policy.md` | Keep the canonical retention, redaction and replay policy. |
| Validation output | `_condamad/stories/CS-275-admin-chart-diagnostics-policy/evidence/validation.txt` | Keep validation transcript. |
| Application surface status | `_condamad/stories/CS-275-admin-chart-diagnostics-policy/evidence/app-surface-status.txt` | Prove app roots stayed untouched. |
| Source checklist | `_condamad/stories/CS-275-admin-chart-diagnostics-policy/evidence/source-checklist.md` | Record source coverage. |
| Review output | `_condamad/stories/CS-275-admin-chart-diagnostics-policy/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this policy story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/admin-chart-diagnostics-v1-policy.md` - define retention, redaction and replay policy.
- `docs/architecture/product-architecture-current-state-2026-05-24.md` - align admin debug roadmap status with the policy decision.
- `backend/tests/unit/test_admin_chart_diagnostics_policy.py` - cover document content, sensitive data, replay separation and runtime neutrality.
- `_condamad/stories/CS-275-admin-chart-diagnostics-policy/evidence/validation.txt` - persist validation output.
- `_condamad/stories/CS-275-admin-chart-diagnostics-policy/evidence/app-surface-status.txt` - persist scoped status output.
- `_condamad/stories/CS-275-admin-chart-diagnostics-policy/evidence/source-checklist.md` - persist source coverage.

Likely tests:

- `backend/tests/unit/test_admin_chart_diagnostics_policy.py` - policy, masking, replay separation, client exclusion and runtime-neutrality checks.
- `backend/tests/architecture/test_api_contract_neutrality.py` - existing public OpenAPI forbidden-token guard remains relevant.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no persistence schema is created.
- `backend/app/api/**` - out of scope; no route path, router registration or auth dependency is touched.
- `backend/app/services/**` - out of scope; no diagnostic or replay service is touched.
- `backend/app/domain/astrology/runtime/**` - out of scope; no calculation behavior is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `rg -n "admin_chart_diagnostics|rétention|redaction|replay|données de naissance|DPO" .\docs .\_story_briefs`
- VC2: `rg -n "admin_chart_diagnostics_v1|retention|DPO-open|redaction|replay" docs/architecture/admin-chart-diagnostics-v1-policy.md`
- VC3: `rg -n "birth date|birth time|birth place|coordinates|user id|chart id|sensitive" docs/architecture/admin-chart-diagnostics-v1-policy.md`
- VC4: `rg -n "storage|input reconstruction|version identity|retention approval|purge" docs/architecture/admin-chart-diagnostics-v1-policy.md`
- VC5: `rg -n "actor|role|action|decision|timestamp|correlation" docs/architecture/admin-chart-diagnostics-v1-policy.md`
- VC6: `pytest -q backend/tests/unit/test_admin_chart_diagnostics_policy.py`
- VC7: `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`
- VC8: `python -c "from app.main import app; assert 'admin_chart_diagnostics' not in str(app.openapi())"`
- VC9: `python -c "from app.main import app; assert all('admin_chart_diagnostics' not in getattr(r, 'path', '') for r in app.routes)"`
- VC10: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-275-admin-chart-diagnostics-policy/evidence/validation.txt').exists()"`
- VC11: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-275-admin-chart-diagnostics-policy/evidence/app-surface-status.txt').exists()"`
- VC12: `git status --short -- backend/app frontend/src`
- VC13: `ruff format .`
- VC14: `ruff check .`
- VC15: `pytest -q`

Before VC6 through VC11, VC13, VC14 and VC15, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- Replay may be implemented before storage, input, version and retention decisions are approved.
- Birth data or identifiers may be retained without masking or documented justification.
- Calculation diagnostics may be confused with narrative answer audit or LLM replay.
- Admin consultations may lack audit logs, weakening accountability.
- Client or public OpenAPI surfaces may expose diagnostic payloads.
- A documentation-only policy story may accidentally mutate backend runtime, DB, auth or frontend surfaces.

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
- Keep replay snapshot storage and execution outside this story.
- Keep narrative answer audit separate from calculation diagnostics.
- Persist validation output under the CS-275 evidence folder before requesting review.

## References

- `_story_briefs/cs-275-decide-admin-chart-diagnostics-retention-redaction-replay-policy.md`
- `docs/architecture/product-architecture-current-state-2026-05-24.md`
- `docs/architecture/official-product-primitives-public-projections.md`
- `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md`
- `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/00-story.md`
- `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/00-story.md`
- `_condamad/stories/CS-268-answer-audit-access-logs/00-story.md`
- `_condamad/stories/CS-274-astrology-full-data-v1-internal-expert-projection/00-story.md`
- `backend/app/core/sensitive_data.py`
- `backend/app/domain/astrology/runtime/calculation_graph_execution_trace.py`
- `backend/app/main.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `_condamad/stories/regression-guardrails.md`
