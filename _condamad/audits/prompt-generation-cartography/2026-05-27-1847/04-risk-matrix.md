<!-- Commentaire global: matrice des risques residuels pour l'audit CS-347. -->

# Risk Matrix

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Info | Low | Output validation pipeline | Medium if provider handoff is mistaken for output validity | None | P3 |
| F-002 | Info | Low | Rejected answer workflow | Medium if raw output bypasses controlled rejection | None | P3 |
| F-003 | Info | Low | Observability and replay metadata | Medium if replay metadata is overexposed | None | P3 |
| F-004 | Medium | Medium | Semantic grounding architecture/reporting | Medium if schema-valid output is described as semantically proven | CS-348/CS-350 documentation | P2 |
| F-005 | Info | Medium | CONDAMAD guardrail registry | Low; exact registry enrichment is out of scope | Later authorized guardrail story | P3 |
