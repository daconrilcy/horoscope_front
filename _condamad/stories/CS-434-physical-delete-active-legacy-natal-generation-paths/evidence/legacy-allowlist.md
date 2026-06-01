# Legacy Allowlist CS-434

| symbol | file | reason | allowed_context | non_generative_proof | owner |
|---|---|---|---|---|---|
| `natal_interpretation_short` | `backend/app/services/llm_generation/natal/interpretation_service.py` | Lecture historique free-short et normalisation readonly des lignes persistees. | historical-readonly | Public routers ne callent plus `interpret`/`interpret_chart`; `AIEngineAdapter` rejette la cle; tests architecture PASS. | backend-llm |
| `natal_long_free` | `backend/app/services/llm_generation/natal/interpretation_service.py` | Detection readonly de lignes historiques marquees anciennement free. | historical-readonly | Retire du catalog/runtime; adapter rejette la cle; `llm_orchestration` PASS. | backend-llm |
| `natal_interpretation_short`, `natal_long_free` | `backend/tests/**` | Assertions anti-retour, fixtures historiques ou tests readonly. | test-guard | Tests nominaux convertis dans `test_context_quality.py`, `test_resolved_execution_plan.py`, `test_runtime_convergence.py`, `test_ai_engine_adapter.py`. | backend-tests |
| `natal_interpretation_short` | `backend/app/ops/llm/bootstrap/seed_30_2_astroresponse_v2.py`, `backend/scripts/**` | Scripts historiques non appeles par startup auto-heal. | bootstrap-classified | `main.py` ne teste plus active short; `seed_29_prompts.py` et `seed_66_20_taxonomy.py` ne reseedent plus les chemins publics supprimes. | backend-ops |
| `natal_interpretation` | `backend/app/domain/llm/prompting/catalog.py`, `backend/app/ops/llm/bootstrap/seed_29_prompts.py` | Premium/admin historique encore non public. | admin-only-non-public | Public routers ne callent plus le service legacy; adapter interdit `plan=basic`; route product-action Basic couverte par tests. | backend-llm |
| `basic_natal_prompt_payload` | `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` | Payload contractuel moderne du prompt theme astral Basic. | documentation | Retire de `NatalExecutionInput`, `adapter.py` et branche gateway legacy; tests theme astral existants conservent le builder moderne. | backend-theme-natal |

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/app/services/llm_generation/natal/interpretation_service.py` | `natal_interpretation_short`, `natal_long_free` | Compatibilite readonly des donnees historiques. | permanent tant que les lignes historiques existent. |
| `backend/tests/**` | cles supprimees | Gardes anti-retour et fixtures historiques. | permanent comme preuve de non-regression. |
| `backend/app/ops/llm/bootstrap/seed_30_2_astroresponse_v2.py`, `backend/scripts/**` | cles legacy | Scripts historiques hors auto-heal courant. | a supprimer dans une story cleanup scripts dediee. |
