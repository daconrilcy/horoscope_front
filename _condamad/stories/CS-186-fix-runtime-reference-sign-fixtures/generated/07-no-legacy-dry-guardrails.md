# No Legacy / DRY Guardrails - CS-186

## Canonical Stance

- `runtime_reference_from_mapping()` must stay strict for incomplete sign profiles.
- Tests that need runtime references must pass complete sign payloads explicitly.
- A shared test helper may build explicit fixture payloads; it must not import seed mappings or hide partial inputs inside `runtime_reference_from_mapping()`.

## Forbidden Patterns

- Importing or referencing `SIGN_PROFILE_DATA` from seed code.
- Adding fallback completion to `_complete_sign_payload()`.
- Adding production constants such as `ELEMENT_BY_SIGN`, `MODALITY_BY_SIGN`, or `POLARITY_BY_SIGN`.
- Editing runtime production code to accept incomplete signs.

## Required Evidence

- `pytest -q app/tests/unit/test_astrology_runtime_reference_guard.py`
- `rg -n "SIGN_PROFILE_DATA" tests/factories app/tests -g "*.py"`
- `rg -n "ELEMENT_BY_SIGN|MODALITY_BY_SIGN|POLARITY_BY_SIGN|SIGN_PROFILE_DATA" app/domain/astrology app/services/natal -g "*.py"`

## Review Checklist

- The helper name and call sites make profile completion explicit.
- No affected test still passes partial signs to `runtime_reference_from_mapping()`.
- No production runtime or DB code changed.
