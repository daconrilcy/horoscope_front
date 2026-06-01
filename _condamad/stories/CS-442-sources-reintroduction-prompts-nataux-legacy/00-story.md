# Story CS-442 sources-reintroduction-prompts-nataux-legacy: Corriger Suppression Sources De Reintroduction Prompts Nataux Legacy
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-442-corriger-suppression-sources-reintroduction-prompts-nataux-legacy.md`.
- Operating mode: Repo-informed story.
- Fast Story Writer Mode: active.
- Source problem: CS-437 n'a pas ferme toutes les sources executable de reintroduction des anciens prompts natals.
- Source alignment evidence: objective, ACs, tasks, validations and guardrails map back to the CS-442 brief without scope narrowing.
- Closure expectation: close the catalogues, seeds, admin prompt and test-positive part that blocks CS-440 CR-3 and CR-4.

## Objective

Delete backend prompt sources that can recreate the old natal use cases `natal_interpretation_short`, `natal_long_free`,
or `natal_interpretation` as Basic or Free prompt runtime.
Rebase admin/catalogue tests onto non-natal fixtures, `theme_natal` contracts, or explicit rejection guards.

## Target State

- `backend/app/services/llm_generation/admin_prompts.py` no longer derives or exposes `natal_long_free`.
- Bootstrap and executable scripts no longer seed `natal_interpretation_short`, `natal_long_free`, or Basic/Free `natal_interpretation`.
- Runtime catalogues and registries no longer keep those keys as executable prompt fallbacks.
- Positive admin/catalogue fixtures no longer use old natal use cases as nominal examples.
- `basic_natal_prompt_payload` remains owned only by the modern `theme_astral` prompt contract.
- Prompt-generation cartography documents modern natal generation through `theme_natal` contracts.
- CS-440 CR-3 and CR-4 have refreshed evidence for the catalogues, seeds, prompts and admin-fixture scope.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-442-corriger-suppression-sources-reintroduction-prompts-nataux-legacy.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-442`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted IDs consulted for local backend LLM prompt guardrails.
- Evidence 4: `resolve_guardrails.py` returned `RG-002` and `RG-022`; targeted ID reads added exact prompt guardrails.
- Evidence 5: `rg` found `backend/app/services/llm_generation/admin_prompts.py:301` returning `natal_long_free`.
- Evidence 6: `rg` found old prompt keys in bootstrap and executable scripts under `backend/app/ops/llm/bootstrap` and `backend/scripts`.
- Evidence 7: `rg` found positive backend test fixtures using `natal_interpretation_short`, `natal_long_free`, or old adapter calls.
- Evidence 8: CS-440 review records CR-3 and CR-4 as blockers for unfinished functional removals and positive Basic/free tests.
- Evidence 9: prompt-generation cartography still describes admin manual execution as `admin-only` provider-capable and to investigate.

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| `admin_prompts.py` `natal_long_free` | in scope | AC1, Task 1, VC3, VC5 |
| `natal_interpretation_short` seedability | in scope | AC2, Task 2, VC5, VC6 |
| `natal_long_free` seedability | in scope | AC3, Task 2, VC5, VC6 |
| `natal_interpretation` Basic/Free mapping | in scope | AC4, Task 3, VC3, VC5 |
| Runtime prompt catalogues | in scope | AC5, Task 3, VC3, VC5 |
| Admin/catalogue positive fixtures | in scope | AC6, Task 4, VC2, VC6 |
| `basic_natal_prompt_payload` | in scope | AC7, Task 5, VC4, VC5 |
| Prompt-generation cartography | in scope | AC8, Task 6, VC7 |
| CS-440 CR-3 and CR-4 | in scope | AC9, Task 7, VC2, VC6 |
| Runtime provider legacy deletion | out of scope | Non-goal; owned by CS-441 |
| Public historical routes | out of scope | Non-goal; owned by CS-443 |
| `_condamad/run-state.json` | forbidden surface | Non-goal; do not edit |

## Domain Boundary

- Domain: backend-llm-prompt-sources
- In scope:
  - Backend admin prompt resolution, prompt catalogues, canonical registries, bootstrap seeds, executable scripts and backend tests.
  - Prompt-generation cartography for the exact old natal prompt source status.
  - Architecture and orchestration tests that guard prompt source extinction.
- Out of scope:
  - Frontend UI, public route removal, DB data cleanup, auth, i18n, style, build tooling and migration history.
  - Runtime provider legacy deletion owned by CS-441.
  - Public historical route deletion owned by CS-443.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
  - No new prompt premium work.
  - No deletion of historical `_condamad` briefs, reports, audits, or evidence.
  - No edit to `_condamad/run-state.json`.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: the story deletes executable old prompt seed, registry, catalogue and admin-fixture surfaces.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Modern natal generation remains owned by `theme_natal` contracts and `theme_astral` prompt payloads.
  - Historical references remain only in `_condamad` evidence or explicit anti-return tests.
  - Admin manual execution may remain admin-only only after old natal prompt keys are removed from nominal samples.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: a scan proves an external consumer still depends on an executable old-key seed or admin prompt path.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, `AST guard`, `app.routes`, `app.openapi()` and bounded scans prove no runtime prompt source remains. |
| Baseline Snapshot | yes | Before and after old-key hit artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Canonical owners are required for admin prompt, bootstrap, scripts, registries and cartography. |
| Allowlist Exception | yes | Remaining hits must be classified as historical proof, rejection guard, readonly, or test-only anti-return evidence. |
| Contract Shape | yes | Removed keys, modern replacements and allowed residual hit classes are exact contract fields. |
| Batch Migration | no | No batch migration or multi-step conversion is in scope. |
| Reintroduction Guard | yes | Architecture guards must fail if old prompt sources return as runtime or nominal test fixtures. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `admin_prompts.py` stops exposing `natal_long_free`. | Evidence profile: targeted_forbidden_symbol_scan; `rg` VC6; `pytest` VC4. |
| AC2 | `natal_interpretation_short` is not seedable. | Evidence profile: targeted_forbidden_symbol_scan; `rg` VC6; `pytest` VC4. |
| AC3 | `natal_long_free` is not seedable. | Evidence profile: targeted_forbidden_symbol_scan; `rg` VC6; `pytest` VC3. |
| AC4 | Basic/Free taxonomy does not map `natal_interpretation`. | Evidence profile: ast_architecture_guard; `pytest` VC3; `rg` VC6. |
| AC5 | Prompt catalogues exclude old natal fallbacks. | Evidence profile: targeted_forbidden_symbol_scan; `pytest` VC3. |
| AC6 | Admin/catalogue positive fixtures use modern keys. | Evidence profile: repo_wide_negative_scan; `rg` VC6; `pytest -q backend/tests/integration/test_admin_llm_catalog.py`. |
| AC7 | `basic_natal_prompt_payload` keeps its modern owner. | Evidence profile: ast_architecture_guard; `pytest` VC4. |
| AC8 | Prompt-generation cartography reflects `theme_natal`. | Evidence profile: baseline_before_after_diff; `rg` VC7; `python` checks cartography artifact path. |
| AC9 | CS-440 prompt-source blockers are refreshed. | Evidence profile: baseline_before_after_diff; `pytest` VC2; `rg` VC6; `python` checks CS-442 evidence artifacts. |
| AC10 | Residual old-key hits are classified. | Evidence profile: allowlist_register_validated; `python` checks the CS-442 allowlist artifact. |
| AC11 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-442 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Remove the `natal_long_free` derivation from admin prompt runtime resolution. (AC: AC1)
- [ ] Task 2: Delete or archive executable seeds for `natal_interpretation_short` and `natal_long_free`. (AC: AC2, AC3)
- [ ] Task 3: Remove Basic/Free mappings for `natal_interpretation` from runtime catalogues and registries. (AC: AC4, AC5)
- [ ] Task 4: Rebase admin and catalogue positive fixtures to non-natal keys, `theme_natal`, or rejection guards. (AC: AC6)
- [ ] Task 5: Preserve `basic_natal_prompt_payload` only under `theme_astral` ownership. (AC: AC7)
- [ ] Task 6: Update prompt-generation cartography with the new source status. (AC: AC8)
- [ ] Task 7: Refresh CS-440 blocker evidence for the prompt-source slice. (AC: AC9)
- [ ] Task 8: Persist the residual-hit allowlist and before/after evidence artifacts. (AC: AC10, AC11)

## Files to Inspect First

- `_story_briefs/cs-442-corriger-suppression-sources-reintroduction-prompts-nataux-legacy.md` - source contract.
- `_story_briefs/cs-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy.md` - upstream failed deletion scope.
- `_condamad/reports/cs-439-cs-440-delivery-report.md` - CS-440 blocker and residual-risk evidence.
- `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/11-code-review.md` - CR-3 and CR-4 findings.
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - cartography owner.
- `backend/app/services/llm_generation/admin_prompts.py` - admin prompt runtime derivation.
- `backend/app/domain/llm/prompting/catalog.py` - runtime prompt catalogue.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - canonical use-case registry.
- `backend/app/domain/llm/configuration/theme_astral_contracts.py` - `basic_natal_prompt_payload` owner.
- `backend/app/ops/llm/bootstrap` - bootstrap seed ownership.
- `backend/scripts` - executable script ownership.
- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` - architecture guard owner.
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py` - legacy extinction test owner.
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py` - governance registry tests.
- `backend/tests/integration/test_admin_llm_catalog.py` - admin catalogue fixture tests.

## Runtime Source of Truth

- Primary source of truth:
  - `pytest`, `AST guard`, `app.routes`, `app.openapi()`, canonical registry loading and bounded `rg` scans.
- Secondary evidence:
  - Prompt-generation cartography before/after artifact and residual-hit allowlist.
- Static scans alone are not sufficient for this story because:
  - Admin resolution, registry ownership and bootstrap behavior must be proven by tests or AST guards.
- Runtime route evidence:
  - `app.routes` and `app.openapi()` are secondary guards proving no public route contract authorizes the removed old-key prompt sources.

## Contract Shape

- Contract type:
  - Backend prompt-source removal contract.
- Fields:
  - `use_case_key`: forbidden old-key values must not be runtime prompt owners.
  - `feature`: `natal` remains valid only through modern product contracts.
  - `plan`: `basic` and `free` must not map to old natal prompt keys.
  - `basic_natal_prompt_payload`: owned by `theme_astral` prompt contract only.
- Required fields:
  - `use_case_key`
  - `feature`
  - `plan`
- Optional fields:
  - `basic_natal_prompt_payload`
- Removed prompt keys:
  - `natal_interpretation_short`
  - `natal_long_free`
  - `natal_interpretation` when mapped as Basic or Free runtime prompt owner.
- Required modern owner:
  - `theme_natal` product contracts for modern natal generation.
  - `theme_astral` prompt contract for `basic_natal_prompt_payload`.
- Allowed residual hit classes:
  - `_condamad` historical proof.
  - Explicit rejection or extinction tests.
  - Readonly historical row tests that do not create a provider-capable prompt path.
- Status codes:
  - none; no public API status contract is changed.
- Serialization names:
  - unchanged; no public schema field is renamed.
- Frontend type impact:
  - none; frontend is out of scope.
- Generated contract impact:
  - `app.openapi()` must not expose a new public route or schema that authorizes old natal prompt sources.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-442-sources-reintroduction-prompts-nataux-legacy/evidence/legacy-source-hits-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-442-sources-reintroduction-prompts-nataux-legacy/evidence/legacy-source-hits-after.txt`
- Expected invariant:
  - The only intended backend prompt-source delta is deletion or reclassification of old natal prompt sources.
- Required comparison:
  - Before/after artifacts must include admin prompts, prompt catalogues, registries, bootstrap, scripts and backend tests.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Modern natal prompt generation | `theme_natal` contracts and `theme_astral` prompt contract | `natal_interpretation_short`, `natal_long_free` |
| Admin prompt runtime derivation | `backend/app/services/llm_generation/admin_prompts.py` with modern keys only | `natal_long_free` derivation |
| Prompt use-case registry | `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | Basic/Free old-key mapping |
| Prompt fallback catalogue | `backend/app/domain/llm/prompting/catalog.py` | Executable old natal fallback row |
| Bootstrap prompt seeds | `backend/app/ops/llm/bootstrap` | Old-key natal seed scripts |
| Root executable scripts | `backend/scripts` plus ownership index | Old-key natal reseed scripts |
| Prompt cartography | `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` | Stale old-key runtime claim |

## Removal Classification Rules

- `canonical-active`: modern `theme_natal` contract or modern `theme_astral` prompt payload owner.
- `external-active`: public docs, generated contract, ops runbook, or known consumer still depends on an executable old-key source.
- `historical-facade`: executable old-key seed, script, catalogue row, registry mapping, or admin prompt fallback retained for old behavior.
- `dead`: old-key source has no production, test, docs, generated contract, or known external consumer after required scans.
- `needs-user-decision`: scans prove unresolved execution risk that cannot be closed inside this story.
- Required decision:
  - `historical-facade` and `dead` items must be deleted or archived as non-executable `_condamad` evidence.
  - `external-active` items must block deletion until the user decision is recorded.

## Removal Audit Format

The implementation must persist:

`_condamad/stories/CS-442-sources-reintroduction-prompts-nataux-legacy/evidence/legacy-source-removal-audit.md`

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

- Each row must classify one route, field, file, symbol, status, import path, or UI route.
- `Classification` must use `canonical-active`, `external-active`, `historical-facade`, `dead`, or `needs-user-decision`.
- `Decision` must use `keep`, `delete`, `replace-consumer`, or `needs-user-decision`.
- `Proof` must include command output, file path evidence, or explicit audit source.
- `Risk` must be filled for every `delete` or `needs-user-decision` row.

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Modern natal prompts | `theme_natal` and `theme_astral` prompt contracts | `natal_interpretation_short`, `natal_long_free`, Basic/Free `natal_interpretation` |
| Admin prompt examples | Non-natal generic samples or `theme_natal` contracts | Old natal use cases as positive fixtures |
| Seed/bootstrap provisioning | Modern prompt assembly seeds | Old-key natal prompt reseeds |
| Legacy extinction guards | Architecture and orchestration tests | Positive old-key runtime examples |
| Documentation truth | Prompt-generation cartography | Stale admin-only or old-key runtime claims |

## Delete-Only Rule

- Removable old-key prompt sources must be deleted rather than redirected.
- Removable old-key seed scripts are deleted, not repointed.
- No wrapper may preserve removed seed behavior.
- No alias may preserve removed prompt keys.
- No compatibility surface may keep old-key prompt generation reachable.
- No fallback may reconstruct old-key prompt runtime.
- No re-export may preserve old-key prompt runtime.
- Archival retention is allowed only as non-executable `_condamad` evidence.

## External Usage Blocker

- External-active consumers block deletion until a user decision is recorded in the removal audit.
- External-active items must not be deleted.
- The blocker must identify the consumer, exact surface, deletion risk, and minimal safe next action.
- `needs-user-decision` rows must keep implementation stopped for that item.

## Generated Contract Check

- Generated contract check: required
- `python` must load the canonical registry and prove Basic or Free taxonomy does not map to old natal keys.
- `app.openapi()` must prove no public schema authorizes an old natal prompt source.
- `app.routes` must prove no public route is added as a substitute for old-key prompt generation.
- `rg` must prove prompt cartography keeps modern natal flows under `theme_natal`.

## Mandatory Reuse / DRY Constraints

- Reuse CS-440 architecture guard files instead of creating a second zero-hit guard suite.
- Reuse existing prompt governance and legacy extinction tests for old-key prompt source proof.
- Reuse existing `theme_astral` prompt contract guard for `basic_natal_prompt_payload` ownership.
- Reuse existing admin catalogue test helpers instead of adding duplicate admin fixture builders.
- Keep each old-key classification in one residual-hit allowlist artifact.

## No Legacy / Forbidden Paths

- No legacy prompt source may remain executable for old natal use cases.
- No compatibility prompt source may remain executable for old natal use cases.
- No fallback prompt source may remain executable for old natal use cases.
- Forbidden prompt keys in runtime source owners:
  - `natal_interpretation_short`
  - `natal_long_free`
  - `natal_interpretation` as Basic or Free prompt owner.
- Forbidden executable surfaces:
  - `backend/app/services/llm_generation/admin_prompts.py` old-key derivation.
  - `backend/app/domain/llm/prompting/catalog.py` old-key fallback.
  - `backend/app/domain/llm/configuration/canonical_use_case_registry.py` Basic/Free old-key mapping.
  - `backend/app/ops/llm/bootstrap` old-key seeds.
  - `backend/scripts` old-key reseed scripts.

## Reintroduction Guard

- Add or update an architecture guard against reintroduction of old natal keys in backend runtime prompt sources.
- The implementation must require an architecture guard against reintroduction.
- The architecture guard must fail when an old natal prompt source is reintroduced.
- Add or update an architecture guard that fails when admin/catalogue tests use old natal keys as positive fixtures.
- Add or update scans that fail when executable bootstrap or root scripts can seed old natal prompt keys.
- Required deterministic guards:
  - `pytest -q backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py`
  - `pytest -q backend/tests/architecture/test_llm_legacy_extinction.py`
  - bounded `rg` scans for the forbidden prompt keys across runtime source roots.
- Deterministic sources: importable Python modules, AST inspection, generated OpenAPI paths, registered routes, and forbidden symbols.

## Regression Guardrails

| Guardrail | Scope -> invariant -> evidence |
|---|---|
| RG-001 `remove-historical-facade-routes` | Old prompt facade sources -> no wrapper, alias, fallback, or re-export -> bounded `rg` and `pytest`. |
| RG-018 `block-supported-family-prompt-fallbacks` | Prompt fallbacks -> natal cannot own fallback prompts -> `pytest` legacy extinction suite. |
| RG-021 `classify-converge-remaining-prompt-fallbacks` | Remaining fallback keys -> each residual key classified -> allowlist artifact and `pytest`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Prompt-generation validation -> test paths are collected -> targeted `pytest` commands. |
| RG-023 `formalize-scripts-ownership` | Root scripts -> old-key scripts deleted or owned -> `pytest` script ownership plus bounded scan. |
| RG-149 `CS-350-prompt-generation-current-implementation` | Cartography -> prompt process matrix stays exact -> cartography `rg` scan. |
| RG-171 `CS-424` | Basic prompt editorial guard -> no old key route for `basic_natal_prompt_payload` -> theme astral pytest. |
| RG-173 `CS-435` | Big Bang natal -> public LLM generation uses product contracts -> OpenAPI/routes plus `rg`. |
| RG-174 `CS-440` | Old natal symbols -> zero public or runtime prompt-source hit -> architecture tests and bounded scans. |

- Scope vector: remove; backend-llm-prompt-sources; admin prompts; prompt catalogues; registries; bootstrap; scripts; backend tests; cartography.
- Needs-investigation: none from the selected local guardrails.
- Non-applicable examples:
  - RG-047 frontend inline style guard is not local because no TSX or CSS surface is touched.
  - RG-052 frontend CSS namespace guard is not local because no frontend build surface is touched.
  - RG-041 entitlement documentation guard is not local because entitlement docs are unchanged.
- Registry gap: none identified for the selected local prompt-source scope.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before hits | `evidence/legacy-source-hits-before.txt` | Capture old-key prompt-source hits before edit. |
| After hits | `evidence/legacy-source-hits-after.txt` | Prove old-key prompt-source hits after edit. |
| Removal audit | `evidence/legacy-source-removal-audit.md` | Classify removed and retained prompt-source items. |
| Residual allowlist | `evidence/legacy-source-allowlist.md` | Limit residual old-key hits to proof-only owners. |
| Validation log | `evidence/validation.txt` | Persist final commands and outcomes. |
| Review output | `_condamad/stories/CS-442-sources-reintroduction-prompts-nataux-legacy/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist required: yes
- Required artifact:
  - `_condamad/stories/CS-442-sources-reintroduction-prompts-nataux-legacy/evidence/legacy-source-allowlist.md`
- Allowed residual classes:
  - `_condamad` historical proof.
  - Explicit rejection or extinction test.
  - Readonly historical row test.
  - Modern `theme_natal` or `theme_astral` guard denying old-key routing.
- Forbidden residual classes:
  - Executable seed.
  - Runtime catalogue fallback.
  - Admin positive sample.
  - Basic or Free taxonomy mapping.
  - Provider-capable old-key prompt path.
- Each residual row must include owner file, reason, command proof and planned permanent owner.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `evidence/legacy-source-removal-audit.md` | old natal prompt keys | Historical proof only. | Permanent historical evidence. |
| `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` | old natal prompt keys | Architecture anti-return guard. | Permanent anti-return evidence. |
| `backend/tests/llm_orchestration/test_llm_legacy_extinction.py` | old natal prompt keys | Extinction guard. | Permanent anti-return evidence. |
| `backend/app/domain/llm/configuration/theme_astral_contracts.py` | `basic_natal_prompt_payload` | Modern theme astral prompt owner. | Permanent canonical owner. |

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/services/llm_generation/admin_prompts.py` - remove `natal_long_free` admin runtime derivation.
- `backend/app/domain/llm/prompting/catalog.py` - remove old natal fallback catalogue entries.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - remove Basic/Free old-key mapping.
- `backend/app/domain/llm/configuration/theme_astral_contracts.py` - preserve `basic_natal_prompt_payload` owner.
- `backend/app/ops/llm/bootstrap` - delete or update old-key bootstrap seeds.
- `backend/scripts` - delete or archive old-key executable scripts.
- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` - update source-hit and fixture-hit guards.
- `backend/tests/architecture/test_llm_legacy_extinction.py` - strengthen old-key absence guard.
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py` - prove registry and fallback state.
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py` - prove old-key prompt source extinction.
- `backend/tests/llm_orchestration/test_assembly_resolution.py` - prove Basic/Free taxonomy ownership.
- `backend/tests/integration/test_admin_llm_catalog.py` - rebase admin positive fixtures.
- `backend/app/tests/integration/test_admin_llm_natal_prompts.py` - rebase admin prompt tests.
- `backend/app/tests/unit/test_scripts_ownership.py` - prove root script ownership after old-key script changes.
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - update prompt-source cartography.
- `_condamad/stories/CS-442-sources-reintroduction-prompts-nataux-legacy/evidence` - persist before/after and audit evidence.

Likely tests:

- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py`
- `backend/tests/architecture/test_llm_legacy_extinction.py`
- `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py`
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py`
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`
- `backend/tests/llm_orchestration/test_assembly_resolution.py`
- `backend/tests/integration/test_admin_llm_catalog.py`
- `backend/app/tests/integration/test_admin_llm_natal_prompts.py`
- `backend/app/tests/unit/test_scripts_ownership.py`

Files not expected to change:

- `frontend/src` - out of scope; no frontend surface is touched.
- `backend/alembic` - out of scope; no schema migration is touched.
- `_condamad/run-state.json` - forbidden by source brief.
- `_condamad/stories/regression-guardrails.md` - not enriched during normal story generation.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q `
  tests/llm_orchestration/test_prompt_governance_registry.py `
  tests/llm_orchestration/test_llm_legacy_extinction.py `
  tests/llm_orchestration/test_assembly_resolution.py --tb=short
python -B -m pytest -q `
  tests/architecture/test_legacy_natal_generation_inventory_guard.py `
  tests/architecture/test_theme_astral_prompt_contract_guard.py `
  tests/architecture/test_llm_legacy_extinction.py --tb=short
python -B -m pytest -q tests/integration/test_admin_llm_catalog.py app/tests/integration/test_admin_llm_natal_prompts.py --tb=short
python -B -m pytest -q app/tests/unit/test_scripts_ownership.py --tb=short
```

- VC1: `ruff format .` in `backend` after venv activation.
- VC2: `ruff check .` in `backend` after venv activation.
- VC3: `pytest` orchestration suite proves governance, extinction and assembly ownership.
- VC4: `pytest` architecture suite proves old-key source absence and `theme_astral` ownership.
- VC5: `pytest` admin suite proves admin/catalogue fixtures no longer use old keys as nominal samples.
- VC5b: `pytest` script ownership guard proves root scripts stay indexed after old-key script changes.

Scans:

- VC6 forbidden pattern: `natal_interpretation_short|natal_long_free|natal_interpretation`.
- VC6 allowed fixture pattern: no matches in runtime roots except `basic_natal_prompt_payload` under `theme_astral_contracts.py`.
- VC6 roots: `app/domain/llm/prompting`, `app/domain/llm/configuration`, `app/ops/llm/bootstrap`,
  `scripts`, `app/services/llm_generation/admin_prompts.py`.
- VC6 expected false positives: `app/domain/llm/configuration/theme_astral_contracts.py` for `basic_natal_prompt_payload` only.

```powershell
rg -n "natal_interpretation_short|natal_long_free|natal_interpretation" `
  app/domain/llm/prompting app/domain/llm/configuration `
  app/ops/llm/bootstrap scripts `
  app/services/llm_generation/admin_prompts.py
```

- VC7 forbidden pattern: `natal_interpretation_short|natal_long_free|fake_generate_natal_interpretation|AIEngineAdapter\.generate_natal_interpretation`.
- VC7 allowed fixture pattern: rejection, extinction, readonly, architecture guard, or `_condamad` proof references only.
- VC7 roots: `tests`, `app/tests`.
- VC7 expected false positives: architecture guards, explicit rejection tests and readonly historical-row tests listed in the allowlist artifact.

```powershell
rg -n "natal_interpretation_short|natal_long_free|fake_generate_natal_interpretation|AIEngineAdapter\.generate_natal_interpretation" tests app/tests
```

- VC8 forbidden pattern: stale old-key runtime or admin-only claims.
- VC8 allowed fixture pattern: documentation stating modern natal generation uses `theme_natal` and old keys are historical or rejected.
- VC8 roots: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`.
- VC8 expected false positives: historical context lines that explicitly state non-runtime or rejected status.

```powershell
rg -n "theme_natal|natal_interpretation_short|natal_long_free|admin-only" _condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md
```

- VC9 runtime contract check:

```powershell
python -B -c "from app.main import app; assert 'natal_long_free' not in str(app.openapi()); assert app.routes"
```

- VC10 persistent evidence check:

```powershell
python -B -c "from pathlib import Path; assert Path('../_condamad/stories/CS-442-sources-reintroduction-prompts-nataux-legacy/evidence/validation.txt').exists()"
```

## Regression Risks

- Admin manual execution may keep a provider-capable path if samples still use old natal keys.
- Deleting executable seeds may expose tests that depended on old prompt rows as convenient fixtures.
- A broad residual allowlist could hide a runtime prompt source; the allowlist must stay exact and file-owned.
- Prompt cartography may remain stale if old keys are removed from code but still described as provider-capable.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Do not modify frontend files.
- Do not modify `_condamad/run-state.json`.
- Do not enrich `_condamad/stories/regression-guardrails.md`.
- Keep historical `_condamad` documents intact.
- Persist every before/after scan and final validation result under the CS-442 evidence directory.

## References

- `_story_briefs/cs-442-corriger-suppression-sources-reintroduction-prompts-nataux-legacy.md`
- `_story_briefs/cs-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy.md`
- `_condamad/reports/cs-439-cs-440-delivery-report.md`
- `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/11-code-review.md`
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/services/llm_generation/admin_prompts.py`
- `backend/app/domain/llm/prompting`
- `backend/app/domain/llm/configuration`
- `backend/app/ops/llm/bootstrap`
- `backend/scripts`
