# Story CS-413 definir-taxonomie-themes-narratifs-basic: Definir Taxonomie Themes Narratifs Basic
Status: ready-to-review

## Trigger / Source
- Source brief: `_story_briefs/cs-408-definir-taxonomie-themes-narratifs-basic.md`.
- Selected mode: Repo-informed story.
- Source dependency: CS-405 remains a QA dependency named by the brief.
- Source dependency: CS-412 implements the salience brief referenced by the source as CS-407.
- Bounded problem: Basic has named narrative themes without activation, priority, content and birth-time availability contracts.
- Source-alignment evidence: objectives, risks, ACs, tasks, validations and non-goals map to the brief without scope drift.

## Objective
Create a versioned Basic natal narrative theme taxonomy that groups prioritized natal facts into bounded, testable themes without final prose generation.

## Target State
- `NatalNarrativeThemeTaxonomy` exposes the canonical Basic theme catalog.
- `ThemeModel` represents active themes with activation metadata and selected fact IDs.
- The ten Basic theme codes named by the brief are the only canonical Basic theme codes.
- Each theme declares triggers, exclusions, compatible sections, advised vocabulary and forbidden formulations.
- Each theme declares availability for `full_birth_time`, `approximate_birth_time` and `date_only`.
- House and angle dependent themes are downgraded or omitted when `EligibilityContext` forbids those sources.
- Neighboring themes are merged or hierarchized when their astrological material is redundant.
- Single weak signals cannot create an autonomous Basic section later in the pipeline.

## Current State Evidence
- Evidence 1: `_story_briefs/cs-408-definir-taxonomie-themes-narratifs-basic.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-413`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted IDs `RG-149`, `RG-152`, `RG-154`, `RG-156`, `RG-002`, `RG-022` and `RG-162` read.
- Evidence 4: `python -B .agents\skills\condamad-story-writer\scripts\resolve_guardrails.py` - scoped resolver executed.
- Evidence 5: `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md` - source plan inspected.
- Evidence 6: `_story_briefs/cs-407-prioriser-faits-natals-basic-par-salience-calibree.md` - salience dependency inspected.
- Evidence 7: `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - prompt-visible boundary inspected.
- Evidence 8: `backend/app/domain/llm/configuration/theme_astral_contracts.py` - existing theme astral contract style inspected.
- Evidence 9: `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py` - public narrative projection boundary inspected.

Repository structure alert:
- `backend` exists in this workspace.
- Expected new files may still need to be created by implementation under existing backend directories.

## Brief Primitive Ledger
| Primitive | Classification | Story mapping |
|---|---|---|
| `NatalNarrativeThemeTaxonomy` | in scope | AC1, AC2, Task 1 |
| `ThemeModel` | in scope | AC3, AC4, Task 2 |
| versioned taxonomy | in scope | AC1, Task 1 |
| prioritized facts | in scope dependency | AC3, AC4, Task 3 |
| salience levels | in scope dependency | AC4, AC12, Task 3 |
| `core_identity` | in scope theme | AC2, AC5, Task 4 |
| `emotional_pattern` | in scope theme | AC2, AC5, Task 4 |
| `public_vocation` | in scope theme | AC2, AC7, Task 5 |
| `relationship_pattern` | in scope theme | AC2, AC6, Task 5 |
| `mental_style` | in scope theme | AC2, AC6, Task 5 |
| `resources_and_values` | in scope theme | AC2, AC6, Task 5 |
| `action_and_drive` | in scope theme | AC2, AC6, Task 5 |
| `growth_direction` | in scope theme | AC2, AC8, Task 5 |
| `tension_to_integrate` | in scope theme | AC2, AC10, Task 6 |
| `talents_and_supports` | in scope theme | AC2, AC11, Task 6 |
| triggers | in scope | AC5, AC6, AC7, Task 4 |
| exclusions | in scope | AC8, AC12, Task 7 |
| sections compatibles | in scope | AC9, Task 8 |
| vocabulaire conseille | in scope | AC13, Task 8 |
| formulations interdites | in scope | AC14, Task 8 |
| birth-time availability | in scope | AC7, AC8, Task 7 |
| theme fusion | in scope | AC10, Task 9 |
| final prose | out of scope | Explicit non-goals |
| LLM call | out of scope | Explicit non-goals |
| `ReadingPlan` final | out of scope | Explicit non-goals |
| `/natal` page | out of scope | Explicit non-goals |
| new astrology calculations | out of scope | Explicit non-goals |

## Domain Boundary
- Domain: backend-domain
- In scope:
  - Backend domain taxonomy for Basic natal narrative themes.
  - Theme activation and omission rules from existing eligibility and salience inputs.
  - Unit tests for activation, date-only behavior, weak-signal blocking and forbidden wording.
  - Bounded scans proving public narrative and prompt-visible boundaries stay clean.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling, migrations, API routes and prompt execution.
- Explicit non-goals:
  - No final prose writing.
  - No LLM provider call.
  - No final `ReadingPlan` construction.
  - No `/natal` page change.
  - No new astrology calculation.
  - No public technical theme-code exposure.

## Operation Contract
- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain theme taxonomy contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only deterministic Basic theme taxonomy, activation and model output.
  - Keep public narrative fields free of internal theme codes and evidence IDs.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-412 does not expose prioritized facts or salience metadata.

Additional validation rules:
- Runtime evidence must include concrete `pytest -q backend/tests` paths.
- Architecture evidence must include `AST guard` or bounded `rg` scans for prompt-visible and public-boundary leaks.
- Loaded config evidence must prove the taxonomy version and ten canonical theme codes.

## Required Contracts
| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `NatalNarrativeThemeTaxonomy`, `ThemeModel`, salience inputs and `EligibilityContext` prove runtime behavior. |
| Baseline Snapshot | yes | Before and after taxonomy artifacts prove the only allowed domain delta. |
| Ownership Routing | yes | Canonical ownership is required because new backend domain files may be created. |
| Allowlist Exception | no | No tolerance register is authorized for duplicate themes, weak sections or public code leaks. |
| Contract Shape | yes | Theme model fields, theme codes, availability, vocabularies and forbidden wording are exact. |
| Batch Migration | no | No data migration or multi-record conversion is in scope. |
| Reintroduction Guard | yes | Duplicate themes, weak single-signal themes and forbidden formulations must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria
| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The taxonomy exposes a version. | Evidence profile: json_contract_shape; `pytest` covers `tests/unit/domain/astrology/test_basic_natal_theme_taxonomy.py`. |
| AC2 | The catalog contains the ten Basic codes. | Evidence profile: json_contract_shape; `pytest` covers `tests/unit/domain/astrology/test_basic_natal_theme_taxonomy.py`. |
| AC3 | Active themes expose selected fact IDs. | Evidence profile: json_contract_shape; `pytest` covers `tests/unit/domain/astrology/test_basic_natal_theme_activation.py`. |
| AC4 | Active themes expose activation metadata. | Evidence profile: json_contract_shape; `pytest` covers `tests/unit/domain/astrology/test_basic_natal_theme_activation.py`. |
| AC5 | Identity themes activate. | Evidence profile: runtime_openapi_contract; `pytest` covers `tests/unit/domain/astrology/test_basic_natal_theme_activation.py`. |
| AC6 | Functional themes activate. | Evidence profile: runtime_openapi_contract; `pytest` covers `tests/unit/domain/astrology/test_basic_natal_theme_activation.py`. |
| AC7 | House themes respect availability. | Evidence profile: runtime_openapi_contract; `pytest` covers `tests/unit/domain/astrology/test_basic_natal_theme_activation.py`. |
| AC8 | Date-only themes omit angle material. | Evidence profile: runtime_openapi_contract; `pytest` covers `tests/unit/domain/astrology/test_basic_natal_theme_activation.py`. |
| AC9 | Compatible sections are declared. | Evidence profile: json_contract_shape; `pytest` covers `tests/unit/domain/astrology/test_basic_natal_theme_taxonomy.py`. |
| AC10 | Redundant themes are hierarchized. | Evidence profile: json_contract_shape; `pytest` covers `tests/unit/domain/astrology/test_basic_natal_theme_activation.py`. |
| AC11 | Tension themes preserve tension facts. | Evidence profile: json_contract_shape; `pytest` covers `tests/unit/domain/astrology/test_basic_natal_theme_activation.py`. |
| AC12 | Weak signals stay section-ineligible. | Evidence profile: ast_architecture_guard; `pytest` covers `tests/unit/domain/astrology/test_basic_natal_theme_activation.py`. |
| AC13 | Advised vocabulary is documented. | Evidence profile: json_contract_shape; `pytest` covers `tests/unit/domain/astrology/test_basic_natal_theme_taxonomy.py`. |
| AC14 | Forbidden formulations are guarded. | Evidence profile: repo_wide_negative_scan; `rg` scan VC9. |
| AC15 | Public boundaries expose no raw theme internals. | Evidence profile: repo_wide_negative_scan; `rg` scan VC10. |
| AC16 | `RG-162` protects versioned Basic theme activation contracts. | `rg -n "RG-162" _condamad/stories/regression-guardrails.md`. |

## Implementation Tasks
- [ ] Task 1: Define the canonical versioned `NatalNarrativeThemeTaxonomy`. (AC: AC1, AC2)
- [ ] Task 2: Define `ThemeModel` with activation score, priority, resources, constraints and selected fact lists. (AC: AC3, AC4)
- [ ] Task 3: Consume CS-412 salience outputs without rebuilding astrology runtime data. (AC: AC3, AC4, AC12)
- [ ] Task 4: Implement triggers for `core_identity` and `emotional_pattern`. (AC: AC5)
- [ ] Task 5: Implement triggers for vocation, relationship, mental, resource, action and growth themes. (AC: AC6, AC7)
- [ ] Task 6: Implement tension and talent theme activation with preserved `must_mention` and `do_not_mention`. (AC: AC10, AC11)
- [ ] Task 7: Apply `EligibilityContext` availability for full, approximate and date-only birth-time states. (AC: AC7, AC8)
- [ ] Task 8: Declare compatible sections, advised vocabulary and forbidden formulations per theme. (AC: AC9, AC13, AC14)
- [ ] Task 9: Add deterministic merge or hierarchy rules for redundant neighboring themes. (AC: AC10)
- [ ] Task 10: Add bounded scans proving raw theme internals and forbidden wording stay out of public surfaces. (AC: AC14, AC15)
- [ ] Task 11: Preserve `RG-162` as the durable guardrail for Basic theme taxonomy contracts. (AC: AC16)

## Files to Inspect First
- `_story_briefs/cs-408-definir-taxonomie-themes-narratifs-basic.md`
- `_story_briefs/cs-407-prioriser-faits-natals-basic-par-salience-calibree.md`
- `_condamad/stories/CS-412-prioriser-faits-natals-basic-salience-calibree/00-story.md`
- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py`
- `backend/app/domain/astrology/interpretation/natal_salience_model.py`
- `backend/tests/unit/domain/astrology/test_basic_natal_salience_model.py`
- `backend/tests/unit/domain/astrology/test_basic_natal_salience_archetypes.py`

## Runtime Source of Truth
- Primary source of truth:
  - `NatalNarrativeThemeTaxonomy`, `ThemeModel`, CS-412 salience results, `EligibilityContext`, loaded fixtures and `AST guard`.
- Secondary evidence:
  - Targeted `rg` scans for forbidden public theme internals and forbidden generic wording.
- Static scans alone are not sufficient for this story because:
  - Theme activation and date-only omission must be proven by loaded runtime test data.

## Contract Shape
- Contract type:
  - Backend domain taxonomy and activated Basic theme model.
- Fields:
  - `taxonomy_version`: stable version for the Basic theme taxonomy.
  - `theme_code`: one of the ten canonical Basic codes.
  - `activation_score`: deterministic internal activation score.
  - `priority_level`: stable priority for later planning.
  - `resources`: supporting fact IDs.
  - `constraints`: limiting fact IDs.
  - `tensions`: contradiction or integration fact IDs.
  - `must_mention`: fact IDs required for later narrative planning.
  - `may_mention`: optional fact IDs for later narrative planning.
  - `do_not_mention`: internal or unsupported fact IDs forbidden in later public text.
  - `availability`: allowed birth-time states for the theme.
  - `compatible_sections`: stable section intents for later planning.
  - `advised_vocabulary`: bounded editorial vocabulary.
  - `forbidden_formulations`: terms or phrase patterns blocked for Basic.
- Required fields:
  - `taxonomy_version`, `theme_code`, `priority_level`, `availability`, `compatible_sections`.
- Optional fields:
  - `activation_score`, `resources`, `constraints`, `tensions`, `must_mention`, `may_mention`, `do_not_mention`.
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
  - `_condamad/stories/CS-413-definir-taxonomie-themes-narratifs-basic/evidence/theme-taxonomy-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-413-definir-taxonomie-themes-narratifs-basic/evidence/theme-taxonomy-after.json`
- Expected invariant:
  - The only intended domain delta is internal Basic theme taxonomy and activation metadata.

## Ownership Routing Rule
| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Basic theme taxonomy | `backend/app/domain/astrology/interpretation/natal_theme_taxonomy.py` | backend API directory |
| Basic theme activation | `backend/app/domain/astrology/interpretation/natal_theme_taxonomy.py` | frontend source directory |
| Theme activation fixtures | backend unit fixtures or test factories | backend application domain |
| Public narrative boundary | `narrative_natal_reading_builder.py` tests | raw internal theme fields |
| Prompt-visible boundary | `llm_astrology_input_v1.py` tests | raw taxonomy audit dumps |

## Mandatory Reuse / DRY Constraints
- Reuse CS-412 salience outputs, fact IDs, `EligibilityContext` and existing runtime fixture builders.
- Keep all theme code definitions in one canonical taxonomy owner.
- Keep activation thresholds named and centralized in the taxonomy owner.
- Do not duplicate the ten Basic theme code list in unrelated modules.
- Do not add external packages.

## No Legacy / Forbidden Paths
- No legacy theme taxonomy path may be added for Basic.
- No compatibility theme taxonomy path may be added for Basic.
- No fallback theme taxonomy path may be added for Basic.
- Do not create alternate public codes for the ten canonical Basic themes.
- Do not expose `theme_code`, `activation_score`, `must_mention`, `may_mention` or `do_not_mention` in public narrative text.
- Do not create a Basic section from one weak signal.
- Do not recalculate houses, angles, aspects, dignities, rulership or dominance inside the theme taxonomy.

## Reintroduction Guard
- Forbidden public symbols:
  - `theme_code`, `activation_score`, `must_mention`, `may_mention`, `do_not_mention`.
- Forbidden unproved generic wording:
  - `spirituel`, `creatif`, `harmonieux`, `profond`.
- Forbidden recalculation markers:
  - `calculate_.*aspect`, `calculate_.*house`, `calculate_.*dignity`, `SwissEph`, `swe`, `HouseRulerResolver(`.
- Required deterministic guards:
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_theme_taxonomy.py`.
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_theme_activation.py`.
  - `rg -n "spirituel|creatif|harmonieux|profond" backend/app/domain/astrology/interpretation backend/app/services/llm_generation/natal`.

## Regression Guardrails
| Guardrail | Scope -> invariant -> evidence |
|---|---|
| RG-149 | prompt process classification -> natal modern prompt boundaries stay explicit -> bounded `rg` on LLM input owners. |
| RG-152 | public reading contract -> internal theme codes stay out of narrative fields -> `pytest` public-boundary tests. |
| RG-154 | public DOM evidence denylist -> raw evidence IDs stay out of public narrative sources -> bounded `rg` leak scan. |
| RG-156 | Basic coverage -> themes cover multiple astrology families -> `pytest` activation corpus. |
| RG-022 | validation plan paths -> active pytest paths must be collectable -> targeted `pytest` commands. |
| RG-162 | Basic theme taxonomy -> ten versioned themes keep activation contracts -> taxonomy pytests and scans. |

Needs-investigation:
- The resolver returned `RG-002`, but no API route is touched; it is rejected as not local to this backend-domain story.

Registry enrichment:
- `RG-162` was added to protect versioned Basic themes and activation conditions.

Non-applicable examples:
- `RG-047` frontend inline style is out of scope because no frontend surface is touched.
- `RG-052` frontend CSS namespace migration is out of scope because no CSS surface is touched.
- `RG-157` quota transactionality is out of scope because no entitlement surface is touched.

## Persistent Evidence Artifacts
| Artifact | Path | Purpose |
|---|---|---|
| Taxonomy before snapshot | `_condamad/stories/CS-413-definir-taxonomie-themes-narratifs-basic/evidence/theme-taxonomy-before.json` | Capture baseline theme contract evidence. |
| Taxonomy after snapshot | `_condamad/stories/CS-413-definir-taxonomie-themes-narratifs-basic/evidence/theme-taxonomy-after.json` | Capture implemented taxonomy decisions. |
| Validation output | `_condamad/stories/CS-413-definir-taxonomie-themes-narratifs-basic/evidence/validation.txt` | Keep lint, tests and scans output. |
| Review output | `_condamad/stories/CS-413-definir-taxonomie-themes-narratifs-basic/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register
- Allowlist handling: not applicable
- Reason: no tolerance register is authorized for duplicate themes, weak sections or public code leaks.

## Batch Migration Plan
- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify
Likely files:
- `backend/app/domain/astrology/interpretation/natal_theme_taxonomy.py` - define taxonomy, `ThemeModel`, activation rules and version.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - verify prompt-visible boundary stays free of raw theme audit dumps.
- `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py` - verify public narrative boundary stays free of raw theme internals.
- `backend/tests/unit/domain/astrology/test_basic_natal_theme_taxonomy.py` - cover catalog, availability, vocabulary and forbidden wording.
- `backend/tests/unit/domain/astrology/test_basic_natal_theme_activation.py` - cover activation, date-only behavior, hierarchy and weak-signal blocking.
- `_condamad/stories/CS-413-definir-taxonomie-themes-narratifs-basic/evidence/validation.txt` - persist validation output.

Likely tests:
- `backend/tests/unit/domain/astrology/test_basic_natal_theme_taxonomy.py`
- `backend/tests/unit/domain/astrology/test_basic_natal_theme_activation.py`

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
- VC5: `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_theme_taxonomy.py --tb=short`
- VC6: `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_theme_activation.py --tb=short`
- VC7: `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_salience_model.py --tb=short`
- VC8: `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_salience_archetypes.py --tb=short`
- VC9: `rg -n "spirituel|creatif|harmonieux|profond" app/domain/astrology/interpretation app/services/llm_generation/natal`
- VC10: `rg -n "theme_code|activation_score|must_mention|may_mention|do_not_mention" app/services/llm_generation/natal`
- VC11: `rg -n "calculate_.*aspect|calculate_.*house|calculate_.*dignity|swe|SwissEph|HouseRulerResolver\\(" app/domain/astrology/interpretation -g "*.py"`

`rg` scan contract:
- VC9 forbidden pattern: `spirituel|creatif|harmonieux|profond`.
- VC9 allowed fixture pattern: hits only in taxonomy definitions or tests documenting forbidden formulations.
- VC9 scan roots: `app/domain/astrology/interpretation`, `app/services/llm_generation/natal`.
- VC9 expected false positives: taxonomy denylist values and tests asserting guarded wording.
- VC10 forbidden pattern: `theme_code|activation_score|must_mention|may_mention|do_not_mention`.
- VC10 allowed fixture pattern: tests may assert these fields remain absent from public narrative output.
- VC10 scan roots: `app/services/llm_generation/natal`.
- VC10 expected false positives: test names or assertions proving public-boundary absence.
- VC11 forbidden pattern: `calculate_.*aspect|calculate_.*house|calculate_.*dignity|swe|SwissEph|HouseRulerResolver\\(`.
- VC11 allowed fixture pattern: existing upstream owners outside the new taxonomy module.
- VC11 scan roots: `app/domain/astrology/interpretation`.
- VC11 expected false positives: none in `natal_theme_taxonomy.py`.

## Regression Risks
- The taxonomy could duplicate neighboring themes instead of merging their material.
- The taxonomy could overfit the existing vocation-heavy fixture.
- A date-only chart could still activate house or angle dependent sections.
- Forbidden Barnum wording could be documented but not guarded.
- Internal theme codes or evidence IDs could leak into prompt-visible or public narrative surfaces.
- The implementation could rebuild astrology facts instead of consuming salience and eligibility owners.

## Dev Agent Instructions
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the Python venv before every Python, Ruff or Pytest command.
- Keep French file comments and docstrings for new or significantly modified application files.
- Preserve CS-412 salience ownership and do not weaken public narrative guardrails.

## References
- `_story_briefs/cs-408-definir-taxonomie-themes-narratifs-basic.md`
- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `_story_briefs/cs-407-prioriser-faits-natals-basic-par-salience-calibree.md`
- `_condamad/stories/CS-412-prioriser-faits-natals-basic-salience-calibree/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py`
