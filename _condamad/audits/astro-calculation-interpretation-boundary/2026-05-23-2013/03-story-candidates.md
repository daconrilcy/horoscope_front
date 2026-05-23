# Story Candidates - Astro Calculation Interpretation Boundary

## Candidate Summary

| Candidate ID | Priority | Source finding | Suggested story title | Closure intent | Primary domain |
|---|---|---|---|---|---|
| SC-001 / CS-252 | P1 | F-001 | Define ChartInterpretationInput public/internal contract | full-closure | `backend/app/domain/astrology/interpretation` |
| SC-002 / CS-253 | P2 | F-002 | Add interpretation-readiness projection from structural facts | full-closure | `backend/app/domain/astrology/interpretation` |
| SC-003 / CS-254 | P2 | F-003 | Guard against narrative tokens in calculation runtime | full-closure | `backend/tests/architecture` and structural runtime roots |

## SC-001 CS-252 Define ChartInterpretationInput Public Internal Contract

- Candidate ID: CS-252
- Source finding: F-001
- Suggested story title: Define ChartInterpretationInput public/internal contract
- Suggested archetype: contract-shape / boundary-guard hardening
- Primary domain: `backend/app/domain/astrology/interpretation`
- Required contracts: Runtime Source of Truth, Ownership Routing, Contract Shape, Reintroduction Guard, Persistent Evidence.
- Draft objective: define which `ChartInterpretationInputRuntimeData` fields are internal-only, which may feed a future public projection, and which form the stable contrat LLM for natal interpretation.
- Closure intent: full-closure
- Must include: contrat interne, contrat public and contrat LLM sections; exact allowed fields; no raw `ChartObjectRuntimeData` public exposure; no prompt/provider dependency in astrology domain.
- Validation hints: `pytest -q backend/tests/architecture/test_chart_interpretation_input_boundary.py`; `pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py`; targeted `rg -n "ChartInterpretationInputRuntimeData|contrat interne|contrat public|contrat LLM" backend docs _condamad`.
- Blockers: stop if product asks to expose raw `ChartInterpretationInputRuntimeData` publicly instead of a reduced public projection.

### Exhaustive Files To Modify

- Application files: exact selection rule is only files that define or document `ChartInterpretationInputRuntimeData` contract boundaries; likely `backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py`, optional docs under `docs/architecture/**`.
- Governance/test files: `backend/tests/architecture/test_chart_interpretation_input_boundary.py` and targeted unit tests if contract shape changes.
- Files to delete: none.
- Before evidence: E-008, E-009, E-014 from this audit plus current field inventory.
- After evidence: contract table proving each field is internal/public/LLM, tests passing, and negative scan showing no public raw runtime exposure.
- Required no-wildcard allowlist and No Legacy checks: no broad folder exception; no alias, shim, fallback, or duplicate public contract.
- Stop condition: every field in `ChartInterpretationInputRuntimeData` has an owner decision and future public exposure is limited to named projection fields.

## SC-002 CS-253 Add Interpretation Readiness Projection From Structural Facts

- Candidate ID: CS-253
- Source finding: F-002
- Suggested story title: Add interpretation-readiness projection from structural facts
- Suggested archetype: ownership-routing refactor / contract-shape
- Primary domain: `backend/app/domain/astrology/interpretation`
- Required contracts: Runtime Source of Truth, Ownership Routing, Contract Shape, Reintroduction Guard, Persistent Evidence.
- Draft objective: add a compact deterministic projection that tells downstream product and LLM code which structural facts are ready for interpretation, without exposing raw runtime payloads or invoking LLM/prompt logic.
- Closure intent: full-closure
- Must include: exact projection owner, source structural facts, readiness states, absent/withheld reasons, no provider dependency, no public raw `chart_objects`.
- Validation hints: `pytest -q backend/tests/architecture/test_chart_interpretation_input_boundary.py`; unit tests for readiness projection; targeted scan `rg -n "OpenAI|AIEngineAdapter|PromptRenderer|developer_prompt" backend/app/domain/astrology -g "*.py"`.
- Blockers: stop if readiness semantics require product policy not derivable from structural facts.

### Exhaustive Files To Modify

- Application files: exact selection rule is a new or existing interpretation-domain projection owner plus its builder/test consumers; no calculator, prompt, provider, API router, migration or frontend file.
- Governance/test files: architecture guard coverage for no LLM/provider dependency and no calculator recomputation.
- Files to delete: none.
- Before evidence: E-006, E-007, E-008, E-011.
- After evidence: projection contract tests, no-provider scan, and proof downstream uses projection instead of raw runtime.
- Required no-wildcard allowlist and No Legacy checks: no fallback from missing readiness to narrative text; no duplicate readiness mapper in services or prompt code.
- Stop condition: all readiness outputs are generated from existing structural facts and every absent value has an explicit reason code.

## SC-003 CS-254 Guard Against Narrative Tokens In Calculation Runtime

- Candidate ID: CS-254
- Source finding: F-003
- Suggested story title: Guard against narrative tokens in calculation runtime
- Suggested archetype: architecture-guard-hardening
- Primary domain: `backend/tests/architecture`
- Required contracts: Reintroduction Guard, No Legacy / DRY, Persistent Evidence.
- Draft objective: extend structural-runtime architecture guards so final-user narrative wording and localized explanatory phrases cannot be introduced into calculation/runtime roots.
- Closure intent: full-closure
- Must include: lexical watchlist for user-facing phrases, French/English narrative verbs where applicable, exact structural roots, exact allowlist for docs/tests only, and scans proving current pass.
- Validation hints: `pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py`; `pytest -q backend/tests/architecture/test_structural_runtime_boundary.py`; targeted `rg -n "Vous avez|Cela signifie|This means|you have|narrative|prompt|LLM" backend/app/domain/astrology -g "*.py"`.
- Blockers: stop if product wants localized labels inside structural runtime; that requires a public/product contract decision first.

### Exhaustive Files To Modify

- Application files: none expected unless a currently hidden offender is discovered; if discovered, stop and route as separate implementation story.
- Governance/test files: `backend/tests/architecture/test_astrology_runtime_boundary.py` or an adjacent guard test.
- Files to delete: none.
- Before evidence: E-012, E-013, E-014.
- After evidence: guard test passing and negative lexical scan over structural roots.
- Required no-wildcard allowlist and No Legacy checks: no broad `backend/app/domain/astrology/**` allowlist; each exception names file, token, reason and permanence.
- Stop condition: structural roots fail on both known interpretive identifiers and representative final-user narrative phrases.

## Deferred Non-Domain Candidates

- F-004 does not produce an implementation candidate in this audit. Future prompt/prediction documentation cleanup may mark historical docs as historical-only, but current runtime ownership can be verified by filesystem and import scans.
