# Final Evidence - CS-425

## Story status

- Status: ready-to-review
- Date: 2026-06-01
- Source: `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/00-story.md`
- Source brief: `_story_briefs/cs-425-invalider-regenerer-lectures-basic-natal-degradees.md`

## Preflight

- Repository root: `C:\dev\horoscope_front`.
- Git present; pre-existing dirty `_condamad/run-state.json` observed before edits and preserved.
- Story row and source brief path matched `_condamad/stories/story-status.md`.
- Scoped guardrails classified: `RG-150`, `RG-152`, `RG-155`, `RG-157`, `RG-164`, `RG-165`, `RG-166`, `RG-167`, `RG-168`, `RG-169`, `RG-171`, `RG-172`.

## Capsule validation

- Initial capsule target missed generated files; repaired with `condamad_prepare.py --repair-generated-only`.
- Final helper validation: PASS after evidence/status synchronization.
- `generated/11-code-review.md` is explicitly marked obsolete/drafting-only for implementation evidence.

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | Editorial version field serialized by `BasicNatalInterpretationV2`; persisted Basic payload includes it. | Contract/cache tests | PASS |
| AC2 | Minimum version constant enforced by `load_basic_natal_interpretation_v2_from_payload`. | Old-version cache test | PASS |
| AC3 | Missing version cache case regenerates. | Missing-version cache test | PASS |
| AC4 | Old version cache case regenerates. | Old-version cache test | PASS |
| AC5 | Degraded baseline-token cache case regenerates; canonical token owner used. | Token cache test and scoped `rg` | PASS |
| AC6 | Clean compatible cache served without gateway call. | Compatible-cache test | PASS |
| AC7 | Eligible degraded cache rows are skipped and regenerated. | Parametrized cache regeneration test | PASS |
| AC8 | Corrective reserved rows stay hidden; non-corrective quota path remains controlled. | Rejected-boundary and quota tests | PASS |
| AC9 | Quota consumed only on accepted non-cached output; `check_and_consume` remains absent. | Quota test and zero-hit `rg` | PASS |
| AC10 | Rejected/audit rows remain hidden from public get/list. | Rejected-boundary integration suite | PASS |
| AC11 | Before/after degraded cache snapshots persisted. | Evidence file existence check | PASS |
| AC12 | No Basic batch/migration path introduced. | Zero-hit batch/migration `rg` | PASS |
| AC13 | Validation artifact persisted. | `evidence/validation.txt` and capsule validation | PASS |

## Files changed

- Backend contract/cache: `backend/app/domain/astrology/reading/basic_natal_contracts.py`, `backend/app/domain/astrology/reading/__init__.py`, `backend/app/services/llm_generation/natal/stored_interpretation_payload.py`.
- Backend DRY/guards: `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`, `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`, `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py`, `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py`.
- Tests: `backend/tests/integration/test_basic_natal_v2_cache_invalidation.py`, `backend/tests/unit/test_basic_natal_reading_contracts.py`.
- CONDAMAD: story status, generated evidence and `evidence/**`.

## Files deleted

- None. The accidental helper-created `_condamad/stories/cs-425` duplicate was removed before it became a tracked story artifact.

## Tests added or updated

- Updated `test_basic_natal_v2_cache_invalidation.py` for missing version, old version, degraded-token regeneration, compatible cache and token helper.
- Updated `test_basic_natal_reading_contracts.py` for editorial version serialization and token ownership.

## Commands run

- `ruff format <modified python files>`
- `ruff check .`
- `python -B -m pytest -q --long tests\integration\test_basic_natal_v2_cache_invalidation.py --tb=short` -> 6 passed
- `python -B -m pytest -q tests\unit\test_natal_chart_long_quota_on_acceptance.py --tb=short` -> 4 passed
- `python -B -m pytest -q --long tests\integration\test_natal_interpretation_rejected_public_boundary.py --tb=short` -> 8 passed
- `python -B -m pytest -q --long tests\integration\test_basic_natal_v2_pipeline.py --tb=short` -> 1 passed
- `python -B -m pytest -q tests\unit\test_basic_natal_narrative_validator.py --tb=short` -> 14 passed
- `python -B -m pytest -q --tb=short` -> 3678 passed, 2 skipped, 1266 deselected
- `python -B -c "from app.main import app; print(app.title)"` -> `horoscope-backend`
- Targeted `rg` scans for no `check_and_consume`, no Basic batch/migration path, editorial version markers and canonical degraded-token hits.

## Commands skipped or blocked

- None. Initial integration commands without `--long` were deselected by pytest policy and rerun with `--long`.

## DRY / No Legacy evidence

- No compatibility shim, alias, fallback route or batch migration was introduced.
- Degraded token detection has one canonical production owner: `BASIC_NATAL_DEGRADED_BASELINE_TOKENS`.
- `backend/alembic` is absent in this checkout; migration scan was run against existing `app tests` roots and passed.

## Diff review

- Diff scoped to backend Basic contract/cache/guard tests and CONDAMAD evidence/status.
- `_story_briefs/cs-425-invalider-regenerer-lectures-basic-natal-degradees.md` unchanged.
- Frontend unchanged.

## Final worktree status

- Story-owned changes are present in backend code/tests and `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/**`.
- Pre-existing `_condamad/run-state.json` remains dirty and was not reverted.

## Remaining risks

- Low: historical rows are not batch-migrated by design; they are classified at runtime and regenerated only when the existing corrective policy allows it.

## Suggested reviewer focus

- Verify that `basic_editorial_contract_version` is the intended durable version name and that runtime cache invalidation matches product expectations for historical Basic rows.
