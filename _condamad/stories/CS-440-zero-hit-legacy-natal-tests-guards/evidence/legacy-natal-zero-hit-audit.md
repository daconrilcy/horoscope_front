# Audit CS-440 legacy natal zero-hit

<!-- Commentaire global: cet audit classe les derniers hits legacy natal et fixe la preuve de non-retour CS-440. -->

## Statut

- Classification: `ready-to-review`
- Invariant durable: `RG-174`
- Surface runtime publique generatrice: zero hit non autorise.
- Residus autorises: readonly historique, admin-only, garde de rejet, tests d'extinction, preuves `_condamad`.

## Classification

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `natal_interpretation_short` | symbol | guard-or-readonly | adapter reject guard, readonly historical rows, extinction tests | `theme_natal` public contract | keep classified only | `test_legacy_natal_runtime_hits_are_explicitly_authorized`; `test_public_runtime_contract_excludes_deleted_natal_generator_keys` | Old short prompt returns if guard list is bypassed |
| `natal_long_free` | symbol | guard-or-readonly | adapter reject guard, readonly historical rows, admin-only metadata, extinction tests | `theme_natal` public contract | keep classified only | `test_legacy_natal_runtime_hits_are_explicitly_authorized`; `test_natal_adapter_does_not_forward_legacy_prompt_carriers` | Old free prompt returns if adapter reject guard is removed |
| `natal_interpretation` Basic or Free | symbol | historical-readonly | readonly historical rows and gone-route tests | product action contract | no public generator | `test_old_public_route_is_removed_or_gone`; OpenAPI excludes old fields | Old complete prompt path returns |
| `use_case_level` public contract | field | public-extinction/admin-only-internal | payload rejection tests, DOM denylist, internal LLM QA | product action `action` | reject public contract | `test_new_route_rejects_legacy_generation_fields`; `natalPublicDomGuard.test.tsx`; architecture guard | Old public contract returns |
| `forceRefresh` | field | extinction-test-only | payload rejection tests and DOM denylist | product action `action` | reject | `test_new_route_rejects_legacy_generation_fields`; zero unauthorized runtime hit guard | Refresh command returns |
| `shouldRefreshShortAfterBasicUpgrade` | field | extinction-test-only | DOM denylist | `theme_natal` product action | reject | `natalPublicDomGuard.test.tsx`; zero unauthorized runtime hit guard | Frontend short refresh path returns |
| `variant_code` command use | field | canonical-active outside command construction | entitlement, prediction/daily, astrology calculation, historical data | product action `action` | keep non-command uses | `test_runtime_route_and_openapi_expose_product_action_contract`; `test_new_route_rejects_legacy_generation_fields` | Command selection drifts |
| `basic_natal_prompt_payload` | symbol | canonical-active | modern `theme_astral` payload owner | theme astral payload builder | keep | `test_theme_astral_prompt_contract_guard.py`; CS-437 non-goal | None |
| old positive fixture consumer | fixture | replaced-by-extinction | named anti-return tests | extinction guard | replace-consumer | `test_old_public_route_is_removed_or_gone`; `test_theme_natal_contract_is_only_public_generation_path` | Nominal fixture remains |
| unresolved external old consumer | symbol | none-detected | none | product action contract | no user decision required | bounded scans and structured OpenAPI/routes checks | None recorded |

## Autorisations runtime explicites

| Path | Tokens | Classification | Reason |
|---|---|---|---|
| `backend/app/api/v1/routers/public/natal_interpretation.py` | `natal_interpretation_short` | readonly historical projection | readonly historical projection |
| `backend/app/api/v1/routers/internal/llm/qa.py` | `use_case_level` | admin-only internal QA | admin-only internal QA |
| `backend/app/domain/llm/runtime/adapter.py` | `natal_interpretation_short`, `natal_long_free` | deleted-key rejection guard | deleted-key rejection guard |
| `backend/app/services/api_contracts/internal/llm/qa.py` | `use_case_level` | admin-only internal QA | admin-only internal QA |
| `backend/app/services/llm_generation/admin_prompts.py` | `natal_long_free` | admin-only prompt metadata | admin-only prompt metadata |
| `backend/app/services/llm_generation/natal/interpretation_service.py` | `natal_interpretation_short`, `natal_long_free` | historical persisted-row read compatibility | historical persisted-row read compatibility |

## Commandes de preuve

- `python -B -m pytest -q tests/architecture/test_legacy_natal_generation_inventory_guard.py tests/architecture/test_llm_legacy_extinction.py tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_llm_legacy_extinction.py --tb=short`
- `python -B -m pytest -q tests/integration/test_theme_natal_public_api_product_actions.py tests/integration/test_theme_natal_public_reads.py --tb=short`
- `pnpm --dir frontend test -- natalChartApi.test.tsx natalPublicDomGuard.test.tsx natalInterpretation.test.tsx NatalChartPage.test.tsx`
- `rg -n "natal_interpretation_short|natal_long_free|shouldRefreshShortAfterBasicUpgrade|forceRefresh" backend/app frontend/src backend/tests frontend/src/tests`
- `rg -n "use_case_level" backend/app/services/api_contracts/public backend/app/api/v1/routers/public frontend/src/api/natal-chart frontend/src/features/natal-chart frontend/src/pages/NatalChartPage.tsx`
