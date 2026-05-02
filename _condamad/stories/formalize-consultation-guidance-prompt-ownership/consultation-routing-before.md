# Consultation routing before

## Snapshot

- Source inspected: `backend/app/services/llm_generation/consultation_generation_service.py`
- Current LLM owner: `GuidanceService.request_contextual_guidance_async`
- Current use case: `guidance_contextual`
- Current prompt family: `guidance`
- Current product objective source: request `objective`, then `consultation_template.prompt_content`, then static objective labels.

## Observed invariant

Consultations already route through contextual guidance. No `consultation` LLM family is present in `prompt_governance_registry.json`.

## Risk to guard

The product field `prompt_content` can be mistaken for a provider `developer_prompt`. The implementation must document and test that it remains a short product objective only.
