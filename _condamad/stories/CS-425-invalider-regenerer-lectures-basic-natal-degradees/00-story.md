# Story CS-425 invalider-regenerer-lectures-basic-natal-degradees: Invalider Ou Regenerer Les Lectures Basic Natal Degradees
Status: ready-to-dev

## Trigger / Source
- Source brief: `_story_briefs/cs-425-invalider-regenerer-lectures-basic-natal-degradees.md`.
- Selected mode: Repo-informed story.
- Fast Story Writer Mode: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` applied first.
- Bounded problem: persisted Basic V2 rows can remain schema-compatible while carrying old editorial content that must not be served as complete.
- Source-alignment evidence: objective, ACs, tasks, validations, non-goals and guardrails map to the brief without narrowing the cache closure.

## Objective
Make Basic complete cache compatibility depend on schema, engine, editorial contract version and degraded-content detection.

## Target State
- A persisted Basic complete row carries a Basic editorial contract version owned by the backend Basic storage contract.
- The minimum compatible Basic editorial contract version is the version delivered after CS-421 and CS-424.
- Existing Basic rows without that version are classified as degraded for public cache reuse.
- Existing Basic rows with an older editorial version are classified as degraded for public cache reuse.
- Basic rows containing known degraded baseline tokens are classified as degraded even with a public schema-compatible payload.
- Degraded Basic rows reuse the existing corrective regeneration policy when eligibility is available.
- Non-regenerable degraded Basic rows return a controlled regeneration state and never appear as a complete valid reading.
- No batch migration path rewrites historical readings.

## Current State Evidence
- Evidence 1: `_story_briefs/cs-425-invalider-regenerer-lectures-basic-natal-degradees.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-425` after existing `CS-424`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted IDs were checked and `RG-172` was added for Basic cache reuse.
- Evidence 4: `backend/app/services/llm_generation/natal/stored_interpretation_payload.py` - current Basic V2 cache helper inspected.
- Evidence 5: `backend/app/services/llm_generation/natal/interpretation_service.py` - generation, cache and corrective policy owner inspected.
- Evidence 6: `backend/app/api/v1/routers/public/natal_interpretation.py` - quota acceptance boundary inspected.
- Evidence 7: `backend/tests/integration/test_basic_natal_v2_cache_invalidation.py` - current cache coverage inspected.
- Evidence 8: `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py` - corrective quota coverage inspected.
- Evidence 9: `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` - public boundary coverage inspected.
- Evidence 10: `_story_briefs/cs-421-renforcer-contrat-redactionnel-basic-natal.md` - editorial quality source inspected.
- Evidence 11: `_story_briefs/cs-424-verifier-corriger-generation-prompts-basic-natal.md` - final prompt source inspected.
- Evidence 12: `_story_briefs/cs-398-rendre-quota-natal-complete-transactionnel-et-remedier-lectures-invalides.md` - fallback source used.
- Evidence 13: `python -B .agents\skills\condamad-story-writer\scripts\resolve_guardrails.py` - scoped resolver executed after venv activation.

Repository structure alert:
- `backend`, `backend/app`, `backend/tests`, `frontend` and `frontend/src` exist in this workspace.
- The source path `_condamad/stories/CS-398-rendre-quota-natal-complete-transactionnel-et-remedier-lectures-invalides/00-story.md` is missing.
- The implementation must use `_story_briefs/cs-398-rendre-quota-natal-complete-transactionnel-et-remedier-lectures-invalides.md` as the CS-398 source.

## Brief Primitive Ledger
| Primitive | Classification | Story mapping |
|---|---|---|
| `basic_editorial_contract_version` | in scope | AC1, AC2, Task 1, Contract Shape |
| minimum compatible editorial version | in scope | AC2, Task 2, Validation Plan |
| Basic row without editorial version | in scope | AC3, Task 3 |
| Basic row with old editorial version | in scope | AC4, Task 3 |
| baseline degraded tokens | in scope | AC5, Task 4 |
| compatible clean Basic cache | in scope | AC6, Task 5 |
| corrective regeneration policy | in scope | AC7, Task 6 |
| non-regenerable controlled state | in scope | AC8, Task 7 |
| quota before acceptance | in scope | AC9, Task 8 |
| public rejected boundary | in scope | AC10, Task 9 |
| before-after user snapshot | in scope | AC11, Task 10 |
| batch migration | out of scope | Non-goals, Batch Migration Plan |
| provider live call in tests | out of scope | Non-goals |
| broad frontend redesign | out of scope | Non-goals |
| guardrail registry enrichment | in scope | `RG-172` added for Basic cache editorial compatibility |

## Domain Boundary
- Domain: backend-domain
- In scope:
  - Backend Basic complete cache compatibility and persistence metadata.
  - Backend degraded-content classification for persisted Basic V2 readings.
  - Existing corrective regeneration and quota-on-acceptance policy.
  - Public API controlled state for degraded Basic readings that cannot regenerate.
  - Backend tests, targeted scans and persisted evidence snapshots.
- Out of scope:
  - Frontend redesign, auth, i18n, styling, build tooling, migrations, provider live calls and mass data migration.
  - New commercial quota limits or plan entitlement changes.
- Explicit non-goals:
  - No batch rewrite of historical Basic readings.
  - No quota debit before a new valid reading is accepted.
  - No public exposure of audit rows, internal carriers, raw IDs or rejected payloads.
  - No second Basic cache policy outside the canonical storage and interpretation service owners.

## Operation Contract
- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend cache, persistence and corrective-regeneration contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only Basic editorial contract compatibility to Basic complete cache reuse.
  - Preserve `basic_natal_interpretation_v2` as the public Basic V2 contract.
  - Preserve `basic-natal-reading-v1` as the Basic complete engine.
  - Preserve corrective regeneration and quota-on-acceptance behavior from CS-398.
  - Preserve public rejected-boundary behavior from CS-384 and later guardrails.
- Additional validation rules:
  - Runtime evidence must include `pytest -q backend/tests/integration/test_basic_natal_v2_cache_invalidation.py`.
  - Runtime evidence must include `pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`.
  - Runtime evidence must include `pytest -q backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`.
  - Runtime evidence must include `TestClient` coverage or service-level integration for the controlled non-regenerable state.
  - Static evidence must scan Basic storage and tests for editorial version markers and degraded baseline tokens.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: CS-421 or CS-424 remains unavailable when implementation starts.

## Required Contracts
| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, service integration and `TestClient` prove cache, regeneration and public API behavior. |
| Baseline Snapshot | yes | Before and after artifacts prove degraded cache no longer appears complete. |
| Ownership Routing | yes | Cache classification, persistence metadata and quota boundaries require canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for degraded Basic public reuse. |
| Contract Shape | yes | Basic editorial metadata and controlled state have exact fields. |
| Batch Migration | no | Mass rewrite or progressive conversion is out of scope. |
| Reintroduction Guard | yes | Old editorial rows and baseline degraded tokens must stay unservable as complete. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria
| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Accepted Basic rows persist editorial version. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_basic_natal_v2_cache_invalidation.py`. |
| AC2 | The minimum editorial version is enforced. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_basic_natal_v2_cache_invalidation.py`. |
| AC3 | No editorial version invalidates cache. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_basic_natal_v2_cache_invalidation.py`. |
| AC4 | Older editorial version invalidates cache reuse. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_basic_natal_v2_cache_invalidation.py`. |
| AC5 | Degraded baseline tokens invalidate cache reuse. | Evidence profile: targeted_forbidden_symbol_scan; `pytest`; `rg` scans backend Basic code and tests. |
| AC6 | Compatible clean Basic cache is served. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/integration/test_basic_natal_v2_cache_invalidation.py`. |
| AC7 | Eligible degraded cache regenerates. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/integration/test_basic_natal_v2_cache_invalidation.py`. |
| AC8 | Non-regenerable degraded cache returns a controlled state. | Evidence profile: runtime_openapi_contract; `TestClient`; `pytest` integration coverage. |
| AC9 | Corrective regeneration preserves quota timing. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`. |
| AC10 | Rejected outputs remain hidden. | Evidence profile: runtime_openapi_contract; `tests/integration/test_natal_interpretation_rejected_public_boundary.py`. |
| AC11 | Before-after degraded cache evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |
| AC12 | No batch migration path is introduced. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks backend migration and script roots. |
| AC13 | Story validation evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks validation artifact paths. |

## Implementation Tasks
- [ ] Task 1: Add a canonical Basic editorial contract version field or metadata owner for accepted Basic rows. (AC: AC1)
- [ ] Task 2: Declare the minimum compatible editorial version that represents the CS-421 and CS-424 contract. (AC: AC2)
- [ ] Task 3: Classify Basic rows without that version or with an older version as degraded for cache reuse. (AC: AC3, AC4)
- [ ] Task 4: Centralize degraded baseline token detection without duplicating token lists across production modules. (AC: AC5)
- [ ] Task 5: Preserve clean compatible Basic cache reads without gateway calls or quota debit. (AC: AC6)
- [ ] Task 6: Reuse the existing corrective regeneration policy for eligible degraded Basic cache rows. (AC: AC7, AC9)
- [ ] Task 7: Return a controlled regeneration state for degraded Basic rows that cannot regenerate. (AC: AC8)
- [ ] Task 8: Extend quota tests so corrective Basic regeneration keeps debit after valid acceptance only. (AC: AC9)
- [ ] Task 9: Extend public-boundary tests so degraded or rejected Basic content never appears as complete. (AC: AC10)
- [ ] Task 10: Persist before-after evidence for an example degraded Basic cache row or equivalent fixture. (AC: AC11, AC13)
- [ ] Task 11: Add targeted scans proving no batch migration path or duplicate cache policy was introduced. (AC: AC12)

## Files to Inspect First
- `_story_briefs/cs-425-invalider-regenerer-lectures-basic-natal-degradees.md`
- `_story_briefs/cs-398-rendre-quota-natal-complete-transactionnel-et-remedier-lectures-invalides.md`
- `_condamad/stories/CS-418-integrer-basic-natal-v2-persistance-cache-qa/00-story.md`
- `_story_briefs/cs-421-renforcer-contrat-redactionnel-basic-natal.md`
- `_story_briefs/cs-424-verifier-corriger-generation-prompts-basic-natal.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/services/llm_generation/natal/stored_interpretation_payload.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/app/domain/astrology/reading/basic_natal_contracts.py`
- `backend/tests/integration/test_basic_natal_v2_cache_invalidation.py`
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`

## Runtime Source of Truth
- Primary source of truth:
  - `UserNatalInterpretationModel`, Basic stored payload helpers, `NatalInterpretationService`, `TestClient` and targeted `pytest`.
- Secondary evidence:
  - Targeted `rg` scans for editorial version markers, degraded baseline tokens, quota calls and batch migration surfaces.
- Static scans alone are not sufficient for this story because:
  - Cache reuse, corrective regeneration, quota timing and controlled public state must be proven from executable runtime tests.

## Contract Shape
- Contract type:
  - Persisted Basic complete cache compatibility metadata and public controlled regeneration state.
- Fields:
  - `basic_editorial_contract_version`: literal version marker for the accepted Basic editorial contract.
  - `engine_version`: literal `basic-natal-reading-v1`.
  - `schema_version`: literal `basic_natal_interpretation_v2`.
  - `degraded_reason`: internal classification code, not public reading prose.
  - `regeneration_state`: controlled public state for non-regenerable degraded cache.
- Required fields:
  - `basic_editorial_contract_version` on newly accepted Basic rows.
  - `engine_version`
  - `schema_version`
- Optional fields:
  - `degraded_reason` for internal evidence, audit or tests.
  - `regeneration_state` only for the controlled non-regenerable response.
- Forbidden public fields:
  - `ranking_score`
  - `condition_axis`
  - `score_profile`
  - `weighted_score`
  - `prompt_hint`
  - `audit_input`
  - `chart_json`
  - `natal_data`
  - `degraded_reason`
- Status codes:
  - Existing public route status behavior remains unchanged unless the controlled state already uses a documented error status.
- Serialization names:
  - `basic_editorial_contract_version` stays the canonical version metadata name unless implementation records a documented equivalent.
- Frontend type impact:
  - No broad frontend change is planned; only an existing controlled regeneration state may be surfaced.
- Generated contract impact:
  - No generated client change is required unless implementation already generates frontend types from backend contracts.

## Baseline / Before-After Rule
- Baseline artifact before implementation:
  - `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/evidence/basic-cache-degraded-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/evidence/basic-cache-degraded-after.json`
- Expected invariant:
  - The only intended behavior delta is stricter Basic cache compatibility for editorial version and degraded-content detection.

## Ownership Routing Rule
| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Basic cache compatibility | `backend/app/services/llm_generation/natal/stored_interpretation_payload.py` | route handler literals |
| Basic generation cache decision | `backend/app/services/llm_generation/natal/interpretation_service.py` | frontend source |
| Corrective quota timing | `backend/app/api/v1/routers/public/natal_interpretation.py` and entitlement gate | provider adapter |
| Public Basic contract | `backend/app/domain/astrology/reading/basic_natal_contracts.py` | DB model helpers |
| Degraded token policy | canonical backend Basic validation or storage helper | duplicated module-level lists |
| Evidence snapshots | `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/evidence/` | production code |

## Mandatory Reuse / DRY Constraints
- Reuse `BasicNatalInterpretationV2` and existing Basic V2 payload helpers.
- Reuse `basic-natal-reading-v1` and `basic_natal_interpretation_v2` version markers.
- Reuse CS-398 corrective regeneration and quota-on-acceptance policy.
- Reuse CS-421 degraded editorial token expectations rather than creating a second denylist family.
- Reuse CS-424 prompt-final compatibility outcome for the minimum editorial version.
- Do not add external packages.
- Do not duplicate degraded token lists across production modules.
- Keep the classification helper small and focused on Basic cache compatibility.

## No Legacy / Forbidden Paths
- No legacy Basic cache rule may serve Basic rows missing the editorial version.
- No compatibility cache rule may serve Basic rows with an older editorial version.
- No fallback route or frontend path may display degraded Basic content as a complete reading.
- No batch migration script may rewrite historical readings for this story.
- No public response may expose rejected output, `chart_json`, `natal_data`, internal scores, raw evidence identifiers or `degraded_reason`.
- Forbidden baseline tokens include `cette lecture s'appuie uniquement`, `Ce repere retient` and `avec une confiance editoriale controlee`.
- Forbidden raw labels include `Luminaire: moon`, `Position planetaire:`, `north node` and `south node`.

## Reintroduction Guard
- Guard exact version markers: `basic_editorial_contract_version`, `basic-natal-reading-v1`, `basic_natal_interpretation_v2`.
- Guard degraded baseline tokens in Basic cache tests and validation helpers.
- Guard quota boundary by keeping `check_and_consume` absent from the public natal route.
- Guard public boundaries so rejected or degraded payloads are not listed or fetched as complete valid readings.
- Required deterministic guard:
  - `python -B -m pytest -q tests/integration/test_basic_natal_v2_cache_invalidation.py --tb=short`
  - `python -B -m pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short`
  - `python -B -m pytest -q tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short`
  - `rg -n "check_and_consume" app/api/v1/routers/public/natal_interpretation.py`

## Regression Guardrails
| Guardrail | Scope -> invariant -> evidence |
|---|---|
| RG-150 | rejected boundary -> rejected Basic payloads stay audit-only -> integration `pytest`. |
| RG-152 | public contract -> Basic complete excludes internal carriers -> boundary `pytest` and `rg`. |
| RG-155 | semantic integrity -> degraded text cannot pass as complete -> cache `pytest` and token `rg`. |
| RG-157 | quota timing -> corrective regeneration does not debit early -> quota `pytest` and route `rg`. |
| RG-164 | Basic plan owner -> cache policy does not create a second Basic engine -> marker `rg`. |
| RG-165 | payload privacy -> Basic payload excludes PII, scores and raw IDs -> contract `pytest` and `rg`. |
| RG-166 | validation -> accepted Basic drafts remain plan-backed -> existing Basic validation `pytest`. |
| RG-167 | runtime engine -> Basic complete reuses `basic-natal-reading-v1` only -> cache `pytest` and `rg`. |
| RG-168 | public Basic V2 -> `BasicNatalInterpretationV2` remains canonical -> contract `pytest` and `rg`. |
| RG-172 | cache compatibility -> Basic cache requires current editorial version and clean baseline tokens -> cache `pytest` and `rg`. |

Needs-investigation:
- `RG-169` and `RG-171` are cited by source briefs but are absent from the current registry; this is not story-blocking.
- Resolver output included `RG-002`, `RG-003`, `RG-007` and `RG-022`; they are adjacent backend/API validation guardrails, not the local invariant core.

Non-applicable examples:
- Frontend style guardrails are not local because no CSS or TSX styling change is planned.
- DB migration guardrails are not local because batch migration is out of scope.
- Auth guardrails are not local because authentication behavior is unchanged.

## Persistent Evidence Artifacts
| Artifact | Path | Purpose |
|---|---|---|
| Before snapshot | `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/evidence/basic-cache-degraded-before.json` | Preserve degraded cache baseline. |
| After snapshot | `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/evidence/basic-cache-degraded-after.json` | Prove degraded cache is not complete. |
| QA report | `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/evidence/qa-report.md` | Separate compatible cache and regeneration states. |
| Validation output | `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/evidence/validation.txt` | Capture lint, tests and scans. |
| Review output | `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register
- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for degraded Basic public reuse.

## Batch Migration Plan
- Batch migration plan: not applicable
- Reason: no batch migration or multi-record conversion is in scope.

## Expected Files to Modify
Likely files:

- `backend/app/services/llm_generation/natal/stored_interpretation_payload.py` - add Basic editorial compatibility helper.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - apply degraded-cache classification and controlled state.
- `backend/app/api/v1/routers/public/natal_interpretation.py` - preserve quota release and consume-on-acceptance behavior.
- `backend/app/domain/astrology/reading/basic_natal_contracts.py` - expose canonical Basic editorial version metadata if owned there.
- `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/evidence/basic-cache-degraded-before.json` - persist baseline.
- `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/evidence/basic-cache-degraded-after.json` - persist final evidence.
- `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/evidence/qa-report.md` - persist QA notes.
- `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/evidence/validation.txt` - persist command output.

Likely tests:

- `backend/tests/integration/test_basic_natal_v2_cache_invalidation.py` - extend missing version, old version and degraded token cases.
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py` - preserve corrective regeneration quota timing.
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` - preserve public hidden degraded or rejected rows.

Files not expected to change:

- `backend/alembic/**` - out of scope; no migration is touched.
- `backend/app/api/dependencies/auth.py` - out of scope; auth behavior is unchanged.
- `frontend/src/**` - out of scope unless the existing controlled regeneration state contract already requires a minimal display hook.
- `_condamad/stories/regression-guardrails.md` - `RG-172` was added for Basic cache editorial compatibility.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan
- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `python -B -m pytest -q tests/integration/test_basic_natal_v2_cache_invalidation.py --tb=short`
- VC6: `python -B -m pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short`
- VC7: `python -B -m pytest -q tests/integration/test_basic_natal_v2_pipeline.py tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short`
- VC8: `rg -n "check_and_consume" app/api/v1/routers/public/natal_interpretation.py`
- VC9: `rg -n "basic_editorial_contract_version|basic-natal-editorial" app tests`
- VC10: `rg -n "cette lecture s'appuie uniquement|Ce repere retient|avec une confiance editoriale controlee" app tests`
- VC11: `rg -n "Luminaire: moon|Position planetaire:|north node|south node" app tests`
- VC12: `rg -n "batch.*basic|migration.*basic|alembic.*basic" app tests alembic`
- VC13: `cd ..`
- VC14: `cd _condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees`
- VC15: `python -c "from pathlib import Path; assert Path('evidence/basic-cache-degraded-after.json').exists()"`
- VC16: `python -c "from pathlib import Path; assert Path('evidence/validation.txt').exists()"`

`rg` scan contracts:

- VC8 forbidden pattern: `check_and_consume`.
- VC8 allowed fixture pattern: none.
- VC8 roots: `app/api/v1/routers/public/natal_interpretation.py`.
- VC8 expected false positives: none; zero-hit is expected.
- VC9 forbidden pattern: missing Basic editorial version marker in final Basic compatibility code.
- VC9 allowed fixture pattern: tests and evidence artifacts may mention the marker.
- VC9 roots: `app`, `tests`.
- VC9 expected false positives: none; hits are required in implementation and tests.
- VC10 forbidden pattern: degraded baseline prose tokens in public-producing code.
- VC10 allowed fixture pattern: denylist constants, negative tests and evidence historical fixtures.
- VC10 roots: `app`, `tests`.
- VC10 expected false positives: negative tests and canonical denylist helper.
- VC11 forbidden pattern: degraded raw labels in public-producing code.
- VC11 allowed fixture pattern: denylist constants, negative tests and evidence historical fixtures.
- VC11 roots: `app`, `tests`.
- VC11 expected false positives: negative tests and canonical denylist helper.
- VC12 forbidden pattern: batch migration path for Basic historical readings.
- VC12 allowed fixture pattern: story or test text proving migration remains out of scope.
- VC12 roots: `app`, `tests`, `alembic`.
- VC12 expected false positives: none in implementation code; tests may assert absence.

## Regression Risks
- Basic cache can remain schema-valid while serving pre-CS-421 or pre-CS-424 mechanical text.
- Editorial version metadata can be attached to public payload in a way that leaks internal classification.
- Corrective regeneration can accidentally debit quota before a new valid Basic row is accepted.
- Controlled non-regenerable state can be mistaken for a complete reading by the public route.
- Token detection can be duplicated across production modules and drift from validator expectations.

## Dev Agent Instructions
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the venv before every Python command.
- Keep comments and docstrings in French for new or significantly modified backend files.
- Keep frontend styles in CSS files, not inline style attributes.
- Persist validation evidence under `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/evidence/`.
- Do not modify `_condamad/stories/regression-guardrails.md` during implementation unless new registry maintenance is authorized.

## References
- `_story_briefs/cs-425-invalider-regenerer-lectures-basic-natal-degradees.md`
- `_story_briefs/cs-398-rendre-quota-natal-complete-transactionnel-et-remedier-lectures-invalides.md`
- `_condamad/stories/CS-418-integrer-basic-natal-v2-persistance-cache-qa/00-story.md`
- `_story_briefs/cs-421-renforcer-contrat-redactionnel-basic-natal.md`
- `_story_briefs/cs-424-verifier-corriger-generation-prompts-basic-natal.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/services/llm_generation/natal/stored_interpretation_payload.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/tests/integration/test_basic_natal_v2_cache_invalidation.py`
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`
