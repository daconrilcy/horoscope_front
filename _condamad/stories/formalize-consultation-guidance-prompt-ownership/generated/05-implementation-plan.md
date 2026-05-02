# Implementation Plan

## Initial repository findings

- `ConsultationGenerationService.generate()` already delegates nominal LLM execution to `GuidanceService.request_contextual_guidance_async`.
- `GuidanceService.request_contextual_guidance_async()` uses `use_case = "guidance_contextual"` and builds a context with `situation`, `objective`, `time_horizon`, `natal_chart_summary`.
- `prompt_governance_registry.json` canonical families are `chat`, `guidance`, `natal`, `horoscope_daily`; no `consultation` family exists.
- `consultation_template.prompt_content` is read only by `_build_consultation_objective()`.

## Proposed changes

- Document consultation-specific ownership in the prompt generation doc.
- Add a guidance test proving the contextual placeholder contract used by consultation.
- Add a consultation service test proving `safeguard_refused` returns before guidance/LLM.
- Add a governance test blocking `consultation` family drift and `consultation_contextual`.
- Persist before/after routing evidence in the story capsule.

## Files to delete

- None.

## Risk assessment

- Low runtime risk: no production code changed.
- Main risk is documentation/test drift if future product work intentionally introduces a consultation family without updating governance.

## Rollback strategy

- Revert documentation and tests added by this story; no data or runtime migration involved.
