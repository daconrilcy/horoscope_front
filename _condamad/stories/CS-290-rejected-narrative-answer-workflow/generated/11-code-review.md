# Implementation Review CS-290 rejected-narrative-answer-workflow

Verdict: CLEAN

## Review Scope

- Story: `_condamad/stories/CS-290-rejected-narrative-answer-workflow/00-story.md`
- Source brief: `_story_briefs/cs-290-implement-rejected-narrative-answer-workflow.md`
- Tracker row: `_condamad/stories/story-status.md`
- Implementation files:
  - `backend/app/services/llm_generation/natal/rejected_answer_workflow.py`
  - `backend/app/services/llm_generation/natal/interpretation_service.py`
  - `backend/app/infra/db/repositories/llm/narrative_answer_audit_repository.py`
- Tests and guards:
  - `backend/tests/unit/test_rejected_narrative_answer_workflow.py`
  - `backend/tests/unit/test_rejected_narrative_answer_logging.py`
  - `backend/tests/integration/test_rejected_narrative_answer_audit.py`
  - `backend/tests/integration/test_rejected_narrative_answer_response.py`
  - `backend/tests/architecture/test_rejected_narrative_answer_boundary.py`

## Iteration 1 Finding

- RESOLVED: `build_rejected_narrative_answer_outcome_from_payload` returned `None` when a structured narrative payload had required
  sections but no `evidence_refs`, so an ungrounded answer could remain outside the CS-290 rejection workflow.

## Fix Evidence

- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` now validates missing or invalid `evidence_refs` as an empty
  proof list whenever section requirements exist, allowing CS-289 to classify the answer as `ungrounded`.
- `backend/tests/unit/test_rejected_narrative_answer_workflow.py` now covers missing `evidence_refs` on required sections.
- `backend/app/services/llm_generation/natal/interpretation_service.py` now keeps an explicit audit source payload so rejected audit hashes
  remain tied to the source answer payload when the client-facing persisted projection is controlled.

## Fresh Review Result

- AC1 through AC8: PASS; ungrounded required sections without proof now reject, store structured diagnostics, mask client content, log internally
  and do not add retry/manual publish behavior.
- AC9: PASS; runtime route and OpenAPI checks still show no rejected narrative public surface.
- AC10: PASS; architecture guard still finds one canonical workflow owner.
- AC11: PASS; evidence artifacts are present and tracker path/source brief match the requested story.

## Validation Results

- PASS: `ruff check .`
- PASS: `python -B -m pytest -q --tb=short`
  - Result: `3366 passed, 1 skipped, 1211 deselected`
- PASS: `python -B -m pytest -q tests\unit\test_rejected_narrative_answer_workflow.py tests\unit\test_rejected_narrative_answer_logging.py tests\integration\test_rejected_narrative_answer_audit.py tests\integration\test_rejected_narrative_answer_response.py tests\architecture\test_rejected_narrative_answer_boundary.py --tb=short`
  - Result: `8 passed, 2 deselected`
- PASS: `python -B -m pytest -q app\tests\unit\legacy_services\test_natal_interpretation_service_v2_refacto.py app\tests\integration\test_natal_free_short_variant.py --tb=short`
  - Result: `2 passed, 1 deselected`
- PASS: `python -B -c "from app.main import app; assert 'rejected_narrative_answer' not in str(app.openapi())"`
- PASS: `python -B -c "from app.main import app; assert all('rejected-narrative' not in getattr(r, 'path', '') for r in app.routes)"`
- PASS: `condamad_story_validate.py _condamad\stories\CS-290-rejected-narrative-answer-workflow\00-story.md`
- PASS: `condamad_story_lint.py --strict _condamad\stories\CS-290-rejected-narrative-answer-workflow\00-story.md`

## Review Output

- Final artifact: `_condamad/stories/CS-290-rejected-narrative-answer-workflow/generated/11-code-review.md`
- Tracker status: `done`
- Propagation decision: no-propagation; the correction is local to CS-290 workflow behavior and tests.

## Residual Risk

None identified.
