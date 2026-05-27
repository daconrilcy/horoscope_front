<!-- Commentaire global: registre des findings de cloture documentaire CS-355. -->

# Finding Register

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | runtime-contract-drift | prompt-generation-document-review | E-005, E-007, E-008, E-014, E-015 | The current CS-350 document still lacks the required wording that `evidence` and `evidence_refs` are validation-owned, excluded from provider prompt material, and may feed audit persistence. | Create a documentation-only correction story for CS-350 wording before final validation. | yes |
| F-002 | High | High | runtime-contract-drift | prompt-generation-document-review | E-005, E-007, E-008, E-014, E-015 | The current CS-350 document still uses ambiguous backend/runtime wording and does not express request, trace and use-case identifiers as provider-only metadata, not prompt-visible payload. | Create a documentation-only correction story for provider metadata wording before final validation. | yes |
| F-003 | High | High | missing-canonical-owner | prompt-generation-document-review | E-006, E-009, E-010, E-011, E-012 | The current CS-350 document has no accepted matrix for Guidance, contextual Guidance, Chat public, Horoscope daily, fallback, repair, bootstrap, admin, test, archival and debt statuses. | Create the CS-350 process-matrix correction using CS-353 SC-001 and CS-354 decisions. | yes |
| F-004 | Medium | High | needs-user-decision | prompt-generation-document-review | E-009, E-010, E-012 | `event_guidance` remains a `chart_json` seed/contract debt surface without an owner decision to migrate, delete or retain as explicit debt. | needs-user-decision: product and architecture owners must decide before final supported/debt wording can close. | needs-user-decision |
| F-005 | Medium | High | needs-user-decision | prompt-generation-document-review | E-009, E-010, E-012 | Admin manual execution is admin-only but provider-capable and can use sample payload contexts; no policy decision is recorded. | needs-user-decision: product, architecture and admin/security owners must classify document/restrict/decommission. | needs-user-decision |
| F-006 | Medium | High | missing-guard | prompt-generation-document-review | E-003, E-010, E-011, E-012 | No exact durable guardrail currently protects the future accepted parallel-process matrix, and CS-354 says this guardrail must wait until the matrix is accepted. | Add a guardrail only after the CS-350 matrix correction becomes durable; do not update the registry in this closure audit. | yes |

## Finding Details

### F-001 Validation And Audit Evidence Wording Still Missing

- Severity: High
- Confidence: High
- Category: runtime-contract-drift
- Domain: prompt-generation-document-review
- Evidence: E-005, E-007, E-008, E-014, E-015.
- Expected rule: CS-351 and CS-352 require CS-350 to state that `evidence` and `evidence_refs` are validation-owned, excluded from provider prompt material, and may be persisted as audit-only anchors.
- Actual state: the targeted scan for `validation-owned` and `audit-only anchors` in CS-350 returned no hit.
- Impact: The current CS-350 document still lacks the required wording that `evidence` and `evidence_refs` are validation-owned, excluded from provider prompt material, and may feed audit persistence.
- Recommended action: Create a documentation-only correction story for CS-350 wording before final validation.
- Story candidate: yes
- Suggested archetype: documentation-correction
- Closure classification: closure-ready through one documentation-only CS-350 correction.

### F-002 Provider Metadata Wording Still Ambiguous

- Severity: High
- Confidence: High
- Category: runtime-contract-drift
- Domain: prompt-generation-document-review
- Evidence: E-005, E-007, E-008, E-014, E-015.
- Expected rule: CS-351 and CS-352 require `runtime/provider-only metadata, not prompt-visible payload` wording for request, trace and use-case identifiers.
- Actual state: the current document contains provider/runtime wording in one section but does not contain the exact accepted correction wording, and the older `backend-only runtime` line is still present.
- Impact: The current CS-350 document still uses ambiguous backend/runtime wording and does not express request, trace and use-case identifiers as provider-only metadata, not prompt-visible payload.
- Recommended action: Create a documentation-only correction story for provider metadata wording before final validation.
- Story candidate: yes
- Suggested archetype: documentation-correction
- Closure classification: closure-ready through one documentation-only CS-350 correction.

### F-003 Parallel Process Matrix Still Absent From CS-350

- Severity: High
- Confidence: High
- Category: missing-canonical-owner
- Domain: prompt-generation-document-review
- Evidence: E-006, E-009, E-010, E-011, E-012.
- Expected rule: CS-353 and CS-354 require an accepted process matrix covering active non-natal provider-capable flows and bounded non-nominal, recovery, bootstrap, admin, test, archival and debt contexts.
- Actual state: the targeted scan over CS-350 finds no matrix heading or required process terms.
- Impact: The current CS-350 document has no accepted matrix for Guidance, contextual Guidance, Chat public, Horoscope daily, fallback, repair, bootstrap, admin, test, archival and debt statuses.
- Recommended action: Create the CS-350 process-matrix correction using CS-353 SC-001 and CS-354 decisions.
- Story candidate: yes
- Suggested archetype: documentation-correction
- Closure classification: closure-ready if the correction preserves blockers instead of implying product support.

### F-004 `event_guidance` Decision Blocks Full Closure

- Severity: Medium
- Confidence: High
- Category: needs-user-decision
- Domain: prompt-generation-document-review
- Evidence: E-009, E-010, E-012.
- Expected rule: CS-354 requires a product/architecture decision to migrate, delete or retain `event_guidance` as explicit debt.
- Actual state: no owner decision is recorded in the source set.
- Impact: `event_guidance` remains a `chart_json` seed/contract debt surface without an owner decision to migrate, delete or retain as explicit debt.
- Recommended action: needs-user-decision: product and architecture owners must decide before final supported/debt wording can close.
- Story candidate: needs-user-decision
- Suggested archetype: legacy-surface-decision
- Closure classification: blocked.

### F-005 Admin Manual Execution Policy Blocks Full Closure

- Severity: Medium
- Confidence: High
- Category: needs-user-decision
- Domain: prompt-generation-document-review
- Evidence: E-009, E-010, E-012.
- Expected rule: CS-354 requires owner classification for admin manual execution as documented admin-only provider-capable, restricted, or decommissioned.
- Actual state: no owner decision is recorded in the source set.
- Impact: Admin manual execution is admin-only but provider-capable and can use sample payload contexts; no policy decision is recorded.
- Recommended action: needs-user-decision: product, architecture and admin/security owners must classify document/restrict/decommission.
- Story candidate: needs-user-decision
- Suggested archetype: admin-policy-classification
- Closure classification: blocked.

### F-006 Exact Guardrail Must Follow Accepted Matrix

- Severity: Medium
- Confidence: High
- Category: missing-guard
- Domain: prompt-generation-document-review
- Evidence: E-003, E-010, E-011, E-012.
- Expected rule: CS-353 SC-002 and CS-354 sequence the exact guardrail after the CS-350 matrix is accepted.
- Actual state: no accepted matrix exists yet, so updating `_condamad/stories/regression-guardrails.md` now would freeze an invariant before its source artifact exists.
- Impact: No exact durable guardrail currently protects the future accepted parallel-process matrix, and CS-354 says this guardrail must wait until the matrix is accepted.
- Recommended action: Add a guardrail only after the CS-350 matrix correction becomes durable; do not update the registry in this closure audit.
- Story candidate: yes
- Suggested archetype: governance-guardrail-hardening
- Closure classification: phased-with-map, dependent on F-003 closure.
