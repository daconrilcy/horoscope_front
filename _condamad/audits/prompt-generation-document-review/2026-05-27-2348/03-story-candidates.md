<!-- Commentaire global: propositions de stories issues de l'audit de cloture documentaire CS-355. -->

# Story Candidates

## SC-001 Correct CS-350 Validation Evidence Wording

- Source finding: F-001
- Suggested story title: Corriger le wording evidence/evidence_refs dans la cartographie prompt LLM
- Suggested archetype: documentation-correction
- Primary domain: prompt-generation-document-review
- Required contracts: Runtime Source of Truth, Ownership Routing, Contract Shape, Reintroduction Guard, Persistent Evidence
- Draft objective: Update `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` only, so it states that `evidence` and `evidence_refs` are validation-owned, excluded from provider prompt material, and may feed audit persistence.
- Closure intent: full-closure
- Must include: exact wording from CS-351 and CS-352, no runtime/provider behavior claim beyond source evidence, no app code edits.
- Validation hints: `rg -n "validation-owned|audit-only anchors|evidence_refs" _condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`; bounded `git status` over app/test/frontend/migration surfaces.
- Blockers: none if wording remains documentation-only.

### Exhaustive Files To Modify

- Application files: none.
- Governance/test files: none.
- Documentation files: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`.
- Before evidence artifacts required: CS-351 F-001/F-002, CS-352 F-001/F-002, current CS-350 scan.
- After evidence artifacts required: exact wording scan and bounded status scan proving no app code changed.
- Ownership routing decisions expected: CS-350 remains the single final cartography document.
- Mandatory no-wildcard allowlist and No Legacy checks: no allowlist; no compatibility prompt/provider path; no fallback wording that promotes audit-only fields into prompt-visible payload.
- Reintroduction guard requirements: if bundled with SC-003 later, exact guardrail must cite the accepted CS-350 wording.
- Stop condition: stop if proposed wording implies new provider calls, runtime behavior, or semantic correctness proof.
- File/surface classification changes expected after implementation: CS-350 remains `used`.

## SC-002 Correct CS-350 Provider Metadata Wording

- Source finding: F-002
- Suggested story title: Corriger le wording provider metadata dans la cartographie prompt LLM
- Suggested archetype: documentation-correction
- Primary domain: prompt-generation-document-review
- Required contracts: Runtime Source of Truth, Ownership Routing, Contract Shape, Reintroduction Guard, Persistent Evidence
- Draft objective: Update `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` only, so request, trace and use-case identifiers are stated as runtime/provider-only metadata, not prompt-visible payload.
- Closure intent: full-closure
- Must include: exact wording from CS-351 and CS-352, no runtime/provider behavior change, no app code edits.
- Validation hints: `rg -n "runtime/provider-only metadata|not prompt-visible payload|request_id|trace_id|use_case" _condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`; bounded `git status` over app/test/frontend/migration surfaces.
- Blockers: none if wording remains documentation-only.

### Exhaustive Files To Modify

- Application files: none.
- Governance/test files: none.
- Documentation files: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`.
- Before evidence artifacts required: CS-351 F-002, CS-352 F-002, current CS-350 scan.
- After evidence artifacts required: exact wording scan and bounded status scan proving no app code changed.
- Ownership routing decisions expected: CS-350 remains the single final cartography document.
- Mandatory no-wildcard allowlist and No Legacy checks: no allowlist; no compatibility prompt/provider path.
- Reintroduction guard requirements: if bundled with SC-004 later, exact guardrail must cite the accepted CS-350 wording.
- Stop condition: stop if proposed wording implies new provider calls, runtime behavior, or semantic correctness proof.
- File/surface classification changes expected after implementation: CS-350 remains `used`.

## SC-003 Add Accepted Parallel Process Matrix To CS-350

- Source finding: F-003
- Suggested story title: Ajouter la matrice des processus paralleles provider-capable dans CS-350
- Suggested archetype: documentation-correction
- Primary domain: prompt-generation-document-review
- Required contracts: Runtime Source of Truth, Ownership Routing, Contract Shape, Reintroduction Guard, Persistent Evidence
- Draft objective: Amend CS-350 with the process taxonomy and matrix accepted by CS-353 and CS-354, covering nominal, parallel, fallback, repair, bootstrap, test, admin, archival and debt contexts.
- Closure intent: full-closure for F-003 if blockers remain explicitly named instead of softened.
- Must include: rows for Guidance, Guidance contextuelle, Chat public, Horoscope daily narration, fallback catalog/no-assembly/provider fallback, repair prompts, guidance seeds, horoscope narrator seed, admin sample payloads, admin manual execution, carrier tests, historical/admin/test `chart_json`, CS-350 archive mentions and `event_guidance`.
- Validation hints: `rg -n "Guidance|Guidance contextuelle|Chat public|Horoscope daily|fallback|repair|bootstrap|admin|event_guidance|provider-capable" _condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`; bounded app status scan.
- Blockers: `event_guidance` and admin manual execution decisions must remain blockers unless owner decisions are supplied.

### Exhaustive Files To Modify

- Application files: none.
- Governance/test files: none; the guardrail follow-up belongs to SC-004 after the matrix is accepted.
- Documentation files: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`.
- Before evidence artifacts required: CS-353 process audit, CS-353 story candidates, CS-354 architecture report.
- After evidence artifacts required: process-term scan, blocker-term scan and bounded status scan.
- Ownership routing decisions expected: one canonical matrix in CS-350; no second canonical cartography document.
- Mandatory no-wildcard allowlist and No Legacy checks: no broad allowlist; no wording that promotes legacy carriers to modern natal prompt-visible inputs.
- Reintroduction guard requirements: candidate exact guardrail after acceptance.
- Stop condition: every CS-353 process has a row or explicit blocking/accepted residual risk decision.
- File/surface classification changes expected after implementation: CS-350 remains `used`.

## SC-004 Add Exact Guardrail For Accepted Prompt-Process Classification

- Source finding: F-006
- Suggested story title: Ajouter le guardrail exact de classification des processus prompt LLM
- Suggested archetype: governance-guardrail-hardening
- Primary domain: prompt-generation-document-review
- Required contracts: Reintroduction Guard, Persistent Evidence, Ownership Routing
- Draft objective: After SC-003 or an equivalent accepted matrix exists, add one exact invariant to `_condamad/stories/regression-guardrails.md` protecting provider-capable, fallback, repair, bootstrap, admin, test, archival and debt classifications.
- Closure intent: full-closure after matrix acceptance.
- Must include: exact CS-350 matrix surface, exact scan terms, no broad folder allowlist.
- Validation hints: `rg -n "Guidance|Chat public|Horoscope daily|fallback|repair|bootstrap|admin|event_guidance|provider-capable" _condamad/docs/prompt-generation-cartography _condamad/stories/regression-guardrails.md`.
- Blockers: blocked until the CS-350 process matrix is accepted as durable.

### Exhaustive Files To Modify

- Application files: none.
- Governance/test files: `_condamad/stories/regression-guardrails.md`.
- Documentation files: none unless combined after SC-003.
- Before evidence artifacts required: accepted CS-350 matrix, CS-353 F-004 and CS-353 SC-002.
- After evidence artifacts required: exact new guardrail row and targeted scans.
- Ownership routing decisions expected: guardrail registry remains the only durable invariant registry.
- Mandatory no-wildcard allowlist and No Legacy checks: no wildcard allowlist; exact surface and terms only.
- Reintroduction guard requirements: the guard itself is the reintroduction guard.
- Stop condition: no accepted matrix exists or the proposed invariant cannot name exact terms.
- File/surface classification changes expected after implementation: regression guardrails remain `used`.

## Deferred Non-Domain Or Decision Items

- F-004 is blocked by product/architecture decision: migrate, delete or retain `event_guidance` as explicit debt.
- F-005 is blocked by product/architecture/admin-security decision: document admin manual execution as admin-only provider-capable, restrict it, or decommission it.
- Broader CS-348 output schema and semantic grounding blockers remain deferred architecture context and do not change this documentary closure verdict.
