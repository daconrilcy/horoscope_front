# Story CS-415 reading-plan-basic-natal-inspectable: Construire Reading Plan Basic Natal Inspectable
Status: ready-to-review

## Trigger / Source
- Source brief: `_story_briefs/cs-410-construire-reading-plan-basic-natal-inspectable.md`.
- Selected mode: Repo-informed story.
- Source dependency: CS-409 through CS-414 define the contracts, eligibility, facts, salience, themes and syntheses consumed here.
- Bounded problem: Basic natal generation lacks an inspectable `BasicNatalReadingPlan` before any LLM drafting.
- Source-alignment evidence: objectives, stakes, ACs, tasks, validations and non-goals map to the brief without scope drift.

## Objective
Create a deterministic `BasicNatalReadingPlan` builder that defines the Basic natal restitution contract before narrative generation.

## Target State
- `BasicNatalReadingPlan` contains `level=basic`, `locale`, `engine_version=basic-natal-reading-v1`, sections, public evidence and style constraints.
- The builder consumes `EligibilityContext`, `NatalFactGraph`, `NatalSalienceModel`, `ThemeModel` and `SynthesisResolver`.
- The plan emits six to eight sections maximum.
- Each section has a section code, target length, theme codes, required facts, forbidden facts and supporting public evidence IDs.
- Full birth-time plans can include synthesis, identity, inner life, vocation, relationships, talents, tensions and growth.
- Date-only plans exclude houses, ASC, MC and house rulers.
- Date-only plans use luminaries, signs, elements, modalities, values, action, aspects and growth by signs.
- Public evidence is readable for users and distinct from internal evidence.
- Public limitations and disclaimers are attached to the plan.
- Insufficiently proven sections are absent from the plan.
- Archetype tests prove that house 10 does not become the only Basic narrative model.

## Current State Evidence
- Evidence 1: `_story_briefs/cs-410-construire-reading-plan-basic-natal-inspectable.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-415`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted IDs `RG-149`, `RG-152`, `RG-154`, `RG-155`, `RG-156`, `RG-164` read.
- Evidence 4: `python -B .agents\skills\condamad-story-writer\scripts\resolve_guardrails.py` - scoped resolver executed.
- Evidence 5: `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md` - ReadingPlan source inspected.
- Evidence 6: `_story_briefs/cs-404-definir-contrats-versionnes-lecture-natale-basic-v2.md` - contract dependency inspected.
- Evidence 7: `_story_briefs/cs-405-classifier-eligibilite-heure-naissance-lecture-basic.md` - eligibility dependency inspected.
- Evidence 8: `_story_briefs/cs-406-construire-fact-graph-natal-basic-tracable.md` - fact graph dependency inspected.
- Evidence 9: `_story_briefs/cs-407-prioriser-faits-natals-basic-par-salience-calibree.md` - salience dependency inspected.
- Evidence 10: `_story_briefs/cs-408-definir-taxonomie-themes-narratifs-basic.md` - theme dependency inspected.
- Evidence 11: `_story_briefs/cs-409-resoudre-contradictions-themes-natals-basic.md` - synthesis dependency inspected.
- Evidence 12: `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py` - current narrative builder inspected.

Repository structure alert:
- `backend`, `backend/app` and `backend/tests` exist in this workspace.
- Expected new files may still need to be created by implementation under existing backend directories.

## Brief Primitive Ledger
| Primitive | Classification | Story mapping |
|---|---|---|
| `BasicNatalReadingPlan` | in scope | AC1, Task 1 |
| plan builder | in scope | AC2, Task 1 |
| `EligibilityContext` | in scope dependency | AC3, AC8, Task 2 |
| `NatalFactGraph` | in scope dependency | AC4, Task 3 |
| `NatalSalienceModel` | in scope dependency | AC5, Task 3 |
| `ThemeModel` | in scope dependency | AC6, Task 4 |
| `SynthesisResolver` | in scope dependency | AC7, Task 4 |
| six to eight sections | in scope | AC9, Task 5 |
| full birth-time order | in scope | AC10, Task 6 |
| date-only order | in scope | AC11, Task 7 |
| `required_fact_ids` | in scope | AC12, Task 8 |
| `supporting_evidence_ids` | in scope | AC13, Task 8 |
| forbidden facts | in scope | AC14, Task 9 |
| `public_evidence` | in scope | AC15, Task 10 |
| limitations | in scope | AC16, Task 11 |
| disclaimers | in scope | AC17, Task 11 |
| house 10 archetype | in scope test case | AC18, Task 12 |
| house 4 archetype | in scope test case | AC19, Task 12 |
| house 7 archetype | in scope test case | AC20, Task 12 |
| house 12 archetype | in scope test case | AC21, Task 12 |
| contradictions | in scope test case | AC22, Task 12 |
| LLM call | out of scope | Explicit non-goals |
| final content writing | out of scope | Explicit non-goals |
| persistence | out of scope | Explicit non-goals |
| frontend | out of scope | Explicit non-goals |
| Basic budgets increase | out of scope | Explicit non-goals |

## Domain Boundary
- Domain: backend-domain
- In scope:
  - Backend domain builder for `BasicNatalReadingPlan`.
  - Section selection, ordering, evidence mapping, limitations, disclaimers and style constraints.
  - Unit tests for full birth time, date-only, archetypes and contradictions.
  - Bounded scans proving public evidence does not leak internal scoring or prompt hints.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling, migrations, API routes and provider calls.
- Explicit non-goals:
  - No LLM call.
  - No final public prose generation.
  - No interpretation persistence change.
  - No frontend change.
  - No Basic word budget increase.
  - No new astrology calculation.

## Operation Contract
- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain reading plan builder contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only deterministic Basic natal reading plan construction from existing pipeline objects.
  - Keep the plan separated from final narrative rendering and provider prompts.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-409 through CS-414 outputs do not expose the required plan inputs.

Additional validation rules:
- Runtime evidence must include concrete `pytest -q backend/tests` paths.
- Architecture evidence must include `AST guard` or bounded `rg` scans for public-boundary leaks.
- Loaded contract evidence must prove section order, forbidden facts, public evidence and date-only omissions.

## Required Contracts
| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Builder runtime tests prove section selection, evidence IDs and eligibility behavior. |
| Baseline Snapshot | yes | Before and after plan artifacts prove the only allowed backend-domain delta. |
| Ownership Routing | yes | Canonical ownership is required because new backend domain files may be created. |
| Allowlist Exception | no | No tolerance register is authorized for leaked internals or unsupported sections. |
| Contract Shape | yes | Plan fields, section fields and public evidence fields are exact. |
| Batch Migration | no | No data migration or multi-record conversion is in scope. |
| Reintroduction Guard | yes | Internal scoring, prompt hints and date-only house markers must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria
| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The plan exposes Basic identity fields. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_builder.py`. |
| AC2 | The builder returns an inspectable plan. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_builder.py`. |
| AC3 | Eligibility controls plan surfaces. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_builder.py`. |
| AC4 | Fact graph IDs feed required facts. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_builder.py`. |
| AC5 | Salience controls section priority. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_builder.py`. |
| AC6 | Theme codes populate sections. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_builder.py`. |
| AC7 | Syntheses feed section intent. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_builder.py`. |
| AC8 | Date-only omits house surfaces. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_builder.py`. |
| AC9 | Plan section count stays bounded. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_builder.py`. |
| AC10 | Full birth-time order is stable. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_builder.py`. |
| AC11 | Date-only order is stable. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_builder.py`. |
| AC12 | Each section names required facts. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_builder.py`. |
| AC13 | Each content section names evidence. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_public_evidence.py`. |
| AC14 | Forbidden facts stay out of sections. | Evidence profile: ast_architecture_guard; `pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_builder.py`. |
| AC15 | Public evidence is user-readable. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_public_evidence.py`. |
| AC16 | Public limitations are emitted. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_public_evidence.py`. |
| AC17 | Required disclaimers are emitted. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_public_evidence.py`. |
| AC18 | House 10 is not the sole model. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_archetypes.py`. |
| AC19 | House 4 archetype has coverage. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_archetypes.py`. |
| AC20 | House 7 archetype has coverage. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_archetypes.py`. |
| AC21 | House 12 archetype has coverage. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_archetypes.py`. |
| AC22 | Contradictions shape plan nuance. | Evidence profile: json_contract_shape; `pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_archetypes.py`. |
| AC23 | Technical internals stay non-public. | Evidence profile: repo_wide_negative_scan; `rg` scan VC7. |

## Implementation Tasks
- [ ] Task 1: Define `BasicNatalReadingPlan` and its builder in the canonical interpretation domain. (AC: AC1, AC2)
- [ ] Task 2: Consume `EligibilityContext` as the only gate for houses, angles, ASC, MC and house rulers. (AC: AC3, AC8)
- [ ] Task 3: Consume `NatalFactGraph` and `NatalSalienceModel` without rebuilding fact extraction or scoring. (AC: AC4, AC5)
- [ ] Task 4: Consume `ThemeModel` and `SynthesisResolver` outputs without duplicating theme activation or synthesis rules. (AC: AC6, AC7)
- [ ] Task 5: Enforce the six to eight section budget in the builder. (AC: AC9)
- [ ] Task 6: Implement the full birth-time section order with optional vocation and relationship sections. (AC: AC10)
- [ ] Task 7: Implement the date-only section order without house, ASC, MC or house-ruler sections. (AC: AC8, AC11)
- [ ] Task 8: Attach `required_fact_ids` and `supporting_evidence_ids` to every content section. (AC: AC12, AC13)
- [ ] Task 9: Apply forbidden fact families before final section selection. (AC: AC14)
- [ ] Task 10: Build user-readable `public_evidence` from allowed editorial evidence only. (AC: AC15, AC23)
- [ ] Task 11: Add public limitations, disclaimers and style constraints to the plan. (AC: AC16, AC17)
- [ ] Task 12: Add archetype tests for date-only, houses 10, 4, 7, 12 and contradictions. (AC: AC18, AC19, AC20, AC21, AC22)
- [ ] Task 13: Add bounded scans for technical internals in public evidence and plan-facing text. (AC: AC23)

## Files to Inspect First
- `_story_briefs/cs-410-construire-reading-plan-basic-natal-inspectable.md`
- `_condamad/stories/CS-409-contrats-versionnes-lecture-natale-basic-v2/00-story.md`
- `_condamad/stories/CS-410-classifier-eligibilite-heure-naissance-basic/00-story.md`
- `_condamad/stories/CS-411-natal-fact-graph-basic-tracable/00-story.md`
- `_condamad/stories/CS-412-prioriser-faits-natals-basic-salience-calibree/00-story.md`
- `_condamad/stories/CS-413-definir-taxonomie-themes-narratifs-basic/00-story.md`
- `_condamad/stories/CS-414-resoudre-contradictions-themes-natals-basic/00-story.md`
- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `backend/app/domain/astrology/interpretation/basic_natal_reading_contracts.py`
- `backend/app/domain/astrology/interpretation/basic_natal_eligibility_context.py`
- `backend/app/domain/astrology/interpretation/natal_fact_graph.py`
- `backend/app/domain/astrology/interpretation/natal_salience_model.py`
- `backend/app/domain/astrology/interpretation/natal_theme_taxonomy.py`
- `backend/app/domain/astrology/interpretation/natal_synthesis_resolver.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py`

## Runtime Source of Truth
- Primary source of truth:
  - `BasicNatalReadingPlan` builder runtime, loaded dependency fixtures, plan serialization and `AST guard`.
- Secondary evidence:
  - Targeted `rg` scans for forbidden internal fields in public evidence and plan-facing text.
- Static scans alone are not sufficient for this story because:
  - Section ordering, evidence linking, date-only omission and archetype diversity must be proven by loaded runtime test data.

## Contract Shape
- Contract type:
  - Backend domain reading plan contract for Basic natal interpretation.
- Fields:
  - `level`: literal `basic`.
  - `locale`: BCP-47 locale string, initially `fr-FR`.
  - `engine_version`: literal `basic-natal-reading-v1`.
  - `sections`: bounded ordered list of plan sections.
  - `public_evidence`: readable evidence list for user-facing explanations.
  - `style_constraints`: controlled constraints for later narrative drafting.
  - `limitations`: readable public limitations.
  - `disclaimers`: required safety and scope disclaimers.
- Section fields:
  - `section_code`, `heading_intent`, `target_length_words`, `theme_codes`, `required_fact_ids`.
  - `forbidden_fact_ids`, `forbidden_fact_families`, `supporting_evidence_ids`.
- Public evidence fields:
  - `id`, `label`, `explanation`, `source_section_codes`.
- Required fields:
  - `level`, `locale`, `engine_version`, `sections`, `public_evidence`, `style_constraints`.
- Optional fields:
  - `limitations`, `disclaimers`.
- Status codes:
  - none; no API route is in scope.
- Serialization names:
  - Contract names stay identical to the field names above.
- Frontend type impact:
  - none; no frontend generated client is in scope.
- Generated contract impact:
  - none; no OpenAPI change is in scope.

## Baseline / Before-After Rule
- Baseline artifact before implementation:
  - `_condamad/stories/CS-415-reading-plan-basic-natal-inspectable/evidence/reading-plan-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-415-reading-plan-basic-natal-inspectable/evidence/reading-plan-after.json`
- Expected invariant:
  - The only intended domain delta is internal Basic natal reading plan construction before generation.

## Ownership Routing Rule
| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Reading plan builder | `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py` | backend API directory |
| Reading plan contracts | `backend/app/domain/astrology/interpretation/basic_natal_reading_contracts.py` | frontend source directory |
| Public evidence mapper | `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py` | LLM provider module |
| Plan archetype fixtures | `backend/tests/unit/domain/astrology` | backend application domain |
| Narrative builder integration | `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py` | frontend source directory |

## Mandatory Reuse / DRY Constraints
- Reuse CS-409 version constants and reading contracts.
- Reuse CS-410 eligibility gates for every house, angle, ASC, MC and house-ruler decision.
- Reuse CS-411 stable fact IDs and source paths instead of creating new fact identifiers.
- Reuse CS-412 salience levels and reason codes instead of adding a second priority system.
- Reuse CS-413 theme codes and activation results instead of duplicating theme taxonomy logic.
- Reuse CS-414 syntheses for section intent and nuance instead of rendering final prose.
- Keep section selection in one canonical builder owner.
- Do not add external packages.

## No Legacy / Forbidden Paths
- No legacy reading plan builder path may be added for Basic.
- No compatibility reading plan builder path may be added for Basic.
- No fallback reading plan builder path may be added for Basic.
- Do not add a second Basic contract family outside the canonical interpretation domain.
- Do not expose `ranking_score`, `condition_axis`, `score_profile`, `weighted_score` or `prompt_hint` in public evidence.
- Do not include `audit_input`, `source_paths` or raw internal evidence IDs in public evidence.
- Do not create sections without required facts.
- Do not create sections with empty supporting evidence when content requires evidence.
- Do not interpret houses, ASC, MC or house rulers in date-only plans.
- Do not call a provider or generate final public prose.

## Reintroduction Guard
- Forbidden public technical fields:
  - `ranking_score`, `condition_axis`, `score_profile`, `weighted_score`, `prompt_hint`, `audit_input`, `source_paths`.
- Forbidden date-only section markers:
  - `ascendant`, `maison`, `MC`, `Milieu du Ciel`, `ruler`, `maitre de maison`.
- Forbidden section anti-patterns:
  - duplicate section codes, empty evidence lists for content sections, house 10 as fixed universal model.
- Required deterministic guards:
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_reading_plan_builder.py`.
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_reading_plan_archetypes.py`.
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_public_evidence.py`.
  - `rg -n "ranking_score|condition_axis|score_profile|weighted_score|prompt_hint" backend/app/domain/astrology/interpretation backend/app/services/llm_generation/natal`.

## Regression Guardrails
| Guardrail | Scope -> invariant -> evidence |
|---|---|
| RG-149 | Basic pipeline -> reading plan replaces prompt-visible uncontrolled payloads -> builder `pytest` and boundary scan. |
| RG-152 | public reading contract -> technical fields stay out of user-facing plan data -> public evidence `pytest` and scan. |
| RG-154 | public denylist -> public evidence and limitations avoid internal identifiers -> public evidence `pytest` and scan. |
| RG-155 | semantic integrity -> no duplicate sections, padding sections or empty content evidence -> builder `pytest`. |
| RG-156 | Basic coverage -> plan remains diversified across astrology families and archetypes -> archetype `pytest`. |
| RG-164 | Basic plan owner -> `BasicNatalReadingPlan` governs Basic selection -> builder `pytest` and owner scan. |

Needs-investigation:
- Resolver output included `RG-002`, but no API route is touched; it is rejected as not local to this backend-domain story.
- Resolver output included `RG-047` and `RG-052`, but no frontend surface is touched; they are rejected as not local.

Registry enrichment:
- `RG-164` protects `BasicNatalReadingPlan` as the mandatory owner of Basic narrative selection.
- Implementation must cite `RG-164` in evidence and keep the owner scan aligned with the final files.

## Persistent Evidence Artifacts
| Artifact | Path | Purpose |
|---|---|---|
| Baseline plan snapshot | `_condamad/stories/CS-415-reading-plan-basic-natal-inspectable/evidence/reading-plan-before.json` | Capture pre-change plan absence or baseline. |
| Final plan snapshot | `_condamad/stories/CS-415-reading-plan-basic-natal-inspectable/evidence/reading-plan-after.json` | Capture implemented plan contract output. |
| Validation output | `_condamad/stories/CS-415-reading-plan-basic-natal-inspectable/evidence/validation.txt` | Keep command output for review. |
| Review output | `_condamad/stories/CS-415-reading-plan-basic-natal-inspectable/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register
- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for leaked internals, unsupported sections or date-only house surfaces.

## Batch Migration Plan
- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify
Likely files:

- `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py` - build the reading plan.
- `backend/app/domain/astrology/interpretation/basic_natal_reading_contracts.py` - expose the plan contracts.
- `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py` - consume the plan only at the narrative boundary.
- `_condamad/stories/CS-415-reading-plan-basic-natal-inspectable/evidence/reading-plan-before.json` - persist baseline evidence.
- `_condamad/stories/CS-415-reading-plan-basic-natal-inspectable/evidence/reading-plan-after.json` - persist final evidence.

Likely tests:

- `backend/tests/unit/domain/astrology/test_basic_natal_reading_plan_builder.py` - cover plan structure and date-only behavior.
- `backend/tests/unit/domain/astrology/test_basic_natal_reading_plan_archetypes.py` - cover house 10, 4, 7, 12 and contradiction cases.
- `backend/tests/unit/domain/astrology/test_basic_natal_public_evidence.py` - cover readable evidence, limitations and denylist.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no API route is touched.
- `backend/app/infra/**` - out of scope; no persistence or external adapter is touched.
- `backend/alembic/**` - out of scope; no migration is touched.

## Dependency Policy
- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan
- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_builder.py --tb=short`
- VC6: `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_archetypes.py --tb=short`
- VC7: `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_public_evidence.py --tb=short`
- VC8: `pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_builder.py`
- VC9: `pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_archetypes.py`
- VC10: `pytest -q tests/unit/domain/astrology/test_basic_natal_public_evidence.py`
- VC11: `rg -n "ranking_score|condition_axis|score_profile|weighted_score|prompt_hint" app/domain/astrology/interpretation app/services/llm_generation/natal`
- VC12: `rg -n "audit_input|source_paths|internal_evidence" app/domain/astrology/interpretation app/services/llm_generation/natal`
- VC13: `rg -n "ascendant|maison|MC|Milieu du Ciel|ruler|maitre de maison" tests/unit/domain/astrology/test_basic_natal_reading_plan_builder.py`

`rg` scan contracts:

- VC11 forbidden pattern: `ranking_score|condition_axis|score_profile|weighted_score|prompt_hint`.
- VC11 allowed fixture pattern: references inside denylist tests and internal audit-only fixtures.
- VC11 roots: `app/domain/astrology/interpretation`, `app/services/llm_generation/natal`.
- VC11 expected false positives: internal model fields not serialized to public evidence.
- VC12 forbidden pattern: `audit_input|source_paths|internal_evidence`.
- VC12 allowed fixture pattern: internal contract definitions and tests proving non-public separation.
- VC12 roots: `app/domain/astrology/interpretation`, `app/services/llm_generation/natal`.
- VC12 expected false positives: internal evidence contracts excluded from `public_evidence`.
- VC13 forbidden pattern: `ascendant|maison|MC|Milieu du Ciel|ruler|maitre de maison`.
- VC13 allowed fixture pattern: negative date-only assertions proving those markers are absent from plan output.
- VC13 roots: `tests/unit/domain/astrology/test_basic_natal_reading_plan_builder.py`.
- VC13 expected false positives: assertion names or literals used to prove date-only denial.

## Regression Risks
- A plan builder could duplicate salience or theme logic already owned by earlier pipeline steps.
- Date-only plans could accidentally include house, ASC, MC or house-ruler content.
- Public evidence could leak internal scores, source paths or prompt hints.
- Archetype coverage could overfit the house 10 fixture and flatten other charts.
- Sections could be padded without sufficient facts or supporting evidence.

## Dev Agent Instructions
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all new Python file comments and docstrings in French.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command.
- Keep all backend validations under `backend` after `cd backend` as listed in VC1 through VC7.
- Do not modify `_condamad/stories/regression-guardrails.md` during normal implementation.

## References
- `_story_briefs/cs-410-construire-reading-plan-basic-natal-inspectable.md`
- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `_story_briefs/cs-404-definir-contrats-versionnes-lecture-natale-basic-v2.md`
- `_story_briefs/cs-405-classifier-eligibilite-heure-naissance-lecture-basic.md`
- `_story_briefs/cs-406-construire-fact-graph-natal-basic-tracable.md`
- `_story_briefs/cs-407-prioriser-faits-natals-basic-par-salience-calibree.md`
- `_story_briefs/cs-408-definir-taxonomie-themes-narratifs-basic.md`
- `_story_briefs/cs-409-resoudre-contradictions-themes-natals-basic.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py`
