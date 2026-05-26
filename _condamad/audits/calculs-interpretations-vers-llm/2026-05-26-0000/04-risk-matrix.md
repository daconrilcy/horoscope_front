# Risk Matrix - Calculs Interpretations Vers LLM

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | High | Natal LLM prompt input | LLM narration remains based on legacy/transition inputs while richer canonical facts are available. | Medium | P1 |
| F-002 | Medium | Medium | LLM runtime contract | Duplicate `chart_json` / `natal_data` representations drift or conflict in prompt/runtime context. | Medium | P2 |
| F-003 | Medium | Medium | LLM evidence validation | Evidence references do not cover recent stable facts, reducing answer auditability. | Medium | P2 |
| F-004 | Low | Medium | Astral-point context naming | `astro_context` is mistaken for a full astrology context. | Low | P3 |
