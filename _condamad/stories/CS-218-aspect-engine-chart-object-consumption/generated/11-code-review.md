# CONDAMAD Code Review

## Review target

- Story: `CS-218-aspect-engine-chart-object-consumption`
- Capsule: `_condamad/stories/CS-218-aspect-engine-chart-object-consumption`
- Review date: 2026-05-22
- Current review/fix iterations: 1 review, 0 fix batch
- Prior resolved findings preserved in validation evidence: 4

## Inputs reviewed

- `00-story.md`
- `generated/03-acceptance-traceability.md`
- `generated/06-validation-plan.md`
- `generated/07-no-legacy-dry-guardrails.md`
- `generated/10-final-evidence.md`
- `evidence/validation.md`
- `_condamad/stories/regression-guardrails.md`
- `git status --short`
- `git diff`
- Changed backend implementation and tests.

## Diff summary

- Added `backend/app/domain/astrology/calculators/aspect_inputs.py` as the
  selector/projector boundary from `ChartObjectRuntimeData` to
  `AspectBodyRuntimeData`.
- Updated `backend/app/domain/astrology/natal_calculation.py` so natal aspect
  participants come from `chart_objects`, filtered by
  `capabilities.supports_aspects`, before calling `calculate_major_aspects`.
- Updated `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
  so astral point and angle aspect capability is explicit and configurable.
- Added and extended unit tests and architecture guards for selector/projector,
  natal runtime source, non-regression pairs, `NatalResult` collections and
  no-legacy constraints.
- Added CS-218 capsule evidence and `RG-145`.

## Review layers

- Diff integrity: PASS. Scope is limited to backend astrology domain, tests,
  CONDAMAD evidence, story status and regression guardrail registry.
- Acceptance audit: PASS. AC1-AC14 have code evidence and validation evidence.
- Validation audit: PASS. Required targeted tests, scans, lint, full backend
  suite, diff check and story validators were rerun after this review.
- DRY / No Legacy audit: PASS. No fallback, shim, alias, compatibility wrapper,
  specialized aspect builder or `object_type` business branch was introduced.
- Edge/security/data audit: PASS. Backend pure domain refactor; no API, DB,
  migration, frontend, auth, secret or external I/O surface changed.

## Findings

Aucun finding actionable dans la review courante.

## Prior resolved findings

The previous capsule evidence records four already-resolved issues:

- Projector longitude validation strengthened for non-finite and non-numeric
  values.
- AC8 runtime-source proof strengthened with a sentinel `ChartObjectRuntimeData`.
- AC9 pair inventory persisted and locked by test.
- AC6 now explicitly covers Mars.

These fixes remain covered by the current validation run.

## Acceptance audit

| AC | Status | Evidence |
|---|---|---|
| AC1-AC7 | PASS | `test_aspect_chart_object_inputs.py` proves selector, validation, duplicate rejection, projection and angle-capable calculation. |
| AC8-AC9 | PASS | `test_natal_aspects_include_points.py` proves natal flow consumes `chart_objects` and preserves stable aspect pairs. |
| AC10 | PASS | `test_natal_result_chart_objects.py` proves historical collections remain present and `chart_objects` remains internal. |
| AC11-AC12 | PASS | Architecture guard and scans prove no `object_type` branch or direct aspect-engine dependency on historical collections. |
| AC13 | PASS | `test_aspect_runtime_builder.py` and full backend suite passed; aspect rules were not changed. |
| AC14 | PASS | `RG-145` present in `_condamad/stories/regression-guardrails.md`. |

## Validation audit

Commands rerun after this review:

- `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_aspect_chart_object_inputs.py backend/tests/unit/domain/astrology/test_natal_aspects_include_points.py backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py`
  - PASS, 25 passed.
- `rg -n "object_type ==|\.object_type|ChartObjectType" backend/app/domain/astrology/calculators -g "*.py"`
  - PASS, zero hits.
- `rg -n "planet_positions|astral_points|angles|fixed_stars" backend/app/domain/astrology/calculators -g "*.py"`
  - PASS, classified hits only in `calculate_planet_positions` and its package export, outside the aspect-engine input boundary.
- `rg -n "PlanetAspectBodyBuilder|AngleAspectBodyBuilder|AstralPointAspectBodyBuilder|FixedStarAspectBodyBuilder" backend/app backend/tests -g "*.py"`
  - PASS, hits only in guard constants.
- `rg -n "RG-145" _condamad/stories/regression-guardrails.md`
  - PASS, registry row present.
- `git diff --check`
  - PASS, no whitespace errors; CRLF warnings only.
- `.\.venv\Scripts\Activate.ps1; Push-Location backend; ruff format .; ruff check .; Pop-Location`
  - PASS, 1517 files left unchanged; all checks passed.
- `.\.venv\Scripts\Activate.ps1; Push-Location backend; pytest -q; Pop-Location`
  - PASS, 2965 passed, 1 skipped, 1177 deselected.
- `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-218-aspect-engine-chart-object-consumption/00-story.md`
  - PASS.
- `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-218-aspect-engine-chart-object-consumption/00-story.md`
  - PASS, no missing required contract.
- `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-218-aspect-engine-chart-object-consumption/00-story.md`
  - PASS.
- `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-218-aspect-engine-chart-object-consumption/00-story.md`
  - PASS.

## DRY / No Legacy audit

- No duplicate active aspect-input path was added.
- The selector uses `capabilities.supports_aspects`; it does not branch on
  `object_type`.
- The projector is the only new `ChartObjectRuntimeData -> AspectBodyRuntimeData`
  conversion path.
- `natal_calculation.py` no longer imports or calls
  `build_aspect_body_from_position` for natal aspect inputs.
- `build_aspect_body_from_position` remains only as an existing helper in
  `aspects.py`, outside the migrated natal orchestration path.

## Feedback loop

- Decision: no-propagation.
- Reason: the current review found no reusable process, skill, AGENTS or
  guardrail learning beyond the CS-218-local evidence already recorded.

## Residual risks

Aucun risque restant identifie.

## Verdict

CLEAN
