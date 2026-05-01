# No Legacy / DRY Guardrails

## Canonical ownership

| Responsibility | Canonical owner | Forbidden destination |
|---|---|---|
| Daily factual payload | `backend/app/prediction/astrologer_prompt_builder.py` | assembly-only text duplication of daily facts |
| Durable narration instructions | governed `horoscope_daily/narration` assembly | `AstrologerPromptBuilder` |
| Plan-specific daily synthesis length | assembly plan rules | builder variant method |
| Post-gateway sentence validation | `backend/app/services/llm_generation/horoscope_daily/narration_service.py` | prompt builder or adapter |

## Forbidden markers

- `Format attendu` in `backend/app/prediction/astrologer_prompt_builder.py`
- `Interdiction` in `backend/app/prediction/astrologer_prompt_builder.py`
- `daily_synthesis : strictement` in `backend/app/prediction/astrologer_prompt_builder.py`
- Durable narration instruction text in `AIEngineAdapter`
- Direct provider calls in horoscope daily runtime

## Guardrails used

- `RG-006`: non-API layers must not import `app.api`.
- `RG-016`: tests must not consume deprecated `LLMNarrator` nominally.
- `RG-017`: horoscope daily runtime must not reintroduce direct provider calls.
- `RG-019`: durable daily narration instructions remain in governed assembly.

## Search classification

| Pattern | Result | Classification | Status |
|---|---|---|---|
| `Format attendu\|Interdiction\|daily_synthesis : strictement` in builder | zero hits | active legacy removed | PASS |
| same markers in adapter / horoscope daily service | zero hits | adapter remains non-owner | PASS |
| migrated instruction positive scan | hits only in `seed_horoscope_narrator_assembly.py` and `assembly_resolver.py` | canonical ownership | PASS |
| `from app\.api\|import app\.api` in non-API layers | zero hits | RG-006 preserved | PASS |
| `LLMNarrator` nominal test consumption | zero hits | RG-016 preserved | PASS |
| direct OpenAI / LLMNarrator runtime scan | zero hits | RG-017 preserved | PASS |
