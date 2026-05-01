# Legacy Narrator Scan After

## Commands

- `rg -n "LLMNarrator|llm_narrator" app tests ..\docs` from `backend/`: exit 0 with classified residual hits.
- `rg -n "LLMNarrator\(|from app\.prediction\.llm_narrator import LLMNarrator|chat\.completions\.create|openai\.AsyncOpenAI" app tests` from `backend/`: exit 1, zero hits.
- `rg -n "LLMNarrator|llm_narrator" ..\frontend\src app\api ..\docs` from `backend/`: exit 0 with classified residual hits.

## Classified residual hits

| Pattern | Location | Classification | Action | Status |
|---|---|---|---|---|
| `llm_narrator_enabled` | `app/core/config.py`, API routers, `app/prediction/public_projection.py`, app tests | feature flag naming | Left unchanged because the story does not rename config or API behavior. It now gates canonical narration via `AIEngineAdapter`. | allowed residual |
| `_LEGACY_MODULE`, `legacy_path` | `tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | test guard expected hit | Required guard evidence against reintroduction of old module. | allowed residual |
| `legacy_residual_registry.json` historical text | `app/domain/llm/governance/data/legacy_residual_registry.json` | governance historical reference | Records residual context; not executable runtime. | allowed residual |
| audit docs | `docs/2026-04-20-audit-prompts-backend*.md` | historical documentation | Existing audit evidence predates this story. | allowed residual |
| direct provider call patterns | `app tests` | none | Zero active hits for direct OpenAI call patterns and class instantiation/import pattern. | PASS |

## Result

The executable facade `backend/app/prediction/llm_narrator.py` and its direct provider path are absent. Remaining `llm_narrator` hits are feature-flag naming, guard code, or historical documentation.
