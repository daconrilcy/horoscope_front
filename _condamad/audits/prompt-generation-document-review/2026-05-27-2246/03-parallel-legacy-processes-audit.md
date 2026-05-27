<!-- Commentaire global: audit specialise CS-353 des processus paralleles, legacy et non nominaux de generation de prompts LLM. -->

# parallel-legacy-processes-audit - CS-353

## Resume executif

Decision finale: `parallel processes confirmed; documentation correction required`.

L'audit confirme plusieurs processus provider-capable hors flux natal moderne `llm_astrology_input_v1`: Guidance, Guidance contextuelle, Chat public et Horoscope daily. Ils reutilisent `AIEngineAdapter` ou `LLMGateway`, mais leurs inputs prompt-visible ne sont pas le carrier natal moderne: ils utilisent des resumes textuels, un contexte conversationnel ou une question de narration quotidienne.

Les chemins repair et fallback sont non nominaux. Les seeds/bootstrap sont des entrees de provisioning. Les samples/admin manual execution sont admin-only mais peuvent atteindre le gateway. Les carriers `chart_json` et `natal_data` restent exclus du prompt natal moderne, mais `chart_json` existe encore dans `event_guidance`, les samples admin, des fixtures et des tests.

## Methode et scans executes

| Evidence | Command or source | Purpose |
|---|---|---|
| E-001 | `_condamad/stories/CS-353-audit-process-paralleles-generation-prompt-llm/00-story.md` | Scope, statuses and required deliverable. |
| E-002 | `_story_briefs/cs-353-audit-process-paralleles-legacy-generation-prompt-llm.md` | Source alignment and candidate process list. |
| E-003 | `rg -n "RG-018|RG-019|RG-020|RG-021|RG-022|RG-017" _condamad/stories/regression-guardrails.md` | Applicable guardrails and exact guardrail gap. |
| E-005 to E-009 | CS-343 to CS-347 audit reads | Prior cartography source truth. |
| E-011 | `rg` over guidance route/service/adapter | Guidance trigger and gateway handoff. |
| E-012 | `rg` over chat route/service/shared context/adapter | Chat trigger and gateway handoff. |
| E-013 | `rg` over horoscope narration/public prediction | Horoscope daily trigger and gateway handoff. |
| E-014 | `rg` over bootstrap guidance and horoscope seeds | Seed/bootstrap classification. |
| E-015 | `rg` over fallback catalog and gateway | Fallback catalog owner and no-assembly/provider fallback classification. |
| E-016 | `rg` over repair modules and gateway | Repair-only recovery classification. |
| E-017 | `rg` over admin manual execution and sample payloads | Admin-only provider-capable classification. |
| E-018 | `rg` over backend tests | Existing guard/test evidence. |

## Inventaire des processus paralleles et legacy

| process | status | trigger | owner | configuration source | prompt-visible input | renderer or assembly | provider handoff | modern natal boundary | risk if ignored |
|---|---|---|---|---|---|---|---|---|---|
| Guidance | runtime active | `/v1/guidance` -> `GuidanceService.request_guidance` | `backend/app/services/llm_generation/guidance/guidance_service.py` / `request_guidance_async` | guidance assembly/profile via `AIEngineAdapter.generate_guidance` and gateway resolution | `natal_chart_summary`, current context, persona line, period context | `PromptRenderer` through `LLMGateway._resolve_plan`; textual summary context | provider-capable via `AIEngineAdapter.generate_guidance` -> `LLMGateway.execute_request` | outside `llm_astrology_input_v1`; uses textual natal summary | CS-350 can imply only natal rich flow reaches provider |
| Guidance contextuelle | runtime active | `/v1/guidance/contextual` -> `GuidanceService.request_contextual_guidance` | `backend/app/services/llm_generation/guidance/guidance_service.py` / `request_contextual_guidance_async` | guidance contextual assembly/profile via gateway | `situation`, `objective`, `time_horizon`, `natal_chart_summary`, context lines | `PromptRenderer` through gateway | provider-capable via adapter/gateway | outside `llm_astrology_input_v1`; textual summary carrier | contextual prompts can be missed as parallel provider path |
| Chat public | runtime active | `/v1/chat` -> `ChatGuidanceService.send_message` | `backend/app/services/llm_generation/chat/chat_guidance_service.py` / `send_message_async` | chat assembly/profile via `AIEngineAdapter.generate_chat_reply` | user message, persona fields, opening profile or `natal_chart_summary` follow-up hint | gateway chat mode with `compose_chat_messages` | provider-capable via adapter/gateway | outside `llm_astrology_input_v1`; textual `build_chat_natal_hint` only on follow-up | chat prompt path can be collapsed into vague "LLM gateway" wording |
| Chat public helper | runtime active | public chat route response mapping | `backend/app/services/llm_generation/chat/public_chat.py` | none | none | none | not provider-capable itself | helper only; owner remains chat service | helper can be mistaken for prompt owner |
| Shared natal textual context | runtime active | guidance/chat service calls | `backend/app/services/llm_generation/shared/natal_context.py` / `build_natal_chart_summary`, `build_chat_natal_hint` | runtime chart/profile data and labels | textual natal summary/hint | none; returns text for caller prompt context | not provider-capable by itself | not `llm_astrology_input_v1`; legacy textual carrier for non-natal flows | textual natal carrier can be treated as harmless without prompt-path proof |
| Horoscope daily narration | runtime active | public prediction service -> `generate_horoscope_narration_via_gateway` | `backend/app/services/llm_generation/horoscope_daily/narration_service.py` | `horoscope_daily/narration` assembly/profile; plan from variant | question built from daily prediction context via `AstrologerPromptBuilder` | gateway structured mode plus governed assembly | provider-capable via direct `LLMGateway.execute_request` | outside modern natal input; uses daily prediction context | daily narration can be missed as active non-natal provider path |
| Legacy daily prediction route marker | runtime non nominal | `variant_code is None` in horoscope narration | `backend/app/services/llm_generation/horoscope_daily/narration_service.py` | same gateway path, logged as legacy route used | same as daily narration | same as daily narration | provider-capable but non-nominal route marker | outside modern natal input | legacy route signal can disappear from documentation |
| Fallback catalog | runtime non nominal | gateway fallback resolution when canonical config is unavailable or bounded fallback allowed | `backend/app/domain/llm/prompting/catalog.py` / `PROMPT_FALLBACK_CONFIGS`, `build_fallback_use_case_config` | synthetic fallback config entries `test_natal`, `test_guidance` | synthetic test placeholders | fallback `UseCaseConfig` consumed by gateway | provider-capable only if gateway executes fallback config | not modern natal nominal; test/synthetic fallback | fallback catalog can be promoted to runtime truth |
| No-assembly bootstrap fallback | runtime non nominal | `_allows_nominal_bootstrap_fallback` when no assembly rows exist | `backend/app/domain/llm/runtime/gateway.py` | DB state and gateway bounded fallback logic | depends on request context | gateway runtime metadata/fallback config | provider-capable only in bounded non-production/bootstrap condition | not modern natal nominal | blank local DB behavior can be mistaken for production path |
| Provider unsupported fallback | runtime non nominal | unsupported provider profile in non-nominal/test-fallback context | `backend/app/domain/llm/runtime/gateway.py` | provider support and mapper branches | original request messages | gateway provider parameter mapper | provider-capable via resolved OpenAI fallback | not modern natal nominal | provider fallback can be treated as nominal provider policy |
| Repair prompts | recovery | invalid provider output -> `_handle_repair_or_fallback` | `backend/app/domain/llm/runtime/repair_prompter.py` and `repair.py` | output schema plus validation errors | raw invalid output, errors and schema in repair prompt | `build_repair_prompt`; gateway re-entry with `is_repair_call` | provider-capable only after invalid output | post-provider recovery, not initial modern natal flow | repair prompt can be documented as normal prompt generation |
| Guidance bootstrap seeds | bootstrap/seed | seed script execution | `backend/app/ops/llm/bootstrap/seed_guidance_prompts.py` | static seed constants and DB rows | developer prompts, including `natal_chart_summary` and `event_guidance` `chart_json` | persisted prompt versions after seed | seed-only unless runtime loads resulting rows | outside modern natal input; `event_guidance` uses `chart_json` | seed prompt can be mistaken for current runtime source |
| Horoscope narrator bootstrap seed | bootstrap/seed | seed script execution | `backend/app/ops/llm/bootstrap/seed_horoscope_narrator_assembly.py` | static prompt/profile/assembly constants | daily narrator prompt text | persisted assembly rows | seed-only unless runtime loads resulting rows | outside modern natal input; provisions daily narrator | seed can be mistaken for runtime truth |
| Admin sample payloads | admin-only | admin CRUD for sample payloads | `backend/app/services/llm_generation/admin_sample_payloads.py` | persisted sample payloads | sample payload fields; natal sample requires `chart_json` | preview renderer in admin prompts | not provider-capable by itself | admin artifact, not public modern natal flow | admin sample can be mistaken for public prompt input |
| Admin manual execution | admin-only | `POST /v1/admin/llm/catalog/{manifest_entry_id}/execute` | `backend/app/api/v1/routers/admin/llm/prompts.py` / `execute_admin_catalog_sample_payload` | runtime preview plus sample payload | sample payload context copied to `ExecutionContext.extra_context` | gateway resolution from built manifest entry | provider-capable via direct `LLMGateway.execute_request` | admin-only; may include `chart_json` sample context | provider-capable admin path can be hidden by "no public runtime" wording |
| Legacy carriers `chart_json` and `natal_data` in modern natal | test-only | backend guard tests | `backend/tests/integration/test_llm_legacy_extinction.py`, `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` | test fixtures | forbidden carrier test inputs | test doubles | not provider-capable in tests | guards prove exclusion when `llm_astrology_input_v1` exists | future docs can omit the active guard evidence |
| Historical/admin/test `chart_json` samples | test-only | admin tests and fixtures | `backend/tests/integration/test_admin_llm_catalog.py`, `backend/tests/integration/test_admin_llm_sample_payloads.py` | test fixtures | `chart_json` sample values | test renderer/gateway doubles | test-only | not modern natal runtime | tests can be confused with runtime source |
| CS-350 narrative mentions | archival | documentation and prior audit artifacts | `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`, prior audits | documentation | none | none | not provider-capable | archival/source context only | archival claims can be treated as source truth without current code proof |
| `event_guidance` | debt | no public route found in audited guidance routes; seed/contract exists | `backend/app/ops/llm/bootstrap/seed_guidance_prompts.py`; `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | guidance seed and canonical contract with `chart_json` | `chart_json`, `event_description` | if invoked, gateway renderer | provider-capable only if invoked through adapter/gateway; no public trigger found in audited route set | outside modern natal input and still uses legacy carrier | needs migrate/delete/retain decision |

## Matrice statut par processus

| status | processes |
|---|---|
| runtime active | Guidance; Guidance contextuelle; Chat public; Chat public helper; Shared natal textual context; Horoscope daily narration |
| runtime non nominal | Legacy daily prediction route marker; Fallback catalog; No-assembly bootstrap fallback; Provider unsupported fallback |
| recovery | Repair prompts |
| bootstrap/seed | Guidance bootstrap seeds; Horoscope narrator bootstrap seed |
| test-only | Legacy carriers in modern natal tests; Historical/admin/test `chart_json` samples |
| admin-only | Admin sample payloads; Admin manual execution |
| archival | CS-350 narrative mentions |
| debt | `event_guidance` |

## Detail par processus candidat

### Guidance

- Evidence: E-011.
- Trigger: `/v1/guidance`.
- Owner: `backend/app/services/llm_generation/guidance/guidance_service.py`.
- Provider classification: provider-capable runtime active.
- Boundary: not the modern natal `llm_astrology_input_v1`; it uses textual `natal_chart_summary` and context fields.
- Required follow-up: document as active non-natal provider-capable flow.

### Chat public

- Evidence: E-012.
- Trigger: `/v1/chat`.
- Owner: `backend/app/services/llm_generation/chat/chat_guidance_service.py`.
- Provider classification: provider-capable runtime active.
- Boundary: not the modern natal `llm_astrology_input_v1`; it uses chat history, user message, persona fields and optional textual natal hint.
- Required follow-up: document as active chat-mode provider-capable flow.

### Horoscope daily

- Evidence: E-013, E-014.
- Trigger: public prediction service calling `generate_horoscope_narration_via_gateway`.
- Owner: `backend/app/services/llm_generation/horoscope_daily/narration_service.py`.
- Provider classification: provider-capable runtime active; legacy route marker is runtime non nominal when `variant_code is None`.
- Boundary: not the modern natal `llm_astrology_input_v1`; it builds a daily narration question and reuses gateway assembly.
- Required follow-up: document daily narration separately from natal interpretation.

### Fallback catalog and no-assembly fallback

- Evidence: E-015.
- Trigger: gateway fallback resolution branches.
- Owner: `backend/app/domain/llm/prompting/catalog.py` and `backend/app/domain/llm/runtime/gateway.py`.
- Provider classification: runtime non nominal; current catalog fallback prompts are synthetic tests.
- Boundary: not modern natal nominal.
- Required follow-up: keep fallback catalog out of runtime truth and cite RG-018/RG-021.

### Repair prompts

- Evidence: E-016.
- Trigger: invalid provider output after validation.
- Owner: `backend/app/domain/llm/runtime/repair_prompter.py`.
- Provider classification: recovery; provider-capable only as a second call after invalid output.
- Boundary: post-provider recovery, not initial prompt-generation source.
- Required follow-up: document as recovery, not as nominal prompt flow.

### Legacy carriers `chart_json` and `natal_data`

- Evidence: E-008, E-014, E-017, E-018.
- Trigger: modern natal guards, `event_guidance` seed, admin samples, fixtures and tests.
- Owner: multiple bounded contexts; modern natal owner excludes them.
- Provider classification: excluded from modern natal prompt; can appear in admin/test/seed/debt contexts.
- Boundary: forbidden carrier for modern natal prompt-visible material when `llm_astrology_input_v1` exists.
- Required follow-up: make carrier status explicit in CS-350 amendment.

## Processus confirmes comme provider-capable

| process | provider capability | proof |
|---|---|---|
| Guidance | provider-capable runtime active | E-011: public route -> service -> `AIEngineAdapter.generate_guidance` -> `LLMGateway.execute_request`. |
| Guidance contextuelle | provider-capable runtime active | E-011: contextual route -> service -> adapter -> gateway. |
| Chat public | provider-capable runtime active | E-012: public chat route -> `ChatGuidanceService` -> `AIEngineAdapter.generate_chat_reply` -> gateway. |
| Horoscope daily narration | provider-capable runtime active | E-013: daily narration service directly calls `LLMGateway.execute_request`. |
| Admin manual execution | provider-capable admin-only | E-017: admin route builds `LLMExecutionRequest` and calls gateway. |
| Repair prompts | provider-capable recovery-only | E-016: repair request re-enters gateway after invalid output. |
| Fallback catalog/no-assembly/provider fallback | provider-capable only in bounded non-nominal cases | E-015: gateway fallback branches can produce executable config or resolved provider fallback. |

## Processus seulement bootstrap, test, admin ou archive

| process | status | proof |
|---|---|---|
| Guidance prompt seeds | bootstrap/seed | E-014: seed script writes prompt versions; no execution by itself. |
| Horoscope narrator assembly seed | bootstrap/seed | E-014: seed script provisions prompt/profile/assembly and archives legacy rows. |
| Admin sample payload CRUD | admin-only | E-017: sample payload validation and persistence, no provider handoff by itself. |
| Admin manual execution | admin-only | E-017: provider-capable but admin route only. |
| Carrier guard tests | test-only | E-018: tests assert exclusion/redaction and use local doubles/fixtures. |
| CS-350 and prior audit mentions | archival | E-004 to E-010: documentation evidence only. |

## Gaps documentaires

| Gap | Evidence | Required correction |
|---|---|---|
| CS-350 has no single matrix for active non-natal provider-capable flows. | E-010 to E-013 | Add rows for guidance, contextual guidance, chat and daily horoscope. |
| `event_guidance` is not decisioned. | E-014, E-015 | Choose migrate, delete, or retain as explicit debt before implementation. |
| Admin manual execution is provider-capable but admin-only. | E-017 | Add admin-only classification or create a dedicated admin execution policy story. |
| Exact guardrail for parallel-process classification is absent. | E-003 | Add only after documentation matrix becomes a durable invariant. |
| `chart_json` and `natal_data` appear in seed/admin/test contexts. | E-014, E-017, E-018 | State they are excluded from modern natal prompt material but still exist in bounded non-modern contexts. |

## Stories candidates de correction ou de documentation

| Candidate | Source finding | Objective | Closure |
|---|---|---|---|
| SC-001 | F-001 | Amend CS-350 with a parallel-process matrix covering runtime active, non-nominal, recovery, bootstrap, test, admin, archival and debt statuses. | full closure for F-001 |
| SC-002 | F-004 | Add exact regression guardrail after the matrix is accepted as durable. | full closure for F-004 |
| Decision item | F-002 | Decide `event_guidance`: migrate, delete, or retain as explicit debt. | blocked pending user/product decision |
| Decision item | F-003 | Decide admin manual execution documentation/policy. | blocked pending user/product decision |

