# Story CS-437 supprimer-catalogues-seeds-scripts-prompts-nataux-legacy: Supprimer Catalogues Seeds Scripts Et Prompts Nataux Legacy
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy.md`.
- Operating mode: Repo-informed story.
- Dependency: CS-434 deleted active public legacy natal generation paths and left a bounded residual allowlist.
- Dependency: CS-436 is the preceding service-path deletion story and must not be contradicted by this cleanup.
- Problem statement: catalogues, canonical registries, bootstrap seeds, runtime scripts and admin prompt helpers can still recreate old natal prompt use cases.
- Source-alignment evidence: every source primitive maps to ACs, tasks, scans, evidence artifacts, non-goals, or blocker rules.

## Objective

Delete or reclassify executable backend prompt sources that can seed, restore, expose, or test old natal prompt use cases as runtime prompt keys.
Keep modern natal generation pointed only at `theme_natal` contracts and keep historical references only as `_condamad` evidence or explicit anti-return tests.

## Target State

- `natal_interpretation_short` is not seedable from backend runtime, bootstrap, or script paths.
- `natal_long_free` is not seedable from backend runtime, bootstrap, or script paths.
- `natal_interpretation` is not mapped to Basic or Free in backend runtime taxonomy.
- Runtime prompt catalogues do not expose the three old natal keys as executable fallback prompts.
- `backend/app/services/llm_generation/admin_prompts.py` cannot create or resolve `natal_long_free`.
- Tests that expected old key presence are converted to absence guards or moved to historical evidence.
- Prompt-generation cartography points modern natal generation to `theme_natal` contracts.
- Remaining old-key hits are limited to `_condamad` history or explicit anti-return tests.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-437`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted ID search read only local brief guardrails.
- Evidence 4: CS-426 `legacy-generation-map.md` classifies seed, bootstrap, script, registry and fallback catalogue surfaces.
- Evidence 5: CS-426 `legacy-surface-classification.md` marks old natal prompt seeds and scripts as deletion or owner-realignment candidates.
- Evidence 6: CS-434 `legacy-allowlist.md` allows script legacy hits only until a dedicated cleanup story.
- Evidence 7: targeted `rg` found `natal_long_free` returned by `admin_prompts.py`.
- Evidence 8: targeted `rg` found old keys in `catalog.py`, `canonical_use_case_registry.py`, bootstrap seeds and backend scripts.
- Evidence 9: targeted `rg` found tests that still assert old-key presence or use old keys as fixtures.
- Repository structure alert: expected backend and frontend roots exist in this workspace; no implementation-created root is required.

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| `natal_interpretation_short` | in scope | AC1, AC4, AC7, Task 1, Task 4 |
| `natal_long_free` | in scope | AC2, AC5, AC7, Task 2, Task 5 |
| `natal_interpretation` as Basic or Free | in scope | AC3, AC6, AC7, Task 3, Task 6 |
| hardcoded prompt catalogues | in scope | AC4, Task 4, Canonical Ownership |
| canonical use case registry | in scope | AC3, Task 3, Ownership Routing Rule |
| bootstrap seeds | in scope | AC1, AC2, AC3, Task 1, Task 2, Task 3 |
| backend scripts | in scope | AC1, AC2, AC6, Task 6, Removal Audit Format |
| `admin_prompts.py` | in scope | AC5, Task 5, Reintroduction Guard |
| prompt-generation cartography | in scope | AC8, Task 8, Persistent Evidence Artifacts |
| `basic_natal_prompt_payload` | in scope | AC9, Task 9, Allowlist / Exception Register |
| existing development DB rows | out of scope | Explicit non-goals |
| Guidance, Chat, Horoscope daily prompts | out of scope | Explicit non-goals |
| global entitlement variant rename | out of scope | Explicit non-goals |
| new premium prompt | out of scope | Explicit non-goals |

## Domain Boundary

- Domain: backend-llm-prompt-runtime-sources
- In scope:
  - Backend prompt catalogues under `backend/app/domain/llm/prompting`.
  - Backend canonical prompt/use-case registries under `backend/app/domain/llm/configuration`.
  - Backend LLM bootstrap seeds under `backend/app/ops/llm/bootstrap`.
  - Backend executable scripts under `backend/scripts`.
  - Admin prompt creation and resolution helper `backend/app/services/llm_generation/admin_prompts.py`.
  - Prompt governance tests, legacy extinction tests, assembly resolution tests and architecture guards.
  - Prompt-generation cartography under `_condamad/docs/prompt-generation-cartography`.
  - Story evidence under `_condamad/stories/CS-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy/**`.
- Out of scope:
  - Frontend UI, DB schema migration, auth, i18n, styling, build tooling, Stripe, public route contracts and data deletion.
- Explicit non-goals:
  - No deletion of persisted development database rows.
  - No change to Guidance, Chat, Horoscope daily or other non-natal prompt families.
  - No global entitlement variant rename.
  - No new premium prompt contract.
  - No compatibility script, alias, facade, fallback, wrapper, re-export, or soft-disabled seed path.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: the story deletes executable old prompt seed and catalogue surfaces that can recreate historical natal runtime keys.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Modern natal runtime remains owned by `theme_natal` contracts.
  - Historical references remain only in `_condamad` evidence or explicit anti-return tests.
  - The only allowed surface delta is deletion or inversion of old natal prompt seed and catalogue sources.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: a script or seed is proven externally active outside development and cannot be archived as `_condamad` evidence.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, AST guards and bounded `rg` scans prove old prompt sources cannot run. |
| Baseline Snapshot | yes | Before and after scans prove the only allowed surface delta. |
| Ownership Routing | yes | `theme_natal` owns modern natal prompt contracts; old raw keys cannot own Basic or Free. |
| Allowlist Exception | yes | Remaining historical hits need a bounded evidence register with owners. |
| Contract Shape | yes | Catalog, registry, admin helper and cartography shapes must name only modern natal owners. |
| Batch Migration | no | No DB data migration or multi-record conversion is in scope. |
| Reintroduction Guard | yes | Old key seed and catalogue paths must fail deterministic guards. |
| Persistent Evidence | yes | Removal audit, scans, validation and review artifacts must be persisted. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `natal_interpretation_short` is not seedable. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scan; `pytest` architecture guard. |
| AC2 | `natal_long_free` is not seedable. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scan; `pytest` extinction guard. |
| AC3 | Basic/Free taxonomy excludes `natal_interpretation`. | Evidence profile: no_legacy_contract; prompt governance `pytest`. |
| AC4 | Prompt fallback catalogues exclude old natal keys. | Evidence profile: no_legacy_contract; `pytest` extinction guard; `rg` scans `catalog.py`. |
| AC5 | Admin prompt resolution excludes `natal_long_free`. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans `admin_prompts.py`; `pytest`. |
| AC6 | Executable scripts do not reseed old natal keys. | Evidence profile: python_module_removed; `rg` scans `backend/scripts`; `pytest` inventory guard. |
| AC7 | Presence tests become absence guards. | Evidence profile: reintroduction_guard; `pytest -q backend/tests/llm_orchestration`; `rg` scans `backend/tests backend/app/tests`. |
| AC8 | Prompt cartography points to `theme_natal`. | Evidence profile: batch_migration_mapping; `rg` scans prompt-generation cartography. |
| AC9 | `basic_natal_prompt_payload` stays modern only. | Evidence profile: ast_architecture_guard; `pytest` theme astral guard; `AST guard`. |
| AC10 | Removal evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence artifacts. |

## Implementation Tasks

- [ ] Task 1: Delete executable `natal_interpretation_short` seeds from bootstrap and script paths. (AC: AC1)
- [ ] Task 2: Delete executable `natal_long_free` seeds from bootstrap and script paths. (AC: AC2)
- [ ] Task 3: Remove Basic or Free taxonomy mappings to raw `natal_interpretation`. (AC: AC3)
- [ ] Task 4: Remove old natal keys from prompt fallback catalogue ownership. (AC: AC4)
- [ ] Task 5: Remove `natal_long_free` fallback creation or resolution from `admin_prompts.py`. (AC: AC5)
- [ ] Task 6: Delete executable old-key backend scripts or archive them as `_condamad` evidence. (AC: AC6)
- [ ] Task 7: Convert presence tests into absence guards for old natal prompt keys. (AC: AC7)
- [ ] Task 8: Update prompt-generation cartography to show `theme_natal` as the modern natal owner. (AC: AC8)
- [ ] Task 9: Keep `basic_natal_prompt_payload` only under the modern `theme_astral` contract owner. (AC: AC9)
- [ ] Task 10: Persist before and after scans, removal audit and final validation output. (AC: AC10)

## Files to Inspect First

- `_story_briefs/cs-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy.md` - source contract.
- `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/legacy-generation-map.md` - starting surface map.
- `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/legacy-surface-classification.md` - prior decisions.
- `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/legacy-allowlist.md` - residual allowlist.
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - canonical prompt-generation map.
- `backend/app/domain/llm/prompting/catalog.py` - fallback prompt catalogue owner.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - canonical use-case registry owner.
- `backend/app/ops/llm/bootstrap/seed_29_prompts.py` - historical prompt bootstrap seed.
- `backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py` - V3 natal prompt bootstrap seed.
- `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py` - product taxonomy bootstrap seed.
- `backend/scripts/seed_natal_short.py` - executable old short seed script.
- `backend/scripts/seed_66_15_assembly_convergence.py` - executable assembly convergence seed script.
- `backend/scripts/seed_66_20_convergence.py` - executable taxonomy convergence seed script.
- `backend/app/services/llm_generation/admin_prompts.py` - admin prompt helper with old free fallback.
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py` - existing extinction tests.
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py` - prompt governance tests.
- `backend/tests/llm_orchestration/test_assembly_resolution.py` - assembly resolution tests.
- `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py` - modern prompt payload guard.
- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` - inventory guard.

## Runtime Source of Truth

- Primary source of truth:
  - `pytest`, AST guard and bounded `rg` scans over backend runtime, scripts and tests.
- Secondary evidence:
  - Removal audit and prompt-generation cartography diff under the story evidence directory.
- Static scans alone are not sufficient for this story because:
  - Tests must prove old keys cannot remain executable through prompt governance, assembly resolution, bootstrap or admin helper paths.

## Contract Shape

- Contract type:
  - Backend prompt source deletion contract and prompt-generation cartography contract.
- Fields:
  - `theme_natal`: canonical modern natal prompt-generation owner.
  - `basic_natal_prompt_payload`: allowed only as `theme_astral` modern runtime contract input.
- Required fields:
  - `theme_natal`.
- Optional fields:
  - `basic_natal_prompt_payload` under the modern `theme_astral` contract owner.
- Forbidden runtime prompt keys:
  - `natal_interpretation_short`.
  - `natal_long_free`.
  - `natal_interpretation` as Basic or Free.
- Forbidden executable owners:
  - `backend/scripts`.
  - `backend/app/ops/llm/bootstrap`.
  - `backend/app/domain/llm/prompting/catalog.py`.
  - `backend/app/services/llm_generation/admin_prompts.py`.
- Status codes:
  - no HTTP status code changes are authorized.
- Serialization names:
  - `theme_natal` is emitted as `theme_natal`.
  - `basic_natal_prompt_payload` is emitted only under the modern owner.
- Frontend type impact:
  - none; frontend is out of scope.
- Generated contract impact:
  - registry and cartography checks must prove old keys are absent from Basic or Free ownership.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy/evidence/legacy-prompt-source-scan-before.txt`
  - `_condamad/stories/CS-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy/evidence/cartography-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy/evidence/legacy-prompt-source-scan-after.txt`
  - `_condamad/stories/CS-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy/evidence/cartography-after.md`
- Expected invariant:
  - The only allowed surface delta is deletion or inversion of old natal prompt seed, catalogue, script and test-presence sources.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Modern natal prompt generation | `backend/app/domain/theme_natal/**` and `theme_natal` contracts | Raw old natal use-case keys |
| Fallback prompt catalogue | Non-supported historical fallback entries only | Supported natal products |
| Product taxonomy | `theme_natal` product contracts | Basic or Free mapped to `natal_interpretation` |
| Admin prompt maintenance | Explicit admin-only non-public owners | `natal_long_free` fallback resolution |
| Historical evidence | `_condamad/stories/**` and `_condamad/docs/**` | Executable backend script path |

## Removal Classification Rules

- `canonical-active`: modern `theme_natal` contract or modern `theme_astral` prompt payload owner.
- `external-active`: public docs, generated contract, ops runbook, or known consumer still depends on executing an old-key script or seed.
- `historical-facade`: executable old-key seed, script, catalogue row, registry mapping, or admin fallback kept for historical behavior.
- `dead`: old-key source has no production, test, docs, generated contract, or known external consumer after required scans.
- `needs-user-decision`: scans prove unresolved execution risk that cannot be closed inside this story.
- Required decision:
  - `historical-facade` and `dead` items must be deleted or archived as non-executable `_condamad` evidence.
  - `external-active` items must block deletion until the user decision is recorded.

## Removal Audit Format

The implementation must persist:

`_condamad/stories/CS-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy/evidence/removal-audit.md`

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

- `Classification` must use `canonical-active`, `external-active`, `historical-facade`, `dead`, or `needs-user-decision`.
- `Decision` must use `keep`, `delete`, `replace-consumer`, or `needs-user-decision`.
- `Proof` must include command output, file path evidence, `pytest`, `python`, `AST guard`, or bounded `rg`.
- `Risk` must be filled for every `delete` or `needs-user-decision` row.

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Modern natal prompt contracts | `backend/app/domain/theme_natal/**` | Raw `natal_interpretation` prompt keys |
| Modern Basic prompt payload | `theme_astral` contract owner | Legacy `natal_interpretation` runtime owner |
| Prompt fallback governance | `test_llm_legacy_extinction.py` and prompt governance registry | Supported natal fallback catalogue ownership |
| Executable seeding | Current bootstrap owners with modern keys | Old natal seed scripts |
| Prompt cartography | `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` | Untracked script comments |

## Delete-Only Rule

- Removable old-key prompt sources must be deleted rather than redirected.
- Removable old-key seed scripts are deleted, not repointed.
- No wrapper may preserve the removed seed behavior.
- No alias may preserve the removed prompt key.
- No compatibility path may keep old natal prompt generation active.
- No fallback may recreate old natal prompt ownership.
- No re-export may preserve a deleted script import path.
- `_condamad` archival is allowed only as non-executable evidence.

## External Usage Blocker

- External-active consumers block deletion until a user decision is recorded in the removal audit.
- External-active items must not be deleted.
- The blocker must identify the consumer, exact surface, deletion risk, and minimal safe next action.
- `needs-user-decision` rows must keep implementation stopped for that item.
- Development DB rows are not external-active because this story does not delete database data.

## Generated Contract Check

- Generated contract check: required
- `python` must load the canonical registry and prove Basic or Free taxonomy does not map to old natal keys.
- `rg` must prove prompt cartography keeps modern natal flows under `theme_natal`.
- `app.openapi()` is secondary only because no public API route shape is changed.

## Mandatory Reuse / DRY Constraints

- Reuse CS-426 inventory and CS-434 allowlist instead of creating a second broad legacy inventory.
- Reuse existing prompt governance, legacy extinction, assembly resolution and architecture guard tests.
- Keep one removal audit artifact for deleted or archived old-key prompt sources.
- Keep one evidence scan before and one evidence scan after for old-key prompt source hits.
- Do not add a duplicate prompt catalogue, registry, admin helper, bootstrap framework, or script ownership mechanism.

## No Legacy / Forbidden Paths

- No legacy prompt seed path may remain executable for the three old natal keys.
- No compatibility prompt seed path may remain executable for the three old natal keys.
- No fallback prompt ownership may remain executable for supported natal products.
- Forbidden runtime symbols in executable backend source:
  - `natal_interpretation_short`
  - `natal_long_free`
  - `natal_interpretation` mapped to Basic or Free
  - `seed_natal_short`
  - `seed_30_8_v3_prompts` as old natal prompt bootstrap
  - `get_active_prompt_version(db, "natal_interpretation_short"`
- Remaining hits must be `_condamad` evidence, explicit anti-return tests, or modern `theme_astral` payload ownership.

## Reintroduction Guard

- Add or update an architecture guard that fails when old natal keys appear in executable bootstrap seeds.
- The implementation must require an architecture guard against reintroduction.
- The architecture guard must fail when a removed old-key prompt source is reintroduced.
- Add or update an architecture guard that fails when old natal keys appear in executable backend scripts.
- Add or update a guard that fails when `admin_prompts.py` returns `natal_long_free`.
- Add or update prompt governance tests that fail when supported natal products regain fallback catalogue ownership.
- Add bounded `rg` scans with a documented allowed fixture pattern and expected false positives.
- Deterministic sources: forbidden symbols, importable Python modules, backend tests, bootstrap files, script files and cartography artifacts.

## Regression Guardrails

| Guardrail | Scope -> invariant -> evidence |
|---|---|
| RG-018 `block-supported-family-prompt-fallbacks` | natal fallback catalogue -> no supported natal fallback owner -> `pytest` and targeted `rg`. |
| RG-021 `classify-converge-remaining-prompt-fallbacks` | fallback registry -> every survivor classified -> prompt governance `pytest`. |
| RG-023 `formalize-scripts-ownership` | script cleanup -> no unowned executable seed script -> architecture `pytest` and `rg`. |
| RG-149 `CS-350-prompt-generation-current-implementation` | prompt cartography -> modern natal owner remains mapped -> documentary `rg`. |
| RG-171 `CS-424` | Basic prompt payload -> no old prompt key route -> theme astral `pytest` and carrier scan. |
| RG-173 `CS-435` | public LLM generation -> product+LLM contracts only -> `pytest`, AST guard and `rg`. |

- Needs-investigation: resolver returned only generic RG-002 for this scope vector; brief-required IDs were loaded by targeted ID search.
- Non-applicable example: frontend `/natal` DOM guardrails are outside this backend prompt-source deletion.
- Non-applicable example: DB migration guardrails are outside this story because no database data deletion is authorized.
- Non-applicable example: i18n and styling guardrails are outside this backend LLM prompt-source domain.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Removal audit | `_condamad/stories/CS-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy/evidence/removal-audit.md` | Classify old-key sources. |
| Scan before | `_condamad/stories/CS-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy/evidence/legacy-prompt-source-scan-before.txt` | Capture starting hits. |
| Scan after | `_condamad/stories/CS-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy/evidence/legacy-prompt-source-scan-after.txt` | Capture final hits. |
| Cartography before | `_condamad/stories/CS-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy/evidence/cartography-before.md` | Capture starting map. |
| Cartography after | `_condamad/stories/CS-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy/evidence/cartography-after.md` | Capture final map. |
| Validation output | `_condamad/stories/CS-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy/evidence/validation.txt` | Store final commands. |
| Review output | `_condamad/stories/CS-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy/generated/11-code-review.md` | Review handoff. |

## Allowlist / Exception Register

- Allowlist required: yes
- Required artifact:
  - `_condamad/stories/CS-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy/evidence/legacy-prompt-source-allowlist.md`
- Required operational columns for `legacy-prompt-source-allowlist.md`:
  - `symbol | file | reason | allowed_context | non_generative_proof | owner | expiry_decision`
- Required allowlist table:

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|

- Allowed contexts:
  - `condamad-historical-doc`
  - `test-guard`
  - `condamad-evidence`
  - `modern-theme-astral-contract`
- Not allowed:
  - public runtime generation, executable seed, bootstrap recreation, admin fallback creation, hidden wrapper, stub, alias, or soft-disabled script.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/llm/prompting/catalog.py` - remove old natal fallback prompt ownership.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - remove Basic or Free old-key mappings.
- `backend/app/ops/llm/bootstrap/seed_29_prompts.py` - remove old prompt seed entries.
- `backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py` - delete or archive old natal prompt bootstrap.
- `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py` - remove old product taxonomy mappings.
- `backend/scripts/seed_natal_short.py` - delete or archive as non-executable `_condamad` evidence.
- `backend/scripts/seed_30_2_astroresponse_v2.py` - delete or archive as non-executable `_condamad` evidence.
- `backend/scripts/seed_30_3_gpt5_prompts.py` - remove old-key handling or block on an explicit owner decision.
- `backend/scripts/seed_66_15_assembly_convergence.py` - remove old-key convergence rows.
- `backend/scripts/seed_66_20_convergence.py` - remove old-key convergence rows.
- `backend/scripts/update_all_prompts_59_5.py` - delete or classify old-key special handling.
- `backend/app/services/llm_generation/admin_prompts.py` - remove `natal_long_free` fallback creation and resolution.
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py` - add or update absence guards.
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py` - update prompt governance expectations.
- `backend/tests/llm_orchestration/test_assembly_resolution.py` - update assembly resolution expectations.
- `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py` - preserve modern prompt payload ownership.
- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` - update old-key source inventory guard.
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - update modern natal map.
- `_condamad/stories/CS-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy/evidence/**` - persist audit evidence.

Likely tests:

- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py`
- `backend/tests/llm_orchestration/test_assembly_resolution.py`
- `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py`
- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py`

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no DB migration is authorized.
- `backend/alembic/**` - out of scope; no DB migration is authorized.
- Runtime route handlers under `backend/app/api/**` - out of scope for this prompt-source deletion.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
ruff format backend
ruff check backend
python -B -m pytest -q backend/tests/llm_orchestration/test_llm_legacy_extinction.py `
  backend/tests/llm_orchestration/test_prompt_governance_registry.py `
  backend/tests/llm_orchestration/test_assembly_resolution.py --tb=short
python -B -m pytest -q backend/tests/architecture/test_theme_astral_prompt_contract_guard.py `
  backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py --tb=short
```

Scans:

```powershell
rg -n "natal_interpretation_short|natal_long_free|natal_interpretation" `
  backend/app/domain/llm/prompting backend/app/domain/llm/configuration `
  backend/app/ops/llm/bootstrap backend/scripts backend/app/services/llm_generation/admin_prompts.py
rg -n "get_active_prompt_version\(db, \"natal_interpretation_short\"|seed_natal_short|seed_30_8_v3_prompts" backend/tests backend/app/tests backend/scripts
rg -n "theme_natal|natal_interpretation_short|natal_long_free|admin-only" _condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md
```

- Scan 1 forbidden pattern: old natal prompt keys in executable prompt, registry, seed, script, or admin helper roots.
- Scan 1 roots:
  - `backend/app/domain/llm/prompting`
  - `backend/app/domain/llm/configuration`
  - `backend/app/ops/llm/bootstrap`
  - `backend/scripts`
  - `backend/app/services/llm_generation/admin_prompts.py`
- Scan 1 allowed fixture pattern: none in executable roots.
- Scan 1 expected false positives: zero, apart from non-executable comments moved under `_condamad` evidence.
- Scan 2 forbidden pattern: tests or scripts that recreate old seed entry points.
- Scan 2 roots: `backend/tests backend/app/tests backend/scripts`.
- Scan 2 allowed fixture pattern: explicit anti-return test assertions only.
- Scan 2 expected false positives: architecture guard strings and removal-audit fixture paths only.
- Scan 3 forbidden pattern: cartography that promotes old natal keys over `theme_natal` or loses admin-only classification.
- Scan 3 roots: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`.
- Scan 3 allowed fixture pattern: historical rows and explicit deleted/admin-only classifications.
- Scan 3 expected false positives: historical evidence rows with deleted or admin-only status.

Evidence artifact checks:

```powershell
.\.venv\Scripts\Activate.ps1
python -B -c "from pathlib import Path; p=Path('_condamad/stories/CS-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy/evidence/removal-audit.md'); assert p.exists()"
$env:CS437_EVIDENCE = "_condamad/stories/CS-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy/evidence"
python -B -c "from os import environ; from pathlib import Path; assert (Path(environ['CS437_EVIDENCE'])/'legacy-prompt-source-scan-after.txt').exists()"
```

## Regression Risks

- An executable seed script may keep recreating old prompt rows after the active service path is deleted.
- A governance test may keep an old key alive as a nominal fixture instead of an anti-return guard.
- `admin_prompts.py` may keep resolving `natal_long_free` as a fallback creation path.
- `basic_natal_prompt_payload` may be misread as owned by raw `natal_interpretation` instead of modern `theme_astral`.
- Cartography drift may hide old prompt sources outside the modern `theme_natal` map.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Run Python commands only after activating `.\.venv\Scripts\Activate.ps1`.
- Keep comments and docstrings in French for new or significantly modified application files.
- Delete executable old-key prompt sources instead of redirecting them.
- Keep `_condamad/stories/regression-guardrails.md` unchanged.

## References

- `_story_briefs/cs-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/legacy-generation-map.md`
- `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/legacy-surface-classification.md`
- `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/legacy-allowlist.md`
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `backend/app/domain/llm/prompting/catalog.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/ops/llm/bootstrap`
- `backend/scripts`
- `backend/app/services/llm_generation/admin_prompts.py`
