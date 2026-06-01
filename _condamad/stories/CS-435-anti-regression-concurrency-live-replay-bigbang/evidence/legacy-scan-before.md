# Legacy scan before
Command: rg -n "natal_interpretation_short|natal_long_free|basic_natal_prompt_payload.*natal_interpretation" backend/app frontend/src
backend/app\tests\unit\test_ai_engine_adapter.py:181:                use_case_key="natal_long_free",
frontend/src\features\natal-chart\NatalInterpretation.tsx:57:  return item.use_case === "natal_long_free"
frontend/src\features\natal-chart\NatalInterpretation.tsx:79:  return items.find((item) => item.use_case === "natal_long_free") ?? null
frontend/src\components\natal-interpretation\NatalInterpretationContent.tsx:296:  const isFreeLongInterpretation = useCase === "natal_long_free"
frontend/src\tests\AdminPromptsCatalogFlow.test.tsx:54:    use_case_key: "natal_long_free",
frontend/src\tests\AdminPromptsCatalogFlow.test.tsx:55:    runtime_use_case_key: "natal_long_free",
frontend/src\tests\AdminPromptsCatalogFlow.test.tsx:99:        source_label: "natal_long_free",
frontend/src\tests\AdminPromptsCatalogFlow.test.tsx:103:        editable_use_case_key: "natal_long_free",
frontend/src\tests\AdminPromptsCatalogFlow.test.tsx:104:        meta: { use_case_key: "natal_long_free" },
frontend/src\tests\AdminPromptsCatalogFlow.test.tsx:279:            key: "natal_long_free",
frontend/src\tests\AdminPromptsCatalogFlow.test.tsx:299:    if (url.endsWith("/v1/admin/llm/use-cases/natal_long_free/prompts") && !init?.method) {
frontend/src\tests\AdminPromptsCatalogFlow.test.tsx:304:            use_case_key: "natal_long_free",
frontend/src\tests\natalPublicDomGuard.test.tsx:92:      use_case: "natal_long_free",
frontend/src\tests\natalPublicDomGuard.test.tsx:94:      meta: { level: "complete", use_case: "natal_long_free", persona_name: null },
frontend/src\tests\natalPublicDomGuard.test.tsx:123:      use_case: "natal_long_free",
frontend/src\tests\natalPublicDomGuard.test.tsx:125:      meta: { level: "complete", use_case: "natal_long_free", persona_name: null },
frontend/src\tests\natalInterpretation.test.tsx:65:  use_case: "natal_interpretation_short",
frontend/src\tests\natalInterpretation.test.tsx:80:    use_case: "natal_interpretation_short",
frontend/src\tests\natalInterpretation.test.tsx:104:      use_case: "natal_interpretation_short"
frontend/src\tests\natalInterpretation.test.tsx:185:      use_case: "natal_interpretation_short",
frontend/src\tests\natalInterpretation.test.tsx:188:      meta: { level: "short", use_case: "natal_interpretation_short", persona_name: null },
frontend/src\tests\natalInterpretation.test.tsx:519:            use_case: "natal_long_free",
frontend/src\tests\natalInterpretation.test.tsx:775:            use_case: "natal_interpretation_short",
frontend/src\tests\natalInterpretation.test.tsx:784:            use_case: "natal_long_free",
frontend/src\tests\natalInterpretation.test.tsx:877:            use_case: "natal_long_free",
frontend/src\tests\NatalChartPage.test.tsx:1828:              use_case: "natal_interpretation_short",
frontend/src\tests\NatalChartPage.test.tsx:1912:              use_case: "natal_long_free",
backend/app\api\v1\routers\public\natal_interpretation.py:189:                        not in {"natal_interpretation", "natal_interpretation_short"}
backend/app\domain\llm\runtime\adapter.py:37:    {"natal_interpretation_short", "natal_long_free", "natal-long-free"}
backend/app\tests\unit\test_seed_29_prompt_contract.py:12:    config = next(c for c in PROMPTS_TO_SEED if c["use_case_key"] == "natal_interpretation_short")
backend/app\tests\unit\test_natal_interpretation_service_v2.py:137:        use_case="natal_long_free",
backend/app\tests\unit\test_natal_interpretation_service_v2.py:324:        """La variante free_short complete ne peut plus reconstruire natal_long_free."""
backend/app\tests\integration\test_natal_interpretations_history.py:61:            use_case="natal_interpretation_short",
backend/app\tests\integration\test_natal_interpretations_history.py:108:            use_case="natal_interpretation_short",
backend/app\tests\integration\test_natal_interpretations_history.py:144:            use_case="natal_interpretation_short",
backend/app\tests\integration\test_admin_actions_api.py:228:                    use_case="natal_interpretation_short",
backend/app\tests\integration\test_admin_llm_natal_prompts.py:111:        key = "natal_interpretation_short"
backend/app\tests\integration\test_admin_llm_natal_prompts.py:152:        key = "natal_interpretation_short"
backend/app\services\llm_generation\admin_prompts.py:301:        return "natal_long_free"
backend/app\services\llm_generation\natal\interpretation_service.py:488:PUBLIC_FREE_SHORT_USE_CASE = "natal_interpretation_short"
backend/app\services\llm_generation\natal\interpretation_service.py:497:        or model.use_case == "natal_long_free"
backend/app\services\llm_generation\natal\interpretation_service.py:954:        if model.variant_code == "free_short" or model.use_case == "natal_long_free":
backend/app\tests\integration\test_contract_api.py:47:        "/v1/admin/llm/use-cases/natal_interpretation_short/contract",
backend/app\tests\integration\test_contract_api.py:52:    assert data["key"] == "natal_interpretation_short"
backend/app\tests\integration\test_migration_20260422_0073_cleanup_llm_legacy.py:107:                "fallback_use_case_key": "natal_interpretation_short",
backend/app\tests\integration\test_migration_20260422_0073_cleanup_llm_legacy.py:201:    assert archive_row["fallback_use_case_key"] == "natal_interpretation_short"
backend/app\tests\integration\test_migration_20260422_0073_cleanup_llm_legacy.py:227:    assert restored_value == "natal_interpretation_short"
backend/app\tests\integration\test_gateway_gpt5_params.py:137:    use_case = "natal_interpretation_short"
backend/app\tests\integration\test_gateway_gpt5_params.py:181:    use_case = "natal_interpretation_short"
backend/app\tests\unit\test_gateway_modes.py:385:    """Reutilise le schema catalogue pour `natal_long_free` hors chemin assembly."""
backend/app\tests\unit\test_gateway_modes.py:386:    use_case = "natal_long_free"
backend/app\tests\unit\test_gateway_input_validation_payload.py:22:        {"use_case": "natal_interpretation_short", "locale": "fr-FR"},
backend/app\tests\unit\test_gateway_input_validation_payload.py:46:        {"use_case": "natal_interpretation_short"},
backend/app\tests\unit\test_eval_harness_natal.py:20:    return "app/tests/eval_fixtures/natal_interpretation_short"
backend/app\tests\unit\test_eval_harness_natal.py:28:        use_case="natal_interpretation_short",
backend/app\tests\unit\test_eval_harness_natal.py:57:    report = await run_eval("natal_interpretation_short", "v1", fixtures_path, db)
backend/app\tests\unit\test_eval_harness_natal.py:70:        use_case="natal_interpretation_short",
backend/app\tests\unit\test_eval_harness_natal.py:99:        use_case="natal_interpretation_short",
backend/app\tests\unit\test_eval_harness_natal.py:127:    report = await run_eval("natal_interpretation_short", "v1", fixtures_path, db)
rg exit code: 0
