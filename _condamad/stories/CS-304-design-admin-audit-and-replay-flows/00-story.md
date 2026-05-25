# Story CS-304 design-admin-audit-and-replay-flows: Design Admin Audit And Replay Flows
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-304-design-admin-audit-and-replay-flows.md`.
- Selected mode: Repo-informed story.
- Source problem statement: les surfaces backend admin existent pour réponses rejetées, audit et replay snapshot, mais les flows admin
  doivent être cadrés avant toute UI afin de rester internes, audités et expurgés des données sensibles.
- Source-alignment evidence: cette story conserve les cinq attentes du brief: flows admin, audit par action, champs interdits,
  endpoints nommés et blocage explicite hors accès admin interne.

## Objective

Produire un contrat UX/API admin qui décrit les écrans et flows nécessaires pour consulter les réponses rejetées, lire les audits
autorisés, consulter le replay snapshot, lancer une tentative de replay contrôlée et purger manuellement avec audit.

## Target State

- Un document canonique `docs/architecture/admin-audit-replay-flows.md` décrit les flows admin minimaux.
- Les endpoints backend consommés sont nommés avec méthode, chemin, objectif et preuve runtime `app.openapi()` ou `app.routes`.
- Chaque action sensible indique son événement d'audit attendu et les champs UI visibles ou masqués.
- Le document interdit toute exposition B2C, publique, support large, export massif ou lecture de données brutes.
- L'implémentation frontend/admin reste bloquée si AuthN/AuthZ admin interne, logs d'audit et masquage ne sont pas prouvés.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-304-design-admin-audit-and-replay-flows.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign the story number.
- Evidence 3: `backend/app/api/v1/routers/admin/audit.py` - admin audit and replay snapshot routes inspected.
- Evidence 4: `backend/app/api/v1/routers/admin/llm/observability.py` - admin LLM observability routes inspected.
- Evidence 5: `backend/app/services/api_contracts/admin/audit.py` - admin audit and replay schemas inspected.
- Evidence 6: `docs/architecture/replay-snapshot-v1-storage-security-model.md` - replay security policy inspected.
- Evidence 7: `docs/architecture/replay-snapshot-v1-dpo-security-approval-request.md` - DPO/security approval inspected.
- Evidence 8: `_condamad/stories/CS-268-answer-audit-access-logs/evidence/final-runtime-closure.md` - access-log closure inspected.
- Evidence 9: `resolve_guardrails.py` selected RG-002, RG-003 and RG-007 for this admin API contract scope.

## Domain Boundary

- Domain: admin-ux-api-contract
- In scope:
  - Architecture document for internal admin audit and replay flows.
  - Backend runtime inventory of admin endpoints already exposed under `/v1/admin/`.
  - Security and redaction rules for fields displayed in future admin UI.
  - Audit expectations for read, replay, purge and review-status actions.
- Out of scope:
  - Frontend UI implementation, generated client, database schema, auth model, RBAC extension, i18n, styling, build tooling and migrations.
  - Public route creation, B2C exposure, export massif, raw prompt display, raw provider payload display and raw birth data display.
- Explicit non-goals:
  - No React admin screen is implemented in this story.
  - No endpoint, serializer, model, migration or generated client is added.
  - No new role or broader support permission is introduced.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this admin UX/API design contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only a canonical architecture contract and CONDAMAD evidence for future admin implementation.
  - Runtime backend surfaces must remain unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the required admin/internal gate cannot be preserved.
- Additional validation rules:
  - The document must name the runtime endpoints proved through `app.openapi()` or `app.routes`.
  - The document must list forbidden sensitive fields using exact names from the source policies.
  - The document must state that future UI work is blocked without existing admin AuthN/AuthZ and audit logs.
  - Runtime proof must use `pytest` with `TestClient` coverage for current admin routes.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()` and `TestClient` prove the existing admin API surface. |
| Baseline Snapshot | yes | A before/after document check proves the only allowed surface delta is the new architecture contract. |
| Ownership Routing | yes | Canonical ownership is required because this story creates a design contract before UI work. |
| Allowlist Exception | no | No allowlist handling is authorized for this admin design story. |
| Contract Shape | yes | The UX/API contract must define screens, states, fields, actions and blocked data. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Public, B2C and broad support surfaces must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Admin flows are fully described. | Evidence profile: baseline_before_after_diff; `python` checks `docs/architecture/admin-audit-replay-flows.md`. |
| AC2 | Sensitive admin actions name audit events. | Evidence profile: json_contract_shape; `pytest -q backend/tests/api/admin/test_rejected_answer_review_workflow.py`. |
| AC3 | Forbidden sensitive fields are excluded. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks the admin flow document. |
| AC4 | Backend endpoints are named from runtime. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`. |
| AC5 | Internal admin access is a hard gate. | Evidence profile: route_absence_runtime; `pytest -q backend/tests/api/admin/test_replay_snapshot_v1_api.py`. |
| AC6 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |

## Implementation Tasks

- [ ] Task 1: Create `docs/architecture/admin-audit-replay-flows.md` with the mandatory global French file comment. (AC: AC1)
- [ ] Task 2: Map the existing admin endpoints for rejected answers, audit logs, replay metadata, replay attempt and purge. (AC: AC4)
- [ ] Task 3: Define screens for list, detail, replay metadata, replay attempt confirmation, purge confirmation and audit log review. (AC: AC1)
- [ ] Task 4: Define states `authorized`, `denied`, `expired`, `purged` and `incomplete` with visible user-facing admin outcomes. (AC: AC1)
- [ ] Task 5: Define visible columns and masked fields for rejected answer, audit detail and replay snapshot views. (AC: AC3)
- [ ] Task 6: Attach audit expectations to read, replay, purge and review-status actions. (AC: AC2)
- [ ] Task 7: Add explicit implementation-blocking gates for internal admin AuthN/AuthZ, audit logs and redaction. (AC: AC5)
- [ ] Task 8: Persist validation and source-alignment evidence under the story evidence directory. (AC: AC6)

## Files to Inspect First

- `_story_briefs/cs-304-design-admin-audit-and-replay-flows.md` - source brief.
- `backend/app/api/v1/routers/admin/audit.py` - audit log and replay snapshot runtime routes.
- `backend/app/api/v1/routers/admin/answer_audit.py` - rejected answer review runtime routes.
- `backend/app/api/v1/routers/admin/llm/observability.py` - LLM observability admin routes.
- `backend/app/services/api_contracts/admin/audit.py` - response models and review statuses.
- `docs/architecture/replay-snapshot-v1-storage-security-model.md` - replay sensitive-data boundary.
- `docs/architecture/replay-snapshot-v1-dpo-security-approval-request.md` - DPO/security controls.
- `_condamad/stories/CS-268-answer-audit-access-logs/evidence/final-runtime-closure.md` - access-log closure evidence.

## Runtime Source of Truth

- Primary source of truth:
  - `app.routes`, `app.openapi()` and `TestClient`.
- Secondary evidence:
  - Targeted `rg` scans for public routes and forbidden sensitive field display.
- Static scans alone are not sufficient for this story because:
  - The design contract must name only admin endpoints that are actually registered by the loaded app.

## Contract Shape

- Contract type:
  - Admin UX/API design contract.
- Fields:
  - `screen_id`: stable identifier for each admin flow screen.
  - `endpoint`: backend method and path consumed by the future admin UI.
  - `visible_fields`: fields allowed for display.
  - `masked_fields`: sensitive fields blocked or redacted from display.
  - `audit_event`: expected audit event for each sensitive action.
  - `blocked_gate`: implementation gate that prevents non-admin exposure.
- Required fields:
  - `screen_id`, `endpoint`, `visible_fields`, `masked_fields`, `audit_event`, `blocked_gate`.
- Optional fields:
  - `empty_state`, `error_state`, `confirmation_copy`.
- Status codes:
  - Existing backend endpoint status codes only; this story adds no runtime status code.
- Serialization names:
  - Document field names are emitted exactly as written in `docs/architecture/admin-audit-replay-flows.md`.
- Required flow sections:
  - rejected answer list and detail;
  - authorized audit details;
  - replay snapshot metadata;
  - controlled replay attempt;
  - manual audited purge;
  - review-status update.
- Required states:
  - `authorized`, `denied`, `expired`, `purged`, `incomplete`.
- Required action audit mapping:
  - read rejected answer list;
  - read rejected answer detail;
  - update rejected answer review status;
  - read replay snapshot metadata;
  - start replay attempt;
  - purge replay snapshot;
  - read audit logs.
- Forbidden UI data:
  - raw prompt;
  - raw provider payload;
  - raw AI answer;
  - raw birth date, time, place, latitude, longitude and timezone;
  - exact coordinates;
  - secrets, API keys, credentials and provider tokens;
  - direct identifiers not already masked by the backend contract.
- Frontend type impact:
  - none for this story.
- Generated contract impact:
  - none for this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-304-design-admin-audit-and-replay-flows/evidence/doc-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-304-design-admin-audit-and-replay-flows/evidence/doc-after.txt`
- Expected invariant:
  - The only intended repository surface delta is `docs/architecture/admin-audit-replay-flows.md` plus story evidence.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Admin flow design | `docs/architecture/admin-audit-replay-flows.md` | `frontend/src/**` |
| Admin API inventory | `docs/architecture/admin-audit-replay-flows.md` | generated frontend client |
| Runtime endpoint proof | `backend/tests/api/admin/**` and `app.openapi()` | public route code |
| Sensitive-data policy | existing architecture security docs | new ad hoc masking policy |

## Mandatory Reuse / DRY Constraints

- Reuse the current admin endpoints and contracts instead of inventing new route names.
- Reuse the DPO/security replay policy as the redaction source of truth.
- Reuse CS-268 and CS-294 access-log evidence for rejected answer audit expectations.
- Do not duplicate backend schemas in the document beyond the fields required for UI visibility and masking.

## No Legacy / Forbidden Paths

- No legacy route path may be added for this admin surface.
- No compatibility route path may be added for this admin surface.
- No fallback route path may be added for this admin surface.
- Forbidden route families: `/v1/replay_snapshot_v1`, `/v1/public/**`, `/v1/support/**`, `/api/replay_snapshot_v1`.
- Forbidden UI behavior: export massif, raw data browsing, automatic replay, client-facing replay and broad support access.
- Forbidden implementation route: creating frontend screens before this contract proves the internal admin gate.

## Reintroduction Guard

- `python` must assert that audit and replay paths containing `audit`, `replay` or `answer-audits` remain under `/v1/admin/`.
- `pytest` must keep `TestClient` coverage for rejected answer review and replay snapshot admin routes.
- `rg` must scan the architecture contract for forbidden raw field display language.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `Routeurs API v1` | Admin route inventory must stay on canonical API v1 paths. | `python` `app.routes`; targeted `pytest`. |
| RG-003 `Architecture des routes API v1` | Public exposure must remain outside the allowed surface delta. | `python` `app.openapi()`; `rg` scan. |
| RG-007 `Endpoints admin LLM observability` | Admin observability and replay flows remain internal. | `pytest` admin API tests; contract doc. |

Non-applicable examples:

- RG-047 frontend inline styles are not selected because no React or CSS file is in scope.
- RG-052 CSS namespace migration is not selected because this story does not touch frontend styles.
- RG-041 entitlement documentation is not selected because replay and audit admin flows are the local domain.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Runtime route inventory | `_condamad/stories/CS-304-design-admin-audit-and-replay-flows/evidence/route-inventory.txt` | Prove `app.routes` and admin-only paths. |
| OpenAPI inventory | `_condamad/stories/CS-304-design-admin-audit-and-replay-flows/evidence/openapi-admin-paths.txt` | Prove `app.openapi()` admin paths. |
| Sensitive-field scan | `_condamad/stories/CS-304-design-admin-audit-and-replay-flows/evidence/sensitive-field-scan.txt` | Prove forbidden raw fields are not UI-visible. |
| Validation output | `_condamad/stories/CS-304-design-admin-audit-and-replay-flows/evidence/validation.txt` | Keep final validation commands and outputs. |
| Source alignment | `_condamad/stories/CS-304-design-admin-audit-and-replay-flows/evidence/source-alignment.md` | Prove the final story matches the brief. |
| Review output | `_condamad/stories/CS-304-design-admin-audit-and-replay-flows/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this admin design story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/admin-audit-replay-flows.md` - canonical admin UX/API design contract.
- `_condamad/stories/CS-304-design-admin-audit-and-replay-flows/evidence/route-inventory.txt` - runtime route evidence.
- `_condamad/stories/CS-304-design-admin-audit-and-replay-flows/evidence/openapi-admin-paths.txt` - OpenAPI path evidence.
- `_condamad/stories/CS-304-design-admin-audit-and-replay-flows/evidence/sensitive-field-scan.txt` - sensitive-field evidence.
- `_condamad/stories/CS-304-design-admin-audit-and-replay-flows/evidence/validation.txt` - validation evidence.
- `_condamad/stories/CS-304-design-admin-audit-and-replay-flows/evidence/source-alignment.md` - source-alignment evidence.

Likely tests:

- `backend/tests/api/admin/test_rejected_answer_review_workflow.py` - covers rejected answer admin behavior and access logs.
- `backend/tests/api/admin/test_replay_snapshot_v1_api.py` - covers replay snapshot metadata, replay attempt and purge.
- `backend/tests/architecture/test_admin_replay_snapshot_v1_public_exposure.py` - covers replay public exposure boundary.

Files not expected to change:

- `frontend/src/**` - out of scope; no admin UI is implemented.
- `backend/app/api/**` - out of scope; no backend route is added.
- `backend/app/infra/**` - out of scope; no persistence or external adapter is touched.
- `backend/migrations/**` - out of scope; no schema change is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `python -B -c "from app.main import app; paths=app.openapi()['paths']; assert all(path.startswith('/v1/admin/') for path in paths if 'replay' in path or 'audit' in path)"`
- VC2: `python -B -c "from app.main import app; paths={getattr(route, 'path', '') for route in app.routes}; assert '/v1/admin/audit/replay_snapshot_v1/{snapshot_id}' in paths"`
- VC3: `pytest -q backend/tests/api/admin/test_rejected_answer_review_workflow.py backend/tests/api/admin/test_replay_snapshot_v1_api.py`
- VC4: `pytest -q backend/tests/architecture/test_admin_replay_snapshot_v1_public_exposure.py`
- VC5: `rg -n "raw prompt|raw provider payload|raw birth|exact coordinates|secret|API key|credential" docs/architecture/admin-audit-replay-flows.md`
- VC6: `python -B -c "from pathlib import Path; p=Path('docs/architecture/admin-audit-replay-flows.md'); assert p.exists() and 'blocked' in p.read_text(encoding='utf-8')"`
- VC7: `ruff format .`
- VC8: `ruff check .`
- VC9: `pytest -q`

All Python validation commands must run after `.\.venv\Scripts\Activate.ps1` and from `backend` when importing `app.main`.

## Regression Risks

- Future UI could expose internal debug data as a client-facing support feature.
- Replay attempt could be perceived as automatic repair rather than a controlled internal action.
- Purge could be implemented without an audit trail or with broad cascade semantics.
- Documentation could drift from runtime endpoints unless `app.openapi()` and `app.routes` evidence is captured.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep the implementation documentation-only unless the user explicitly authorizes frontend/admin UI work.
- Run Python commands only after activating `.\.venv\Scripts\Activate.ps1`.
- Store command outputs under `_condamad/stories/CS-304-design-admin-audit-and-replay-flows/evidence/`.

## References

- `_story_briefs/cs-304-design-admin-audit-and-replay-flows.md`
- `backend/app/api/v1/routers/admin/audit.py`
- `backend/app/api/v1/routers/admin/answer_audit.py`
- `backend/app/api/v1/routers/admin/llm/observability.py`
- `backend/app/services/api_contracts/admin/audit.py`
- `docs/architecture/replay-snapshot-v1-storage-security-model.md`
- `docs/architecture/replay-snapshot-v1-dpo-security-approval-request.md`
- `_condamad/stories/CS-268-answer-audit-access-logs/evidence/final-runtime-closure.md`
