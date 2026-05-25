# Delivery Report - CS-256 to CS-291

## 0. Report metadata

| Field | Value |
|---|---|
| Generated at | 2026-05-25 09:59:23 +02:00 |
| Repository | `c:\dev\horoscope_front` |
| Branch | `main` |
| Current HEAD | `5429f8712423d075c4c97a7cc831ef5e3434c19b` - `Add Condamad audit reports` |
| Commit range | Not evidenced |
| Stories covered | CS-256 through CS-291 |
| Source documents | `_condamad/stories/story-status.md`; `_condamad/stories/CS-*/00-story.md`; `_story_briefs/cs-256-*.md` through `_story_briefs/cs-291-*.md` |
| Diff source | Story-time final evidence; report-time `git status --short` before report creation and after report creation |
| Validation source | Story-time capsule evidence; no report-time application validation rerun |

## 1. Executive summary

This report covers 36 CONDAMAD stories from CS-256 to CS-291. Repository evidence supports 32 stories as `Delivered`, 1 as `Partially delivered`, 1 as `Requires business/QA validation`, and 2 as `Not evidenced` for implementation closure. The first report-time `git status --short` check returned no output before this report was written; final verification after report creation showed this new report plus unrelated `.agents/skills/**` modifications. Several story-time final evidence files also record that their implementation ran in a dirty worktree with unrelated pre-existing changes.

Final initiative status: `Partially delivered`.

The blocking and missing-evidence items are material: CS-262 and CS-284 are clean drafted stories but have no implementation final evidence; CS-268 is blocked by the absence, at that time, of the protected answer-audit consultation surface; CS-278 is intentionally blocked until external DPO/security approval resolves `DPO-REPLAY-SNAPSHOT-V1-RETENTION-001`.

## 2. Initial context and trigger

The story registry `_condamad/stories/story-status.md` lists CS-256 through CS-291 as a connected delivery set spanning public astrology projection contracts, projection builders, generic projection endpoint runtime, narrative answer audit, rejected answer workflow, admin/internal access policies, diagnostics, replay snapshot policy, and transit projections.

The source trigger for each story is the corresponding `_story_briefs/cs-*.md` file referenced in `_condamad/stories/story-status.md`. This report did not find one single initiative brief that names the whole CS-256 to CS-291 range; the initiative grouping is inferred from the user's requested range and the contiguous registry rows.

## 3. Story scope

| Story | Goal | AC source | Non-goals / exclusions |
|---|---|---|---|
| CS-256 | Define `structured_facts_v1` stable hashable fact projection. | `_condamad/stories/CS-256-structured-facts-v1-contract/00-story.md` | Final evidence says no builder, API route, DB migration, frontend or generated client added. |
| CS-257 | Define `beginner_summary_v1` deterministic B2C projection. | `_condamad/stories/CS-257-beginner-summary-v1-b2c-projection/00-story.md` | Documentation/contract story; local server start skipped with app import/OpenAPI checks used. |
| CS-258 | Define `client_interpretation_projection_v1` by plan. | `_condamad/stories/CS-258-client-interpretation-projection-v1-by-plan/00-story.md` | No runtime/API code changed per final evidence. |
| CS-259 | Define `narrative_answer_audit_v1` audit contract. | `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md` | Documentation-only; no public OpenAPI exposure. |
| CS-260 | Add `evidence_refs` contract and validation. | `_condamad/stories/CS-260-evidence-refs-contract-validation/00-story.md` | No public API exposure for proof internals. |
| CS-261 | Add rejection workflow policy for ungrounded narrative answers. | `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/00-story.md` | Application source surfaces unchanged. |
| CS-262 | Audit existing prompt version and answer id storage. | `_condamad/stories/CS-262-audit-existing-prompt-version-answer-id-storage/00-story.md` | Audit-only; application source changes forbidden. |
| CS-263 | Define generic projection endpoint contract. | `_condamad/stories/CS-263-generic-projection-endpoint-contract/00-story.md` | Runtime route intentionally absent at contract stage. |
| CS-264 | Persist projection payloads with `projection_hash`. | `_condamad/stories/CS-264-projection-persistence-projection-hash/00-story.md` | No API router/frontend change. |
| CS-265 | Define projection versioning and incompatibility policy. | `_condamad/stories/CS-265-projection-versioning-incompatibility-policy/00-story.md` | Runtime API surface unchanged. |
| CS-266 | Add OpenAPI internal/public exposure guards. | `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/00-story.md` | Scope is exposure guardrail, not feature runtime. |
| CS-267 | Define `admin_answer_audit_v1` admin API. | `_condamad/stories/CS-267-admin-answer-audit-api/00-story.md` | CS-268 evidence records this as declarative only at that time. |
| CS-268 | Add admin answer audit access logs. | `_condamad/stories/CS-268-answer-audit-access-logs/00-story.md` | Runtime implementation blocked by missing prerequisite surface. |
| CS-269 | Add rejected answer review workflow. | `_condamad/stories/CS-269-add-rejected-answer-review-workflow/00-story.md` | Final status includes review/fix closure. |
| CS-270 | Define internal role model. | `_condamad/stories/CS-270-internal-role-model/00-story.md` | Policy/role model scope. |
| CS-271 | Define admin data permission matrix. | `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md` | Permission matrix scope. |
| CS-272 | Define admin endpoint domain segmentation. | `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/00-story.md` | Final evidence status says pass after implementation review/fix. |
| CS-273 | Define `expert_technical_projection_v1` internal contract. | `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/00-story.md` | Internal expert/admin contract. |
| CS-274 | Define `astrology_full_data_v1` internal expert projection. | `_condamad/stories/CS-274-astrology-full-data-v1-internal-expert-projection/00-story.md` | Internal expert projection contract. |
| CS-275 | Decide admin chart diagnostics policy. | `_condamad/stories/CS-275-admin-chart-diagnostics-policy/00-story.md` | Policy before runtime diagnostics. |
| CS-276 | Implement `admin_chart_diagnostics_v1`. | `_condamad/stories/CS-276-admin-chart-diagnostics-v1/00-story.md` | Admin/internal diagnostics runtime. |
| CS-277 | Define replay snapshot storage and security model. | `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/00-story.md` | Final evidence leaves runtime implementation gated by approval. |
| CS-278 | Implement `replay_snapshot_v1` after approval. | `_condamad/stories/CS-278-replay-snapshot-v1-implementation/00-story.md` | Blocked before implementation because approval is absent. |
| CS-279 | Define `transit_chart_v1` internal manifest. | `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/00-story.md` | Manifest/contract scope. |
| CS-280 | Implement internal transit runtime. | `_condamad/stories/CS-280-internal-transit-runtime/00-story.md` | Internal runtime. |
| CS-281 | Define transit client projection by plan. | `_condamad/stories/CS-281-transit-client-projection-by-plan/00-story.md` | Public projection contract by plan. |
| CS-282 | Expose transit projection only after proof gate. | `_condamad/stories/CS-282-transit-projection-proof-gated-api/00-story.md` | Proof-gated exposure only. |
| CS-283 | Define B2C projection entitlement policy. | `_condamad/stories/CS-283-b2c-projection-entitlement-policy/00-story.md` | Policy; no Python app file modified per final evidence. |
| CS-284 | Define astrology disclaimer projection policy. | `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/00-story.md` | Story review says legal-policy drafting, UI, routes, DB, prompt rewrites and admin-only exposure are out of scope. |
| CS-285 | Implement `structured_facts_v1` builder. | `_condamad/stories/CS-285-structured-facts-v1-builder/00-story.md` | No route, OpenAPI, DB, migration or frontend file changed. |
| CS-286 | Implement `beginner_summary_v1` builder. | `_condamad/stories/CS-286-beginner-summary-v1-builder/00-story.md` | No frontend, API router, DB, migration, OpenAPI client or persistence path added. |
| CS-287 | Implement `client_interpretation_projection_v1` builder by plan. | `_condamad/stories/CS-287-client-interpretation-projection-v1-builder-by-plan/00-story.md` | No public route/OpenAPI exposure. |
| CS-288 | Implement `narrative_answer_audit_v1` persistence. | `_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/00-story.md` | No HTTP route/UI surface. |
| CS-289 | Implement `evidence_refs` section validation. | `_condamad/stories/CS-289-evidence-refs-section-validation/00-story.md` | No route/schema added for proof internals. |
| CS-290 | Implement rejected narrative answer workflow. | `_condamad/stories/CS-290-rejected-narrative-answer-workflow/00-story.md` | Frontend checks not applicable; no frontend file touched. |
| CS-291 | Implement generic projection endpoint runtime. | `_condamad/stories/CS-291-generic-projection-endpoint-runtime/00-story.md` | Frontend checks not applicable; no frontend files touched. |

## 4. Implementation summary

Projection contract and public projection groundwork:

- CS-256, CS-257 and CS-258 define public projection contracts and prove neutrality through `app.openapi()` / `app.routes` checks in each `generated/10-final-evidence.md`.
- CS-263 defines the generic projection endpoint contract while proving `/v1/astrology/projections` is absent at contract time through `TestClient` 404, OpenAPI and route assertions.
- CS-264 implements projection persistence with `PersistedProjectionModel.projection_hash` and service hash assignment; evidence is `_condamad/stories/CS-264-projection-persistence-projection-hash/generated/10-final-evidence.md`.
- CS-265 and CS-283 define versioning/incompatibility and B2C entitlement policy; both final evidence files record runtime API neutrality checks.

Narrative answer audit and rejection:

- CS-259 defines the `narrative_answer_audit_v1` contract and verifies it stays absent from OpenAPI.
- CS-260 and CS-289 define and then implement `evidence_refs` validation; CS-289 final evidence records targeted validation tests and duplicate-validator scans.
- CS-288 implements persistence by selecting `UserNatalInterpretationModel`, adding `projection_hash`, `llm_input_hash`, prompt/provider/model provenance fields, and validating with targeted tests plus full backend pytest.
- CS-290 implements rejected answer workflow in `backend/app/services/llm_generation/natal/rejected_answer_workflow.py`, wires it through `interpretation_service.py`, persists rejected audits in `narrative_answer_audit_repository.py`, and masks client responses.

Admin/internal policy and diagnostics:

- CS-266, CS-270, CS-271 and CS-272 establish OpenAPI exposure guards, internal roles, permission matrix and admin domain segmentation.
- CS-275 sets the admin chart diagnostics policy; CS-276 implements `admin_chart_diagnostics_v1`.
- CS-267 defines the admin answer audit API, but CS-268 evidence records that the protected runtime consultation surface was absent at the time CS-268 ran.

Replay and transit:

- CS-277 defines the replay snapshot storage/security model and explicitly gates runtime implementation on DPO/security approval.
- CS-278 stops before implementation because `approval_state` remains `non approuve` and blocker `DPO-REPLAY-SNAPSHOT-V1-RETENTION-001` is open.
- CS-279 through CS-282 cover internal transit manifest/runtime and proof-gated transit projection exposure.

Builder and endpoint runtime:

- CS-285, CS-286 and CS-287 implement the three projection builders with unit tests and API-neutrality checks.
- CS-291 implements `POST /v1/astrology/projections` through `backend/app/api/v1/routers/public/projections.py`, router registry registration, public schemas, `ProjectionEndpointService`, builder dispatch, entitlement enforcement and optional persistence through `ProjectionPersistenceService.persist_from_builder`.

## 5. Traceability matrix

| Story | Expected outcome | Initial need source | Implemented evidence | Validation evidence | Status |
|---|---|---|---|---|---|
| CS-256 | Stable `structured_facts_v1` contract. | `_story_briefs/cs-256-*.md` | Contract/docs evidence in CS-256 final evidence. | `ruff check .` PASS; full pytest `3236 passed, 1 skipped, 1182 deselected`; OpenAPI absence PASS. | Delivered |
| CS-257 | Deterministic beginner summary B2C projection contract. | `_story_briefs/cs-257-*.md` | CS-257 final evidence and product registry update. | `ruff check .`, `ruff format --check .`, full pytest `3236 passed, 1 skipped, 1182 deselected`. | Delivered |
| CS-258 | Client interpretation projection by plan contract. | `_story_briefs/cs-258-*.md` | CS-258 final evidence records no runtime/API code changed. | Targeted domain/architecture tests PASS; `ruff check .` PASS; OpenAPI absence PASS. | Delivered |
| CS-259 | Narrative answer audit contract. | `_story_briefs/cs-259-*.md` | CS-259 final evidence. | Architecture tests `15 passed`; full pytest `3236 passed, 1 skipped, 1182 deselected`; OpenAPI absence PASS. | Delivered |
| CS-260 | `evidence_refs` contract validation. | `_story_briefs/cs-260-*.md` | Evidence artifacts under CS-260. | `ruff check .` PASS; full pytest `3236 passed, 1 skipped, 1182 deselected`; architecture review fix `15 passed`. | Delivered |
| CS-261 | Rejection workflow policy for ungrounded answers. | `_story_briefs/cs-261-*.md` | CS-261 evidence says application source surfaces unchanged. | `ruff check .` PASS; full pytest `3236 passed, 1 skipped, 1182 deselected`; routes/OpenAPI checks PASS. | Delivered |
| CS-262 | Audit existing prompt version and answer id storage. | `_story_briefs/cs-262-*.md` | Not evidenced; only clean editorial story review exists. | Story validate/lint PASS in `generated/11-code-review.md`; no implementation `10-final-evidence.md`. | Not evidenced |
| CS-263 | Generic projection endpoint contract. | `_story_briefs/cs-263-*.md` | CS-263 final evidence; endpoint absent by design. | Architecture tests PASS; full pytest `3236 passed, 1 skipped, 1182 deselected`; TestClient 404 and OpenAPI absence PASS. | Delivered |
| CS-264 | Projection persistence and hash. | `_story_briefs/cs-264-*.md` | `PersistedProjectionModel.projection_hash`; projection persistence service. | Targeted tests `14 passed, 2 deselected`; full pytest `3243 passed, 1 skipped, 1184 deselected`; `ruff check .` PASS. | Delivered |
| CS-265 | Projection versioning and incompatibility policy. | `_story_briefs/cs-265-*.md` | CS-265 final evidence. | Runtime OpenAPI/routes checks and architecture pytest PASS. | Delivered |
| CS-266 | OpenAPI internal/public exposure guards. | `_story_briefs/cs-266-*.md` | CS-266 final evidence. | Final evidence records PASS. | Delivered |
| CS-267 | Admin answer audit API contract. | `_story_briefs/cs-267-*.md` | CS-267 final evidence; CS-268 cites it as declarative only. | Final evidence records PASS. | Delivered |
| CS-268 | Admin answer audit access logs. | `_story_briefs/cs-268-*.md` | Retention doc and CS-268 capsule/evidence only; runtime ACs blocked. | Runtime route/OpenAPI absence PASS; capsule validation PASS; full backend not run because no backend Python code changed. | Partially delivered |
| CS-269 | Rejected answer review workflow. | `_story_briefs/cs-269-*.md` | CS-269 final evidence records `PASS_AFTER_FINAL_ALIGNMENT_REVIEW_FIX`. | Final evidence records PASS after review/fix. | Delivered |
| CS-270 | Internal role model. | `_story_briefs/cs-270-*.md` | CS-270 final evidence. | Final evidence records PASS. | Delivered |
| CS-271 | Admin data permission matrix. | `_story_briefs/cs-271-*.md` | CS-271 final evidence. | Final evidence records PASS. | Delivered |
| CS-272 | Admin endpoint domain segmentation. | `_story_briefs/cs-272-*.md` | CS-272 final evidence. | Final evidence records PASS after implementation review/fix. | Delivered |
| CS-273 | Expert technical projection internal contract. | `_story_briefs/cs-273-*.md` | CS-273 final evidence. | Final evidence records passed. | Delivered |
| CS-274 | Astrology full data internal expert projection. | `_story_briefs/cs-274-*.md` | CS-274 final evidence. | Final evidence records PASS. | Delivered |
| CS-275 | Admin chart diagnostics policy. | `_story_briefs/cs-275-*.md` | CS-275 final evidence. | Final evidence records PASS. | Delivered |
| CS-276 | Admin chart diagnostics runtime. | `_story_briefs/cs-276-*.md` | CS-276 final evidence. | Final evidence records PASS. | Delivered |
| CS-277 | Replay snapshot storage/security model. | `_story_briefs/cs-277-*.md` | `docs/architecture/replay-snapshot-v1-storage-security-model.md`; CS-277 final evidence. | Final evidence records scoped PASS with implementation review; runtime held back. | Delivered |
| CS-278 | Replay snapshot runtime after approval. | `_story_briefs/cs-278-*.md` | Runtime implementation withheld by approval gate. | Approval scans PASS; replay OpenAPI/routes absence PASS; CS-277 blocker evidence cited. | Requires business/QA validation |
| CS-279 | Transit chart internal manifest. | `_story_briefs/cs-279-*.md` | CS-279 final evidence. | Final evidence records PASS. | Delivered |
| CS-280 | Internal transit runtime. | `_story_briefs/cs-280-*.md` | CS-280 final evidence. | Final evidence records PASS. | Delivered |
| CS-281 | Transit client projection by plan. | `_story_briefs/cs-281-*.md` | CS-281 final evidence. | Final evidence records PASS. | Delivered |
| CS-282 | Transit projection proof-gated API. | `_story_briefs/cs-282-*.md` | CS-282 final evidence. | Final evidence records PASS. | Delivered |
| CS-283 | B2C projection entitlement policy. | `_story_briefs/cs-283-*.md` | CS-283 final evidence. | `ruff check .` PASS; full pytest `3239 passed, 1 skipped, 1204 deselected`; OpenAPI/routes checks PASS. | Delivered |
| CS-284 | Astrology disclaimer projection policy. | `_story_briefs/cs-284-*.md` | Not evidenced; only clean editorial story review exists. | Story validate/lint PASS in `generated/11-code-review.md`; no implementation `10-final-evidence.md`. | Not evidenced |
| CS-285 | `structured_facts_v1` builder. | `_story_briefs/cs-285-*.md` | `structured_facts_v1_builder.py` and tests. | Targeted tests `7 passed` then `9 passed`; full pytest `3322 passed, 1 skipped, 1204 deselected`; OpenAPI absence PASS. | Delivered |
| CS-286 | `beginner_summary_v1` builder. | `_story_briefs/cs-286-*.md` | `beginner_summary_v1_builder.py` and tests. | Targeted test `8 passed`; full pytest `3330 passed, 1 skipped, 1204 deselected`; `ruff check .` PASS. | Delivered |
| CS-287 | `client_interpretation_projection_v1` builder. | `_story_briefs/cs-287-*.md` | `client_interpretation_projection_v1_builder.py` and tests. | Targeted test `9 passed`; full pytest `3339 passed, 1 skipped, 1204 deselected`; `ruff check .` PASS. | Delivered |
| CS-288 | Narrative answer audit persistence. | `_story_briefs/cs-288-*.md` | Model/repository/persistence changes in CS-288 final evidence. | Targeted CS-288 tests PASS; full pytest `3346 passed, 1 skipped, 1208 deselected`; OpenAPI smoke PASS. | Delivered |
| CS-289 | `evidence_refs` section validation. | `_story_briefs/cs-289-*.md` | `validate_evidence_refs_by_section` and tests. | Targeted tests `12 passed, 1 deselected`; full pytest `3358 passed, 1 skipped, 1209 deselected`; duplicate-validator scans PASS. | Delivered |
| CS-290 | Rejected narrative answer workflow. | `_story_briefs/cs-290-*.md` | `rejected_answer_workflow.py`, `interpretation_service.py`, audit repository and tests. | Targeted suite `7 passed, 2 deselected`; full backend pytest `3365 passed, 1 skipped, 1211 deselected`; OpenAPI/route neutrality PASS. | Delivered |
| CS-291 | Generic projection endpoint runtime. | `_story_briefs/cs-291-*.md` | Public router, registry, schemas, `ProjectionEndpointService`, tests, OpenAPI artifacts. | Targeted API/service tests `12 passed`; full pytest `3378 passed, 1 skipped, 1211 deselected`; local Uvicorn OpenAPI startup PASS. | Delivered |

## 6. Evidence of completion

### Code evidence

- `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`: CS-285 builder implementation for `structured_facts_v1`.
- `backend/app/domain/astrology/interpretation/beginner_summary_v1_builder.py`: CS-286 builder implementation for `beginner_summary_v1`.
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`: CS-287 builder implementation for plan-sensitive client interpretation projection.
- `backend/app/infra/db/repositories/llm/narrative_answer_audit_repository.py`: CS-288/CS-290 canonical persistence evidence for narrative answer audit and rejected records.
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py`: CS-290 rejected answer workflow owner.
- `backend/app/services/llm_generation/natal/interpretation_service.py`: CS-290 integration point between validation, audit persistence and controlled client response.
- `backend/app/api/v1/routers/public/projections.py`: CS-291 public `POST /v1/astrology/projections` route.
- `backend/app/api/v1/routers/registry.py`: CS-291 canonical router registration evidence.
- `backend/app/services/api_contracts/public/projections.py`: CS-291 public request/response schema evidence.
- `backend/app/services/projections/projection_endpoint_service.py`: CS-291 orchestration, chart resolution, builder dispatch, entitlement and persistence evidence.

### Test evidence

- `backend/tests/unit/domain/astrology/test_structured_facts_v1_builder.py`: CS-285 unit validation.
- `backend/tests/unit/domain/astrology/test_beginner_summary_v1_builder.py`: CS-286 unit validation.
- `backend/tests/unit/domain/astrology/test_client_interpretation_projection_v1_builder.py`: CS-287 unit validation.
- `backend/tests/unit/test_evidence_refs_validation.py`, `backend/tests/unit/test_evidence_refs_section_status.py`, `backend/tests/integration/test_narrative_answer_audit_evidence_refs.py`, `backend/tests/architecture/test_evidence_refs_validation_boundary.py`: CS-289 proof validation and boundary evidence.
- `backend/tests/unit/test_rejected_narrative_answer_workflow.py`, `backend/tests/unit/test_rejected_narrative_answer_logging.py`, `backend/tests/integration/test_rejected_narrative_answer_audit.py`, `backend/tests/integration/test_rejected_narrative_answer_response.py`, `backend/tests/architecture/test_rejected_narrative_answer_boundary.py`: CS-290 rejection/audit/logging/boundary evidence.
- `backend/tests/api/test_projection_endpoint.py`, `backend/tests/api/test_projection_authorization.py`, `backend/tests/api/test_projection_persistence_endpoint.py`, `backend/tests/api/test_projection_openapi.py`, `backend/tests/unit/services/test_projection_endpoint_service.py`: CS-291 endpoint runtime evidence.

### Documentation evidence

- `docs/architecture/replay-snapshot-v1-storage-security-model.md`: CS-277 approval state and replay runtime blocker evidence.
- `docs/architecture/admin-answer-audit-access-retention.md`: CS-268 retention uncertainty and no-parallel-owner evidence.
- CS-256 through CS-291 story capsules under `_condamad/stories/CS-*/generated/`: acceptance traceability, validation plans, guardrails and final evidence.

### Operational evidence

- `_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/openapi-before.json` and `openapi-after.json`: CS-291 route appears after runtime implementation.
- `_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/validation.txt`: CS-291 validation transcript.
- `_condamad/stories/CS-290-rejected-narrative-answer-workflow/evidence/validation.txt`: CS-290 validation transcript.
- Report-time `git status --short`: initial check before report creation returned no output; final verification after report creation showed this report as untracked plus unrelated `.agents/skills/**` modifications.

## 7. Validation results

| Command / source | Scope | Result | Evidence | Notes |
|---|---|---|---|---|
| Story-time `ruff check .` | full suite | PASS | Multiple final evidence files, including CS-256, CS-257, CS-259, CS-260, CS-264, CS-285 through CS-291 | Python commands are recorded as run with venv active in story evidence. |
| Story-time full backend `python -B -m pytest -q --tb=short` | full suite | PASS | CS-256/257/259/260/261/263: `3236 passed, 1 skipped, 1182 deselected`; CS-291: `3378 passed, 1 skipped, 1211 deselected` | Suite size increases across delivered stories. |
| CS-285 targeted builder tests | targeted | PASS | `_condamad/stories/CS-285-structured-facts-v1-builder/generated/10-final-evidence.md` | `7 passed`, then `9 passed` with doctrine-governance guard. |
| CS-286 targeted builder tests | targeted | PASS | `_condamad/stories/CS-286-beginner-summary-v1-builder/generated/10-final-evidence.md` | `8 passed`. |
| CS-287 targeted builder tests | targeted | PASS | `_condamad/stories/CS-287-client-interpretation-projection-v1-builder-by-plan/generated/10-final-evidence.md` | `9 passed`. |
| CS-288 targeted persistence tests | targeted | PASS | `_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/generated/10-final-evidence.md` | Targeted CS-288 tests PASS; full suite PASS. |
| CS-289 targeted evidence refs tests | targeted | PASS | `_condamad/stories/CS-289-evidence-refs-section-validation/generated/10-final-evidence.md` | `12 passed, 1 deselected` after alignment evidence correction. |
| CS-290 targeted rejection workflow tests | targeted | PASS | `_condamad/stories/CS-290-rejected-narrative-answer-workflow/generated/10-final-evidence.md` | `7 passed, 2 deselected`; full backend pytest PASS. |
| CS-291 targeted API/service tests | targeted | PASS | `_condamad/stories/CS-291-generic-projection-endpoint-runtime/generated/10-final-evidence.md` | API/service tests `12 passed`; route/OpenAPI assertions PASS. |
| CS-291 local Uvicorn startup | manual | PASS | `_condamad/stories/CS-291-generic-projection-endpoint-runtime/generated/10-final-evidence.md` | Startup on `127.0.0.1:8011` and `127.0.0.1:8012` with `/openapi.json`. |
| CS-268 runtime checks | targeted | PASS | `_condamad/stories/CS-268-answer-audit-access-logs/generated/10-final-evidence.md` | Route/OpenAPI absence proves blocker; runtime ACs remain blocked. |
| CS-278 approval and runtime neutrality checks | external / targeted | EXTERNALLY REQUIRED | `_condamad/stories/CS-278-replay-snapshot-v1-implementation/generated/10-final-evidence.md` | Approval missing; implementation intentionally withheld. |
| Report-time app validation | full suite | NOT RUN | This report | Report generation did not rerun tests or app startup. |
| CI validation | external | NOT RUN | Not evidenced | No CI output was inspected for this report. |

## 8. Deviations, limits and assumptions

### Deviations from story scope

- CS-268 deviates from runtime implementation expectation because the protected consultation surface and persisted answer-audit owner were absent at story time. Evidence: `_condamad/stories/CS-268-answer-audit-access-logs/generated/10-final-evidence.md`.
- CS-278 deviates by stopping before implementation because CS-277 approval remains `non approuve` and `DPO-REPLAY-SNAPSHOT-V1-RETENTION-001` is open. Evidence: `_condamad/stories/CS-278-replay-snapshot-v1-implementation/generated/10-final-evidence.md` and `docs/architecture/replay-snapshot-v1-storage-security-model.md`.
- CS-262 and CS-284 have clean editorial review artifacts only; implementation closure evidence is absent. Evidence: their `generated/11-code-review.md` files and absence of implementation `generated/10-final-evidence.md`.

### Known limits

- Some final evidence files use non-canonical validation labels such as `pass`, `passed`, `PASS.`, `PASS_AFTER_FINAL_ALIGNMENT_REVIEW_FIX`, and `blocked-by-missing-prerequisite`; this report normalizes them to delivery statuses while retaining the source wording as evidence.
- Several story-time final evidence files record pre-existing dirty worktrees. This report cannot reconstruct exact story preflight dirty state except from story evidence.
- No report-time test, lint or local startup command was executed. Validation is based on story-time evidence.
- Commit range is not evidenced; current HEAD is known, but the range implementing CS-256 through CS-291 was not established.

### Assumptions

- The user's requested range CS-256 to CS-291 is the initiative boundary.
- Story registry `done` means the story owner intended delivery closure unless contradicted by final evidence. This assumption is not applied to CS-262, CS-268, CS-278 or CS-284 because their evidence contradicts full implementation delivery.

## 9. Residual risks

- CS-262 implementation/audit execution is not evidenced. Impact: prompt version and answer id storage gaps may remain unknown before downstream audit/persistence decisions. Mitigation: implement CS-262 or produce its missing final evidence.
- CS-284 disclaimer policy implementation is not evidenced. Impact: projection disclaimer ownership and plan applicability may remain undocumented or inconsistent. Mitigation: implement CS-284 or produce its missing final evidence.
- CS-268 access-log runtime ACs remain blocked. Impact: protected admin answer-audit consultation may lack access logging until the canonical runtime surface exists. Mitigation: rerun CS-268 after confirming CS-288/CS-267 runtime dependencies are present.
- CS-278 replay runtime remains blocked by external DPO/security approval. Impact: replay snapshot runtime cannot be delivered without violating the CS-277 security gate. Mitigation: obtain written approval resolving `DPO-REPLAY-SNAPSHOT-V1-RETENTION-001`, then rerun CS-278.
- No CI artifact was inspected. Impact: local story-time validation may not reflect CI environment. Mitigation: attach CI run URLs/logs for the final delivery candidate.

## 10. Evidence gaps

- No `generated/10-final-evidence.md` exists for CS-262 in the inspected capsule.
- No `generated/10-final-evidence.md` exists for CS-284 in the inspected capsule.
- No single initiative source document tying CS-256 through CS-291 together was found; range grouping is user-specified and registry-inferred.
- No commit range or PR number was evidenced for the implementation set.
- No report-time lint/test/startup validation was run.
- No CI status or pipeline logs were inspected.

## 11. Recommended next actions

1. Execute or close CS-262 with a full CONDAMAD final evidence file, including storage inventory, gap classification against CS-259 and validation transcript.
2. Execute or close CS-284 with a full CONDAMAD final evidence file, including disclaimer inventory, policy document evidence and app-surface checks.
3. Re-evaluate CS-268 now that later persistence stories exist; either implement access logging against the canonical answer-audit consultation surface or keep it blocked with updated dependency evidence.
4. Obtain DPO/security approval for replay snapshot retention and update CS-277 before attempting CS-278 runtime implementation.
5. Run a final release validation pass after isolating unrelated worktree changes: backend `ruff check .`, backend `python -B -m pytest -q --tb=short`, and local app startup/OpenAPI smoke, all with the venv activated.
6. Attach CI evidence or create a PR/release checklist linking this report, current HEAD and validation run IDs.

## 12. Final delivery status

`Partially delivered`

The CS-256 to CS-291 initiative has strong delivery evidence for 32 stories, including builder implementations, narrative audit persistence, rejected answer workflow and the generic projection endpoint runtime. However, CS-262 and CS-284 are not evidenced beyond clean story drafting review, CS-268 is only partially delivered because runtime access logging was blocked by missing prerequisites, and CS-278 requires external DPO/security approval before runtime implementation. These gaps prevent a `Delivered` initiative status.
