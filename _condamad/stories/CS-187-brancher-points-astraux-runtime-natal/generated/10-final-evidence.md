# Final Evidence — CS-187-brancher-points-astraux-runtime-natal

## Story status

- Story key: CS-187-brancher-points-astraux-runtime-natal
- Validation outcome: PASS
- Final status: done
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-187-brancher-points-astraux-runtime-natal/`
- Review iterations: 2

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Initial dirty state included `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`, the CS-187 capsule path, and unrelated `docs/recherches astro/2026-05-18-calcul-theme-astrologique.md`.
- AGENTS instructions applied: backend commands run through the project venv, Python 3.13/FastAPI stack preserved, no branch created.
- Capsule note: `00-story.md` was reconstructed after a Windows case-insensitive path incident during capsule preparation; story validate/lint now pass.

## AC validation

| AC | Evidence | Status |
|---|---|---|
| AC1 | SQLAlchemy metadata and seed integrity tests cover `astral_point_*`. | PASS |
| AC2 | `seed_astral_point_defaults()` path retained and covered. | PASS |
| AC3 | Runtime dataclasses and repository expose `reference.astral_points`. | PASS |
| AC4 | Alias/variant FK integrity and counts covered. | PASS |
| AC5 | Resolver returns typed instructions; direct variants require DB `engine_key`. | PASS |
| AC6 | `calculate_astral_points()` returns normalized positions. | PASS |
| AC7 | `NatalResult.points` added; no flat node/lilith fields. | PASS |
| AC8 | `include_points_in_aspects` flows API -> service -> domain and has real aspect output coverage. | PASS |
| AC9 | Raw natal calculation has no editorial point profile/keyword dependency. | PASS |
| AC10 | `docs/tables-astral-points.md` documents the runtime contract. | PASS |
| AC11 | Before artifacts are real repository/service dumps from detached HEAD `989acc7a`; after artifacts are real repository/service dumps from the current implementation. | PASS |

## Runtime artifacts

| File | Source | Status |
|---|---|---|
| `evidence/astral-points-runtime-after.json` | `AstrologyRuntimeReferenceRepository(db).load("1.0.0")` on a freshly seeded SQLite DB. | PASS |
| `evidence/natal-payload-after.json` | `NatalCalculationService.calculate(...).model_dump(mode="json")`. | PASS |
| `evidence/astral-points-runtime-before.json` | `AstrologyRuntimeReferenceRepository(db).load("1.0.0")` in detached HEAD worktree `989acc7a`. | PASS |
| `evidence/natal-payload-before.json` | `NatalCalculationService.calculate(...).model_dump(mode="json")` in detached HEAD worktree `989acc7a`. | PASS |

## Files changed

| File | Purpose |
|---|---|
| `backend/app/domain/astrology/runtime/runtime_reference.py` | Add immutable astral point runtime contracts. |
| `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` | Map DB point rows to dataclasses. |
| `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py` | Load and validate astral points from DB. |
| `backend/app/services/prediction/reference_seed_service.py` | Align full-suite seed count for the two new DB-backed point aliases. |
| `backend/app/domain/astrology/astral_point_calculation_resolver.py` | Resolve point variants to typed calculation instructions. |
| `backend/app/domain/astrology/ephemeris_provider.py` | Add SwissEph point longitude support, including `SE_` key normalization. |
| `backend/app/domain/astrology/natal_calculation.py` | Add point positions and optional point aspects. |
| `backend/app/services/natal/calculation_service.py` | Propagate `include_points_in_aspects`. |
| `backend/app/services/api_contracts/public/astrology_engine.py` | Expose additive request option. |
| `backend/app/api/v1/routers/public/astrology_engine.py` | Pass the option to the service. |
| `docs/db_seeder/astrology/astral_point_aliases.json` | Add DB-backed lunar apogee SwissEph engine keys. |
| `backend/tests/factories/astrology_runtime_reference_factory.py` | Add point fixtures. |
| `backend/app/tests/unit/test_astral_point_seed_integrity.py` | Add seed integrity tests. |
| `backend/app/tests/unit/test_astral_point_repository.py` | Add runtime repository tests. |
| `backend/tests/unit/domain/astrology/test_astral_point_calculation_resolver.py` | Add resolver tests. |
| `backend/tests/unit/domain/astrology/test_natal_result_contains_configured_points.py` | Add natal point output tests. |
| `backend/tests/unit/domain/astrology/test_natal_aspects_include_points.py` | Add optional point-aspect tests. |
| `backend/app/tests/integration/test_natal_calculate_api.py` | Add API propagation coverage. |
| `backend/app/tests/unit/test_astrology_runtime_reference_guard.py` | Add no-legacy runtime guards. |
| `backend/app/tests/unit/test_astrology_runtime_reference_repository.py` | Add orphan point-code orb-rule validation coverage. |
| `backend/app/tests/unit/test_prediction_reference_repository.py` | Update expected point alias count. |
| `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md` | Realign exact SQL boundary line metadata for the touched astrology router. |
| `docs/tables-astral-points.md` | Add runtime contract documentation. |
| `_condamad/stories/CS-187-brancher-points-astraux-runtime-natal/**` | Add capsule, evidence, review records. |

## Commands run

| Command | Directory | Result |
|---|---|---|
| `ruff format <changed python files>` | `backend/` | PASS |
| `ruff check .` | `backend/` | PASS |
| `pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py app/tests/unit/test_astral_point_repository.py app/tests/unit/test_astrology_runtime_reference_guard.py tests/unit/domain/astrology/test_natal_aspects_include_points.py` | `backend/` | PASS, 17 passed |
| `pytest -q app/tests/unit/test_astral_point_seed_integrity.py app/tests/unit/test_astral_point_repository.py app/tests/unit/test_astrology_runtime_reference_repository.py app/tests/unit/test_prediction_reference_repository.py tests/unit/domain/astrology/test_astral_point_calculation_resolver.py tests/unit/domain/astrology/test_natal_result_contains_configured_points.py tests/unit/domain/astrology/test_natal_aspects_include_points.py app/tests/unit/test_astrology_runtime_reference_guard.py app/tests/unit/test_astrology_prediction_boundary.py app/tests/unit/test_natal_calculation_service.py app/tests/integration/test_natal_calculate_api.py::test_calculate_natal_passes_include_points_in_aspects` | `backend/` | PASS, 79 passed, 1 deselected |
| `pytest -q app/tests/unit/test_api_router_architecture.py::test_api_sql_boundary_debt_matches_exact_allowlist app/tests/unit/test_calibration_job.py::test_job_stores_raw_day app/tests/unit/test_percentile_calculator.py::test_calibration_injected_in_db` | `backend/` | PASS, 3 passed |
| `pytest -q` | `backend/` | PASS, 2634 passed, 1 skipped, 1176 deselected |
| `pytest -q app/tests/integration/test_natal_calculate_api.py::test_calculate_natal_passes_include_points_in_aspects tests/unit/domain/astrology/test_natal_aspects_include_points.py` | `backend/` | PASS, 3 passed, 1 deselected |
| No-legacy scans for flat point fields, local catalogs, runtime dict contracts, and editorial imports | `backend/` | PASS; only pre-existing non-point dict-contract hits classified |
| Runtime before evidence generation from detached HEAD worktree `989acc7a` using repository load and `NatalResult.model_dump(mode="json")` | `C:\dev\cs187-before-worktree\backend` | PASS |
| Runtime after evidence generation script using repository load and `NatalResult.model_dump(mode="json")` | repo root -> `backend/` | PASS |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py ...` | repo root | PASS |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict ...` | repo root | PASS |
| `git diff --check` | repo root | PASS; CRLF warnings only |
| `python -m uvicorn app.main:app --host 127.0.0.1 --port 8017` + `GET /openapi.json` | `backend/` | PASS |

## Review loop

- Iteration 1 finding fixed: aspect orb-rule validation did not reject orphan `source_point_code` / `target_point_code`; repository validation and regression test added.
- Evidence finding fixed: the before artifacts are now real runtime/service dumps from detached HEAD `989acc7a`, not reconstructed baselines.
- Full-suite validation findings fixed: prediction seed alias count aligned to 17 and exact SQL router allowlist line numbers realigned after the API field addition.
- Iteration 2 result: CLEAN, no actionable findings remain.

## Remaining risks

- Unrelated untracked `docs/recherches astro/2026-05-18-calcul-theme-astrologique.md` remains untouched.
