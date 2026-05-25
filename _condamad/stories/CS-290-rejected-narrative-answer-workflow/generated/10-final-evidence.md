# Final Evidence - CS-290

## Story status

- Story key: `CS-290-rejected-narrative-answer-workflow`
- Status: `done`
- Source story: `_condamad/stories/CS-290-rejected-narrative-answer-workflow/00-story.md`
- Source brief: `_story_briefs/cs-290-implement-rejected-narrative-answer-workflow.md`
- Source finding closure: `full-closure`

## Preflight

- `.git` exists; initial `git status --short` showed a dirty worktree unrelated to CS-290.
- Verified `story-status.md` row for CS-290 matches target path and source brief.
- Required generated files were missing; repaired the target capsule before reading generated context.
- An accidental `_condamad/stories/cs-290` capsule created by an initial helper run was removed after path verification.

## Capsule validation

- `condamad_prepare.py --repair-generated-only _condamad\stories\CS-290-rejected-narrative-answer-workflow --root C:\dev\horoscope_front`: PASS.
- `condamad_validate.py _condamad\stories\CS-290-rejected-narrative-answer-workflow`: PASS after final evidence format corrections.

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | `rejected_answer_workflow.py` builds a rejected outcome from CS-289 `ungrounded` validation. | Unit workflow test PASS. | PASS |
| AC2 | `NarrativeAnswerAuditRepository.create` persists rejected records on the canonical model. | Integration audit test PASS. | PASS |
| AC3 | Structured `rejection_reason` is required and stored. | Integration audit test PASS. | PASS |
| AC4 | CS-289 `validation_context` is required and stored. | Integration audit test PASS. | PASS |
| AC5 | Client payload and service mapping use controlled wording. | Response masking test PASS. | PASS |
| AC6 | Raw answer is internal-only under `raw_answer_storage`. | Response test and raw sentinel scan PASS. | PASS |
| AC7 | Internal log includes event, request, trace, answer, use case and reason. | Logging unit test PASS. | PASS |
| AC8 | Retry/manual publish/queue behavior absent; policy remains `out_of_scope`. | Architecture guard and retry scan PASS. | PASS |
| AC9 | Public API runtime surface unchanged. | OpenAPI and route runtime checks PASS. | PASS |
| AC10 | Single workflow owner exists. | Architecture guard PASS. | PASS |
| AC11 | Evidence artifacts persisted. | Evidence path checks PASS. | PASS |

## Files changed

- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/infra/db/repositories/llm/narrative_answer_audit_repository.py`
- `_condamad/stories/CS-290-rejected-narrative-answer-workflow/**`
- `_condamad/stories/story-status.md`

## Files deleted

- None.

## Tests added or updated

- `backend/tests/unit/test_rejected_narrative_answer_workflow.py`
- `backend/tests/unit/test_rejected_narrative_answer_logging.py`
- `backend/tests/integration/test_rejected_narrative_answer_audit.py`
- `backend/tests/integration/test_rejected_narrative_answer_response.py`
- `backend/tests/architecture/test_rejected_narrative_answer_boundary.py`

## Commands run

- `ruff format` on changed Python files: PASS.
- `ruff check app\services\llm_generation\natal\rejected_answer_workflow.py --fix`: PASS.
- `ruff check .`: PASS.
- Targeted CS-290 pytest suite: PASS, `7 passed, 2 deselected`.
- Full backend pytest: PASS, `3365 passed, 1 skipped, 1211 deselected`.
- Runtime OpenAPI and route neutrality assertions: PASS.
- Negative raw leakage and retry scans: PASS, no matches.

## Commands skipped or blocked

- Frontend checks skipped because no frontend file or generated client is in scope.

## DRY / No Legacy evidence

- No shim, alias, duplicate validator, duplicate persistence path, route or retry queue was added.
- CS-289 validation and CS-288 persistence are reused.
- `retry_policy` is stored as exact out-of-scope metadata, not executable retry behavior.

## Diff review

- Scoped diff/stat reviewed for CS-290 application, tests, evidence and story status paths.
- Existing dirty worktree outside CS-290 was left untouched.
- No brief source file was modified.

## Final worktree status

- CS-290 changed/untracked files remain for review.
- Other pre-existing modified/untracked files remain outside this story scope.

## Remaining risks

- Aucun risque restant identifie.

## Suggested reviewer focus

- Review the boundary between `rejected_answer_workflow.py` and `interpretation_service.py`, especially storing diagnostics inside the existing JSON audit payload rather than adding columns.

## Feedback Loop

- Status: `no-propagation`.

## Review/fix closure update

- Implementation review iterations: 2.
- Iteration 1 finding fixed: structured narrative payloads with required sections but missing `evidence_refs` could bypass CS-289 rejection
  because the workflow returned `None` before validating an empty proof list.
- Fix: `rejected_answer_workflow.py` now validates missing or invalid evidence refs as empty evidence when section requirements exist, and the
  unit suite covers that rejected path.
- Additional hardening: `interpretation_service.py` separates `audit_source_payload` from the controlled client persistence payload so rejected
  audit hashes remain tied to the source answer payload.
- Fresh review result: CLEAN; `_condamad/stories/story-status.md` updated to `done`.
- Final validation: `ruff check .`, full backend `pytest -q --tb=short`, targeted CS-290 tests, route/OpenAPI neutrality checks,
  `condamad_story_validate.py` and strict story lint all PASS.
