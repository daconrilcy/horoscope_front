<!-- Commentaire global: matrice des risques pour l'audit adversarial CS-351 du document de cartographie prompt LLM. -->

# Risk Matrix

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Medium | Medium | Future documentation and prompt-boundary stories | Medium: may blur validation-owned fields with audit persistence or prompt material | Low | P1 |
| F-002 | Low | Medium | Future provider metadata and privacy reviews | Low: wording only, source code is clear | Low | P2 |
| F-003 | Low | Low | Future guardrail routing for docs and provider handoff | Low: gap is already documented | Medium | P3 |
