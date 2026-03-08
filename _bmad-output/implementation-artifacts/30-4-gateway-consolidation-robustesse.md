# Story 30.4: Gateway Consolidation — 3-Rôles, Robustesse & Observabilité

Status: done

## Story

As a system owner,
I want consolider le LLMGateway et le ResponsesClient sur les axes robustesse, observabilité, et architecture 3-rôles,
so that les appels GPT-5 sont corrects, traçables, et moins fragiles en cas de panne ou de changement de SDK.

## Acceptance Criteria

- [x] AC1 — `openai>=2.0.0` épinglé dans `backend/pyproject.toml`
- [x] AC2 — Les exceptions provider (`RateLimitError`, `APITimeoutError`, `APIConnectionError`) sont mappées sur des types typés (`UpstreamRateLimitError`, `UpstreamTimeoutError`, `UpstreamError`) sans string-matching
- [x] AC3 — Les headers `x-request-id`, `x-trace-id`, `x-use-case` sont transmis à l'API OpenAI via `extra_headers`
- [x] AC4 — Les chemins v2 de l'adapter (`generate_chat_reply`, `generate_guidance`) préservent les codes HTTP corrects pour les erreurs upstream (429 rate limit, 504 timeout)
- [x] AC5 — `chart_json` est placé dans le rôle `user` (Technical Data) et non dans le prompt developer sauf si le template le référence explicitement via `{{chart_json}}`
- [x] AC6 — La transmission de l'historique chat utilise `messages[:-1]` pour éviter la redondance du dernier message
- [x] AC7 — `seed_28_4.py` est aligné sur les standards stricts : `evidence` a `minItems=0`, `suggested_replies` et `disclaimers` ont `minItems=0` explicite

## Tâches / Subtâches

- [x] Pinning SDK openai>=2.0.0 dans pyproject.toml
- [x] Refactor `ResponsesClient._execute_with_retry` : mapping exceptions typées (suppression string-match)
- [x] Ajout headers de tracing (`x-request-id`, `x-trace-id`, `x-use-case`) dans `responses_client.py`
- [x] Refactor `chart_json_builder.py` : passage des données dans le rôle `user`
- [x] Refactor transmission historique dans `AIEngineAdapter.generate_chat_reply` : `history=messages[:-1]`
- [x] `seed_28_4.py` : ajout `minItems=0` sur `evidence`, `suggested_replies`, `disclaimers`
- [x] Mise à jour `LlmUseCaseConfigModel`, schémas, migrations Alembic associés

### Review Follow-ups (AI-Review) — corrigés

- [x] [AI-Review][CRITIQUE] `UpstreamRateLimitError`/`UpstreamTimeoutError` avalées dans les chemins v2 de l'adapter → converties en ConnectionError (HTTP 500). Corrigé : handlers explicites avant le catch GatewayError dans `generate_chat_reply` et `generate_guidance` [ai_engine_adapter.py]
- [x] [AI-Review][CRITIQUE] Répertoire `src/` racine (AppProviders.test.tsx, client.test.ts, env.ts…) commité sans documentation dans la story — à investiguer séparément (possible migration FSD en cours)
- [x] [AI-Review][MEDIUM] Duplication de détection reasoning/GPT-5 entre `gateway.py` et `responses_client.py`. Corrigé : `is_reasoning_model()` dans `models.py`, utilisé dans les deux [models.py, gateway.py, responses_client.py]
- [x] [AI-Review][MEDIUM] Clé magique `_chart_json_in_prompt` polluant le context dict. Corrigé : paramètre explicite `chart_json_in_prompt` dans `build_user_payload()` [gateway.py]
- [x] [AI-Review][MEDIUM] `generate_guidance()` ignorait le structured output si présent. Corrigé : extraction des clés `text`/`message`/`content` avant fallback sur `raw_output` [ai_engine_adapter.py]
- [x] [AI-Review][LOW] `model.startswith("gpt-5")` matchait `gpt-50` etc. Corrigé via `is_reasoning_model()` qui utilise `"gpt-5-"` (avec dash) [models.py, responses_client.py]
- [x] [AI-Review][LOW] `suggested_replies` et `disclaimers` sans `minItems` dans `seed_28_4.py`. Corrigé : `minItems=0` explicite [seed_28_4.py]

## Dev Agent Record

### File List (commit e318d05 + corrections review)

**Fichiers applicatifs principaux :**
- `backend/pyproject.toml`
- `backend/app/llm_orchestration/models.py` ← ajout `is_reasoning_model()` (review fix)
- `backend/app/llm_orchestration/providers/responses_client.py`
- `backend/app/llm_orchestration/gateway.py`
- `backend/app/llm_orchestration/schemas.py`
- `backend/app/llm_orchestration/services/persona_composer.py`
- `backend/app/llm_orchestration/services/prompt_registry_v2.py`
- `backend/app/services/ai_engine_adapter.py`
- `backend/app/services/chart_json_builder.py`
- `backend/app/services/cross_tool_report.py`
- `backend/app/services/feature_flag_service.py`
- `backend/app/services/natal_interpretation_service.py`
- `backend/app/services/user_astro_profile_service.py`
- `backend/app/api/v1/routers/astrologers.py`
- `backend/app/api/v1/schemas/natal_interpretation.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/infra/db/models/user_natal_interpretation.py`
- `backend/app/core/config.py`
- `backend/scripts/seed_28_4.py`
- `backend/scripts/seed_29_prompts.py`
- `backend/scripts/seed_30_2_astroresponse_v2.py`
- `backend/scripts/seed_30_3_gpt5_prompts.py`
- `backend/scripts/seed_30_5_new_use_cases.py`
- `backend/scripts/seed_natal_short.py`
- `backend/scripts/create_tables.py`
- `backend/scripts/fix_schemas_strict.py`
- `backend/migrations/env.py`
- (+ 10 fichiers de migrations Alembic)

**Fichiers de tests :**
- `backend/app/llm_orchestration/tests/test_gateway_model_override.py`
- `backend/app/llm_orchestration/tests/test_prompt_lint.py`
- `backend/app/tests/unit/test_gateway_3_roles.py`
- `backend/app/tests/unit/test_gateway_modes.py`
- `backend/app/tests/unit/test_responses_client_exceptions.py`
- `backend/app/tests/unit/test_responses_client_gpt5.py`
- `backend/app/tests/unit/test_astro_response_v2.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_eval_harness_natal.py`
- `backend/app/tests/unit/test_natal_interpretation_service.py`
- `backend/app/tests/unit/test_natal_interpretation_service_v2.py`
- `backend/app/tests/unit/test_prompt_lint_natal.py`
- `backend/app/tests/unit/test_natal_pro_docs.py`
- `backend/app/tests/unit/test_natal_tt.py`
- `backend/app/tests/golden/fixtures.py`
- `backend/app/tests/unit/test_golden_zodiac_sidereal_ayanamsa.py`
- `backend/app/tests/unit/test_houses_provider.py`
- `backend/app/tests/unit/test_natal_calculation_service.py`
- `backend/app/tests/integration/test_admin_llm_natal_prompts.py`
- `backend/app/tests/integration/test_gateway_gpt5_params.py`
- `backend/app/tests/integration/test_natal_interpretation_endpoint.py`
- `backend/app/tests/integration/test_user_natal_chart_api.py`

**Fichiers non-applicatifs commités (à nettoyer) :**
- `docs/chat/plan_implementation_chat_memoire.md` — planning interne, ne devrait pas être dans le repo
- `src/app/AppProviders.test.tsx` — origine à clarifier (migration FSD ?)
- `src/shared/api/client.test.ts` — idem
- `src/shared/config/env.ts` — idem
- `src/shared/hooks/useClearPriceLookupCache.test.tsx` — idem
- `src/widgets/DevTerminalConsole/DevTerminalConsole.test.tsx` — idem

### Validation

- [x] Tests unitaires exceptions provider : 3/3 passent (`test_responses_client_exceptions.py`)
- [x] Test 3-rôles : 2/2 passent (`test_gateway_3_roles.py`)
- [x] Tests gateway modes : passent (`test_gateway_modes.py`)
- [x] Tests intégration Chat avec historique : passent (`test_user_natal_chart_api.py`)

### Change Log

| Date | Auteur | Description |
|------|--------|-------------|
| 2026-03-03 | dev-agent | Implémentation initiale (commit e318d05) |
| 2026-03-08 | AI-Review | Corrections : C3 exceptions v2, M1 is_reasoning_model, M2 chart_json_in_prompt, M3 guidance structured output, L1 gpt-5 prefix, L2 minItems seed |
