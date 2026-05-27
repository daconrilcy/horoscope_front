<!-- Commentaire global: candidats de stories issus de l'audit CS-352 de concordance code-document prompt LLM. -->

# Story Candidates

## SC-001 clarify validation-owned audit evidence wording

- Source finding: F-001
- Suggested story title: Clarifier les roles validation et audit de `evidence_refs` dans la cartographie prompt LLM
- Suggested archetype: documentation-correction
- Primary domain: condamad-audit-documentation
- Required contracts: Ownership Routing, Contract Shape, Reintroduction Guard, Persistent Evidence
- Draft objective: Update only `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` so it states that `evidence` and `evidence_refs` are validation-owned, excluded from provider prompt material, and may feed audit persistence.
- Closure intent: `full-closure`
- Must include: preserve prompt-visible blocks `facts`, `signals`, `limits`, `shaping`; preserve validation-only/audit-only separation; do not edit backend, tests, migrations or frontend; cite CS-352 audit evidence.
- Validation hints: `rg -n "evidence_refs|validation-owned|audit-only|prompt-visible" _condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`; run the listed payload boundary tests if documentation wording changes validation paths.
- Blockers: stop if the correction requires redefining runtime semantics or adding new prompt-visible fields.

### Exhaustive Files To Modify

- Documentation files: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`.
- Application files: none.
- Governance/test files: none.

### Closure Evidence Required

- Before/after diff proving only the documentation wording changed.
- Targeted scan showing `evidence_refs` is still not described as provider prompt material.
- No-wildcard No Legacy scan for `chart_json`, `natal_data`, `evidence`, `provenance`, `projection_hash`, `llm_input_hash` in the changed section.

## SC-002 clarify provider-only metadata wording

- Source finding: F-002
- Suggested story title: Clarifier les metadonnees runtime/provider dans la cartographie prompt LLM
- Suggested archetype: documentation-correction
- Primary domain: condamad-audit-documentation
- Required contracts: Ownership Routing, Contract Shape, Reintroduction Guard, Persistent Evidence
- Draft objective: Update only `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` so `request_id`, `trace_id` and `use_case` are described as runtime/provider-only metadata and explicitly not prompt-visible payload.
- Closure intent: `full-closure`
- Must include: preserve the source-backed fact that `_call_provider` passes these fields to provider runtime; do not imply they are prompt-visible user payload; do not edit provider code.
- Validation hints: `rg -n "runtime/provider-only|request_id|trace_id|use_case|not prompt-visible" _condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`; `rg -n "request_id|trace_id|use_case|x-request-id|x-trace-id" backend/app/domain/llm/runtime/gateway.py backend/app/infra/providers/llm/openai_responses_client.py`.
- Blockers: stop if a product/security decision is required about whether these headers should be sent externally.

### Exhaustive Files To Modify

- Documentation files: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`.
- Application files: none.
- Governance/test files: none.

### Closure Evidence Required

- Before/after diff proving only the documentation wording changed.
- Targeted scan showing `backend-only runtime` is no longer used for provider-bound request/trace/use-case metadata.
- No runtime behavior diff in `backend/app/**`.

## Deferred Non-Domain Context

- F-003 does not receive an implementation story candidate in this audit because it is a governance coverage observation. A future dedicated story may create an exact documentation-concordance guardrail if the user wants durable automation.
