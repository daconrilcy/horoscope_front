# Story CS-406 router-basic-complete-assembly-natale-v3: Router Basic Complete Vers Assembly Natale V3
Status: ready-to-review

## Trigger / Source

- Source brief: `_story_briefs/cs-406-router-basic-complete-assembly-natale-v3.md`.
- Selected mode: Repo-informed story in Fast Story Writer Mode.
- Source problem: `POST /natal/interpretation` avec `plan=basic` et `level=complete` resout aujourd'hui l'assembly free courte.
- Source stakes: lecture Basic complete V3, taxonomie ciblee, free short preserve, premium preserve, absence de promotion globale Basic.
- Source-alignment evidence: objectif, AC, taches, preuves et guardrails couvrent les primitives du brief sans deplacer le sujet vers UI.

## Objective

Garantir que la lecture natale `basic` complete resout une assembly `natal/interpretation/basic` explicite, basee sur
`natal_interpretation`, `AstroResponse_v3` et un profil d'execution Basic dedie.

## Target State

- `basic + complete + natal/interpretation` conserve le plan `basic` jusqu'a `AssemblyRegistry`.
- L'assembly publiee `natal/interpretation/basic/fr-FR` pointe vers le use case `natal_interpretation`.
- Le contrat de sortie de l'assembly Basic complete est `AstroResponse_v3`.
- Le profil d'execution `natal/interpretation/basic` est publie, explicite et different du profil free par defaut.
- `free + complete + variant_code=free_short` continue d'utiliser l'experience courte explicite.
- `premium + complete` continue de resoudre `natal_interpretation` en V3.
- `chat` et `guidance` Basic gardent leur normalisation actuelle tant qu'aucune assembly Basic dediee n'existe.
- Une garde prouve que l'ajout du seed seul ne suffit pas: le runtime appelle `AssemblyRegistry` avec `plan="basic"`.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-406-router-basic-complete-assembly-natale-v3.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted; next available story number is `CS-406`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted lookup found `RG-149`, `RG-150`, `RG-152`, `RG-155`, `RG-156`, and `RG-157`.
- Evidence 4: guardrail resolver ran for backend LLM runtime scope; unrelated frontend universal IDs were rejected from the local scope.
- Evidence 5: `backend/app/domain/llm/governance/feature_taxonomy.py` maps `basic` to `free` through `normalize_plan_scope()`.
- Evidence 6: `backend/app/domain/llm/runtime/gateway.py` normalizes the plan before `AssemblyRegistry.get_active_config_sync()`.
- Evidence 7: `backend/app/domain/llm/runtime/adapter.py` maps `natal_interpretation` to subfeature `interpretation` and forwards the plan.
- Evidence 8: `backend/app/services/llm_generation/natal/interpretation_service.py` builds `NatalExecutionInput(plan=user_plan)`.
- Evidence 9: `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py` seeds free and premium natal interpretation assemblies only.
- Evidence 10: `backend/app/domain/llm/configuration/canonical_use_case_registry.py` maps `natal_interpretation` to `AstroResponse_v3`.
- Repository structure alert: expected backend roots exist in this workspace; no implementation-created root directory is required.
- Scope vector:
  - operation `update`, domain `backend-llm-runtime`
  - route `POST /natal/interpretation`
  - paths `backend/app/domain/llm`, `backend/app/services/llm_generation/natal`, `backend/app/ops/llm/bootstrap`
  - contracts `assembly-resolution`, `execution-profile`, `AstroResponse_v3`, `llm_astrology_input_v1`

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| `POST /natal/interpretation` | in scope | AC1, AC2, AC3, Task 1, Task 5 |
| `plan=basic` | in scope | AC1, AC4, AC9, Task 2, Task 5 |
| `level=complete` | in scope | AC1, AC4, Task 2 |
| `variant_code=free_short` | in scope | AC6, Task 6 |
| `natal/interpretation/basic` | in scope | AC1, AC2, AC3, Task 3 |
| `natal_interpretation` | in scope | AC2, AC7, Task 3 |
| `natal_interpretation_short` | in scope | AC6, Task 6 |
| `AstroResponse_v3` | in scope | AC3, AC7, Task 4 |
| Basic execution profile | in scope | AC4, Task 4 |
| `AssemblyRegistry` receives `plan="basic"` | in scope | AC9, Task 5 |
| Free complete short path | in scope | AC6, Task 6 |
| Premium complete path | in scope | AC7, Task 7 |
| Chat Basic scope | in scope | AC8, Task 8 |
| Guidance Basic scope | in scope | AC8, Task 8 |
| Commercial rights, quotas and prices | out of scope | Non-goals |
| Frontend rendering | out of scope | Non-goals |

## Domain Boundary

- Domain: backend-llm-runtime
- In scope:
  - Backend LLM assembly seeding for `natal/interpretation/basic`.
  - Backend contextual plan normalization for complete natal interpretation only.
  - Backend execution profile ownership for Basic complete natal reading.
  - Backend tests proving Basic, Free, Premium, Chat and Guidance routing behavior.
- Out of scope:
  - Frontend UI, React rendering, CSS, commercial rights, quotas, prices, auth, i18n, build tooling and DB migrations.
- Explicit non-goals:
  - No frontend route, screen, client generation, plan pricing change, prompt rewrite, global Basic promotion or quota behavior change.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Preserve `basic` only for complete natal interpretation assembly resolution.
  - Add only the canonical `natal/interpretation/basic/fr-FR` assembly for this flow.
  - Keep global `normalize_plan_scope("basic") == "free"` for non-dedicated Basic assemblies.
  - Keep chat and guidance Basic behavior unchanged unless a dedicated Basic assembly exists for that family.
  - Keep free short and premium complete outputs unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product cannot provide explicit Basic model, budget and verbosity values for the V3 execution profile.
- Additional validation rules:
  - Use `pytest -q backend/tests/llm_orchestration/test_assembly_resolution.py -k "basic or natal"` for runtime resolution.
  - Use `pytest -q backend/tests/llm_orchestration/test_execution_profile_taxonomy.py` for execution profile taxonomy.
  - Use `pytest -q backend/tests/integration/test_admin_llm_catalog.py -k "natal and basic"` for catalog visibility.
  - Use `pytest -q backend/tests/unit/test_seed_66_20_taxonomy_basic_natal.py` for seed completeness.
  - Use `AST guard`, `AssemblyRegistry` spy, or `app.routes` only when tied to this runtime path.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `AssemblyRegistry`, runtime pytest, and optional `TestClient` prove selected assembly behavior. |
| Baseline Snapshot | yes | Before and after artifacts prove the only allowed surface delta is Basic complete natal routing. |
| Ownership Routing | yes | Taxonomy, gateway, seed, profile and service responsibilities must stay canonical. |
| Allowlist Exception | no | No broad tolerance register is authorized for Basic-to-free routing on this path. |
| Contract Shape | yes | Assembly, use case, schema and profile values have exact observable rules. |
| Batch Migration | no | No batch migration or schema migration is in scope. |
| Reintroduction Guard | yes | Basic complete natal must not silently resolve back to free. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Basic complete resolves `natal/interpretation/basic`. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_assembly_resolution.py`. |
| AC2 | Basic complete uses `natal_interpretation`. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_seed_66_20_taxonomy_basic_natal.py`. |
| AC3 | Basic complete uses `AstroResponse_v3`. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_seed_66_20_taxonomy_basic_natal.py`. |
| AC4 | Basic complete has an explicit execution profile. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_execution_profile_taxonomy.py`. |
| AC5 | Basic complete avoids the free default profile. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_execution_profile_taxonomy.py`. |
| AC6 | Free short continues to use the short assembly. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_assembly_resolution.py`. |
| AC7 | Premium complete remains V3. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_assembly_resolution.py`. |
| AC8 | Chat Basic scope is unchanged. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_assembly_resolution.py`. |
| AC9 | Runtime calls `AssemblyRegistry` with `plan="basic"`. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/llm_orchestration/test_assembly_resolution.py`. |
| AC10 | The Basic assembly seed is discoverable. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks the Basic assembly tuple. |
| AC11 | Admin catalog exposes Basic natal assembly. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_admin_llm_catalog.py`. |
| AC12 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |
| AC13 | Guidance Basic scope is unchanged. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_assembly_resolution.py`. |

## Implementation Tasks

- [ ] Task 1: Trace the `POST /natal/interpretation` complete path from service to gateway resolution. (AC: AC1, AC9)
- [ ] Task 2: Add contextual plan preservation for `basic` only on complete natal interpretation. (AC: AC1, AC8, AC9)
- [ ] Task 3: Seed `natal/interpretation/basic/fr-FR` with `natal_interpretation`. (AC: AC2, AC3, AC10)
- [ ] Task 4: Create or update the explicit Basic execution profile with model, budget and verbosity. (AC: AC4, AC5)
- [ ] Task 5: Add a runtime guard proving `AssemblyRegistry` receives `plan="basic"`. (AC: AC1, AC9)
- [ ] Task 6: Preserve the free short `variant_code=free_short` path. (AC: AC6)
- [ ] Task 7: Preserve the premium complete V3 path. (AC: AC7)
- [ ] Task 8: Prove Chat Basic scope behavior remains unchanged. (AC: AC8)
- [ ] Task 9: Update admin catalog or seed tests for Basic natal discoverability. (AC: AC10, AC11)
- [ ] Task 10: Persist validation output and before/after evidence under this story directory. (AC: AC12)
- [ ] Task 11: Prove Guidance Basic scope behavior remains unchanged. (AC: AC13)

## Files to Inspect First

- `backend/app/domain/llm/governance/feature_taxonomy.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/tests/llm_orchestration/test_assembly_resolution.py`
- `backend/tests/llm_orchestration/test_execution_profile_taxonomy.py`
- `backend/tests/integration/test_admin_llm_catalog.py`
- `backend/tests/unit/test_seed_66_20_taxonomy_basic_natal.py`

## Runtime Source of Truth

- Primary source of truth:
  - `AssemblyRegistry.get_active_config_sync()`, `ResolvedExecutionPlan`, `pytest`, `TestClient`, and seeded DB rows.
- Runtime evidence:
  - `pytest -q backend/tests/llm_orchestration/test_assembly_resolution.py -k "basic or natal"`.
  - `pytest -q backend/tests/llm_orchestration/test_execution_profile_taxonomy.py`.
  - `pytest -q backend/tests/integration/test_admin_llm_catalog.py -k "natal and basic"`.
  - `pytest -q backend/tests/unit/test_seed_66_20_taxonomy_basic_natal.py`.
- Secondary evidence:
  - Targeted `rg` scan for the Basic assembly tuple in the seed file.
- Static scans alone are not sufficient for this story because:
  - Runtime plan preservation must be proven at the `AssemblyRegistry` call boundary.

## Contract Shape

- Contract type:
  - Backend LLM assembly resolution and execution profile contract.
- Fields:
  - `feature`: `natal`.
  - `subfeature`: `interpretation`.
  - `plan`: `basic`.
  - `locale`: `fr-FR`.
  - `use_case_key`: `natal_interpretation`.
  - `output_schema_name`: `AstroResponse_v3`.
  - `execution_profile`: explicit Basic model, budget, verbosity, provider and status.
- Required fields:
  - `feature`, `subfeature`, `plan`, `locale`, `use_case_key`, `output_schema_name`, `execution_profile`.
- Optional fields:
  - none for this story delta.
- Status codes:
  - unchanged; this story changes backend LLM runtime resolution, not HTTP response mapping.
- Serialization names:
  - Existing public response names stay unchanged.
- Frontend type impact:
  - none.
- Generated contract impact:
  - `app.openapi()` remains unchanged for `POST /natal/interpretation`.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-406-router-basic-complete-assembly-natale-v3/evidence/assembly-resolution-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-406-router-basic-complete-assembly-natale-v3/evidence/assembly-resolution-after.txt`
- Expected invariant:
  - The only intended behavior delta is Basic complete natal resolution to `natal/interpretation/basic`.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Plan taxonomy defaults | `backend/app/domain/llm/governance/feature_taxonomy.py` | service route handlers |
| Contextual assembly plan resolution | `backend/app/domain/llm/runtime/gateway.py` | seed script only |
| Natal service plan handoff | `backend/app/services/llm_generation/natal/interpretation_service.py` | frontend code |
| Adapter use-case mapping | `backend/app/domain/llm/runtime/adapter.py` | API routers |
| Assembly seed ownership | `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py` | runtime ad hoc row creation |
| Canonical schema ownership | `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | prompt text |
| Admin catalog verification | `backend/tests/integration/test_admin_llm_catalog.py` | manual-only review |

## Mandatory Reuse / DRY Constraints

- Reuse the existing `AssemblyRegistry` and execution profile registry; do not create a second registry path.
- Reuse `natal_interpretation` and `AstroResponse_v3`; do not create a duplicate Basic use case or duplicate schema.
- Reuse existing seed bootstrap patterns in `seed_66_20_taxonomy.py`.
- Centralize contextual Basic preservation in one runtime helper or owner.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy route path may be added for this endpoint.
- No compatibility route path may be added for this endpoint.
- No fallback route path may be added for this endpoint.
- No shim or alias may map all Basic traffic to Premium.
- Forbidden behavior: global `basic -> premium` mapping.
- Forbidden behavior: Basic complete natal resolving `natal/interpretation/free`.
- Forbidden behavior: Basic complete natal using `natal_interpretation_short`.
- Forbidden behavior: Basic complete natal using free default `gpt-4o-mini` profile without explicit product choice.

## Reintroduction Guard

- Guard source:
  - `rg -n '"natal", "interpretation", "basic"' backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py`
- Runtime guard:
  - `pytest -q backend/tests/llm_orchestration/test_assembly_resolution.py -k "basic or natal"`.
  - `pytest -q backend/tests/llm_orchestration/test_execution_profile_taxonomy.py`.
- Registry-call guard:
  - Add a spy, fake registry, or `AST guard` proving the complete natal Basic path calls the registry with `plan="basic"`.
- Forbidden reintroduction:
  - Resolving Basic complete natal through `normalize_plan_scope(basic)` alone.
  - Treating seed addition as sufficient without runtime plan preservation.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-149 | scope -> modern LLM process classification -> natal remains on `llm_astrology_input_v1`. | orchestration `pytest`; carrier `rg`. |
| RG-150 | scope -> rejected answer boundary -> route change must not expose rejected outputs. | rejected-boundary `pytest`; ownership review. |
| RG-152 | scope -> complete accepted reading -> Basic complete remains under `narrative_natal_reading_v1`. | narrative `pytest`; runtime check. |
| RG-155 | scope -> Basic/Premium complete output -> no padding or empty public sources. | narrative integrity `pytest`. |
| RG-156 | scope -> Basic editorial richness -> Basic V3 consumes support elements. | orchestration `pytest`; support scan. |
| RG-157 | scope -> complete generation acceptance -> quota debit timing remains unchanged. | quota `pytest`; ownership review. |
| RG-022 | scope -> prompt-generation validation paths -> backend pytest paths must be collected. | exact validation commands. |

- Registry gap: no exact route-specific guardrail exists for `natal/interpretation/basic`; this story records the local invariant instead.
- Non-applicable example: frontend style guardrails are out of scope because no React or CSS file is listed.
- Non-applicable example: DB migration guardrails are out of scope because no schema migration is authorized.
- Non-applicable example: auth guardrails are out of scope because no authentication model change is authorized.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline before | `_condamad/stories/CS-406-router-basic-complete-assembly-natale-v3/evidence/assembly-resolution-before.txt` | Record initial Basic assembly behavior. |
| Baseline after | `_condamad/stories/CS-406-router-basic-complete-assembly-natale-v3/evidence/assembly-resolution-after.txt` | Record final Basic assembly behavior. |
| Validation output | `_condamad/stories/CS-406-router-basic-complete-assembly-natale-v3/evidence/validation.txt` | Keep final lint, test and scan command output. |
| Registry-call proof | `_condamad/stories/CS-406-router-basic-complete-assembly-natale-v3/evidence/basic-registry-call.txt` | Prove registry receives `plan="basic"`. |
| Review output | `_condamad/stories/CS-406-router-basic-complete-assembly-natale-v3/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | No tolerance entry is authorized for Basic complete resolving through free. | permanent zero-entry register |

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/llm/governance/feature_taxonomy.py` - keep global plan defaults explicit.
- `backend/app/domain/llm/runtime/gateway.py` - preserve Basic contextually before assembly resolution.
- `backend/app/domain/llm/runtime/adapter.py` - inspect natal use-case and context handoff.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - preserve level and variant context in the runtime handoff.
- `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py` - seed Basic assembly and profile.
- `_condamad/stories/CS-406-router-basic-complete-assembly-natale-v3/evidence/**` - persist proof artifacts.

Likely tests:

- `backend/tests/llm_orchestration/test_assembly_resolution.py` - cover Basic, Free, Premium, Chat and Guidance assembly resolution.
- `backend/tests/llm_orchestration/test_execution_profile_taxonomy.py` - cover explicit Basic profile behavior.
- `backend/tests/integration/test_admin_llm_catalog.py` - cover Basic natal catalog detail.
- `backend/tests/unit/test_seed_66_20_taxonomy_basic_natal.py` - cover seed assembly, schema and profile.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/alembic/**` - out of scope; no migration is authorized.
- `backend/app/api/**` - out of scope; no route or status code change is authorized.
- `backend/app/services/quota/**` - out of scope; no quota behavior is authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `python -B -m pytest -q tests/llm_orchestration/test_assembly_resolution.py -k "basic or natal" --tb=short`
- VC6: `python -B -m pytest -q tests/llm_orchestration/test_execution_profile_taxonomy.py --tb=short`
- VC7: `python -B -m pytest -q tests/integration/test_admin_llm_catalog.py -k "natal and basic" --tb=short`
- VC8: `python -B -m pytest -q tests/unit/test_seed_66_20_taxonomy_basic_natal.py --tb=short`
- VC9: `rg -n '"natal", "interpretation", "basic"' app/ops/llm/bootstrap/seed_66_20_taxonomy.py`
- VC10: `python -B -m pytest -q tests/llm_orchestration/test_assembly_resolution.py tests/llm_orchestration/test_execution_profile_taxonomy.py --tb=short`
- VC11: `python -B -c "from app.main import app; assert '/v1/natal/interpretation' in app.openapi()['paths']"`
- VC12: `python -B -c "from pathlib import Path; assert Path('../_condamad/stories/CS-406-router-basic-complete-assembly-natale-v3/evidence/basic-registry-call.txt').exists()"`

`rg` scan details:

- VC9 forbidden pattern: absence of the exact Basic assembly tuple.
- VC9 allowed fixture pattern: the seed tuple `("natal", "interpretation", "basic", "natal_interpretation")`.
- VC9 roots: `app/ops/llm/bootstrap/seed_66_20_taxonomy.py`.
- VC9 expected false positives: zero.

## Regression Risks

- Contextual plan preservation can become too broad; AC8 requires Chat and Guidance Basic behavior unchanged.
- Seed-only correction can leave runtime resolving free; AC9 requires a registry-call proof.
- Basic profile choices can silently reuse free defaults; AC4 and AC5 require explicit model, budget and verbosity.
- Free short behavior can drift into V3; AC6 preserves the intentional short experience.
- Premium complete can regress while adding Basic; AC7 preserves V3 premium resolution.

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
- Preserve CS-396, CS-397 and CS-398 behavior before changing Basic complete routing.

## References

- `_story_briefs/cs-406-router-basic-complete-assembly-natale-v3.md`
- `_condamad/stories/regression-guardrails.md#RG-149`
- `_condamad/stories/regression-guardrails.md#RG-150`
- `_condamad/stories/regression-guardrails.md#RG-152`
- `_condamad/stories/regression-guardrails.md#RG-155`
- `_condamad/stories/regression-guardrails.md#RG-156`
- `_condamad/stories/regression-guardrails.md#RG-157`
- `_condamad/stories/regression-guardrails.md#RG-022`
- `backend/app/domain/llm/governance/feature_taxonomy.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
