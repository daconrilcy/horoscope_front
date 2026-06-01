# Legacy scan results

Status: PASS_WITH_CLASSIFIED_HITS

VS1:

- Command: `rg -n "natal_interpretation_short|natal_long_free|basic_natal_prompt_payload.*natal_interpretation" backend/app backend/tests frontend/src`
- Result: classified hits.
- Runtime public generator owners are protected by `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`.
- Classified app hits:
  - `backend/app/api/v1/routers/public/natal_interpretation.py`: readonly list projection compatibility, not a generator.
  - `backend/app/services/llm_generation/natal/interpretation_service.py`: legacy read/filter service still required for historical reads, guarded by rejected/public-boundary tests.
  - `frontend/src/features/natal-chart/NatalInterpretation.tsx` and `NatalInterpretationContent.tsx`: `natal_long_free` readonly/free display classification, not a generation trigger.
  - `backend/app/domain/llm/runtime/adapter.py` and admin prompt surfaces: admin/config/eval compatibility, outside public theme-natal product-action runtime.
- Classified test hits: fixtures and denylist guard strings.

VS2:

- Command: `rg -n "shouldRefreshShortAfterBasicUpgrade|use_case_level|variant_code|forceRefresh" frontend/src backend/app`
- Result: classified hits.
- `shouldRefreshShortAfterBasicUpgrade` and `forceRefresh`: no active app hit.
- `use_case_level`: internal LLM QA/admin or gone-endpoint tests only; public product-action OpenAPI rejects it.
- `variant_code`: canonical entitlement/astrology field in many non-theme-natal-public owners. Product-action request schema rejects it, covered by `test_runtime_route_and_openapi_expose_product_action_contract`.

VS3:

- Command: `rg -n "PROMPT_FALLBACK_CONFIGS|fallback_default|EXIGENCE PREMIUM|AstroResponse_v3" backend/app backend/tests`
- Result: classified hits.
- Runtime public theme-natal product-action owners do not import fallback catalog or legacy interpretation service.
- Remaining hits are prompt governance tests, historical bootstrap seeds, canonical prompt configuration, or denylist tests.

VS4:

- Command: `rg -n "ThemeNatalReadingProductContract|LLMGenerationContract|basic_full_reading|generation_contract_hash" backend/app backend/tests frontend/src _condamad/stories/regression-guardrails.md`
- Result: PASS, required contract markers present in runtime, tests, and `RG-173`.

AC couverts: AC7, AC8, AC12, AC15.
