# Story CS-412 prioriser-faits-natals-basic-salience-calibree: Prioriser Faits Natals Basic Par Salience Calibree
Status: ready-to-dev

## Trigger / Source
- Source brief: `_story_briefs/cs-407-prioriser-faits-natals-basic-par-salience-calibree.md`.
- Selected mode: Repo-informed story.
- Source dependency: CS-411 `NatalFactGraph` must be implemented before this story is executed.
- Bounded problem: Basic needs deterministic salience so spectacular secondary facts cannot outrank natal pillars.
- Source-alignment evidence: objectives, risks, ACs, tests, guardrails and non-goals map to the brief without scope drift.

## Objective
Create `NatalSalienceModel` for Basic natal facts so each eligible `NatalFactGraph` fact receives calibrated priority metadata without public scoring leaks.

## Target State
- `NatalSalienceModel` consumes `NatalFactGraph` and `EligibilityContext` from the backend domain.
- Each included fact receives `salience_score`, `salience_level` and stable `reason_codes`.
- Each excluded Basic fact receives a deterministic `exclusion_reason`.
- The scoring model is deterministic, configurable and versioned.
- The model protects Sun, Moon and eligible Ascendant as natal pillars.
- Minor points, technical dignity details and forbidden Basic signals stay non-central.
- A minimal anonymized archetype corpus covers contrasted natal profiles.
- Internal audit evidence records salience decisions without exposing scores in public contracts.

## Current State Evidence
- Evidence 1: `_story_briefs/cs-407-prioriser-faits-natals-basic-par-salience-calibree.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-412`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted IDs `RG-144` to `RG-148`, `RG-151`, `RG-156`, `RG-160`, `RG-161` read.
- Evidence 4: `python -B .agents\skills\condamad-story-writer\scripts\resolve_guardrails.py` - scoped resolver executed.
- Evidence 5: `_condamad/stories/CS-411-natal-fact-graph-basic-tracable/00-story.md` - dependency contract inspected.
- Evidence 6: `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` - public projection boundary inspected.
- Evidence 7: `backend/app/domain/astrology/interpretation_adapters/signal_builder.py` - existing runtime signal builder inspected.
- Evidence 8: `backend/tests/fixtures/golden/natal_test.yaml` and `backend/tests/fixtures/golden/natal_premium_test.yaml` - golden fixture shape inspected.

Repository structure alert:
- `backend` exists in this workspace.
- Expected new files may still need to be created by implementation under existing backend directories.

## Brief Primitive Ledger
| Primitive | Classification | Story mapping |
|---|---|---|
| `NatalSalienceModel` | in scope | AC1, AC2, AC3, AC4, Task 1 |
| `NatalFactGraph` | in scope dependency | AC1, AC5, Task 2, Files to Inspect First |
| `EligibilityContext` | in scope | AC4, AC7, Task 2 |
| `salience_score` | in scope | AC1, AC8, Task 1 |
| `salience_level` | in scope | AC2, Task 1 |
| `reason_codes` | in scope | AC3, Task 3 |
| `exclusion_reason` | in scope | AC4, AC11, Task 4 |
| luminaries | in scope | AC5, AC6, Task 5 |
| eligible Ascendant | in scope | AC7, Task 5 |
| angularity | in scope | AC8, Task 5 |
| dominant house | in scope | AC10, Task 6 |
| dominant planet | in scope | AC12, Task 6 |
| strong dignity | in scope | AC12, Task 6 |
| strong constraint | in scope | AC12, Task 6 |
| exact aspect | in scope | AC9, Task 6 |
| thematic repetition | in scope | AC10, Task 6 |
| archetype corpus | in scope | AC12, Task 7 |
| golden chart expected facts | in scope | AC13, Task 7 |
| public scores | forbidden | AC14, Non-goals, Reintroduction Guard |
| narrative theme construction | out of scope | Explicit non-goals |
| contradiction fusion | out of scope | Explicit non-goals |
| final section order | out of scope | Explicit non-goals |
| astrology calculation | out of scope | Explicit non-goals |
| prompt changes | out of scope | Explicit non-goals |

## Domain Boundary
- Domain: backend-domain
- In scope:
  - Backend domain salience scoring for Basic natal facts.
  - Internal audit rows for salience decisions.
  - Unit fixtures and factories for contrasted Basic archetypes.
  - Regression guards proving public payloads do not expose salience internals.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling, migrations, prompts and public narrative rendering.
- Explicit non-goals:
  - No narrative theme builder.
  - No contradiction fusion.
  - No final section ordering.
  - No new astrology calculations.
  - No prompt modification.
  - No public score exposure.

## Operation Contract
- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain salience contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only deterministic Basic natal salience metadata from existing fact graph inputs.
  - Keep public projections free of internal salience scores.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-411 does not expose `NatalFactGraph` or `EligibilityContext`.

Additional validation rules:
- Runtime evidence must include concrete `pytest -q backend/tests` paths.
- Architecture evidence must include `AST guard` or bounded `rg` scans for forbidden recalculation and public leaks.
- Loaded fixture evidence must cover the named archetype corpus.

## Required Contracts
| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `NatalFactGraph`, `EligibilityContext`, loaded fixtures and `AST guard` prove runtime salience behavior. |
| Baseline Snapshot | yes | Before and after salience audit artifacts prove calibrated ranking decisions. |
| Ownership Routing | yes | Canonical ownership is required because new backend domain files may be created. |
| Allowlist Exception | no | No tolerance register is authorized for public score leaks or local recalculation. |
| Contract Shape | yes | Salience metadata has exact fields, levels, reason codes and exclusion reasons. |
| Batch Migration | no | No data migration or multi-record conversion is in scope. |
| Reintroduction Guard | yes | Forbidden minor centrality and public score leakage must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria
| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Each included fact has `salience_score`. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_salience_model.py`. |
| AC2 | Each included fact has `salience_level`. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_salience_model.py`. |
| AC3 | Each included fact has stable `reason_codes`. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_salience_model.py`. |
| AC4 | Exclusions have a reason. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_salience_model.py`. |
| AC5 | Eligible Sun remains a pillar. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_salience_model.py`. |
| AC6 | Eligible Moon remains a pillar. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_salience_model.py`. |
| AC7 | Eligible Ascendant remains a pillar. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_salience_model.py`. |
| AC8 | Minor facts stay below pillars. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_salience_model.py`. |
| AC9 | Exact luminary aspect ranks higher. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_salience_model.py`. |
| AC10 | Dominant house stays thematic. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_salience_archetypes.py`. |
| AC11 | Single weak signal is blocked. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_salience_archetypes.py`. |
| AC12 | Required profiles are covered. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_salience_archetypes.py`. |
| AC13 | Golden metadata is declared. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_salience_archetypes.py`. |
| AC14 | Public contracts expose no salience score. | Evidence profile: repo_wide_negative_scan; `rg -n "salience_score|salience_level" backend/app backend/tests`. |

## Implementation Tasks
- [ ] Task 1: Define the canonical `NatalSalienceModel` and versioned salience result contract. (AC: AC1, AC2, AC3)
- [ ] Task 2: Consume `NatalFactGraph` with `EligibilityContext` without rebuilding astrology runtime data. (AC: AC1, AC4, AC7)
- [ ] Task 3: Define stable documented `reason_codes` for every salience factor in the brief. (AC: AC3)
- [ ] Task 4: Emit deterministic `exclusion_reason` values for facts unavailable or forbidden in Basic. (AC: AC4, AC11)
- [ ] Task 5: Calibrate pillar priority for Sun, Moon, eligible Ascendant and angularity. (AC: AC5, AC6, AC7, AC8)
- [ ] Task 6: Calibrate dominant house, dominant planet, dignity, constraint, exact aspect and repetition factors. (AC: AC9, AC10, AC12)
- [ ] Task 7: Create or enrich anonymized archetype fixtures for the full required corpus. (AC: AC12, AC13)
- [ ] Task 8: Persist internal salience audit evidence without public contract exposure. (AC: AC13, AC14)
- [ ] Task 9: Add bounded scans preventing minor signals and internal score names from becoming public. (AC: AC8, AC14)

## Files to Inspect First
- `_story_briefs/cs-407-prioriser-faits-natals-basic-par-salience-calibree.md`
- `_condamad/stories/CS-411-natal-fact-graph-basic-tracable/00-story.md`
- `backend/app/domain/astrology/interpretation/natal_fact_graph.py`
- `backend/app/domain/astrology/interpretation/natal_fact_graph_builder.py`
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/domain/astrology/interpretation_adapters/signal_builder.py`
- `backend/tests/fixtures/golden/natal_test.yaml`
- `backend/tests/fixtures/golden/natal_premium_test.yaml`
- `backend/tests/factories/astrology_runtime_reference_factory.py`
- `backend/tests/unit/domain/astrology/test_basic_natal_fact_graph.py`

## Runtime Source of Truth
- Primary source of truth:
  - `NatalFactGraph`, `EligibilityContext`, loaded golden fixtures, runtime tests and `AST guard`.
- Secondary evidence:
  - Targeted `rg` scans for forbidden local recalculation and public score leaks.
- Static scans alone are not sufficient for this story because:
  - Priority ordering must be proven by loaded fact graph test data.

## Contract Shape
- Contract type:
  - Backend domain salience result for Basic natal facts.
- Fields:
  - `fact_id`: stable fact identifier copied from `NatalFactGraph`.
  - `salience_score`: internal deterministic numeric score.
  - `salience_level`: stable enum-like level for Basic prioritization.
  - `reason_codes`: stable list of documented scoring reasons.
  - `exclusion_reason`: stable reason for Basic exclusion.
- Required fields:
  - `fact_id`, `salience_score`, `salience_level`, `reason_codes`.
- Optional fields:
  - `exclusion_reason`, present only for excluded facts.
- Status codes:
  - none; no API route is in scope.
- Serialization names:
  - Internal audit names stay identical to the field names above.
- Frontend type impact:
  - none; no frontend generated client is in scope.
- Generated contract impact:
  - none; no OpenAPI change is in scope.

## Baseline / Before-After Rule
- Baseline artifact before implementation:
  - `_condamad/stories/CS-412-prioriser-faits-natals-basic-salience-calibree/evidence/salience-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-412-prioriser-faits-natals-basic-salience-calibree/evidence/salience-after.json`
- Expected invariant:
  - The only intended domain delta is internal Basic salience metadata and audit evidence.

## Ownership Routing Rule
| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Basic salience model | `backend/app/domain/astrology/interpretation/natal_salience_model.py` | backend API directory |
| Salience reason codes | `backend/app/domain/astrology/interpretation/natal_salience_model.py` | frontend source directory |
| Salience archetype fixtures | golden fixtures or backend test factories | backend application domain |
| Public projection boundary | `client_interpretation_projection_v1_builder.py` tests | public JSON score fields |

## Mandatory Reuse / DRY Constraints
- Reuse `NatalFactGraph`, fact IDs, `EligibilityContext`, runtime payloads and existing golden fixtures.
- Reuse existing test factories for astrology runtime references.
- Keep all salience rules in one canonical model module.
- Do not duplicate scoring weights in tests; tests assert outcomes through named fixtures or helper builders.
- Do not add external packages.

## No Legacy / Forbidden Paths
- No legacy scoring path may be added for Basic salience.
- No compatibility scoring path may be added for Basic salience.
- No fallback scoring path may be added for Basic salience.
- Do not create public fields named `salience_score`, `salience_level`, `ranking_score` or `weighted_score`.
- Do not make `Lilith`, `hayz`, `voices`, `forms`, `fertility` or numeric dignity details central in Basic.
- Do not recalculate aspects, dignities, houses, rulership or dominance inside the salience model.

## Reintroduction Guard
- Forbidden public symbols:
  - `salience_score`, `salience_level`, `ranking_score`, `weighted_score`.
- Forbidden Basic-central signals:
  - `lilith`, `hayz`, `voices`, `forms`, `fertility`.
- Forbidden recalculation markers:
  - `calculate_.*aspect`, `calculate_.*dignity`, `SwissEph`, `swe`, `HouseRulerResolver(`.
- Required deterministic guards:
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_salience_model.py`.
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_salience_archetypes.py`.
  - `rg -n "lilith|hayz|voices|forms|fertility|ranking_score|weighted_score" backend/app/domain/astrology/interpretation backend/tests/unit/domain/astrology`.

## Regression Guardrails
| Guardrail | Scope -> invariant -> evidence |
|---|---|
| RG-144 | runtime objects -> consume canonical chart object runtime data -> `pytest` architecture guard. |
| RG-145 | aspect facts -> preserve existing aspect engine inputs -> `pytest` salience aspect case. |
| RG-147 | dignity, dominance -> consume runtime payloads without score recalculation -> `rg` recalculation scan. |
| RG-148 | houses, rulers -> consume existing house and rulership runtime payloads -> `rg` resolver scan. |
| RG-151 | aspect identity -> keep stable pair and aspect code during ranking -> `pytest` exact aspect case. |
| RG-156 | Basic coverage -> keep diversified support material families -> `pytest` archetype corpus. |
| RG-160 | fact graph -> keep single owner and no public `source_paths` -> `pytest` plus bounded `rg`. |
| RG-161 | salience -> keep minor facts below natal pillars -> salience ranking tests plus forbidden-signal scan. |

Needs-investigation:
- `RG-146` is adjacent for motion and visibility payloads, but this story does not score motion or visibility directly.

Registry enrichment:
- `RG-161` protects the durable invariant preventing minor facts from outranking eligible natal pillars.

Non-applicable examples:
- `RG-047` frontend inline style is out of scope because no frontend surface is touched.
- `RG-052` frontend CSS namespace migration is out of scope because no CSS surface is touched.
- `RG-157` quota transactionality is out of scope because no entitlement surface is touched.

## Persistent Evidence Artifacts
| Artifact | Path | Purpose |
|---|---|---|
| Salience before snapshot | `_condamad/stories/CS-412-prioriser-faits-natals-basic-salience-calibree/evidence/salience-before.json` | Capture baseline fact priority evidence. |
| Salience after snapshot | `_condamad/stories/CS-412-prioriser-faits-natals-basic-salience-calibree/evidence/salience-after.json` | Capture implemented salience decisions. |
| Validation output | `_condamad/stories/CS-412-prioriser-faits-natals-basic-salience-calibree/evidence/validation.txt` | Keep lint, tests and scans output. |
| Review output | `_condamad/stories/CS-412-prioriser-faits-natals-basic-salience-calibree/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register
- Allowlist handling: not applicable
- Reason: no tolerance register is authorized for public score leaks, local recalculation or minor-fact centrality.

## Batch Migration Plan
- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify
Likely files:
- `backend/app/domain/astrology/interpretation/natal_salience_model.py` - define model, result contract, reason codes and scoring config.
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` - verify public boundary stays score-free.
- `backend/tests/fixtures/golden/natal_test.yaml` - add Basic salience expectations for the main golden chart.
- `backend/tests/fixtures/golden/natal_premium_test.yaml` - add shared golden metadata without public Basic score exposure.
- `backend/tests/factories/astrology_runtime_reference_factory.py` - add anonymized archetype factory helpers.
- `backend/tests/unit/domain/astrology/test_basic_natal_salience_model.py` - cover deterministic model ranking.
- `backend/tests/unit/domain/astrology/test_basic_natal_salience_archetypes.py` - cover calibrated archetype corpus.
- `_condamad/stories/CS-412-prioriser-faits-natals-basic-salience-calibree/evidence/validation.txt` - persist validation output.

Likely tests:
- `backend/tests/unit/domain/astrology/test_basic_natal_salience_model.py`
- `backend/tests/unit/domain/astrology/test_basic_natal_salience_archetypes.py`

Files not expected to change:
- `frontend/src` - out of scope; no frontend surface is touched.
- `backend/app/api` - out of scope; no API route is touched.
- `backend/app/infra` - out of scope; no persistence or external adapter is touched.
- `backend/alembic` - out of scope; no migration is touched.

## Dependency Policy
- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan
- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_salience_model.py --tb=short`
- VC6: `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_salience_archetypes.py --tb=short`
- VC7: `python -B -m pytest -q tests/unit/domain/astrology/test_chart_object_runtime_architecture.py --tb=short`
- VC8: `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_fact_graph.py --tb=short`
- VC9: `rg -n "lilith|hayz|voices|forms|fertility|ranking_score|weighted_score" app/domain/astrology/interpretation tests/unit/domain/astrology`
- VC10: `rg -n "calculate_.*aspect|calculate_.*dignity|swe|SwissEph|HouseRulerResolver\\(" app/domain/astrology/interpretation -g "*.py"`
- VC11: `rg -n "salience_score|salience_level" app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py tests -g "*.py"`

`rg` scan contract:
- VC9 forbidden pattern: `lilith|hayz|voices|forms|fertility|ranking_score|weighted_score`.
- VC9 allowed fixture pattern: hits only in tests asserting non-central or excluded Basic facts.
- VC9 scan roots: `app/domain/astrology/interpretation`, `tests/unit/domain/astrology`.
- VC9 expected false positives: test names and assertion fixtures proving forbidden facts stay non-central.
- VC10 forbidden pattern: `calculate_.*aspect|calculate_.*dignity|swe|SwissEph|HouseRulerResolver\\(`.
- VC10 allowed fixture pattern: zero hits in new salience model code; existing upstream imports only outside salience code.
- VC10 scan roots: `app/domain/astrology/interpretation`.
- VC10 expected false positives: none in `natal_salience_model.py`.
- VC11 forbidden pattern: `salience_score|salience_level`.
- VC11 allowed fixture pattern: unit tests may assert fields remain absent from public projection.
- VC11 scan roots: public projection builder and tests.
- VC11 expected false positives: tests proving public contract absence.

## Regression Risks
- A scoring rule could overfit the existing house 10 chart.
- A minor technical signal could become central because its label looks impressive.
- Internal salience scores could leak into public JSON or prompt-facing payloads.
- A local recalculation could drift from runtime astrology owners.
- The archetype corpus could omit date-only or non-career centered profiles.

## Dev Agent Instructions
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the Python venv before every Python, Ruff or Pytest command.
- Keep French file comments and docstrings for new or significantly modified application files.
- Preserve CS-411 fact graph ownership and do not weaken `RG-160`.

## References
- `_story_briefs/cs-407-prioriser-faits-natals-basic-par-salience-calibree.md`
- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `_story_briefs/cs-406-construire-fact-graph-natal-basic-tracable.md`
- `_condamad/stories/CS-411-natal-fact-graph-basic-tracable/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/domain/astrology/interpretation_adapters/signal_builder.py`
- `backend/tests/fixtures/golden/natal_test.yaml`
- `backend/tests/fixtures/golden/natal_premium_test.yaml`
