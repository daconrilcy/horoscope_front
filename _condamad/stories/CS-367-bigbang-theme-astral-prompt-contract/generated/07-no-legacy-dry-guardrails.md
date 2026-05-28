# No Legacy / DRY Guardrails

## Applied

- No compatibility wrapper, alias, shim, or fallback path was added.
- `theme_astral` now fails explicitly when the canonical `theme_astral_llm_input_v1` provider payload is absent.
- `chart_json`, `natal_data`, and `llm_astrology_input_v1` are not accepted as substitute prompt-visible carriers for `theme_astral`.
- `theme_astral_prompt_v1` is the single prompt contract id for the theme astral provider skeleton.
- `ThemeAstralProviderPayloadBuilder` remains the single provider payload builder owner.
- Example JSON files use one stable skeleton across profiles.

## Residual Legacy Classification

- `llm_astrology_input_v1`, `chart_json`, `natal_data`, and old natal prompt constants remain in natal, admin sample, historical docs, tests, or non-theme-astral scopes.
- No residual occurrence is classified as an active `theme_astral` provider input after this story.

## Guard Evidence

- `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py`
- `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`
- `evidence/legacy-scan-after.txt`
