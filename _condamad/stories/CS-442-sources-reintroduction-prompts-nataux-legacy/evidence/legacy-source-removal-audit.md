# Legacy Source Removal Audit

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `admin_prompts.py` `natal_long_free` derivation | admin runtime derivation | delete | admin resolved catalog detail | assembly template key | removed | admin tests PASS; after scan no admin hit | low |
| `PROMPT_RUNTIME_DATA["natal_interpretation"]` | runtime prompt catalogue | delete | gateway fallback/schema resolution | `theme_natal.*` generation contracts and `theme_astral_prompt_v1` | removed | orchestration tests PASS | medium |
| `CANONICAL_USE_CASE_CONTRACTS["natal_interpretation"]` | canonical registry | delete | assembly/schema resolution | `theme_natal.reading.*.v1` contracts | removed | old assembly raises `GatewayConfigError` in tests | medium |
| `seed_66_20_taxonomy` `natal_interpretation` target | bootstrap taxonomy | delete | local auto-heal | modern natal thematic targets and theme astral seed | removed | orchestration and architecture tests PASS | medium |
| `backend/app/ops/llm/bootstrap/seed_29_prompts.py` | bootstrap prompt seed | delete | local startup auto-heal | `seed_theme_astral_prompt_contract` and theme natal contracts | file deleted | seed absence guards PASS | low |
| `backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py` | bootstrap prompt seed | delete | local startup auto-heal | theme natal contracts | file deleted | seed absence guards PASS | low |
| `backend/scripts/seed_natal_short.py` | executable script | delete | manual legacy reseed | none; key is removed | file deleted | architecture guard PASS | low |
| `backend/scripts/seed_28_4.py` | executable script | delete | old schema/use-case seed | canonical bootstrap contracts | file deleted | architecture guard PASS | low |
| `backend/scripts/seed_29_prompts.py` | executable wrapper | delete | old manual seed | none | file deleted | architecture guard PASS | low |
| `backend/scripts/seed_30_2_astroresponse_v2.py` | executable script | delete | old schema mutation | none | file deleted | architecture guard PASS | low |
| `backend/scripts/seed_30_3_gpt5_prompts.py` | executable script | delete | old prompt mutation | none | file deleted | architecture guard PASS | low |
| `backend/scripts/seed_30_8_v3_prompts.py` | executable wrapper | delete | old manual seed | none | file deleted | architecture guard PASS | low |
| `backend/scripts/update_all_prompts_59_5.py` | executable prompt mutation | delete | old prompt update | modern prompt contracts | file deleted | architecture guard PASS | low |
| `backend/scripts/seed_66_20_convergence.py` old natal rows | executable convergence seed | update | local tests and manual convergence | modern non-legacy targets only | old rows removed | scans and tests PASS | low |
| `backend/scripts/seed_66_15_assembly_convergence.py` old natal rows | executable convergence seed | update | local tests and manual convergence | modern non-legacy targets only | old rows removed | scans and tests PASS | low |
