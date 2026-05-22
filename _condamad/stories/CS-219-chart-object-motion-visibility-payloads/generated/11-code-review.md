# Code Review

## Iteration 1

Verdict: CHANGES_REQUESTED

Accepted findings:

- MEDIUM: natal integration evidence did not directly prove motion payloads.
- LOW: architecture threshold guard omitted `17`.
- LOW: `00-story.md` status was still `ready-to-dev`.
- HIGH: builder fallback from raw `PlanetPosition` facts kept a non-canonical
  motion payload path alive.
- LOW: AC6 lacked a direct missing visibility payload validator test.

Rejected findings:

- None.

## Fix Evidence

- Removed motion fallback from raw `PlanetPosition` facts.
- Added natal integration proof for motion payloads with reliable speeds.
- Added direct visibility missing-payload validator test.
- Aligned threshold guard with story scan terms.
- Synchronized `00-story.md` status.

Validation after fixes:

- `pytest -q backend/tests/unit/domain/astrology/test_chart_object_motion_visibility_payloads.py backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` - PASS, `24 passed`.
- `ruff format .` from `backend` - PASS.
- `ruff check .` from `backend` - PASS.
- `pytest -q` from `backend` - PASS, `2978 passed, 1 skipped, 1177 deselected`.
- RG-146 scans - PASS or classified in `evidence/validation.md`.

## Iteration 2

Verdict: CHANGES_REQUESTED

Accepted findings:

- MEDIUM: `ChartObjectMotionPayload.source` still defaulted to
  `planet_position`, preserving an implicit legacy source for newly
  constructed motion payloads even after the builder fallback had been removed.

Rejected findings:

- None.

## Iteration 2 Fix Evidence

- Replaced the motion payload default source with
  `planetary_conditions.motion`.
- Made the validator regression test explicit about the canonical motion
  source.
- Synchronized `00-story.md` to `done` for closure.

Validation after fixes:

- `pytest -q backend/tests/unit/domain/astrology/test_chart_object_motion_visibility_payloads.py backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` - PASS, `24 passed`.
- `ruff format .` from `backend` - PASS, `1518 files left unchanged`.
- `ruff check .` from `backend` - PASS, `All checks passed`.
- `pytest -q` from `backend` - PASS, `2978 passed, 1 skipped, 1177 deselected`.
- Story validation and lint commands - PASS.
- `rg -n 'source="planet_position"|source: str = "planet_position"' backend/app backend/tests -g "*.py"` - PASS, zero hit.
- RG-146 scans - PASS or classified in `evidence/validation.md`.

## Iteration 3

Verdict: CLEAN.

Fresh review after iteration 2 found no remaining actionable findings.

## Final Verdict

CLEAN.

All accepted findings were fixed and validated. Feedback-loop routing:
`no-propagation`; the corrections are local CS-219 evidence/code issues already
covered by tests and `RG-146`.
