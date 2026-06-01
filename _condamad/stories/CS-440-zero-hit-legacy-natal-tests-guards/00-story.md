# Story CS-440 zero-hit-legacy-natal-tests-guards: Verrouiller Zero Hit Legacy Natal Et Nettoyer Les Tests
Status: ready-to-review

## Trigger / Source

- Source brief: `_story_briefs/cs-440-zero-hit-legacy-natal-tests-guards.md`.
- Operating mode: Repo-informed story.
- Fast Story Writer Mode: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` read first.
- Removal contract: `.agents/skills/condamad-story-writer/references/removal-story-contract.md` read because this story removes legacy test fixtures.
- Problem statement: temporary CS-434 and CS-435 allowlists still permit legacy natal vocabulary as nominal test language.
- Closure expectation: close the legacy natal deletion series with zero-hit guards or minimal proof-only allowlists.
- Source-alignment evidence: every source primitive maps to ACs, tasks, validation commands, non-goals, or blocker rules.

## Objective

Turn the CS-434 and CS-435 legacy natal allowlists into zero-hit guards or minimal proof-only records.
Remove nominal tests and fixtures that keep old natal generation symbols active as expected behavior.

## Target State

- Runtime code under `backend/app` and `frontend/src` has zero unauthorized hits for old natal generation symbols.
- CS-434 and CS-435 allowlists authorize only `_condamad` proof artifacts or explicitly named extinction tests.
- Nominal tests no longer build positive prompt, route, adapter, or command behavior around old natal generation symbols.
- Extinction tests use names such as `test_legacy_natal_*_is_absent`, `test_old_public_route_is_removed_or_gone`, or `test_theme_natal_contract_is_only_public_generation_path`.
- The architecture guard fails on any new old-symbol hit outside the authorized proof and extinction-test scopes.
- Remaining `variant_code` hits are classified as entitlement, prediction, daily horoscope, astrology calculation, or historical data.
- Public `theme_natal` generation remains the only public generation path for natal readings.
- A final zero-hit report is persisted under `_condamad/reports`.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-440-zero-hit-legacy-natal-tests-guards.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-440`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted IDs from the brief were resolved by ID lookup.
- Evidence 4: `resolve_guardrails.py` - resolver run with remove, backend-tests, frontend-tests, no-legacy, and architecture-guard scope.
- Evidence 5: CS-434 `legacy-allowlist.md` still classifies old symbols in backend tests and historical surfaces.
- Evidence 6: CS-435 `legacy-scan-results.md` records `PASS_WITH_CLASSIFIED_HITS`, not zero-hit closure.
- Evidence 7: CS-426 `legacy-generation-map.md` maps old public generation, readonly, script, test, and frontend trigger surfaces.
- Evidence 8: delivery report confirms `theme_natal` product contracts and `RG-173` are the modern public generation baseline.
- Evidence 9: `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` still carries old-symbol denylist data.
- Evidence 10: `backend/tests/architecture/test_llm_legacy_extinction.py` already asserts absent old generator keys.
- Evidence 11: `frontend/src/tests/natalPublicDomGuard.test.tsx` still contains positive `natal_long_free` fixture payloads.
- Repository structure alert: expected `backend`, `backend/tests`, `frontend`, and `frontend/src` roots exist in this workspace.

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| CS-434 `legacy-allowlist.md` | in scope | AC1, Task 1, Validation Plan |
| CS-435 `legacy-scan-results.md` | in scope | AC1, AC10, Task 1 |
| CS-426 inventory | in scope | AC6, Task 2, Removal Audit |
| `natal_interpretation_short` | in scope | AC2, AC5, AC8, Task 3 |
| `natal_long_free` | in scope | AC3, AC5, AC8, Task 3 |
| `natal_interpretation` for Basic or Free | in scope | AC4, AC11, Task 4 |
| `use_case_level` public contract | in scope | AC5, AC11, Task 4 |
| `variant_code` command use | in scope | AC6, Task 5, Removal Audit |
| positive legacy tests and fixtures | in scope | AC2, AC3, AC4, AC7 |
| extinction test names | in scope | AC7, Task 6 |
| architecture guard | in scope | AC8, Task 7 |
| final zero-hit report | in scope | AC10, Task 9 |
| `basic_natal_prompt_payload` modern theme astral owner | constrained keep | Non-goals and AC6 |
| `_condamad/run-state.json` | out of scope | Explicit non-goals |
| functional deletions from CS-436 to CS-439 | out of scope | Explicit non-goals |

## Domain Boundary

- Domain: legacy-natal-test-guards
- In scope:
  - Backend architecture and LLM orchestration tests guarding old natal generation symbols.
  - Frontend natal DOM guard tests that still carry old public fixture payloads.
  - CS-434, CS-435, and CS-426 evidence artifacts used to close temporary allowlists.
  - Bounded scans over `backend/app`, `backend/tests`, `frontend/src`, and `frontend/src/tests`.
  - A final `_condamad/reports` zero-hit report for the legacy natal closure.
- Out of scope:
  - New runtime feature work, database schema, auth, i18n copy, visual styling, build tooling, migrations, and `_condamad/run-state.json`.
- Explicit non-goals:
  - No implementation of functional deletion work owned by CS-436, CS-437, CS-438, or CS-439.
  - No deletion of historical `_condamad/reports` or already delivered briefs.
  - No removal of `basic_natal_prompt_payload` from its modern `theme_astral` owner.
  - No new public route, UI screen, database migration, or generated client.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: the story removes nominal legacy fixtures and replaces broad allowlists with deterministic extinction guards.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Change only test, guard, evidence, report, and guardrail documentation surfaces required for legacy natal closure.
  - Preserve modern `theme_natal` public generation and `theme_astral` payload ownership.
  - The only allowed surface delta is zero-hit legacy natal evidence plus minimal proof-only allowlists.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: a runtime old-symbol hit remains necessary after CS-436 through CS-439 are complete.
- Additional validation rules:
  - Use `pytest` architecture and LLM orchestration tests for backend guard behavior.
  - Use `pnpm` frontend tests for DOM guard behavior and public reading anti-return coverage.
  - Use `app.routes`, `app.openapi()`, `pytest`, and `TestClient` evidence for old public route absence or gone behavior.
  - Use bounded `rg` scans for forbidden old symbols with explicit allowed proof and extinction-test patterns.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, `TestClient`, `app.routes`, `app.openapi()`, and frontend tests prove old public behavior stays absent. |
| Baseline Snapshot | yes | Before and after scan artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Extinction tests, reports, and proof-only allowlists need canonical owners. |
| Allowlist Exception | yes | CS-434 and CS-435 allowlists must be closed or reduced to proof-only scopes. |
| Contract Shape | yes | Forbidden old symbols, allowed proof scopes, and public route absence have exact shapes. |
| Batch Migration | no | No batch data migration or generated conversion is in scope. |
| Reintroduction Guard | yes | Old natal generation symbols must fail deterministic guards when reintroduced. |
| Persistent Evidence | yes | Zero-hit scans, audits, validations, and final report must be kept for handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Allowlists reject runtime old-symbol hits. | Evidence profile: no_legacy_contract; `pytest`; `app.routes`; `app.openapi()`. |
| AC2 | No nominal backend test uses `natal_interpretation_short`. | Evidence profile: targeted_forbidden_symbol_scan; `pytest`; `rg`. |
| AC3 | No nominal backend test uses `natal_long_free`. | Evidence profile: targeted_forbidden_symbol_scan; `pytest`; `backend/tests/architecture/test_llm_legacy_extinction.py`. |
| AC4 | No nominal test mocks old generation success. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks old generation mocks. |
| AC5 | Public app scans are zero-hit for old natal control symbols. | Evidence profile: repo_wide_negative_scan; `rg` scans `backend/app` and `frontend/src`. |
| AC6 | `variant_code` never constructs a theme natal generation command. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans bounded app, src, and tests roots. |
| AC7 | Extinction tests use explicit anti-return names. | Evidence profile: ast_architecture_guard; `rg` checks extinction test names. |
| AC8 | The architecture guard fails on new unauthorized hits. | Evidence profile: reintroduction_guard; `pytest`; `rg`. |
| AC9 | The durable zero-hit invariant is tracked. | Evidence profile: reintroduction_guard; `rg` scans guardrail registry and this story. |
| AC10 | The final zero-hit report is persisted. | Evidence profile: baseline_before_after_diff; `python` checks `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md`. |
| AC11 | The old public route is removed or gone. | Evidence profile: route_absence_runtime; `python` checks `app.routes`; `pytest` uses `TestClient`. |

## Implementation Tasks

- [ ] Task 1: Reclassify CS-434 and CS-435 allowlists into zero-hit or proof-only entries. (AC: AC1, AC10)
- [ ] Task 2: Use the CS-426 inventory to classify every remaining old-symbol test or fixture hit. (AC: AC1, AC6)
- [ ] Task 3: Remove nominal backend tests for old prompt keys and keep only extinction assertions. (AC: AC2, AC3, AC7)
- [ ] Task 4: Remove success-path mocks around old natal interpretation generation and old public route controls. (AC: AC4, AC11)
- [ ] Task 5: Classify every remaining `variant_code` hit outside theme natal command construction. (AC: AC6)
- [ ] Task 6: Rename or rewrite retained tests to explicit anti-return names. (AC: AC7)
- [ ] Task 7: Update the architecture guard to fail on any unauthorized old-symbol hit. (AC: AC8)
- [ ] Task 8: Add or document the durable zero-hit guardrail invariant after closure is proven. (AC: AC9)
- [ ] Task 9: Persist before scans, after scans, validation output, removal audit, and final report. (AC: AC9, AC10)
- [ ] Task 10: Run backend, frontend, and scan validations from the validation plan. (AC: AC1, AC5, AC8, AC11)

## Files to Inspect First

- `_story_briefs/cs-440-zero-hit-legacy-natal-tests-guards.md` - source brief.
- `_condamad/stories/regression-guardrails.md` - targeted guardrail IDs and final invariant registry.
- `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/legacy-allowlist.md` - allowlist closure source.
- `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/legacy-scan-results.md` - classified-hit source.
- `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/legacy-generation-map.md` - old-surface inventory.
- `_condamad/reports/cs-426-cs-427-cs-428-cs-429-cs-430-cs-431-cs-432-cs-433-cs-434-cs-435-delivery-report.md` - closure baseline.
- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` - architecture guard owner.
- `backend/tests/architecture/test_llm_legacy_extinction.py` - LLM old-key extinction owner.
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py` - prompt governance guard owner.
- `frontend/src/tests/natalPublicDomGuard.test.tsx` - frontend DOM guard owner.

## Removal Classification Rules

- `canonical-active`: modern `theme_natal` generation contracts, public product actions, and `theme_astral` payload builder ownership.
- `external-active`: any public or generated consumer requiring old natal keys after the bounded scans.
- `historical-facade`: old symbols retained only by positive tests, fixture names, broad allowlists, or old public route controls.
- `dead`: old symbols with zero references outside historical `_condamad` proof artifacts and extinction tests.
- `needs-user-decision`: a runtime old-symbol hit required by production behavior after all required scans and CS-436 to CS-439 status checks.

## Removal Audit Format

The implementation must write `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/legacy-natal-zero-hit-audit.md`.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `natal_interpretation_short` | symbol | historical-facade | tests or proof artifacts | `theme_natal` public contract | delete | `rg` output | Old short prompt returns |
| `natal_long_free` | symbol | historical-facade | tests or proof artifacts | `theme_natal` public contract | delete | `rg` output | Old free prompt returns |
| `natal_interpretation` Basic or Free | symbol | historical-facade | nominal tests | product action contract | delete | `rg` output | Old complete prompt path returns |
| `use_case_level` public contract | field | historical-facade | old public tests | product action `action` | delete | OpenAPI and `rg` output | Old public contract returns |
| `variant_code` command use | field | historical-facade | old command tests | product action `action` | delete | `rg` output | Command selection drifts |
| `variant_code` entitlement or non-natal use | field | canonical-active | entitlement or non-natal owners | existing owner | keep | `rg` output | None |
| `basic_natal_prompt_payload` | symbol | canonical-active | modern theme astral owner | theme astral payload builder | keep | `rg` output | None |
| old positive fixture consumer | fixture | historical-facade | nominal tests | extinction test name | replace-consumer | `rg` output | Nominal fixture remains |
| unresolved external old consumer | symbol | needs-user-decision | external consumer | product action contract | needs-user-decision | audit output | Public breakage |

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Legacy natal extinction guard | `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` | nominal old-symbol tests |
| LLM old-key extinction | `backend/tests/architecture/test_llm_legacy_extinction.py` | success-path old prompt fixtures |
| Prompt governance classification | `backend/tests/llm_orchestration/test_prompt_governance_registry.py` | broad unclassified prompt allowlists |
| Frontend public DOM anti-return | `frontend/src/tests/natalPublicDomGuard.test.tsx` | positive old payload fixtures |
| Closure evidence | `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md` | scattered untracked scan notes |
| Durable invariant registry | `_condamad/stories/regression-guardrails.md` | story-local guardrail text only |

## Delete-Only Rule

- Items classified as `historical-facade` or `dead` must be deleted from nominal tests, fixtures, and runtime paths.
- Removable items must be deleted, not repointed.
- Do not repoint old prompt keys to the modern `theme_natal` product contract.
- Do not preserve wrapper fixtures that make old keys look like expected behavior.
- Do not add a compatibility alias for old public request fields.
- Do not keep a fallback branch keyed by `use_case_level`, `forceRefresh`, or `variant_code`.
- Do not preserve old public generation through re-export, helper naming, or fixture vocabulary.
- Do not replace deletion with a soft-disabled hidden path.

## External Usage Blocker

- External usage blocker: active.
- Required action: scan first-party runtime, tests, reports, guardrails, OpenAPI, and frontend public tests before deleting each item.
- Any item classified as `external-active` must not be deleted.
- Blocker rule: any `external-active` item must be recorded in the removal audit with consumer, deletion risk, and user-decision text.
- The story requires an explicit user decision before deleting any `external-active` item.
- Allowed closure: no runtime old-symbol hit may remain without a `needs-user-decision` audit row.

## Generated Contract Check

- Generated contract check: active
- Required proof:
  - `app.openapi()` must not expose an old public generation contract for Basic or Free natal generation.
  - `app.routes` must not register an old public generation route as an active success path.
  - `TestClient` coverage must prove the old public route is removed or returns gone behavior.
  - Frontend public API tests must prove `variant_code`, `use_case_level`, and `forceRefresh` are not command fields.
- Reason: public backend and frontend contracts are part of the legacy natal deletion boundary.

## Runtime Source of Truth

- Primary source of truth:
  - `pytest`, `TestClient`, `app.routes`, `app.openapi()`, and frontend `pnpm` tests.
- Secondary evidence:
  - Targeted `rg` scans over `backend/app`, `backend/tests`, `frontend/src`, `frontend/src/tests`, and `_condamad` proof artifacts.
- Static scans alone are not sufficient for this story because:
  - The old public route state, OpenAPI shape, frontend command shape, and architecture guard behavior must be proven at runtime.

## Contract Shape

- Contract type:
  - Legacy natal zero-hit scan, public route absence, and proof-only allowlist contract.
- Fields:
  - `natal_interpretation_short`: forbidden outside proof-only and extinction-test scopes.
  - `natal_long_free`: forbidden outside proof-only and extinction-test scopes.
  - `natal_interpretation`: forbidden as Basic or Free public generation key.
  - `use_case_level`: forbidden in public theme natal contracts.
  - `variant_code`: forbidden as theme natal generation command selector.
  - `forceRefresh`: forbidden in public theme natal command flow.
  - `shouldRefreshShortAfterBasicUpgrade`: forbidden in public frontend flow.
- Required fields:
  - none for old public generation commands.
- Optional fields:
  - none for old public generation commands.
- Status codes:
  - Old public route behavior must be removed or gone, proven by `TestClient`.
- Serialization names:
  - Old command keys must not be emitted as `use_case_level`, `variant_code`, `force_refresh`, or `forceRefresh`.
- Frontend type impact:
  - Public `/natal` command tests must not expose old technical generation controls.
- Generated contract impact:
  - `app.openapi()` must show no active old public generation request contract for Basic or Free natal generation.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/legacy-symbols-before.txt`
  - `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/variant-code-before.txt`
  - `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/openapi-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/legacy-symbols-after.txt`
  - `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/variant-code-after.txt`
  - `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/openapi-after.json`
- Expected invariant:
  - The only intended surface delta is closure of old natal test fixtures, broad allowlists, and unauthorized runtime hits.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Backend extinction guard | `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` | nominal old-key test files |
| LLM adapter old-key guard | `backend/tests/architecture/test_llm_legacy_extinction.py` | positive mock tests |
| Frontend DOM guard | `frontend/src/tests/natalPublicDomGuard.test.tsx` | production component code |
| Public route absence proof | `backend/tests/integration/test_theme_natal_public_api_product_actions.py` | old public route tests |
| Closure report | `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md` | scattered evidence notes |
| Durable zero-hit invariant | `_condamad/stories/regression-guardrails.md` | generated review output |

## Mandatory Reuse / DRY Constraints

- Reuse existing architecture guard tests instead of creating a second guard with overlapping patterns.
- Reuse existing `theme_natal` public contract tests for route and OpenAPI proof.
- Keep one canonical forbidden-symbol list for the legacy natal guard.
- Keep one final zero-hit report rather than separate untracked scan summaries.
- Do not duplicate frontend denylist patterns across multiple test files without shared ownership.

## No Legacy / Forbidden Paths

- No legacy prompt key may remain as nominal expected behavior.
- No compatibility route, schema, fixture, or helper may accept old Basic or Free natal generation commands.
- No fallback branch may select public natal generation from `use_case_level`, `forceRefresh`, or `variant_code`.
- Forbidden prompt symbols: `natal_interpretation_short` and `natal_long_free`.
- Forbidden public contract symbols: `use_case_level`, `forceRefresh`, `force_refresh`, and `shouldRefreshShortAfterBasicUpgrade`.
- Forbidden success mock: `AIEngineAdapter.generate_natal_interpretation` used as positive Basic or Free runtime behavior.
- Forbidden command use: `variant_code` constructing a `theme_natal` generation command.
- Allowed proof scopes: `_condamad` historical artifacts and tests with explicit extinction names.

## Reintroduction Guard

- Guard target: old natal generation symbols in runtime code, nominal tests, and public frontend command surfaces.
- The implementation must add or update an architecture guard against reintroduction.
- The implementation must add or update an architecture guard that fails when unauthorized old-symbol hits return.
- The implementation must add or update an architecture guard that fails if the removed surface is reintroduced.
- Deterministic source: `pytest`, `app.routes`, `app.openapi()`, `TestClient`, and bounded `rg` scans.
- The guard must check at least one deterministic source:
  - registered router prefixes;
  - generated OpenAPI paths;
  - forbidden symbols or states.
- Guard command 1:
  - `python -B -m pytest -q tests/architecture/test_legacy_natal_generation_inventory_guard.py tests/architecture/test_llm_legacy_extinction.py --tb=short`
- Guard command 2:
  - `rg -n "natal_interpretation_short|natal_long_free|shouldRefreshShortAfterBasicUpgrade|forceRefresh" backend/app frontend/src backend/tests frontend/src/tests`
- Guard command 3:
  ```powershell
  rg -n "use_case_level" `
    backend/app/services/api_contracts/public `
    backend/app/api/v1/routers/public `
    frontend/src/api/natal-chart `
    frontend/src/features/natal-chart `
    frontend/src/pages/NatalChartPage.tsx
  ```
- Guard command 4:
  ```powershell
  rg -n "AIEngineAdapter\\.generate_natal_interpretation|fake_generate_natal_interpretation" backend/app backend/tests
  rg -n "patch\\.object\\(AIEngineAdapter, \"generate_natal_interpretation\"" backend/app backend/tests
  ```
- Expected result:
  - Guard command 1 passes.
  - Guard command 2 allows only `_condamad` proof outputs or explicit extinction-test declarations after classification.
  - Guard command 3 has zero public theme natal contract hits.
  - Guard command 4 has zero positive Basic or Free runtime generation mocks.

## Regression Guardrails

| Guardrail | scope -> invariant -> evidence |
|---|---|
| RG-001 `remove-historical-facade-routes` | old facades -> no wrapper, alias, fallback, or re-export -> `rg`, `app.routes`, `app.openapi()`. |
| RG-010 `converge-backend-test-topology` | backend tests -> collected topology stays canonical -> targeted `pytest`. |
| RG-012 `reclassify-story-regression-guards` | backend story guards -> no new unmapped `test_story_*.py` -> changed-file audit. |
| RG-014 `replace-seed-validation-facade-test` | backend tests -> no noop extinction proof -> targeted `pytest` and `rg`. |
| RG-018 `block-supported-family-prompt-fallbacks` | natal prompts -> supported families avoid prompt fallback ownership -> LLM `pytest`. |
| RG-021 `classify-converge-remaining-prompt-fallbacks` | fallback remnants -> every remaining key has a decision -> governance `pytest`. |
| RG-149 `CS-350-prompt-generation-current-implementation` | prompt cartography -> modern natal classification stays exact -> scan evidence. |
| RG-153 `CS-393-refondre-page-natal-autour-lecture-narrative` | `/natal` DOM -> modern narrative layout stays primary -> pnpm tests. |
| RG-154 `CS-395-verrouiller-non-regression-lecture-natale-publique` | public DOM -> old technical symbols stay hidden -> `pnpm` DOM guard. |
| RG-170 `CS-422` | Basic V2 DOM -> sources and legal mentions stay deduplicated -> pnpm tests or build evidence. |
| RG-173 `CS-435` | public generation -> product and LLM contracts own theme natal -> `pytest`, OpenAPI, routes, `rg`. |

- Applicability note: `RG-012` is satisfied by reusing existing backend guard files and avoiding new unmapped `test_story_*.py`.
- Applicability note: `RG-153` and `RG-170` stay applicable while frontend natal DOM fixtures are edited or validated.
- Registry gap: no dedicated invariant currently states `Legacy natal deleted: zero public/runtime hit`; AC9 requires closure or gap evidence.
- Non-applicable examples: database schema, auth, migrations.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Removal audit | `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/legacy-natal-zero-hit-audit.md` | Classify removed symbols and blockers. |
| Before scan | `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/legacy-symbols-before.txt` | Capture old symbol hits before work. |
| After scan | `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/legacy-symbols-after.txt` | Prove old symbol hits after work. |
| Variant scan | `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/variant-code-after.txt` | Prove command-use absence. |
| OpenAPI snapshot | `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/openapi-after.json` | Prove old public contract absence. |
| Validation output | `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/validation.txt` | Keep lint, tests, and scans. |
| Final report | `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md` | Document closure, scans, and residual risks. |
| Review output | `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: active.
- CS-434 `legacy-allowlist.md` must stop authorizing runtime legacy hits under `backend/app` or `frontend/src`.
- CS-435 `legacy-scan-results.md` must move from classified runtime hits to zero-hit or proof-only classification.
- Allowed remaining entries:
  - historical `_condamad` evidence artifacts;
  - explicit extinction tests with anti-return names;
  - modern `basic_natal_prompt_payload` ownership under `theme_astral`.
- Forbidden remaining entries:
  - runtime app code using old symbols as public generation input;
  - positive fixtures that make old symbols expected behavior;
  - broad folder allowlists over backend test trees or frontend test trees.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `CS-434 legacy-allowlist.md` | old natal symbols | Historical proof source. | Permanent historical evidence. |
| `CS-435 legacy-scan-results.md` | old natal symbols | Historical scan source. | Permanent historical evidence. |
| `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` | old natal symbols | Extinction guard declarations only. | Permanent anti-return test. |
| `backend/tests/architecture/test_llm_legacy_extinction.py` | old natal symbols | Extinction guard declarations only. | Permanent anti-return test. |
| `frontend/src/tests/natalPublicDomGuard.test.tsx` | old natal symbols | DOM denylist declarations only. | Permanent anti-return tests. |
| `backend/app/api/v1/routers/public/theme_natal_readings.py` | old natal generation symbols | Runtime old-symbol usage is not authorized. | Must be zero-hit or blocked. |

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step data conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` - tighten forbidden-symbol inventory and allowed scopes.
- `backend/tests/architecture/test_llm_legacy_extinction.py` - keep old generator keys absent without positive prompt fixtures.
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py` - align prompt governance with zero-hit closure.
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py` - keep orchestration old-key rejection proof.
- `frontend/src/tests/natalPublicDomGuard.test.tsx` - remove positive old payload fixtures and keep DOM denylist guard.
- `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/legacy-allowlist.md` - reduce allowlist scope.
- `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/legacy-scan-results.md` - update scan classification.
- `_condamad/stories/regression-guardrails.md` - add durable zero-hit invariant after closure is proven.
- `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md` - persist final scan report.
- `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/*.txt` - persist implementation evidence.

Likely tests:

- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` - zero-hit architecture guard.
- `backend/tests/architecture/test_llm_legacy_extinction.py` - old LLM generation key extinction.
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py` - prompt governance classification.
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py` - orchestration old-key rejection.
- `frontend/src/tests/natalPublicDomGuard.test.tsx` - frontend DOM anti-return guard.
- `frontend/src/tests/natalChartApi.test.tsx` - public command contract.
- `frontend/src/tests/natalInterpretation.test.tsx` - public rendering contract.
- `frontend/src/tests/NatalChartPage.test.tsx` - page-level public behavior.

Files not expected to change:

- `backend/app/infra/**` - out of scope; no persistence or external adapter change is owned.
- `backend/migrations/**` - out of scope; no schema migration is owned.
- `frontend/src/styles/**` - out of scope unless a touched test reveals inline style drift in implementation.
- `_condamad/run-state.json` - explicitly out of scope.
- Historical `_condamad/reports` and delivered briefs - must not be deleted.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VP0: activate the Python virtual environment before backend commands: `.\.venv\Scripts\Activate.ps1`.
- VC1 backend format:
  ```powershell
  Push-Location backend
  ruff format .
  Pop-Location
  ```
- VC2 backend lint:
  ```powershell
  Push-Location backend
  ruff check .
  Pop-Location
  ```
- VC3 backend architecture and LLM guard tests:
  ```powershell
  Push-Location backend
  python -B -m pytest -q `
    tests/architecture/test_legacy_natal_generation_inventory_guard.py `
    tests/architecture/test_llm_legacy_extinction.py `
    tests/llm_orchestration/test_prompt_governance_registry.py `
    tests/llm_orchestration/test_llm_legacy_extinction.py `
    --tb=short
  Pop-Location
  ```
- VC4 backend theme natal public runtime tests:
  ```powershell
  Push-Location backend
  python -B -m pytest -q `
    tests/unit/domain/theme_natal `
    tests/integration/test_theme_natal_public_api_product_actions.py `
    tests/integration/test_theme_natal_basic_full_reading_runtime.py `
    tests/integration/test_theme_natal_public_reads.py `
    --tb=short
  Pop-Location
  ```
- VC5 frontend tests:
  ```powershell
  pnpm --dir frontend test -- natalChartApi.test.tsx natalPublicDomGuard.test.tsx natalInterpretation.test.tsx NatalChartPage.test.tsx
  ```
- VC6 frontend lint:
  ```powershell
  pnpm --dir frontend lint
  ```
- VC7 forbidden pattern: `natal_interpretation_short|natal_long_free|shouldRefreshShortAfterBasicUpgrade|forceRefresh`.
- VC7 allowed fixture pattern: `_condamad` proof artifacts and explicit extinction-test declarations only.
- VC7 roots: `backend/app`, `frontend/src`, `backend/tests`, and `frontend/src/tests`.
- VC7 expected false positives: denylist constants or test names proving absence.
- VC7 command:
  ```powershell
  rg -n "natal_interpretation_short|natal_long_free|shouldRefreshShortAfterBasicUpgrade|forceRefresh" backend/app frontend/src backend/tests frontend/src/tests
  ```
- VC8 forbidden pattern: `use_case_level`.
- VC8 allowed fixture pattern: gone-route or rejection tests only.
- VC8 roots: public backend contracts, public routers, frontend natal API, frontend natal features, and `NatalChartPage.tsx`.
- VC8 expected false positives: rejection test data only, outside runtime public contract emission.
- VC8 command:
  ```powershell
  rg -n "use_case_level" `
    backend/app/services/api_contracts/public `
    backend/app/api/v1/routers/public `
    frontend/src/api/natal-chart `
    frontend/src/features/natal-chart `
    frontend/src/pages/NatalChartPage.tsx
  ```
- VC9 forbidden pattern: `AIEngineAdapter\.generate_natal_interpretation|fake_generate_natal_interpretation|patch\.object\(AIEngineAdapter, "generate_natal_interpretation"`.
- VC9 allowed fixture pattern: extinction guard source inspection only.
- VC9 roots: `backend/app` and `backend/tests`.
- VC9 expected false positives: architecture tests that assert absence from the adapter method body.
- VC9 command:
  ```powershell
  rg -n "AIEngineAdapter\.generate_natal_interpretation|fake_generate_natal_interpretation" backend/app backend/tests
  rg -n "patch\.object\(AIEngineAdapter, \"generate_natal_interpretation\"" backend/app backend/tests
  ```
- VC10 forbidden pattern: `variant_code|variantCode`.
- VC10 allowed fixture pattern: entitlement, prediction, daily horoscope, astrology calculation, or historical data classification.
- VC10 roots: `backend/app`, `backend/tests`, `frontend/src`, and `_condamad/reports`.
- VC10 expected false positives: classified non-generative owners and final report rows.
- VC10 command:
  ```powershell
  rg -n "variant_code|variantCode" backend/app backend/tests frontend/src _condamad/reports
  ```
- VC11 runtime route and OpenAPI absence check:
  ```powershell
  Push-Location backend
  python -B -c "from app.main import app; paths={getattr(r,'path','') for r in app.routes}; assert '/v1/natal/interpretation' not in paths"
  python -B -c "from app.main import app; assert '/v1/natal/interpretation' not in app.openapi().get('paths', {})"
  Pop-Location
  ```
- VC12 persisted evidence check:
  ```powershell
  python -B -c "from pathlib import Path; assert Path('_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md').exists()"
  python -B -c "from pathlib import Path; assert Path('_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/validation.txt').exists()"
  ```
- VC13 durable invariant check:
  ```powershell
  rg -n "Legacy natal deleted: zero public/runtime hit|zero public/runtime hit" `
    _condamad/stories/regression-guardrails.md `
    _condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/00-story.md
  ```

## Regression Risks

- Broad old allowlists can hide a newly introduced runtime hit; the architecture guard must use zero-hit default behavior.
- Removing positive fixtures can reduce test coverage if extinction tests are not renamed and kept executable.
- `variant_code` has valid non-theme-natal owners; the removal audit must classify each remaining hit rather than deleting unrelated owners.
- `basic_natal_prompt_payload` is modern under `theme_astral`; deleting it would break an explicitly protected owner.
- Old public route behavior must be proven through runtime evidence, not only scans.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python, Ruff, or Pytest command.
- Keep frontend work limited to tests and public command guard evidence.
- Do not edit `_condamad/run-state.json`.
- Do not delete historical `_condamad/reports` or delivered briefs.
- Do not add inline styles.

## References

- `_story_briefs/cs-440-zero-hit-legacy-natal-tests-guards.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/legacy-allowlist.md`
- `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/legacy-scan-results.md`
- `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/legacy-generation-map.md`
- `_condamad/reports/cs-426-cs-427-cs-428-cs-429-cs-430-cs-431-cs-432-cs-433-cs-434-cs-435-delivery-report.md`
- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py`
- `backend/tests/architecture/test_llm_legacy_extinction.py`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `.agents/skills/condamad-story-writer/references/removal-story-contract.md`
