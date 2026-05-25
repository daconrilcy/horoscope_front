# Story CS-267 admin-answer-audit-api: Define admin_answer_audit_v1 Admin API
Status: done

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-267-define-admin-answer-audit-api.md`.
- Related dependency: CS-259 defines `narrative_answer_audit_v1` as the source audit contract.
- Related dependency: CS-260 defines `evidence_refs` as the proof reference contract.
- Related dependency: CS-261 defines rejected narrative answer handling.
- Related future dependency: CS-288 persists `narrative_answer_audit_v1` records before real query data exists.
- Related future dependency: CS-289 validates `evidence_refs` before proof drilldown can be trusted.
- Related future dependency: CS-290 implements real rejected answer workflow data.
- Existing owner found: `backend/app/api/v1/routers/admin/users.py` uses `require_admin_user` for protected admin routes.
- Existing owner found: `backend/app/api/v1/routers/admin/logs.py` exposes protected admin diagnostic read routes.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: admins need one protected audit API contract for narrative answers, proofs, versions and rejected outputs.
- Source-alignment evidence: PASS; ACs cover protected admin access, fields, filters, masking, rejected answers and diagnostics separation.

## Objective

Define one canonical backend API contract document for `admin_answer_audit_v1`.

The implementation must specify the protected admin consultation surface for narrative answer audits without creating the real persistence,
frontend admin UI, replay workflow, client access, or calculation debug coupling.

## Target State

- `admin_answer_audit_v1` is documented as an internal protected admin API contract.
- The API contract defines admin use cases for consultation, filtering, diagnostic review and rejected answer analysis.
- The list response and detail response fields are explicit and reuse `narrative_answer_audit_v1` and `evidence_refs` terminology.
- Filters are defined for `status`, `plan`, date range, `provider` and `model`.
- Birth data masking rules are explicit and block raw birth date, time, place, coordinates and timezone from default responses.
- Error and permission behavior is explicit for unauthenticated, non-admin, missing record and unavailable backing store states.
- The API remains separate from `admin_chart_diagnostics_v1`, client endpoints, replay workflows and calculation debug data.
- No backend route, model, repository, migration, frontend file, generated client, replay job or auth redesign is created by this story.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-267-define-admin-answer-audit-api.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-267`.
- Evidence 3: `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md` - audit contract dependency read.
- Evidence 4: `_condamad/stories/CS-260-evidence-refs-contract-validation/00-story.md` - proof reference dependency read.
- Evidence 5: `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/00-story.md` - rejection dependency read.
- Evidence 6: `backend/app/api/v1/routers/admin/users.py` - protected admin route owner pattern found.
- Evidence 7: `backend/app/api/v1/routers/admin/logs.py` - protected admin diagnostic read route pattern found.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output only.
- Evidence 9: `resolve_guardrails.py` - scoped resolver run for backend API, admin route, OpenAPI, JSON response and protected admin scope.
- Repository structure alert: backend, backend app and backend tests roots exist in this workspace.
- Source-alignment evidence: PASS; no brief stake was narrowed into a generic documentation task.

## Domain Boundary

- Domain: backend-api
- In scope:
  - Canonical API contract documentation for `admin_answer_audit_v1`.
  - Protected admin-only route family definition for narrative answer audit consultation.
  - List and detail response fields for answers, proof references, versions, providers, models, plans and rejected records.
  - Filters for `status`, `plan`, date range, `provider` and `model`.
  - Birth data masking policy for default admin audit payloads.
  - Error and permission rules for the protected internal API.
  - Negative runtime checks that no public client endpoint or calculation debug route is introduced by this contract story.
- Out of scope:
  - Frontend UI, client API access, DB schema, migrations, replay workflow, i18n, styling, build tooling and generated clients.
  - Real persistence query implementation, real `evidence_refs` validation, real rejected workflow data and calculation debug fusion.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No client endpoint, response serializer, DB table, repository, migration, replay job or calculation debug endpoint.
  - No merge with `admin_chart_diagnostics_v1`.
  - No raw birth data exposure in default admin answer audit payloads.

## Operation Contract

- Operation type: create
- Primary archetype: api-contract-change
- Archetype reason: the story defines a protected admin API contract with OpenAPI, permissions and JSON response rules.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the `admin_answer_audit_v1` API contract documentation and story evidence artifacts.
  - Reuse CS-259 `narrative_answer_audit_v1`, CS-260 `evidence_refs` and CS-261 rejected answer terminology.
  - Reuse existing `require_admin_user` admin protection pattern in the documented route contract.
  - Keep runtime routers, frontend, DB, migrations, replay, i18n, style and build tooling unchanged.
  - Keep `admin_answer_audit_v1` separate from `admin_chart_diagnostics_v1`.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product asks to expose this audit surface to clients or to merge it with chart diagnostics.
- Additional validation rules:
  - The contract must name `admin_answer_audit_v1` exactly.
  - The contract must document the protected internal admin API surface.
  - The contract must define admin use cases, list fields, detail fields, filters, permissions and errors.
  - The contract must define birth data masking rules for default responses.
  - The contract must allow consultation of rejected narrative answers.
  - The contract must keep `admin_chart_diagnostics_v1` separate.
  - `app.routes`, `app.openapi()`, `pytest` and `TestClient` prove no client route or premature runtime route is added.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, `TestClient` and `pytest` prove runtime API exposure boundaries. |
| Baseline Snapshot | yes | Before and after evidence prove one contract document and no application surface drift. |
| Ownership Routing | yes | Admin answer audit, chart diagnostics, persistence and frontend admin UI need separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this protected API contract story. |
| Contract Shape | yes | The API has exact route family, filters, fields, permissions, errors and masking rules. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Client routes, debug fusion, raw birth data and runtime route drift must stay out. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `admin_answer_audit_v1` is documented. | Evidence profile: baseline_before_after_diff; `python` checks the contract document path. |
| AC2 | Admin use cases are explicit. | Evidence profile: json_contract_shape; `rg` checks consultation, diagnostic review and rejected answers. |
| AC3 | Consultable fields are explicit. | Evidence profile: json_contract_shape; `rg` checks answer_id, evidence_refs, provider, model and prompt_version. |
| AC4 | Filters are explicit. | Evidence profile: json_contract_shape; `rg` checks status, plan, date range, provider and model. |
| AC5 | Birth data is masked. | Evidence profile: api_error_shape_contract; `rg` checks masked birth data and forbidden raw fields. |
| AC6 | Permission errors are explicit. | Evidence profile: api_error_shape_contract; `rg` checks 401, 403, 404 and 503 rules. |
| AC7 | Rejected answers are consultable. | Evidence profile: json_contract_shape; `rg` checks rejected status and rejection_reason. |
| AC8 | Chart diagnostics stay separate. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks admin_chart_diagnostics_v1 separation. |
| AC9 | Runtime route exposure is unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`. |
| AC10 | Protected route behavior is specified. | Evidence profile: runtime_openapi_contract; `pytest -q backend/app/tests/integration/test_admin_answer_audit_contract.py`. |
| AC11 | Application source surfaces remain unchanged. | Evidence profile: repo_wide_negative_scan; `python` records scoped git status output. |
| AC12 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-267 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-259, CS-260, CS-261 and existing admin routers before writing the contract. (AC: AC1, AC2)
- [ ] Task 2: Create `docs/architecture/admin-answer-audit-api.md` with a French global file comment. (AC: AC1)
- [ ] Task 3: Define admin use cases for consultation, diagnostics and rejected answer analysis. (AC: AC2, AC7)
- [ ] Task 4: Document list and detail response fields using upstream audit and proof vocabulary. (AC: AC3)
- [ ] Task 5: Document filters for status, plan, date range, provider and model. (AC: AC4)
- [ ] Task 6: Document default birth data masking and forbidden raw birth fields. (AC: AC5)
- [ ] Task 7: Document permission and error behavior for protected admin access. (AC: AC6, AC10)
- [ ] Task 8: Document separation from `admin_chart_diagnostics_v1`, client APIs and replay workflows. (AC: AC8)
- [ ] Task 9: Add contract tests that use `TestClient`, `app.routes` and `app.openapi()` for exposure boundaries. (AC: AC9, AC10)
- [ ] Task 10: Persist validation, scoped status and source checklist evidence under the CS-267 evidence folder. (AC: AC11, AC12)

## Files to Inspect First

- `_story_briefs/cs-267-define-admin-answer-audit-api.md` - source brief.
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md` - upstream answer audit contract.
- `_condamad/stories/CS-260-evidence-refs-contract-validation/00-story.md` - upstream proof reference contract.
- `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/00-story.md` - rejected answer workflow contract.
- `docs/architecture/narrative-answer-audit-v1-contract.md` - expected audit contract after CS-259 implementation.
- `docs/architecture/evidence-refs-contract.md` - expected proof contract after CS-260 implementation.
- `docs/architecture/ungrounded-narrative-rejection-workflow.md` - expected rejection contract after CS-261 implementation.
- `backend/app/api/v1/routers/admin/users.py` - current protected admin route pattern.
- `backend/app/api/v1/routers/admin/logs.py` - current protected admin diagnostics pattern.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output only.

## Runtime Source of Truth

- Primary source of truth:
  - CS-259 `narrative_answer_audit_v1` story for answer audit fields.
  - CS-260 `evidence_refs` story for proof reference fields and validation vocabulary.
  - CS-261 rejected answer story for rejected status, reason and client masking vocabulary.
  - `backend/app/api/v1/routers/admin/users.py` and `backend/app/api/v1/routers/admin/logs.py` for admin auth patterns.
  - `app.routes`, `app.openapi()`, `TestClient`, scoped `git status`, `pytest` and targeted `rg` scans for exposure boundaries.
- Secondary evidence:
  - Targeted `rg` scans over `docs/architecture/admin-answer-audit-api.md`.
- Static scans alone are not sufficient because:
  - protected API exposure and route neutrality must be proven from the loaded app and HTTP test harness.

## Contract Shape

- Contract type:
  - Protected internal admin API contract for narrative answer audit consultation.
- Route family:
  - `GET /v1/admin/answer-audits` for filtered list consultation.
  - `GET /v1/admin/answer-audits/{answer_id}` for one audit detail.
- Fields:
  - `contract_id`: exact value `admin_answer_audit_v1`.
  - `answer_id`: audited narrative answer identifier.
  - `answer_type`: category inherited from `narrative_answer_audit_v1`.
  - `user_id`: user identifier, returned only to authorized admins.
  - `chart_id`: chart identifier, returned only to authorized admins.
  - `plan`: commercial plan at generation time.
  - `status`: audit status including `grounded`, `partial`, `ungrounded`, `rejected` and `not_checked`.
  - `created_at`: generation or audit timestamp used for date filters.
  - `projection_version`: upstream projection version.
  - `projection_hash`: stable hash from the audited projection.
  - `llm_input_version`: AI input contract version.
  - `llm_input_hash`: stable hash of the LLM input payload.
  - `prompt_version`: prompt contract version.
  - `provider`: LLM provider identifier.
  - `model`: provider model identifier.
  - `evidence_refs`: admin proof reference summary and detail linkage.
  - `rejection_reason`: structured reason for rejected answers.
  - `birth_data`: masked summary only, never raw date, time, place, coordinates or timezone by default.
  - `permission_policy`: admin-only access through existing admin authentication dependency.
  - `error_policy`: 401, 403, 404 and 503 response rules.
- Required fields:
  - `contract_id`
  - `answer_id`
  - `answer_type`
  - `plan`
  - `status`
  - `created_at`
  - `projection_version`
  - `projection_hash`
  - `llm_input_version`
  - `llm_input_hash`
  - `prompt_version`
  - `provider`
  - `model`
  - `evidence_refs`
  - `birth_data`
  - `permission_policy`
  - `error_policy`
- Optional fields:
  - `rejection_reason` only for rejected answers.
  - `user_id` and `chart_id` only for authorized admin detail scope.
- Status codes:
  - `200` for successful protected admin list or detail consultation.
  - `401` when authentication is missing.
  - `403` when the authenticated user is not admin.
  - `404` when the requested audit answer is not found.
  - `503` when the backing audit store is not available.
- Serialization names:
  - JSON keys use the exact snake_case names listed in this contract.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose a client route for this API from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-267-define-admin-answer-audit-api.md`
  - `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md`
  - `_condamad/stories/CS-260-evidence-refs-contract-validation/00-story.md`
  - `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/00-story.md`
  - `backend/app/api/v1/routers/admin/users.py`
  - `backend/app/api/v1/routers/admin/logs.py`
- Comparison after implementation:
  - `docs/architecture/admin-answer-audit-api.md`
  - `backend/app/tests/integration/test_admin_answer_audit_contract.py`
  - `_condamad/stories/CS-267-admin-answer-audit-api/evidence/validation.txt`
  - `_condamad/stories/CS-267-admin-answer-audit-api/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended repository delta is one architecture contract document, targeted tests and CONDAMAD evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| `admin_answer_audit_v1` API contract | `docs/architecture/admin-answer-audit-api.md` | frontend, DB models, chart diagnostics |
| Protected admin route pattern | `backend/app/api/v1/routers/admin/**` | public or client routers |
| Narrative answer audit fields | `docs/architecture/narrative-answer-audit-v1-contract.md` | duplicated admin-only field registry |
| Proof reference fields | `docs/architecture/evidence-refs-contract.md` | admin route code as proof source owner |
| Rejected answer workflow | `docs/architecture/ungrounded-narrative-rejection-workflow.md` | replay jobs or calculation debug |
| Future persistence | later CS-288 persistence story | this API contract story |
| Evidence artifacts | `_condamad/stories/CS-267-admin-answer-audit-api/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse `require_admin_user` as the documented admin permission pattern.
- Reuse CS-259 field names for answer audit identity, hashes, provider, model and prompt provenance.
- Reuse CS-260 `evidence_refs` source and validation vocabulary.
- Reuse CS-261 rejected answer status and reason vocabulary.
- Reuse existing admin router namespace conventions under `/v1/admin`.
- Keep one canonical `admin_answer_audit_v1` contract document and one contract identifier.
- Do not add external packages, duplicate proof taxonomies, duplicate rejected status values or parallel admin diagnostics contracts.

## No Legacy / Forbidden Paths

- No legacy public route path may be added for this API contract.
- No compatibility route path may be added for this API contract.
- No fallback route path may be added for this API contract.
- No client endpoint may expose `admin_answer_audit_v1`.
- No route may merge `admin_answer_audit_v1` with `admin_chart_diagnostics_v1`.
- No raw birth date, raw birth time, raw birth place, raw coordinates or raw timezone may appear in default admin answer audit responses.
- No replay endpoint, DB migration, generated frontend client or calculation debug endpoint is authorized by this story.

## Reintroduction Guard

- Forbidden route paths:
  - `/v1/answer-audits`
  - `/v1/users/me/answer-audits`
  - `/v1/admin/chart-diagnostics/answer-audits`
  - `/v1/admin/answer-audit-replay`
- Forbidden contract merge:
  - `admin_chart_diagnostics_v1` must not own `admin_answer_audit_v1` fields.
- Forbidden raw birth fields in default admin audit responses:
  - `birth_date`
  - `birth_time`
  - `birth_place`
  - `birth_lat`
  - `birth_lon`
  - `birth_timezone`
- Required guards:
  - `python` checks `app.routes` for forbidden route paths.
  - `python` checks `app.openapi()` for no client exposure.
  - `rg` checks the contract and tests for masking and diagnostic separation.
  - `pytest -q backend/app/tests/integration/test_admin_answer_audit_contract.py` runs the `TestClient` contract suite.

## Regression Guardrails

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `Routeurs API v1` | Admin API contract stays under canonical `/v1/admin` ownership. | `app.routes`; targeted `pytest`. |
| RG-003 `Architecture des routes API v1` | Public and client routers do not own this admin audit surface. | `app.openapi()`; `rg` route scan. |
| RG-007 `Endpoints admin LLM observability` | LLM audit diagnostics remain protected admin behavior. | `TestClient`; OpenAPI check. |
| RG-020 `Taxonomie LLM consultation specifique` | Admin answer audit terminology reuses LLM audit taxonomy. | `rg` contract scan. |
| RG-022 `Plans de validation des stories prompt-generation` | Backend tests must cover prompt/provider audit contract terms. | `pytest`; targeted `rg`. |
| Registry gap | No exact `admin_answer_audit_v1` guardrail exists in resolver output. | Story-local route and contract guards. |
| Non-applicable example | RG-041 entitlement docs are out of scope for this admin audit API. | No entitlement file edits. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation output | `_condamad/stories/CS-267-admin-answer-audit-api/evidence/validation.txt` | Keep validation transcript. |
| Application surface status | `_condamad/stories/CS-267-admin-answer-audit-api/evidence/app-surface-status.txt` | Prove scoped app changes. |
| Source checklist | `_condamad/stories/CS-267-admin-answer-audit-api/evidence/source-checklist.md` | Record mandatory source coverage. |
| Review output | `_condamad/stories/CS-267-admin-answer-audit-api/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this protected API contract story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/admin-answer-audit-api.md` - define the canonical protected admin API contract.
- `backend/app/tests/integration/test_admin_answer_audit_contract.py` - cover route exposure, OpenAPI and masking contract checks.
- `_condamad/stories/CS-267-admin-answer-audit-api/evidence/validation.txt` - persist validation output.
- `_condamad/stories/CS-267-admin-answer-audit-api/evidence/app-surface-status.txt` - persist scoped status output.
- `_condamad/stories/CS-267-admin-answer-audit-api/evidence/source-checklist.md` - persist source coverage.

Likely tests:

- `backend/app/tests/integration/test_admin_answer_audit_contract.py` - `TestClient`, `app.routes` and `app.openapi()` contract checks.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no persistence schema is created.
- `backend/app/infra/**` - out of scope; no repository or DB adapter is created.
- `backend/app/api/v1/routers/public/**` - out of scope; no client route is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `rg -n "admin_answer_audit_v1|GET /v1/admin/answer-audits|GET /v1/admin/answer-audits/{answer_id}" docs/architecture/admin-answer-audit-api.md`
- VC2: `rg -n "consultation|diagnostic review|rejected answers|rejection_reason" docs/architecture/admin-answer-audit-api.md`
- VC3: `rg -n "answer_id|evidence_refs|provider|model|prompt_version|projection_hash" docs/architecture/admin-answer-audit-api.md`
- VC4: `rg -n "status|plan|date range|provider|model" docs/architecture/admin-answer-audit-api.md`
- VC5: `rg -n "masked birth data|birth_date|birth_time|birth_place|birth_lat|birth_lon|birth_timezone" docs/architecture/admin-answer-audit-api.md`
- VC6: `rg -n "401|403|404|503|require_admin_user|admin-only" docs/architecture/admin-answer-audit-api.md`
- VC7: `rg -n "admin_chart_diagnostics_v1|calculation debug|client endpoint|replay" docs/architecture/admin-answer-audit-api.md`
- VC8: `pytest -q backend/app/tests/integration/test_admin_answer_audit_contract.py`
- VC9: `python -c "from app.main import app; assert all('/v1/users/me/answer-audits' not in getattr(r, 'path', '') for r in app.routes)"`
- VC10: `python -c "from app.main import app; assert '/v1/users/me/answer-audits' not in str(app.openapi())"`
- VC11: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-267-admin-answer-audit-api/evidence/validation.txt').exists()"`
- VC12: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-267-admin-answer-audit-api/evidence/app-surface-status.txt').exists()"`
- VC13: `git status --short -- backend/app frontend/src`
- VC14: `ruff format .`
- VC15: `ruff check .`
- VC16: `pytest -q`
- VC17: `rg -n "admin_answer_audit|réponses rejetées|evidence_refs|masquage|admin" .\docs .\_story_briefs`

## Regression Risks

- The admin API could expose proof metadata through a client route instead of a protected admin namespace.
- The contract could leak raw birth data by documenting raw fields as default response content.
- The API could merge narrative answer audit with calculation debug and make diagnostics ambiguous.
- The story could implement runtime persistence before CS-288, CS-289 and CS-290 provide real backing data.
- The contract could duplicate CS-259, CS-260 or CS-261 terminology instead of reusing their canonical names.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the Python virtual environment before every Python command.
- Keep backend runtime implementation limited to tests and documentation unless the contract test requires a no-op import check.
- Keep all new or significantly modified application files documented with a French top-level comment or docstring.
- Do not create frontend UI, generated clients, migrations, repositories, replay jobs or calculation debug routes.
- Persist validation output under the CS-267 evidence folder before requesting review.

## References

- `_story_briefs/cs-267-define-admin-answer-audit-api.md`
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md`
- `_condamad/stories/CS-260-evidence-refs-contract-validation/00-story.md`
- `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/00-story.md`
- `backend/app/api/v1/routers/admin/users.py`
- `backend/app/api/v1/routers/admin/logs.py`
- `_condamad/stories/regression-guardrails.md`
