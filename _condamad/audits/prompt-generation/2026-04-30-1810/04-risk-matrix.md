# Risk Matrix - prompt-generation - 2026-04-30-1810

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | Medium | `horoscope_daily` runtime | High | Medium | P1 |
| F-002 | High | Medium | All supported LLM prompt families | High | Medium | P1 |
| F-003 | Medium | High | `horoscope_daily` narration quality/governance | Medium | Medium | P2 |
| F-004 | Medium | Medium | Consultation/guidance product taxonomy | Medium | Medium | P2 |
| F-005 | Info | Low | Prompt generation boundary | Low | Low | P3 |
| F-006 | Info | Medium | Future prompt-generation stories | Low | Low | P3 |

## Guardrails mapping

| Guardrail | Applicabilite | Findings |
|---|---|---|
| RG-004 | Services LLM ne doivent pas dependre de FastAPI/API errors. | F-005 |
| RG-005 | Les routes/API ne doivent pas reprendre de logique metier; l'audit cible les services. | F-005 |
| RG-006 | Les couches non API n'importent pas `app.api`. | F-005 |
| RG-016 | Tests nominaux ne doivent pas redevenir consommateurs de `LLMNarrator`; l'audit etend le risque au code runtime restant. | F-001 |

## BMAD 70 risk overlays

| Overlay | Source | Risque couvert | Findings |
|---|---|---|---|
| Namespace canonique | Audit 2026-04-21, stories 70.14-70.15 | Reintroduire `app.llm_orchestration.*`, `app.prompts.*` ou un bridge legacy pour corriger vite. | F-001, F-002 |
| Admin runtime honesty | Stories 70.9-70.12 | Corriger le runtime sans que l'admin montre les vraies couches, versions, diffs et artefacts provider. | F-002, F-003 |
| QA executable proof | Story 70.16 | Declarer le pipeline couvert sans revalider guidance/chat/natal/horoscope via routes/tests QA canoniques. | F-002, F-003, F-004 |
| Adapter minimal | Story 70.20 | Replacer dans `AIEngineAdapter` des heuristiques de narration, prompting durable ou fallback de test. | F-001, F-003 |
| Services DRY | Stories 70.21, 70.23 | Ajouter un nouveau service LLM a plat, un alias transitoire ou une duplication entre feature service, prediction et domaine LLM. | F-001, F-003, F-006 |

## Coverage risk conclusion

Le risque architectural principal n'est plus une absence de socle canonique: ce socle existe et a ete valide par 70.15/70.16. Le risque restant est une divergence d'execution autour des bords: fallback, narrateur legacy direct-provider, builder quotidien trop instructif et taxonomie consultation non formalisee.
