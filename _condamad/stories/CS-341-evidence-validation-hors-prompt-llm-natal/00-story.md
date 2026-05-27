# Story CS-341 evidence-validation-hors-prompt-llm-natal: Move Evidence Out Of Natal LLM Prompt And Validate Output
Status: done

## Trigger / Source

- Mode: Brief direct with repo-informed evidence.
- Source brief: `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md`.
- Source problem: `llm_astrology_input_v1` still exposes `evidence` as prompt-visible, then the gateway serializes an empty evidence block.
- Source stakes:
  - Prompt engine must receive only `facts`, `signals`, `limits`, and `shaping`.
  - Backend must keep evidence material for audit and post-generation validation.
  - Output validation must reject unsupported or limit-ignoring natal LLM writing without a real provider call.
- Source-alignment review: PASS. Objective, ACs, tasks, evidence, non-goals, and guardrails map to the brief stakes.

## Objective

Finalize the `llm_astrology_input_v1` evidence boundary so evidence is never sent to the natal LLM prompt engine, while backend audit and
post-generation validation still use internal evidence, refs, grounding status, hashes, and limits to validate the generated writing.

## Target State

- `LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"]` contains `facts`, `signals`, `limits`, and `shaping` only.
- Evidence material is classified under a backend-only role such as `validation_only` or `audit_validation`.
- The provider payload for modern natal LLM handoff has no top-level `evidence` key.
- Tests no longer assert `prompt_payload["evidence"] == {}`.
- The complete `llm_astrology_input_v1` object still contains evidence refs, grounding status, validation owner, provenance, and hashes.
- Persistent natal audit keeps evidence refs, grounding status, projection hash, and LLM input hash.
- Post-generation validation proves grounded writing passes and unsupported or limit-ignoring writing is rejected or marked non-compliant.
- CS-339 and CS-340 guards on provenance, hashes, audit-only fields, `chart_json`, and `natal_data` remain active.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md` - source brief read.
- Evidence 2: `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md` - hash and evidence audit source read.
- Evidence 3: `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md` - prompt guard source read.
- Evidence 4: `_story_briefs/cs-339-aligner-provenance-audit-only-hors-prompt-llm-natal.md` - provenance boundary source read.
- Evidence 5: `_story_briefs/cs-340-cloturer-validation-frontiere-provenance-prompt-audit-llm-natal.md` - closure validation source read.
- Evidence 6: `_condamad/reports/cs-339-cs-340-delivery-report.md` - prior delivery report read.
- Evidence 7: `_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/2026-05-27-1407/validation-frontiere-provenance.md` - final boundary report read.
- Evidence 8: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-341`.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - guardrails resolved by scope vector without registry enrichment.
- Evidence 10: targeted `rg` found current LLM evidence, prompt, audit, hash, and legacy symbols in `backend/app` and `backend/tests`.
- Evidence 11: `resolve_guardrails.py` returned RG-002, RG-022, RG-047, and RG-052 for the backend LLM scope vector.
- Repository structure alert: none. `backend` and `frontend` roots exist in this workspace.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend contract roles for `llm_astrology_input_v1`.
  - Natal LLM provider payload projection in the gateway.
  - Backend post-generation validation of generated natal writing against internal facts, signals, limits, evidence refs, and grounding.
  - Persistent audit checks for evidence refs, grounding status, `projection_hash`, and `llm_input_hash`.
  - Targeted tests and scans for prompt boundary, post-generation validation, audit persistence, and legacy guards.
- Out of scope:
  - Frontend UI, public API route changes, database schema changes, auth, i18n, styling, build tooling, and migrations.
  - Real LLM provider calls, editorial rewrite of all prompts, hash semantic changes, and audit evidence deletion.
  - Reintroducing `chart_json` or `natal_data` into the modern natal prompt.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
  - No new provider integration, external package, persistence policy, or public endpoint.
  - No broad cleanup of historical `_condamad` or `_story_briefs` references.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend LLM prompt-boundary and post-generation validation contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Remove only prompt exposure of `evidence` for the modern natal LLM provider payload.
  - Preserve backend access to internal evidence and hashes for validation, audit, and persistence.
  - Add or tighten post-generation validation without calling a real provider.
  - Keep CS-339, CS-340, CS-336, and CS-338 boundary guards active.
- Deletion allowed: no
- Replacement allowed: yes
- Replacement constraints:
  - Replace the empty prompt `evidence` handoff with backend-only evidence usage.
  - Replace tests that lock `prompt_payload["evidence"] == {}` with absence and validation checks.
- User decision required if: output validation cannot be expressed without changing the persisted audit schema or public API contract.
- Additional validation rules:
  - The provider handoff payload must be checked through `pytest`, `TestClient`-free gateway tests, or an equivalent `AST guard`.
  - Validation must prove the complete internal object still carries evidence refs and grounding data outside the prompt projection.
  - Negative tests must cover unsupported claims and ignored critical limits.
  - Runtime evidence must include full `pytest -q backend/tests/` target paths or `AST guard` checks.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, provider-boundary tests, audit tests, and `AST guard` evidence prove runtime backend behavior. |
| Baseline Snapshot | yes | Before and after prompt-boundary artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Prompt material, validation evidence, and persistent audit fields need separate canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this boundary correction. |
| Contract Shape | yes | Roles, provider payload blocks, validation output, and audit fields have exact expected shapes. |
| Batch Migration | no | No batch migration or multi-step conversion is in scope. |
| Reintroduction Guard | yes | Evidence prompt exposure, empty evidence payloads, hashes, provenance, `chart_json`, and `natal_data` must stay guarded. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for implementation review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Prompt-visible roles exclude `evidence`. | Evidence profile: ast_architecture_guard; `python` checks `LLM_ASTROLOGY_INPUT_DATA_ROLES`. |
| AC2 | Provider payload omits top-level `evidence`. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`. |
| AC3 | Empty evidence payload expectations are gone. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks `prompt_payload[\"evidence\"] == {}`. |
| AC4 | The full internal LLM input keeps evidence refs. | Evidence profile: json_contract_shape; `pytest` evidence-ref tests. |
| AC5 | Persistent audit stores evidence refs. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py`. |
| AC6 | Grounded generated writing passes validation. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_rejected_narrative_answer_workflow.py`. |
| AC7 | Unsupported generated claims fail validation. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_rejected_narrative_answer_workflow.py`. |
| AC8 | Ignored critical limits fail validation. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_rejected_narrative_answer_workflow.py`. |
| AC9 | Audit-only prompt boundary guards remain active. | Evidence profile: ast_architecture_guard; hash/boundary pytest; `rg`. |
| AC10 | Legacy natal prompt carrier guards remain active. | Evidence profile: targeted scan; legacy extinction pytest; `rg`. |
| AC11 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |

## Implementation Tasks

- [ ] Task 1: Update the canonical role map so `evidence` is backend-only and no longer part of `prompt_visible`. (AC: AC1)
- [ ] Task 2: Update gateway prompt projection so modern natal provider payload contains `facts`, `signals`, `limits`, and `shaping` only. (AC: AC2)
- [ ] Task 3: Replace tests that lock an empty `evidence` prompt block with tests proving the key is absent from provider handoff. (AC: AC2, AC3)
- [ ] Task 4: Preserve evidence refs, grounding status, validation owner, provenance, projection hash, and LLM input hash in the full contract. (AC: AC4)
- [ ] Task 5: Keep audit persistence reading evidence refs, grounding status, projection hash, and LLM input hash from backend-owned data. (AC: AC5)
- [ ] Task 6: Strengthen post-generation validation for grounded positive output, unsupported claims, and ignored critical limits. (AC: AC6, AC7, AC8)
- [ ] Task 7: Keep CS-339 and CS-340 guards active for provenance, hashes, and audit-only prompt boundaries. (AC: AC9)
- [ ] Task 8: Keep CS-336 and CS-338 guards active for `chart_json` and `natal_data`. (AC: AC10)
- [ ] Task 9: Persist prompt-boundary, scan, validation, final evidence, and review artifacts for handoff. (AC: AC11)

## Files to Inspect First

- `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md` - source scope.
- `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md` - hash and evidence audit expectations.
- `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md` - prompt-boundary guard expectations.
- `_story_briefs/cs-339-aligner-provenance-audit-only-hors-prompt-llm-natal.md` - audit-only boundary expectations.
- `_story_briefs/cs-340-cloturer-validation-frontiere-provenance-prompt-audit-llm-natal.md` - closure validation expectations.
- `_condamad/reports/cs-339-cs-340-delivery-report.md` - prior delivery evidence.
- `_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/2026-05-27-1407/validation-frontiere-provenance.md` - final report.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - canonical data roles and full internal contract owner.
- `backend/app/domain/llm/runtime/gateway.py` - provider handoff prompt projection owner.
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` - post-generation rejection workflow owner.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - persistent audit owner.
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` - provider payload boundary tests.
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` - static prompt boundary guard.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py` - evidence ref contract tests.
- `backend/tests/unit/test_rejected_narrative_answer_workflow.py` - output validation tests.
- `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py` - audit persistence tests.

## Runtime Source of Truth

- Primary source of truth:
  - `pytest` coverage for gateway/provider-boundary behavior.
  - `pytest` coverage for evidence refs and rejected narrative answer workflow.
  - `pytest` coverage for persistent natal audit.
  - `AST guard` coverage for canonical prompt role ownership in the gateway.
- Secondary evidence:
  - Targeted `rg` scans for empty prompt evidence payloads, evidence placeholders, audit-only fields, and legacy prompt carriers.
- Static scans alone are not sufficient for this story because:
  - The final payload just before provider handoff and the post-generation validation result must be proven by executable tests.

## Contract Shape

- Contract type:
  - Backend internal LLM input role contract, provider payload projection, post-generation validation, and audit persistence.
- Fields:
  - `facts`: prompt-eligible factual material.
  - `signals`: prompt-eligible interpretive signals.
  - `limits`: prompt-eligible missing data and reading limits.
  - `shaping`: prompt-eligible plan and editorial shaping metadata.
  - `evidence_refs`: backend-only evidence links for post-generation validation and audit.
  - `grounding_status`: backend-only validation status.
  - `projection_hash`: backend-only source projection hash for audit.
  - `llm_input_hash`: backend-only LLM input hash for audit.
- Prompt-visible fields after implementation:
  - `facts`: prompt-eligible factual material.
  - `signals`: prompt-eligible interpretive signals.
  - `limits`: prompt-eligible missing data and reading limits.
  - `shaping`: prompt-eligible plan and editorial shaping metadata.
- Backend-only validation and audit fields:
  - `evidence`
  - `evidence_refs`
  - `grounding_status`
  - `validation_owner`
  - `provenance`
  - `projection_hash`
  - `llm_input_hash`
  - `provider_response`
  - `persisted_answer`
- Required validation output states:
  - grounded writing passes without rejection.
  - unsupported writing is rejected or marked non-compliant.
  - limit-ignoring writing is rejected or marked non-compliant.
- Minimal expected LLM output contract for validation:
  - sections or items identifiable by the backend validator.
  - interpretive claims or assertions checkable against internal facts, signals, limits, and evidence refs.
  - explicit handling of injected limits and missing data.
  - no assertion contradicting internal source data.
  - validation status, marker, or rejection reason when the existing schema supports it.
- Required fields:
  - `facts`
  - `signals`
  - `limits`
  - `shaping`
  - backend-owned evidence refs
  - validation status or rejection reason
- Optional fields:
  - none for provider payload evidence; `evidence` must be absent from provider payload.
- Status codes:
  - none; this story does not change a public API route.
- Serialization names:
  - JSON keys are emitted with the exact names listed above.
- Frontend type impact:
  - none.
- Generated contract impact:
  - none.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal/evidence/prompt-boundary-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal/evidence/prompt-boundary-after.json`
- Expected invariant:
  - The only intended provider payload surface delta is removal of top-level `evidence`; backend evidence and audit data remain available.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Data role classification | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | duplicated prompt block list |
| Provider prompt projection | `backend/app/domain/llm/runtime/gateway.py` | service-layer ad hoc payload assembly |
| Post-generation validation | `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` | provider prompt payload |
| Audit persistence fields | `backend/app/services/llm_generation/natal/interpretation_service.py` | prompt-visible projection |
| Boundary tests | `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` | uncollected helper-only tests |
| Architecture guards | `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` | historical report-only evidence |

## Mandatory Reuse / DRY Constraints

- Reuse `LLM_ASTROLOGY_INPUT_DATA_ROLES` as the single canonical role map.
- Reuse existing gateway projection helpers instead of adding a parallel prompt serializer.
- Reuse `validate_evidence_refs_by_section` and rejected narrative workflow concepts for post-generation validation.
- Reuse existing audit persistence path for evidence refs and hashes.
- Do not add external packages.
- Do not duplicate prompt/audit field lists across production code and tests without an ownership guard.

## No Legacy / Forbidden Paths

- No legacy `chart_json` or `natal_data` prompt path may be accepted for modern natal LLM handoff.
- No compatibility prompt path may be added for evidence refs or hash fields.
- No fallback prompt path may be added for backend-only evidence material.
- Forbidden provider prompt fields for the modern natal payload:
  - `evidence`
  - `evidence_refs`
  - `grounding_status`
  - `validation_owner`
  - `provenance`
  - `projection_hash`
  - `llm_input_hash`
  - `provider_response`
  - `persisted_answer`

## Reintroduction Guard

- Guard the exact forbidden provider prompt symbols with targeted `pytest`, `AST guard`, and `rg` checks.
- Required empty-payload scan:
  - `rg -n "\"evidence\": \{\}|prompt_payload\\[\"evidence\"\\]|{{evidence}}|{{evidence_refs}}|{{grounding_status}}" app tests`
- Required role scan:
  - `rg -n "prompt_visible|validation_only|audit_only|evidence|evidence_refs|grounding_status|llm_input_hash|projection_hash" app tests`
- Required legacy scan:
  - `rg -n "chart_json|natal_data|LLM_ASTROLOGY_INPUT_V1_PROMPT_BLOCKS" app tests`
- Required payload tests:
  - `pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
  - `pytest -q tests/architecture/test_llm_astrology_input_payload_boundaries.py`

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-022 `align-prompt-generation-story-validation-paths` | Active validation commands must target collected backend tests. | `pytest` targeted paths; validation output. |
| RG-002 `refactor-api-v1-routers` | Needs-investigation only for backend layout drift; API routers are not in scope. | `rg` ownership scan; no API route edits. |
| Registry gap | No exact guardrail exists for `llm_astrology_input_v1` evidence prompt removal. | Resolver output recorded in evidence. |

Non-applicable examples: RG-047 and RG-052 are frontend style or CSS guardrails and remain out of scope for this backend-only story.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Prompt baseline | `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal/evidence/prompt-boundary-before.json` | Preserve provider payload before change. |
| Prompt after | `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal/evidence/prompt-boundary-after.json` | Preserve provider payload after change. |
| Scan output | `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal/evidence/boundary-scan.txt` | Keep targeted scan results. |
| Validation output | `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal/evidence/validation-output.txt` | Keep command results. |
| Final evidence | `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal/generated/10-final-evidence.md` | Keep implementation evidence. |
| Review output | `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this single backend LLM boundary story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - canonical role map and full evidence ownership.
- `backend/app/domain/llm/runtime/gateway.py` - prompt projection and provider handoff.
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` - post-generation validation outcome.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - audit persistence integration.
- `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal/evidence/prompt-boundary-before.json` - baseline artifact.
- `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal/evidence/prompt-boundary-after.json` - after artifact.
- `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal/evidence/validation-output.txt` - validation artifact.
- `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal/generated/10-final-evidence.md` - final handoff.

Likely tests:

- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` - data role and contract shape checks.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py` - prompt-influencing hash behavior.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py` - backend-only evidence refs checks.
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` - provider payload boundary checks.
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` - AST prompt boundary guard.
- `backend/tests/unit/test_rejected_narrative_answer_workflow.py` - grounded and non-compliant output validation checks.
- `backend/tests/integration/test_llm_legacy_extinction.py` - legacy prompt carrier guard.
- `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py` - audit persistence checks.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no public API route changes are touched.
- `backend/app/infra/**` - out of scope; no persistence adapter or schema change is touched.
- `backend/migrations/**` - out of scope; no migration is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

All Python commands must run after `.\.venv\Scripts\Activate.ps1`, then `cd backend`.

- VC1 role:
  `python -c "from app.domain.astrology.interpretation.llm_astrology_input_v1 import LLM_ASTROLOGY_INPUT_DATA_ROLES as r; assert 'evidence' not in r['prompt_visible']"`
- VC2 format: `ruff format .`
- VC3 lint: `ruff check .`
- VC4 contract:
  `pytest -q tests/unit/domain/astrology/test_llm_astrology_input_v1.py tests/unit/domain/astrology/test_llm_astrology_input_hash.py --tb=short`
- VC5 evidence:
  `pytest -q tests/unit/domain/astrology/test_llm_astrology_input_evidence.py --tb=short`
- VC6 boundary:
  `pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py tests/architecture/test_llm_astrology_input_payload_boundaries.py --tb=short`
- VC7 validation:
  `pytest -q tests/unit/test_rejected_narrative_answer_workflow.py --tb=short`
- VC8 audit:
  `pytest -q tests/integration/test_llm_legacy_extinction.py tests/integration/llm/test_natal_llm_astrology_input_audit.py --tb=short`
- VC9 full: `pytest -q tests --tb=short`
- VC10 roles:
  `rg -n "prompt_visible|validation_only|audit_only|evidence|evidence_refs|grounding_status|llm_input_hash|projection_hash" app tests`
- VC11 empty evidence:
  `rg -n "\"evidence\": \{\}|prompt_payload\\[\"evidence\"\\]|{{evidence}}|{{evidence_refs}}|{{grounding_status}}" app tests`
- VC12 legacy:
  `rg -n "chart_json|natal_data|LLM_ASTROLOGY_INPUT_V1_PROMPT_BLOCKS" app tests`
- VC13 artifacts:
  ```powershell
  python -c "from pathlib import Path; root=Path('../_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal'); assert (root/'evidence').exists()"
  python -c "from pathlib import Path; root=Path('../_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal'); assert (root/'generated').exists()"
  ```

## Regression Risks

- Removing prompt `evidence` without strengthening post-generation validation would weaken non-invention controls.
- Treating `evidence` absence in the prompt as evidence deletion would break audit and persistence.
- A provider-boundary test could inspect a builder object instead of the serialized handoff payload.
- Broad scans can include legitimate historical references; classify executable prompt paths separately from reports and briefs.
- Full backend tests may expose unrelated failures; record unrelated failures separately and keep the boundary result strict.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Use PowerShell on Windows and activate `.\.venv\Scripts\Activate.ps1` before every Python, Ruff, Pytest, or script command.
- Start from `llm_astrology_input_v1.py`, `gateway.py`, `rejected_answer_workflow.py`, and the listed tests.
- Prove provider handoff with local test doubles or deterministic unit tests, not a real LLM provider call.
- Do not modify frontend files, public API route files, database migrations, or prompt editorial copy outside the boundary.

## References

- `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md`
- `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md`
- `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md`
- `_story_briefs/cs-339-aligner-provenance-audit-only-hors-prompt-llm-natal.md`
- `_story_briefs/cs-340-cloturer-validation-frontiere-provenance-prompt-audit-llm-natal.md`
- `_condamad/reports/cs-339-cs-340-delivery-report.md`
- `_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/2026-05-27-1407/validation-frontiere-provenance.md`
- `_condamad/stories/regression-guardrails.md`
