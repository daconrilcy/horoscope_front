# Final Evidence — CS-401-refuser-padding-sources-vides

## Story status

- Validation outcome: PASS
- Ready for review: clean implementation review complete
- Story key: CS-401-refuser-padding-sources-vides
- Source story: `_condamad/stories/CS-401-refuser-padding-sources-vides/00-story.md`
- Source brief: `_story_briefs/cs-396-refuser-padding-semantique-lecture-natale-et-sources-vides.md`
- Capsule path: `_condamad/stories/CS-401-refuser-padding-sources-vides`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial git status: pre-existing dirty files under `.agents/skills/**`, `_condamad/run-state.json`, `_condamad/reports/**`, and CS-390 artifacts; left untouched.
- Tracker verification: row `CS-401` path and source brief matched the requested story and brief.
- Guardrails: `RG-150`, `RG-152`, `RG-155` applicable; `RG-041` non-applicable.
- Capsule repair: generated files were missing and repaired with `condamad_prepare.py --repair-generated-only`, then validated PASS.

## Capsule validation

- `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-401-refuser-padding-sources-vides`: PASS after repair.
- `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-401-refuser-padding-sources-vides --final`: PASS after final evidence synchronization.

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | Missing source raises `NarrativeChapterSourceMissingError` and is converted to `chapter_source_missing`. | Unit tests PASS. | PASS |
| AC2 | Builder and validator use `NARRATIVE_CHAPTER_ORDER`. | Unit tests PASS. | PASS |
| AC3 | Duplicate normalized narratives rejected. | Unit + `--long` integration PASS. | PASS |
| AC4 | Duplicate normalized titles rejected. | Unit tests PASS. | PASS |
| AC5 | Empty Basic/Premium sources rejected. | Unit tests PASS. | PASS |
| AC6 | Invalid semantic payloads are not returned by public GET/LIST. | `--long` integration PASS. | PASS |
| AC7 | `response.sections[0]` absent from natal generation code. | `rg` zero-hit PASS; architecture guard PASS. | PASS |
| AC8 | Contract doc states no padding, distinct chapters and required sources. | Documentation scan PASS. | PASS |
| AC9 | Evidence artifacts persisted. | Capsule final validation PASS. | PASS |

## Implementation review correction

- Iteration 1 finding: Pydantic `ValidationError` during narrative contract projection could continue as an accepted
  complete response without audited semantic rejection.
- Fix: `interpretation_service.py` converts that path to `narrative_semantic_integrity` with
  `narrative_contract_invalid`.
- Proof: unit test `test_complete_response_with_invalid_narrative_contract_is_rejected` plus fresh targeted validations.

## Files changed

- `backend/tests/unit/test_narrative_natal_reading_v1.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`
- `backend/tests/architecture/test_narrative_semantic_integrity_guard.py`
- `backend/docs/narrative-natal-reading-v1-contract.md`
- `_condamad/stories/CS-401-refuser-padding-sources-vides/**`
- `_condamad/stories/story-status.md`

## Files deleted

- none.

## Tests added or updated

- Unit tests for duplicate titles, canonical order through public validation, empty Basic/Premium sources, and invalid
  narrative contract rejection.
- Integration test for a persisted complete reading with duplicate narrative chapters staying out of public GET/LIST.
- Architecture guard preventing reintroduction of first-section source padding.

## Commands run

| Command | Working directory | Result |
|---|---|---|
| `ruff format tests\unit\test_narrative_natal_reading_v1.py tests\integration\test_natal_interpretation_rejected_public_boundary.py tests\architecture\test_narrative_semantic_integrity_guard.py` | `backend` | PASS |
| `ruff check .` | `backend` | PASS |
| `python -B -m pytest -q tests/unit/test_narrative_natal_reading_v1.py --tb=short` | `backend` | PASS, 13 passed |
| `python -B -m pytest -q --long tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short` | `backend` | PASS, 8 passed |
| `python -B -m pytest -q tests/architecture/test_narrative_semantic_integrity_guard.py tests/architecture/test_narrative_natal_reading_public_boundary.py --tb=short` | `backend` | PASS, 4 passed |
| `python -B -m pytest -q --long tests/unit/test_narrative_natal_reading_v1.py tests/integration/test_natal_interpretation_rejected_public_boundary.py tests/architecture/test_narrative_natal_reading_public_boundary.py tests/architecture/test_narrative_semantic_integrity_guard.py --tb=short` | `backend` | PASS, 25 passed |
| `python -B -c "from app.main import app; print(f'app_routes={len(app.routes)}')"` | `backend` | PASS, `app_routes=230` |
| `rg -n "response\\.sections\\[0\\]" backend/app backend/tests backend/docs` | repo root | PASS, exit 1 no matches |
| `rg -n "response\\.sections\\[0\\]" backend/app/services/llm_generation/natal` | repo root | PASS, exit 1 no matches |
| `rg -n "fallback = response\\.sections\\[0\\]" backend/app/services/llm_generation/natal` | repo root | PASS, exit 1 no matches |
| `rg -n "padding\|used_astrological_elements\|RG-155" backend/docs/narrative-natal-reading-v1-contract.md` | repo root | PASS |
| `condamad_validate.py _condamad/stories/CS-401-refuser-padding-sources-vides --final` | repo root | PASS |
| `condamad_story_validate.py _condamad/stories/CS-401-refuser-padding-sources-vides/00-story.md` | repo root | PASS |
| `condamad_story_lint.py --strict _condamad/stories/CS-401-refuser-padding-sources-vides/00-story.md` | repo root | PASS |

## Commands skipped or blocked

- Full backend pytest suite: skipped because capsule validation plan targets the narrative unit suite, public-boundary integration suite and architecture guards; broader run risk is residual only.
- Persistent local server run: skipped; app import/startup contract was verified via FastAPI app import with 230 routes and no server process left running.

## DRY / No Legacy evidence

- No compatibility shim, alias, fallback copy, or duplicate active path introduced.
- Existing source resolution remains in the builder; semantic checks remain centralized in `narrative_semantic_integrity.py`.
- `response.sections[0]` is absent from `backend/app`, `backend/tests` and `backend/docs`.
- `fallback = response.sections[0]` is absent from `backend/app/services/llm_generation/natal`.
- `RG-155` remains enforced by unit, integration, architecture and scan evidence.

## Diff review

- Scoped `git diff --check`: PASS.
- Scoped diff limited to tests, contract documentation and CS-401 evidence/status files.
- Note: `backend/docs/narrative-natal-reading-v1-contract.md` emits Git's LF-to-CRLF warning on this Windows checkout.

## Code review artifact

- `generated/11-code-review.md` refreshed as final implementation review evidence.
- Fresh review verdict after correction: CLEAN.

## Final worktree status

- Final `git status --short` recorded after validation.
- CS-401 changes are limited to story artifacts, narrative contract docs, targeted tests and the new architecture guard.
- Unrelated pre-existing dirty files remain outside CS-401 scope under `.agents/skills/**`, `_condamad/run-state.json`, `_condamad/reports/**`, and CS-390 artifacts.

## Remaining risks

- Historical padded readings may still need separate CS-398 remediation, as stated by the story non-goal.
- Integration tests require `--long`; the default fast run deselects `tests/integration/**` by project configuration.

## Suggested reviewer focus

- Verify the public-boundary deletion/hiding behavior for semantically invalid complete rows and the anti-padding architecture guard.
