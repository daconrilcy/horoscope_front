# Story CS-414 resoudre-contradictions-themes-natals-basic: Resoudre Contradictions Themes Natals Basic
Status: done

## Trigger / Source
- Source brief: `_story_briefs/cs-414-resoudre-contradictions-themes-natals-basic.md`.
- Selected mode: Repo-informed story.
- Source dependency: CS-413 defines the Basic theme taxonomy referenced by this resolver story.
- Bounded problem: Basic themes can contain mixed astrological signals without a deterministic synthesis contract.
- Source-alignment evidence: objectives, risks, ACs, tasks, validations and non-goals map to the brief without scope drift.

## Objective
Create a deterministic `SynthesisResolver` that turns active Basic natal themes into structured editorial syntheses without final public prose generation.

## Target State
- `SynthesisResolver` consumes active `ThemeModel` entries with resources, constraints and tensions.
- Each resolved theme emits `core_statement`, `resource_statement`, `constraint_statement`, `integration_statement` and `confidence`.
- A strong resource combined with a strong constraint produces an explicit nuance.
- A theme based on one weak fact cannot become an autonomous section candidate.
- Redundant themes sharing the same facts are merged or explicitly linked in resolver output.
- House-dependent themes are downgraded or omitted when birth-time eligibility forbids houses, ASC or MC.
- Date-only synthesis uses signs, luminaries, aspects and balances without house, ASC or MC interpretation.
- Forbidden absolute, fatalistic and prescriptive formulations are denied before downstream narrative generation.
- Resolved syntheses stay editorial inputs for plan or LLM use, not direct public text.

## Current State Evidence
- Evidence 1: `_story_briefs/cs-414-resoudre-contradictions-themes-natals-basic.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-414`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted IDs `RG-152`, `RG-154`, `RG-155`, `RG-156`, `RG-022`, `RG-163` read.
- Evidence 4: `python -B .agents\skills\condamad-story-writer\scripts\resolve_guardrails.py` - scoped resolver executed.
- Evidence 5: `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md` - source plan inspected.
- Evidence 6: `_story_briefs/cs-413-definir-taxonomie-themes-narratifs-basic.md` - taxonomy dependency inspected.
- Evidence 7: `backend/app/services/llm_generation/natal/narrative_semantic_integrity.py` - semantic validator inspected.
- Evidence 8: `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py` - public text denylist inspected.
- Evidence 9: `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` - existing golden-case pattern inspected.

Repository structure alert:
- `backend`, `backend/app` and `backend/tests` exist in this workspace.
- Expected new files may still need to be created by implementation under existing backend directories.

## Brief Primitive Ledger
| Primitive | Classification | Story mapping |
|---|---|---|
| `SynthesisResolver` | in scope | AC1, AC2, Task 1 |
| active themes | in scope dependency | AC1, Task 2 |
| `resources` | in scope | AC3, Task 3 |
| `constraints` | in scope | AC4, Task 3 |
| `tensions` | in scope | AC5, Task 4 |
| `core_statement` | in scope | AC6, Task 5 |
| `resource_statement` | in scope | AC7, Task 5 |
| `constraint_statement` | in scope | AC8, Task 5 |
| `integration_statement` | in scope | AC9, Task 5 |
| `confidence` | in scope | AC10, Task 5 |
| dignity plus constraint nuance | in scope | AC11, Task 6 |
| single weak fact blocking | in scope | AC12, Task 7 |
| redundant theme merge | in scope | AC13, Task 8 |
| unavailable houses downgrade | in scope | AC14, Task 9 |
| date-only synthesis | in scope | AC15, Task 9 |
| Venus strong but combust | in scope test case | AC16, Task 10 |
| constrained Moon | in scope test case | AC17, Task 10 |
| Jupiter square luminaires | in scope test case | AC18, Task 10 |
| mixed relationship theme | in scope test case | AC19, Task 10 |
| wording denylist | in scope | AC20, Task 11 |
| final prose generation | out of scope | Explicit non-goals |
| prompt provider | out of scope | Explicit non-goals |
| frontend | out of scope | Explicit non-goals |

## Domain Boundary
- Domain: backend-domain
- In scope:
  - Backend domain resolver for Basic natal theme synthesis.
  - Editorial synthesis structure for active `ThemeModel` entries.
  - Unit tests for contradictory themes, weak facts, redundant themes and date-only behavior.
  - Bounded scans proving public narrative and prompt-visible boundaries stay clean.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling, migrations, API routes and prompt provider changes.
- Explicit non-goals:
  - No full `ReadingPlan` construction.
  - No final public prose generation.
  - No prompt provider change.
  - No medical, legal, financial or psychological recommendation.
  - No frontend change.
  - No new astrology calculation.

## Operation Contract
- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain synthesis resolver contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only deterministic Basic theme synthesis from existing theme, salience and eligibility inputs.
  - Keep resolved syntheses separated from final user-facing narrative rendering.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-413 theme outputs do not expose resources, constraints or tensions.

Additional validation rules:
- Runtime evidence must include concrete `pytest -q backend/tests` paths.
- Architecture evidence must include `AST guard` or bounded `rg` scans for public-boundary leaks.
- Loaded contract evidence must prove the five synthesis fields and denylist policy.

## Required Contracts
| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `SynthesisResolver`, `ThemeModel`, eligibility inputs and pytest fixtures prove runtime behavior. |
| Baseline Snapshot | yes | Before and after resolver artifacts prove the only allowed backend-domain delta. |
| Ownership Routing | yes | Canonical ownership is required because new backend domain files may be created. |
| Allowlist Exception | no | No tolerance register is authorized for unilateral synthesis or forbidden wording. |
| Contract Shape | yes | Synthesis fields, confidence values and date-only limits are exact. |
| Batch Migration | no | No data migration or multi-record conversion is in scope. |
| Reintroduction Guard | yes | Absolute wording, autonomous weak sections and raw technical surfaces must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria
| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The resolver consumes active themes. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py`. |
| AC2 | The resolver returns resolved themes. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py`. |
| AC3 | Resource facts drive resource synthesis. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py`. |
| AC4 | Constraint facts drive synthesis. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py`. |
| AC5 | Tension facts drive integration. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py`. |
| AC6 | Each synthesis has a core statement. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py`. |
| AC7 | Each synthesis has a resource statement. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py`. |
| AC8 | Each synthesis has a constraint statement. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py`. |
| AC9 | Each synthesis has integration. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py`. |
| AC10 | Each synthesis has confidence. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py`. |
| AC11 | Strong mixed signals force nuance. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_contradictions.py`. |
| AC12 | One weak fact stays ineligible. | Evidence profile: ast_architecture_guard; `pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py`. |
| AC13 | Redundant themes are merged. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py`. |
| AC14 | Unavailable house themes are downgraded. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py`. |
| AC15 | Date-only synthesis excludes houses. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py`. |
| AC16 | Venus combust case is nuanced. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_contradictions.py`. |
| AC17 | Constrained Moon case is nuanced. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_contradictions.py`. |
| AC18 | Jupiter square case is nuanced. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_contradictions.py`. |
| AC19 | Mixed relationship case is nuanced. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_contradictions.py`. |
| AC20 | Forbidden formulations are denied. | Evidence profile: repo_wide_negative_scan; `rg` scan VC8. |
| AC21 | Resolved syntheses remain non-public. | Evidence profile: repo_wide_negative_scan; `rg` scan VC9. |

## Implementation Tasks
- [ ] Task 1: Define `SynthesisResolver` and resolved synthesis contracts in the canonical interpretation domain. (AC: AC1, AC2)
- [ ] Task 2: Consume CS-413 active `ThemeModel` entries without rebuilding theme detection. (AC: AC1)
- [ ] Task 3: Map resources and constraints into separate synthesis fields. (AC: AC3, AC4, AC7, AC8)
- [ ] Task 4: Map tensions into `integration_statement` without final prose rendering. (AC: AC5, AC9)
- [ ] Task 5: Emit `core_statement`, `resource_statement`, `constraint_statement`, `integration_statement` and `confidence`. (AC: AC6, AC7, AC8, AC9, AC10)
- [ ] Task 6: Add adversarial mixed-signal rules for strong resource plus strong constraint themes. (AC: AC11, AC16, AC17, AC18, AC19)
- [ ] Task 7: Block autonomous section candidacy for themes founded on one weak fact. (AC: AC12)
- [ ] Task 8: Merge or explicitly link redundant themes sharing the same selected facts. (AC: AC13)
- [ ] Task 9: Apply birth-time eligibility to downgrade or omit house, ASC and MC dependent syntheses. (AC: AC14, AC15)
- [ ] Task 10: Add representative contradiction tests for Venus, Moon, Jupiter and mixed relationship themes. (AC: AC16, AC17, AC18, AC19)
- [ ] Task 11: Add bounded denylist scans for absolute, fatalistic and prescriptive formulations. (AC: AC20, AC21)

## Files to Inspect First
- `_story_briefs/cs-414-resoudre-contradictions-themes-natals-basic.md`
- `_condamad/stories/CS-413-definir-taxonomie-themes-narratifs-basic/00-story.md`
- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `backend/app/domain/astrology/interpretation/natal_theme_taxonomy.py`
- `backend/app/domain/astrology/interpretation/natal_salience_model.py`
- `backend/app/services/llm_generation/natal/narrative_semantic_integrity.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`
- `backend/tests/unit/domain/astrology/test_basic_natal_theme_taxonomy.py`
- `backend/tests/unit/domain/astrology/test_basic_natal_theme_activation.py`
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`

## Runtime Source of Truth
- Primary source of truth:
  - `SynthesisResolver`, active `ThemeModel` fixtures, eligibility fixtures, loaded denylist and `AST guard`.
- Secondary evidence:
  - Targeted `rg` scans for forbidden public synthesis internals and forbidden wording.
- Static scans alone are not sufficient for this story because:
  - Mixed-signal resolution, weak-fact blocking and date-only omission must be proven by loaded runtime test data.

## Contract Shape
- Contract type:
  - Backend domain synthesis contract for Basic natal themes.
- Fields:
  - `theme_code`: canonical Basic theme code from CS-413.
  - `core_statement`: controlled editorial summary for the resolved theme.
  - `resource_statement`: controlled editorial resource line.
  - `constraint_statement`: controlled editorial constraint line.
  - `integration_statement`: controlled editorial integration line.
  - `confidence`: bounded confidence value derived from evidence quality.
  - `section_eligible`: boolean gate for later plan construction.
  - `merge_group`: optional identifier for redundant themes sharing selected facts.
  - `omission_reason`: optional controlled reason for date-only or weak-fact omission.
- Required fields:
  - `theme_code`, `core_statement`, `resource_statement`, `constraint_statement`, `integration_statement`, `confidence`.
- Optional fields:
  - `section_eligible`, `merge_group`, `omission_reason`.
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
  - `_condamad/stories/CS-414-resoudre-contradictions-themes-natals-basic/evidence/before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-414-resoudre-contradictions-themes-natals-basic/evidence/after.json`
- Expected invariant:
  - The only intended domain delta is internal Basic theme synthesis resolution.

## Ownership Routing Rule
| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Basic synthesis resolver | `backend/app/domain/astrology/interpretation/natal_synthesis_resolver.py` | backend API directory |
| Synthesis contracts | `backend/app/domain/astrology/interpretation/natal_synthesis_resolver.py` | frontend source directory |
| Contradiction fixtures | backend unit fixtures or test factories | backend application domain |
| Public narrative denylist | `narrative_natal_reading_validator.py` tests | raw synthesis internals |
| Semantic integrity checks | `narrative_semantic_integrity.py` tests | final prose generator |

## Mandatory Reuse / DRY Constraints
- Reuse CS-413 `ThemeModel`, active theme outputs, fact IDs and eligibility metadata.
- Reuse existing validation denylist patterns for public text leaks before adding resolver-specific terms.
- Keep synthesis field definitions in one canonical resolver owner.
- Keep contradiction thresholds named and centralized in the resolver owner.
- Do not duplicate theme activation logic from CS-413.
- Do not add external packages.

## No Legacy / Forbidden Paths
- No legacy synthesis resolver path may be added for Basic.
- No compatibility synthesis resolver path may be added for Basic.
- No fallback synthesis resolver path may be added for Basic.
- Do not create a second Basic theme taxonomy.
- Do not expose `theme_code`, `confidence`, `merge_group` or `omission_reason` in public narrative text.
- Do not create an autonomous section candidate from one weak fact.
- Do not interpret houses, ASC or MC for date-only syntheses.
- Do not add medical, legal, financial or psychological recommendations.

## Reintroduction Guard
- Forbidden public synthesis symbols:
  - `theme_code`, `confidence`, `merge_group`, `omission_reason`.
- Forbidden absolute wording:
  - `toujours`, `jamais`, `destin`, `oblige`, `doit absolument`.
- Forbidden recommendation domains:
  - `medical`, `juridique`, `financier`, `psychologique`.
- Forbidden date-only interpretation markers:
  - `ascendant`, `maison`, `MC`, `Milieu du Ciel`.
- Required deterministic guards:
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py`.
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_synthesis_contradictions.py`.
  - `rg -n "toujours|jamais|destin|oblige|doit absolument|medical|juridique|financier" backend/app/domain/astrology/interpretation backend/app/services/llm_generation/natal`.

## Regression Guardrails
| Guardrail | Scope -> invariant -> evidence |
|---|---|
| RG-152 | public reading contract -> synthesis internals stay out of narrative fields -> public-boundary `pytest` and scan. |
| RG-154 | public text evidence boundary -> raw evidence identifiers stay out of public narrative text -> public-boundary scan. |
| RG-155 | semantic integrity -> no duplicated chapters or padding from unresolved themes -> semantic `pytest` coverage. |
| RG-156 | Basic coverage -> syntheses remain based on multiple astrology families -> resolver `pytest` corpus. |
| RG-022 | validation plan paths -> active pytest paths must be collectable -> targeted `pytest` commands. |
| RG-163 | mixed Basic synthesis -> strong mixed signals require nuance -> contradiction `pytest` and wording scan. |

Needs-investigation:
- The resolver returned `RG-002`, but no API route is touched; it is rejected as not local to this backend-domain story.

Registry enrichment:
- `RG-163` now protects mandatory nuance for mixed Basic themes with strong contradictory signals.

Non-applicable examples:
- `RG-047` frontend inline style is out of scope because no frontend surface is touched.
- `RG-052` frontend CSS namespace migration is out of scope because no CSS surface is touched.

## Persistent Evidence Artifacts
| Artifact | Path | Purpose |
|---|---|---|
| Resolver before snapshot | `_condamad/stories/CS-414-resoudre-contradictions-themes-natals-basic/evidence/before.json` | Capture baseline synthesis contract evidence. |
| Resolver after snapshot | `_condamad/stories/CS-414-resoudre-contradictions-themes-natals-basic/evidence/after.json` | Capture implemented resolver decisions. |
| Validation output | `_condamad/stories/CS-414-resoudre-contradictions-themes-natals-basic/evidence/validation.txt` | Keep lint, tests and scans output. |
| Review output | `_condamad/stories/CS-414-resoudre-contradictions-themes-natals-basic/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register
- Allowlist handling: not applicable
- Reason: no tolerance register is authorized for unilateral synthesis or forbidden wording.

## Batch Migration Plan
- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify
Likely files:
- `backend/app/domain/astrology/interpretation/natal_synthesis_resolver.py` - define resolver, resolved synthesis contract and rules.
- `backend/app/services/llm_generation/natal/narrative_semantic_integrity.py` - verify downstream semantic guard stays aligned.
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py` - verify public wording denylist stays aligned.
- `backend/tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py` - cover resolver fields, weak facts, redundancy and date-only.
- `backend/tests/unit/domain/astrology/test_basic_natal_synthesis_contradictions.py` - cover Venus, Moon, Jupiter and relationship contradictions.
- `_condamad/stories/CS-414-resoudre-contradictions-themes-natals-basic/evidence/validation.txt` - persist validation output.

Likely tests:
- `backend/tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py`
- `backend/tests/unit/domain/astrology/test_basic_natal_synthesis_contradictions.py`

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
- VC5: `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py --tb=short`
- VC6: `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_contradictions.py --tb=short`
- VC7: `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_theme_activation.py --tb=short`
- VC8: `rg -n "toujours|jamais|destin|oblige|doit absolument|medical|juridique|financier" app/domain/astrology/interpretation app/services/llm_generation/natal`
- VC9: `rg -n "theme_code|confidence|merge_group|omission_reason" app/services/llm_generation/natal`
- VC10: `rg -n "ascendant|maison|MC|Milieu du Ciel" app/domain/astrology/interpretation/natal_synthesis_resolver.py`

`rg` scan contract:
- VC8 forbidden pattern: `toujours|jamais|destin|oblige|doit absolument|medical|juridique|financier`.
- VC8 allowed fixture pattern: hits only in denylist definitions or tests documenting forbidden formulations.
- VC8 scan roots: `app/domain/astrology/interpretation`, `app/services/llm_generation/natal`.
- VC8 expected false positives: resolver denylist values and tests asserting guarded wording.
- VC9 forbidden pattern: `theme_code|confidence|merge_group|omission_reason`.
- VC9 allowed fixture pattern: tests may assert these fields remain absent from public narrative output.
- VC9 scan roots: `app/services/llm_generation/natal`.
- VC9 expected false positives: test names or assertions proving public-boundary absence.
- VC10 forbidden pattern: `ascendant|maison|MC|Milieu du Ciel`.
- VC10 allowed fixture pattern: controlled denylist or omission reason values only.
- VC10 scan roots: `app/domain/astrology/interpretation/natal_synthesis_resolver.py`.
- VC10 expected false positives: date-only guard constants and tests asserting absence from generated date-only statements.

## Regression Risks
- The resolver could become a deterministic prose writer instead of a controlled editorial synthesis layer.
- A strong resource could hide a strong constraint and produce one-sided output.
- Date-only synthesis could interpret unavailable houses, ASC or MC.
- Redundant themes could create duplicated future chapters.
- Forbidden absolute or prescriptive wording could enter downstream narrative generation.
- Internal resolver fields could leak into prompt-visible or public narrative surfaces.

## Dev Agent Instructions
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the Python venv before every Python, Ruff or Pytest command.
- Keep French file comments and docstrings for new or significantly modified application files.
- Preserve CS-413 taxonomy ownership and do not weaken public narrative guardrails.

## References
- `_story_briefs/cs-414-resoudre-contradictions-themes-natals-basic.md`
- `_story_briefs/cs-413-definir-taxonomie-themes-narratifs-basic.md`
- `_condamad/stories/CS-413-definir-taxonomie-themes-narratifs-basic/00-story.md`
- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/services/llm_generation/natal/narrative_semantic_integrity.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`
