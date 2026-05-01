# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Facade inventory completed. | Baseline before/after and removal audit persisted; legacy runtime module deleted. | `legacy-narrator-scan-before.md`; `legacy-narrator-scan-after.md`; `rg -n "LLMNarrator|llm_narrator" app tests ..\docs` hits classified. | PASS |
| AC2 | Canonical narration owner used. | `NarratorResult` / `NarratorAdvice` moved to `app.domain.llm.prompting.narrator_contract`; app/tests import canonical contract. | `pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py` PASS; targeted combined tests PASS. | PASS |
| AC3 | Direct provider path absent. | `backend/app/prediction/llm_narrator.py` deleted; direct provider calls removed with the module. | `rg -n "LLMNarrator\(|from app\.prediction\.llm_narrator import LLMNarrator|chat\.completions\.create|openai\.AsyncOpenAI" app tests` zero hits. | PASS |
| AC4 | Migration tests preserved. | `tests/llm_orchestration/test_narrator_migration.py` imports canonical contract and still asserts adapter/gateway routing. | `pytest -q tests/llm_orchestration/test_narrator_migration.py` PASS; combined targeted tests PASS. | PASS |
| AC5 | Regression guard registry honored. | `test_llm_narrator_deprecation_guard.py` now checks tests, runtime surface absence, and direct provider calls outside canonical provider. | `pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py` PASS; `RG-016` / `RG-017` mapped. | PASS |
