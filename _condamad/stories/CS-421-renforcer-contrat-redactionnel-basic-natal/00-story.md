# Story CS-421 renforcer-contrat-redactionnel-basic-natal: Renforcer Contrat Redactionnel Basic Natal
Status: ready-to-dev

## Trigger / Source

Brief direct from `_story_briefs/cs-421-renforcer-contrat-redactionnel-basic-natal.md`.

The bounded problem is that Basic natal V2 is exact at plan level but still reads like internal data assembly. The public output can expose raw labels,
generic source explanations, weak deterministic fallback prose, and no clear narrative thread for a non-initiated reader.

Source-alignment evidence: this story preserves the brief stakes by constraining the provider payload, public labels, validator, fallback workflow, snapshots,
and non-regression guards back to `BasicNatalReadingPlan` without adding astrology sources or frontend rendering work.

Drafting review note: the Contract Shape markers were corrected after validation diagnostics and must remain covered by story validation before implementation.

## Objective

Create a backend Basic natal editorial contract that turns `BasicNatalReadingPlan` facts into controlled narrative material for the provider, then rejects
public Basic text that remains mechanical, technical, unaccented, duplicated, or disconnected from the plan.

## Target State

- Basic provider payload includes a `BasicNatalEditorialBrief` derived only from `BasicNatalReadingPlan`.
- Each section receives a role, localized public labels, human meaning, possible manifestation, anti-fatalist nuance, usage limit, forbidden claims, and trace refs.
- The public Basic draft contains an introduction, narrative themes, a conclusion, and short source annexes rather than source listings as main content.
- The deterministic fallback stays plan-backed and audited with `fallback_used=True`; it rejects through the existing workflow when editorial quality is not met.
- Public accepted Basic content contains no PII, scores, raw IDs, paths, `chart_json`, `natal_data`, or raw English astrology labels.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-421-renforcer-contrat-redactionnel-basic-natal.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-421`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted guardrail IDs resolved for Basic natal backend scope.
- Evidence 4: `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py` - current plan owns sections and public evidence.
- Evidence 5: `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` - current provider payload includes Basic plan material.
- Evidence 6: `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py` - current validation and fallback workflow are in scope.
- Evidence 7: `backend/app/domain/astrology/reading/basic_natal_contracts.py` - current public Basic V2 contract owner is in scope.
- Evidence 8: CS-416, CS-417, CS-418, and CS-419 story contracts were checked as upstream Basic V2 constraints.
- Evidence 9: the source brief captures the user's current `/natal` DOM observations from 2026-05-31 as product evidence for mechanical public text.
- Repository structure alert: required backend roots exist; implementation must create only story-specific evidence files that are still missing.

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| `BasicNatalEditorialBrief` | in scope | AC1, AC3, tasks 1-2, expected files. |
| `BasicNatalReadingPlan` | in scope | AC1, AC3, AC12, runtime source of truth. |
| localized public labels | in scope | AC2, AC10, AC11, RG-109, RG-112. |
| controlled meaning per fact group | in scope | AC3, AC4, AC5, AC8. |
| provider payload fields | in scope | AC1, AC4, contract shape, snapshots. |
| `summary`, `introduction`, `Fil conducteur` | in scope | AC6, AC7, public contract shape. |
| deterministic fallback | in scope | AC12, validation plan. |
| public validator denylist | in scope | AC9, AC10, AC11, AC13. |
| fixture equivalent to `daconrilcy@hotmail.com` | in scope | AC14, likely tests. |
| CS-409 to CS-418 guards | in scope | AC15, regression guardrails. |
| frontend `/natal` rendering | out of scope | non-goals and files not expected to change. |
| prompt final assembly `theme_astral_prompt_v1` | out of scope | non-goals; CS-424 handles it. |
| historical reading regeneration | out of scope | non-goals; CS-425 handles it. |

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend Basic natal editorial brief model and builder derived from `BasicNatalReadingPlan`.
  - Backend provider payload enrichment for Basic natal.
  - Backend public Basic narrative validation and deterministic fallback contract.
  - Backend tests, snapshots, and scans for Basic natal editorial quality.
- Out of scope:
  - Frontend UI, database schema, auth, i18n routing, styling, build tooling, migrations, and quota or commerce behavior.
- Explicit non-goals:
  - No frontend route, screen, CSS, or client generation.
  - No astrology calculation changes.
  - No new astrology facts beyond the plan.
  - No provider live call in automated tests.
  - No Premium scope broadening.
  - No historical reading invalidation or regeneration.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend editorial contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only Basic natal editorial material derived from `BasicNatalReadingPlan`.
  - Strengthen public Basic validation without weakening CS-409 to CS-418 contracts.
  - Keep deterministic fallback inside the CS-417 workflow.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the required editorial quality cannot be reached without adding astrology sources outside the plan.
- Additional validation rules:
  - Runtime evidence must include `pytest -q backend/tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py --tb=short`.
  - Runtime evidence must include `pytest -q backend/tests/unit/test_basic_natal_narrative_validator.py backend/tests/unit/test_basic_natal_reading_contracts.py --tb=short`.
  - Runtime evidence must include `AST guard` or targeted `rg` scans proving no local astrology reference table was introduced.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `BasicNatalReadingPlan`, provider payload tests, validator tests, and `TestClient` pipeline tests prove runtime behavior. |
| Baseline Snapshot | yes | Before and after JSON snapshots prove the Basic payload and accepted public contract changed only as authorized. |
| Ownership Routing | yes | Editorial formatters must not become competing astrology owners. |
| Allowlist Exception | no | No broad allowlist handling is authorized for this Basic editorial contract. |
| Contract Shape | yes | Provider payload gains exact editorial fields and public Basic text keeps exact structure. |
| Batch Migration | no | No batch migration or historical regeneration is in scope. |
| Reintroduction Guard | yes | Mechanical phrases, raw labels, technical keys, and local astrology tables must stay absent. |
| Persistent Evidence | yes | Snapshots, scan classification, and validation output must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Basic payload contains section editorial briefs. | `pytest -q tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py`. |
| AC2 | Public evidence labels are localized for non-initiated readers. | `pytest -q tests/unit/domain/astrology/test_basic_natal_public_evidence.py`. |
| AC3 | Each section brief carries controlled human meaning. | `pytest -q tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py`. |
| AC4 | Provider payload prevents model-only interpretation from codes. | `pytest -q tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py`. |
| AC5 | Accepted Basic drafts explain facts instead of listing them. | `pytest -q tests/unit/test_basic_natal_narrative_validator.py`. |
| AC6 | `summary` cannot replace the introduction. | `pytest -q tests/unit/test_basic_natal_reading_contracts.py`. |
| AC7 | `Fil conducteur` is not rendered as an ordinary duplicate theme. | `pytest -q tests/unit/test_basic_natal_narrative_validator.py`. |
| AC8 | Each accepted theme contains at least two informative sentences. | `pytest -q tests/unit/test_basic_natal_narrative_validator.py`. |
| AC9 | Observed mechanical template phrases are rejected. | `pytest -q tests/unit/test_basic_natal_narrative_validator.py`; `rg` denylist. |
| AC10 | Raw English astrology labels are rejected from public text. | `pytest -q tests/unit/test_basic_natal_narrative_validator.py`; `rg` label scan. |
| AC11 | Unaccented French public forms are rejected. | `pytest -q tests/unit/test_basic_natal_narrative_validator.py`; `rg` accent scan. |
| AC12 | Deterministic fallback cannot publish mechanical text. | `pytest -q tests/unit/test_basic_natal_narrative_validator.py`. |
| AC13 | Disclaimers do not count as editorial content. | `pytest -q tests/unit/test_basic_natal_narrative_validator.py`. |
| AC14 | The user fixture produces readable plan-bounded Basic public text. | `pytest -q tests/integration/test_basic_natal_v2_pipeline.py`. |
| AC15 | CS-409 to CS-418 regression guards remain green. | `pytest -q tests/unit/test_basic_natal_reading_contracts.py`; `rg` scans. |
| AC16 | Story evidence artifacts are persisted. | `python -B -c` checks story `evidence` path. |

## Implementation Tasks

- [ ] Task 1: Define the internal `BasicNatalEditorialBrief` contract with section-level editorial fields. (AC: AC1, AC3)
- [ ] Task 2: Build editorial briefs exclusively from `BasicNatalReadingPlan` sections, evidence, and theme refs. (AC: AC1, AC3, AC4)
- [ ] Task 3: Resolve public labels through canonical translation/runtime owners or a pure presentation formatter. (AC: AC2, AC10, AC11)
- [ ] Task 4: Enrich `basic_natal_prompt_payload` with report arc, section briefs, glossary, denied phrases, and source policy. (AC: AC1, AC4)
- [ ] Task 5: Clarify the public Basic structure around `summary`, `introduction`, and `Fil conducteur`. (AC: AC6, AC7)
- [ ] Task 6: Strengthen the Basic validator against mechanical phrases, raw labels, weak themes, and disclaimer-only content. (AC: AC5, AC8, AC9, AC13)
- [ ] Task 7: Keep fallback inside the existing repair or rejection workflow with `fallback_used=True`. (AC: AC12)
- [ ] Task 8: Add or update tests proving the `daconrilcy@hotmail.com` equivalent fixture returns readable plan-bounded Basic text. (AC: AC14)
- [ ] Task 9: Persist before and after JSON snapshots for provider payload and public accepted contract. (AC: AC16)
- [ ] Task 10: Run regression tests and scans for CS-409 to CS-418 invariants. (AC: AC15)

## Files to Inspect First

- `_story_briefs/cs-421-renforcer-contrat-redactionnel-basic-natal.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/00-story.md`
- `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/00-story.md`
- `_condamad/stories/CS-418-integrer-basic-natal-v2-persistance-cache-qa/00-story.md`
- `_condamad/stories/CS-419-stabiliser-contrat-public-interpretation-natale-free-basic/00-story.md`
- `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py`
- `backend/app/domain/astrology/interpretation/natal_fact_graph.py`
- `backend/app/domain/astrology/interpretation/natal_theme_taxonomy.py`
- `backend/app/domain/astrology/runtime`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`
- `backend/app/domain/astrology/reading/basic_natal_contracts.py`
- `backend/tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py`
- `backend/tests/unit/test_basic_natal_narrative_validator.py`
- `backend/tests/unit/test_basic_natal_reading_contracts.py`

## Runtime Source of Truth

- Primary source of truth:
  - `BasicNatalReadingPlan`, `BasicNatalInterpretationV2`, provider payload tests, validator tests, and Basic V2 integration tests.
- Runtime evidence:
  - `pytest -q backend/tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py --tb=short`.
  - `pytest -q backend/tests/unit/test_basic_natal_narrative_validator.py backend/tests/unit/test_basic_natal_reading_contracts.py --tb=short`.
  - `pytest -q backend/tests/integration/test_basic_natal_v2_pipeline.py --tb=short`.
- Secondary evidence:
  - `AST guard` or targeted `rg` scans prove no competing astrology reference owner was introduced.
- Static scans alone are not sufficient for this story because:
  - Accepted public text, fallback behavior, and payload shape must be proven from runtime tests.

## Contract Shape

- Contract type:
  - Backend provider payload and public Basic narrative contract.
- Fields:
  - `report_arc`: short narrative thread derived from plan sections.
  - `section_editorial_briefs`: list matching authorized plan sections.
  - `plain_language_glossary`: public localized vocabulary for included facts.
  - `forbidden_template_phrases`: phrase denylist used by provider instructions and validator tests.
  - `source_usage_policy`: rule that sources are annex evidence, not main section prose.
- Required fields:
  - `public_label`
  - `reader_meaning`
  - `possible_manifestation`
  - `nuance`
  - `allowed_section_role`
  - `forbidden_claims`
  - `source_fact_refs`
- Public contract required structure:
  - `introduction` gives the narrative thread.
  - `themes` contain explanatory narrative sections.
  - `conclusion` synthesizes without prescribing.
  - `public_evidence` remains an annex-style source surface.
- Optional fields:
  - none for the new section editorial brief minimum.
- Status codes:
  - No HTTP status code contract changes are in scope.
- Serialization names:
  - New provider payload fields use the exact snake_case names listed above.
- Frontend type impact:
  - none; CS-422 owns `/natal` rendering changes.
- Generated contract impact:
  - snapshots must show authorized Basic payload and public contract shape.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/evidence/basic-payload-before.json`
  - `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/evidence/basic-public-contract-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/evidence/basic-payload-after.json`
  - `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/evidence/basic-public-contract-after.json`
- Expected invariant:
  - The only intended surface delta is Basic editorial material and stricter Basic public validation.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Plan-backed fact selection | `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py` | Provider prompt assembly or validator recalculation. |
| Public Basic contract | `backend/app/domain/astrology/reading/basic_natal_contracts.py` | API route, frontend, or persistence layer. |
| Provider payload assembly | `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` | Service orchestration or UI code. |
| Draft validation and fallback | `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py` | Provider payload builder. |
| Localized astrology labels | Existing translation/runtime owners or pure presentation formatter | New local astrology reference table. |

## Mandatory Reuse / DRY Constraints

- Reuse `BasicNatalReadingPlan`; do not recalculate natal facts.
- Reuse existing astrology translation/runtime owners for labels.
- Keep any presentation formatter pure, deterministic, and derived from canonical owners.
- Do not duplicate validation denylist patterns between runtime code and tests without one named owner.
- Keep tests focused on Basic natal editorial quality rather than broad prompt-generation behavior.

## No Legacy / Forbidden Paths

- No legacy Basic payload path may be added.
- No compatibility Basic public contract may be added.
- No fallback path may bypass CS-417 validation, audit metadata, or rejection workflow.
- No raw `chart_json`, `natal_data`, PII, scores, file paths, prompt hints, audit inputs, or raw fact IDs may enter public Basic text.
- No local astrology reference table may be introduced for signs, planets, nodes, aspects, houses, axes, or rulerships.

## Reintroduction Guard

- Guard forbidden public phrases with validator tests and a bounded `rg` scan.
- Guard raw English astrology labels with validator tests and a bounded `rg` scan.
- Guard unaccented public French forms with validator tests and a bounded `rg` scan.
- Guard local astrology reference tables with a bounded `rg` scan over astrology, provider payload, and validator surfaces.
- Guard fallback publication by proving `fallback_used=True` plus rejection when editorial quality is below threshold.

## Regression Guardrails

Scope vector: create, backend-domain, Basic natal editorial payload, Basic public contract, validator, fallback, localized labels, no local astrology reference.

| Guardrail | Scope -> invariant -> evidence |
|---|---|
| RG-109 `localized-labels` | Label formatting -> canonical translation owners -> translation resolver pytest plus local table `rg` scan. |
| RG-112 `astrology-reference-ownership` | Editorial formatter -> no competing astrology tables -> `AST guard` or table-pattern `rg` scan. |
| RG-154 `public-technical-markers` | Public Basic text -> no technical markers in user-facing content -> validator pytest plus denylist `rg` scan. |
| RG-152 `public-technical-boundary` | Basic public text -> no technical carriers -> public contract pytest plus technical-key `rg` scan. |
| RG-155 `semantic-integrity` | Basic narrative -> no padding or duplicate chapters -> validator pytest. |
| RG-156 `basic-editorial-coverage` | Basic material -> diverse plan-driven content -> payload builder pytest. |
| RG-164 `basic-plan-owner` | Fact selection -> `BasicNatalReadingPlan` remains owner -> plan and payload pytests. |
| RG-165 `basic-payload-privacy` | Provider payload -> no PII, scores, paths, raw IDs -> payload pytest plus privacy `rg` scan. |
| RG-166 `basic-validation` | Accepted drafts -> match reading plan -> validator pytest. |
| RG-167 `basic-runtime-engine` | Runtime Basic complete -> uses `basic-natal-reading-v1` -> integration pytest. |
| RG-168 `basic-public-contract` | Public Basic V2 -> canonical contract unchanged -> contract pytest and architecture pytest. |

Needs-investigation: resolver returned RG-002 and RG-022 as broad backend matches; the brief-specific IDs above are more local to this story.

Registry gap: the brief asks for future `RG-169` only if implementation creates a durable editorial-quality invariant; normal story generation does not update the registry.

Non-applicable examples:

- RG-047 is frontend inline-style-focused; this story does not touch TSX or CSS.
- RG-052 is frontend CSS-migration-focused; this story does not touch style assets.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Payload baseline | `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/evidence/basic-payload-before.json` | Capture current Basic provider payload. |
| Payload after | `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/evidence/basic-payload-after.json` | Prove authorized editorial payload delta. |
| Public contract baseline | `evidence/basic-public-contract-before.json` | Capture current accepted public shape. |
| Public contract after | `evidence/basic-public-contract-after.json` | Prove accepted public shape after change. |
| Scan classification | `evidence/scan-classification.md` | Classify denylist hits as tests, guards, evidence, or blockers. |
| Validation output | `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/evidence/validation-output.txt` | Keep executed validation proof. |
| Review output | `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no broad allowlist is authorized; scan hits must be classified as tests, guards, historical evidence, or blockers.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py` - expose plan-backed material required by editorial brief.
- `backend/app/domain/astrology/interpretation/basic_natal_editorial_brief.py` - expected new pure editorial brief builder.
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` - add Basic editorial payload fields.
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py` - enforce editorial quality and denied public phrases.
- `backend/app/domain/astrology/reading/basic_natal_contracts.py` - clarify public Basic structure invariants.
- `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/evidence/*.json` - persist before and after snapshots.
- `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/evidence/scan-classification.md` - classify scan hits.
- `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/evidence/validation-output.txt` - persist validation proof.

Likely tests:

- `backend/tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py`
- `backend/tests/unit/test_basic_natal_narrative_validator.py`
- `backend/tests/unit/test_basic_natal_reading_contracts.py`
- `backend/tests/integration/test_basic_natal_v2_pipeline.py`
- `backend/app/tests/unit/test_astrology_translation_resolver.py`
- `backend/tests/unit/domain/astrology/test_basic_natal_public_evidence.py`

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/infra/**` - out of scope; no persistence or external adapter is touched.
- `backend/alembic/**` - out of scope; no migration is touched.
- `backend/app/api/**` - out of scope; no route contract is changed.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

All Python commands must run after `.\\.venv\\Scripts\\Activate.ps1`.

- VC1: from repository root run `cd backend; ruff format .`.
- VC2: from repository root run `cd backend; ruff check .`.
- VC3: from `backend` run `python -B -m pytest -q tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py --tb=short`.
- VC4: from `backend` run Basic narrative validator and reading contract pytests with `--tb=short`.
- VC5: from `backend` run `python -B -m pytest -q tests/integration/test_basic_natal_v2_pipeline.py --tb=short`.
- VC6: from `backend` run `python -B -m pytest -q app/tests/unit/test_astrology_translation_resolver.py --tb=short`.
- VC7: forbidden pattern `cette lecture s'appuie uniquement|Ce repere retient|avec une confiance editoriale controlee|Luminaire: moon|Position planetaire:|north node|south node`;
  allowed hits are negative tests, denylist constants, or historical evidence under `app tests`.
- VC8: forbidden pattern `\\b(Synthese|theme|themes|repere|planetaire|a integrer)\\b`;
  allowed hits are negative tests or denylist constants under astrology, LLM runtime, validator, and backend tests roots.
  expected false positives documented in scan classification.
- VC9: forbidden pattern `ranking_score|condition_axis|score_profile|weighted_score|prompt_hint|audit_input|chart_json|natal_data`;
  allowed hits are validators, denylist tests, or private audit assertions under reading, LLM runtime, and validator roots.
  expected false positives documented in scan classification.
- VC10: forbidden pattern `SIGN_NAMES_FR|SIGN_LABELS|PLANET_LABELS|NODE_LABELS|ASPECT_LABELS|\\bSIGNS\\s*=\\s*\\[`;
  allowed hits are exact existing documented guards under astrology, LLM runtime, and validator roots.
  expected false positives documented in scan classification.
- VC11: from repository root run a `python -B -c` path-existence check for the story evidence directory.

## Regression Risks

- Editorial enrichment could invent meaning not backed by the plan; AC3, AC4, RG-164, and snapshots constrain this.
- Label localization could recreate local astrology reference tables; RG-109, RG-112, and VC10 constrain this.
- Stronger validation could accept disclaimer-only content as narrative; AC13 constrains this.
- Fallback could become a second silent narrative engine; AC12 constrains this.
- Public contract changes could weaken CS-409 to CS-418; AC15 constrains this.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all new or significantly changed applicative files documented with a French top-of-file comment and French docstrings.
- Do not call a live provider from automated tests.
- Persist evidence artifacts before requesting review.

## References

- `_story_briefs/cs-421-renforcer-contrat-redactionnel-basic-natal.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/00-story.md`
- `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/00-story.md`
- `_condamad/stories/CS-418-integrer-basic-natal-v2-persistance-cache-qa/00-story.md`
- `_condamad/stories/CS-419-stabiliser-contrat-public-interpretation-natale-free-basic/00-story.md`
- `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py`
- `backend/app/domain/astrology/interpretation/natal_fact_graph.py`
- `backend/app/domain/astrology/interpretation/natal_theme_taxonomy.py`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`
- `backend/app/domain/astrology/reading/basic_natal_contracts.py`
