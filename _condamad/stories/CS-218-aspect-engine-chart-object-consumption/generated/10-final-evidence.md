# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-218-aspect-engine-chart-object-consumption`
- Source story: `_condamad/stories/CS-218-aspect-engine-chart-object-consumption/00-story.md`
- Capsule path: `_condamad/stories/CS-218-aspect-engine-chart-object-consumption`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: pre-existing dirty
  `_condamad/stories/regression-guardrails.md`,
  `_condamad/stories/story-status.md`, and untracked research doc.
- AGENTS considered: `AGENTS.md`.
- Capsule generated: yes, missing generated files were created.
- Sufficiency gate: PASS; story is finite, non-audit, full implementation scope.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story intact. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Story-specific. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC14 mapped. |
| `generated/04-target-files.md` | yes | yes | PASS | Scope recorded. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Commands explicit. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | `RG-145` classified. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Complete. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `AspectChartObjectSelector.select` filters by `capabilities.supports_aspects`. | `test_aspect_chart_object_inputs.py` PASS. | PASS | |
| AC2 | Selector skips non-aspectable object without longitude. | `test_selector_ignores_non_aspectable_object_without_longitude` PASS. | PASS | |
| AC3 | Selector raises explicit `ValueError` for aspectable missing longitude. | `test_selector_rejects_aspectable_object_without_longitude` PASS. | PASS | |
| AC4 | Selector rejects duplicate normalized aspectable codes. | `test_selector_rejects_duplicate_aspectable_codes` PASS. | PASS | |
| AC5 | `AspectBodyProjector` is the unique `ChartObjectRuntimeData -> AspectBodyRuntimeData` projector. | Projector test + builder scan classified. | PASS | |
| AC6 | Natal participants match aspectable `chart_objects` for planets and optional points; Sun/Moon/Mars covered explicitly. | `test_aspect_chart_object_inputs.py` and `test_natal_aspects_include_points.py` PASS. | PASS | |
| AC7 | Unit calculation includes an aspectable `asc` angle when capability is true. | `test_calculation_consumes_projected_chart_objects_with_angle` PASS. | PASS | Natal default keeps angles out to preserve outputs. |
| AC8 | `build_natal_result` builds `chart_objects` before aspect calculation and a sentinel absent des collections historiques reaches the aspect pool. | `test_aspect_flow_consumes_chart_objects_runtime_source` PASS. | PASS | |
| AC9 | Existing planetary/point aspect behavior remains equivalent. | Stable pair inventory `(("conjunction", "jupiter", "mercury", 6.711141), ("conjunction", "mars", "moon", 0.578196))` + full backend suite PASS. | PASS | Initial angle-output regression fixed. |
| AC10 | `NatalResult` retains historical collections and internal `chart_objects`. | `test_natal_result_chart_objects.py` PASS. | PASS | |
| AC11 | No `object_type` branch in aspect calculators. | AST guard PASS; `rg` zero active hit. | PASS | |
| AC12 | Aspect engine modules do not consume historical collections directly. | AST guard PASS; broad scan hits only unrelated `calculate_planet_positions`. | PASS | |
| AC13 | Orb rules and aspect runtime contracts unchanged. | `test_aspect_runtime_builder.py` PASS; full backend suite PASS. | PASS | |
| AC14 | `RG-145` present. | `rg -n "RG-145" ...` PASS. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/domain/astrology/calculators/aspect_inputs.py` | added | Selector/projector chart-object aspects. | AC1-AC7 |
| `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` | modified | Configurer les capacites aspects points/angles pour le flux natal. | AC8-AC10 |
| `backend/app/domain/astrology/natal_calculation.py` | modified | Brancher les aspects sur `chart_objects`. | AC6-AC10 |
| `backend/tests/unit/domain/astrology/test_aspect_chart_object_inputs.py` | added | Tests selector/projector/calcul. | AC1-AC7 |
| `backend/tests/unit/domain/astrology/test_natal_aspects_include_points.py` | modified | Spy du flux depuis `chart_objects`. | AC8-AC9 |
| `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` | modified | Guard anti-retour aspect engine. | AC11-AC12 |
| `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py` | modified | Non-regression collections et capacites natales. | AC10 |
| `_condamad/stories/CS-218-aspect-engine-chart-object-consumption/generated/*` | added | Capsule execution/evidence. | all |

## Files deleted

- Aucun.

## Tests added or updated

- Added `backend/tests/unit/domain/astrology/test_aspect_chart_object_inputs.py`.
- Updated:
  - `test_natal_aspects_include_points.py`
  - `test_chart_object_runtime_architecture.py`
  - `test_natal_result_chart_objects.py`

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_natal_aspects_include_points.py` | repo root | PASS | 0 | Baseline 3 passed. |
| `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_aspect_chart_object_inputs.py` | repo root | PASS | 0 | 10 passed after review fixes. |
| `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_natal_aspects_include_points.py` | repo root | PASS | 0 | 5 passed after review fixes. |
| `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` | repo root | PASS | 0 | 3 passed. |
| `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py` | repo root | PASS | 0 | 4 passed. |
| `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py` | repo root | PASS | 0 | 3 passed. |
| `.\.venv\Scripts\Activate.ps1; Push-Location backend; ruff format .; ruff check .; Pop-Location` | repo root | PASS | 0 | Format/lint OK. |
| `.\.venv\Scripts\Activate.ps1; Push-Location backend; pytest -q; Pop-Location` | repo root | FAIL then PASS | 1 then 0 | First run found angle-output regressions; final run after all review fixes 2965 passed, 1 skipped. |
| `.\.venv\Scripts\Activate.ps1; python - <<inventory script>>` | repo root | PASS | 0 | Aspect pair inventory: `(("conjunction", "jupiter", "mercury", 6.711141), ("conjunction", "mars", "moon", 0.578196))`. |
| `rg -n "object_type ==|\.object_type|ChartObjectType" backend/app/domain/astrology/calculators -g "*.py"` | repo root | PASS | 1 | Zero hits. |
| `rg -n "planet_positions|astral_points|angles|fixed_stars" backend/app/domain/astrology/calculators -g "*.py"` | repo root | PASS | 0 | Hits only unrelated `calculate_planet_positions` symbol. |
| `rg -n "PlanetAspectBodyBuilder|AngleAspectBodyBuilder|AstralPointAspectBodyBuilder|FixedStarAspectBodyBuilder" backend/app backend/tests -g "*.py"` | repo root | PASS | 0 | Hits only test guard constants. |
| `rg -n "RG-145" _condamad/stories/regression-guardrails.md` | repo root | PASS | 0 | Registry row present. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; CRLF warnings only. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-218-aspect-engine-chart-object-consumption/00-story.md` | repo root | PASS | 0 | Story validation PASS. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-218-aspect-engine-chart-object-consumption/00-story.md` | repo root | PASS | 0 | No missing contracts. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-218-aspect-engine-chart-object-consumption/00-story.md` | repo root | PASS | 0 | Story lint PASS. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-218-aspect-engine-chart-object-consumption/00-story.md` | repo root | PASS | 0 | Strict lint PASS. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| Frontend validation | no | Story backend-only, no `frontend/**` change. | None. | Backend full suite and scans. |

## DRY / No Legacy evidence

- No new fallback, alias, shim, re-export or compatibility wrapper.
- `object_type` calculator scan: zero active hit.
- Historical collection scan classification:
  - `backend/app/domain/astrology/calculators/natal.py::calculate_planet_positions`:
    existing planet-position calculator, not aspect-engine input.
  - `backend/app/domain/astrology/calculators/__init__.py`: export of same
    existing calculator, not aspect-engine input.
- Specialized builder scan classification:
  - hits in `test_chart_object_runtime_architecture.py` are guard constants.
- `build_aspect_body_from_position` remains in `aspects.py` for existing callers
  outside CS-218, but `natal_calculation.py` no longer imports or calls it.

## Diff review

- Scope limited to backend astrology domain, tests and CS-218 evidence.
- No frontend, API, infra, migration or public JSON builder changes.
- Existing pre-story dirty registry/status changes are in-scope for CS-218
  tracking and `RG-145`.

## Final worktree status

- Fresh review completed on 2026-05-22 with verdict `CLEAN`.
- `_condamad/stories/story-status.md` records CS-218 as `done` with last update
  `2026-05-22`.

## Remaining risks

- None identified for implementation review.

## Suggested reviewer focus

- Confirm that keeping angles out of the natal default pool is the right
  preservation choice while the selector/projector still supports angle-capable
  inputs.
- Confirm `build_aspect_body_from_position` can remain as a non-natal helper
  outside the CS-218 migration scope.
