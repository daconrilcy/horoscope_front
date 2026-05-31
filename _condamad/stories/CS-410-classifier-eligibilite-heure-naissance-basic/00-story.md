# Story CS-410 classifier-eligibilite-heure-naissance-basic: Classifier Eligibilite Heure Naissance Basic
Status: ready-to-review

## Trigger / Source
- Source type: product-risk brief.
- Source reference: `_story_briefs/cs-405-classifier-eligibilite-heure-naissance-lecture-basic.md`.
- Reason for change: une lecture Basic doit rester juste avec heure complete, heure approximative ou date seule.
- Selected mode: Repo-informed story with Fast Story Writer Mode.
- Source-alignment evidence: objectif, AC, taches, preuves et guardrails couvrent l'heure fiable, approximative et absente.

## Objective
Creer un `EligibilityContext` canonique pour piloter les familles maisons, angles, rulers et noeuds par maison dans la lecture natale Basic.

## Target State
- `EligibilityContext` classe `full_birth_time`, `approximate_birth_time` et `date_only`.
- Une heure fiable active maisons, angles, rulers de maisons et noeuds lunaires par maison.
- Une heure approximative active ces surfaces avec prudence et limitation publique.
- Une date seule exclut Ascendant, MC, maisons, angularite, rulers de maisons et noeuds lunaires par maison.
- Les faits solaires, lunaires, signes, elements, modalites et aspects non dependants de l'heure restent utilisables.
- Les composants aval consomment `EligibilityContext` au lieu de redecider localement l'usage des maisons.

## Current State Evidence
- Evidence 1: `_story_briefs/cs-405-classifier-eligibilite-heure-naissance-lecture-basic.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign the story number.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted IDs `RG-144` to `RG-148`, `RG-152`, `RG-154`, `RG-156` and `RG-159` consulted.
- Evidence 4: `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md` - source plan inspected.
- Evidence 5: `backend/app/services/user_profile/natal_chart_service.py` - current user birth profile and chart generation flow inspected.
- Evidence 6: `backend/app/services/natal/calculation_service.py` - calculation options and timezone handling inspected.
- Evidence 7: `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - current LLM input limits inspected.
- Evidence 8: `backend/app/services/llm_generation/natal/interpretation_service.py` - downstream natal interpretation flow inspected.
- Evidence 9: `backend/tests/fixtures/golden/natal_test.yaml` - current natal golden fixture inspected.
- Repository structure alert: backend roots exist in this workspace; implementation must create only missing domain or test files.
- Scope vector:
  - operation `create`, domain `backend-domain`
  - paths `backend/app/domain/astrology/interpretation`, `backend/app/services/llm_generation/natal`
  - contracts `eligibility-context`, `narrative-natal-reading`, `no-technical-public-leak`

## Brief Primitive Ledger
| Primitive | Classification | Story mapping |
|---|---|---|
| `EligibilityContext` | in scope | AC1, AC2, AC3, Task 1, Task 2 |
| `birth_time_status` | in scope | AC1, AC2, AC3, Task 2 |
| `full_birth_time` | in scope | AC1, Task 2, Task 4 |
| `approximate_birth_time` | in scope | AC2, Task 2, Task 4 |
| `date_only` | in scope | AC3, AC4, Task 2, Task 5 |
| `can_use_houses` | in scope | AC1, AC2, AC3, Task 2 |
| `can_use_angles` | in scope | AC1, AC2, AC3, Task 2 |
| `can_use_house_rulers` | in scope | AC1, AC2, AC3, Task 2 |
| `can_use_lunar_nodes_by_house` | in scope | AC1, AC2, AC3, Task 2 |
| public `limitations` | in scope | AC4, AC8, Task 3 |
| timezone missing | in scope | AC5, Task 4 |
| partially calculated chart | in scope | AC6, Task 4 |
| downstream guards | in scope | AC7, Task 6 |
| basic calculation algorithm | out of scope | Non-goals |
| UI birth time capture | out of scope | Non-goals |
| final narrative generation | out of scope | Non-goals |
| quotas or entitlements | out of scope | Non-goals |

## Domain Boundary
- Domain: backend-domain
- In scope:
  - Backend domain or application-service builder for `EligibilityContext`.
  - Backend tests for complete time, approximate time, date-only, missing timezone and partial chart states.
  - Downstream guards proving Basic interpretation cannot locally re-enable houses or angles.
- Out of scope:
  - Frontend UI, database schema, auth, i18n runtime, styling, build tooling, migrations, quotas and entitlements.
  - Changes to the base astrology calculation algorithm, provider selection or final narrative prose generation.
- Explicit non-goals:
  - No default birth time invention.
  - No React route, screen, client generation or UI validation.
  - No change to persisted quotas, paid-plan policy or entitlement checks.

## Operation Contract
- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add one canonical eligibility builder and route downstream Basic selection through it.
  - Preserve calculation outputs; this story classifies interpretability, not astronomical computation.
  - Preserve Basic usefulness with date-only input by keeping non-time-dependent facts available.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the profile model cannot distinguish approximate time from complete time.
- Additional validation rules:
  - Use `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_eligibility_context.py` for classification behavior.
  - Use `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_date_only_reading_guards.py` for downstream guard behavior.
  - Use `AST guard` or bounded `rg` scans to prove downstream code does not locally re-enable house-dependent families.
  - Use loaded config or fixture construction in `pytest` to prove timezone-missing and partial-chart behavior.

## Required Contracts
| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, loaded fixtures and AST guard prove runtime classification and downstream consumption. |
| Baseline Snapshot | yes | Before and after artifacts prove the only allowed surface delta is Basic eligibility gating. |
| Ownership Routing | yes | Canonical ownership prevents duplicated eligibility decisions in downstream components. |
| Allowlist Exception | no | No tolerance register is authorized for local house reactivation. |
| Contract Shape | yes | `EligibilityContext` has exact fields, statuses and limitation rules. |
| Batch Migration | no | No data migration or multi-record conversion is in scope. |
| Reintroduction Guard | yes | House and angle interpretation must stay blocked without eligibility. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria
| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Full birth time enables all time-dependent families. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/test_basic_natal_eligibility_context.py`. |
| AC2 | Approximate birth time marks cautious eligibility. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/test_basic_natal_eligibility_context.py`. |
| AC3 | Date-only input disables house-dependent families. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/test_basic_natal_eligibility_context.py`. |
| AC4 | Date-only limitation is public. | Evidence profile: targeted_forbidden_symbol_scan; `tests/unit/domain/astrology/test_basic_natal_eligibility_context.py`. |
| AC5 | Missing timezone prevents full-time confidence. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/test_basic_natal_eligibility_context.py`. |
| AC6 | Partial chart state cannot enable absent surfaces. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/test_basic_natal_eligibility_context.py`. |
| AC7 | Downstream Basic uses eligibility. | Evidence profile: ast_architecture_guard; AST guard; `tests/unit/domain/astrology/test_basic_natal_date_only_reading_guards.py`. |
| AC8 | Non-time-dependent facts remain available. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/test_basic_natal_date_only_reading_guards.py`. |
| AC9 | No noon surrogate drives house interpretation. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans backend astrology and generation roots. |
| AC10 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |

## Implementation Tasks
- [ ] Task 1: Choose the canonical backend owner for `EligibilityContext` before editing downstream code. (AC: AC1, AC7)
- [ ] Task 2: Implement the three `birth_time_status` classifications and boolean family gates. (AC: AC1, AC2, AC3, AC5, AC6)
- [ ] Task 3: Emit public limitation text for uncertain or absent birth time without technical identifiers. (AC: AC2, AC4)
- [ ] Task 4: Add unit fixtures for complete time, approximate time, date-only, missing timezone and partial chart state. (AC: AC1, AC2, AC3, AC5, AC6)
- [ ] Task 5: Preserve solar, lunar, sign, element, modality and non-time-dependent aspect material for date-only reads. (AC: AC8)
- [ ] Task 6: Add downstream guards so Basic selection passes through `EligibilityContext`. (AC: AC7, AC9)
- [ ] Task 7: Add bounded scans proving no local noon surrogate or local house reactivation path was introduced. (AC: AC7, AC9)
- [ ] Task 8: Persist validation and before-after evidence under this story evidence directory. (AC: AC10)

## Files to Inspect First
- `_story_briefs/cs-405-classifier-eligibilite-heure-naissance-lecture-basic.md`
- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `backend/app/services/user_profile/natal_chart_service.py`
- `backend/app/services/natal/calculation_service.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/tests/fixtures/golden/natal_test.yaml`
- `_condamad/stories/regression-guardrails.md`

## Runtime Source of Truth
- Primary source of truth:
  - `EligibilityContext` model validation, runtime builder tests, downstream service tests and `AST guard`.
- Runtime evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_eligibility_context.py`.
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_date_only_reading_guards.py`.
- Secondary evidence:
  - Targeted `rg` scans for forbidden local house, angle and noon-surrogate logic.
- Static scans alone are not sufficient for this story because:
  - Birth-time classification must be proven through loaded test fixtures and downstream behavior.

## Contract Shape
- Contract type:
  - Backend domain eligibility context for Basic natal reading.
- Fields:
  - `birth_time_status`: one of `full_birth_time`, `approximate_birth_time`, `date_only`.
  - `can_use_houses`: boolean gate for houses.
  - `can_use_angles`: boolean gate for Ascendant, MC and angle-derived interpretation.
  - `can_use_house_rulers`: boolean gate for house ruler interpretation.
  - `can_use_lunar_nodes_by_house`: boolean gate for node-by-house interpretation.
  - `limitations`: public list of readable limitations.
- Required fields:
  - `birth_time_status`, `can_use_houses`, `can_use_angles`, `can_use_house_rulers`, `can_use_lunar_nodes_by_house`, `limitations`.
- Optional fields:
  - none for the first eligibility contract.
- Status codes:
  - unchanged; this story does not add or change an API route.
- Serialization names:
  - `birth_time_status`, `can_use_houses`, `can_use_angles`, `can_use_house_rulers`, `can_use_lunar_nodes_by_house`, `limitations`.
- Frontend type impact:
  - none.
- Generated contract impact:
  - no generated API client or OpenAPI path is changed.

## Baseline / Before-After Rule
- Baseline artifact before implementation:
  - `_condamad/stories/CS-410-classifier-eligibilite-heure-naissance-basic/evidence/eligibility-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-410-classifier-eligibilite-heure-naissance-basic/evidence/eligibility-after.md`
- Expected invariant:
  - The only intended behavior delta is Basic eligibility gating for time-dependent natal reading families.

## Ownership Routing Rule
| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Birth-time eligibility model | `backend/app/domain/astrology/interpretation/basic_natal_eligibility.py` | API routers or frontend code |
| Eligibility builder | `backend/app/domain/astrology/interpretation/basic_natal_eligibility.py` | downstream prompt builders |
| LLM input limitation mapping | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | provider adapter code |
| Downstream Basic guard tests | `backend/tests/unit/domain/astrology/test_basic_natal_date_only_reading_guards.py` | integration-only tests |
| Classification unit tests | `backend/tests/unit/domain/astrology/test_basic_natal_eligibility_context.py` | frontend tests |

## Mandatory Reuse / DRY Constraints
- Reuse existing birth profile, `BirthInput`, `NatalResult` and interpretation projection data instead of inventing parallel DTOs.
- Keep the eligibility decision in one owner and import it into downstream selection code.
- Reuse current public limitation or disclaimer patterns for readable messages.
- Do not duplicate house, angle or ruler detection logic inside prompt or renderer code.
- Do not add external packages.

## No Legacy / Forbidden Paths
- No legacy path may interpret houses, angles or rulers without `EligibilityContext`.
- No compatibility wrapper may map date-only input to a synthetic complete-time state.
- No fallback path may use `12:00`, noon or a default hour to produce house-dependent interpretation.
- Do not add a shim, alias, broad tolerance register, hidden residual path or frontend-side repair.
- Forbidden surfaces: `frontend/src/**`, DB models, Alembic migrations, route handlers, quotas and entitlement services.

## Reintroduction Guard
- Forbidden local decision markers:
  - `house_number|ascendant|mc|house_ruler|angular`
- Forbidden surrogate markers:
  - `12:00|noon|default_birth_time|birth_time or`
- Required guard:
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_eligibility_context.py`
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_date_only_reading_guards.py`
  - `rg -n "house_number|ascendant|mc|house_ruler|angular" backend/app/domain/astrology/interpretation backend/app/services/llm_generation/natal`
- Allowed fixture pattern:
  - Test literals in `backend/tests/unit/domain/astrology/test_basic_natal_eligibility_context.py`.
  - Test literals in `backend/tests/unit/domain/astrology/test_basic_natal_date_only_reading_guards.py`.
- Expected false positives:
  - Existing canonical data-field names and test denylist literals only.

## Regression Guardrails
| Guardrail | Scope -> invariant -> evidence |
|---|---|
| RG-144 | natal runtime scope -> existing `NatalResult.chart_objects` and collections stay intact -> targeted `pytest` and AST guard. |
| RG-145 | aspect runtime scope -> aspect candidates stay runtime-owned -> existing chart-object aspect `pytest` and scans. |
| RG-146 | motion/visibility scope -> payloads stay precomputed and typed -> existing runtime payload `pytest` and scans. |
| RG-147 | dignity/dominance scope -> eligibility must not branch by `object_type` -> existing runtime `pytest` and scans. |
| RG-148 | house/ruler scope -> runtime house payloads stay source-owned -> eligibility `pytest` and bounded `rg`. |
| RG-152 | public narrative scope -> limitations expose no technical data -> targeted `pytest` and public marker scan. |
| RG-154 | public DOM scope -> limitations expose no internal markers in public reading -> public marker scan. |
| RG-156 | Basic editorial scope -> date-only still has diversified non-house material -> downstream `pytest`. |
| RG-159 | Basic eligibility scope -> houses and angles require `EligibilityContext` -> eligibility `pytest` and bounded `rg`. |
| RG-002 | backend ownership scope -> logic stays out of route layers -> ownership review and targeted `rg`. |

Needs-investigation:
- none for the brief guardrails; all required IDs are classified in this section.

Registry enrichment:
- `RG-159` records the durable invariant forbidding house and angle interpretation without `EligibilityContext`.

Non-applicable examples:
- Frontend guardrails are out of scope because no React or CSS file is listed.
- DB and migration guardrails are out of scope because no persistence surface changes.
- Auth guardrails are out of scope because no access-control surface changes.

## Persistent Evidence Artifacts
| Artifact | Path | Purpose |
|---|---|---|
| Baseline before | `_condamad/stories/CS-410-classifier-eligibilite-heure-naissance-basic/evidence/eligibility-before.md` | Record initial eligibility surfaces. |
| Baseline after | `_condamad/stories/CS-410-classifier-eligibilite-heure-naissance-basic/evidence/eligibility-after.md` | Record final eligibility surfaces. |
| Validation output | `_condamad/stories/CS-410-classifier-eligibilite-heure-naissance-basic/evidence/validation.txt` | Keep local validation proof. |
| Guard output | `_condamad/stories/CS-410-classifier-eligibilite-heure-naissance-basic/evidence/date-only-guards.txt` | Keep guard scan proof. |
| Review output | `_condamad/stories/CS-410-classifier-eligibilite-heure-naissance-basic/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register
- Allowlist handling: not applicable
- Reason: no allowlist entry or broad permitted delta is authorized.

## Batch Migration Plan
- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify
Likely files:
- `backend/app/domain/astrology/interpretation/basic_natal_eligibility.py` - define `EligibilityContext` and builder.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - route limits through eligibility context.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - preserve downstream consumption through the canonical context.
- `_condamad/stories/CS-410-classifier-eligibilite-heure-naissance-basic/evidence/eligibility-before.md` - persist initial evidence.
- `_condamad/stories/CS-410-classifier-eligibilite-heure-naissance-basic/evidence/eligibility-after.md` - persist final evidence.
- `_condamad/stories/CS-410-classifier-eligibilite-heure-naissance-basic/evidence/validation.txt` - persist validation output.
- `_condamad/stories/CS-410-classifier-eligibilite-heure-naissance-basic/evidence/date-only-guards.txt` - persist guard output.

Likely tests:
- `backend/tests/unit/domain/astrology/test_basic_natal_eligibility_context.py` - cover classification and public limitations.
- `backend/tests/unit/domain/astrology/test_basic_natal_date_only_reading_guards.py` - prove downstream date-only gating.

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
- VC5: `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_eligibility_context.py --tb=short`
- VC6: `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_date_only_reading_guards.py --tb=short`
- VC7 forbidden pattern: `house_number|ascendant|mc|house_ruler|angular`
- VC7 allowed fixture pattern: literals in the two Basic eligibility test files.
- VC7 scan roots: `app/domain/astrology/interpretation` and `app/services/llm_generation/natal` after `cd backend`
- VC7 expected false positives: existing canonical field names and test denylist literals only
- VC7 command: `rg -n "house_number|ascendant|mc|house_ruler|angular" app/domain/astrology/interpretation app/services/llm_generation/natal`
- VC8 forbidden pattern: `12:00|noon|default_birth_time|birth_time or`
- VC8 allowed fixture pattern: none in production roots.
- VC8 scan roots: `app/domain/astrology/interpretation`, `app/services/llm_generation/natal` and `app/services/user_profile` after `cd backend`
- VC8 expected false positives: existing error messages about missing birth time only
- VC8 command: `rg -n "12:00|noon|default_birth_time|birth_time or" app/domain/astrology/interpretation app/services/llm_generation/natal app/services/user_profile`
- VC9: `python -B -c "from pathlib import Path; p=Path('../_condamad/stories/CS-410-classifier-eligibilite-heure-naissance-basic/evidence/validation.txt'); assert p.exists()"`

## Regression Risks
- Date-only readings could become falsely complete if any downstream code reads house fields directly.
- Approximate birth time could be treated as fully precise unless the limitation is explicit.
- Public limitation text could leak internal status codes or calculation details.
- Non-time-dependent material could be hidden too aggressively and make Basic unhelpful.

## Dev Agent Instructions
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep Python commands inside the activated `.venv`.
- Keep comments and docstrings in French for new or significantly modified application files.
- Do not update `_condamad/stories/regression-guardrails.md` during implementation of this story.

## References
- `_story_briefs/cs-405-classifier-eligibilite-heure-naissance-lecture-basic.md`
- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `_condamad/stories/regression-guardrails.md#RG-144`
- `_condamad/stories/regression-guardrails.md#RG-145`
- `_condamad/stories/regression-guardrails.md#RG-146`
- `_condamad/stories/regression-guardrails.md#RG-147`
- `_condamad/stories/regression-guardrails.md#RG-148`
- `_condamad/stories/regression-guardrails.md#RG-152`
- `_condamad/stories/regression-guardrails.md#RG-154`
- `_condamad/stories/regression-guardrails.md#RG-156`
- `_condamad/stories/regression-guardrails.md#RG-159`
- `backend/app/services/user_profile/natal_chart_service.py`
- `backend/app/services/natal/calculation_service.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/tests/fixtures/golden/natal_test.yaml`
