<!-- Commentaire global: propositions de stories issues de l'audit CS-353 des processus paralleles LLM. -->

# Story Candidates

## SC-001 Document Parallel Provider-Capable Prompt Processes

- Source finding: F-001
- Suggested story title: Document parallel provider-capable prompt-generation processes in CS-350
- Suggested archetype: documentation-correction
- Primary domain: prompt-generation-document-review
- Required contracts: Runtime Source of Truth, Ownership Routing, Contract Shape, Reintroduction Guard, Persistent Evidence
- Draft objective: Amend `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` with a concise process matrix for guidance, contextual guidance, public chat, daily horoscope, fallback, repair, bootstrap, admin samples and carriers.
- Closure intent: full-closure
- Must include: exact process rows with `process`, `status`, `trigger`, `owner`, `configuration source`, `prompt-visible input`, `renderer or assembly`, `provider handoff`, `modern natal boundary`, and `risk if ignored`.
- Validation hints: run targeted `rg` checks for `Guidance`, `Chat public`, `Horoscope daily`, `fallback catalog`, `repair prompts`, `chart_json`, `natal_data`, and source-doc headings; run carrier guard tests if backend venv is available.
- Blockers: stop if product wording would imply runtime behavior changes or if admin manual execution policy is unresolved.

### Exhaustive Files To Modify

- Application files: none.
- Governance/test files: none unless SC-002 is accepted in the same story.
- Documentation files: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`.
- Before evidence: CS-353 report plus targeted source scans E-011 to E-018.
- After evidence: source-doc matrix scan and unchanged `backend/app`, `backend/tests`, `frontend/src`, migrations.
- Ownership routing decisions expected: keep the canonical CS-350 document as the only final cartography document; do not create a second canonical doc.
- Mandatory no-wildcard allowlist and No Legacy checks: no broad allowlist; scan for vague "legacy process" wording without process rows.
- Reintroduction guard requirements: reference RG-017 to RG-022 and include a candidate invariant for exact parallel-process classification.
- Stop condition: every process in `03-parallel-legacy-processes-audit.md` has a corresponding documented classification or an explicit accepted residual risk.
- File/surface classification changes expected after implementation: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` remains `used`; no runtime file changes.

## SC-002 Add Exact Guardrail For Parallel Prompt Process Classification

- Source finding: F-004
- Suggested story title: Add guardrail for parallel legacy prompt process classification
- Suggested archetype: governance-guardrail-hardening
- Primary domain: prompt-generation-document-review
- Required contracts: Reintroduction Guard, Persistent Evidence, Ownership Routing
- Draft objective: Add a durable regression guardrail only after SC-001 establishes the accepted matrix, so future prompt-generation stories keep provider-capable, recovery, bootstrap, admin, test and archival paths distinct.
- Closure intent: full-closure
- Must include: one exact guardrail row in `_condamad/stories/regression-guardrails.md` naming the CS-350 matrix or accepted successor artifact, plus scans that prove guidance/chat/horoscope/fallback/repair/carrier terms remain classified.
- Validation hints: run `rg -n "Guidance|Chat public|Horoscope daily|fallback catalog|repair prompts|chart_json|natal_data" _condamad/docs _condamad/stories/regression-guardrails.md`.
- Blockers: do not add this guardrail before SC-001 or an equivalent documentation decision defines the durable invariant.

### Exhaustive Files To Modify

- Application files: none.
- Governance/test files: `_condamad/stories/regression-guardrails.md`.
- Documentation files: none unless bundled with SC-001.
- Before evidence: RG-017 to RG-022 scan and CS-353 F-004.
- After evidence: exact new guardrail row and targeted scans.
- Ownership routing decisions expected: guardrail registry remains the only durable invariant registry.
- Mandatory no-wildcard allowlist and No Legacy checks: guardrail must name exact surfaces, not broad `backend/app/**` wildcards.
- Reintroduction guard requirements: guard future stories against collapsing provider-capable, recovery, bootstrap, admin, test and archival statuses.
- Stop condition: registry includes one exact invariant and targeted scans show the accepted matrix terms.
- File/surface classification changes expected after implementation: `_condamad/stories/regression-guardrails.md` remains `used`; no runtime file changes.

## Deferred Non-Domain Or Decision Items

- F-002 requires a user/product decision before a remediation story: migrate, delete, or retain `event_guidance` as explicitly classified debt.
- F-003 requires admin LLM execution policy classification before implementation: document as admin-only provider-capable, restrict/decommission, or create a dedicated admin execution policy story.
- F-005 has no story candidate; cite existing tests and audits.

