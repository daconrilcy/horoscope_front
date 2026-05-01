# No Legacy / DRY Guardrails

## Canonical ownership

| Responsibility | Canonical owner | Forbidden legacy owner |
|---|---|---|
| Daily horoscope narration use case | `backend/app/services/llm_generation/horoscope_daily` | `backend/app/prediction/llm_narrator.py` |
| Narration contract dataclasses | `backend/app/domain/llm/prompting/narrator_contract.py` | `backend/app/prediction/llm_narrator.py` |
| Provider execution | `backend/app/infra/providers/llm` | `backend/app/prediction` |
| Application facade | `backend/app/domain/llm/runtime/adapter.py` | any direct narrator facade |

## Forbidden patterns

- Compatibility wrapper for `LLMNarrator`.
- Re-export preserving `app.prediction.llm_narrator`.
- Direct `openai.AsyncOpenAI` outside provider canonical.
- Direct `chat.completions.create` outside provider canonical.
- Tests importing or instantiating the deprecated narrator class.
- Silent fallback from gateway narration back to the legacy provider path.

## Required negative evidence

- `backend/app/prediction/llm_narrator.py` removed.
- Active imports of `app.prediction.llm_narrator` removed from app/tests.
- Guard test fails on reintroduction of narrator class usage.
- Provider direct scan has no active hits outside canonical provider.

## Applicable regression guardrails

- `RG-016`: tests backend must not consume nominally deprecated narrator class.
- `RG-017`: horoscope daily runtime must not reintroduce provider direct via narrator or direct OpenAI calls outside provider canonical.
- `RG-006`: non-API layers must not import `app.api`; this story must not touch that boundary.

## Review checklist

- No old module preserved as shim.
- No alias or re-export keeps the old import path alive.
- The dataclass contract has one owner.
- Remaining `llm_narrator_enabled` hits are classified as feature flag naming, not executable facade usage.
