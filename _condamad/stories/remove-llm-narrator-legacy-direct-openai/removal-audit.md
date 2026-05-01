# Removal Audit

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `LLMNarrator` | class | `historical-facade` | No collected nominal tests; runtime module present before story only. | `AIEngineAdapter.generate_horoscope_narration` | `delete` | module deleted; guard test passes | none identified |
| `backend/app/prediction/llm_narrator.py` | module | `historical-facade` | Contract dataclass imports migrated before deletion. | `app.domain.llm.prompting.narrator_contract` for dataclasses; gateway service for execution | `delete` | file deleted; direct provider scan zero-hit | none identified |
| `NarratorResult` / `NarratorAdvice` | contract types | `canonical-active` | Adapter, narration service, tests. | `app.domain.llm.prompting.narrator_contract` | `replace-consumer` | imports migrated and tests pass | shape preserved as dataclasses |
