<!-- Commentaire global: matrice des risques residuels pour l'audit CS-346. -->

# Risk Matrix

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Info | Low | Natal LLM input source map | Low; builders are centralized and tested | None | P3 |
| F-002 | Info | Low | Gateway prompt payload | Low; canonical role contract is reused by gateway/tests | None | P3 |
| F-003 | Info | Low | Modern natal prompt carrier boundary | Medium if integration guards are not run with `--long` | None | P3 |
| F-004 | Info | Low | Audit hashes and evidence refs | Low; unit tests cover current policy | None | P3 |
