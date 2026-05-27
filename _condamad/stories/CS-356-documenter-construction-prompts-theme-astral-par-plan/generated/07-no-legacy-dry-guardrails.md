# No Legacy / DRY Guardrails

## CS-356 scoped guardrails

| Guardrail | Implementation invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Documentation work must not move backend ownership into API or docs files. | `evidence/validation.txt` VC8 proves `backend/app`, `backend/tests`, and `frontend/src` are unchanged. |
| RG-149 `CS-350-prompt-generation-current-implementation` | `chart_json` and `natal_data` must not become modern natal prompt-visible inputs, and non-natal provider-capable flows must remain outside `llm_astrology_input_v1`. | The document explicitly classifies `chart_json`, `natal_data`, admin samples, guidance, chat public, horoscope daily and provider unsupported paths as non-modern or out of `llm_astrology_input_v1`; VC4/VC5 scans passed. |
| RG-041 non-applicable | Entitlement documentation is outside CS-356 scope. | Manual review: no entitlement endpoint, table, or security claim was introduced. |

## Forbidden unless explicitly required by the story

- Compatibility wrappers
- Transitional aliases
- Legacy import paths
- Duplicate active implementations
- Re-export modules preserving old imports
- Silent fallback behavior
- Tests that preserve legacy paths as nominal behavior

## Required when relevant

- One canonical path per responsibility
- Negative search evidence for removed symbols or imports
- Tests or architecture guards that fail if a legacy path is reintroduced
- Explicit errors instead of silent fallback for missing canonical configuration

## Reviewer questions

- Did we delete the legacy path or only move the problem?
- Did we preserve an old path “temporarily”?
- Did any test import the old namespace?
- Did any doc, registry, or config still reference the old path?
