# Finding Register

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | observability-gap | theme-astral-prompt-contract | E-001, E-013 | The adversarial audit cannot prove real provider behavior because provider invocation is explicitly out of scope. Builder, gateway, persistence, examples, and tests are coherent, but provider-side interpretation of the payload remains unexercised. | Accept as residual risk for this audit-only run; consider a separate non-production provider smoke/eval story only if product wants provider-level proof. | no |

No Critical, High, Medium, or Low active in-domain implementation finding was found. F-001 is an explicit limitation/observation, not a code correction driver.

## F-001 Provider Runtime Not Invoked

- Severity: Info
- Confidence: High
- Category: observability-gap
- Domain: theme-astral-prompt-contract
- Evidence: E-001, E-013
- Expected rule: The audit must distinguish runtime contract proof from real provider execution proof.
- Actual state: The audit proves builder, gateway, persistence, examples, and scans, but no real LLM provider call is executed.
- Impact: The adversarial audit cannot prove real provider behavior because provider invocation is explicitly out of scope. Builder, gateway, persistence, examples, and tests are coherent, but provider-side interpretation of the payload remains unexercised.
- Recommended action: Accept as residual risk for this audit-only run; consider a separate non-production provider smoke/eval story only if product wants provider-level proof.
- Story candidate: no
- Suggested archetype: observability-audit
