# Story CS-411 natal-fact-graph-basic-tracable: Construire Fact Graph Natal Basic Tracable
Status: ready-to-dev

## Trigger / Source
- Source type: implementation brief.
- Source reference: `_story_briefs/cs-406-construire-fact-graph-natal-basic-tracable.md`.
- Reason for change: le backend Basic doit extraire des faits astrologiques atomiques, types et tracables avant scoring ou narration.
- Selected mode: Repo-informed story with Fast Story Writer Mode.
- Source-alignment evidence: objectif, AC, taches, preuves et guardrails couvrent extraction, tracabilite, eligibilite et anti-recalcul.

## Objective
Creer `NatalFactGraph`, une couche backend factuelle qui extrait des faits natals Basic depuis les projections runtime existantes.

## Target State
- `NatalFactGraph` expose des faits internes atomiques, types, deterministes et tracables.
- Les familles minimales du brief sont representees sans score de salience ni phrase utilisateur finale.
- Chaque fait porte un identifiant stable, une famille, des objets, une confiance, `requires_birth_time` et des `source_paths`.
- `EligibilityContext` pilote l'absence ou le degrade des faits dependants de l'heure.
- Les facts internes restent distincts des candidats a preuve editoriale.
- Le builder consomme les projections runtime existantes sans recalculer aspects, dignites, maisons, rulers ou conditions avancees.

## Current State Evidence
- Evidence 1: `_story_briefs/cs-406-construire-fact-graph-natal-basic-tracable.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign the story number.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted IDs `RG-144` to `RG-148`, `RG-156` and `RG-160` consulted.
- Evidence 4: `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md` - source plan inspected.
- Evidence 5: `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - current LLM input boundary inspected.
- Evidence 6: `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` - Basic projection shaping inspected.
- Evidence 7: `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` - runtime object projection inspected.
- Evidence 8: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - canonical runtime object contract inspected.
- Evidence 9: `backend/app/domain/astrology/interpretation_adapters/signal_builder.py` - existing signal builder ownership inspected.
- Evidence 10: `backend/tests/factories/astrology_runtime_reference_factory.py` - runtime test factory inspected.
- Repository structure alert: backend roots exist in this workspace; implementation must create only missing domain or test files.
- Scope vector:
  - operation `create`, domain `backend-domain`
  - paths `backend/app/domain/astrology/interpretation` and `backend/tests/unit/domain/astrology`
  - contracts `natal-fact-graph`, `runtime-source`, `traceability`, `no-local-recalculation`

## Brief Primitive Ledger
| Primitive | Classification | Story mapping |
|---|---|---|
| `NatalFactGraph` | in scope | AC1, AC2, AC3, Task 1, Task 2 |
| `luminary_fact` | in scope | AC1, AC5, Task 2 |
| `angle_fact` | in scope | AC1, AC4, Task 2 |
| `planet_position_fact` | in scope | AC1, AC5, Task 2 |
| `house_emphasis_fact` | in scope | AC1, AC4, Task 2 |
| `sign_emphasis_fact` | in scope | AC1, AC5, Task 2 |
| `element_balance_fact` | in scope | AC1, AC5, Task 2 |
| `modality_balance_fact` | in scope | AC1, AC5, Task 2 |
| `aspect_fact` | in scope | AC1, AC6, Task 2 |
| `rulership_fact` | in scope | AC1, AC4, Task 2 |
| `condition_fact` | in scope | AC1, AC7, Task 2 |
| `node_fact` | in scope | AC1, AC4, Task 2 |
| `EligibilityContext` | in scope | AC4, Task 3 |
| `source_paths` | in scope | AC2, AC8, Task 4 |
| stable identifiers | in scope | AC3, AC6, Task 5 |
| internal facts | in scope | AC8, Task 6 |
| editorial evidence candidates | in scope | AC8, Task 6 |
| salience scoring | out of scope | Non-goals |
| narrative sections | out of scope | Non-goals |
| user-facing prose | out of scope | Non-goals |
| new astrology calculations | out of scope | Non-goals |
| frontend contract | out of scope | Non-goals |

## Domain Boundary
- Domain: backend-domain
- In scope:
  - Backend domain model and builder for `NatalFactGraph`.
  - Unit tests for rich fixture, date-only fixture and partial runtime data.
  - Architecture guards proving runtime projections are consumed without local recalculation.
- Out of scope:
  - Frontend UI, database schema, auth, i18n runtime, styling, build tooling, migrations, quotas and entitlements.
  - Narrative planning, salience scoring, final prose generation and public API contract changes.
- Explicit non-goals:
  - No selection of narrative sections.
  - No final user-facing text.
  - No new aspect, dignity, house, rulership or condition calculation engine.
  - No React route, screen, client generation or UI validation.

## Operation Contract
- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add one canonical fact graph builder for Basic natal factual material.
  - Preserve runtime owners for chart objects, aspects, dignities, conditions, houses and rulership.
  - Preserve public payloads; this story creates internal factual material only.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: existing runtime projections do not expose enough material to build one required fact family.
- Additional validation rules:
  - Use `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_fact_graph.py` for rich fixture behavior.
  - Use `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_fact_graph_date_only.py` for date-only behavior.
  - Use `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` for runtime-source ownership.
  - Use `AST guard` or bounded `rg` scans to prove the builder does not call local calculators or Swiss Ephemeris.

## Required Contracts
| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, runtime fixtures and AST guard prove the builder consumes existing projections. |
| Baseline Snapshot | yes | Before and after artifacts prove the only allowed surface delta is internal fact graph extraction. |
| Ownership Routing | yes | Canonical ownership prevents duplicate fact graph builders or local recalculation helpers. |
| Allowlist Exception | no | No tolerance register is authorized for local recalculation or public leakage. |
| Contract Shape | yes | `NatalFactGraph` and fact items have exact required fields and family codes. |
| Batch Migration | no | No data migration or multi-record conversion is in scope. |
| Reintroduction Guard | yes | Recalculation markers and public payload leaks must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria
| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | All required fact families are emitted. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/test_basic_natal_fact_graph.py`. |
| AC2 | Every fact has traceable source paths. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/test_basic_natal_fact_graph.py`. |
| AC3 | Fact identifiers are deterministic. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/test_basic_natal_fact_graph.py`. |
| AC4 | Date-only input gates time-dependent facts. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/test_basic_natal_fact_graph_date_only.py`. |
| AC5 | Non-time-dependent families remain available. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/test_basic_natal_fact_graph_date_only.py`. |
| AC6 | Major aspects keep pair identity. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/test_basic_natal_fact_graph.py`. |
| AC7 | Runtime projections are the only calculation source. | Evidence profile: ast_architecture_guard; AST guard; `pytest`. |
| AC8 | Internal facts stay separate from editorial candidates. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/test_basic_natal_fact_graph.py`. |
| AC9 | Fact graph emits no final user text. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans backend fact graph module and tests. |
| AC10 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |

## Implementation Tasks
- [ ] Task 1: Define the canonical `NatalFactGraph` owner and typed fact contract. (AC: AC1, AC2, AC3)
- [ ] Task 2: Build the required fact families from existing runtime projections. (AC: AC1, AC5, AC6)
- [ ] Task 3: Route time-dependent families through `EligibilityContext`. (AC: AC4, AC5)
- [ ] Task 4: Attach internal `source_paths` for audit without adding them to public payloads. (AC: AC2, AC8)
- [ ] Task 5: Implement deterministic identifiers for facts and aspect pairs. (AC: AC3, AC6)
- [ ] Task 6: Separate internal facts from editorial evidence candidates in the model. (AC: AC8, AC9)
- [ ] Task 7: Add rich, date-only and partial-data unit fixtures. (AC: AC1, AC4, AC5, AC6)
- [ ] Task 8: Add architecture guards against local recalculation and final prose generation. (AC: AC7, AC9)
- [ ] Task 9: Persist before-after, validation and guard evidence under this story directory. (AC: AC10)

## Files to Inspect First
- `_story_briefs/cs-406-construire-fact-graph-natal-basic-tracable.md`
- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `backend/app/domain/astrology/interpretation_adapters/signal_builder.py`
- `backend/tests/factories/astrology_runtime_reference_factory.py`
- `_condamad/stories/regression-guardrails.md`

## Runtime Source of Truth
- Primary source of truth:
  - Existing runtime projections, `ChartObjectRuntimeData`, `EligibilityContext`, loaded fixtures and `AST guard`.
- Runtime evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_fact_graph.py`.
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_fact_graph_date_only.py`.
  - `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`.
- Secondary evidence:
  - Targeted `rg` scans for forbidden local calculators, Swiss Ephemeris calls and final prose markers.
- Static scans alone are not sufficient for this story because:
  - Fact graph content, date-only gating and identifier determinism must be proven through loaded runtime fixtures.

## Contract Shape
- Contract type:
  - Backend domain fact graph for Basic natal reading.
- Fields:
  - `graph_id`: deterministic graph identifier.
  - `facts`: ordered tuple or list of fact items.
  - `fact_id`: stable fact identifier.
  - `family`: one required family code from the brief.
  - `objects`: astrology object references used by the fact.
  - `confidence`: confidence level derived from runtime availability.
  - `requires_birth_time`: boolean marker for time-dependent facts.
  - `source_paths`: internal audit paths to runtime source material.
  - `editorial_candidate`: boolean marker for downstream evidence selection.
- Required fields:
  - `graph_id`, `facts`, `fact_id`, `family`, `objects`, `confidence`, `requires_birth_time`, `source_paths`, `editorial_candidate`.
- Optional fields:
  - none for the first fact graph contract.
- Status codes:
  - unchanged; this story does not add or change an API route.
- Serialization names:
  - `graph_id`, `facts`, `fact_id`, `family`, `objects`, `confidence`, `requires_birth_time`, `source_paths`, `editorial_candidate`.
- Frontend type impact:
  - none.
- Generated contract impact:
  - no generated API client or OpenAPI path is changed.

## Baseline / Before-After Rule
- Baseline artifact before implementation:
  - `_condamad/stories/CS-411-natal-fact-graph-basic-tracable/evidence/fact-graph-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-411-natal-fact-graph-basic-tracable/evidence/fact-graph-after.md`
- Expected invariant:
  - The only intended behavior delta is internal Basic natal fact graph extraction from existing runtime projections.

## Ownership Routing Rule
| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Fact graph model | `backend/app/domain/astrology/interpretation/natal_fact_graph.py` | API routers or frontend code |
| Fact graph builder | `backend/app/domain/astrology/interpretation/natal_fact_graph_builder.py` | prompt builders or services |
| Runtime object source | `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` | local fact graph DTO clones |
| Runtime projection source | `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` | local recalculation helpers |
| Fact graph unit tests | `backend/tests/unit/domain/astrology/test_basic_natal_fact_graph.py` | integration-only tests |
| Date-only fact tests | `backend/tests/unit/domain/astrology/test_basic_natal_fact_graph_date_only.py` | frontend tests |

## Mandatory Reuse / DRY Constraints
- Reuse existing `ChartObjectRuntimeData`, runtime payloads, `EligibilityContext` and interpretation projection data.
- Keep fact graph construction in one canonical builder and import it into downstream code.
- Reuse current runtime reference factories for tests rather than building parallel astrology dictionaries.
- Do not duplicate aspect, dignity, dominance, house, rulership, motion or visibility calculation logic.
- Do not add external packages.

## No Legacy / Forbidden Paths
- No legacy fact graph builder may be added outside the canonical interpretation owner.
- No compatibility wrapper may expose `source_paths` through public payloads.
- No fallback path may recalculate missing aspects, dignities, houses, rulership, motion or visibility.
- Do not add a shim, alias, broad tolerance register, hidden residual path or frontend-side repair.
- Forbidden surfaces: `frontend/src/**`, DB models, Alembic migrations, route handlers, quotas and entitlement services.

## Reintroduction Guard
- Forbidden recalculation markers:
  - `calculate_.*aspect|calculate_.*dignity|swe|SwissEph|HouseRulerResolver\(`
- Forbidden prose markers:
  - `paragraph|sentence|public_text|narrative_text|final_text|llm_prompt`
- Required guard:
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_fact_graph.py`
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_fact_graph_date_only.py`
  - `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
  - `rg -n "calculate_.*aspect|calculate_.*dignity|swe|SwissEph|HouseRulerResolver\\(" backend/app/domain/astrology/interpretation -g "*.py"`
- Allowed fixture pattern:
  - Test literals in `backend/tests/unit/domain/astrology/test_basic_natal_fact_graph.py`.
  - Test literals in `backend/tests/unit/domain/astrology/test_basic_natal_fact_graph_date_only.py`.
- Expected false positives:
  - Existing imports outside the fact graph module and test denylist literals only.

## Regression Guardrails
| Guardrail | Scope -> invariant -> evidence |
|---|---|
| RG-144 | natal runtime scope -> `ChartObjectRuntimeData` remains canonical -> targeted `pytest` and AST guard. |
| RG-145 | aspect scope -> aspects come from existing runtime output -> fact graph `pytest` and recalculation scan. |
| RG-146 | motion/visibility scope -> payloads are consumed, not recomputed -> runtime architecture `pytest`. |
| RG-147 | dignity/dominance scope -> historical projections stay source-owned -> targeted `pytest` and `rg`. |
| RG-148 | house/ruler scope -> resolver outputs stay source-owned -> date-only `pytest` and recalculation scan. |
| RG-156 | Basic coverage scope -> fact families stay diverse -> rich fixture and date-only `pytest`. |
| RG-160 | Fact graph scope -> one owner consumes runtime projections without recalculation -> targeted `pytest` and `rg`. |

Needs-investigation:
- `RG-002` and `RG-022` were returned by the resolver but rejected as adjacent because no API router or prompt-generation story surface is touched.

Registry enrichment completed:
- `RG-160` protects durable `NatalFactGraph` ownership and the anti-recalculation invariant requested by the brief.

Non-applicable examples:
- Frontend guardrails are out of scope because no React or CSS file is listed.
- DB and migration guardrails are out of scope because no persistence surface changes.
- Auth guardrails are out of scope because no access-control surface changes.

## Persistent Evidence Artifacts
| Artifact | Path | Purpose |
|---|---|---|
| Baseline before | `_condamad/stories/CS-411-natal-fact-graph-basic-tracable/evidence/fact-graph-before.md` | Record initial fact sources. |
| Baseline after | `_condamad/stories/CS-411-natal-fact-graph-basic-tracable/evidence/fact-graph-after.md` | Record final fact graph surface. |
| Validation output | `_condamad/stories/CS-411-natal-fact-graph-basic-tracable/evidence/validation.txt` | Keep local validation proof. |
| Guard output | `_condamad/stories/CS-411-natal-fact-graph-basic-tracable/evidence/recalculation-guards.txt` | Keep guard scan proof. |
| Review output | `_condamad/stories/CS-411-natal-fact-graph-basic-tracable/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register
- Allowlist handling: not applicable
- Reason: no allowlist entry or broad permitted delta is authorized.

## Batch Migration Plan
- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify
Likely files:
- `backend/app/domain/astrology/interpretation/natal_fact_graph.py` - define fact graph and fact item contracts.
- `backend/app/domain/astrology/interpretation/natal_fact_graph_builder.py` - build facts from existing runtime projections.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - consume editorial candidates only after graph extraction.
- `_condamad/stories/CS-411-natal-fact-graph-basic-tracable/evidence/fact-graph-before.md` - persist initial evidence.
- `_condamad/stories/CS-411-natal-fact-graph-basic-tracable/evidence/fact-graph-after.md` - persist final evidence.
- `_condamad/stories/CS-411-natal-fact-graph-basic-tracable/evidence/validation.txt` - persist validation output.
- `_condamad/stories/CS-411-natal-fact-graph-basic-tracable/evidence/recalculation-guards.txt` - persist guard output.

Likely tests:
- `backend/tests/unit/domain/astrology/test_basic_natal_fact_graph.py` - cover rich fixture, families, IDs and source paths.
- `backend/tests/unit/domain/astrology/test_basic_natal_fact_graph_date_only.py` - cover date-only gating and surviving families.
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` - extend anti-recalculation ownership guards.

Files not expected to change:
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/alembic/**` - out of scope; no migration is authorized.
- `backend/app/api/**` - out of scope; no route or status code change is authorized.
- `backend/app/infra/**` - out of scope; no persistence or external adapter is touched.
- `backend/app/services/entitlement/**` - out of scope; no quota or entitlement change is authorized.

## Dependency Policy
- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan
- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_fact_graph.py --tb=short`
- VC6: `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_fact_graph_date_only.py --tb=short`
- VC7: `python -B -m pytest -q tests/unit/domain/astrology/test_chart_object_runtime_architecture.py --tb=short`
- VC8 forbidden pattern: `calculate_.*aspect|calculate_.*dignity|swe|SwissEph|HouseRulerResolver\(`
- VC8 allowed fixture pattern: literals in the Basic fact graph test files.
- VC8 scan roots: `app/domain/astrology/interpretation` after `cd backend`
- VC8 expected false positives: existing test denylist literals only
- VC8 command: `rg -n "calculate_.*aspect|calculate_.*dignity|swe|SwissEph|HouseRulerResolver\\(" app/domain/astrology/interpretation -g "*.py"`
- VC9 forbidden pattern: `paragraph|sentence|public_text|narrative_text|final_text|llm_prompt`
- VC9 allowed fixture pattern: literals in the Basic fact graph test files.
- VC9 scan roots: `app/domain/astrology/interpretation` after `cd backend`
- VC9 expected false positives: test denylist literals only
- VC9 command: `rg -n "paragraph|sentence|public_text|narrative_text|final_text|llm_prompt" app/domain/astrology/interpretation`
- VC10: `python -B -c "from pathlib import Path; p=Path('../_condamad/stories/CS-411-natal-fact-graph-basic-tracable/evidence/validation.txt'); assert p.exists()"`

## Regression Risks
- The fact graph could become a hidden narrative or scoring engine instead of staying factual.
- Date-only charts could expose house, angle or ruler facts without eligibility proof.
- `source_paths` could leak into public payloads if internal and editorial facts are not separated.
- Recalculating runtime material locally could diverge from canonical astrology engines.

## Dev Agent Instructions
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep Python commands inside the activated `.venv`.
- Keep comments and docstrings in French for new or significantly modified application files.
- Preserve `RG-160`; do not weaken the `NatalFactGraph` ownership or anti-recalculation invariant during implementation.

## References
- `_story_briefs/cs-406-construire-fact-graph-natal-basic-tracable.md`
- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `_condamad/stories/regression-guardrails.md#RG-144`
- `_condamad/stories/regression-guardrails.md#RG-145`
- `_condamad/stories/regression-guardrails.md#RG-146`
- `_condamad/stories/regression-guardrails.md#RG-147`
- `_condamad/stories/regression-guardrails.md#RG-148`
- `_condamad/stories/regression-guardrails.md#RG-156`
- `_condamad/stories/regression-guardrails.md#RG-160`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `backend/app/domain/astrology/interpretation_adapters/signal_builder.py`
- `backend/tests/factories/astrology_runtime_reference_factory.py`
