# CONDAMAD Code Review

## Review target

- Story: `CS-179-fermer-i18n-prediction-astrologique`
- Capsule: `_condamad/stories/CS-179-fermer-i18n-prediction-astrologique/`
- Closure class: full-closure
- Review/fix iterations in this session: 2

## Inputs reviewed

- `00-story.md`
- `prediction-i18n-before.md`
- `prediction-i18n-after.md`
- `generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md`
- Current `git diff --stat`, `git diff --check`, status, and changed files
- Runtime and test call sites for `PublicPredictionAssembler`,
  `AstrologerPromptBuilder`, `PublicAstroDailyEventsPolicy`,
  `PublicAstroFoundationPolicy`, and `PublicTimeWindowPolicy`

## Diff summary

- Prediction runtime no longer owns FR mappings for planets, signs, aspects,
  houses or effect labels.
- API/service entry points resolve labels outside `domain/prediction` and inject
  them into projection and prompt code.
- Tests now reuse `app/tests/helpers/prediction_astro_labels.py` for the fake
  label contract.
- V4 integration tests selected by `--long` now inject `astro_labels`.

## Findings

### CR-001 High - V4 integration tests did not inject required astro labels

- Bucket: patch
- Location: `backend/tests/integration/test_v4_scenarios.py:47`,
  `backend/tests/integration/test_v4_migration.py:50`
- Source layer: validation / acceptance
- Evidence: `pytest --long -q tests/integration/test_v4_scenarios.py tests/integration/test_v4_migration.py`
  failed with `TypeError: PublicPredictionAssembler.assemble() missing 1 required
  keyword-only argument: 'astro_labels'`.
- Impact: the story made `astro_labels` required to prevent silent fallback, but
  long integration coverage for the V4 payload was stale and would fail in the
  integration lane.
- Suggested fix: inject the shared test label contract into every V4 assembler
  integration call and keep it in a helper outside `test_*.py`.
- Resolution: fixed in `backend/tests/integration/test_v4_scenarios.py`,
  `backend/tests/integration/test_v4_migration.py`,
  `backend/tests/llm_orchestration/__init__.py`, and
  `backend/app/tests/helpers/prediction_astro_labels.py`.
- Verification: `pytest --long -q tests/integration/test_v4_scenarios.py tests/integration/test_v4_migration.py`
  now passes, 6 tests.

## Acceptance audit

| AC | Status | Evidence |
|---|---|---|
| AC1 baseline inventory | PASS | `prediction-i18n-before.md` present and reviewed. |
| AC2 public vocabulary convergence | PASS | Forbidden symbol scans under `app/domain/prediction` have zero hits. |
| AC3 prompt builder labels | PASS | `tests/unit/prediction/test_astrologer_prompt_builder.py` passes with injected labels. |
| AC4 payload keys stable | PASS | Unit projection tests and V4 `--long` integration tests pass. |
| AC5 reintroduction guard | PASS | `app/tests/unit/test_astrology_localization_guardrails.py` passes. |
| AC6 after audit residual proof | PASS | `prediction-i18n-after.md` contains `Known residual in-domain work: none`. |

## Validation audit

| Command | Result |
|---|---|
| `ruff format .` from `backend/` after venv activation | PASS |
| `ruff check .` from `backend/` after venv activation | PASS |
| `pytest -q app/tests/unit/test_astrology_localization_guardrails.py tests/unit/prediction/test_astrologer_prompt_builder.py app/tests/unit/test_public_projection.py tests/unit/prediction/test_public_astro_daily_events.py tests/unit/prediction/test_public_astro_foundation.py tests/unit/prediction/test_public_time_window.py app/tests/unit/prediction/test_public_projection_evidence.py` | PASS, 46 tests |
| `pytest --long -q tests/integration/test_v4_scenarios.py tests/integration/test_v4_migration.py` | PASS, 6 tests |
| AST scan for `.assemble(...)` calls without `astro_labels` under `app/` and `tests/` | PASS, zero missing injections |
| Forbidden symbol scans for `PLANET_NAMES_FR`, `SIGN_NAMES_FR`, `SIGN_LABELS_FR`, `PLANET_CODE_LABELS`, `ASPECT_LABELS`, `HOUSE_SIGNIFICATIONS`, `EFFECT_LABELS`, and removed helper names under `app/domain/prediction` | PASS, zero hits |
| Service/resolver import boundary scan under `app/domain/prediction` | PASS, zero hits |
| `python -c "from app.main import app; print(app.title)"` | PASS, `horoscope-backend` |
| `git diff --check` | PASS |

## DRY / No Legacy audit

- No forbidden FR mapping symbol remains in `backend/app/domain/prediction`.
- No `app.services` import was introduced inside `domain/prediction`.
- Test fake labels are centralized in one helper rather than copied across unit
  and integration tests.
- `_ASPECT_TONES` remains classified as non DB-backed metadata and is guarded
  against unclassified aspect mapping growth.

## Residual risks

- Full backend `pytest -q` was not run; the targeted story suite and the V4
  integration lane covering the signature regression both passed.

## Verdict

CLEAN
