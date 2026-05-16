# Validation Plan

## Environment Assumptions

- PowerShell on Windows.
- Python commands run only after `.\.venv\Scripts\Activate.ps1`.
- Backend working directory for Python checks: `backend/`.

## Commands

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend/` | yes | formatting succeeds |
| Lint | `ruff check .` | `backend/` | yes | no lint errors |
| Resolver regression | `pytest -q app/tests/unit/test_astrology_translation_resolver.py` | `backend/` | yes | all tests pass |
| Prompt labels | `pytest -q tests/unit/prediction/test_astrologer_prompt_builder.py` | `backend/` | yes | all tests pass |
| Projection payloads | `pytest -q app/tests/unit/test_public_projection.py tests/unit/prediction/test_public_astro_daily_events.py tests/unit/prediction/test_public_astro_foundation.py` | `backend/` | yes | all tests pass |
| Guardrail | `pytest -q app/tests/unit/test_astrology_localization_guardrails.py` | `backend/` | yes | all tests pass |
| Forbidden mappings scan 1 | `rg -n "PLANET_NAMES_FR\|SIGN_NAMES_FR\|SIGN_LABELS_FR\|PLANET_CODE_LABELS" app/domain/prediction -g "*.py"` | `backend/` | yes | zero active hits |
| Forbidden mappings scan 2 | `rg -n "ASPECT_LABELS\|HOUSE_SIGNIFICATIONS\|EFFECT_LABELS" app/domain/prediction -g "*.py"` | `backend/` | yes | zero active hits |
| Forbidden helpers scan | `rg -n "get_planet_name_fr\|get_sign_name_fr\|get_aspect_label\|get_effect_label" app/domain/prediction -g "*.py"` | `backend/` | yes | zero active hits |
| Boundary scan | `rg -n "AstrologyTranslationResolver\|astrology_translation_resolver\|LanguageModel\|from app\.services" app/domain/prediction -g "*.py"` | `backend/` | yes | zero active hits |
| Residual proof | `rg -n "Known residual in-domain work: none" ../_condamad/stories/CS-179-fermer-i18n-prediction-astrologique/prediction-i18n-after.md` | `backend/` | yes | marker found |

## Diff Review

- `git diff --stat`
- `git diff --check`
- `git status --short`
