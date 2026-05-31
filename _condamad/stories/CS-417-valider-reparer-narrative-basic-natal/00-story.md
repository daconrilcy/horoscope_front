# Story CS-417 valider-reparer-narrative-basic-natal: Valider Et Reparer Narrative Basic Natal
Status: ready-to-review

## Trigger / Source
- Source brief: `_story_briefs/cs-412-valider-et-reparer-narrative-basic-natal.md`.
- Source dependencies: CS-410, CS-411, CS-402 and CS-398 must provide the upstream Basic reading inputs and quota contract.
- Bounded problem: Basic natal LLM output can be accepted before proving that the draft matches the reading plan and public narrative rules.
- Source-alignment evidence: objectives, stakes, ACs, tasks, validations, non-goals and guardrails map to the brief without scope drift.

## Objective
Validate each Basic natal `NarrativeDraft` against `BasicNatalReadingPlan`, repair constrained invalid drafts once, then reject or use a short deterministic fallback.

## Target State
- `NarrativeValidator` checks Basic natal draft structure against `BasicNatalReadingPlan`.
- Accepted Basic output contains every requested section and no unauthorized section.
- Accepted Basic output uses only facts present in the reading plan.
- Accepted Basic output hides scores, internal fields, raw markers and technical identifiers.
- Accepted Basic output stays in `vous`, respects maximum length, keeps limitations, disclaimers and public sources, and avoids prescriptive advice.
- Invalid Basic output is repaired through a constrained prompt attempt, then rejected or replaced by a short deterministic fallback.
- Rejection audit records `request_id`, `engine_version`, `schema_version` and structured `validation_errors`.
- Quota is consumed only after a valid accepted reading is persisted.

## Current State Evidence
- Evidence 1: `_story_briefs/cs-412-valider-et-reparer-narrative-basic-natal.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-417` after existing `CS-416`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - local IDs `RG-150`, `RG-152`, `RG-154`, `RG-155`, `RG-157` were checked.
- Evidence 4: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract applied.
- Evidence 5: `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md` - source plan confirms the validator stage.
- Evidence 6: `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py` - existing validator module exists.
- Evidence 7: `backend/app/services/llm_generation/natal/narrative_semantic_integrity.py` - semantic integrity module exists.
- Evidence 8: `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` - rejected answer audit workflow exists.
- Evidence 9: `backend/tests/unit/test_narrative_natal_reading_v1.py` - existing narrative tests are available for extension.
- Evidence 10: `backend/tests/unit/test_basic_natal_narrative_validator.py` - expected implementation-created path for Basic validator tests.

## Brief Primitive Ledger
| Primitive | Classification | Story mapping |
|---|---|---|
| `NarrativeDraft` | in scope | Objective, AC1 to AC8, Task 2 |
| `BasicNatalReadingPlan` | in scope | Objective, AC1, AC2, AC4, Task 1 |
| `NarrativeValidator` | in scope | Target state, AC1 to AC8, Task 2 |
| Structured `validation_errors` | in scope | AC9, Task 5, validation plan |
| Constrained repair prompt | in scope | AC10, Task 6 |
| Deterministic short fallback | in scope | AC11, Task 7 |
| `request_id` | in scope | AC9, Task 5 |
| `engine_version` | in scope | AC9, Task 5 |
| `schema_version` | in scope | AC9, Task 5 |
| Rejected public boundary | in scope | AC12, Task 8 |
| Quota consumption | in scope | AC13, Task 9 |
| Unexplained jargon | in scope | AC5, Task 4 |
| Unsupported vocation section | in scope | AC16, Task 4 |
| `/natal` page | out of scope | Non-goals |
| Plan builder rewrite | out of scope | Non-goals |
| Real provider calls in tests | out of scope | Non-goals |
| Basic complete V1/V2 acceptance | out of scope | Non-goals |
| Guardrail registry enrichment | in scope | AC15, Task 11, Regression Guardrails |

## Domain Boundary
- Domain: backend-domain
- In scope:
  - Backend post-generation validation for Basic natal narrative drafts.
  - Repair orchestration for invalid Basic natal drafts.
  - Deterministic fallback generation after repeated validation failure.
  - Rejected answer audit data and public boundary tests.
  - Quota acceptance timing proof for Basic natal generation.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling, migrations and provider-live tests.
  - Rewriting the Basic reading plan builder or changing `/natal`.
  - Quota policy changes beyond proving no consumption before valid acceptance.
- Explicit non-goals:
  - No frontend route, screen, client generation or UI validation.
  - No real provider call in automated tests.
  - No support for accepting Basic complete V1 or V2 schemas.

## Operation Contract
- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain validator and repair contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only Basic natal post-generation validation, repair, fallback and audit behavior.
  - Preserve public routes outside the rejected-output boundary.
  - Preserve quota policy except for proving consumption occurs after valid acceptance.
- Additional validation rules:
  - Runtime evidence must include `pytest -q backend/tests/unit/test_basic_natal_narrative_validator.py`.
  - Runtime evidence must include `pytest -q backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`.
  - Runtime evidence must include `pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`.
  - Static evidence must scan Basic natal generation code for technical markers and forbidden fallback padding.
  - `AST guard` coverage is required for public route boundary or acceptance-before-quota sequencing if tests cannot prove it directly.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: CS-410/CS-411 does not expose a usable `BasicNatalReadingPlan` contract at implementation time.

## Required Contracts
| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Targeted `pytest`, `TestClient` and audit tests prove accepted, rejected and quota behavior. |
| Baseline Snapshot | yes | Before and after validation artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Validator, semantic integrity, rejected audit and orchestration responsibilities must stay separated. |
| Allowlist Exception | yes | Empty register required because the story uses rejection and fallback vocabulary. |
| Contract Shape | yes | Validation errors, audit metadata and accepted narrative fields have exact required shapes. |
| Batch Migration | no | No batch migration or persisted data conversion is in scope. |
| Reintroduction Guard | yes | Technical markers, unsupported facts and padding patterns must stay rejected. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria
| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Missing requested Basic section is invalid. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_basic_natal_narrative_validator.py`. |
| AC2 | Unauthorized Basic section is invalid. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_basic_natal_narrative_validator.py`. |
| AC3 | Unsupported generated fact is invalid. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_basic_natal_narrative_validator.py`. |
| AC4 | Date-only draft cannot mention Ascendant. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_basic_natal_narrative_validator.py`. |
| AC5 | Technical score marker or unexplained jargon is invalid. | Evidence profile: targeted_scan; `pytest`; `rg` VC10. |
| AC6 | Mixed grammatical person is invalid. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_basic_natal_narrative_validator.py`. |
| AC7 | Prescriptive advice is invalid. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_basic_natal_narrative_validator.py`. |
| AC8 | Valid Basic draft keeps limitations. | Evidence profile: json_contract_shape; validator `pytest`. |
| AC9 | Rejection audit stores structured metadata. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_basic_natal_narrative_validator.py`. |
| AC10 | First invalid draft triggers constrained repair. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_basic_natal_narrative_validator.py`. |
| AC11 | Second invalid draft produces audited rejection or short fallback. | Evidence profile: json_contract_shape; `pytest` VC6 and VC7. |
| AC12 | Rejected Basic output stays audit-only. | Evidence profile: runtime_openapi_contract; `pytest` VC8; `TestClient`. |
| AC13 | Quota waits for valid acceptance. | Evidence profile: runtime_openapi_contract; `pytest` VC9. |
| AC14 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` VC12 checks evidence paths. |
| AC15 | Basic plan-backed validation has a durable registry guardrail. | Evidence profile: registry_guardrail; `rg` VC13. |
| AC16 | Unsupported vocation section is invalid. | Evidence profile: json_contract_shape; validator `pytest`. |
| AC17 | Valid Basic draft keeps disclaimers. | Evidence profile: json_contract_shape; validator `pytest`. |
| AC18 | Valid Basic draft keeps public sources. | Evidence profile: json_contract_shape; validator `pytest`. |

## Implementation Tasks
- [x] Task 1: Locate the final `BasicNatalReadingPlan` owner from CS-410/CS-411 before validator work starts. (AC: AC1, AC2, AC3, AC4)
- [x] Task 2: Extend or create Basic `NarrativeValidator` checks for sections, facts, tone, length, limitations, disclaimers, sources and advice. (AC: AC1, AC8, AC17, AC18)
- [x] Task 3: Add date-only rejection for Ascendant, MC, houses and house rulers when the plan does not authorize time-based facts. (AC: AC4)
- [x] Task 4: Reject scores, engine fields, unsupported jargon, raw audit markers and unsupported vocation sections. (AC: AC5, AC16)
- [x] Task 5: Emit structured `validation_errors` with `request_id`, `engine_version` and `schema_version` for invalid drafts. (AC: AC9)
- [x] Task 6: Add one constrained repair attempt that receives validation errors and the original reading plan. (AC: AC10)
- [x] Task 7: Add short deterministic fallback output only when it can satisfy the validator without semantic padding. (AC: AC11)
- [x] Task 8: Preserve rejected outputs in audit storage and outside public interpretation responses. (AC: AC12)
- [x] Task 9: Keep quota consumption after valid acceptance by extending existing quota-on-acceptance tests. (AC: AC13)
- [x] Task 10: Persist before and after validation examples plus validation output under the story evidence directory. (AC: AC14)
- [x] Task 11: Add the Basic plan-backed validation invariant to the regression guardrail registry. (AC: AC15)

## Files to Inspect First
- `_story_briefs/cs-412-valider-et-reparer-narrative-basic-natal.md`
- `_condamad/stories/CS-410-classifier-eligibilite-heure-naissance-basic/00-story.md`
- `_condamad/stories/CS-411-natal-fact-graph-basic-tracable/00-story.md`
- `_condamad/stories/CS-415-reading-plan-basic-natal-inspectable/00-story.md`
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`
- `backend/app/services/llm_generation/natal/narrative_semantic_integrity.py`
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/tests/unit/test_narrative_natal_reading_v1.py`
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`
- `backend/tests/unit/test_basic_natal_narrative_validator.py` - expected implementation-created path.

## Runtime Source of Truth
- Primary source of truth:
  - `BasicNatalReadingPlan`, `NarrativeDraft`, `NarrativeValidator`, rejected answer audit workflow, targeted `pytest` and `TestClient`.
- Secondary evidence:
  - Targeted `rg` scans for forbidden technical markers, score fields, padding patterns and public-route leakage.
- Static scans alone are not sufficient for this story because:
  - The repair, rejection, public boundary and quota timing behavior must be proven by executable backend tests.

## Contract Shape
- Contract type:
  - Backend domain validation result for Basic natal post-generation narrative output.
- Fields:
  - `is_valid`: boolean acceptance flag for the draft.
  - `validation_errors`: structured error codes describing invalid draft violations.
  - `request_id`: request correlation identifier copied into rejection audit.
  - `engine_version`: Basic engine version copied into rejection audit.
  - `schema_version`: Basic schema version copied into rejection audit.
  - `fallback_used`: boolean flag for deterministic fallback outcome.
- Required fields:
  - `is_valid`
  - `validation_errors`
  - `request_id`
  - `engine_version`
  - `schema_version`
- Optional fields:
  - `fallback_used`
- Forbidden accepted narrative fields:
  - `ranking_score`
  - `condition_axis`
  - `audit_input`
  - `visibility_expression`
  - raw evidence IDs
  - provider prompt internals
- Status codes:
  - none; this is not an API-route story.
- Serialization names:
  - Audit keys must remain `request_id`, `engine_version`, `schema_version` and `validation_errors`.
- Frontend type impact:
  - none; frontend projection is out of scope.
- Generated contract impact:
  - none; no OpenAPI or generated frontend client change is in scope.

## Baseline / Before-After Rule
- Baseline artifact before implementation:
  - `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/evidence/basic-validator-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/evidence/basic-validator-after.json`
- Expected invariant:
  - The only intended behavior delta is Basic natal post-generation validation, repair, fallback and audit handling.

## Ownership Routing Rule
| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Basic draft validation | `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py` | frontend code |
| Semantic support checks | `backend/app/services/llm_generation/natal/narrative_semantic_integrity.py` | route handlers |
| Rejected output audit | `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` | public serializers |
| Orchestration handoff | `backend/app/services/llm_generation/natal/interpretation_service.py` | provider adapter tests only |
| Quota acceptance timing | existing quota gate and interpretation service owner | validator module |

## Mandatory Reuse / DRY Constraints
- Reuse `BasicNatalReadingPlan` rather than rebuilding section, fact, limitation or source selection inside the validator.
- Reuse existing narrative semantic integrity helpers before adding new duplicate text scans.
- Reuse existing rejected answer workflow for audit persistence.
- Reuse existing quota-on-acceptance tests and entitlement gate patterns.
- Do not add external packages.
- Do not duplicate denylist tokens across production files when one canonical helper can own them.

## No Legacy / Forbidden Paths
- No legacy Basic validation path may accept draft facts that are absent from `BasicNatalReadingPlan`.
- No compatibility schema path may accept Basic complete V1 or V2 output for this story.
- No fallback path may pad missing sections with copied content or empty sources.
- No public route may expose rejected Basic narrative output.
- Forbidden accepted narrative markers include `ranking_score`, `condition_axis`, `audit_input`, `visibility_expression` and raw evidence IDs.
- Forbidden unsupported date-only facts include Ascendant, MC, houses, angularity and house rulers.

## Reintroduction Guard
- Guard exact forbidden accepted markers: `ranking_score`, `condition_axis`, `audit_input`, `visibility_expression`, `interpretive_signal_ids`.
- Guard exact forbidden date-only facts: `Ascendant`, `MC`, `maison`, `maisons`, `maitre de maison`, `angularite`.
- Guard exact padding pattern: `fallback = response.sections[0]`.
- Required deterministic guard:
  - `python -B -m pytest -q tests/unit/test_basic_natal_narrative_validator.py --tb=short`
  - `python -B -m pytest -q tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short`
  - `rg -n "fallback = response\\.sections\\[0\\]|ranking_score|condition_axis|audit_input" app/services/llm_generation/natal`

## Regression Guardrails
| Guardrail | Scope -> invariant -> evidence |
|---|---|
| RG-022 | prompt validation plan -> backend tests and scans stay explicit -> story `pytest` and `rg` evidence. |
| RG-150 | rejected output boundary -> invalid Basic drafts stay audit-only -> integration `pytest`. |
| RG-152 | public narrative contract -> accepted text hides technical markers -> validator `pytest` and `rg`. |
| RG-154 | public DOM denylist -> Basic technical markers cannot leak to public narrative -> DOM guard evidence. |
| RG-155 | semantic integrity -> no padding or empty-source fallback -> validator `pytest` and scan. |
| RG-157 | quota timing -> consumption waits for valid acceptance -> quota `pytest`. |
| RG-166 | Basic plan validation -> accepted Basic drafts must match `BasicNatalReadingPlan` -> validator tests and scans. |

Registry enrichment:
- `RG-166` records the durable Basic validator invariant requested by the brief.

Non-applicable examples:
- Database migration guardrails are not local because no schema or migration is in scope.
- Auth guardrails are not local because authentication behavior is unchanged.

## Persistent Evidence Artifacts
| Artifact | Path | Purpose |
|---|---|---|
| Before validator snapshot | `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/evidence/basic-validator-before.json` | Preserve baseline validator behavior. |
| After validator snapshot | `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/evidence/basic-validator-after.json` | Prove final validator behavior. |
| Validation output | `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/evidence/validation.txt` | Capture lint, tests and scans. |
| Review output | `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register
| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | No allowlist entry is authorized for Basic narrative validation. | Permanent: empty register. |

## Batch Migration Plan
- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify
Likely files:

- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py` - implement Basic plan-backed validation.
- `backend/app/services/llm_generation/natal/narrative_semantic_integrity.py` - reuse or extend semantic checks for unsupported claims.
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` - persist structured rejection audit metadata.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - orchestrate validation, repair, fallback, rejection and quota timing.
- `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/evidence/basic-validator-before.json` - persist baseline evidence.
- `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/evidence/basic-validator-after.json` - persist final evidence.
- `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/evidence/validation.txt` - persist command output.
- `_condamad/stories/regression-guardrails.md` - add the Basic plan-backed validation invariant.

Likely tests:

- `backend/tests/unit/test_basic_natal_narrative_validator.py` - expected implementation-created path for validator and repair tests.
- `backend/tests/unit/test_narrative_natal_reading_v1.py` - extend accepted public narrative technical-marker coverage.
- `backend/tests/unit/test_natal_interpretation_service_v3_schema_guard.py` - preserve Basic complete schema rejection behavior.
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` - prove rejected drafts stay off public routes.
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py` - prove quota consumption waits for valid acceptance.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/alembic/**` - out of scope; no migration is touched.
- `backend/app/infra/**` - out of scope unless existing audit repository imports require no-behavior wiring.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan
- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `python -B -m pytest -q tests/unit/test_basic_natal_narrative_validator.py --tb=short`
- VC6: `python -B -m pytest -q tests/unit/test_narrative_natal_reading_v1.py --tb=short`
- VC7: `python -B -m pytest -q tests/unit/test_natal_interpretation_service_v3_schema_guard.py --tb=short`
- VC8: `python -B -m pytest -q tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short`
- VC9: `python -B -m pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short`
- VC10: `rg -n "fallback = response\\.sections\\[0\\]|ranking_score|condition_axis|audit_input" app/services/llm_generation/natal`
- VC11: `rg -n "Ascendant|MC|maison|maisons|angularite" app/services/llm_generation/natal tests/unit/test_basic_natal_narrative_validator.py`
- VC12: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/evidence/validation.txt').exists()"`
- VC13: `rg -n "RG-166|Basic plan validation|BasicNatalReadingPlan" ../_condamad/stories/regression-guardrails.md`

`rg` scan contract:
- VC10 forbidden pattern: `fallback = response\.sections\[0\]|ranking_score|condition_axis|audit_input`.
- VC10 allowed fixture pattern: tests may mention tokens to prove rejection.
- VC10 scan roots: `app/services/llm_generation/natal`.
- VC10 expected false positives: validator denylist constants and test assertions for invalid draft rejection.
- VC11 forbidden pattern: `Ascendant|MC|maison|maisons|angularite` in date-only accepted narrative paths.
- VC11 allowed fixture pattern: tests and validator constants may mention tokens to prove date-only rejection.
- VC11 scan roots: `app/services/llm_generation/natal`, `tests/unit/test_basic_natal_narrative_validator.py`.
- VC11 expected false positives: eligibility checks, validator denylist constants and explicit rejection tests.

## Regression Risks
- Repair can become a second generation path that ignores the original reading plan.
- Deterministic fallback can recreate semantic padding instead of using only sourced public facts.
- Public route serializers can accidentally expose rejected Basic drafts.
- Quota can regress if consumption occurs before validation and persistence of an accepted reading.

## Dev Agent Instructions
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the venv before every Python command.
- Keep comments and docstrings in French for new or significantly modified backend files.
- Persist validation evidence under `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/evidence/`.

## References
- `_story_briefs/cs-412-valider-et-reparer-narrative-basic-natal.md`
- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `_condamad/stories/CS-410-classifier-eligibilite-heure-naissance-basic/00-story.md`
- `_condamad/stories/CS-411-natal-fact-graph-basic-tracable/00-story.md`
- `_condamad/stories/CS-415-reading-plan-basic-natal-inspectable/00-story.md`
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`
- `backend/app/services/llm_generation/natal/narrative_semantic_integrity.py`
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
