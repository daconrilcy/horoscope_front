# Consultation routing after

## Snapshot

- Runtime LLM owner: `GuidanceService.request_contextual_guidance_async`
- Runtime use case: `guidance_contextual`
- Runtime prompt family: `guidance`
- Consultation precheck refusal: returns a business response before any `GuidanceService` call.
- `consultation_template.prompt_content`: classified as short product objective, not durable provider prompt.

## Guarded invariant

Consultations specific remain a documented subcase of `guidance_contextual`. A new `consultation` family or `consultation_contextual` use case must fail governance tests until a product decision changes the ownership model.
