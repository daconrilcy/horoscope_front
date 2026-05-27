<!-- Commentaire global: matrice de risques pour l'audit CS-353 des processus paralleles LLM. -->

# Risk Matrix

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Medium | High | Documentation and future prompt-generation stories | Medium: future work may miss active non-natal provider-capable flows | Small documentation correction | P1 |
| F-002 | Medium | Medium | Guidance configuration and bootstrap debt | Medium: legacy `chart_json` seed can be normalized by inertia | Product decision then small targeted story | P1 |
| F-003 | Medium | Medium | Admin LLM execution and sample payload governance | Medium: admin-only provider capability can be understated or overstated | Product decision then bounded docs/policy work | P2 |
| F-004 | Low | Medium | Guardrail registry and future stories | Low: adjacent guardrails exist but exact classification may drift | Small governance update after SC-001 | P2 |
| F-005 | Info | Low | Documentation references | Low: existing carrier guards already exist | Reference reuse only | P3 |

