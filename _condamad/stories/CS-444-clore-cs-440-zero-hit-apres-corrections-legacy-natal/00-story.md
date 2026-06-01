# Story CS-444 clore-cs-440-zero-hit-apres-corrections-legacy-natal: Clore CS-440 Zero Hit Apres Corrections Legacy Natal
Status: ready-to-review

## Trigger / Source

- Mode: Repo-informed story.
- Source brief: `_story_briefs/cs-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal.md`.
- Fast Story Writer Mode: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` read first.
- Bounded problem: CS-440 is not `done` while review blockers CR-3 and CR-4 remain tied to CS-441, CS-442, and CS-443.
- Closure expectation: prove CS-441 to CS-443 are clean, rerun strict zero-hit scans, update CS-440 evidence, then mark CS-440 `done`.
- Source-alignment evidence: every brief primitive maps to ACs, tasks, validation commands, non-goals, or blocker rules.

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| CS-441 status and review | in scope | AC1, Task 1, Validation Plan |
| CS-442 status and review | in scope | AC1, Task 1, Validation Plan |
| CS-443 status and review | in scope | AC1, Task 1, Validation Plan |
| CS-440 blocked review CR-3 | in scope | AC1, AC6, Task 2 |
| CS-440 blocked review CR-4 | in scope | AC2, AC5, Task 3 |
| `generate_natal_interpretation` | in scope | AC2, Task 3, Validation Plan |
| `/v1/natal/interpretation(s)` | in scope | AC3, Task 4, Validation Plan |
| old natal prompt and refresh symbols | in scope | AC4, Task 5, Validation Plan |
| CS-434, CS-435, CS-440 allowlists | in scope | AC5, Task 6 |
| `legacy-natal-zero-hit-audit.md` | in scope | AC7, Task 7 |
| CS-440 report | in scope | AC8, Task 8 |
| CS-440 final evidence | in scope | AC9, Task 9 |
| CS-440 code review | in scope | AC6, AC10, Task 10 |
| CS-440 tracker status | in scope | AC11, Task 11 |
| Runtime removals owned by CS-441 to CS-443 | out of scope | Explicit non-goals |
| Historical briefs and reports | out of scope | Explicit non-goals |
| `_condamad/run-state.json` | out of scope | Explicit non-goals |

## Objective

Close CS-440 after CS-441, CS-442, and CS-443 deliver their corrections. Replace temporary classified-hit allowances with strict zero-hit proof,
refresh CS-440 evidence, and update the tracker only after a clean review.

## Target State

- CS-441, CS-442, and CS-443 are `done` with clean implementation review evidence or explicit accepted replacement proof.
- CS-440 review no longer records blockers CR-3 or CR-4.
- `backend/app` has zero hits for `generate_natal_interpretation`.
- Public backend and frontend code have zero hits for `/v1/natal/interpretation` and `/v1/natal/interpretations`.
- Old natal prompt and refresh symbols are absent from runtime public code, with only extinction-test or `_condamad` proof hits.
- CS-434, CS-435, and CS-440 allowlists are reduced to proof-only and extinction-test scopes.
- CS-440 audit, report, final evidence, and code review state full closure without partial-pass wording.
- `_condamad/stories/story-status.md` marks CS-440 `done` only after validations and clean review.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-444`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted IDs from the brief were resolved by ID lookup.
- Evidence 4: `resolve_guardrails.py` - resolver run with legacy-natal, backend, frontend, zero-hit, and review-evidence scope.
- Evidence 5: `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/11-code-review.md` records final verdict `CLEAN`.
- Evidence 6: `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/10-final-evidence.md` records AC2, AC3, and AC4 `PASS`.
- Evidence 7: `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md` still says CS-440 cannot be closed `done`.
- Evidence 8: `_condamad/reports/cs-439-cs-440-delivery-report.md` records CS-440 as partially delivered.
- Evidence 9: `_story_briefs/cs-441-corriger-suppression-runtime-generate-natal-legacy.md` read as closure prerequisite source.
- Evidence 10: `_story_briefs/cs-442-corriger-suppression-sources-reintroduction-prompts-nataux-legacy.md` read as closure prerequisite source.
- Evidence 11: `_story_briefs/cs-443-corriger-suppression-api-publique-natal-interpretations-legacy.md` read as closure prerequisite source.
- Repository structure alert: expected `backend`, `frontend`, `backend/tests`, and `frontend/src` roots exist in this workspace.

## Domain Boundary

- Domain: legacy-natal-closure-evidence
- In scope:
  - Verify CS-441, CS-442, and CS-443 completion status and clean review evidence.
  - Rerun CS-440 zero-hit scans that were previously failed or blocked.
  - Reduce CS-434, CS-435, and CS-440 allowlists to proof-only and extinction-test scopes.
  - Update CS-440 audit, report, final evidence, code review, and tracker row.
  - Run bounded backend, frontend, OpenAPI, route, and static scan validations.
- Out of scope:
  - Functional runtime deletion, prompt catalogue deletion, public API removal, database schema, auth, i18n, styling, build tooling, migrations.
- Explicit non-goals:
  - No implementation of missing CS-441, CS-442, or CS-443 functional corrections.
  - No deletion of historical `_condamad` reports, delivered briefs, or analysis artifacts.
  - No frontend production change outside tests or guards required by CS-440 closure.
  - No modification of `_condamad/run-state.json`.
  - No update to `_condamad/stories/regression-guardrails.md` during normal story execution.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this closure evidence and review unblocking contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Change only CS-440 closure evidence, bounded tests, guards, reports, and tracker state required by this story.
  - Preserve modern `theme_natal` public generation, DOM, and product-action contracts.
  - The only allowed surface delta is CS-440 closure proof after CS-441, CS-442, and CS-443 corrections are complete.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: CS-441, CS-442, or CS-443 cannot reach clean closure before CS-440 is closed.
- Additional validation rules:
  - Use `pytest` architecture, LLM, and theme natal tests for backend closure proof.
  - Use `TestClient`, `app.routes`, and `app.openapi()` for public API absence evidence.
  - Use `pnpm` frontend tests and lint for `/natal` public DOM and client anti-return evidence.
  - Use bounded `rg` scans for forbidden old symbols with explicit allowed proof and extinction-test patterns.
  - Use `python` checks for persisted CS-440 evidence artifacts and tracker state.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, `TestClient`, `app.routes`, and `app.openapi()` prove old public and runtime behavior stays absent. |
| Baseline Snapshot | yes | Before and after scan artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | CS-440 audit, report, evidence, review, and tracker updates need canonical owners. |
| Allowlist Exception | yes | CS-434, CS-435, and CS-440 allowances must be reduced to proof-only scopes. |
| Contract Shape | yes | Closure status, zero-hit scans, and public route absence have exact shapes. |
| Batch Migration | no | No data migration or generated multi-file conversion is in scope. |
| Reintroduction Guard | yes | Old natal runtime, prompt, public API, and frontend symbols must stay absent. |
| Persistent Evidence | yes | Closure scans, validations, reports, and review evidence must be kept for handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | CS-441 to CS-443 are clean prerequisites. | Evidence profile: baseline_before_after_diff; `python` checks tracker and generated reviews. |
| AC2 | Generator is absent. | Evidence profile: targeted_forbidden_symbol_scan; `pytest -q backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py`; `rg`. |
| AC3 | Public code has zero old natal API URLs. | Evidence profile: route_absence_runtime; `python` checks `app.routes`; `app.openapi()`; `rg`. |
| AC4 | Public code has zero old prompt-control hits. | Evidence profile: repo_wide_negative_scan; `rg`; `pytest`; `pnpm --dir frontend test`. |
| AC5 | No positive test mocks old generation success. | Evidence profile: targeted_forbidden_symbol_scan; `rg`; `pytest`. |
| AC6 | CS-440 review verdict is clean. | Evidence profile: baseline_before_after_diff; `python` checks `generated/11-code-review.md`. |
| AC7 | CS-440 zero-hit audit is final. | Evidence profile: baseline_before_after_diff; `python` checks audit artifact; `rg` checks blocked wording. |
| AC8 | CS-440 report claims full closure only. | Evidence profile: baseline_before_after_diff; `python` checks report; `rg` checks partial wording absence. |
| AC9 | CS-440 final evidence marks AC2 to AC4 pass. | Evidence profile: baseline_before_after_diff; `python` checks `generated/10-final-evidence.md`. |
| AC10 | RG-174 remains strict. | Evidence profile: reintroduction_guard; `rg` checks `RG-174`; `pytest` architecture guard. |
| AC11 | CS-440 tracker status changes after proof. | Evidence profile: baseline_before_after_diff; `python` checks `story-status.md`. |

## Implementation Tasks

- [x] Task 1: Verify CS-441, CS-442, and CS-443 are `done` with clean review outputs or accepted replacement proof. (AC: AC1)
- [x] Task 2: Reopen CS-440 review evidence and map CR-3 and CR-4 to completed prerequisite proof. (AC: AC1, AC6)
- [x] Task 3: Rerun backend old-runtime scans and architecture tests after prerequisite corrections. (AC: AC2, AC5, AC10)
- [x] Task 4: Rerun public route inventory, OpenAPI checks, and frontend URL scans for old natal APIs. (AC: AC3)
- [x] Task 5: Rerun old prompt-control scans over backend, frontend, and tests with proof-only allowances. (AC: AC4, AC5)
- [x] Task 6: Reduce CS-434, CS-435, and CS-440 allowlists to historical proof and extinction-test entries. (AC: AC5, AC7)
- [x] Task 7: Update `legacy-natal-zero-hit-audit.md` with final zero-hit classifications and no unresolved blocker. (AC: AC7)
- [x] Task 8: Update the CS-440 report to remove partial closure wording after validations pass. (AC: AC8)
- [x] Task 9: Update CS-440 final evidence so AC2, AC3, and AC4 are `PASS` with command evidence. (AC: AC9)
- [x] Task 10: Update CS-440 code review to `CLEAN` only after the executable evidence is complete. (AC: AC6, AC10)
- [x] Task 11: Mark CS-440 `done` in `story-status.md` only after clean review and validation evidence. (AC: AC11)

## Files to Inspect First

- `_condamad/stories/story-status.md` - prerequisite and CS-440 lifecycle status.
- `_condamad/stories/regression-guardrails.md` - targeted guardrail IDs and RG-174 strictness.
- `_story_briefs/cs-440-zero-hit-legacy-natal-tests-guards.md` - original CS-440 contract.
- `_story_briefs/cs-441-corriger-suppression-runtime-generate-natal-legacy.md` - runtime prerequisite.
- `_story_briefs/cs-442-corriger-suppression-sources-reintroduction-prompts-nataux-legacy.md` - prompt-source prerequisite.
- `_story_briefs/cs-443-corriger-suppression-api-publique-natal-interpretations-legacy.md` - public API prerequisite.
- `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/10-final-evidence.md` - final AC evidence source.
- `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/11-code-review.md` - final clean review source.
- `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/legacy-natal-zero-hit-audit.md` - audit to finalize.
- `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md` - report to finalize.
- `_condamad/reports/cs-439-cs-440-delivery-report.md` - partial-delivery baseline.
- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` - zero-hit guard owner.
- `backend/tests/architecture/test_llm_legacy_extinction.py` - LLM old-key extinction owner.
- `frontend/src/tests/natalPublicDomGuard.test.tsx` - frontend DOM anti-return owner.

## Runtime Source of Truth

- Primary source of truth:
  - `pytest`, `TestClient`, `app.routes`, `app.openapi()`, and frontend `pnpm` tests.
- Secondary evidence:
  - Targeted `rg` scans over `backend/app`, `backend/tests`, `backend/app/tests`, `frontend/src`, and `frontend/src/tests`.
- Static scans alone are not sufficient for this story because:
  - CS-440 closure depends on loaded route inventory, generated OpenAPI, TestClient behavior, and executable guards.

## Contract Shape

- Contract type:
  - Legacy natal closure, zero-hit scan, public route absence, and proof-only allowance contract.
- Fields:
  - `generate_natal_interpretation`: forbidden under `backend/app`.
  - `AIEngineAdapter.generate_natal_interpretation`: forbidden as positive runtime mock target.
  - `fake_generate_natal_interpretation`: forbidden as positive runtime fixture.
  - `/v1/natal/interpretation`: forbidden in public backend and frontend code.
  - `/v1/natal/interpretations`: forbidden in public backend and frontend code.
  - `natal_interpretation_short`: forbidden outside proof-only and extinction-test scopes.
  - `natal_long_free`: forbidden outside proof-only and extinction-test scopes.
  - `shouldRefreshShortAfterBasicUpgrade`: forbidden outside proof-only and extinction-test scopes.
  - `forceRefresh`: forbidden outside proof-only and extinction-test scopes.
- Required fields:
  - none for old public generation commands.
- Optional fields:
  - none for old public generation commands.
- Status codes:
  - Historical public natal interpretation routes must be absent from the loaded route inventory and OpenAPI.
- Serialization names:
  - Old command keys must not be emitted as public request fields.
- Frontend type impact:
  - Public `/natal` tests must prove no historical API URL or old technical control remains in nominal flows.
- Generated contract impact:
  - `app.openapi()` must omit historical natal interpretation paths.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal/evidence/cs-440-before-status.txt`
  - `_condamad/stories/CS-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal/evidence/legacy-symbols-before.txt`
  - `_condamad/stories/CS-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal/evidence/openapi-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal/evidence/cs-440-after-status.txt`
  - `_condamad/stories/CS-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal/evidence/legacy-symbols-after.txt`
  - `_condamad/stories/CS-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal/evidence/openapi-after.json`
- Expected invariant:
  - The only intended delta is CS-440 closure from blocked or partial evidence to clean zero-hit completion.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| CS-440 lifecycle status | `_condamad/stories/story-status.md` | untracked status note |
| CS-440 final evidence | `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/10-final-evidence.md` | separate ad hoc proof |
| CS-440 review verdict | `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/11-code-review.md` | report-only review statement |
| Zero-hit audit | `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/legacy-natal-zero-hit-audit.md` | scattered scan notes |
| Final closure report | `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md` | historical delivery report |
| Runtime guard | `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` | nominal old-symbol tests |
| Frontend anti-return guard | `frontend/src/tests/natalPublicDomGuard.test.tsx` | production UI code |

## Mandatory Reuse / DRY Constraints

- Reuse existing CS-440 architecture and LLM extinction guards instead of creating overlapping guards.
- Reuse existing frontend natal tests for DOM and public command proof.
- Reuse existing CS-440 audit and report artifacts rather than creating a parallel closure report.
- Keep one canonical CS-440 review verdict in `generated/11-code-review.md`.
- Keep one canonical tracker status for CS-440 in `_condamad/stories/story-status.md`.
- Do not duplicate old-symbol allowlists across CS-434, CS-435, and CS-440.

## No Legacy / Forbidden Paths

- No legacy runtime generation method may remain under `backend/app`.
- No compatibility route path may remain for historical natal interpretations.
- No fallback route, prompt, fixture, or frontend control may preserve old natal generation behavior.
- Forbidden runtime symbol: `generate_natal_interpretation`.
- Forbidden positive mock targets: `AIEngineAdapter.generate_natal_interpretation` and `fake_generate_natal_interpretation`.
- Forbidden public URLs: `/v1/natal/interpretation` and `/v1/natal/interpretations`.
- Forbidden control symbols: `natal_interpretation_short`, `natal_long_free`, `shouldRefreshShortAfterBasicUpgrade`, and `forceRefresh`.
- Allowed proof scopes: `_condamad` historical artifacts and explicitly named extinction tests.

## Reintroduction Guard

- Guard target: old natal runtime, prompt, public API, frontend control, and positive test symbols.
- The implementation must keep or update deterministic guards that fail when unauthorized old-symbol hits return.
- Deterministic source:
  - `pytest`, `TestClient`, `app.routes`, `app.openapi()`, `pnpm`, and bounded `rg` scans.
- Required backend guard command:
  ```powershell
  python -B -m pytest -q tests/architecture/test_legacy_natal_generation_inventory_guard.py tests/architecture/test_llm_legacy_extinction.py --tb=short
  ```
- Required route and OpenAPI checks:
  ```powershell
  python -B -c "from app.main import app; paths={getattr(r,'path','') for r in app.routes}; assert '/v1/natal/interpretation' not in paths"
  python -B -c "from app.main import app; assert '/v1/natal/interpretation' not in app.openapi().get('paths', {})"
  ```
- Required scan guard:
  ```powershell
  rg -n "generate_natal_interpretation" backend/app
  rg -n "/v1/natal/interpretation|/v1/natal/interpretations" backend/app/api/v1/routers/public frontend/src
  ```
- Expected result:
  - Python route and OpenAPI checks pass.
  - Backend architecture and LLM extinction tests pass.
  - Forbidden scans return zero unauthorized hits.

## Regression Guardrails

Applicable guardrails:

| Guardrail | scope -> invariant -> evidence |
|---|---|
| RG-001 `remove-historical-facade-routes` | old facades -> no wrapper, alias, fallback, or re-export -> `rg`, `app.routes`, `app.openapi()`. |
| RG-018 `block-supported-family-prompt-fallbacks` | natal prompts -> no supported prompt fallback ownership -> LLM `pytest`. |
| RG-021 `classify-converge-remaining-prompt-fallbacks` | fallback remnants -> remaining keys have final decision -> governance `pytest`. |
| RG-149 `CS-350-prompt-generation-current-implementation` | prompt cartography -> modern natal classification stays exact -> bounded scans. |
| RG-153 `CS-393-refondre-page-natal-autour-lecture-narrative` | `/natal` DOM -> modern narrative layout stays primary -> `pnpm` tests. |
| RG-154 `CS-395-verrouiller-non-regression-lecture-natale-publique` | public DOM -> old technical symbols stay hidden -> `pnpm` DOM guard. |
| RG-170 `CS-422` | Basic V2 DOM -> sources and legal mentions stay deduplicated -> frontend tests. |
| RG-173 `CS-435` | public generation -> product and LLM contracts own theme natal -> OpenAPI, routes, and `pytest`. |
| RG-174 `CS-440` | legacy natal closure -> zero public and runtime hit -> architecture guard plus bounded scans. |

- Scope vector: operation `update`, domain `legacy-natal-closure-evidence`, paths `backend/app`, `backend/tests`, `frontend/src`, and CS-440 evidence.
- Needs-investigation: none recorded from targeted ID lookup.
- Adjacent non-applicable examples: database schema, auth, migrations.
- Registry gap: none for this story; `RG-174` exists and must remain strict.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Status before | `_condamad/stories/CS-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal/evidence/cs-440-before-status.txt` | Capture status baseline. |
| Status after | `_condamad/stories/CS-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal/evidence/cs-440-after-status.txt` | Prove CS-440 final tracker state. |
| Legacy scan after | `_condamad/stories/CS-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal/evidence/legacy-symbols-after.txt` | Persist zero-hit scan output. |
| API scan after | `_condamad/stories/CS-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal/evidence/public-api-after.txt` | Persist public URL absence output. |
| OpenAPI after | `_condamad/stories/CS-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal/evidence/openapi-after.json` | Prove generated public API absence. |
| Validation output | `_condamad/stories/CS-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal/evidence/validation.txt` | Keep lint, tests, and scans. |
| CS-440 audit | `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/legacy-natal-zero-hit-audit.md` | Persist final zero-hit audit. |
| CS-440 final evidence | `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/10-final-evidence.md` | Mark final CS-440 AC closure. |
| Review output | `_condamad/stories/CS-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal/generated/11-code-review.md` | Keep review output. |

## Allowlist / Exception Register

- Allowlist handling: active.
- CS-434, CS-435, and CS-440 allowances must not authorize runtime old-symbol hits under `backend/app` or `frontend/src`.
- Allowed remaining entries:
  - historical `_condamad` evidence artifacts;
  - explicit extinction tests with anti-return names;
  - CS-440 review and final evidence records that document closure history.
- Forbidden remaining entries:
  - runtime app code using old symbols as public generation input;
  - positive tests that make old symbols expected behavior;
  - broad folder allowances over backend test trees or frontend test trees.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `CS-434 legacy-allowlist.md` | old natal symbols | Historical proof source. | Permanent historical evidence only. |
| `CS-435 legacy-scan-results.md` | old natal symbols | Historical scan source. | Permanent historical evidence only. |
| `CS-440 legacy-natal-zero-hit-audit.md` | old natal symbols | Final closure classification. | Permanent zero-hit audit. |
| `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` | old natal symbols | Extinction guard declarations. | Permanent anti-return test. |
| `frontend/src/tests/natalPublicDomGuard.test.tsx` | old control symbols | DOM denylist declarations. | Permanent anti-return test. |

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step data conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/legacy-natal-zero-hit-audit.md` - finalize closure classifications.
- `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md` - remove partial closure wording after proof.
- `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/10-final-evidence.md` - mark AC2, AC3, and AC4 pass.
- `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/11-code-review.md` - record clean review.
- `_condamad/stories/story-status.md` - mark CS-440 done after validations and review.
- `_condamad/stories/CS-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal/evidence/*.txt` - persist closure evidence.

Likely tests:

- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` - zero-hit architecture guard.
- `backend/tests/architecture/test_llm_legacy_extinction.py` - old LLM generation key extinction.
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py` - prompt governance classification.
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py` - orchestration old-key rejection.
- `backend/tests/unit/domain/theme_natal` - modern theme natal domain coverage.
- `backend/tests/integration/test_theme_natal_public_api_product_actions.py` - public product actions.
- `backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py` - Basic full runtime.
- `backend/tests/integration/test_theme_natal_public_reads.py` - public reads.
- `frontend/src/tests/natalChartApi.test.tsx` - frontend public API contract.
- `frontend/src/tests/natalPublicDomGuard.test.tsx` - frontend DOM anti-return guard.
- `frontend/src/tests/natalInterpretation.test.tsx` - public rendering contract.
- `frontend/src/tests/NatalChartPage.test.tsx` - page-level public behavior.

Files not expected to change:

- `backend/app/infra/**` - out of scope; no persistence adapter change is owned.
- `backend/migrations/**` - out of scope; no schema migration is owned.
- `frontend/src/styles/**` - out of scope; no styling change is owned.
- `_condamad/run-state.json` - explicitly out of scope.
- `_condamad/stories/regression-guardrails.md` - consulted only; no normal-generation enrichment is authorized.
- Historical `_condamad/reports` and delivered briefs outside CS-440 closure outputs - must not be deleted.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

Run Python, Ruff, and Pytest commands only after activating the venv with `.\.venv\Scripts\Activate.ps1`.

Backend validation:

```powershell
.\.venv\Scripts\Activate.ps1
Push-Location backend
ruff format .
ruff check .
python -B -m pytest -q tests/architecture/test_legacy_natal_generation_inventory_guard.py `
  tests/architecture/test_llm_legacy_extinction.py `
  tests/llm_orchestration/test_prompt_governance_registry.py `
  tests/llm_orchestration/test_llm_legacy_extinction.py --tb=short
python -B -m pytest -q tests/unit/domain/theme_natal `
  tests/integration/test_theme_natal_public_api_product_actions.py `
  tests/integration/test_theme_natal_basic_full_reading_runtime.py `
  tests/integration/test_theme_natal_public_reads.py --tb=short
Pop-Location
```

Runtime route and OpenAPI checks:

```powershell
.\.venv\Scripts\Activate.ps1
Push-Location backend
python -B -c "from app.main import app; paths={getattr(r,'path','') for r in app.routes}; assert '/v1/natal/interpretation' not in paths"
python -B -c "from app.main import app; assert all(not p.startswith('/v1/natal/interpretations') for p in app.openapi().get('paths', {}))"
Pop-Location
```

Frontend validation:

```powershell
pnpm --dir frontend test -- natalChartApi.test.tsx natalPublicDomGuard.test.tsx natalInterpretation.test.tsx NatalChartPage.test.tsx
pnpm --dir frontend lint
```

Scans:

```powershell
rg -n "generate_natal_interpretation" backend/app
```

- Forbidden pattern: `generate_natal_interpretation`.
- Allowed fixture pattern: none under `backend/app`.
- Scan roots: `backend/app`.
- Expected false positives: zero.

```powershell
rg -n "/v1/natal/interpretation|/v1/natal/interpretations" backend/app/api/v1/routers/public frontend/src
```

- Forbidden pattern: historical public natal interpretation URLs.
- Allowed fixture pattern: none in public backend router or frontend source roots.
- Scan roots: `backend/app/api/v1/routers/public`, `frontend/src`.
- Expected false positives: zero.

```powershell
rg -n "natal_interpretation_short|natal_long_free|shouldRefreshShortAfterBasicUpgrade|forceRefresh" backend/app frontend/src
```

- Forbidden pattern: old natal prompt and refresh control symbols.
- Allowed fixture pattern: none in runtime public roots.
- Scan roots: `backend/app`, `frontend/src`.
- Expected false positives: zero.

```powershell
rg -n "AIEngineAdapter\.generate_natal_interpretation|fake_generate_natal_interpretation" backend/tests backend/app/tests
rg -n "patch\.object\(AIEngineAdapter, \"generate_natal_interpretation\"" backend/tests backend/app/tests
```

- Forbidden pattern: positive mocks of old generation success.
- Allowed fixture pattern: extinction guard source inspection only.
- Scan roots: `backend/tests`, `backend/app/tests`.
- Expected false positives: zero positive runtime tests.

Story evidence checks:

```powershell
.\.venv\Scripts\Activate.ps1
python -B -c "from pathlib import Path; assert Path('_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/11-code-review.md').read_text().find('CLEAN') >= 0"
python -B -c "from pathlib import Path; assert '| CS-440 |' in Path('_condamad/stories/story-status.md').read_text()"
python -B -c "from pathlib import Path; assert Path('_condamad/stories/CS-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal/evidence/validation.txt').exists()"
```

Guardrail check:

```powershell
rg -n "RG-174.*zero public/runtime hit|Legacy natal deleted: zero public/runtime hit" _condamad/stories/regression-guardrails.md
```

## Regression Risks

- CS-440 can be closed prematurely if prerequisite stories are not cleanly reviewed.
- Zero-hit scans can be weakened by retaining broad allowances in CS-434, CS-435, or CS-440 evidence.
- Removing partial-closure wording without executable proof can hide CR-3 or CR-4.
- Frontend public DOM and Basic V2 behavior can regress while old technical controls are removed from tests.
- `RG-174` can drift if it allows runtime public hits instead of proof-only or extinction-test hits.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python, Ruff, or Pytest command.
- Do not edit `_condamad/run-state.json`.
- Do not enrich `_condamad/stories/regression-guardrails.md` during this story.
- Do not delete historical `_condamad` reports or delivered briefs.
- Do not add inline styles.

## References

- `_story_briefs/cs-444-clore-cs-440-zero-hit-apres-corrections-legacy-natal.md`
- `_story_briefs/cs-440-zero-hit-legacy-natal-tests-guards.md`
- `_story_briefs/cs-441-corriger-suppression-runtime-generate-natal-legacy.md`
- `_story_briefs/cs-442-corriger-suppression-sources-reintroduction-prompts-nataux-legacy.md`
- `_story_briefs/cs-443-corriger-suppression-api-publique-natal-interpretations-legacy.md`
- `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/10-final-evidence.md`
- `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/11-code-review.md`
- `_condamad/reports/cs-439-cs-440-delivery-report.md`
- `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md`
- `_condamad/stories/regression-guardrails.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
