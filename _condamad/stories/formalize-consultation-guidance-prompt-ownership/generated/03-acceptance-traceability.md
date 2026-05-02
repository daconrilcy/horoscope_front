# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Consultation ownership documented. | `docs/llm-prompt-generation-by-feature.md` documents consultations as `guidance_contextual`; before/after routing artifacts persisted. | `rg -n "guidance_contextual" docs/llm-prompt-generation-by-feature.md` | PASS |
| AC2 | Placeholder contract tested. | `backend/app/tests/unit/test_guidance_service.py` asserts contextual consultation context carries `situation`, `objective`, `time_horizon`, `natal_chart_summary` and `guidance_contextual`. | `pytest -q app/tests/unit/test_guidance_service.py` and targeted combined pytest | PASS |
| AC3 | Precheck refusal stops LLM. | `backend/app/tests/unit/test_consultation_generation_service.py` asserts `safeguard_refused` returns before `GuidanceService.request_contextual_guidance_async`. | `pytest -q app/tests/unit/test_consultation_generation_service.py` and targeted combined pytest | PASS |
| AC4 | No consultation family drift. | `backend/tests/llm_orchestration/test_prompt_governance_registry.py` asserts `consultation` is absent from canonical families and `consultation_contextual` is rejected as unknown family. | `pytest -q tests/llm_orchestration/test_prompt_governance_registry.py`; forbidden symbol scan classified | PASS |
