# CONDAMAD Domain Audit - prompt-generation - 2026-05-02-1452

## Scope

- Domain target: `prompt-generation`
- Archetype: service-boundary-audit with No Legacy / DRY overlay
- Previous audit baseline: `_condamad/audits/prompt-generation/2026-04-30-1810`
- Stories re-audited: `remove-llm-narrator-legacy-direct-openai`, `block-supported-family-prompt-fallbacks`, `converge-horoscope-daily-narration-assembly`, `formalize-consultation-guidance-prompt-ownership`
- Mode: read-only for application code; audit artifacts written under `_condamad/audits/**`
- Guardrails consulted: `_condamad/stories/regression-guardrails.md`

## Expected responsibility

Le domaine de generation de prompt doit conserver un proprietaire canonique unique pour les consignes LLM durables: assemblies, contrats, renderer, gateway et provider wrapper. Les services de feature preparent le contexte metier, mais ne doivent pas maintenir de prompts concurrents, de fallbacks legacy nominaux ou d'appels provider directs.

## Re-audit conclusion

Les quatre findings principaux du 2026-04-30 sont majoritairement resolus dans le code:

- `LLMNarrator` et les appels directs `openai.AsyncOpenAI` / `chat.completions.create` ne sont plus presents dans `backend/app` ni `backend/tests`.
- Les cles fallback explicitement interdites pour `chat_astrologer`, `guidance_contextual`, `natal_interpretation` et `horoscope_daily` sont absentes de `PROMPT_FALLBACK_CONFIGS` et gardees par tests.
- `AstrologerPromptBuilder` est redevenu un builder de contexte quotidien; les consignes durables de narration vivent dans la seed d'assembly `horoscope_daily/narration`.
- La consultation specifique est documentee et testee comme sous-cas de `guidance_contextual`, sans famille LLM `consultation`.

Le risque residuel principal est plus borne que dans l'audit precedent: `PROMPT_FALLBACK_CONFIGS` reste executable pour une allowlist d'exceptions, dont plusieurs use cases canoniques (`natal_interpretation_short`, `guidance_daily`, `guidance_weekly`, `event_guidance`). Le gateway limite le fallback des familles supportees en production, mais le registre fallback conserve encore des prompts durables qui peuvent alimenter des chemins bootstrap/use-case-first. Cette dette est documentee par la story, mais elle reste une surface DRY / No Legacy a converger si l'objectif final est zero fallback prompt canonique.

## Findings summary

| Severity | Count | Findings |
|---|---:|---|
| Critical | 0 | - |
| High | 0 | - |
| Medium | 1 | F-001 |
| Low | 1 | F-002 |
| Info | 4 | F-003, F-004, F-005, F-006 |

## Mandatory audit dimensions

### DRY

Partial. Les prompts fallback des familles explicitement ciblees par la story sont supprimes, mais `PROMPT_FALLBACK_CONFIGS` reste un second proprietaire executable pour certaines exceptions canoniques ou proches du nominal.

### No Legacy

Partial. La surface legacy directe `LLMNarrator` est eteinte. La dette restante est le fallback prompt allowliste, qui reste auditable mais executable.

### Mono-domain ownership

Pass for `horoscope_daily` and consultation-specific ownership. Partial for fallback exceptions because une partie du texte prompt durable demeure dans `backend/app/domain/llm/prompting/catalog.py` au lieu d'etre uniquement portee par assemblies/prompts gouvernes.

### Dependency direction

Pass. Aucun import `app.api`, `HTTPException` ou `JSONResponse` n'a ete trouve dans `domain/llm`, `services/llm_generation` ou `prediction` pour le scope audite.

## Guardrail mapping

| Guardrail | Status | Evidence |
|---|---|---|
| `RG-016` | respected | E-002, E-010 |
| `RG-017` | respected | E-002, E-010 |
| `RG-018` | respected for explicitly supported fallback keys | E-003, E-004, E-010 |
| `RG-019` | respected | E-005, E-006, E-010 |
| `RG-020` | respected | E-007, E-008, E-010 |
| `RG-006` | respected | E-009 |

## Files created

- `00-audit-report.md`
- `01-evidence-log.md`
- `02-finding-register.md`
- `03-story-candidates.md`
- `04-risk-matrix.md`
- `05-executive-summary.md`
