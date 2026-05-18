# Target Files - CS-186

## Must Read

- `backend/tests/factories/astrology_runtime_reference_factory.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `_condamad/stories/CS-185-brancher-profils-signes-runtime-natal/generated/11-code-review.md`
- `_condamad/stories/regression-guardrails.md`

## Likely Modified

- `backend/tests/factories/astrology_runtime_reference_factory.py`
- `backend/app/tests/unit/test_aspect_orb_overrides.py`
- `backend/app/tests/unit/test_aspect_ruleset_schema.py`
- `backend/app/tests/unit/test_golden_zodiac_sidereal_ayanamsa.py`
- `backend/app/tests/unit/test_natal_metadata.py`
- `backend/app/tests/unit/test_natal_pipeline_swisseph.py`
- `backend/app/tests/unit/test_natal_tt.py`

## Forbidden Unless Directly Justified

- `backend/app/**`
- `backend/migrations/**`
- `docs/db_seeder/**`
- Existing user-modified DB model and seed files.

## Required Searches

- `rg -n "runtime_reference_from_mapping|_complete_sign_payload|SIGN_PROFILE_DATA" backend tests _condamad -g "*.py" -g "*.md"`
- `rg -n "ELEMENT_BY_SIGN|MODALITY_BY_SIGN|POLARITY_BY_SIGN|SIGN_PROFILE_DATA" app/domain/astrology app/services/natal -g "*.py"`
