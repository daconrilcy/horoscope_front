# CS-231 Final Evidence

## Capsule

- Story: `_condamad/stories/CS-231-runtime-boundary-guardrails-structural-vs-interpretive/00-story.md`.
- Brief source: `_story_briefs/cs-231-runtime-boundary-guardrails-structural-vs-interpretive.md`.
- Tracker check: `_condamad/stories/story-status.md` contains the same Path and brief source.
- Skill note: `.agents/skills/condamad-review-fix-story/SKILL.md` was requested but absent from this workspace. Review followed the story, brief, scoped guardrails and available project validations.
- Capsule note: no `condamad-review-fix-story` scripts were available under the requested skill path.

## AC Traceability

| AC | Evidence |
|---|---|
| AC1 | `test_structural_runtime_does_not_expose_interpretive_fields` in `backend/tests/architecture/test_astrology_runtime_boundary.py`; targeted structural token scan classified by allowlist. |
| AC2 | `test_interpretive_adapters_do_not_recalculate_structural_facts`; recalculation scan returned no matches in interpretation roots. |
| AC3 | `test_runtime_boundary_allowlist_entries_are_complete`; every allowlist entry contains path, owner, field, reason and permanence/temporary decision. |
| AC4 | `test_runtime_boundary_layers_are_documented`; `docs/architecture/astrology-runtime-surfaces.md` contains the CS-231 matrix and allowed paths. |
| AC5 | `test_historical_fixtures_are_excluded_by_explicit_paths`; exclusions are explicit for tests, fixtures and evidence. |
| AC6 | `test_structural_reference_contracts_do_not_require_interpretive_fields`; structural reference contracts do not require valence or energy fields. |
| AC7 | `test_future_structural_calculators_are_covered_by_explicit_zones`; `backend/app/domain/astrology/calculators` is part of the structural roots. |
| AC8 | `test_api_contract_neutrality.py`; `app.routes`, `app.openapi()` and `TestClient` evidence captured in `openapi-routes.md`. |

## Commands

All Python commands were run after `.\.venv\Scripts\Activate.ps1`.

| Command | Result |
|---|---|
| `ruff format backend\tests\architecture\test_astrology_runtime_boundary.py` | PASS, 1 file reformatted then unchanged on rerun. |
| `python -B -m pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py` | PASS, `7 passed in 0.49s`. |
| `ruff check backend\tests\architecture\test_astrology_runtime_boundary.py backend\tests\architecture\test_aspect_runtime_boundary.py backend\tests\architecture\test_chart_interpretation_input_boundary.py backend\tests\architecture\test_api_contract_neutrality.py` | PASS, all checks passed. |
| `python -B -m pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py backend/tests/architecture/test_aspect_runtime_boundary.py backend/tests/architecture/test_chart_interpretation_input_boundary.py backend/tests/architecture/test_api_contract_neutrality.py` | PASS, `20 passed in 3.52s`. |
| `ruff check backend` | PASS, all checks passed. |
| `python -B -m pytest -q backend/tests` | PASS, `862 passed, 201 deselected in 40.69s`. |
| local uvicorn smoke on `127.0.0.1:8765/openapi.json` | PASS, `status=200 bytes=543969` on 2026-05-23 rerun. |

## Review/Fix Cycle

Iteration 1 fresh review found one actionable implementation issue:

- The AST guard only matched forbidden identifiers by exact equality, while the
  raw structural scan still found `prompt_hint` in
  `backend/app/domain/astrology/runtime/runtime_reference.py`.

Corrections applied:

- The AST guard now catches forbidden tokens embedded in names, attributes and
  string constants.
- `PlanetConditionSignalProfileReferenceData` now exposes `signal_hint` to the
  structural runtime; the infra mapper still reads the legacy DB column
  `prompt_hint` and maps it at the boundary.
- The documentation owner for the `interpretive_weight` allowlist was aligned
  with the real code owner `AspectRuntimeWeightTaxonomy`.

Post-fix validations, all after `.\.venv\Scripts\Activate.ps1`:

| Command | Result |
|---|---|
| `python -B -m pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py` | PASS, `7 passed in 0.48s`. |
| `python -B -m pytest -q backend/tests/unit/domain/astrology/test_planet_condition_signal_builder.py backend/tests/unit/domain/astrology/test_signal_builder.py` | PASS, `9 passed in 0.56s`. |
| `ruff format backend` | PASS, `1567 files left unchanged`. |
| `ruff check backend` | PASS, all checks passed. |
| `python -B -m pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py backend/tests/architecture/test_aspect_runtime_boundary.py backend/tests/architecture/test_chart_interpretation_input_boundary.py backend/tests/architecture/test_api_contract_neutrality.py` | PASS, `20 passed in 4.98s`. |
| `python -B -m pytest -q backend/tests` | PASS, `862 passed, 201 deselected in 39.70s`. |
| `python -B -c "from fastapi.testclient import TestClient; from app.main import app; ..."` | PASS, `routes=197 openapi_paths=193 schemas=544 testclient_status=200 has_openapi=True`. |

Fresh post-fix review result:

- Structural token scan: PASS, remaining matches are limited to documented
  aspect-runtime allowlist entries; no `prompt` token remains in scanned
  structural runtime files.
- Interpretive recalculation scan: PASS, no matches.
- `git diff -- backend/app/api backend/alembic frontend/src`: PASS, no diff.
- Story status and tracker updated to `done` only after the clean review.

Implementation alignment review on 2026-05-23 found one additional stale test
expectation:

- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py` still
  asserted `condition_signal.prompt_hint` on the runtime reference contract after
  the structural contract had been renamed to `signal_hint`.

Correction applied:

- The app-level repository test now asserts `condition_signal.signal_hint`, while
  the infra mapper remains the boundary that reads the legacy DB column
  `prompt_hint`.

Post-correction validations, all after `.\.venv\Scripts\Activate.ps1`:

| Command | Result |
|---|---|
| `ruff format app/tests/unit/test_astrology_runtime_reference_repository.py` | PASS, `1 file left unchanged`. |
| `ruff check app/tests/unit/test_astrology_runtime_reference_repository.py app/tests/unit/test_chart_json_builder.py tests/architecture/test_astrology_runtime_boundary.py tests/architecture/test_api_contract_neutrality.py` | PASS, all checks passed. |
| `python -B -m pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py app/tests/unit/test_chart_json_builder.py tests/architecture/test_astrology_runtime_boundary.py tests/architecture/test_api_contract_neutrality.py` | PASS, `51 passed in 9.38s`. |
| `ruff check .` | PASS, all checks passed. |
| `python -B -m pytest -q tests` | PASS, `862 passed, 201 deselected in 40.49s`. |

## Scans

Structural token scan:

- Command: `rg -n "default_valence|interpretive_valence|energy_type|interpretive_weight|meaning|narrative|prompt|llm|OpenAI|AIEngineAdapter" backend/app/domain/astrology/calculators backend/app/domain/astrology/runtime backend/app/domain/astrology/builders backend/app/domain/astrology/dominance backend/app/domain/astrology/fixed_stars backend/app/domain/astrology/dignities backend/app/domain/astrology/planetary_conditions backend/app/domain/astrology/advanced_conditions -g "*.py"`.
- Result after review fix: matches are limited to allowlisted runtime aspect profile and legacy bridge entries; no `prompt` token remains in scanned structural runtime files.

Interpretive recalculation scan:

- Command: `rg -n -e "calculate_major_aspects|calculate_interchart_aspects|resolve_orb" -e "PlanetDominanceEngine\.calculate|FixedStarConjunctionCalculator" -e "EssentialDignityCalculator|AccidentalDignityCalculator" backend/app/domain/astrology/interpretation backend/app/domain/astrology/interpretation_adapters -g "*.py"`.
- Result: PASS, no matches (`rg` exit code 1 expected for absence).

Neutrality diff:

- Command: `git diff -- backend/app/api backend/alembic frontend/src`.
- Result: PASS, no diff.
