# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | LLMNarrator warning baseline is persisted. | Added before/after warning artifacts under this story directory. | `pytest -q tests/unit/prediction/test_llm_narrator.py` captured before; `pytest -q -W error::DeprecationWarning tests/unit/prediction` captured after. | PASS |
| AC2 | Canonical narration adapter has equivalent coverage. | Updated `backend/tests/unit/prediction/test_llm_narrator.py` to exercise `AIEngineAdapter.generate_horoscope_narration`. | `pytest -q tests/unit/prediction/test_llm_narrator.py` passed. | PASS |
| AC3 | Prediction tests reject unclassified deprecations. | Removed nominal deprecated class usage from prediction tests. | `pytest -q -W error::DeprecationWarning tests/unit/prediction` passed. | PASS |
| AC4 | `LLMNarrator` class usage is guarded. | Added `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py`. | Guard test passed; forbidden-symbol `rg` scan returned zero active hits. | PASS |
| AC5 | Compatibility decision is persisted. | Added `llm-narrator-deprecation-decision.md` with migration decision and expiry rule. | `rg -n "LLMNarrator|decision|expiry" _condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-deprecation-decision.md` returned expected decision hits. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
