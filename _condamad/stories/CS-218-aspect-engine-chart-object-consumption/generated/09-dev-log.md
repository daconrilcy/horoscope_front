# Dev Log

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/CS-218-aspect-engine-chart-object-consumption/00-story.md`
- Initial dirty files:
  - `_condamad/stories/regression-guardrails.md`
  - `_condamad/stories/story-status.md`
  - `docs/recherches astro/2026-05-22-synthese-calculs-astrologiques-post-cs-216.md`
- Applicable AGENTS: root `AGENTS.md`.
- Regression guardrails read: yes, `RG-144` and `RG-145` applicable.

## Baseline

- `pytest -q backend/tests/unit/domain/astrology/test_natal_aspects_include_points.py`: PASS, 3 passed.
- Baseline scan showed `natal_calculation.py` still used
  `aspect_source_positions`, `aspect_positions` and
  `build_aspect_body_from_position`.
- `backend/app/domain/astrology/calculators/aspects.py` contained the existing
  `build_aspect_body_from_position` helper and `calculate_major_aspects`.
- `object_type` scan in calculators: zero hit.

## Implementation Notes

- Added `AspectChartObjectSelector` and `AspectBodyProjector`.
- Moved `positions`, `points`, `houses` and `chart_objects` construction before
  natal aspect calculation.
- Preserved `include_points_in_aspects` by making astral-point aspect capability
  configurable in the chart-object builder.
- Kept angles outside the natal aspect pool by default to preserve existing
  public aspect outputs; unit tests still prove that an angle with
  `supports_aspects=True` can be selected and calculated.

## Validation Notes

- First full backend run failed two regression tests because angle inclusion
  changed existing outputs and triggered an unsupported school/orb path.
- Fix applied: natal builder call sets `include_angles_in_aspects=False`.
- Rerun targeted failed tests: PASS.
- Final full backend run: PASS, 2959 passed, 1 skipped.

## Review Fix Iteration 1

- Accepted Story Conformance findings:
  - AC9 baseline proof incomplete.
  - AC6 did not explicitly name Mars.
- Accepted Technical Risk findings:
  - Projector longitude validation was weaker than the old
    `AspectBodyRuntimeData.from_position` boundary.
  - AC8 proof could pass if old raw collections produced the same codes.
- Fixes:
  - Added finite/numeric longitude validation in `AspectBodyProjector`.
  - Added non-finite and non-numeric projector tests.
  - Added Mars to the chart-object calculation proof.
  - Added a sentinel chart-object flow test.
  - Added stable aspect-pair inventory test.
- Validation:
  - Targeted story tests PASS.
  - Final backend suite PASS, 2965 passed, 1 skipped.
- Feedback-loop routing: no-propagation; findings were local story evidence and
  boundary-test gaps fully resolved inside CS-218.
