# Story CS-365 interpretation-material-builder-theme-astral: Implement Interpretation Material Builder For Theme Astral
Status: done

## Trigger / Source

- Mode: Repo-informed story from implementation brief.
- Source brief: `_story_briefs/cs-365-implementer-interpretation-material-builder-theme-astral.md`.
- Source problem: `theme_astral` exposes mostly calculated facts while the target LLM input requires structured interpretive material.
- Source stakes:
  - User impact: generated theme astral text needs selected, sourced, scored material instead of an encyclopedic dump.
  - Technical risk: prompt builders could fabricate interpretive text or bypass audited DB/reference text owners.
  - Closure expectation: implement one builder that feeds `theme_astral_llm_input_v1` with stable `interpretation_material`.
  - Forbidden regression: gateway provider, output schemas, provider calls, frontend UI, DB migrations, and source text creation stay unchanged.
- Source-alignment review: PASS. Objective, target state, ACs, tasks, evidence, non-goals, and guardrails map to the brief stakes.

## Objective

Implement `InterpretationMaterialBuilder` for `theme_astral`.

The builder must consume calculated astrology facts, reuse audited interpretation text owners, attach every item to a calculated fact, score and
limit selections by delivery profile, and return stable `interpretation_material` for `theme_astral_llm_input_v1`.

## Target State

`theme_astral_llm_input_v1` can receive an `interpretation_material` block with the same top-level keys for `free`, `basic`, and `premium`.

The block shape is:

- `planet_sign_interpretations`
- `planet_house_interpretations`
- `aspect_interpretations`
- `dominant_themes`
- `tensions`
- `resources`
- `integration_levers`
- `warnings`

Every item contains:

- `source_ref`
- `fact_ref`
- `theme`
- `keywords`
- `interpretive_text` or `writing_hint`
- `risk`
- `resource`
- `weight`
- `selection_reason`

`free`, `basic`, and `premium` share the same keys. Delivery profiles change item quantities, scoring thresholds, and selection depth only.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-365-implementer-interpretation-material-builder-theme-astral.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-365`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/00-story.md` - source audit story read.
- Evidence 5: `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/00-story.md` - architecture story read.
- Evidence 6: `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - current LLM input builder read.
- Evidence 7: `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py` - current calculated fact projection owner read.
- Evidence 8: `backend/app/infra/db/repositories/astral_point_interpretation_repository.py` - existing DB text repository read.
- Evidence 9: targeted `rg` found aspect interpretation, dominance, LLM input, source, and fact surfaces under backend astrology paths.
- Evidence 10: scoped guardrail resolver returned `RG-002`, `RG-022`, `RG-047`, and `RG-052`; only backend-local guardrails apply.
- Registry gap: no exact guardrail covers `theme_astral` interpretation material builder selection and non-invention.
- Repository structure alert: none. `backend`, `backend/app`, `backend/tests`, `frontend`, and `frontend/src` exist.
- Assumption risk: CS-361 and CS-363 deliverable reports may be produced by their own stories before CS-365 implementation starts.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend domain/service builder for `theme_astral` interpretation material.
  - Reuse of existing calculated astrology facts from `ChartInterpretationInputBuilder` and related runtime projections.
  - Reuse of existing DB/reference text owners for point, planet, house, sign, aspect, dominance, tension, resource, and warning material.
  - Matching calculated facts to sourced interpretation rows with `source_ref` and `fact_ref`.
  - Selection, scoring, ranking, and profile-specific quantity limits for `free`, `basic`, and `premium`.
  - DTO or contract classes for stable `interpretation_material` shape.
  - Unit tests for fact-to-text matching, source provenance, scoring, profile quantities, and stable keys.
  - Integration tests proving the material reaches the LLM input construction boundary without provider calls.
- Out of scope:
  - Gateway provider changes, output schema changes, provider calls, frontend UI, auth, i18n, styling, build tooling, and DB migrations.
  - Creating a new source of interpretation texts when existing tables and references satisfy the contract.
  - Changing prompt prose, real LLM calls, or provider payload output schema persistence.
  - Guardrail registry maintenance or enrichment.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
  - No SQL in UI and no direct DB access from prompt, provider, or frontend code.
  - No provider gateway edit.
  - No output schema edit.
  - No new migration.

Named brief primitives in scope:

- `InterpretationMaterialBuilder`
- `theme_astral`
- `theme_astral_llm_input_v1`
- `interpretation_material`
- `planet_sign_interpretations`
- `planet_house_interpretations`
- `aspect_interpretations`
- `dominant_themes`
- `tensions`
- `resources`
- `integration_levers`
- `warnings`
- `source_ref`
- `fact_ref`
- `delivery_profile`

Named brief primitives out of scope:

- `gateway provider`
- `output schemas`
- `LLM provider call`
- `new interpretation source`
- `frontend UI`
- `DB migration`

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain interpretation material builder.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add the builder, DTO or contract classes, and wiring required for `theme_astral_llm_input_v1`.
  - Reuse existing interpretation repositories, runtime projections, and domain facts.
  - Keep gateway provider behavior unchanged.
  - Keep output schema definitions unchanged.
  - Keep frontend files unchanged.
  - Keep migrations unchanged.
  - Keep source text tables and seeds unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: audited source text owners cannot cover a required material family without creating new text sources.
- Additional validation rules:
  - `AST guard` must prove builder ownership stays under `backend/app/domain/astrology/interpretation`.
  - A full `pytest -q backend/tests/unit/domain/astrology/interpretation/test_interpretation_material_builder.py` path must prove matching behavior.
  - A full `pytest -q backend/tests/integration/astrology/test_theme_astral_interpretation_material_input.py` path must prove LLM input handoff.
  - Tests must prove no `interpretation_material` item is emitted without `source_ref` and `fact_ref`.
  - Tests must prove each item emits `interpretive_text` or `writing_hint`.
  - Tests must prove `free`, `basic`, and `premium` keep identical top-level keys with different allowed quantities.
  - Targeted `rg` must prove no SQL access is added outside infra repositories.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `AST guard`, loaded builder tests, and integration tests prove fact-to-text runtime behavior. |
| Baseline Snapshot | yes | Before and after scans prove the only allowed surface delta is the builder contract and tests. |
| Ownership Routing | yes | Builder, repositories, DTOs, LLM input, and tests need clear canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this builder story. |
| Contract Shape | yes | `interpretation_material` has exact keys and required item fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Prompt/provider fabrication and UI or SQL bypass paths must stay absent. |
| Persistent Evidence | yes | Source scans, shape checks, validation output, and review handoff must persist. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The builder has one canonical owner. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks `InterpretationMaterialBuilder`. |
| AC2 | Material keys are stable. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/interpretation/test_interpretation_material_builder.py`. |
| AC3 | Planet-sign facts match sourced text. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/interpretation/test_interpretation_material_builder.py`. |
| AC4 | Planet-house facts match sourced text. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/interpretation/test_interpretation_material_builder.py`. |
| AC5 | Aspect facts match sourced text. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/interpretation/test_interpretation_material_builder.py`. |
| AC6 | Items have `source_ref`. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/interpretation/test_interpretation_material_builder.py`. |
| AC7 | Items have `fact_ref`. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/interpretation/test_interpretation_material_builder.py`. |
| AC8 | Missing source text emits no item. | Evidence profile: no_legacy_contract; `tests/unit/domain/astrology/interpretation/test_interpretation_material_builder.py`. |
| AC9 | Profiles limit quantities. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/interpretation/test_interpretation_material_builder.py`. |
| AC10 | LLM input gets material. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/integration/astrology/test_theme_astral_interpretation_material_input.py`. |
| AC11 | Protected surfaces stay unchanged. | Evidence profile: repo_wide_negative_scan; `AST guard`; `python` checks bounded git diff. |
| AC12 | Story evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks evidence and generated paths. |
| AC13 | Items have `interpretive_text` or `writing_hint`. | Evidence profile: json_contract_shape; `test_interpretation_material_builder.py`. |

## Implementation Tasks

- [ ] Task 1: Read CS-361 and CS-363 deliverables or record exact assumption risk in evidence. (AC: AC1, AC12)
- [ ] Task 2: Define `InterpretationMaterialBuilder` under the canonical astrology interpretation owner. (AC: AC1)
- [ ] Task 3: Define DTO or contract classes for `interpretation_material` keys and item fields. (AC: AC2)
- [ ] Task 4: Reuse existing repository services for point, planet, house, sign, and aspect interpretation text. (AC: AC3, AC4, AC5)
- [ ] Task 5: Match calculated facts to text rows and require `source_ref`, `fact_ref`, and source text or hint. (AC: AC3, AC4, AC5, AC6, AC7, AC13)
- [ ] Task 6: Add non-invention behavior so missing source text produces no material item. (AC: AC8)
- [ ] Task 7: Score, rank, and limit selected items for `free`, `basic`, and `premium`. (AC: AC9)
- [ ] Task 8: Wire the material block into the theme astral LLM input construction boundary. (AC: AC10)
- [ ] Task 9: Add unit tests for shape, matching, provenance, non-invention, scoring, and quantities. (AC: AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9)
- [ ] Task 10: Add integration coverage for LLM input handoff without provider calls. (AC: AC10)
- [ ] Task 11: Run validation commands, persist output, and prove protected surfaces stay unchanged. (AC: AC11, AC12)

## Files to Inspect First

- `_story_briefs/cs-365-implementer-interpretation-material-builder-theme-astral.md` - source scope.
- `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/00-story.md` - prerequisite audit contract.
- `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/00-story.md` - target architecture contract.
- `_condamad/audits/theme-astral-prompt-contract/**/01-audit-usage-tables-textes-interpretation.md` - audit deliverable input.
- `_condamad/architecture/theme-astral-prompt-contract/**/archi-theme-astral-prompt-contract-v1.md` - architecture deliverable input.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - current LLM input owner.
- `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py` - calculated fact projection owner.
- `backend/app/domain/astrology/interpretation/aspect_interpretation_builder.py` - existing aspect text builder pattern.
- `backend/app/domain/astrology/interpretation/aspect_interpretation_contracts.py` - aspect interpretation DTO pattern.
- `backend/app/domain/astrology/interpretation/astral_point_interpretation.py` - existing point interpretation DTOs.
- `backend/app/infra/db/repositories/astral_point_interpretation_repository.py` - existing point text repository.
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py` - runtime reference repository owner.
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` - runtime reference mapper owner.
- `backend/app/infra/db/models/interpretation_reference.py` - interpretation text models.
- `backend/app/infra/db/models/translation_reference.py` - localized interpretation translation models.
- `backend/tests/unit/domain/astrology/interpretation/**` - existing interpretation builder tests.
- `backend/tests/integration/astrology/**` - integration tests for astrology runtime and input handoff.

## Runtime Source of Truth

- Primary source of truth:
  - `ChartInterpretationInputBuilder` and existing runtime projections for calculated fact inputs.
  - Existing interpretation repositories and reference models for source text.
  - `InterpretationMaterialBuilder` tests under `backend/tests/unit/domain/astrology/interpretation`.
  - Integration test `backend/tests/integration/astrology/test_theme_astral_interpretation_material_input.py`.
  - `AST guard` for ownership and import direction.
- Secondary evidence:
  - Targeted `rg` scans for material keys, source and fact references, provider surface names, and SQL surface boundaries.
  - Bounded git diff checks proving provider, output schema, frontend, and migration surfaces stay unchanged.
- Static scans alone are not sufficient for this story because:
  - Matching, ranking, quantity limits, and non-invention must be proven from loaded builder behavior and integration tests.

## Contract Shape

- Contract type:
  - Backend domain DTO or serializable mapping for `theme_astral_llm_input_v1.input_data.interpretation_material`.
- Fields:
  - `planet_sign_interpretations`: sourced items matching planet plus sign facts.
  - `planet_house_interpretations`: sourced items matching planet plus house facts.
  - `aspect_interpretations`: sourced items matching calculated aspect facts.
  - `dominant_themes`: ranked themes derived from calculated dominance and sourced interpretation signals.
  - `tensions`: ranked sourced risks or shadow axes attached to calculated facts.
  - `resources`: ranked sourced resources attached to calculated facts.
  - `integration_levers`: ranked writing or integration hints attached to calculated facts.
  - `warnings`: sourced limits and caution notes attached to calculated facts.
- Required fields:
  - `source_ref`
  - `fact_ref`
  - `theme`
  - `keywords`
  - `risk`
  - `resource`
  - `weight`
  - `selection_reason`
- Required text field rule:
  - Each item contains `interpretive_text` or `writing_hint`.
- Optional fields:
  - none.
- Status codes:
  - none; no API route is created or changed.
- Serialization names:
  - Top-level keys and item keys are emitted exactly as listed in this section.
- Frontend type impact:
  - none.
- Generated contract impact:
  - none; this story does not change provider output schemas or generated frontend contracts.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/evidence/source-availability.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/evidence/material-shape-check.txt`
- Expected invariant:
  - The only intended app surface delta is the backend domain interpretation material builder, its DTO or contract support, and its tests.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Interpretation material builder | `backend/app/domain/astrology/interpretation/` | `backend/app/domain/llm/runtime/` |
| Source text loading | `backend/app/infra/db/repositories/**` | `backend/app/domain/astrology/interpretation/**` raw SQL |
| Material DTO or contract | `backend/app/domain/astrology/interpretation/` | `frontend/src/**` |
| LLM input handoff | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | provider gateway code |
| Unit builder tests | `backend/tests/unit/domain/astrology/interpretation/` | integration-only coverage |
| Integration handoff tests | `backend/tests/integration/astrology/` | provider live tests |
| Story evidence | `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/evidence/` | `backend/tests/**` |

## Mandatory Reuse / DRY Constraints

- Reuse CS-361 and CS-363 findings as source inputs instead of re-auditing broad prompt surfaces.
- Reuse `ChartInterpretationInputBuilder` fact projection instead of rebuilding natal fact extraction.
- Reuse existing interpretation repositories and runtime reference repositories instead of copying queries into domain builders.
- Reuse existing aspect interpretation contracts and point interpretation DTO patterns for item shape.
- Use one scoring and quantity policy source for all material families.
- Use one top-level key skeleton for `free`, `basic`, and `premium`.
- Keep validation commands centralized in the Validation Plan and persist their output once.
- Do not introduce new dependencies.

## No Legacy / Forbidden Paths

- No legacy prompt carrier may produce `interpretation_material`.
- No compatibility prompt carrier may produce `interpretation_material`.
- No fallback prompt carrier may fabricate source text.
- No hidden residual source of interpretive material may exist outside repository-backed or audited runtime sources.
- Do not add SQL queries to frontend, prompt builders, provider gateway, or domain builders.
- Do not edit provider gateway code, output schema files, frontend files, migrations, source text seeds, or guardrail registry entries.
- Do not emit an item without both `source_ref` and `fact_ref`.
- Do not create parallel profile-specific top-level key sets.

## Reintroduction Guard

- The builder must reject or omit unsourced material instead of fabricating text.
- The builder must attach each item to a calculated fact reference.
- The validation plan must include targeted `rg` guards for provider gateway, output schema, migration, frontend, SQL, and material keys.
- The validation plan must include `pytest` proof for stable shape, non-invention, delivery profile quantities, and runtime LLM input handoff.
- The validation output must include a bounded git diff guard proving protected surfaces are unchanged.

## Regression Guardrails

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend app layout remains canonical and no API router ownership is hijacked. | `AST guard`; `rg` ownership scan. |
| RG-022 `align-prompt-generation-story-validation-paths` | Backend validation paths stay explicit and collected. | `pytest` paths; validation artifact. |
| Registry gap | No exact guardrail covers theme astral material selection and non-invention. | Resolver output saved in evidence. |

Non-applicable examples:

- `RG-047` frontend inline styles is out of scope because no frontend source is touched.
- `RG-052` frontend CSS namespace migration is out of scope because no style source is touched.
- `RG-041` entitlement documentation is out of scope because no entitlement surface is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Source availability | `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/evidence/source-availability.txt` | Prove required sources. |
| Source scan | `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/evidence/source-scan.txt` | Store targeted source scans. |
| Material shape check | `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/evidence/material-shape-check.txt` | Prove material keys. |
| Non-invention proof | `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/evidence/non-invention-proof.txt` | Prove source and fact refs. |
| Validation output | `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/evidence/validation.txt` | Store validation commands. |
| Review output | `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist Exception: not applicable
- Reason: no allowlist handling is authorized for this builder story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/interpretation/interpretation_material_contracts.py` - stable material DTO or contract classes.
- `backend/app/domain/astrology/interpretation/interpretation_material_builder.py` - builder implementation.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - add material handoff to theme astral input.
- `backend/app/domain/astrology/interpretation/__init__.py` - export canonical builder or contracts.
- `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/evidence/source-availability.txt` - source evidence.
- `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/evidence/source-scan.txt` - source scan.
- `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/evidence/material-shape-check.txt` - shape evidence.
- `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/evidence/non-invention-proof.txt` - provenance evidence.
- `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/evidence/validation.txt` - validation output.
- `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/generated/11-code-review.md` - generated review handoff.

Likely tests:

- `backend/tests/unit/domain/astrology/interpretation/test_interpretation_material_builder.py` - shape, matching, provenance, scoring, quantities.
- `backend/tests/integration/astrology/test_theme_astral_interpretation_material_input.py` - LLM input handoff without provider calls.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` - adapt existing input contract tests.
- `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py` - adapt audit-only boundary coverage.

Files not expected to change:

- `backend/app/domain/llm/runtime/**` - out of scope; provider runtime handoff remains unchanged.
- `backend/app/infra/db/models/**` - out of scope; no schema model change is authorized.
- `backend/migrations/**` - out of scope; no migration is authorized.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `_condamad/stories/regression-guardrails.md` - out of scope; no registry enrichment is authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

All Python commands must run after `.\.venv\Scripts\Activate.ps1`.
Run VC13 from `backend` after activation unless the command path starts with `_condamad`.

- VC1: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-365-interpretation-material-builder-theme-astral/evidence/source-availability.txt').exists()"`
- VC2: `rg -n "InterpretationMaterialBuilder|interpretation_material|planet_sign_interpretations|planet_house_interpretations" app tests`
- VC3: `rg -n "aspect_interpretations|dominant_themes|tensions|resources|integration_levers|warnings" app tests`
- VC4: `rg -n "source_ref|fact_ref|interpretive_text|writing_hint|selection_reason|delivery_profile|free|basic|premium" app tests`
- VC5: `pytest -q tests/unit/domain/astrology/interpretation/test_interpretation_material_builder.py`
- VC6: `pytest -q tests/integration/astrology/test_theme_astral_interpretation_material_input.py`
- VC7: `pytest -q tests/unit/domain/astrology/test_llm_astrology_input_v1.py`
- VC8: `pytest -q tests/integration/llm/test_natal_llm_astrology_input_audit.py`
- VC9: `python -c "import subprocess; subprocess.run(['git','diff','--quiet','--','app/domain/llm/runtime','app/infra/db/models'], check=True)"`
- VC10: `python -c "import subprocess; subprocess.run(['git','diff','--quiet','--','../frontend/src','migrations'], check=True)"`
- VC11: `rg -n "select\\(|Session\\(|execute\\(" app/domain/astrology/interpretation tests/unit/domain/astrology/interpretation`
- VC12: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-365-interpretation-material-builder-theme-astral/evidence/validation.txt').exists()"`
- VC13: `ruff format .`
- VC14: `ruff check .`
- VC15: `pytest -q tests/unit/domain/astrology tests/integration --tb=short`
- VC16: `rg -n "InterpretationMaterialBuilder|interpretation_material|planet_sign_interpretations|aspect_interpretations|integration_levers|source_ref|fact_ref" app tests`

## Regression Risks

- The builder could transmit too many texts and recreate an encyclopedic dump.
- The builder could emit material without a sourced text owner.
- The builder could emit material without a calculated fact anchor.
- The builder could create different top-level shapes per delivery profile.
- The builder could bypass repository ownership with SQL inside domain or prompt code.
- The builder could drift into provider payload or output schema changes.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.venv` before every Python, Ruff, or Pytest command.
- Add the required French global file comment and French docstrings in new or materially changed Python files.
- Keep SQL and DB session usage inside infra repositories.
- Do not make real provider calls.
- Do not modify frontend files, migrations, provider gateway files, output schema owners, source text seeds, or guardrail registry entries.
- Persist validation output under the CS-365 story evidence folder.

## References

- `_story_briefs/cs-365-implementer-interpretation-material-builder-theme-astral.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/00-story.md`
- `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/00-story.md`
- `_condamad/audits/theme-astral-prompt-contract/**/01-audit-usage-tables-textes-interpretation.md`
- `_condamad/architecture/theme-astral-prompt-contract/**/archi-theme-astral-prompt-contract-v1.md`
- `backend/app/domain/astrology/interpretation/**`
- `backend/app/infra/db/repositories/**`
- `backend/app/infra/db/models/**`
- `backend/tests/unit/domain/astrology/**`
- `backend/tests/integration/**`
