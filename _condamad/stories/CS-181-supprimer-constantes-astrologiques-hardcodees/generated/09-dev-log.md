# Dev Log

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Initial dirty files: `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`, CS-181 capsule, audit markdown.
- Applicable instructions: root `AGENTS.md`, CS-181 `00-story.md`, `regression-guardrails.md`.
- Story sufficiency gate: PASS, full-closure with exact batches, artifacts, guardrails and no residual in-domain work allowed.

## Implementation notes

- Removed natal mock fallback conversion from `NatalCalculationService`.
- Added runtime aspect resolver from loaded prediction context.
- Added `angle` and `family_code` to `AspectProfileData`.
- Replaced local aspect mappings in EventDetector, enriched event builder, transit/intraday builders and natal aspect orchestration.
- Added AST guard against reintroduced daily aspect mappings.

## First validation

- `pytest -q app/tests/unit/test_event_detector.py tests/unit/prediction/test_enriched_astro_events_builder.py app/tests/unit/test_natal_calculation_service.py` passed: 54 tests.
