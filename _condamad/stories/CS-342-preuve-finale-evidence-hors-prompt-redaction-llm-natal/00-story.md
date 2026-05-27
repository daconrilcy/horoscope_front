# Story CS-342 preuve-finale-evidence-hors-prompt-redaction-llm-natal: Prove Final Evidence Boundary And Natal LLM Validation
Status: ready-to-review

## Trigger / Source

- Mode: Brief direct with repo-informed evidence.
- Source brief: `_story_briefs/cs-342-cloturer-process-evidence-hors-prompt-validation-redaction-llm-natale.md`.
- Source problem: after CS-341, the project needs final proof that evidence stays outside the natal prompt and still validates LLM writing.
- Source stakes:
  - Prompt-visible natal material must be limited to writing guidance data.
  - Evidence, refs, hashes, grounding status, and validation decisions must remain backend validation-only or audit-only.
  - The final report must explain acceptance, rejection, or partial compliance decisions without a real provider call.
  - Scans must classify remaining evidence occurrences instead of treating every historical mention as executable drift.
- Source-alignment review: PASS. Objective, target state, ACs, tasks, evidence, non-goals, and guardrails map to the brief stakes.

## Objective

Produce the final CS-342 validation report proving that the modern natal LLM prompt receives no evidence block, that backend validation uses
internal evidence after generation, and that persistent audit keeps the data required to explain validation decisions.

## Target State

- A timestamped final report exists under `_condamad/reports/evidence-hors-prompt-validation-redaction-llm-natal/`.
- The report defines the final prompt-visible blocks as `facts`, `signals`, `limits`, and `shaping`.
- The report defines evidence, evidence refs, hashes, grounding status, and validation owner as validation-only or audit-only material.
- Provider handoff proof shows no `evidence`, `evidence_refs`, `grounding_status`, `validation_owner`, hashes, or `provenance` in the user message.
- Backend tests prove post-generation validation with one compliant writing case, invented-data rejection, missing-data or limit-contradiction
  rejection, and internally ungrounded-writing rejection.
- Persistent audit proof shows evidence refs, hashes, and grounding data remain available outside the prompt.
- Targeted scans classify remaining evidence occurrences as validation owner, audit owner, internal contract, guard test, history, or debt.
- The story remains backend-only and report-focused; frontend, public API, schema migration, and real provider calls stay out of scope.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-342-cloturer-process-evidence-hors-prompt-validation-redaction-llm-natale.md` - source brief read.
- Evidence 2: `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md` - prerequisite source read.
- Evidence 3: `_story_briefs/cs-340-cloturer-validation-frontiere-provenance-prompt-audit-llm-natal.md` - prior closure source read.
- Evidence 4: `_condamad/reports/cs-339-cs-340-delivery-report.md` - prior delivery report read.
- Evidence 5: `_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/2026-05-27-1407/validation-frontiere-provenance.md` - prior validation report read.
- Evidence 6: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-342`.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - guardrail IDs resolved by scope vector without registry enrichment.
- Evidence 8: `resolve_guardrails.py` returned RG-002, RG-022, RG-047, and RG-052 for the backend LLM validation scope.
- Evidence 9: targeted file inventory found the LLM input, gateway, natal service, provider-boundary, architecture, and audit test surfaces.
- Repository structure alert: none. `backend`, `backend/app`, `backend/tests`, `frontend`, and `frontend/src` exist in this workspace.
- Prerequisite status note: tracker currently marks CS-341 as `ready-to-dev`; CS-342 implementation must confirm CS-341 completion before validation.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Final validation report for the natal LLM evidence prompt boundary.
  - Backend tests and scans proving provider handoff excludes validation-only and audit-only evidence fields.
  - Backend tests proving post-generation validation accepts grounded writing and rejects unsupported, missing-data or limit-contradicting,
    and internally ungrounded writing.
  - Persistent audit proof for evidence refs, hashes, grounding status, and validation decisions.
  - Occurrence classification for evidence-related terms in active code, tests, reports, and briefs.
- Out of scope:
  - Frontend UI, public API route changes, database schema changes, auth, i18n, styling, build tooling, and migrations.
  - Real LLM provider calls, editorial prompt rewrite, hash semantic changes, and audit evidence deletion.
  - Reworking the prior `chart_json` or `natal_data` extinction beyond keeping existing guards active.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
  - No new provider integration, external package, persistence policy, or public endpoint.
  - No broad historical rewrite of `_condamad` reports or `_story_briefs`.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend LLM closure-report and runtime-validation contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only validation, scan, report, guard, or blocking fix work required to prove the CS-341 boundary.
  - Preserve backend evidence, evidence refs, hashes, grounding status, and validation owner for validation and audit.
  - Do not call a real LLM provider.
  - Keep CS-339, CS-340, CS-336, CS-338, and CS-341 boundary guards active.
- Deletion allowed: no
- Replacement allowed: yes
- Replacement constraints:
  - Replace stale validation expectations only when they contradict the final evidence-out-of-prompt boundary.
  - Replace uncollected or obsolete validation targets with collected backend tests that prove the same boundary.
- User decision required if: CS-341 is not implemented when CS-342 execution starts or semantic validation requires a public API or schema change.
- Additional validation rules:
  - The provider handoff user message must be proven with `pytest`, local doubles, or an equivalent `AST guard`.
  - Validation must prove the complete internal object still carries evidence refs, grounding data, and hashes outside the prompt projection.
  - Runtime evidence must include full `pytest -q backend/tests/` target paths or `AST guard` checks.
  - The final report must classify remaining occurrences without requiring total absence of evidence vocabulary.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, provider-boundary tests, audit tests, and `AST guard` evidence prove backend behavior. |
| Baseline Snapshot | yes | Before and after prompt-boundary and scan artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Prompt material, validation evidence, audit fields, and report artifacts need separate canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this final validation story. |
| Contract Shape | yes | Prompt-visible blocks, provider payload exclusions, validation outcomes, and report sections have exact shapes. |
| Batch Migration | no | No batch migration or multi-step conversion is in scope. |
| Reintroduction Guard | yes | Evidence prompt exposure, empty evidence payloads, hashes, provenance, `chart_json`, and `natal_data` stay guarded. |
| Persistent Evidence | yes | Report, scans, validation output, final evidence, and review output must be kept for handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The final validation report exists. | Evidence profile: baseline_before_after_diff; `python` checks the report path under `_condamad/reports`. |
| AC2 | Prompt-visible blocks exclude evidence. | Evidence profile: ast_architecture_guard; `python` checks `LLM_ASTROLOGY_INPUT_DATA_ROLES`; `AST guard`. |
| AC3 | Provider user message excludes validation data. | Evidence profile: json_contract_shape; `pytest` handoff boundary test. |
| AC4 | Internal LLM input keeps evidence refs. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py`. |
| AC5 | Persistent audit stores validation data. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py`. |
| AC6 | Compliant generated writing passes validation. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_rejected_narrative_answer_workflow.py`. |
| AC7 | Invented generated data fails validation. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_rejected_narrative_answer_workflow.py`. |
| AC8 | Missing-data or limit-contradicting writing fails validation. | Evidence profile: json_contract_shape; rejected narrative workflow `pytest`. |
| AC9 | Internally ungrounded writing fails validation. | Evidence profile: json_contract_shape; rejected narrative workflow `pytest`. |
| AC10 | Empty evidence prompt contracts are absent. | Evidence profile: targeted_forbidden_symbol_scan; evidence placeholder `rg`. |
| AC11 | Registry/schema/fixture prompt dependencies are absent. | Evidence profile: targeted_forbidden_symbol_scan; `AST guard` plus targeted `rg` scan. |
| AC12 | Remaining evidence occurrences are classified. | Evidence profile: repo_wide_negative_scan; `rg` output plus report classification table. |
| AC13 | Backend validations pass. | Evidence profile: baseline_before_after_diff; `ruff check .`; `pytest -q backend/tests --tb=short`. |
| AC14 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence and generated paths. |

## Implementation Tasks

- [x] Task 1: Confirm CS-341 is implemented or record a blocker before running CS-342 validation. (AC: AC13)
- [x] Task 2: Generate or refresh baseline prompt-boundary and scan artifacts for active backend prompt surfaces. (AC: AC2, AC3, AC10)
- [x] Task 3: Verify the provider handoff user message excludes evidence, validation, audit, hash, and provenance fields. (AC: AC3)
- [x] Task 4: Verify the complete internal LLM input and persistent audit keep evidence refs, hashes, and grounding status. (AC: AC4, AC5)
- [x] Task 5: Verify post-generation validation with compliant, invented-data, missing-data or limit-contradiction, and ungrounded cases. (AC: AC6, AC7, AC8, AC9)
- [x] Task 6: Run targeted scans for evidence placeholders, empty prompt evidence blocks, schemas, registries, fixtures, and audit-only provider payload fields. (AC: AC10, AC11)
- [x] Task 7: Classify remaining evidence occurrences in the final report with clear ownership. (AC: AC12)
- [x] Task 8: Run backend format, lint, targeted tests, full backend tests, and report path checks. (AC: AC13)
- [x] Task 9: Persist validation output, scan output, final evidence, and review output artifacts. (AC: AC1, AC14)

## Files to Inspect First

- `_story_briefs/cs-342-cloturer-process-evidence-hors-prompt-validation-redaction-llm-natale.md` - source scope.
- `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md` - prerequisite boundary scope.
- `_story_briefs/cs-340-cloturer-validation-frontiere-provenance-prompt-audit-llm-natal.md` - prior closure scope.
- `_condamad/reports/cs-339-cs-340-delivery-report.md` - prior delivery evidence.
- `_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/2026-05-27-1407/validation-frontiere-provenance.md` - prior report.
- `_condamad/stories/story-status.md` - prerequisite and tracker state.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - canonical data roles and full internal contract owner.
- `backend/app/domain/llm/runtime/gateway.py` - provider handoff prompt projection owner.
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` - post-generation validation owner.
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
  - Targeted `rg` scans for evidence placeholders, empty prompt evidence payloads, validation-only fields, audit-only fields, and legacy carriers.
- Static scans alone are not sufficient for this story because:
  - The provider handoff message and post-generation validation decisions must be proven by executable tests.

## Contract Shape

- Contract type:
  - Backend validation report, internal LLM input role contract, provider payload projection, post-generation validation, and audit persistence.
- Fields:
  - `facts`: prompt-eligible factual material.
  - `signals`: prompt-eligible interpretive signals.
  - `limits`: prompt-eligible missing data and reading limits.
  - `shaping`: prompt-eligible plan and editorial shaping metadata.
  - `evidence_refs`: backend-only evidence links for post-generation validation and audit.
  - `grounding_status`: backend-only validation status.
  - `projection_hash`: backend-only source projection hash for audit.
  - `llm_input_hash`: backend-only LLM input hash for audit.
- Prompt-visible fields:
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
  - compliant writing passes without rejection.
  - unsupported writing is rejected or marked non-compliant.
  - limit-contradicting or missing-data-contradicting writing is rejected or marked non-compliant.
  - ungrounded writing is rejected, marked non-compliant, or explicitly classified by validation status.
- Required report sections:
  - summary of verified correction.
  - final prompt-visible block definition.
  - final evidence, validation, and audit role definition.
  - provider handoff proof without evidence fields.
  - post-generation validation proof with positive and negative cases.
  - scan results.
  - validation commands.
  - residual risks.
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
  - `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/evidence/prompt-boundary-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/evidence/prompt-boundary-after.json`
- Expected invariant:
  - The only intended prompt-boundary delta from CS-341 validation is proof completion; backend evidence and audit data remain available.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Data role classification | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | duplicated prompt block list |
| Provider prompt projection | `backend/app/domain/llm/runtime/gateway.py` | service-layer ad hoc payload assembly |
| Post-generation validation | `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` | provider prompt payload |
| Audit persistence fields | `backend/app/services/llm_generation/natal/interpretation_service.py` | prompt-visible projection |
| Boundary tests | `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` | uncollected helper-only tests |
| Architecture guards | `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` | historical report-only evidence |
| Final report | `_condamad/reports/evidence-hors-prompt-validation-redaction-llm-natal/*/validation-evidence-hors-prompt.md` | story notes only |

## Mandatory Reuse / DRY Constraints

- Reuse `LLM_ASTROLOGY_INPUT_DATA_ROLES` as the single canonical role map.
- Reuse existing gateway projection helpers instead of adding a parallel prompt serializer.
- Reuse existing evidence ref validation and rejected narrative workflow concepts for post-generation validation.
- Reuse existing audit persistence path for evidence refs, hashes, and grounding status.
- Reuse existing CS-339, CS-340, CS-336, CS-338, and CS-341 guard tests.
- Do not add external packages.
- Do not duplicate prompt, validation, or audit field lists across production code and tests without an ownership guard.

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
- Required boundary scan:
  - Run the full evidence boundary `rg` command from VC12 and save the classified output.
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
| Registry gap | No exact guardrail exists for final evidence-out-of-prompt validation closure. | Resolver output recorded in evidence. |

Non-applicable examples: RG-047 and RG-052 are frontend style or CSS guardrails and remain out of scope for this backend-only story.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Prompt baseline | `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/evidence/prompt-boundary-before.json` | Preserve provider payload baseline. |
| Prompt after | `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/evidence/prompt-boundary-after.json` | Preserve provider payload after proof. |
| Scan output | `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/evidence/boundary-scan.txt` | Keep targeted scan results. |
| Validation output | `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/evidence/validation-output.txt` | Keep command results. |
| Final report | `_condamad/reports/evidence-hors-prompt-validation-redaction-llm-natal/*/validation-evidence-hors-prompt.md` | Keep closure report. |
| Final evidence | `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/generated/10-final-evidence.md` | Keep implementation evidence. |
| Review output | `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/generated/11-code-review.md` | Keep review handoff. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this single backend LLM validation story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/reports/evidence-hors-prompt-validation-redaction-llm-natal/*/validation-evidence-hors-prompt.md` - final validation report.
- `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/evidence/prompt-boundary-before.json` - baseline artifact.
- `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/evidence/prompt-boundary-after.json` - after artifact.
- `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/evidence/boundary-scan.txt` - scan artifact.
- `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/evidence/validation-output.txt` - validation artifact.
- `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/generated/10-final-evidence.md` - final handoff.
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` - provider payload boundary checks.
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` - AST prompt boundary guard.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py` - evidence ref checks.
- `backend/tests/unit/test_rejected_narrative_answer_workflow.py` - generated writing validation checks.
- `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py` - audit persistence checks.

Likely production files only for blocking validation fixes:

- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - canonical role map and full evidence ownership.
- `backend/app/domain/llm/runtime/gateway.py` - prompt projection and provider handoff.
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` - post-generation validation outcome.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - audit persistence integration.

Likely tests:

- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` - data role and contract shape checks.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py` - prompt-influencing hash behavior.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py` - backend-only evidence refs checks.
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` - provider payload boundary checks.
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` - AST prompt boundary guard.
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

- VC1 prerequisite:
  `python -c "from pathlib import Path; s=Path('../_condamad/stories/story-status.md').read_text(); assert '| CS-341 |' in s and '| done |' in s"`
- VC2 report:
  `python -c "from pathlib import Path; root=Path('../_condamad/reports/evidence-hors-prompt-validation-redaction-llm-natal'); assert root.exists()"`
  Run a `python` check that `root.glob('*/validation-evidence-hors-prompt.md')` returns at least one report.
- VC3 role:
  `python -c "from app.domain.astrology.interpretation.llm_astrology_input_v1 import LLM_ASTROLOGY_INPUT_DATA_ROLES as r; assert 'evidence' not in r['prompt_visible']"`
- VC4 format: `ruff format .`
- VC5 lint: `ruff check .`
- VC6 contract:
  `pytest -q tests/unit/domain/astrology/test_llm_astrology_input_v1.py tests/unit/domain/astrology/test_llm_astrology_input_hash.py --tb=short`
- VC7 evidence:
  `pytest -q tests/unit/domain/astrology/test_llm_astrology_input_evidence.py --tb=short`
- VC8 boundary:
  `pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py tests/architecture/test_llm_astrology_input_payload_boundaries.py --tb=short`
- VC9 validation:
  `pytest -q tests/unit/test_rejected_narrative_answer_workflow.py --tb=short`
- VC10 audit:
  `pytest -q tests/integration/test_llm_legacy_extinction.py tests/integration/llm/test_natal_llm_astrology_input_audit.py --tb=short`
- VC11 full: `pytest -q tests --tb=short`
- VC12 classified scan:
  `rg -n "evidence|evidence_refs|grounding_status|validation_owner|prompt_visible|validation_only" app tests ..\_condamad ..\_story_briefs`
  `rg -n "audit_only|llm_input_hash|projection_hash|provenance" app tests ..\_condamad ..\_story_briefs`
- VC13 empty evidence:
  `rg -n "{{evidence}}|{{evidence_refs}}|{{grounding_status}}|\"evidence\": \{\}|prompt_payload\\[\"evidence\"\\]" app tests`
- VC14 artifacts:
  ```powershell
  python -c "from pathlib import Path; root=Path('../_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal'); assert (root/'evidence').exists()"
  python -c "from pathlib import Path; root=Path('../_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal'); assert (root/'generated').exists()"
  ```

## Regression Risks

- A false closure could prove evidence absence from the prompt while checking only JSON form and not semantic grounding.
- Treating prompt evidence absence as evidence deletion would break audit and persistence.
- A provider-boundary test could inspect a builder object instead of the serialized handoff payload.
- Broad scans can include legitimate historical references; classify executable prompt paths, registries, schemas, and fixtures separately from reports and briefs.
- Full backend tests may expose unrelated failures; record unrelated failures separately and keep the boundary result strict.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Use PowerShell on Windows and activate `.\.venv\Scripts\Activate.ps1` before every Python, Ruff, Pytest, or script command.
- Confirm CS-341 is `done` before executing CS-342 validation; record a blocker if it is not done.
- Prove provider handoff with local test doubles or deterministic unit tests, not a real LLM provider call.
- Do not modify frontend files, public API route files, database migrations, or prompt editorial copy outside the boundary.
- Write the report under a timestamped child directory of `_condamad/reports/evidence-hors-prompt-validation-redaction-llm-natal/`.

## References

- `_story_briefs/cs-342-cloturer-process-evidence-hors-prompt-validation-redaction-llm-natale.md`
- `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md`
- `_story_briefs/cs-340-cloturer-validation-frontiere-provenance-prompt-audit-llm-natal.md`
- `_condamad/reports/cs-339-cs-340-delivery-report.md`
- `_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/2026-05-27-1407/validation-frontiere-provenance.md`
- `_condamad/stories/regression-guardrails.md`
