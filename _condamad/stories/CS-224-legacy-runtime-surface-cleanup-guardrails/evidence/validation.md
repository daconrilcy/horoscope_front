## CS-224 Final Evidence

### Runtime surfaces
- Documented canonical and legacy runtime surfaces in `docs/architecture/astrology-runtime-surfaces.md`.
- `chart_objects` is documented as the canonical internal source.
- Legacy collections are retained as compatibility projections, public API projections or chart-level results.
- Required surfaces documented: `chart_objects`, `planet_positions`, `astral_points`, `houses`, `angles`, `aspects`, `dignity_results`, `dominance_result`, `advanced_conditions`, `fixed_star_conjunctions`.

### AC traceability
| AC | Evidence |
|---|---|
| AC1-AC3 | `backend/tests/architecture/test_chart_runtime_surface_documentation.py` passed. |
| AC4-AC8 | `backend/tests/architecture/test_chart_runtime_surface_guardrails.py` passed; scans captured below. |
| AC9-AC11 | `backend/tests/unit/domain/astrology/test_chart_runtime_surface_projections.py` passed. |
| AC12 | `backend/tests/unit/domain/astrology/test_natal_result_contract.py` passed. |
| AC13 | `backend/tests/integration/astrology/test_natal_public_contract_compatibility.py` passed; `app.routes` and `app.openapi()` checked via `TestClient`. |
| AC14 | `evidence/runtime-surface-removal-audit.md` records no deletion candidate classified `dead`. |
| AC15 | Full backend `pytest -q` passed, including golden tests. |
| AC16 | This file contains `CS-224 Final Evidence`. |

### Cleanup
- Removed or consolidated redundant builders/adapters where safe: none.
- Reason: no scanned runtime surface reached `dead` classification without public/API risk.
- No public API/front-breaking removal.
- Adjacent diff check: `git diff -- backend/app/api backend/app/infra backend/migrations frontend/src` is not empty because of pre-existing `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` changes outside CS-224. CS-224 did not modify API, infra, migrations or frontend.

### Guardrails
- Added architecture tests for direct legacy consumption.
- Strengthened the legacy-consumption AST guard after review so it recognizes any variable explicitly typed as `NatalResult`
  or assigned from `build_natal_result`, not only a local variable named `natal_result`.
- Added architecture tests for `object_type`-driven logic.
- Added guardrails against specialized builders.
- Added guardrails against local magic thresholds, with explicit existing-owner allowlist.

### Allowlist
| Surface / pattern | Allowed location | Reason |
|---|---|---|
| `natal_result.astral_points` | `backend/app/domain/astrology/interpretation/astral_point_interpretation.py` | Existing interpretation compatibility service; future migration story can move it to `chart_objects`. |
| `ChartObjectType.PLANET`, `ChartObjectType.ANGLE`, `ChartObjectType.FIXED_STAR` | `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` | Canonical projection owner assigning runtime object family. |
| `PlanetConditionSignalBuilder` | `backend/app/domain/astrology/condition/planet_condition_signal_builder.py` | Existing condition-signal builder, not a new object-family runtime builder. |
| `0.01`, `17.0`, `8.5` threshold hits | Existing owners listed in guardrail test | Existing ephemeris/aspect safety or named planetary-condition contract values. |

### Scans
- `rg -n "natal_result\.planet_positions|natal_result\.astral_points|natal_result\.advanced_conditions|natal_result\.dignities|natal_result\.dignity_results" backend\app\domain\astrology -g "*.py"`: one allowlisted hit in `interpretation/astral_point_interpretation.py`.
- `rg -n "natal_result\.fixed_star_conjunctions|natal_result\.houses|natal_result\.angles" backend\app\domain\astrology -g "*.py"`: PASS, no matches.
- `rg -n "object_type ==|\.object_type ==|ChartObjectType\.PLANET|ChartObjectType\.ANGLE|ChartObjectType\.FIXED_STAR" backend\app\domain\astrology -g "*.py"`: allowlisted builder assignments only.
- `rg -n "Planet.*Builder|Angle.*Builder|AstralPoint.*Builder|FixedStar.*Builder" backend\app\domain\astrology -g "*.py"`: existing `PlanetConditionSignalBuilder` allowlisted only.
- `rg -n "\b8\.5\b|\b17\b|\b0\.2833\b|\b0\.01\b" backend\app\domain\astrology -g "*.py"`: existing named/owner thresholds only; no new calculator threshold.

### Consistency
- Historical `planet_positions` remain coherent with `chart_objects`.
- Historical `dignities` remain coherent with `payloads.dignity`.
- Fixed star contacts remain coherent with `payloads.fixed_star_conjunctions`; no top-level public `fixed_star_conjunctions` field is introduced.
- `NatalResult` compatibility is preserved.
- `app.routes`, `app.openapi()` and a `TestClient` call to `/v1/astrology-engine/natal/calculate` show no intentional public API delta.
- The public TestClient check verifies `planet_positions`, `houses`, `astral_points`, `dignities`, `advanced_conditions` and `aspects`
  remain exposed while `chart_objects` stays internal.

### Validation
- Post-implementation alignment pass on 2026-05-23: brief, story, AC, implementation, tests and final evidence reviewed; only story status metadata was corrected from `ready-to-review` to `done`.
- Implementation review artifact: `_condamad/stories/CS-224-legacy-runtime-surface-cleanup-guardrails/generated/11-code-review.md`
  records 2 review iterations; the second review is clean.
- Review-cycle fix validation:
  - `.\.venv\Scripts\Activate.ps1; ruff format backend\tests\architecture\test_chart_runtime_surface_guardrails.py backend\tests\integration\astrology\test_natal_public_contract_compatibility.py`: PASS.
  - `.\.venv\Scripts\Activate.ps1; ruff check backend\tests\architecture\test_chart_runtime_surface_guardrails.py backend\tests\integration\astrology\test_natal_public_contract_compatibility.py`: PASS.
  - `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\architecture\test_chart_runtime_surface_guardrails.py backend\tests\integration\astrology\test_natal_public_contract_compatibility.py`: PASS, `4 passed, 3 deselected`.
- Fresh review validation:
  - `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\architecture\test_chart_runtime_surface_documentation.py backend\tests\architecture\test_chart_runtime_surface_guardrails.py backend\tests\unit\domain\astrology\test_chart_runtime_surface_projections.py backend\tests\unit\domain\astrology\test_natal_result_contract.py backend\tests\unit\domain\astrology\test_chart_object_runtime_architecture.py backend\tests\integration\astrology\test_natal_public_contract_compatibility.py`: PASS, `23 passed, 3 deselected`.
- Capsule preparation: skipped because `.agents/skills/condamad-dev-story/SKILL.md`, `condamad_prepare.py` and `condamad_validate.py` are absent.
- `.\.venv\Scripts\Activate.ps1; ruff format backend\tests\architecture\test_chart_runtime_surface_documentation.py backend\tests\architecture\test_chart_runtime_surface_guardrails.py backend\tests\unit\domain\astrology\test_chart_runtime_surface_projections.py backend\tests\integration\astrology\test_natal_public_contract_compatibility.py`: PASS.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\architecture\test_chart_runtime_surface_documentation.py backend\tests\architecture\test_chart_runtime_surface_guardrails.py backend\tests\unit\domain\astrology\test_chart_runtime_surface_projections.py backend\tests\unit\domain\astrology\test_natal_result_contract.py backend\tests\unit\domain\astrology\test_chart_object_runtime_architecture.py backend\tests\integration\astrology\test_natal_public_contract_compatibility.py`: PASS, `23 passed, 2 deselected`.
- `.\.venv\Scripts\Activate.ps1; Push-Location backend; ruff format .; ruff check .; Pop-Location`: PASS, `1548 files left unchanged`, `All checks passed!`.
- `.\.venv\Scripts\Activate.ps1; Push-Location backend; python -B -m pytest -q; Pop-Location`: PASS, `3061 passed, 1 skipped, 1181 deselected`.
- `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-224-legacy-runtime-surface-cleanup-guardrails\00-story.md`: PASS.
- `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-224-legacy-runtime-surface-cleanup-guardrails\00-story.md`: PASS.
- `git diff --check`: PASS, line-ending warnings only from existing worktree files.
- Cache cleanup: `.pytest_cache`, `backend/.pytest_cache`, `.ruff_cache` and `backend/.ruff_cache` removed after validation.

### Exceptions
- Registry gap for a future dedicated CS-224 guardrail is documented in the story; no `RG-149` was added.
- Worktree contains many pre-existing unrelated changes and deletions; CS-224 only relies on the files listed in this evidence.
