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

## Autorisations de tests exactes

Les fichiers suivants sont les seuls tests autorises a conserver un ancien symbole natal.
Le guard `test_legacy_natal_test_hits_are_explicitly_authorized` echoue pour tout nouveau fichier non classe.

- `backend/app/tests/integration/test_admin_actions_api.py` - historique admin/user detail.
- `backend/app/tests/integration/test_admin_llm_natal_prompts.py` - metadata admin-only.
- `backend/app/tests/integration/test_contract_api.py` - contrat admin legacy lu sans chemin public.
- `backend/app/tests/integration/test_gateway_gpt5_params.py` - profil execution historique.
- `backend/app/tests/integration/test_llm_qa_router.py` - QA interne admin-only.
- `backend/app/tests/integration/test_migration_20260422_0073_cleanup_llm_legacy.py` - migration historique.
- `backend/app/tests/integration/test_natal_chart_long_entitlement.py` - ancien endpoint gone/rejet.
- `backend/app/tests/integration/test_natal_free_short_variant.py` - ancien endpoint gone/rejet.
- `backend/app/tests/integration/test_natal_interpretation_endpoint.py` - ancien endpoint gone/rejet.
- `backend/app/tests/integration/test_natal_interpretations_history.py` - readonly historique.
- `backend/app/tests/unit/test_ai_engine_adapter.py` - garde deleted-key.
- `backend/app/tests/unit/test_gateway_input_validation_payload.py` - rejet des carriers legacy.
- `backend/app/tests/unit/test_gateway_modes.py` - schema catalogue hors generation publique.
- `backend/app/tests/unit/test_natal_interpretation_service_v2.py` - garde de rejet free short.
- `backend/app/tests/unit/test_seed_29_prompt_contract.py` - contrat seed historique.
- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` - guard CS-440.
- `backend/tests/architecture/test_llm_legacy_extinction.py` - extinction LLM.
- `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py` - anti-retour theme astral.
- `backend/tests/evaluation/__init__.py` - evaluation legacy classee.
- `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py` - anti-retour theme astral.
- `backend/tests/integration/test_admin_llm_catalog.py` - metadata admin-only.
- `backend/tests/integration/test_llm_release.py` - release LLM historique.
- `backend/tests/integration/test_natal_basic_complete_v3_runtime.py` - anti-retour modern basic runtime.
- `backend/tests/integration/test_natal_interpretation_public_free_basic_contract.py` - readonly historique.
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` - rejected/audit-only.
- `backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py` - anti-retour theme natal.
- `backend/tests/integration/test_theme_natal_public_api_product_actions.py` - rejet/gone public.
- `backend/tests/integration/test_theme_natal_public_reads.py` - readonly accepted-only.
- `backend/tests/llm_orchestration/test_assembly_resolution.py` - resolution historique classee.
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py` - extinction orchestration.
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py` - gouvernance prompts.
- `backend/tests/llm_orchestration/test_runtime_convergence.py` - rejet de fallback supprime.
- `backend/tests/unit/test_natal_interpretation_stored_payload.py` - payload persiste historique.
- `frontend/src/tests/natalPublicDomGuard.test.tsx` - denylist DOM publique.

## Fixtures renommees

- `backend/app/tests/eval_fixtures/natal_interpretation_short` -> `backend/app/tests/eval_fixtures/generic_structured_short`.
- `backend/app/tests/eval_fixtures/natal_interpretation` -> `backend/app/tests/eval_fixtures/generic_structured_complete`.

## Commandes de preuve

- `python -B -m pytest -q tests/architecture/test_legacy_natal_generation_inventory_guard.py tests/architecture/test_llm_legacy_extinction.py tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_llm_legacy_extinction.py --tb=short`
- `python -B -m pytest -q tests/integration/test_theme_natal_public_api_product_actions.py tests/integration/test_theme_natal_public_reads.py --tb=short`
- `pnpm --dir frontend test -- natalChartApi.test.tsx natalPublicDomGuard.test.tsx natalInterpretation.test.tsx NatalChartPage.test.tsx`
- `rg -n "natal_interpretation_short|natal_long_free|shouldRefreshShortAfterBasicUpgrade|forceRefresh" backend/app frontend/src backend/tests frontend/src/tests`
- `rg -n "use_case_level" backend/app/services/api_contracts/public backend/app/api/v1/routers/public frontend/src/api/natal-chart frontend/src/features/natal-chart frontend/src/pages/NatalChartPage.tsx`
