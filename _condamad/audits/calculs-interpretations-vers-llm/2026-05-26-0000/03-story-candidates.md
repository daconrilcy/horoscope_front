# Story Candidates - Calculs Interpretations Vers LLM

## SC-001

- Candidate ID: SC-001
- Source finding: F-001
- Suggested story title: Converger l'entree LLM natale vers un contrat narratif canonique
- Suggested archetype: `service-boundary-refactor`
- Primary domain: backend astrology LLM input
- Required contracts: Runtime Source of Truth, Contract Shape, Ownership Routing, Reintroduction Guard, No Legacy
- Draft objective: make the natal LLM input consume one explicit canonical narrative/factual owner, likely `AINarrativeInputContract` or a derived LLM-specific DTO, without exposing raw `ChartObjectRuntimeData`.
- Closure intent: `phased-with-map`
- Must include: choose owner (`AINarrativeInputContract` vs `structured_facts_v1` vs dedicated DTO), map every `NatalExecutionInput` field, preserve existing prompt/runtime behavior where required by tests, and document compatibility fields.
- Validation hints: targeted tests for natal interpretation service, gateway input contract tests, zero-hit scan proving no direct raw runtime payload in prompt/provider layers, and scans for `structured_facts_v1|AINarrativeInputBuilder|ChartInterpretationInputBuilder` in the chosen service path.
- Blockers: user/architecture decision required if the canonical LLM input owner is not `AINarrativeInputContract`.

### Exhaustive Files To Modify

- Application files: exact selection rule only; likely `backend/app/services/llm_generation/natal/interpretation_service.py`, selected contract/adapter file under `backend/app/domain/llm/runtime/**`, and selected owner under `backend/app/domain/astrology/interpretation/**` only if existing contract is insufficient.
- Governance/test files: natal interpretation service tests, LLM runtime contract tests, architecture guard for no raw runtime prompt exposure.
- Before evidence: E-008, E-009, E-010, E-011, E-013, E-016.
- After evidence required: one canonical owner is invoked in the natal LLM path; `NatalExecutionInput` field map is documented; raw `ChartObjectRuntimeData` still absent from provider/public payloads.
- Ownership routing decisions: runtime facts stay under `backend/app/domain/astrology/runtime/**`; interpretation/narrative facts stay under `backend/app/domain/astrology/interpretation/**`; LLM adapter stays under `backend/app/domain/llm/**` or service orchestration.
- Mandatory no-wildcard allowlist and No Legacy checks: no broad folder allowlist, no fallback prompt path, no duplicated builder, no hidden second projection.
- Reintroduction guard requirements: exact scans for raw runtime classes in provider/prompt layers and exact positive scan for chosen owner in natal LLM assembly.
- Stop condition: finding closes when current LLM path uses the chosen canonical owner or the user explicitly rejects convergence and records compatibility as intentional.

## SC-002

- Candidate ID: SC-002
- Source finding: F-002
- Suggested story title: Documenter et reduire la duplication `chart_json` / `natal_data` dans l'entree LLM natale
- Suggested archetype: `duplicate-rule-removal`
- Primary domain: backend LLM runtime contract
- Required contracts: Contract Shape, Ownership Routing, No Legacy, Reintroduction Guard
- Draft objective: ensure `chart_json` and `natal_data` are either deliberately compatibility aliases or replaced by one factual payload after SC-001.
- Closure intent: `full-closure`
- Must include: before/after field map for `NatalExecutionInput`, compatibility decision for existing gateway/prompt consumers, and no silent fallback.
- Validation hints: gateway input tests, natal service tests, prompt context rendering tests, targeted scan for both fields in adapter/gateway/prompt contexts.
- Blockers: blocked if external LLM prompt contracts require both fields without a migration decision.

### Exhaustive Files To Modify

- Application files: exact selection rule only; `backend/app/domain/llm/runtime/contracts.py`, `backend/app/domain/llm/runtime/adapter.py`, `backend/app/domain/llm/runtime/gateway.py`, `backend/app/services/llm_generation/natal/interpretation_service.py`, selected prompt context code if field use changes.
- Governance/test files: contract and gateway tests; no broad allowlist.
- Before evidence: E-012, E-013, E-014.
- After evidence required: either one canonical factual field remains, or compatibility status is explicit and guarded.
- Ownership routing decisions: public chart projection remains in `json_builder.py`; LLM factual input owner must be explicit.
- Mandatory no-wildcard allowlist and No Legacy checks: no new `*_legacy` field, no duplicate alias without expiry/decision.
- Reintroduction guard requirements: scan that no third chart-facts field was introduced without contract update.
- Stop condition: closes when duplication is removed or explicitly classified as intentional compatibility with tests.

## SC-003

- Candidate ID: SC-003
- Source finding: F-003
- Suggested story title: Aligner le catalogue d'evidence LLM avec la source factuelle canonique
- Suggested archetype: `contract-shape-audit`
- Primary domain: backend astrology LLM evidence
- Required contracts: Runtime Source of Truth, Contract Shape, Ownership Routing, Reintroduction Guard
- Draft objective: define whether LLM evidence labels/hash references are derived from `structured_facts_v1`, `AINarrativeInputContract`, or a dedicated evidence DTO.
- Closure intent: `phased-with-map`
- Must include: evidence ID ownership, compatibility with output validation, hash/provenance policy, and exact missing-data behavior.
- Validation hints: output validator tests, rejected/narrative answer audit tests, projection hash tests, scans for evidence catalog construction.
- Blockers: should follow SC-001 owner decision.

### Exhaustive Files To Modify

- Application files: exact selection rule only; `backend/app/services/chart/json_builder.py` only if legacy catalog remains, selected interpretation/LLM evidence owner if new catalog is introduced, `backend/app/domain/llm/**` validator/context files if evidence shape changes.
- Governance/test files: output validation tests, audit evidence refs tests, architecture guard for no raw runtime evidence IDs.
- Before evidence: E-010, E-012, E-013.
- After evidence required: evidence catalog source matches chosen canonical LLM input source and tests prove references validate.
- Ownership routing decisions: evidence source cannot be owned by prompt text; it must be domain interpretation or LLM contract code.
- Mandatory no-wildcard allowlist and No Legacy checks: no fallback to public `chart_json` when canonical evidence source is unavailable unless explicitly tested as compatibility.
- Reintroduction guard requirements: positive scan for chosen evidence owner and negative scan for raw runtime class names in public/provider payload.
- Stop condition: closes when evidence catalog ownership is explicit and validated against current output validators.

## Deferred Non-Domain Context

- Prompt wording, provider selection, frontend rendering, public API contract shape, auth/security, CI, DB and migrations are deferred non-domain concerns.
- No candidate should edit `frontend/**`, `backend/tests/**` only for unrelated cleanup, prompt files, or runtime calculators unless the chosen implementation evidence proves a direct need.
