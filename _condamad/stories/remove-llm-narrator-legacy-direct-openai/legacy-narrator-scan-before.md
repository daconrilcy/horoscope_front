# Legacy Narrator Scan Before

## Commands

- `rg -n "LLMNarrator|llm_narrator" backend/app backend/tests docs`
- `rg -n "chat\.completions\.create|openai\.AsyncOpenAI" backend/app backend/tests`
- `rg -n "from app\.prediction\.llm_narrator import LLMNarrator|LLMNarrator\(|LLMNarrator\.narrate" backend/tests backend/app/tests -g "test_*.py"`

## Summary

| Pattern | Classification | Evidence |
|---|---|---|
| `backend/app/prediction/llm_narrator.py` | active legacy runtime | Defines `LLMNarrator`, imports `openai`, constructs `openai.AsyncOpenAI`, calls `client.chat.completions.create`. |
| `app.prediction.llm_narrator` contract imports | active legacy coupling | `adapter.py`, `narration_service.py`, migration tests, and app tests import `NarratorResult` / `NarratorAdvice` from the legacy module. |
| `llm_narrator_enabled` | feature flag naming | Config/API/projection flag still controls whether canonical narration is generated; not the direct provider runtime. |
| docs hits | historical documentation | Audit docs reference the deprecated module as obsolete. |
| collected tests importing `LLMNarrator` class | absent | Zero hits for class import/instantiation/narrate patch in collected test files. |
