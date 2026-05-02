# No Legacy / DRY Guardrails

## Canonical ownership

- Consultation orchestration: `backend/app/services/llm_generation/consultation_generation_service.py`.
- Contextual prompt execution: `backend/app/services/llm_generation/guidance/guidance_service.py`.
- Prompt taxonomy: `backend/app/domain/llm/governance/data/prompt_governance_registry.json`.

## Forbidden active paths

- New `consultation` canonical family in the prompt governance registry.
- New `consultation_contextual` use case without product decision.
- Mapping `consultation_template.prompt_content` into provider `developer_prompt`.
- New `PROMPT_FALLBACK_CONFIGS["consultation"]` or equivalent fallback.
- Guidance call after `safeguard_refused` or blocked precheck.

## Allowed exceptions

- `consultation_template.prompt_content` remains a short product objective used by `_build_consultation_objective()`.
- Existing `PROMPT_FALLBACK_CONFIGS` references remain allowed only where current tests already govern fallback catalog exceptions.

## Evidence required

- Unit test proving refusal precheck does not call guidance.
- Unit test proving consultation guidance context uses `situation`, `objective`, `natal_chart_summary`.
- Governance test proving no `consultation` family and no accepted `consultation_contextual` placeholders.
- Classified scan hits for forbidden symbols.

## Hit classification

| Pattern | Classification | Action | Status |
|---|---|---|---|
| `consultation_contextual` in governance test | `test_guard_expected_hit` | Keep as negative guard. | PASS |
| `"consultation"` in governance test | `test_guard_expected_hit` | Keep as negative guard. | PASS |
| `PROMPT_FALLBACK_CONFIGS` in existing catalog/tests | `allowed_historical_reference` | Existing fallback governance, no consultation family hit. | PASS |
| `developer_prompt.*prompt_content` | `negative_evidence` | No hits. | PASS |
