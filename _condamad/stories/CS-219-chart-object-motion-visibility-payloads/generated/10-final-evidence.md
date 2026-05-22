# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: no, closed after clean review
- Story key: `CS-219-chart-object-motion-visibility-payloads`
- Source story: `_condamad/stories/CS-219-chart-object-motion-visibility-payloads/00-story.md`
- Capsule path: `_condamad/stories/CS-219-chart-object-motion-visibility-payloads`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: pre-existing dirty files recorded before implementation.
- Pre-existing dirty files:
  - `_condamad/stories/regression-guardrails.md`
  - `_condamad/stories/story-status.md`
  - `docs/recherches astro/2026-05-22-synthese-calculs-astrologiques-post-cs-216.md`
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated for execution. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Generated for execution. |
| `generated/04-target-files.md` | yes | yes | PASS | Generated for execution. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Generated for execution. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Generated for execution. |
| `generated/10-final-evidence.md` | yes | yes | PASS | To complete after validation. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `ChartObjectMotionPayload` typed dataclass extended. | Payload tests passed. | PASS | No free dict payload. |
| AC2 | `ChartObjectVisibilityPayload` typed dataclass added with `is_visible`. | Payload tests passed. | PASS | Visibility can remain `None` when unknown. |
| AC3 | Builder maps `PlanetaryMotionCondition` only; raw position speed facts are not a normalized fallback source. | Payload tests and scans passed. | PASS | No motion calculator call or `planet_position` fallback source. |
| AC4 | Builder maps `PlanetaryConditionsBundle` solar facts. | Payload tests and scans passed. | PASS | No solar recalculation. |
| AC5 | Runtime validator requires motion payload when capability is true. | Existing and new validator tests passed. | PASS | |
| AC6 | Runtime validator requires visibility payload when capability is true. | Direct missing-payload validator test passed. | PASS | |
| AC7 | Runtime validator rejects payload without capability. | New validator tests passed. | PASS | |
| AC8 | `build_natal_result` passes advanced conditions to chart-object builder. | Natal chart object tests passed. | PASS | |
| AC9 | Astral points, angles and house cusps remain without motion/visibility when no source exists. | Builder and natal tests passed. | PASS | |
| AC10 | Historical fields remain present. | Integration tests and backend suite passed. | PASS | |
| AC11 | `chart_objects` remains excluded from model dump and OpenAPI schema. | OpenAPI/schema test passed. | PASS | |
| AC12 | Architecture guard verifies no business calculator branches on `object_type`. | Architecture tests and zero-hit scan passed. | PASS | |
| AC13 | No local magic thresholds in CS-219 builder/runtime. | Architecture test and threshold scan classification passed. | PASS | |
| AC14 | `RG-146` row exists. | `rg -n "RG-146" ...` passed. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` | modified | Extend payload contracts, set canonical motion source, and capability/payload validator. | AC1, AC2, AC5, AC6, AC7 |
| `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` | modified | Map existing motion/visibility conditions into chart objects without fallback to raw position facts. | AC3, AC4, AC8, AC9, AC13 |
| `backend/app/domain/astrology/natal_calculation.py` | modified | Compute advanced conditions before chart-object projection and pass them to the builder. | AC8, AC10, AC11 |
| `backend/tests/unit/domain/astrology/test_chart_object_motion_visibility_payloads.py` | added | Cover payload builders and validator. | AC1-AC7 |
| `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py` | modified | Cover advanced payload projection and non-applicable objects. | AC3, AC4, AC8, AC9 |
| `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py` | modified | Cover natal visibility payloads and public schema stability. | AC8, AC9, AC10, AC11 |
| `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` | modified | Add anti-calculator and anti-threshold guards. | AC12, AC13 |
| `_condamad/stories/CS-219-chart-object-motion-visibility-payloads/evidence/validation.md` | added | Persistent validation evidence. | AC14 |
| `_condamad/stories/CS-219-chart-object-motion-visibility-payloads/generated/*` | added/modified | CONDAMAD capsule and final evidence. | all |
| `_condamad/stories/story-status.md` | modified | Mark CS-219 ready for review after implementation. | all |

## Files deleted

None.

## Tests added or updated

- `backend/tests/unit/domain/astrology/test_chart_object_motion_visibility_payloads.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `pytest -q backend/tests/unit/domain/astrology/test_chart_object_motion_visibility_payloads.py backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` | repo root | FAIL then PASS | 1 then 0 | Missing import fixed; final rerun after review fixes `24 passed`. |
| `pytest -q backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py` | repo root | PASS | 0 | `36 passed`. |
| `ruff format .` | `backend` | PASS | 0 | Formatting applied locally, final run unchanged. |
| `ruff check .` | `backend` | PASS | 0 | All checks passed. |
| `pytest -q` | `backend` | PASS | 0 | Final rerun after review fixes: `2978 passed, 1 skipped, 1177 deselected`. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-219-chart-object-motion-visibility-payloads/00-story.md` | repo root | PASS | 0 | Story validation passed. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-219-chart-object-motion-visibility-payloads/00-story.md` | repo root | PASS | 0 | No missing required contracts. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-219-chart-object-motion-visibility-payloads/00-story.md` | repo root | PASS | 0 | Story lint passed. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-219-chart-object-motion-visibility-payloads/00-story.md` | repo root | PASS | 0 | Strict story lint passed. |
| `rg -n 'source="planet_position"\|source: str = "planet_position"' backend/app backend/tests -g "*.py"` | repo root | PASS | 1 | Zero hit; no implicit legacy payload source remains. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| None | no | No required command skipped before review. | None. | None. |

## DRY / No Legacy evidence

`RG-146` was verified. No `source="planet_position"` motion fallback remains.
Condition-term scan hits are expected existing
condition/calculator/profile names plus CS-219 payload mapping fields. The
calculator-call scan is zero-hit for builder/runtime. The object-type branch
scan is zero-hit. Magic-threshold hits are existing canonical thresholds or
unrelated orb/ayanamsa tolerances, with no hit in CS-219 builder/runtime.

## Diff review

`git diff --check` passed with no whitespace or conflict-marker errors.
Diff is scoped to CS-219 implementation/evidence plus pre-existing dirty
governance files already present before this task.

## Final worktree status

Expected story files are dirty. Pre-existing dirty files preserved:
`_condamad/stories/regression-guardrails.md`,
`_condamad/stories/story-status.md`, and
`docs/recherches astro/2026-05-22-synthese-calculs-astrologiques-post-cs-216.md`.

## Remaining risks

Aucun risque restant identifie.

## Suggested reviewer focus

Review that motion and visibility payloads are mapped from existing CS-209 to
CS-214 condition outputs without local recalculation or public schema changes.
