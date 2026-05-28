<!-- Commentaire global: matrice de risques pour l'audit CS-360 admin manual execution. -->

# Risk Matrix - CS-360 Admin Manual Execution

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | Medium | Admin LLM execution policy implementation | Inconsistent documentation or behavior change before migration lands | Medium | P1 |
| F-002 | High | High | Admin live provider execution | Legacy `chart_json` remains prompt material | Medium | P1 |
| F-003 | Medium | Medium | Audit trail interpretation | Execution audit lacks policy status | Low | P2 |
| F-004 | Medium | Medium | Route/caller/carrier guardrails | Public promotion or carrier regression not caught exactly | Low | P2 |

## Risk Notes

- Security posture is currently bounded by `require_admin_user` and tested 401/403 denial evidence.
- Provider cost/side-effect risk exists by design because `execute-sample` calls `LLMGateway.execute_request`.
- The highest No Legacy risk is `chart_json` in natal admin samples, not sample payload CRUD by itself.
