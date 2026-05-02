# Dev Log

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: untracked `_condamad/audits/prompt-generation/` and `_condamad/stories/formalize-consultation-guidance-prompt-ownership/`; status warned on inaccessible pytest temp directories.
- AGENTS.md considered: root `AGENTS.md`.
- Regression guardrails read: `_condamad/stories/regression-guardrails.md`; applicable `RG-004`, `RG-006`, `RG-020`.

## Search evidence

- Inspected consultation and guidance services, canonical use case registry, prompt governance registry, prompt generation doc, guidance tests, governance tests.
- Confirmed runtime delegates consultation LLM work to `GuidanceService.request_contextual_guidance_async`.
- Confirmed no `consultation` family in `prompt_governance_registry.json`.

## Implementation notes

- Added documentation that consultations are a product subcase of `guidance_contextual`.
- Added test coverage for contextual placeholder contract and precheck refusal with no guidance call.
- Added governance guard rejecting `consultation_contextual` placeholder family.
- Added persisted routing before/after artifacts.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `pytest -q app/tests/unit/test_guidance_service.py app/tests/unit/test_consultation_generation_service.py tests/llm_orchestration/test_prompt_governance_registry.py` | FAIL then PASS | First failure corrected an invalid assumption about `resolve_placeholder_family`; rerun passed 46 tests. |
| `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\formalize-consultation-guidance-prompt-ownership\00-story.md` | PASS | Story structure valid. |
| `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\formalize-consultation-guidance-prompt-ownership\00-story.md` | PASS | Story lint valid. |
| `ruff check .` | PASS | No lint errors. |
| `ruff format --check .` | FAIL then PASS | First run required formatting `app/tests/unit/test_guidance_service.py`; after `ruff format`, check passed. |
| `pytest -q` | PASS | 3501 passed, 12 skipped. |

## Final `git status --short`

- Recorded in `10-final-evidence.md`.
