<!-- Commentaire global: carte des symboles runtime audites pour CS-345. -->

# Runtime Handoff Symbol Map

| Symbol | Path | Role | Provider visibility | Evidence |
|---|---|---|---|---|
| `LLMGateway.execute_request` | `backend/app/domain/llm/runtime/gateway.py` | Sequenced runtime entrypoint | runtime-only orchestration | E-005, E-011 |
| `LLMGateway._resolve_plan` | `backend/app/domain/llm/runtime/gateway.py` | Resolves config, schema, profile and provider params into plan | runtime-only | E-005, E-011 |
| `LLMGateway._validate_input` | `backend/app/domain/llm/runtime/gateway.py` | Validates request/context against input schema before messages | validation-only | E-016 |
| `LLMGateway.build_user_payload` | `backend/app/domain/llm/runtime/gateway.py` | Builds final user prompt payload string | prompt-visible | E-006 |
| `_prompt_visible_llm_astrology_input` | `backend/app/domain/llm/runtime/gateway.py` | Filters rich natal input to prompt-visible roles | prompt-visible projection | E-006, E-013 |
| `LLMGateway.compose_structured_messages` | `backend/app/domain/llm/runtime/gateway.py` | Builds system, developer, optional persona, user messages | prompt-visible | E-007 |
| `LLMGateway.compose_chat_messages` | `backend/app/domain/llm/runtime/gateway.py` | Builds system, developer, optional persona, history, user messages | prompt-visible | E-007 |
| `LLMGateway._build_messages` | `backend/app/domain/llm/runtime/gateway.py` | Selects structured or chat composer | provider handoff payload owner | E-007, E-011 |
| `LLMGateway._call_provider` | `backend/app/domain/llm/runtime/gateway.py` | Last gateway boundary before provider manager | provider handoff | E-008, E-011 |
| `ProviderRuntimeManager.execute_with_resilience` | `backend/app/domain/llm/runtime/provider_runtime_manager.py` | Retries, timeout, breaker, provider call forwarding | provider handoff | E-009 |
| `ResponsesClient.execute` | `backend/app/infra/providers/llm/openai_responses_client.py` | Final adapter call shape for OpenAI Responses API | provider handoff | E-010 |
| `validate_output` | `backend/app/domain/llm/runtime/output_validator.py` | Post-provider output validation and evidence sanitization | validation-only | E-016 |
| `repair.build_repair_prompt` | `backend/app/domain/llm/runtime/repair.py` | Canonical runtime repair entrypoint imported by gateway | non nominal recovery | E-016 |
| `repair_prompter.build_repair_prompt` | `backend/app/domain/llm/runtime/repair_prompter.py` | Non-nominal repair prompt implementation | non nominal recovery | E-016 |
| `observability.log_call` | `backend/app/domain/llm/runtime/observability.py` | Canonical runtime observability entrypoint imported by gateway | audit-only | E-016 |
| `observability_service.log_call` | `backend/app/domain/llm/runtime/observability_service.py` | Call logs, operational metadata, replay snapshot implementation | audit-only | E-016 |
