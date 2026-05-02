# Risk Matrix - prompt-generation - 2026-05-02-1452

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Medium | Medium | Prompt fallback runtime | Medium | Medium | P1 |
| F-002 | Low | Medium | CONDAMAD evidence | Low | Small | P2 |
| F-003 | Info | Low | Horoscope narrator | Low | Small | P3 |
| F-004 | Info | Low | Horoscope assembly | Low | Small | P3 |
| F-005 | Info | Low | Consultation guidance | Low | Small | P3 |
| F-006 | Info | Low | Prompt generation boundary | Low | Small | P3 |

## Top risks

1. Fallback exceptions: risque residuel de duplication de prompt durable si une exception devient un chemin nominal.
2. Evidence drift: les chemins de tests invalides dans des stories peuvent affaiblir la reproductibilite de validation.
