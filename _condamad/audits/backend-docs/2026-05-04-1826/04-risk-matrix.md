# Risk Matrix - backend-docs

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Medium | High | All future backend documentation and generated artifacts | Medium: new files can silently extend the catch-all pattern | Low | P1 |
| F-002 | Medium | Medium | Entitlement ops, security docs, route/table expectations | Medium: canonical-looking prose can drift from runtime behavior | Medium | P1 |
| F-003 | Medium | Medium | LLM runtime, DB cleanup, prompt/aggregate governance | Medium: uneven governance can leave source-of-truth prose stale | Medium | P2 |
| F-004 | Medium | High | Calibration reviews and generated percentile evidence | Low: stale artifact mainly misleads reviewers unless consumed manually | Low | P1 |
| F-005 | Info | Low | LLM DB cleanup governance | Low: existing validator protects the registry | Low | monitor |

## Top Risks

1. `F-001` keeps the folder ambiguous: without a classification index, cleanup work can accidentally move or edit executable governance data as if it were passive documentation.
2. `F-004` is the cleanest immediate win because the current code path and the existing artifact location visibly disagree.
3. `F-002` has higher product/security sensitivity than the file-system symptom suggests; if the entitlement document remains canonical, it needs parity checks.
