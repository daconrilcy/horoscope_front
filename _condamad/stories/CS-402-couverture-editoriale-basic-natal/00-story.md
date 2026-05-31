# Story CS-402 couverture-editoriale-basic-natal: Enrichir Couverture Editoriale Basic Natal
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-397-enrichir-matiere-editoriale-basic-lecture-natale.md`.
- Selected mode: Repo-informed story in Fast Story Writer Mode.
- Source problem: la lecture natale Basic exploite trop peu de faits astrologiques alors que le theme calcule contient une matiere riche.
- Source stakes: diversite editoriale, budget Basic respecte, sources publiques vulgarisees, absence de fuite technique, fermeture du guardrail `RG-156`.
- Source-alignment evidence: objectif, AC, taches, preuves et guardrails couvrent les seize primitives du brief sans deplacer le sujet vers UI, quotas ou calculs.

## Objective

Construire une matiere editoriale Basic equilibree pour la lecture natale complete: personnalite, emotions, relations, vocation et evolution
doivent recevoir des faits astrologiques distincts, priorises, vulgarisables et limites aux budgets existants.

## Target State

- `client_interpretation_projection_v1.support_elements` alimente Basic et Premium lorsque des faits exploitables existent.
- `llm_astrology_input_v1.shaping.support_elements` transporte ces faits sans carrier historique ni champ public technique.
- La selection privilegie une couverture thematique avant le score global brut.
- Les familles minimales sont couvertes quand elles existent: big three, rulers, maisons dominantes, aspects majeurs, dominantes planetaires, tensions structurantes.
- Le payload provider et le prompt nominal demandent cinq familles de sections sources pour la lecture narrative.
- Les lectures completes utilisent preferentiellement `AstroResponseV3`; V1/V2 restent explicitement historiques et non paddes.
- Une fixture riche Basic prouve cinq chapitres alimentes et des metriques auditables.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-397-enrichir-matiere-editoriale-basic-lecture-natale.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted; next available story number is `CS-402`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted lookup found `RG-144` to `RG-149`, `RG-152`, and `RG-156`.
- Evidence 4: resolver run for backend-domain scope returned generic backend guardrail `RG-002`; brief-specific IDs were resolved by targeted ID lookup.
- Evidence 5: `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` contains `support_elements`.
- Evidence 6: `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` maps projection support into shaping.
- Evidence 7: `backend/app/domain/llm/configuration/theme_astral_contracts.py` declares Basic budget `max_source_items=24` and `max_sections=6`.
- Evidence 8: `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` builds provider section and material budgets.
- Evidence 9: `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py` builds from `AstroResponseV1`, `AstroResponseV2`, and `AstroResponseV3`.
- Repository structure alert: expected backend roots exist in this workspace; no implementation-created root directory is required.
- Scope vector:
  - operation `create`, domain `backend-domain`
  - paths `backend/app/domain/astrology/interpretation`, `backend/app/domain/llm`, `backend/app/services/llm_generation/natal`

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| `client_interpretation_projection_v1` to `llm_astrology_input_v1` | in scope | AC1, AC2, Task 1, Task 2 |
| `support_elements` Basic | in scope | AC1, AC3, Task 1, Task 3 |
| `support_elements` Premium | in scope | AC2, Task 1, Task 3 |
| thematic coverage | in scope | AC3, AC4, Task 3 |
| big three, rulers, maisons dominantes | in scope | AC4, Task 4 |
| aspects majeurs, dominantes planetaires, tensions | in scope | AC4, Task 4 |
| prompt nominal | in scope | AC5, Task 5 |
| payload provider | in scope | AC5, AC7, Task 5, Task 8 |
| schema nominal | in scope | AC6, Task 6 |
| `AstroResponseV3` | in scope | AC6, Task 6 |
| V1/V2 schemas | in scope | AC6, Task 6 |
| fixture riche | in scope | AC8, Task 9 |
| repartition par chapitre | in scope | AC8, Task 9 |
| metriques auditables | in scope | AC7, Task 8 |
| frontend exposure | out of scope | Non-goals, RG-152 |
| quota or React rendering | out of scope | Non-goals, Expected files not expected |

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend interpretation projection enrichment for Basic and Premium support material.
  - Backend LLM astrology input shaping and provider payload source-section contract.
  - Backend prompt seed content for the nominal complete natal reading contract.
  - Backend unit and orchestration tests proving chapter distribution and public-source material.
- Out of scope:
  - Frontend UI, React rendering, CSS, DB schema, auth, i18n, build tooling, migrations, quotas, and new astrology calculations.
- Explicit non-goals:
  - No frontend route, screen, client generation, quota change, DB migration, new calculation engine, final deterministic narration, or public technical field.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Enrich only Basic and Premium source material selection inside existing budgets.
  - Preserve existing commercial limits: Basic `max_source_items=24`, Basic `max_sections=6`, and six support elements.
  - Keep public narrative fields free of engine codes, scores, `evidence_refs`, `chart_json`, and `natal_data`.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: five requested narrative source families cannot fit inside the existing Basic budget.
- Additional validation rules:
  - Use `pytest -q backend/tests/unit/domain/astrology/test_client_interpretation_support_elements.py` for projection and support behavior.
  - Use `pytest -q backend/tests/llm_orchestration -k "natal or theme_astral"` for provider and prompt runtime behavior.
  - Use `AST guard` or bounded `rg` scans for forbidden public technical fields.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Runtime projection, provider and narrative tests prove support material behavior. |
| Baseline Snapshot | yes | Before/after artifacts prove the only allowed delta is editorial material coverage. |
| Ownership Routing | yes | Projection, shaping, provider, prompt and narrative responsibilities must stay canonical. |
| Allowlist Exception | no | No broad tolerance register is authorized for missing support material. |
| Contract Shape | yes | The provider payload and narrative source sections have exact family and budget rules. |
| Batch Migration | no | No data migration or multi-file conversion batch is in scope. |
| Reintroduction Guard | yes | Technical fields and historical carriers must stay absent from public narrative output. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Basic support is populated from projection facts. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/test_client_interpretation_support_elements.py`. |
| AC2 | Premium support is populated from projection facts. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/test_client_interpretation_support_elements.py`. |
| AC3 | Basic selected source count stays within budget. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/test_client_interpretation_support_elements.py`. |
| AC4 | Basic selection covers multiple fact families. | Evidence profile: json_contract_shape; `tests/unit/domain/astrology/test_client_interpretation_support_elements.py`. |
| AC5 | The nominal prompt asks for five source-section families. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks prompt family labels. |
| AC6 | Complete readings prefer `AstroResponseV3`. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/llm_orchestration -k "natal or theme_astral"`. |
| AC7 | Provider metrics expose selected families privately. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration -k "natal or theme_astral"`. |
| AC8 | A rich Basic fixture produces five chapter source groups. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration -k "natal or theme_astral"`. |
| AC9 | Technical carriers stay outside the public narrative. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks public carrier roots. |
| AC10 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |

## Implementation Tasks

- [ ] Task 1: Audit projection-to-shaping flow for `support_elements` population. (AC: AC1, AC2)
- [ ] Task 2: Preserve `llm_astrology_input_v1` as the only modern astrology input carrier. (AC: AC1, AC2, AC9)
- [ ] Task 3: Implement family-aware support selection inside existing Basic and Premium budgets. (AC: AC1, AC2, AC3, AC4)
- [ ] Task 4: Cover big three, rulers, houses, aspects, dominants and structural tensions when facts exist. (AC: AC4)
- [ ] Task 5: Align provider payload and nominal prompt wording on the five narrative source families. (AC: AC5, AC7, AC8)
- [ ] Task 6: Prefer `AstroResponseV3` for complete readings and document V1/V2 historical behavior. (AC: AC6)
- [ ] Task 7: Keep V1/V2 incomplete schemas explicit without silent padding. (AC: AC6, AC9)
- [ ] Task 8: Add auditable private metrics for selected families, fact count, chapters covered and public sources. (AC: AC7)
- [ ] Task 9: Add a rich Basic fixture proving five chapter source groups. (AC: AC8)
- [ ] Task 10: Persist validation output and before/after evidence under this story directory. (AC: AC10)

## Files to Inspect First

- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `backend/app/domain/astrology/interpretation_adapters/signal_builder.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/scripts/seed_30_3_gpt5_prompts.py`
- `backend/tests/unit/domain/astrology/test_client_interpretation_support_elements.py`
- `backend/tests/llm_orchestration`

## Runtime Source of Truth

- Primary source of truth:
  - `client_interpretation_projection_v1`, `llm_astrology_input_v1`, provider payload builder, and `TestClient` or service-level pytest flows.
- Runtime evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_client_interpretation_support_elements.py`.
  - `pytest -q backend/tests/llm_orchestration -k "natal or theme_astral"`.
- Secondary evidence:
  - `AST guard` or targeted `rg` scans for public technical carriers.
- Static scans alone are not sufficient for this story because:
  - The selected facts must move through projection, shaping, provider payload and narrative-building runtime paths.

## Contract Shape

- Contract type:
  - Backend LLM input shaping and provider payload for complete natal readings.
- Fields:
  - `shaping.support_elements`: list of selected vulgarizable support facts.
  - `material_budget.max_source_items`: unchanged commercial fact budget.
  - `material_budget.max_sections`: unchanged section budget.
  - `section_budget.max_sections`: unchanged provider section budget.
- Required source families:
  - `personnalite`, `emotions`, `relations`, `vocation`, `evolution`.
- Required fact families:
  - big three, rulers, houses, major aspects, planetary dominants, structural tensions.
- Required fields:
  - `shaping.support_elements`, `material_budget.max_source_items`, `material_budget.max_sections`.
- Optional fields:
  - none for this story delta.
- Status codes:
  - unchanged; this story changes backend material selection and provider contract content.
- Serialization names:
  - `llm_astrology_input_v1`, `support_elements`, `narrative_natal_reading_v1`, and public source names stay unchanged.
- Frontend type impact:
  - none.
- Generated contract impact:
  - no generated API client or OpenAPI path is changed.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-402-couverture-editoriale-basic-natal/evidence/editorial-coverage-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-402-couverture-editoriale-basic-natal/evidence/editorial-coverage-after.txt`
- Expected invariant:
  - The only intended behavior delta is richer thematic source selection inside existing Basic and Premium budgets.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Client projection support selection | `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` | API routers or frontend code |
| LLM shaping carrier | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | historical `chart_json` or `natal_data` carriers |
| Delivery budgets | `backend/app/domain/llm/configuration/theme_astral_contracts.py` | prompt text or UI code |
| Provider payload assembly | `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` | narrative renderer |
| Narrative public assembly | `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py` | pure astrology calculation modules |
| Prompt seed wording | `backend/scripts/seed_30_3_gpt5_prompts.py` | runtime ad hoc string patches |

## Mandatory Reuse / DRY Constraints

- Reuse existing projection facts and runtime capabilities; do not add new astrology calculations.
- Reuse delivery profile budgets from `theme_astral_contracts.py`; do not duplicate numeric Basic budgets in prompt code.
- Reuse existing narrative chapter order and public-source models.
- Centralize family selection in one owner so provider payload and tests consume the same classification.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy astrology carrier may become prompt-visible for the modern natal flow.
- No compatibility path may reintroduce `chart_json` or `natal_data` into the nominal prompt.
- No fallback text may fill missing Basic source material.
- Do not add a shim, alias, broad tolerance register, hidden residual path, or frontend-side repair.
- Forbidden public carriers: `chart_json`, `natal_data`, raw `evidence_refs`, engine scores, raw condition codes.
- Forbidden behavior: Basic source selection that collapses to only globally top-ranked facts when several fact families exist.

## Reintroduction Guard

- Guard source:
  - `rg -n "chart_json|natal_data" backend/app/domain/llm backend/app/services/llm_generation/natal`
- Architecture guard required:
  - Add or update a deterministic backend guard that fails if modern natal prompt payloads expose historical carriers.
- Runtime guard:
  - `pytest -q backend/tests/unit/domain/astrology/test_client_interpretation_support_elements.py`.
  - `pytest -q backend/tests/llm_orchestration -k "natal or theme_astral"`.
- Deterministic source:
  - support family metrics and public narrative source payload shape.
- Forbidden reintroduction:
  - public narrative material exposing raw engine facts instead of vulgarized source labels.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-144 | scope -> runtime projections -> consume existing natal runtime objects. | `pytest` projection tests; `AST guard`. |
| RG-145 | scope -> runtime projection family -> consume existing runtime facts without recalculation. | support-elements `pytest`; ownership review. |
| RG-146 | scope -> runtime projection family -> consume existing runtime facts without recalculation. | support-elements `pytest`; ownership review. |
| RG-147 | scope -> runtime projection family -> consume existing runtime facts without recalculation. | support-elements `pytest`; ownership review. |
| RG-148 | scope -> runtime projection family -> consume existing runtime facts without recalculation. | support-elements `pytest`; ownership review. |
| RG-149 | scope -> modern LLM input -> keep `llm_astrology_input_v1` canonical. | `rg` carrier scan; orchestration `pytest`. |
| RG-152 | scope -> public narrative -> no technical fields leak. | `rg` public carrier scan; narrative tests. |
| RG-156 | scope -> Basic coverage -> diversify support families in budgets. | support-elements `pytest`; orchestration `pytest`. |
| RG-002 | scope -> backend ownership -> keep logic out of route layers. | ownership review; targeted `rg`. |

- Needs-investigation: catalogue/rules inside `interpretation_adapter` only if the implementation proves the diversity loss comes from that owner.
- Non-applicable example: `RG-041` entitlement documentation is out of scope because no entitlement surface is touched.
- Non-applicable example: frontend style guardrails are out of scope because no React or CSS file is listed.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline before | `_condamad/stories/CS-402-couverture-editoriale-basic-natal/evidence/editorial-coverage-before.txt` | Record initial support coverage and prompt state. |
| Baseline after | `_condamad/stories/CS-402-couverture-editoriale-basic-natal/evidence/editorial-coverage-after.txt` | Record final support coverage and prompt state. |
| Validation output | `_condamad/stories/CS-402-couverture-editoriale-basic-natal/evidence/validation.txt` | Keep final lint, test and scan command output. |
| Coverage metrics | `_condamad/stories/CS-402-couverture-editoriale-basic-natal/evidence/editorial-coverage-metrics.json` | Keep final coverage metrics. |
| Review output | `_condamad/stories/CS-402-couverture-editoriale-basic-natal/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | No tolerance entry is authorized for missing support material or public technical carrier leakage. | permanent zero-entry register |

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` - enrich family-aware support selection.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - preserve support shaping contract.
- `backend/app/domain/llm/configuration/theme_astral_contracts.py` - verify existing Basic and Premium budgets remain canonical.
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` - expose private coverage metrics and source families.
- `backend/app/domain/astrology/interpretation_adapters/signal_builder.py` - inspect signal family ownership before changing classification.
- `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py` - prefer complete schema behavior without padding.
- `backend/scripts/seed_30_3_gpt5_prompts.py` - align nominal prompt on five source-section families.
- `_condamad/stories/CS-402-couverture-editoriale-basic-natal/evidence/**` - persist proof artifacts.

Likely tests:

- `backend/tests/unit/domain/astrology/test_client_interpretation_support_elements.py` - cover Basic and Premium support family selection.
- `backend/tests/llm_orchestration` - cover provider payload, nominal prompt, rich Basic fixture and narrative source distribution.
- `backend/tests/architecture/test_natal_public_technical_carrier_guard.py` - fail on historical carriers in modern public narrative flow.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/alembic/**` - out of scope; no migration is authorized.
- `backend/app/api/**` - out of scope; no route or status code change is authorized.
- `backend/app/domain/astrology/calculators/**` - out of scope; no astrology computation is added.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `python -B -m pytest -q tests/llm_orchestration --tb=short -k "natal or theme_astral"`
- VC6: `python -B -m pytest -q tests/unit/domain/astrology/test_client_interpretation_support_elements.py --tb=short`
- VC7: `rg -n "chart_json|natal_data" app/domain/llm app/services/llm_generation/natal`
- VC8: `rg -n "support_elements" app/domain/astrology/interpretation/llm_astrology_input_v1.py app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- VC9: `rg -n "personnalite|emotions|relations|vocation|evolution" scripts/seed_30_3_gpt5_prompts.py`
- VC10: `python -B -m pytest -q tests/llm_orchestration tests/unit/domain/astrology/test_client_interpretation_support_elements.py --tb=short`

`rg` scan details:

- VC7 forbidden pattern: `chart_json|natal_data`.
- VC7 allowed fixture pattern: none in production paths.
- VC7 roots: `app/domain/llm`, `app/services/llm_generation/natal`.
- VC7 expected false positives: audit-only variable names.
- VC8 required pattern: `support_elements`; allowed fixture pattern: none; roots: two interpretation files; expected false positives: comments naming the field.
- VC9 required pattern: the five source family labels; allowed fixture pattern: prompt seed text; root: `scripts/seed_30_3_gpt5_prompts.py`; expected false positives: none.

## Regression Risks

- Richer source selection can increase prompt size; the story keeps Basic budgets unchanged and verifies selected counts.
- Family-aware selection can overfit fixture labels; tests must assert families and chapter coverage, not one exact ranked list.
- Private metrics can leak if routed into public schemas; `RG-152` and carrier scans guard the public boundary.

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

- `_story_briefs/cs-397-enrichir-matiere-editoriale-basic-lecture-natale.md`
- `_condamad/stories/regression-guardrails.md#RG-144`
- `_condamad/stories/regression-guardrails.md#RG-145`
- `_condamad/stories/regression-guardrails.md#RG-146`
- `_condamad/stories/regression-guardrails.md#RG-147`
- `_condamad/stories/regression-guardrails.md#RG-148`
- `_condamad/stories/regression-guardrails.md#RG-149`
- `_condamad/stories/regression-guardrails.md#RG-152`
- `_condamad/stories/regression-guardrails.md#RG-156`
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
