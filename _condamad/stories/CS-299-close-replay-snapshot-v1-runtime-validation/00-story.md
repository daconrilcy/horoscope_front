# Story CS-299 close-replay-snapshot-v1-runtime-validation: Close replay_snapshot_v1 Runtime Validation
Status: ready-to-review

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-299-close-replay-snapshot-v1-runtime-validation.md`.
- Required dependency: CS-295 through CS-298 must provide implementation evidence before CS-278 can move to `done`.
- Required dependency: CS-278 remains the parent runtime story for approved `replay_snapshot_v1` delivery closure.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: CS-278 cannot be closed until runtime proof, exposure scans, safety scans and delivery report updates are synchronized.
- Source-alignment evidence: PASS; final runtime proof, report update, no public exposure, forbidden-data scans and residual risks are covered.

## Objective

Close the approved `replay_snapshot_v1` runtime delivery by validating CS-295 through CS-298 evidence and synchronizing the CS-278 closure artifacts.

This story must not add functional runtime behavior. It must prove the existing runtime delivery, persist final evidence, update the delivery report and
leave CS-278 out of `done` when any runtime acceptance proof is missing.

## Target State

- CS-295 through CS-298 implementation evidence has been reviewed before CS-278 closure.
- `_condamad/stories/CS-278-replay-snapshot-v1-implementation/generated/10-final-evidence.md` records final runtime evidence.
- `_condamad/stories/story-status.md` marks CS-278 `done` only after all runtime acceptance proof is present.
- `_condamad/reports/CS-256-CS-291-delivery-report.md` reflects the final replay runtime status and residual risks.
- Backend lint and full backend tests pass from an activated virtual environment.
- `app.openapi()`, `app.routes` and `TestClient` evidence prove the replay surface stays internal.
- DB, log and test scans prove forbidden replay data is not persisted or emitted.
- No frontend, public client, generated client, role expansion, DPO policy change or new runtime behavior is introduced.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-299-close-replay-snapshot-v1-runtime-validation.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-299`.
- Evidence 3: `_condamad/stories/CS-278-replay-snapshot-v1-implementation/00-story.md` - parent runtime story inspected.
- Evidence 4: `_condamad/stories/CS-278-replay-snapshot-v1-implementation/generated/10-final-evidence.md` - approval status inspected.
- Evidence 5: CS-295 through CS-298 story files and editorial review artifacts were inspected as prerequisite closure evidence.
- Evidence 6: `docs/architecture/replay-snapshot-v1-dpo-security-approval-request.md` - approved DPO/security gate inspected.
- Evidence 7: `docs/architecture/replay-snapshot-v1-storage-security-model.md` - storage and security policy inspected.
- Evidence 8: `_condamad/reports/CS-256-CS-291-delivery-report.md` - current delivery report inspected.
- Evidence 9: `resolve_guardrails.py` - scoped resolver run for backend runtime closure, OpenAPI exposure and persistent evidence.
- Repository structure alert: backend, backend/app, backend/tests, docs, frontend and frontend/src exist in this workspace.
- Source-alignment evidence: PASS; no source concern was dropped, softened into a vague AC or replaced by cleanup work.

## Domain Boundary

- Domain: backend-runtime-validation
- In scope:
  - Final CS-278 runtime closure evidence for `replay_snapshot_v1`.
  - Review of CS-295, CS-296, CS-297 and CS-298 implementation evidence before closure.
  - Backend lint, full backend pytest, OpenAPI checks, route checks, TestClient proof, DB scans, log scans and test scans.
  - Delivery report update and residual-risk documentation for the replay runtime.
  - Tracker update for CS-278 only after runtime proof exists.
- Out of scope:
  - Frontend UI, generated clients, styling, i18n, build tooling, role taxonomy expansion and DPO/security policy changes.
  - New replay storage, service, API, execution logic, DB migration, purge behavior or audit feature implementation.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No new endpoint, service, table, migration, scheduled job, replay executor, frontend route, generated client or policy expansion.
  - No storage of raw prompts, raw birth data, exact coordinates, direct identifiers, secrets, credentials or raw provider payloads.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits final backend runtime validation and cross-story closure evidence.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Validate and document the delivered `replay_snapshot_v1` runtime without adding behavior.
  - Update CS-278 status to `done` only after CS-295 through CS-298 runtime acceptance proof is present.
  - Keep public routes, public OpenAPI, frontend, generated clients, role taxonomy and DPO/security policy unchanged.
  - Keep forbidden replay data out of DB records, logs, tests, API responses and persisted evidence.
  - Record residual risks instead of closing CS-278 when runtime proof is incomplete.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-295 through CS-298 are not implemented or their runtime evidence is incomplete.
- Additional validation rules:
  - The implementation must prove CS-295 through CS-298 evidence is complete before updating CS-278 to `done`.
  - The implementation must run full backend lint and pytest with the venv activated.
  - The implementation must prove `app.openapi()` contains only approved replay admin exposure.
  - The implementation must prove `app.routes` contains no public replay path.
  - The implementation must prove `TestClient` admin replay behavior is covered by the implemented tests.
  - The implementation must scan DB, logs and tests for forbidden replay data tokens.
  - The implementation must persist final evidence and delivery-report updates.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, `TestClient`, `app.routes`, `app.openapi()`, DB scans and log scans prove runtime closure. |
| Baseline Snapshot | yes | Before and after report and CS-278 evidence artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Closure evidence must stay in CS-278, the delivery report and story tracker. |
| Allowlist Exception | no | No broad allowlist handling is authorized for runtime closure. |
| Contract Shape | yes | Final evidence, report status, tracker state and residual-risk entries have exact required content. |
| Batch Migration | no | No migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Public replay exposure, forbidden data and premature `done` status must stay absent. |
| Persistent Evidence | yes | Final evidence, validation output, scans and report updates must be retained for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | CS-295 through CS-298 evidence is reviewed. | Evidence profile: baseline_before_after_diff; `python` checks the CS-295..CS-298 review artifacts. |
| AC2 | CS-278 final evidence records closure. | Evidence profile: baseline_before_after_diff; `python` checks CS-278 evidence and `app.routes`. |
| AC3 | CS-278 status changes only after proof. | Evidence profile: ast_architecture_guard; `python` checks tracker status and final evidence tokens. |
| AC4 | The delivery report reflects final replay state. | Evidence profile: baseline_before_after_diff; `rg` checks `_condamad/reports/CS-256-CS-291-delivery-report.md`. |
| AC5 | Backend lint passes. | Evidence profile: baseline_before_after_diff; `ruff check .` output is persisted in CS-299 validation evidence. |
| AC6 | Full backend pytest passes. | Evidence profile: json_contract_shape; `python -B -m pytest -q --tb=short` output is persisted. |
| AC7 | Runtime OpenAPI replay exposure is approved. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` for replay paths. |
| AC8 | Runtime routes expose no public replay path. | Evidence profile: route_absence_runtime; `python` checks `app.routes`; `rg` checks bounded route paths. |
| AC9 | Forbidden replay data is absent. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks DB, logs and tests for forbidden tokens. |
| AC10 | Persistent closure artifacts exist. | Evidence profile: baseline_before_after_diff; `python` checks CS-278 and CS-299 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-295 through CS-298 story files, review artifacts and final runtime evidence. (AC: AC1)
- [ ] Task 2: Inspect CS-278 current final evidence and identify every runtime AC still missing proof. (AC: AC2, AC3)
- [ ] Task 3: Run backend formatting, lint and full backend tests from an activated venv. (AC: AC5, AC6)
- [ ] Task 4: Run `app.openapi()`, `app.routes` and TestClient-backed checks for replay exposure. (AC: AC7, AC8)
- [ ] Task 5: Run bounded scans for forbidden replay data across DB model, logs and tests. (AC: AC9)
- [ ] Task 6: Update CS-278 final evidence with closure proof or an explicit blocker state. (AC: AC2, AC3, AC10)
- [ ] Task 7: Update `_condamad/reports/CS-256-CS-291-delivery-report.md` with final replay runtime status. (AC: AC4)
- [ ] Task 8: Update `_condamad/stories/story-status.md` for CS-278 only after runtime proof is complete. (AC: AC3)
- [ ] Task 9: Persist CS-299 validation and scan outputs under the CS-299 evidence folder. (AC: AC10)

## Files to Inspect First

- `_story_briefs/cs-299-close-replay-snapshot-v1-runtime-validation.md` - source brief.
- `_condamad/stories/CS-278-replay-snapshot-v1-implementation/00-story.md` - parent runtime closure contract.
- `_condamad/stories/CS-278-replay-snapshot-v1-implementation/generated/10-final-evidence.md` - current parent evidence.
- `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/00-story.md` - storage and redaction slice.
- `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/00-story.md` - lifecycle service slice.
- `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/00-story.md` - internal admin API slice.
- `_condamad/stories/CS-298-replay-snapshot-v1-execution-audit/00-story.md` - execution and audit slice.
- `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/generated/11-code-review.md` - story review evidence.
- `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/generated/11-code-review.md` - story review evidence.
- `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/generated/11-code-review.md` - story review evidence.
- `_condamad/stories/CS-298-replay-snapshot-v1-execution-audit/generated/11-code-review.md` - story review evidence.
- `docs/architecture/replay-snapshot-v1-dpo-security-approval-request.md` - DPO/security approval.
- `docs/architecture/replay-snapshot-v1-storage-security-model.md` - approved storage and security policy.
- `_condamad/reports/CS-256-CS-291-delivery-report.md` - delivery report to update.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - CS-278 final evidence and tracker status for runtime closure.
  - CS-295 through CS-298 implementation evidence for storage, service, API, execution and audit proof.
  - `pytest`, `TestClient`, loaded DB schema checks, `app.routes` and `app.openapi()` for runtime behavior.
  - Bounded `rg` scans for forbidden replay data in DB model, logs, tests and API responses.
- Secondary evidence:
  - Delivery report updates and residual-risk notes.
  - Persisted validation outputs under `_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/evidence`.
- Static scans alone are not sufficient because:
  - final closure depends on executable tests, loaded app routes, OpenAPI output and persisted runtime evidence.

## Contract Shape

- Contract type:
  - Backend runtime closure evidence and report synchronization for `replay_snapshot_v1`.
- Fields:
  - `story_id`: exact value `CS-278` for the parent runtime closure row.
  - `runtime_status`: `done` only after all CS-295 through CS-298 runtime proof exists.
  - `approval_decision_id`: exact value `DPO-REPLAY-SNAPSHOT-V1-RETENTION-001`.
  - `validation_commands`: backend lint, full pytest, OpenAPI, routes and forbidden-data scans.
  - `exposure_status`: approved internal admin exposure only, with no public replay path.
  - `residual_risks`: bounded list of unresolved risks or explicit `none identified`.
- Required fields:
  - `story_id`
  - `runtime_status`
  - `approval_decision_id`
  - `validation_commands`
  - `exposure_status`
  - `residual_risks`
- Optional fields:
  - none.
- Status codes:
  - Existing CS-297 admin API status behavior remains the HTTP source of truth.
- Serialization names:
  - Evidence headings and report labels must stay stable and reviewable in Markdown.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must keep replay snapshot operations inside the approved internal admin route family.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-278-replay-snapshot-v1-implementation/generated/10-final-evidence.md`
  - `_condamad/reports/CS-256-CS-291-delivery-report.md`
  - `_condamad/stories/story-status.md`
- Comparison after implementation:
  - `_condamad/stories/CS-278-replay-snapshot-v1-implementation/generated/10-final-evidence.md`
  - `_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/evidence/validation.txt`
  - `_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/evidence/runtime-surface-status.txt`
  - `_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/evidence/forbidden-data-scan.txt`
  - `_condamad/reports/CS-256-CS-291-delivery-report.md`
- Expected invariant:
  - The only intended delta is closure evidence, tracker synchronization, validation artifacts and delivery report updates.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Parent runtime closure | `_condamad/stories/CS-278-replay-snapshot-v1-implementation/generated/10-final-evidence.md` | New parent story |
| Story status | `_condamad/stories/story-status.md` | Per-story status note only |
| Delivery report | `_condamad/reports/CS-256-CS-291-delivery-report.md` | Untracked ad hoc summary |
| Runtime validation output | `_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/evidence/` | Application source folders |
| API exposure proof | loaded `app.routes`, `app.openapi()` and TestClient tests | Static route list only |
| Forbidden-data proof | bounded DB, log and test scans | Manual prose assertion |

## Mandatory Reuse / DRY Constraints

- Reuse CS-278 as the parent replay runtime closure artifact.
- Reuse CS-295 through CS-298 implementation evidence rather than duplicating runtime proof in a new feature story.
- Reuse the existing delivery report instead of creating a parallel closure report.
- Reuse the existing backend validation commands and TestClient tests for runtime behavior.
- Reuse DPO/security approval and storage model documents as policy sources.
- Do not duplicate replay runtime behavior, storage shape, route contracts, report formats or tracker state.

## No Legacy / Forbidden Paths

- No legacy replay closure path may mark CS-278 `done` without runtime proof.
- No compatibility closure path may bypass CS-295 through CS-298 evidence.
- No fallback closure path may rely on report prose alone.
- No new public replay route, frontend route, generated client, DB table, migration, service or scheduled job is authorized.
- No raw prompt, raw birth data, exact coordinate, direct identifier, secret, credential or raw provider payload may appear in DB, logs or tests.
- No delivery report update may state runtime delivered while any required proof remains missing.

## Reintroduction Guard

- Forbidden closure states:
  - CS-278 marked `done` without CS-295 through CS-298 runtime evidence.
  - Delivery report saying replay runtime is delivered while backend lint or full pytest failed.
  - Public `replay_snapshot_v1` path in `app.routes` or `app.openapi()`.
  - Forbidden replay data in DB models, logs, tests, API responses or persisted evidence.
- Required deterministic guards:
  - `ruff check .`
  - `python -B -m pytest -q --tb=short`
  - `python -B -c "from app.main import app; assert '/v1/astrology/projections' in app.openapi()['paths']"`
  - `$env:PYTHONPATH='backend'; python -c "from app.main import app; assert all('/admin/' in p for p in app.openapi()['paths'] if 'replay_snapshot_v1' in p)"`
  - `$env:PYTHONPATH='backend'; python -c "from app.main import app; assert not any(getattr(r,'path','') == '/replay_snapshot_v1' for r in app.routes)"`
  - `rg -n "raw_prompt|birth_date|birth_time|birth_place|latitude|longitude|email|password|api_key|payload_enc" backend/app backend/tests`

## Regression Guardrails

Scope vector:

- backend-runtime-validation: yes;
- operation type: create;
- paths: CS-278 through CS-299 story evidence, backend app, backend tests and delivery report;
- contracts: runtime validation, OpenAPI exposure, route exposure, forbidden-data scans and persistent evidence;
- frontend, i18n, style, build and broad migration: no.

Selected guardrails:

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend route surfaces must not gain public replay exposure. | `app.routes`; OpenAPI check. |
| RG-003 `architecture-routes-api-v1` | API v1 route ownership remains bounded during closure. | route scan; architecture tests. |
| RG-007 `admin-llm-observability` | Replay admin observability remains internal and protected. | TestClient tests; OpenAPI diff. |
Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is out of scope because replay closure does not change entitlement policy.
- RG-022 prompt-generation validation plans are out of scope because CS-299 is backend runtime closure, not prompt generation.

Registry gap:

- No exact `replay_snapshot_v1` runtime closure guardrail was returned by the scoped resolver.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| CS-278 final evidence | `_condamad/stories/CS-278-replay-snapshot-v1-implementation/generated/10-final-evidence.md` | Record parent runtime closure. |
| Validation output | `_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/evidence/validation.txt` | Keep lint and pytest output. |
| Runtime status | `_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/evidence/runtime-surface-status.txt` | Prove routes and OpenAPI. |
| Forbidden-data scan | `_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/evidence/forbidden-data-scan.txt` | Prove DB, log and test safety. |
| Report update notes | `_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/evidence/report-update.md` | Link report changes to proof. |
| Review output | `_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this runtime closure story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/stories/CS-278-replay-snapshot-v1-implementation/generated/10-final-evidence.md` - parent closure evidence.
- `_condamad/stories/story-status.md` - CS-278 and CS-299 status synchronization.
- `_condamad/reports/CS-256-CS-291-delivery-report.md` - final replay runtime status and residual risks.
- `_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/evidence/runtime-surface-status.txt` - route and OpenAPI proof.
- `_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/evidence/forbidden-data-scan.txt` - forbidden-data scan proof.
- `_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/evidence/report-update.md` - report traceability.

Likely tests:

- `backend/tests/api/admin/test_replay_snapshot_v1_api.py` - TestClient admin replay behavior and denial proof.
- `backend/tests/architecture/test_admin_replay_snapshot_v1_public_exposure.py` - public route and OpenAPI absence proof.
- `backend/tests/architecture/test_replay_snapshot_v1_execution_boundary.py` - bounded execution ownership proof.
- `backend/tests/unit/test_replay_snapshot_v1_execution_audit.py` - replay execution and audit proof.
- `backend/tests/integration/test_replay_snapshot_v1_service_purge.py` - purge behavior proof.
- `backend/tests/integration/test_replay_snapshot_v1_db_redaction.py` - persisted forbidden-data scan proof.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/**` - out of scope; runtime behavior must already be implemented by CS-295 through CS-298.
- `backend/migrations/**` - out of scope; migration work belongs to CS-295.
- `docs/architecture/replay-snapshot-v1-dpo-security-approval-request.md` - source approval should remain stable.
- `docs/architecture/replay-snapshot-v1-storage-security-model.md` - source policy should remain stable.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `python -B -c "from pathlib import Path; assert len(list(Path('_condamad/stories').glob('CS-29[5-8]-*/generated/11-code-review.md'))) == 4"`
- VC2: `ruff format .`
- VC3: `ruff check .`
- VC4: `python -B -m pytest -q --tb=short`
- VC5: `python -B -c "from app.main import app; assert '/v1/astrology/projections' in app.openapi()['paths']"`
- VC6: `$env:PYTHONPATH='backend'; python -c "from app.main import app; assert all('/admin/' in p for p in app.openapi()['paths'] if 'replay_snapshot_v1' in p)"`
- VC7: `$env:PYTHONPATH='backend'; python -c "from app.main import app; assert not any(getattr(r,'path','') == '/replay_snapshot_v1' for r in app.routes)"`
- VC8: `pytest -q backend/tests/api/admin/test_replay_snapshot_v1_api.py`
- VC9: `pytest -q backend/tests/architecture/test_admin_replay_snapshot_v1_public_exposure.py`
- VC10: `pytest -q backend/tests/architecture/test_replay_snapshot_v1_execution_boundary.py`
- VC11: `rg -n "raw_prompt|birth_date|birth_time|birth_place|latitude|longitude|email|password|api_key|payload_enc" backend/app backend/tests`
- VC12: `python -B -c "from pathlib import Path; assert Path('_condamad/stories/CS-299-close-replay-snapshot-v1-runtime-validation/evidence/validation.txt').exists()"`
- VC13: `rg -n "CS-278|replay_snapshot_v1|runtime|residual" _condamad/reports/CS-256-CS-291-delivery-report.md`

Before Python, ruff and pytest commands, activate the venv with `. .\.venv\Scripts\Activate.ps1`.
Run VC5 from `backend` or set `PYTHONPATH=backend` from the repository root. Persist outputs under the CS-299 evidence folder.

## Regression Risks

- CS-278 could be marked `done` before CS-295 through CS-298 runtime evidence exists.
- The delivery report could overstate replay delivery while lint, tests or exposure scans are incomplete.
- A public replay route or generated-client path could be introduced by CS-297 without final closure detection.
- DB rows, logs, tests or persisted evidence could contain raw replay-sensitive material.
- Residual replay risks could be omitted from the final report.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the backend virtual environment before every Python, ruff or pytest command.
- Do not add runtime behavior while closing this story.
- Mark CS-278 `done` only after all runtime proof and report updates are persisted.
- Keep documentation comments and public docstrings in French for new or significantly modified applicative files.
- Keep frontend, public API, generated client, role taxonomy, DPO/security policy and migrations unchanged.

## References

- `_story_briefs/cs-299-close-replay-snapshot-v1-runtime-validation.md`
- `_condamad/stories/CS-278-replay-snapshot-v1-implementation/00-story.md`
- `_condamad/stories/CS-278-replay-snapshot-v1-implementation/generated/10-final-evidence.md`
- `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/00-story.md`
- `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/00-story.md`
- `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/00-story.md`
- `_condamad/stories/CS-298-replay-snapshot-v1-execution-audit/00-story.md`
- `docs/architecture/replay-snapshot-v1-dpo-security-approval-request.md`
- `docs/architecture/replay-snapshot-v1-storage-security-model.md`
- `_condamad/reports/CS-256-CS-291-delivery-report.md`
- `_condamad/stories/regression-guardrails.md`
