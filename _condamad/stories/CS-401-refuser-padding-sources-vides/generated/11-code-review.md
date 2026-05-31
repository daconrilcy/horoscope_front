# Implementation review - CS-401 refuser-padding-sources-vides

Verdict: CLEAN

## Review scope

- Story: `_condamad/stories/CS-401-refuser-padding-sources-vides/00-story.md`
- Source brief: `_story_briefs/cs-396-refuser-padding-semantique-lecture-natale-et-sources-vides.md`
- Tracker row: `_condamad/stories/story-status.md` row `CS-401`
- Guardrails: `RG-150`, `RG-152`, `RG-155`
- Reviewed surfaces: builder, validator, semantic integrity helper, service rejection path, public-boundary tests,
  architecture guard, contract documentation and persisted story evidence.

## Iteration 1 findings

- Fixed: Pydantic `ValidationError` during `narrative_natal_reading_v1` projection was logged and then allowed a complete
  interpretation to continue without an audited semantic rejection.

Resolution:

- `backend/app/services/llm_generation/natal/interpretation_service.py` now converts that path to a
  `narrative_semantic_integrity` rejection with `narrative_contract_invalid`.
- `backend/tests/unit/test_narrative_natal_reading_v1.py` covers a complete response with all source sections present but
  an invalid public narrative contract.

## Fresh review result

No remaining actionable implementation issue found against AC1-AC9.

- Missing source sections raise `NarrativeChapterSourceMissingError` and route to audited semantic rejection.
- Chapter order, duplicate narratives, duplicate titles and empty Basic/Premium sources are validated before persistence or
  re-exposure.
- Rejected or invalid complete payloads stay outside public GET/LIST surfaces.
- `response.sections[0]` and `fallback = response.sections[0]` are absent from bounded natal generation scans.
- Contract documentation states no padding, distinct chapters and required Basic/Premium sources.

## Validation evidence

All Python commands were run after `.\.venv\Scripts\Activate.ps1`.

```text
cd backend
ruff check .
All checks passed!

python -B -m pytest -q tests/unit/test_narrative_natal_reading_v1.py --tb=short
13 passed

python -B -m pytest -q --long tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short
8 passed

python -B -m pytest -q tests/architecture/test_narrative_semantic_integrity_guard.py tests/architecture/test_narrative_natal_reading_public_boundary.py --tb=short
4 passed

python -B -m pytest -q --long tests/unit/test_narrative_natal_reading_v1.py tests/integration/test_natal_interpretation_rejected_public_boundary.py tests/architecture/test_narrative_natal_reading_public_boundary.py tests/architecture/test_narrative_semantic_integrity_guard.py --tb=short
25 passed

python -B -c "from app.main import app; print(f'app_routes={len(app.routes)}')"
app_routes=230

rg -n "response\\.sections\\[0\\]" backend/app/services/llm_generation/natal
PASS: no matches

rg -n "response\\.sections\\[0\\]" backend/app backend/tests backend/docs
PASS: no matches

rg -n "fallback = response\\.sections\\[0\\]" backend/app/services/llm_generation/natal
PASS: no matches

python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-401-refuser-padding-sources-vides --final
CONDAMAD validation: PASS

python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-401-refuser-padding-sources-vides\00-story.md
CONDAMAD story validation: PASS

python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-401-refuser-padding-sources-vides\00-story.md
CONDAMAD story lint: PASS
```

## Propagation decision

No-propagation: the issue was local to this implementation path and is covered by a targeted regression test.

## Residual risk

Historical padded readings remain deferred to CS-398, as stated by the story non-goal.
