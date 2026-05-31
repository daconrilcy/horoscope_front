# Story CS-416 contraindre-payload-llm-basic-par-reading-plan: Contraindre Payload LLM Basic Par Reading Plan
Status: done

## Trigger / Source
- Source brief: `_story_briefs/cs-411-contraindre-payload-llm-basic-par-reading-plan.md`.
- Source dependency: CS-410/CS-415 define `BasicNatalReadingPlan` as the upstream Basic narrative selection contract.
- Bounded problem: Basic natal provider payload can still be assembled from broad natal runtime data instead of the resolved reading plan.
- Source-alignment evidence: objectives, stakes, ACs, tasks, validations, non-goals and guardrails map to the brief without scope drift.

## Objective
Make `BasicNatalReadingPlan` the only narrative selection source for the Basic natal LLM payload sent to the provider.

## Target State
- `BasicNatalPromptPayload` is built from `BasicNatalReadingPlan`.
- The provider receives only selected facts, resolved syntheses, `editorial_evidence`, limitations, disclaimers and style constraints.
- The Basic prompt builder no longer uses raw `NatalResult` to select new narrative facts.
- Prompt-visible Basic natal payload excludes personal data, exact coordinates, internal IDs, internal scores and internal source paths.
- The Basic assembly instructs a 900 to 1300 word draft, six to eight sections maximum, `vous` tone, no firm prediction and no prescriptive advice.
- Existing Basic and Premium routes, provider calls and assemblies remain unchanged outside the Basic natal payload handoff.

## Current State Evidence
- Evidence 1: `_story_briefs/cs-411-contraindre-payload-llm-basic-par-reading-plan.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-416` after existing `CS-415`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - local IDs `RG-149`, `RG-152`, `RG-154`, `RG-156`, `RG-164`, `RG-165` were checked.
- Evidence 4: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract applied.
- Evidence 5: `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` - current provider payload owner exists.
- Evidence 6: `backend/app/services/llm_generation/natal/interpretation_service.py` - current natal generation service still carries chart JSON assembly paths.
- Evidence 7: `backend/tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py` - expected test file is absent and must be created.
- Evidence 8: source-alignment review confirms the story closes the brief objective without adding frontend, DB, provider-live or validator work.

## Brief Primitive Ledger
| Primitive | Classification | Story mapping |
|---|---|---|
| `BasicNatalReadingPlan` | in scope | Domain boundary, AC1, Task 1, validations |
| `BasicNatalPromptPayload` | in scope | Contract shape, AC2, Task 2 |
| Provider handoff | in scope | Runtime source of truth, AC3, Task 4 |
| `NatalResult` raw selection | forbidden source | AC4, Reintroduction Guard, static scans |
| personal data fields | forbidden payload surface | AC5, privacy scan |
| `editorial_evidence` | required payload surface | AC6, Contract shape |
| internal scores and source paths | forbidden payload surface | AC7, static scan |
| style constraints and disclaimers | required payload surface | AC8, seed or assembly test |
| `chart_json` and `natal_data` | forbidden prompt-visible carriers | AC9, regression guard |
| Basic/Premium routes and assemblies | unchanged adjacent surface | AC10, no-regression tests |
| post-generation validator | out of scope | Non-goals |
| frontend projection | out of scope | Non-goals |
| real provider call | out of scope | Non-goals |
| commercial Basic policy | out of scope | Non-goals |
| data migration | out of scope | Non-goals |

## Domain Boundary
- Domain: backend-domain
- In scope:
  - Backend LLM Basic natal payload builder from `BasicNatalReadingPlan`.
  - Provider payload contract for Basic natal generation.
  - Prompt seed or assembly constraints for Basic natal generation.
  - Unit and architecture tests proving the Basic payload boundary.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling, migrations and post-generation validator.
  - Premium narrative redesign, real provider execution, quota logic and commercial policy changes.
- Explicit non-goals:
  - No frontend route, screen, client generation or UI validation.
  - No provider-live test.
  - No migration of persisted natal readings.
  - No change to Premium payload selection beyond proving it still works.

## Operation Contract
- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain LLM payload contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the Basic natal payload path that derives prompt-visible content from `BasicNatalReadingPlan`.
  - Preserve existing Basic and Premium route contracts outside the provider payload content boundary.
  - Keep provider tests unit-level with no external provider call.
- Additional validation rules:
  - Runtime evidence must include `pytest -q backend/tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py`.
  - Runtime evidence must include an `AST guard` or equivalent architecture test for forbidden raw selection paths.
  - Static evidence must scan prompt-visible payload code for forbidden personal data and raw natal carriers.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: CS-410/CS-415 does not provide a usable `BasicNatalReadingPlan` contract at implementation time.

## Required Contracts
| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Runtime payload tests and `AST guard` prove the loaded Basic payload builder behavior. |
| Baseline Snapshot | yes | Before and after payload artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Canonical ownership is required because the payload path must not select facts in service code. |
| Allowlist Exception | no | No broad allowlist handling is authorized for this Basic payload handoff. |
| Contract Shape | yes | The provider payload has exact required and forbidden JSON fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Raw natal carriers and personal data must stay absent from prompt-visible payloads. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria
| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Basic payload selection is derived from `BasicNatalReadingPlan`. | Evidence profile: json_contract_shape; `pytest` VC5. |
| AC2 | `BasicNatalPromptPayload` exposes the expected narrative sections. | Evidence profile: json_contract_shape; `pytest` VC5. |
| AC3 | Provider handoff receives the Basic payload contract. | Evidence profile: json_contract_shape; `pytest` VC7. |
| AC4 | Raw `NatalResult` cannot select new Basic prompt facts. | Evidence profile: ast_architecture_guard; `pytest` VC6 and `AST guard`. |
| AC5 | Prompt-visible Basic payload excludes personal data. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans payload code and tests for privacy tokens. |
| AC6 | Prompt-visible Basic payload includes `editorial_evidence`. | Evidence profile: json_contract_shape; `pytest` VC5. |
| AC7 | Prompt-visible Basic payload excludes internal scores. | Evidence profile: forbidden_symbol_scan; `rg` VC9. |
| AC8 | Basic style constraints are sent to the prompt layer. | Evidence profile: json_contract_shape; `pytest` VC5. |
| AC9 | `chart_json` stays absent from prompt-visible Basic natal payloads. | Evidence profile: no_legacy_contract; `pytest` VC6. |
| AC10 | Existing Basic assembly remains usable. | Evidence profile: runtime_openapi_contract; `pytest` VC7. |
| AC11 | Existing Premium assembly remains usable. | Evidence profile: runtime_openapi_contract; `pytest` VC7. |
| AC12 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` VC10 checks evidence paths. |
| AC13 | Prompt-visible Basic payload excludes internal source paths. | Evidence profile: forbidden_symbol_scan; `rg` VC9. |
| AC14 | Prompt-visible Basic payload excludes raw evidence IDs. | Evidence profile: forbidden_symbol_scan; `rg` VC9. |

## Implementation Tasks
- [ ] Task 1: Locate or finish the `BasicNatalReadingPlan` import boundary from CS-410/CS-415 before payload work starts. (AC: AC1)
- [ ] Task 2: Add a Basic natal payload builder that maps plan sections, syntheses, limitations and style constraints. (AC: AC1, AC2, AC8)
- [ ] Task 3: Include only sanitized `editorial_evidence` in the provider-facing Basic payload. (AC: AC6, AC7, AC13, AC14)
- [ ] Task 4: Wire the Basic natal provider handoff to the plan-derived payload without calling a real provider in tests. (AC: AC3)
- [ ] Task 5: Add a privacy filter or serializer boundary for prompt-visible Basic payload fields. (AC: AC5)
- [ ] Task 6: Add a guard proving raw `NatalResult` is not used for Basic prompt fact selection. (AC: AC4)
- [ ] Task 7: Preserve `chart_json` and `natal_data` as non-prompt-visible for modern natal generation. (AC: AC9)
- [ ] Task 8: Update the Basic prompt seed or assembly constraints for length, section count, tone and advice limits. (AC: AC8)
- [ ] Task 9: Add focused unit and architecture tests for Basic payload shape, forbidden fields and assembly no-regression. (AC: AC1, AC3, AC10, AC11)
- [ ] Task 10: Persist before and after payload evidence plus validation output under the story evidence directory. (AC: AC12)

## Files to Inspect First
- `_story_briefs/cs-411-contraindre-payload-llm-basic-par-reading-plan.md`
- `_story_briefs/cs-410-construire-reading-plan-basic-natal-inspectable.md`
- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `_condamad/stories/CS-415-reading-plan-basic-natal-inspectable/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py`
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`
- `backend/tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py` - expected implementation-created path.

## Runtime Source of Truth
- Primary source of truth:
  - `BasicNatalReadingPlan`, `BasicNatalPromptPayload`, provider payload serialization, targeted `pytest` and `AST guard`.
- Secondary evidence:
  - Targeted `rg` scans for forbidden raw natal carriers, personal data, raw evidence IDs and internal fields.
- Static scans alone are not sufficient for this story because:
  - The final payload must be proven from executable builder tests and provider handoff tests.

## Contract Shape
- Contract type:
  - Backend domain JSON payload sent to the LLM provider for Basic natal drafting.
- Fields:
  - `sections`: planned Basic section payloads from `BasicNatalReadingPlan`.
  - `resolved_syntheses`: resolved narrative syntheses selected by the plan.
  - `editorial_evidence`: provider-visible evidence selected for drafting.
  - `limitations`: plan limitations carried into the prompt.
  - `disclaimers`: Basic natal disclaimers carried into the prompt.
  - `style_constraints`: word count, section count, tone and advice limits.
- Required fields:
  - `sections`
  - `resolved_syntheses`
  - `editorial_evidence`
  - `limitations`
  - `disclaimers`
  - `style_constraints`
- Optional fields:
  - none
- Forbidden prompt-visible fields:
  - `email`
  - `user_id`
  - `place_id`
  - `latitude`
  - `longitude`
  - `chart_json`
  - `natal_data`
  - `audit_input`
  - `ranking_score`
  - `weighted_score`
  - `score_profile`
  - internal source paths
  - raw evidence identifiers
- Status codes:
  - none; this is not an API-route story.
- Serialization names:
  - Provider payload keys must match the canonical Basic payload contract used by tests.
- Frontend type impact:
  - none; frontend projection is out of scope.
- Generated contract impact:
  - none; no OpenAPI or generated frontend client change is in scope.

## Baseline / Before-After Rule
- Baseline artifact before implementation:
  - `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/basic-payload-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/basic-payload-after.json`
- Expected invariant:
  - The only intended provider payload delta is the Basic natal prompt-visible content boundary.

## Ownership Routing Rule
| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Basic payload selection | `backend/app/domain/llm/runtime` or established LLM payload domain module | route handlers and frontend code |
| Reading plan contract | existing CS-410/CS-415 Basic reading plan module | prompt seed text |
| Prompt style constraints | `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py` or active assembly owner | provider adapter |
| Provider handoff wiring | `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` | UI projection |

## Mandatory Reuse / DRY Constraints
- Reuse `BasicNatalReadingPlan` rather than rebuilding selection, salience, theme resolution or synthesis resolution in the payload builder.
- Reuse existing provider payload assembly patterns in `ThemeAstralProviderPayloadBuilder`.
- Reuse existing test fixtures for natal provider payloads and architecture boundary guards.
- Do not add external packages.
- Do not duplicate privacy denylist tokens across production files when a canonical helper can own them.

## No Legacy / Forbidden Paths
- No legacy Basic payload path may select facts from raw `NatalResult`.
- No compatibility route, adapter or builder may preserve an alternate Basic prompt-visible carrier.
- No fallback payload may send `chart_json`, `natal_data`, personal data, internal IDs or internal scores to the provider.
- Forbidden prompt-visible surfaces include `email`, `user_id`, `place_id`, `latitude`, `longitude`, `audit_input` and source paths.
- Forbidden raw natal carriers include `chart_json` and `natal_data` for modern Basic natal provider payloads.

## Reintroduction Guard
- Guard exact forbidden payload fields: `chart_json`, `natal_data`, `email`, `user_id`, `place_id`, `latitude`, `longitude`, `audit_input`.
- Guard internal scoring symbols: `ranking_score`, `weighted_score`, `score_profile`, `condition_axis`, `prompt_hint`.
- Required deterministic guard:
  - `python -B -m pytest -q tests/architecture/test_llm_astrology_input_payload_boundaries.py --tb=short`
  - `rg -n "chart_json|natal_data|email|user_id|place_id|latitude|longitude" app/domain/llm app/services/llm_generation/natal`

## Regression Guardrails
| Guardrail | Scope -> invariant -> evidence |
|---|---|
| RG-002 | backend API adjacency -> route ownership stays unchanged -> targeted provider `pytest`. |
| RG-022 | prompt-generation story -> validation plan keeps backend tests and scans -> story `pytest` evidence. |
| RG-149 | modern natal prompt -> `chart_json` and `natal_data` stay non-prompt-visible -> architecture `pytest` and `rg`. |
| RG-152 | public narrative contract -> technical prompt data stays outside accepted reading text -> boundary `pytest`. |
| RG-154 | public denylist adjacency -> raw evidence IDs stay non-public -> targeted scans guard provider-to-public drift. |
| RG-156 | Basic coverage -> selected diversity remains plan-driven -> Basic payload `pytest`. |
| RG-164 | Basic plan owner -> `BasicNatalReadingPlan` owns Basic selection -> payload builder `pytest` and owner scan. |
| RG-165 | Basic payload privacy -> provider payload excludes PII/raw carriers/scores/paths/raw IDs -> payload `pytest` and `rg`. |

Registry enrichment:
- `RG-165` was added for the durable Basic provider payload privacy invariant requested by the brief.

Non-applicable examples:
- `RG-047` and `RG-052` are frontend style guardrails; no frontend files are in scope.
- Database migration guardrails are not local because no schema or migration is in scope.
- Auth guardrails are not local because authentication behavior is unchanged.

Registry alignment:
- `RG-165` closes the brief request for a durable Basic payload privacy invariant.

## Persistent Evidence Artifacts
| Artifact | Path | Purpose |
|---|---|---|
| Before payload snapshot | `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/basic-payload-before.json` | Preserve baseline Basic payload shape. |
| After payload snapshot | `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/basic-payload-after.json` | Prove final Basic payload shape. |
| Validation output | `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/validation.txt` | Capture lint, tests and scans. |
| Review output | `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register
- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this Basic payload handoff.

## Batch Migration Plan
- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify
Likely files:

- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` - wire plan-derived Basic payload into provider payload.
- `backend/app/domain/llm/configuration/theme_astral_contracts.py` - keep or extend Basic provider payload contract metadata.
- `backend/app/domain/llm/runtime/adapter.py` - preserve provider handoff boundary without raw prompt-visible carriers.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - route Basic handoff through the plan-derived payload.
- `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py` - align Basic prompt constraints for length, tone and advice limits.
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/basic-payload-before.json` - persist baseline evidence.
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/basic-payload-after.json` - persist final evidence.
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/validation.txt` - persist command output.

Likely tests:

- `backend/tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py` - expected implementation-created path for payload shape tests.
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` - extend forbidden payload carrier guard.
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` - preserve provider Basic/Premium handoff behavior.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/alembic/**` - out of scope; no migration is touched.
- `backend/app/infra/**` - out of scope unless existing imports require no-behavior wiring.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan
- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `python -B -m pytest -q tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py --tb=short`
- VC6: `python -B -m pytest -q tests/architecture/test_llm_astrology_input_payload_boundaries.py --tb=short`
- VC7: `python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py -k "natal or basic" --tb=short`
- VC8: `rg -n "chart_json|natal_data|email|user_id|place_id|latitude|longitude" app/domain/llm app/services/llm_generation/natal`
- VC9: `rg -n "ranking_score|condition_axis|score_profile|weighted_score|prompt_hint" app/domain/llm app/services/llm_generation/natal`
- VC10: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/validation.txt').exists()"`

`rg` scan contract:
- VC8 forbidden pattern: `chart_json|natal_data|email|user_id|place_id|latitude|longitude`.
- VC8 allowed fixture pattern: test denylist constants and assertions may mention forbidden tokens.
- VC8 scan roots: `app/domain/llm`, `app/services/llm_generation/natal`.
- VC8 expected false positives: existing non-prompt-visible runtime guards in provider gateway or architecture tests.
- VC9 forbidden pattern: `ranking_score|condition_axis|score_profile|weighted_score|prompt_hint`.
- VC9 allowed fixture pattern: tests may mention tokens to prove absence from prompt-visible payloads.
- VC9 scan roots: `app/domain/llm`, `app/services/llm_generation/natal`.
- VC9 expected false positives: internal calculation or guard constants outside prompt-visible serialization.

## Regression Risks
- The Basic payload may accidentally keep two narrative selection owners: the reading plan and a raw natal traversal path.
- Privacy can regress if provider handoff serializes broad context dictionaries instead of the plan-derived payload.
- Prompt quality can regress if style constraints are only stored in code comments rather than sent to the prompt layer.
- Premium can regress if common provider payload code changes without a focused Premium no-regression test.

## Dev Agent Instructions
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the venv before every Python command.
- Keep comments and docstrings in French for new or significantly modified backend files.
- Persist validation evidence under `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/`.

## References
- `_story_briefs/cs-411-contraindre-payload-llm-basic-par-reading-plan.md`
- `_story_briefs/cs-410-construire-reading-plan-basic-natal-inspectable.md`
- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `_condamad/stories/CS-415-reading-plan-basic-natal-inspectable/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py`
