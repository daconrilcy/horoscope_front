<!-- Commentaire global: registre des constats CS-360 pour la surface admin manual execution. -->

# Finding Register - CS-360 Admin Manual Execution

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | policy-implementation-gap | admin-manual-llm-execution | E-004, E-005, E-007, E-009, E-015 | The route is intentionally admin-only and provider-capable, and this audit selects `migrate`; however, the selected policy is not yet encoded in runtime behavior, audit metadata, documentation, or guards. Future agents can otherwise document or change it inconsistently. | Implement the selected `migrate` policy: keep admin-only manual execution, but migrate sample payload carriers away from natal `chart_json` before treating it as a supported admin surface. | yes |
| F-002 | High | High | legacy-surface | admin-manual-llm-execution | E-004, E-007, E-010, E-011, E-015 | Natal admin samples require `chart_json`, and manual execution copies the sample payload into `ExecutionContext.extra_context`; therefore a legacy carrier can be prompt material for live provider execution in this admin path. | Migrate natal admin sample payloads and templates to an explicit non-legacy prompt-visible carrier; keep compatibility blocked or explicitly transitional until all samples/templates are converted. | yes |
| F-003 | Medium | High | observability-gap | admin-manual-llm-execution | E-013, E-015 | Logs and audit events exist for start/success/failure, but the policy classification is not persisted in the audit details; future analysis must infer whether a call was `migrate`, `restricted`, `supported`, or `decommissioned`. | Add policy/status metadata to admin manual execution audit details once the policy is implemented. | yes |
| F-004 | Medium | Medium | missing-guard | admin-manual-llm-execution | E-003, E-006, E-007, E-014, E-017 | There is coverage for admin denial and current route behavior, but no exact guardrail prevents future promotion of execute-sample outside admin-only provider-capable classification. | Add a precise regression guard after the migration/restriction policy lands; it should scan route ownership, admin dependency, frontend-only admin caller, and `chart_json` carrier absence where applicable. | yes |

## Finding Details

### F-001 - Policy Not Closed For Provider-Capable Admin Execution

- Severity: High
- Confidence: High
- Category: policy-implementation-gap
- Domain: admin-manual-llm-execution
- Evidence: E-004, E-005, E-007, E-009, E-015
- Expected rule: a provider-capable admin execution surface must have one durable policy: document, restrict, migrate, or decommission.
- Actual state: source and tests prove a live execution path; this audit resolves the CS-353/CS-350 policy gap by selecting `migrate`, but the selected policy is not yet implemented in runtime behavior, audit metadata, documentation, or guards.
- Impact: The route is intentionally admin-only and provider-capable, and this audit selects `migrate`; however, the selected policy is not yet encoded in runtime behavior, audit metadata, documentation, or guards. Future agents can otherwise document or change it inconsistently.
- Recommended action: Implement the selected `migrate` policy: keep admin-only manual execution, but migrate sample payload carriers away from natal `chart_json` before treating it as a supported admin surface.
- Story candidate: yes
- Suggested archetype: no-legacy-policy-migration

### F-002 - Natal Sample Payloads Still Require `chart_json`

- Severity: High
- Confidence: High
- Category: legacy-surface
- Domain: admin-manual-llm-execution
- Evidence: E-004, E-007, E-010, E-011, E-015
- Expected rule: legacy carriers must not remain implicit prompt material for provider-capable execution.
- Actual state: `feature == "natal"` sample payload validation requires `chart_json`; manual execution copies the sample payload into gateway execution context.
- Impact: Natal admin samples require `chart_json`, and manual execution copies the sample payload into `ExecutionContext.extra_context`; therefore a legacy carrier can be prompt material for live provider execution in this admin path.
- Recommended action: Migrate natal admin sample payloads and templates to an explicit non-legacy prompt-visible carrier; keep compatibility blocked or explicitly transitional until all samples/templates are converted.
- Story candidate: yes
- Suggested archetype: legacy-carrier-migration

### F-003 - Policy Status Missing From Execution Audit Details

- Severity: Medium
- Confidence: High
- Category: observability-gap
- Domain: admin-manual-llm-execution
- Evidence: E-013, E-015
- Expected rule: operational audit events should carry enough classification to distinguish manual execution policy status without rediscovering source context.
- Actual state: audit details include execution surface, manifest entry, sample id and gateway metadata, but not the policy classification.
- Impact: Logs and audit events exist for start/success/failure, but the policy classification is not persisted in the audit details; future analysis must infer whether a call was `migrate`, `restricted`, `supported`, or `decommissioned`.
- Recommended action: Add policy/status metadata to admin manual execution audit details once the policy is implemented.
- Story candidate: yes
- Suggested archetype: observability-guard-hardening

### F-004 - No Exact Anti-Promotion Guard

- Severity: Medium
- Confidence: Medium
- Category: missing-guard
- Domain: admin-manual-llm-execution
- Evidence: E-003, E-006, E-007, E-014, E-017
- Expected rule: admin-only provider-capable surfaces should have a deterministic guard preventing accidental public promotion or carrier regression.
- Actual state: RG-149 gives a broad documentation invariant; no exact CS-360 guard exists for `execute-sample` route ownership, admin dependency, caller scope and migrated carrier policy.
- Impact: There is coverage for admin denial and current route behavior, but no exact guardrail prevents future promotion of execute-sample outside admin-only provider-capable classification.
- Recommended action: Add a precise regression guard after the migration/restriction policy lands; it should scan route ownership, admin dependency, frontend-only admin caller, and `chart_json` carrier absence where applicable.
- Story candidate: yes
- Suggested archetype: architecture-guard-hardening
