# Story CS-426 freeze-inventory-legacy-generation-natal-bigbang: Freeze Inventory Legacy Generation Natal Big Bang
Status: ready-to-review

Commentaire global: cette story fige l'inventaire des surfaces capables de generer une lecture natale legacy avant le Big Bang.

## Trigger / Source

Brief direct from `_story_briefs/cs-426-freeze-inventory-legacy-generation-natal-bigbang.md`.
Selected mode: Repo-informed story, because mandatory source files define the inventory boundary.

Source problem statement: before adding `ThemeNatalReadingProductContract`, the team needs a persistent map of every path still able to
produce a public natal reading through old use cases, prompt seeds, front triggers, service paths, gateways, persistence, or scripts.

Source stakes:

- User impact: Basic users can receive Free-short or premium-shaped content behind a Basic label.
- Technical risk: a Big Bang model can become one more layer above `natal_long_free`, `natal_interpretation_short`, and `natal_interpretation`.
- Closure expectation: this story produces the inventory and classification that later destructive stories must enforce.
- Forbidden regression: `_condamad/run-state.json` deletion remains out of scope.

Source-alignment review: objective, target state, ACs, tasks, evidence, non-goals, and guardrails map to the brief's inventory stakes.

## Objective

Produce a persistent inventory of every natal legacy generation surface, classify each surface, and persist the initial scans that will
become blocking evidence for later Big Bang stories. This story adds no functional runtime behavior.

## Target State

- `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/legacy-generation-map.md` lists each generative path.
- `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/legacy-surface-classification.md` classifies each surface.
- `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/initial-scans.txt` preserves the required scans.
- Classifications use exactly `delete`, `replace`, `readonly`, `keep`, or `needs-decision`.
- `readonly` entries are explicitly non-generative.
- `needs-decision` entries include the expected decision and owner.
- `_condamad/run-state.json` is documented as out of scope and remains unchanged.
- No new runtime, route, provider, migration, schema, DB table, or frontend behavior is introduced.

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| Public, admin, and dev natal generation endpoints | in scope | AC1, Task 1, VC1, VC5 |
| Services, gateways, seeds, prompts, schemas, tests, mocks | in scope | AC3, AC4, Task 3, VC1, VC3, VC4 |
| Frontend `use_case_level`, `variant_code`, `forceRefresh` | in scope | AC2, Task 2, VC2 |
| `natal_interpretation_short` | in scope | AC1, AC3, VC1, VC3 |
| `natal_long_free` | in scope | AC1, AC2, VC1 |
| `natal_interpretation` | in scope | AC1, AC3, VC1, VC3 |
| `basic_natal_prompt_payload` | in scope | AC3, VC1, VC3 |
| Cache or persistence without `chart_id` | in scope | AC4, VC4 |
| Public deterministic fallback | in scope | AC3, AC4, VC3 |
| `ThemeNatalReadingProductContract` | out of scope | Non-goals, AC9 |
| DB tables and migrations | out of scope | Non-goals, AC9 |
| New provider or fake provider | out of scope | Non-goals, AC9 |
| Physical code deletion | out of scope | Non-goals, AC9 |
| Frontend runtime modification | out of scope | Non-goals, AC9 |
| `_condamad/run-state.json` deletion | out of scope | AC8, Task 8, VC5 |

## Current State Evidence

- Evidence 1: `_story_briefs/cs-426-freeze-inventory-legacy-generation-natal-bigbang.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-426`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted IDs from the brief were consulted.
- Evidence 4: `resolve_guardrails.py` - scope vector was run for audit, natal generation inventory, backend paths, and frontend paths.
- Evidence 5: `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md` - live test report consulted.
- Evidence 6: `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - Big Bang report consulted by targeted scan.
- Evidence 7: `_story_briefs/cs-425-invalider-regenerer-lectures-basic-natal-degradees.md` - upstream Basic cache story consulted.
- Evidence 8: selected source files show current paths for API routing, service generation, gateway recovery, frontend trigger, and API client.

Repository structure alert: none. `backend`, `backend/app`, `backend/tests`, `frontend`, and `frontend/src` exist in this workspace.

## Domain Boundary

- Domain: natal-legacy-generation-inventory
- In scope:
  - Inventory and classification of natal legacy generation paths across backend, frontend trigger code, seeds, prompts, scripts, and reports.
  - Persistent evidence artifacts under this story directory.
  - Targeted scans over the roots named by the source brief.
- Out of scope:
  - New runtime, frontend UI, database schema, auth, i18n, styling, build tooling, migrations, and provider integration.
  - Physical deletion of legacy code or `_condamad/run-state.json`.
- Explicit non-goals:
  - No `ThemeNatalReadingProductContract` implementation.
  - No new route, service, gateway behavior, provider, fake provider, seed execution, schema, DB table, migration, or frontend runtime change.
  - No mass refactor, compatibility bridge, wrapper, alias, shim, or broad allowlist.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: the story inventories legacy generation facades before later destructive removal work.
- Behavior change allowed: no
- Behavior change constraints:
  - Runtime application behavior changes are forbidden in this inventory story.
  - Add or modify only story tracker, story evidence artifacts, generated review output, and executable guard evidence.
  - Preserve functional application code unchanged.
- Deletion allowed: yes
- Deletion constraints: `delete` is only an inventory classification for later stories; physical code deletion is forbidden here.
- Replacement allowed: no
- User decision required if: an inventory surface cannot be classified without product or architecture ownership.
- Additional validation rules:
  - Classification values are limited to `delete`, `replace`, `readonly`, `keep`, and `needs-decision`.
  - Every generative entry records file path, symbol, trigger, exposure, use case, and classification.
  - Every `needs-decision` entry records expected decision and owner.
  - Every `readonly` entry states why it cannot generate new LLM output.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Runtime-capable surfaces are classified from loaded code paths, scans, and source reports. |
| Baseline Snapshot | yes | The initial scans become before-state evidence for later destructive work. |
| Ownership Routing | yes | Each surface needs a canonical owner before later removal or replacement work. |
| Allowlist Exception | yes | The allowed delta must stay limited to inventory evidence and guard artifacts. |
| Contract Shape | yes | The evidence artifacts have a fixed classification shape and required columns. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Later stories must not add new legacy generation paths before classification. |
| Persistent Evidence | yes | Inventory reports and scans must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Backend natal generation routes are mapped. | Evidence profile: ast_architecture_guard; `rg` VC1; `AST guard`; `python` checks map. |
| AC2 | Frontend natal generation triggers are mapped. | Evidence profile: targeted_forbidden_symbol_scan; `rg` VC2; `python` checks `legacy-generation-map.md`. |
| AC3 | Natal prompt/seed surfaces are classified. | Evidence profile: targeted_forbidden_symbol_scan; `rg` VC3; `python` checks classification artifact. |
| AC4 | Cache/persistence generation surfaces are classified. | Evidence profile: targeted_forbidden_symbol_scan; `rg` VC4; `python` checks classification artifact. |
| AC5 | Readonly surfaces are non-generative. | Evidence profile: json_contract_shape; `python` checks `readonly` and `non-generative` tokens. |
| AC6 | Needs-decision surfaces have owners. | Evidence profile: json_contract_shape; `python` checks `needs-decision`, `owner`, and `expected decision`. |
| AC7 | Exposure classes are recorded. | Evidence profile: json_contract_shape; `python` checks public, admin-only, test-only, bootstrap, and historical tokens. |
| AC8 | `_condamad/run-state.json` remains out of scope. | Evidence profile: repo_wide_negative_scan; `git status --short -- _condamad/run-state.json`; `rg` story evidence. |
| AC9 | Functional application code stays unchanged. | Concrete validation command: run the `python` check in VC11; app runtime delta must be empty. |
| AC10 | Initial scans are persisted. | Evidence profile: baseline_before_after_diff; `python` checks `evidence/initial-scans.txt`. |

## Implementation Tasks

- [x] Task 1: Map public, admin, and dev backend paths that can trigger natal generation. (AC: AC1, AC7)
- [x] Task 2: Map frontend controls that send use-case level, variant code, or force refresh signals. (AC: AC2, AC7)
- [x] Task 3: Classify seeds, prompts, use cases, schemas, tests, mocks, services, gateways, scripts, and reports. (AC: AC3, AC4)
- [x] Task 4: Separate `readonly` historical reads from active generation paths. (AC: AC5)
- [x] Task 5: Assign `delete`, `replace`, `readonly`, `keep`, or `needs-decision` to every mapped surface. (AC: AC3, AC4, AC6)
- [x] Task 6: Persist all required scans in `evidence/initial-scans.txt`. (AC: AC10)
- [x] Task 7: Record source alignment and classification assumptions in the evidence artifacts. (AC: AC6, AC7)
- [x] Task 8: Document `_condamad/run-state.json` as out of scope without modifying it. (AC: AC8)
- [x] Task 9: Verify the worktree only contains story, tracker, and evidence artifacts for this inventory. (AC: AC9)

## Files to Inspect First

- `_story_briefs/cs-426-freeze-inventory-legacy-generation-natal-bigbang.md` - source brief.
- `_condamad/stories/regression-guardrails.md` - targeted guardrail IDs from the brief.
- `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md` - live Basic and Free generation report.
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - Big Bang prompt and response report.
- `_story_briefs/cs-425-invalider-regenerer-lectures-basic-natal-degradees.md` - upstream cache invalidation context.
- `backend/app/api/v1/routers/public/natal_interpretation.py` - public route and generation trigger boundary.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - natal generation service and persistence behavior.
- `backend/app/domain/llm/runtime/gateway.py` - runtime fallback, recovery, and use-case mapping behavior.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - frontend generation trigger behavior.
- `frontend/src/api/natal-chart/index.ts` - frontend API request contract.
- `backend/app/ops/llm/bootstrap` - seed and prompt bootstrap surfaces.
- `backend/scripts` - operational and diagnostic script surfaces.

## Runtime Source of Truth

- Primary source of truth:
  - `AST guard` over the source files named in the brief.
  - Targeted scans over the source files named in the brief.
  - Source reports describing observed live generation behavior.
  - The generated manifest `legacy-generation-map.md` and `legacy-surface-classification.md`.
- Secondary evidence:
  - `git status --short -- _condamad _story_briefs backend frontend`.
  - Targeted `python` checks that required artifact tokens exist.
- Static scans alone are not sufficient for this story because:
  - The final classification must also distinguish active generation, readonly readback, bootstrap, admin-only, test-only, and historical surfaces.

## Contract Shape

- Contract type:
  - Persistent inventory and classification artifacts.
- Fields:
  - `surface`, `symbol`, `trigger`, `generation mode`, `legacy primitive`, `classification`, `evidence`, and `notes`.
- Required fields:
  - `surface`, `symbol`, `trigger`, `generation mode`, `legacy primitive`, `classification`, and `evidence`.
- Required fields for `legacy-generation-map.md` rows:
  - `surface`: canonical path or source artifact.
  - `symbol`: route, function, class, seed key, prompt key, test, mock, or component symbol.
  - `trigger`: public, admin, dev, bootstrap, test, historical, or frontend trigger.
  - `generation mode`: active-generation, readonly, bootstrap, test-only, admin-only, or historical.
  - `legacy primitive`: one of the named brief primitives or `none`.
  - `classification`: `delete`, `replace`, `readonly`, `keep`, or `needs-decision`.
  - `evidence`: scan command or source line reference.
- Required fields for `legacy-surface-classification.md` rows:
  - `surface`, `classification`, `rationale`, `owner`, `expected decision`, and `next story input`.
- Optional fields:
  - `notes`.
- Status codes:
  - none.
- Serialization names:
  - Markdown table column names are emitted exactly as listed above.
- Frontend type impact:
  - none.
- Generated contract impact:
  - Check required because API, frontend, and field surfaces are inventoried.
  - No generated OpenAPI, route manifest, or TypeScript client output may change in this inventory story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/initial-scans.txt`
- Comparison after implementation:
  - Later stories must compare their destructive scans against this inventory.
- Expected invariant:
  - The only intended surface delta in this story is documentation and evidence under this story directory plus the tracker row.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Public route inventory | `backend/app/api/v1/routers/public/natal_interpretation.py` entry in evidence | New route implementation |
| Generation service inventory | `backend/app/services/llm_generation/natal/interpretation_service.py` entry in evidence | Service behavior change |
| Runtime gateway inventory | `backend/app/domain/llm/runtime/gateway.py` entry in evidence | Gateway behavior change |
| Frontend trigger inventory | `frontend/src/features/natal-chart/NatalInterpretation.tsx` entry in evidence | Frontend runtime change |
| API client inventory | `frontend/src/api/natal-chart/index.ts` entry in evidence | Generated client change |
| Prompt and seed inventory | `backend/app/ops/llm/bootstrap` and `backend/scripts` entries in evidence | Seed execution |

## Mandatory Reuse / DRY Constraints

- Reuse the source brief's classification vocabulary exactly.
- Reuse the required scan commands as the canonical baseline.
- Do not duplicate the same surface under multiple names; use one canonical row plus notes.
- Do not add a second evidence format for the same inventory fact.
- Keep the generated evidence under this story directory.

## No Legacy / Forbidden Paths

- No legacy route, wrapper, or facade may be introduced.
- No compatibility bridge may be introduced.
- No fallback path may be added or promoted.
- No shim, alias, or broad allowlist may be used to close an unknown surface.
- No functional edits are authorized under `backend/app`, `backend/scripts`, `frontend/src`, or DB migration roots.
- No new Big Bang runtime, provider, fake provider, schema, table, migration, frontend behavior, or seed execution is authorized.

## Reintroduction Guard

- Guard target:
  - `natal_interpretation_short`, `natal_long_free`, `natal_interpretation`, `basic_natal_prompt_payload`, `use_case_level`,
    `variant_code`, `forceRefresh`, `PROMPT_FALLBACK_CONFIGS`, `fallback_default`, `AstroResponse_v3`, and `EXIGENCE PREMIUM`.
- Deterministic guard:
  - Deterministic source: forbidden symbols.
  - Required architecture guard against reintroduction: `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py`.
  - Evidence profile: `reintroduction_guard`; `pytest -q backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py`.
  - Architecture guard against reintroduction: forbidden legacy generation symbols fail if reintroduced unclassified.
  - The guard must fail if a new unclassified legacy generation surface is introduced.
  - VC1 through VC5 must be preserved in `evidence/initial-scans.txt`.
  - VC6 checks that `_condamad/run-state.json` has no worktree change.
- Allowed surface delta:
  - Story markdown, inventory evidence artifacts, generated review handoff path, architecture guard evidence, and tracker row.

## Regression Guardrails

Applicable guardrails:

| Guardrail | scope -> invariant -> evidence |
|---|---|
| RG-001 `remove-historical-facade-routes` | legacy routes -> no wrapper return -> VC1, VC5. |
| RG-002 `refactor-api-v1-routers` | API router inventory -> router stays adapter -> VC1, VC5. |
| RG-005 `remove-api-v1-router-logic` | API boundary -> no route-owned business logic edit -> VC5. |
| RG-018 `block-supported-family-prompt-fallbacks` | natal prompts -> no prompt fallback ownership -> VC3. |
| RG-021 `classify-converge-remaining-prompt-fallbacks` | prompt fallback keys -> classification required -> VC3. |
| RG-149 `CS-350-prompt-generation-current-implementation` | prompt-generation map -> explicit categories -> AC7, VC1, VC3. |
| RG-150 `CS-384-separer-interpretations-natales-acceptees-rejets-llm` | rejected payloads -> public exclusion remains mapped -> VC4. |
| RG-152 `CS-392-implementer-generation-narrative-natal-reading-v1` | public natal reading -> no internal audit exposure change -> VC5. |
| RG-157 `CS-398-rendre-quota-natal-complete-transactionnel-et-remedier-lectures-invalides` | quota path -> no debit logic edit -> VC5. |
| RG-171 `CS-424` | Basic prompt -> old natal prompt keys are inventoried -> VC1, VC3. |
| RG-172 `CS-425` | Basic cache -> editorial-version cache surface is classified -> VC4. |

Needs-investigation and registry gaps:

- None from the brief-listed IDs. Resolver output also returned adjacent global IDs, but CSS, entitlement docs, and generic frontend docs guardrails are not local.

Non-applicable examples:

- `RG-047` is CSS-inline local validation and is not touched by this audit.
- `RG-052` is CSS namespace migration-only and is not touched by this audit.
- `RG-041` is entitlement documentation governance and is not the local inventory contract.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Legacy generation map | `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/legacy-generation-map.md` | Inventory. |
| Surface classification | `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/legacy-surface-classification.md` | Classification. |
| Initial scans | `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/initial-scans.txt` | Preserve baseline scan output for later stories. |
| Source alignment | `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/source-alignment.md` | Record source coverage and accepted assumptions. |
| Review output | `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Removal Classification Rules

- `canonical-active`: canonical production owner that must remain `keep`.
- `external-active`: public docs, generated links, admin docs, clients, or audit evidence that require `keep` or `needs-decision`.
- `historical-facade`: legacy route, field, prompt key, script, seed, wrapper, alias, or compatibility surface that can be `delete`.
- `dead`: zero-consumer surface that can be `delete`.
- `needs-user-decision`: ambiguous surface that blocks later deletion until the owner decides.

## Removal Audit Format

Implementation must persist the audit artifact at
`_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/legacy-surface-classification.md`.

The persisted audit artifact must use this table shape:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions are `keep`, `delete`, `replace-consumer`, and `needs-user-decision`.

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Public natal reading route | `backend/app/api/v1/routers/public/natal_interpretation.py` | Legacy route or facade rows in evidence. |
| Natal generation service | `backend/app/services/llm_generation/natal/interpretation_service.py` | Legacy service helper rows in evidence. |
| LLM runtime gateway | `backend/app/domain/llm/runtime/gateway.py` | Legacy fallback and recovery rows in evidence. |
| Frontend generation trigger | `frontend/src/features/natal-chart/NatalInterpretation.tsx` | Legacy trigger rows in evidence. |
| Frontend API client | `frontend/src/api/natal-chart/index.ts` | Legacy request field rows in evidence. |
| Prompt and seed bootstrap | `backend/app/ops/llm/bootstrap` and `backend/scripts` | Historical seed and script rows in evidence. |

## Delete-Only Rule

- Forbidden route: deleted, not repointed.
- A surface classified as removable must be deleted in a later implementation story, not repointed.
- Preserving a wrapper, compatibility alias, deprecated path, re-export, or soft-disable behavior is forbidden.
- This inventory story may classify deletion candidates, but it does not physically delete application code.

## External Usage Blocker

- A surface classified as `external-active` must not be deleted by this story.
- The blocker must record exact external evidence, owner, expected decision, and deletion risk.
- A later destructive story must obtain explicit user decision before deleting `external-active` or `needs-user-decision` surfaces.

## Generated Contract Check

- Generated contract check: required.
- Reason: API, frontend, and field-level legacy generation surfaces are in scope for inventory.
- Expected result: no OpenAPI path, route manifest, generated TypeScript client, or public API docs change is produced.
- Validation evidence: VC5 and AC9 prove that generated/API/frontend contract outputs were not modified.

## Allowlist / Exception Register

- Allowlist register: active
- Required columns: File, Symbol / Route / Import, Reason, and Expiry or permanence decision.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `00-story.md` | story contract | Inventory contract. | Permanent. |
| `evidence/legacy-generation-map.md` | map | Inventory output. | Permanent. |
| `evidence/legacy-surface-classification.md` | audit | Classification output. | Permanent. |
| `evidence/initial-scans.txt` | scans | Baseline scan output. | Permanent. |
| `evidence/source-alignment.md` | alignment | Brief coverage. | Permanent. |
| `generated/11-code-review.md` | review | Review output. | Permanent. |
| `_condamad/stories/story-status.md` | CS-426 tracker row | Track readiness and source link. | Permanent tracker record. |
| `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` | guard | Block unclassified reintroduction. | Permanent. |

- Allowed delta:
  - Story markdown, tracker row, inventory evidence, generated review output, and executable architecture guard evidence.
- Forbidden delta:
  - Runtime behavior, provider behavior, DB migrations, seed execution, route changes, frontend behavior, and broad allowlist entries.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/00-story.md` - this story contract.
- `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/legacy-generation-map.md` - inventory output.
- `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/legacy-surface-classification.md` - classification output.
- `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/initial-scans.txt` - scan baseline.
- `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/source-alignment.md` - source coverage output.
- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` - executable guard against unclassified surfaces.
- `_condamad/stories/story-status.md` - tracker row for `CS-426`.

Likely tests:

- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` - guard unclassified legacy generation surfaces.
- The scan suite and artifact token checks in the Validation Plan remain required.

Files not expected to change:

- `backend/app/**` - out of scope; no application runtime surface is edited.
- `backend/scripts/**` - out of scope; scripts are inspected but not edited or executed.
- `frontend/src/**` - out of scope; frontend triggers are inspected but not edited.
- `backend/migrations/**` - out of scope; no migration is created.
- `_condamad/run-state.json` - out of scope; no deletion or worktree change is authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `rg -n "natal_interpretation_short|natal_long_free|natal_interpretation|basic_natal_prompt_payload" backend frontend _story_briefs _condamad`
  - Forbidden pattern: unclassified natal legacy use-case and payload surfaces.
  - Allowed fixture pattern: occurrences recorded in `legacy-generation-map.md`, source briefs, reports, tests, and evidence artifacts.
  - Scan roots: `backend`, `frontend`, `_story_briefs`, `_condamad`.
  - Expected false positives: this story, its evidence artifacts, source briefs, and reports.
- VC2: `rg -n "use_case_level|variant_code|forceRefresh|shouldRefreshShortAfterBasicUpgrade" frontend/src backend/app`
  - Forbidden pattern: unclassified frontend or backend trigger signals for natal generation.
  - Allowed fixture pattern: occurrences recorded in `legacy-generation-map.md`.
  - Scan roots: `frontend/src`, `backend/app`.
  - Expected false positives: tests or type definitions after classification.
- VC3: `rg -n "PROMPT_FALLBACK_CONFIGS|fallback_default|AstroResponse_v3|EXIGENCE PREMIUM" backend/app backend/scripts`
  - Forbidden pattern: unclassified prompt fallback, old schema, or premium prompt carrier surface.
  - Allowed fixture pattern: rows classified as `delete`, `replace`, `readonly`, `keep`, or `needs-decision`.
  - Scan roots: `backend/app`, `backend/scripts`.
  - Expected false positives: historical scripts and bootstrap files after classification.
- VC4: `rg -n "UserNatalInterpretationModel|chart_id|variant_code|answer_type|was_fallback" backend/app/services/llm_generation/natal backend/app/infra/db/models`
  - Forbidden pattern: unclassified persistence or cache path that can affect natal generation reuse.
  - Allowed fixture pattern: rows classified with ownership and trigger.
  - Scan roots: `backend/app/services/llm_generation/natal`, `backend/app/infra/db/models`.
  - Expected false positives: model definitions and service readback logic after classification.
- VC5: `git status --short -- _condamad _story_briefs backend frontend`
  - Forbidden pattern: functional code changes outside authorized story and evidence artifacts.
  - Allowed fixture pattern: `00-story.md`, evidence artifacts, generated review path, and tracker row.
  - Scan roots: `_condamad`, `_story_briefs`, `backend`, `frontend`.
- Expected false positives: pre-existing unrelated worktree changes documented by the implementer.
- VC6: `git status --short -- _condamad/run-state.json`
  - Forbidden pattern: any worktree change to `_condamad/run-state.json`.
  - Allowed fixture pattern: no output.
  - Scan roots: `_condamad/run-state.json`.
  - Expected false positives: none.
- VC7: `python` verifies legacy generation map tokens.

  ```powershell
  Push-Location _condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence
  python -c "assert 'natal_interpretation' in open('legacy-generation-map.md', encoding='utf-8').read()"
  Pop-Location
  ```

- VC8: `python` verifies classification vocabulary.

  ```powershell
  Push-Location _condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence
  python -c "t=open('legacy-surface-classification.md', encoding='utf-8').read(); assert all(x in t for x in 'delete replace readonly keep needs-decision'.split())"
  Pop-Location
  ```

- VC9: `python` verifies persisted scan output.

  ```powershell
  Push-Location _condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence
  python -c "assert 'rg -n' in open('initial-scans.txt', encoding='utf-8').read()"
  Pop-Location
  ```

- VC10: `python` verifies decision ownership tokens.

  ```powershell
  Push-Location _condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence
  python -c "t=open('legacy-surface-classification.md', encoding='utf-8').read(); assert 'owner' in t and 'expected decision' in t"
  Pop-Location
  ```
- VC11: `python` verifies no functional runtime delta.

  ```powershell
  @'
  import subprocess
  paths = ["backend/app", "backend/scripts", "frontend/src", "backend/migrations"]
  result = subprocess.run(["git", "diff", "--name-only", "--", *paths], capture_output=True, text=True)
  assert not result.stdout.strip(), result.stdout
  '@ | python -
  ```

  - Forbidden pattern: any functional application, script, frontend runtime, or migration file change.
  - Allowed fixture pattern: no output.
  - Scan roots: `backend/app`, `backend/scripts`, `frontend/src`, `backend/migrations`.
  - Expected false positives: none.

## Regression Risks

- Inventory drift: a later story may treat a mapped path as closed without evidence. Mitigation: persistent scan artifacts and classification rows.
- Over-broad scope: implementation may edit runtime code during inventory. Mitigation: AC9, VC5, and explicit non-goals.
- Hidden generation path: a surface may be missed by filename-only reasoning. Mitigation: required targeted scans over use cases, prompts, frontend triggers, and persistence.
- Misclassified readonly path: a readback path may still trigger generation through cache miss or refresh. Mitigation: AC5 requires explicit non-generative rationale.
- Product ambiguity: `needs-decision` entries may lack owner. Mitigation: AC6 and VC10 block ownerless decisions.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the Python venv before every Python command in this repository.
- Do not run seeds, providers, migrations, app servers, or frontend build commands for this audit story.
- Preserve the source brief's scan commands textually in `evidence/initial-scans.txt`.
- Keep `_condamad/run-state.json` unchanged and document it as out of scope.

## References

- `_story_briefs/cs-426-freeze-inventory-legacy-generation-natal-bigbang.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `_story_briefs/cs-425-invalider-regenerer-lectures-basic-natal-degradees.md`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/api/natal-chart/index.ts`
- `backend/app/ops/llm/bootstrap`
- `backend/scripts`
