# Target Files

## Must inspect before implementation

- `C:\dev\horoscope_front` repository instructions supplied by the user.
- `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/00-story.md`
- `_story_briefs/cs-435-anti-regression-concurrency-live-replay-bigbang.md`
- `_condamad/stories/regression-guardrails.md` scoped to `RG-173` and cited IDs.
- Targeted backend runtime/tests around theme natal product actions, slots, runtime, entitlement and quota.
- Targeted frontend tests for natal interpretation and public DOM guards.

## Searches used before editing

```powershell
rg -n "product_action|generate_full|accepted|rejected|output_variant|generation_contract_hash|generation_contract_key|quota|plan=free|public" backend\app\api\v1\routers\public\natal_interpretation.py backend\app\services\llm_generation\natal\interpretation_service.py backend\app\services\entitlement\effective_entitlement_resolver_service.py backend\app\services\quota\usage_service.py
rg -n "product_action|generate_full|accepted|rejected|output_variant|generation_contract_hash|generation_contract_key|quota|plan=free|public" backend\tests\integration\test_theme_natal_public_api_product_actions.py backend\tests\integration\test_theme_natal_basic_full_reading_runtime.py backend\tests\integration\test_theme_natal_reading_slots.py backend\tests\integration\test_natal_interpretation_rejected_public_boundary.py backend\tests\unit\test_natal_chart_long_quota_on_acceptance.py backend\tests\llm_orchestration\test_theme_natal_generation_contracts.py
rg -n "shouldRefreshShortAfterBasicUpgrade|forceRefresh|generate_full|productAction|product_action|natal_interpretation_short|use_case_level|variant_code|technical|fallback|DOM" frontend\src\features\natal-chart frontend\src\api\natal-chart frontend\src\tests
```

## Modified files

- `backend/tests/integration/test_theme_natal_bigbang_replay.py`
- `backend/tests/integration/test_theme_natal_concurrency.py`
- `backend/tests/integration/test_theme_natal_entitlement_freshness.py`
- `backend/tests/integration/test_theme_natal_public_reads.py`
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`
- `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/**`
- `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/generated/**`
- `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/00-story.md`
- `_condamad/stories/story-status.md`

## Forbidden or high-risk files

- `_condamad/run-state.json`: pre-existing dirty file, explicitly out of scope and left untouched.
- `_story_briefs/cs-435-anti-regression-concurrency-live-replay-bigbang.md`: source brief left unchanged.
- Provider clients under `backend/app/infra/providers/llm/**`: no provider optimization in scope.
- Frontend CSS files: no visual redesign in scope.
- Payment provider internals: checkout simulated deterministically through existing entitlement gate.
