## CS-222 Final Evidence

### Runtime
- Fixed stars are represented as `ChartObjectRuntimeData` through `build_chart_object_runtime_data`.
- `FixedStarRuntimePayload` and `FixedStarConjunctionRuntimePayload` are available in the chart-object runtime contract.
- Eligible targets receive `payloads.fixed_star_conjunctions` after natal chart-object construction.
- Fixed star payload objects are excluded from conjunction targets even if an accidental capability flag is present.
- The requested review skill path `.agents/skills/condamad-review-fix-story/SKILL.md` was absent; the scoped story, generated review, and available CONDAMAD story validation scripts were used.

### Calculation
- Conjunctions are computed from `chart_objects` by `FixedStarConjunctionCalculator`.
- Fixed stars are selected through `payloads.fixed_star`.
- Targets are selected through `supports_fixed_star_conjunction`.
- Orbs are driven by `FixedStarConjunctionRulesRuntimeData` and `DEFAULT_FIXED_STAR_CONJUNCTION_MAX_ORB_DEG`.
- Distance uses the canonical normalized `angular_distance_deg` helper.

### Compatibility
- Existing public outputs are preserved by `SkipJsonSchema`/`exclude=True` on `NatalResult.chart_objects`.
- `app.routes` and `app.openapi()` check: `routes=221 schemas=544 chart_objects_in_openapi=False`.
- No interpretation text is introduced by the fixed star runtime payloads.
- Adjacent diff note: `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` has a fixed-star runtime mapping delta already present in this working tree; no API, frontend, migration, prediction, or interpretation diff was introduced during finalization.

### AC Traceability
- AC1-AC3: `test_fixed_star_runtime.py` validates non-narrative payloads, calculatory conjunction payloads, and empty tuple defaults.
- AC4: `test_chart_object_runtime_builder.py` validates fixed star chart-object projection.
- AC5-AC8: `test_fixed_star_selectors.py` validates payload/capability selection, fixed-star target exclusion, and explicit longitude errors.
- AC9-AC12: `test_fixed_star_conjunction_runtime.py` validates exact, within-orb, outside-orb, and 359/0 wrap behavior.
- AC13: `test_fixed_star_enricher.py` validates immutable enrichment.
- AC14-AC15: `test_natal_result_chart_objects.py` and `test_natal_result_contract.py` validate natal integration and public contract preservation.
- AC16-AC18: `test_chart_object_runtime_architecture.py` plus scans validate no object-type eligibility, no duplicate builders, no local magic thresholds outside rules, and no fixed-star narrative payload.
- AC19: this file contains `CS-222 Final Evidence`.

### Validation
- Brief-alignment pass 2026-05-23: code, story AC, tests and evidence were compared against `_story_briefs/cs-222-fixed-star-conjunction-runtime-from-chart-objects.md`.
- Brief-alignment correction 2026-05-23: `_condamad/stories/story-status.md` now uses a strict `Source` value equal to the source brief path.
- `story-status` strict Source lookup for `_story_briefs/cs-222-fixed-star-conjunction-runtime-from-chart-objects.md` -> `1 row`.
- `python -B -m pytest -q backend/tests/unit/domain/astrology/test_fixed_star_selectors.py backend/tests/unit/domain/astrology/test_fixed_star_conjunction_runtime.py backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` -> `22 passed`.
- `Push-Location backend; ruff format .; ruff check .; Pop-Location` -> `1533 files left unchanged`; `All checks passed!`.
- `Push-Location backend; ruff format --check .; ruff check .; Pop-Location` -> `1533 files already formatted`; `All checks passed!`.
- `python -B -m pytest -q backend/tests/unit/domain/astrology/test_fixed_star_runtime.py backend/tests/unit/domain/astrology/test_fixed_star_selectors.py backend/tests/unit/domain/astrology/test_fixed_star_conjunction_runtime.py backend/tests/unit/domain/astrology/test_fixed_star_enricher.py backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` -> `46 passed`.
- `Push-Location backend; python -B -m pytest -q; Pop-Location` -> `3037 passed, 1 skipped, 1177 deselected`.
- `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-222-fixed-star-conjunction-runtime-from-chart-objects\00-story.md` -> `PASS`.
- `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-222-fixed-star-conjunction-runtime-from-chart-objects\00-story.md` -> `PASS`.

### Guardrails
- `rg -n "object_type ==|\.object_type ==|ChartObjectType\.PLANET|ChartObjectType\.FIXED_STAR" backend/app/domain/astrology/fixed_stars backend/app/domain/astrology/builders -g "*.py"` -> hits only in the chart-object projection builder for object construction.
- `rg -n "\borb\s*<=\s*1\.0\b|\b1\.0\b|\b1\.5\b|\b2\.0\b" backend/app/domain/astrology/fixed_stars -g "*.py"` -> hit only the named default orb constant.
- `rg -n "meaning|interpretation|narrative|prompt|llm|good|bad|malefic|benefic" backend/app/domain/astrology/runtime backend/app/domain/astrology/fixed_stars -g "*.py"` -> hits only existing non-fixed-star runtime interpretation surfaces and `supports_interpretation`.
- `rg -n "fixed_star_catalog|FixedStarBuilder|PlanetFixedStarConjunctionBuilder" backend/app/domain/astrology -g "*.py"` -> `PASS: no matches`.
- Registry gap for a future dedicated CS-222 guardrail remains documented for follow-up outside this generation.
