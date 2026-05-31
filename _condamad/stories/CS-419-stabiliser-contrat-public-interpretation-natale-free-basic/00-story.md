# Story CS-419 stabiliser-contrat-public-interpretation-natale-free-basic: Stabiliser Contrat Public Interpretation Natale Free Et Basic
Status: ready-to-review

## Trigger / Source
- Source brief: `_story_briefs/cs-419-stabiliser-contrat-public-interpretation-natale-free-basic.md`.
- Selected mode: Repo-informed story.
- Source dependencies: CS-416, CS-417 and CS-418 are complete upstream Basic V2 contract dependencies.
- Bounded problem: `/v1/natal/interpretation` is not explicit enough for the frontend to classify free short versus Basic V2 complete.
- Source-alignment evidence: objectives, stakes, ACs, tasks, validations, non-goals and guardrails map to the brief without scope drift.

## Objective
Stabilize the public backend contract returned by `/v1/natal/interpretation` for free short and Basic V2 complete natal readings.

## Target State
- Free short responses are classified as `meta.level=short` with `use_case=natal_interpretation_short`.
- Free short responses expose a readable `AstroFreeResponseV1` under `data.interpretation`.
- Free short `data.interpretation` keeps public title, summary, sections, highlights, advice and disclaimers.
- Free short responses do not require `narrative_natal_reading_v1`.
- Free short responses keep `data.basic_natal_interpretation_v2=null`.
- Basic complete responses expose non-null `data.basic_natal_interpretation_v2`.
- Basic complete responses expose `locale`, `level=basic`, `engine_version=basic-natal-reading-v1`,
  `schema_version=basic_natal_interpretation_v2`, taxonomy, salience, prompt and validator versions.
- Basic complete responses expose title, introduction, themes, conclusion, public evidence, limitations and disclaimers.
- Basic complete public payloads exclude technical markers, internal IDs, audit inputs, raw chart carriers and scoring fields.
- Root or payload disclaimers remain available with one coherent canonical source.
- Before and after snapshots document the expected public contract delta.

## Current State Evidence
- Evidence 1: `_story_briefs/cs-419-stabiliser-contrat-public-interpretation-natale-free-basic.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-419` after existing `CS-418`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract applied.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - targeted IDs `RG-150`, `RG-152`, `RG-154`, `RG-155`, `RG-164` through `RG-168` checked.
- Evidence 5: `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/00-story.md` - Basic payload dependency inspected.
- Evidence 6: `_condamad/stories/CS-418-integrer-basic-natal-v2-persistance-cache-qa/00-story.md` - Basic V2 runtime dependency inspected.
- Evidence 7: `_condamad/stories/CS-418-integrer-basic-natal-v2-persistance-cache-qa/evidence/basic-v2-runtime-after.json` - Basic V2 evidence inspected.
- Evidence 8: `backend/app/services/api_contracts/public/natal_interpretation.py` - public API response schema inspected.
- Evidence 9: `backend/app/services/llm_generation/natal/interpretation_service.py` - free short and Basic projection owner inspected.
- Evidence 10: `backend/app/services/llm_generation/natal/stored_interpretation_payload.py` - persisted payload loader inspected.
- Evidence 11: `backend/app/domain/astrology/reading/basic_natal_contracts.py` - Basic V2 public contract inspected.
- Evidence 12: `backend/tests/integration/test_basic_natal_v2_pipeline.py` - existing Basic V2 integration evidence inspected.
- Evidence 13: `python -B .agents\skills\condamad-story-writer\scripts\resolve_guardrails.py` - scoped resolver executed after venv activation.

Repository structure alert:
- `backend`, `backend/app` and `backend/tests` exist in this workspace.
- `backend/tests/integration/test_natal_interpretation_public_free_basic_contract.py` is expected to be created by implementation.

## Brief Primitive Ledger
| Primitive | Classification | Story mapping |
|---|---|---|
| `/v1/natal/interpretation` | in scope | AC1, AC5, Runtime Source of Truth |
| free short | in scope | AC1, AC2, AC3, AC4 |
| `natal_interpretation_short` | in scope | AC1, Contract Shape |
| `meta.level=short` | in scope | AC1, Contract Shape |
| `AstroFreeResponseV1` | in scope | AC2, AC3 |
| `data.interpretation` | in scope | AC2, AC9 |
| `narrative_natal_reading_v1` | constrained surface | AC4 |
| Basic complete | in scope | AC5, AC6, AC7, AC8 |
| `basic-natal-reading-v1` | in scope | AC6, Reintroduction Guard |
| `basic_natal_interpretation_v2` | in scope | AC5, AC6, AC7, AC14 |
| disclaimers | in scope | AC3, AC8 |
| technical fields denylist | forbidden surface | AC10, Reintroduction Guard |
| snapshots before/after | in scope | AC11, Persistent Evidence |
| frontend `/natal` rendering | out of scope | Non-goals |
| provider live call | out of scope | Non-goals |
| commercial rights | out of scope | Non-goals |
| persisted historical migration | out of scope | Non-goals |

## Domain Boundary
- Domain: backend-api
- In scope:
  - Backend public response contract for `POST /v1/natal/interpretation`.
  - Public serializer and persisted-payload loading for free short and Basic V2 complete readings.
  - Backend integration tests and snapshots proving the two public contract branches.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling, migrations and commercial entitlement rules.
  - Provider-live execution, historical data migration and `/natal` React rendering.
- Explicit non-goals:
  - No frontend route, screen, client generation or UI validation.
  - No provider-live test.
  - No migration of older persisted interpretations.
  - No change to quotas or commercial plan eligibility.

## Operation Contract
- Operation type: update
- Primary archetype: api-contract-change
- Archetype reason: the story stabilizes a public API route response contract with JSON shape and runtime evidence.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Update only the public natal interpretation contract and serializers for free short and Basic V2 complete outputs.
  - Preserve the existing route path, HTTP method, authentication behavior, entitlement policy and quota policy.
  - Keep `data.interpretation` present for free short compatibility.
  - Keep Basic V2 canonical content under `data.basic_natal_interpretation_v2`.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: frontend classification requires a new public field beyond existing `meta`, `interpretation` and Basic V2 payload keys.

## Required Contracts
| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, `TestClient` and integration `pytest` prove runtime API behavior. |
| Baseline Snapshot | yes | Before and after artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Public projection ownership must stay out of frontend heuristics. |
| Allowlist Exception | no | No allowlist handling is authorized for public payload leaks. |
| Contract Shape | yes | The route has exact JSON branch rules for free short and Basic V2 complete. |
| Batch Migration | no | No batch migration or stored-row conversion is in scope. |
| Reintroduction Guard | yes | Technical markers and alternate public classifications must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria
| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Free short returns `meta.level=short`. | Evidence profile: json_contract_shape; `pytest` VC5. |
| AC2 | Free short returns readable `AstroFreeResponseV1` content. | Evidence profile: json_contract_shape; `pytest` VC5. |
| AC3 | Free short exposes canonical disclaimers. | Evidence profile: json_contract_shape; `pytest` VC5. |
| AC4 | Free short does not require `narrative_natal_reading_v1`. | Evidence profile: json_contract_shape; `pytest` VC5. |
| AC5 | Basic complete returns non-null Basic V2 payload. | Evidence profile: json_contract_shape; `pytest` VC5. |
| AC6 | Basic complete returns the complete Basic V2 version block. | `TestClient`, `app.openapi()` and `pytest` VC5. |
| AC7 | Basic complete returns the required public synthesis body. | Evidence profile: json_contract_shape; `pytest` VC5. |
| AC8 | Basic complete exposes coherent public disclaimers. | Evidence profile: json_contract_shape; `pytest` VC5. |
| AC9 | `data.interpretation` remains a free compatibility surface. | Evidence profile: runtime_openapi_contract; `TestClient` and `pytest` in public contract tests. |
| AC10 | Accepted public payloads exclude technical markers. | Evidence profile: targeted_forbidden_symbol_scan; `rg` VC10 and backend `pytest` rejection tests. |
| AC11 | Before snapshot is persisted. | Evidence profile: baseline_before_after_diff; `python` VC11 checks evidence path. |
| AC12 | After snapshot is persisted. | Evidence profile: baseline_before_after_diff; `python` VC12 checks evidence path. |
| AC13 | Runtime API contract remains registered. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`. |
| AC14 | Free short keeps `data.basic_natal_interpretation_v2=null`. | Evidence profile: json_contract_shape; `pytest` VC5. |

## Implementation Tasks
- [ ] Task 1: Audit the free short projection from request through response serialization. (AC: AC1, AC2, AC3, AC4, AC14)
- [ ] Task 2: Correct free short metadata so the public response uses `meta.level=short`. (AC: AC1)
- [ ] Task 3: Preserve readable `AstroFreeResponseV1` content under `data.interpretation`. (AC: AC2, AC9)
- [ ] Task 4: Preserve free disclaimers without contradictory duplication. (AC: AC3)
- [ ] Task 5: Audit Basic complete projection from persisted payload and generation response. (AC: AC5, AC6, AC7, AC8)
- [ ] Task 6: Ensure Basic V2 remains the canonical public Basic payload. (AC: AC5, AC7)
- [ ] Task 7: Preserve Basic version metadata from `BasicNatalInterpretationV2`. (AC: AC6)
- [ ] Task 8: Add the new integration test for free short and Basic complete public branches. (AC: AC1, AC5, AC10)
- [ ] Task 9: Persist the baseline public response snapshot under the story evidence directory. (AC: AC11)
- [ ] Task 10: Persist the final public response snapshot under the story evidence directory. (AC: AC12)
- [ ] Task 11: Add route and OpenAPI runtime assertions for the public endpoint. (AC: AC13)
- [ ] Task 12: Run denylist scans and classify allowed guard hits. (AC: AC10)

## Files to Inspect First
- `_story_briefs/cs-419-stabiliser-contrat-public-interpretation-natale-free-basic.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/00-story.md`
- `_condamad/stories/CS-418-integrer-basic-natal-v2-persistance-cache-qa/00-story.md`
- `_condamad/stories/CS-418-integrer-basic-natal-v2-persistance-cache-qa/evidence/basic-v2-runtime-after.json`
- `backend/app/services/api_contracts/public/natal_interpretation.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/services/llm_generation/natal/stored_interpretation_payload.py`
- `backend/app/domain/astrology/reading/basic_natal_contracts.py`
- `backend/tests/integration/test_basic_natal_v2_pipeline.py`
- `backend/tests/integration/test_basic_natal_v2_cache_invalidation.py`
- `backend/tests/unit/test_basic_natal_reading_contracts.py`
- `backend/tests/architecture/test_basic_natal_reading_contract_boundaries.py`
- `backend/tests/unit/test_natal_interpretation_stored_payload.py`
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`
- `backend/tests/integration/test_natal_interpretation_public_free_basic_contract.py` - expected implementation-created path.

## Runtime Source of Truth
- Primary source of truth:
  - `app.routes`, `app.openapi()`, `TestClient`, public Pydantic response models and targeted `pytest`.
- Secondary evidence:
  - Targeted `rg` scans for technical markers in public contract, generation and Basic reading modules.
- Static scans alone are not sufficient for this story because:
  - Runtime serialization must prove both free short and Basic V2 complete branches from the loaded app.

## Contract Shape
- Contract type:
  - Public API response for `POST /v1/natal/interpretation`.
- Fields:
  - `data.meta.level`: `short` for free short, `complete` for Basic complete.
  - `data.use_case`: `natal_interpretation_short` for free short.
  - `data.interpretation`: readable `AstroFreeResponseV1` for free short.
  - `data.narrative_natal_reading_v1`: nullable for free short.
  - `data.basic_natal_interpretation_v2`: null for free short and non-null `BasicNatalInterpretationV2` for Basic complete.
  - `data.basic_natal_interpretation_v2.locale`: public Basic locale for Basic complete.
  - `data.basic_natal_interpretation_v2.level`: `basic` for Basic complete.
  - `data.basic_natal_interpretation_v2.engine_version`: `basic-natal-reading-v1` for Basic complete.
  - `data.basic_natal_interpretation_v2.schema_version`: `basic_natal_interpretation_v2` for Basic complete.
  - `data.basic_natal_interpretation_v2.*_version`: taxonomy, salience, prompt and validator versions for Basic complete.
  - `disclaimers`: public disclaimers list available at root.
- Required fields:
  - `data`
  - `data.meta`
  - `data.interpretation`
  - `disclaimers`
- Optional fields:
  - `data.narrative_natal_reading_v1`
  - `data.basic_natal_interpretation_v2`
  - `entitlement_info`
- Status codes:
  - Existing route status behavior remains unchanged for successful and rejected responses.
- Serialization names:
  - `basic_natal_interpretation_v2` is emitted as `basic_natal_interpretation_v2`.
  - `narrative_natal_reading_v1` is emitted as `narrative_natal_reading_v1`.
- Frontend type impact:
  - No frontend code change is in scope; backend response keys must give the frontend unambiguous branch selection.
- Generated contract impact:
  - `app.openapi()` must expose the public natal interpretation response schema for the existing route.

## Baseline / Before-After Rule
- Baseline artifact before implementation:
  - `_condamad/stories/CS-419-stabiliser-contrat-public-interpretation-natale-free-basic/evidence/public-contract-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-419-stabiliser-contrat-public-interpretation-natale-free-basic/evidence/public-contract-after.json`
- Expected invariant:
  - The only intended API surface delta is clearer classification and Basic V2 public payload stabilization.

## Ownership Routing Rule
| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Public response schema | `backend/app/services/api_contracts/public/natal_interpretation.py` | frontend branch heuristics |
| Free short projection | `backend/app/services/llm_generation/natal/interpretation_service.py` | React rendering code |
| Basic V2 payload loading | `backend/app/services/llm_generation/natal/stored_interpretation_payload.py` | route literals |
| Basic public contract | `backend/app/domain/astrology/reading/basic_natal_contracts.py` | API router local models |
| Public contract tests | `backend/tests/integration/test_natal_interpretation_public_free_basic_contract.py` | frontend tests |

## Mandatory Reuse / DRY Constraints
- Reuse `NatalInterpretationResponse`, `NatalInterpretationData` and `InterpretationMeta`.
- Reuse `AstroFreeResponseV1` for the free short public payload.
- Reuse `BasicNatalInterpretationV2` and its version constants for Basic complete.
- Reuse existing Basic V2 helpers and integration fixtures from CS-418 tests.
- Reuse the existing disclaimers registry.
- Do not add external packages.
- Do not duplicate denylist tokens across production files when a canonical helper can own them.

## No Legacy / Forbidden Paths
- No legacy complete classification may be used for the free short public response.
- No compatibility response field may become the canonical Basic V2 public contract.
- No fallback route or alternate endpoint may be added for this contract.
- Forbidden alternate public routes include `/v1/natal/interpretation/free`, `/v1/natal/basic` and `/v1/natal/complete`.
- Forbidden public markers include `ranking_score`, `condition_axis`, `score_profile`, `weighted_score`, `prompt_hint` and `audit_input`.
- Forbidden public raw carriers include `chart_json` and `natal_data`.

## Reintroduction Guard
- Guard exact public branch markers: `natal_interpretation_short`, `short`, `basic_natal_interpretation_v2`, `basic-natal-reading-v1`.
- Guard technical markers: `ranking_score`, `condition_axis`, `score_profile`, `weighted_score`, `prompt_hint`, `audit_input`, `chart_json`, `natal_data`.
- Required deterministic guard:
  - `python -B -m pytest -q tests/integration/test_natal_interpretation_public_free_basic_contract.py --tb=short`
  - `python -c "from app.main import app; assert any(getattr(r, 'path', '') == '/v1/natal/interpretation' for r in app.routes)"`
  - `python -c "from app.main import app; assert '/v1/natal/interpretation' in app.openapi()['paths']"`

## Regression Guardrails
| Guardrail | Scope -> invariant -> evidence |
|---|---|
| RG-150 | rejected boundary -> rejected payloads stay non-public -> stored-payload `pytest`. |
| RG-152 | public contract -> accepted readings hide technical data -> API `pytest` and `rg`. |
| RG-154 | DOM exposure via contract -> backend payload carries no DOM-denylisted markers -> API `pytest` and `rg`. |
| RG-155 | semantic integrity -> complete readings avoid padding and empty sources -> backend `pytest`. |
| RG-164 | Basic plan owner -> Basic selection stays plan-backed -> Basic V2 pipeline `pytest`. |
| RG-165 | Basic payload privacy -> provider and public payloads exclude private internals -> `pytest` and `rg`. |
| RG-166 | Basic validation -> accepted Basic drafts match the plan -> validator integration `pytest`. |
| RG-167 | Basic runtime engine -> Basic complete uses `basic-natal-reading-v1` -> Basic V2 `pytest`. |
| RG-168 | Basic public contract -> `BasicNatalInterpretationV2` stays canonical -> contract `pytest` and `rg`. |

Needs-investigation:
- Resolver returned `RG-002`, `RG-003` and `RG-007`; they are adjacent API guardrails, but the local invariants are the natal public contract IDs.
- `RG-154` is locally enforced only at backend contract level; full `/natal` DOM proof remains owned by CS-420.

Non-applicable examples:
- Frontend style guardrails are not local because no CSS or TSX change is in scope.
- Database migration guardrails are not local because no schema or stored-row batch conversion is in scope.
- Auth guardrails are not local because authentication behavior is unchanged.

Registry gap:
- No new durable invariant is added to `_condamad/stories/regression-guardrails.md` during this normal story generation.

## Persistent Evidence Artifacts
| Artifact | Path | Purpose |
|---|---|---|
| Before public snapshot | `evidence/public-contract-before.json` | Preserve baseline response shape in this story directory. |
| After public snapshot | `evidence/public-contract-after.json` | Prove final response shape in this story directory. |
| Validation output | `_condamad/stories/CS-419-stabiliser-contrat-public-interpretation-natale-free-basic/evidence/validation.txt` | Capture lint, tests and scans. |
| Review output | `generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register
- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for public payload leaks.

## Batch Migration Plan
- Batch migration plan: not applicable
- Reason: no batch migration or multi-record conversion is in scope.

## Expected Files to Modify
Likely files:

- `backend/app/services/api_contracts/public/natal_interpretation.py` - stabilize response schema and serialization.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - correct free short and Basic public projection.
- `backend/app/services/llm_generation/natal/stored_interpretation_payload.py` - preserve Basic V2 payload loading contract.
- `_condamad/stories/CS-419-stabiliser-contrat-public-interpretation-natale-free-basic/evidence/public-contract-before.json` - persist baseline evidence.
- `_condamad/stories/CS-419-stabiliser-contrat-public-interpretation-natale-free-basic/evidence/public-contract-after.json` - persist final evidence.
- `_condamad/stories/CS-419-stabiliser-contrat-public-interpretation-natale-free-basic/evidence/validation.txt` - persist command output.

Likely tests:

- `backend/tests/integration/test_natal_interpretation_public_free_basic_contract.py` - create public free and Basic branch tests.
- `backend/tests/integration/test_basic_natal_v2_pipeline.py` - preserve Basic V2 runtime no-regression.
- `backend/tests/integration/test_basic_natal_v2_cache_invalidation.py` - preserve compatible cache behavior.
- `backend/tests/unit/test_basic_natal_reading_contracts.py` - preserve Basic public contract validation.
- `backend/tests/architecture/test_basic_natal_reading_contract_boundaries.py` - preserve Basic contract ownership.
- `backend/tests/unit/test_natal_interpretation_stored_payload.py` - preserve stored payload boundary.
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` - preserve rejected payload boundary.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/alembic/**` - out of scope; no migration is touched.
- `backend/app/api/dependencies/auth.py` - out of scope; auth behavior is unchanged.
- `_condamad/stories/regression-guardrails.md` - out of scope for normal story generation.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan
- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `python -B -m pytest -q tests/integration/test_natal_interpretation_public_free_basic_contract.py --tb=short`
- VC6: `python -B -m pytest -q tests/integration/test_basic_natal_v2_pipeline.py --tb=short`
- VC7: `python -B -m pytest -q tests/integration/test_basic_natal_v2_cache_invalidation.py --tb=short`
- VC8: `python -B -m pytest -q tests/unit/test_basic_natal_reading_contracts.py tests/architecture/test_basic_natal_reading_contract_boundaries.py --tb=short`
- VC9: `python -B -m pytest -q tests/unit/test_natal_interpretation_stored_payload.py tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short`
- VC10: `rg` scan for public technical markers across public contract, natal generation and Basic reading roots.
- VC11: `python` checks `public-contract-before.json` in the story evidence directory.
- VC12: `python` checks `public-contract-after.json` in the story evidence directory.
- VC13: `python -c "from app.main import app; assert any(getattr(r, 'path', '') == '/v1/natal/interpretation' for r in app.routes)"`
- VC14: `python -c "from app.main import app; assert '/v1/natal/interpretation' in app.openapi()['paths']"`

`rg` scan contract:
- VC10 forbidden pattern: `ranking_score|condition_axis|score_profile|weighted_score|prompt_hint|audit_input|chart_json|natal_data`.
- VC10 allowed fixture pattern: denylist constants, validators, rejection tests and explicit guard assertions may mention forbidden tokens.
- VC10 scan roots: `app/services/api_contracts`, `app/services/llm_generation/natal`, `app/domain/astrology/reading`.
- VC10 expected false positives: validator denylist constants and tests proving public rejection.

## Regression Risks
- Free short can be misclassified as complete and trigger frontend regeneration messaging.
- Basic V2 can regress into a summary-only compatibility branch instead of the canonical public payload.
- Denylist markers can leak through nested public evidence or cached payload loading.
- Disclaimers can drift between root response and nested public payload.

## Dev Agent Instructions
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the venv before every Python command.
- Keep comments and docstrings in French for new or significantly modified backend files.
- Persist validation evidence under `_condamad/stories/CS-419-stabiliser-contrat-public-interpretation-natale-free-basic/evidence/`.
- Do not modify `_condamad/stories/regression-guardrails.md` during implementation.

## References
- `_story_briefs/cs-419-stabiliser-contrat-public-interpretation-natale-free-basic.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/00-story.md`
- `_condamad/stories/CS-418-integrer-basic-natal-v2-persistance-cache-qa/00-story.md`
- `_condamad/stories/CS-418-integrer-basic-natal-v2-persistance-cache-qa/evidence/basic-v2-runtime-after.json`
- `backend/app/services/api_contracts/public/natal_interpretation.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/services/llm_generation/natal/stored_interpretation_payload.py`
- `backend/app/domain/astrology/reading/basic_natal_contracts.py`
- `backend/tests/integration/test_basic_natal_v2_pipeline.py`
