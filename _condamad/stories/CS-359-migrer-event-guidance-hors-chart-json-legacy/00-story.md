# Story CS-359 migrer-event-guidance-hors-chart-json-legacy: Migrate Event Guidance Away From Legacy Chart Json
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-359-migrer-event-guidance-hors-chart-json-legacy.md`.
- Selected mode: Repo-informed story, because the story must audit runtime ownership before choosing migration or deletion.
- Source problem: `event_guidance` still exposes `chart_json` through canonical contracts, adapter routing, prompt seeds, and guidance governance.
- Source stakes:
  - No prompt-visible `chart_json` or `natal_data` may remain in a provider-capable `event_guidance` path.
  - A dormant use case must not be kept as debt after the product decision.
  - A real product trigger must be proven before preserving `event_guidance`.
  - Seeds, contracts, docs, tests, and governance must converge on the same final classification.
  - Modern natal prompt carriers must stay separate from non-natal guidance behavior.
- Source-alignment evidence: objective, target state, ACs, tasks, validation, non-goals, and guardrails preserve all brief stakes.

## Objective

Eliminate the legacy `chart_json` dependency from `event_guidance`.

The implementation must first audit whether `event_guidance` has a real product trigger. If it has one, migrate it to a canonical non-legacy input.
If it has no supported trigger, delete the dormant use case from runtime contracts, seeds, mappings, docs, and tests.

## Target State

- `event_guidance` has exactly one final classification in persisted evidence: `migrated` or `deleted`.
- `event_guidance` never requires `chart_json` or `natal_data` in runtime contracts, prompt placeholders, seed prompts, or provider-bound payloads.
- A kept `event_guidance` path uses a canonical versioned input that is distinct from `llm_astrology_input_v1`.
- A deleted `event_guidance` path has no canonical use-case contract, seed prompt, adapter branch, or governance mapping.
- CS-350 documentation and RG-149 classification stay aligned with the final decision.
- Frontend UI, database schema, auth, i18n, styling, build tooling, migrations, provider integration, and public API routes remain unchanged.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-359-migrer-event-guidance-hors-chart-json-legacy.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-359`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - `event_guidance` requires `chart_json` and `event_description`.
- Evidence 5: `backend/app/domain/llm/runtime/adapter.py` - `AIEngineAdapter.generate_guidance` still maps `event_guidance` to subfeature `event`.
- Evidence 6: `backend/app/ops/llm/bootstrap/seed_guidance_prompts.py` - guidance seed still declares `chart_json` for `event_guidance`.
- Evidence 7: `backend/app/domain/llm/governance/data/prompt_governance_registry.json` - guidance placeholders still include `chart_json`.
- Evidence 8: `backend/tests/llm_orchestration/test_llm_legacy_extinction.py` - `event_guidance` is still listed as governed supported prompt surface.
- Evidence 9: `backend/tests/llm_orchestration/test_prompt_governance_registry.py` - tests still classify `event_guidance` with fallback guards.
- Evidence 10: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - CS-350 classifies `event_guidance` as mandatory migration.
- Evidence 11: `_condamad/stories/regression-guardrails.md` - scoped resolver and targeted ID reads consulted RG-002, RG-022, and RG-149.
- Evidence 12: source-alignment review confirms this story closes the brief's migrate-or-delete decision without retaining debt.

Repository structure alert: no expected backend or documentation root is absent in this workspace.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend LLM guidance runtime contract for `event_guidance`.
  - Canonical use-case registry, adapter routing, guidance prompt seeds, prompt governance registry, and relevant backend tests.
  - Audit evidence proving whether a product trigger exists for `event_guidance`.
  - CS-350 documentation and RG-149 wording when the final classification changes.
  - Persistent evidence under `_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/evidence/`.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling, migrations, public API route changes, and real provider calls.
  - Modern natal use-case migration already owned by `llm_astrology_input_v1` stories.
  - Admin manual execution policy, admin sample payload policy, and unrelated guidance use cases.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
  - No real LLM provider call.
  - No retention of `event_guidance` as explicit debt.
  - No replacement of `chart_json` with `natal_data` or another legacy carrier.

Named brief primitives in scope:

- `event_guidance`
- `chart_json`
- `natal_data`
- `event_description`
- `canonical_use_case_registry.py`
- `AIEngineAdapter`
- `seed_guidance_prompts.py`
- `prompt_governance_registry.json`
- CS-350 prompt-generation cartography
- RG-149 prompt-generation classification guardrail

## Operation Contract

- Operation type: migrate
- Primary archetype: legacy-facade-removal
- Archetype reason: the story deletes or replaces a legacy prompt-carrier facade after the canonical LLM input path exists.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Change only `event_guidance` and directly attached LLM guidance contracts.
  - Keep `guidance_daily`, `guidance_weekly`, `guidance_contextual`, chat, horoscope, and natal use cases behaviorally unchanged.
  - Keep public routes, OpenAPI paths, frontend, DB, migrations, auth, i18n, style, build tooling, and provider policy unchanged.
  - Preserve only one final outcome: canonical migration or full deletion.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: a real product trigger exists but the canonical non-legacy event input cannot be defined from current owners.
- Additional validation rules:
  - `AST guard` or `pytest` must prove `event_guidance` no longer requires `chart_json` or `natal_data`.
  - `pytest -q backend/tests/llm_orchestration/test_llm_legacy_extinction.py` must prove old prompt carriers stay excluded.
  - `pytest -q backend/tests/llm_orchestration/test_prompt_governance_registry.py` must prove governance and fallback guards converge.
  - `rg` scans must classify every residual `event_guidance`, `chart_json`, and `natal_data` hit in touched backend and docs paths.
  - `app.routes`, `app.openapi()`, and `TestClient` must prove public API routes are unchanged.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, `AST guard`, `app.routes`, `app.openapi()`, and `TestClient` prove runtime boundaries. |
| Baseline Snapshot | yes | Before and after scans prove the only allowed surface delta is `event_guidance` convergence. |
| Ownership Routing | yes | Canonical ownership prevents moving prompt carrier logic into adapter, provider, frontend, or docs. |
| Allowlist Exception | no | No allowlist handling is authorized for this single use-case convergence. |
| Contract Shape | yes | A kept use case must expose exact canonical input; a deleted use case must leave no runtime shape. |
| Batch Migration | yes | Contracts, seeds, governance, adapter branch, docs, and tests must converge together. |
| Reintroduction Guard | yes | `chart_json`, `natal_data`, aliases, and dormant seeds must not return for this use case. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | A final `event_guidance` decision is persisted. | Evidence profile: baseline_before_after_diff; `python` checks decision artifact path. |
| AC2 | Runtime contracts exclude legacy carriers. | Evidence profile: field_removed; `pytest -q backend/tests/llm_orchestration/test_llm_legacy_extinction.py`; `AST guard`. |
| AC3 | Guidance seeds exclude legacy carriers. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks seed prompts; `pytest` seed or governance tests. |
| AC4 | Prompt governance excludes legacy carriers. | Evidence profile: no_legacy_contract; `pytest` governance test path; `rg`. |
| AC5 | Adapter routing matches the final decision. | Evidence profile: ast_architecture_guard; `AST guard`; `pytest` runtime suppression test path. |
| AC6 | Residual `event_guidance` hits are classified. | Evidence profile: targeted_forbidden_symbol_scan; `rg -n "event_guidance" backend/app backend/tests _condamad`. |
| AC7 | Modern natal legacy carriers stay blocked. | Evidence profile: no_legacy_contract; `pytest` astrology input boundary test path. |
| AC8 | CS-350 reflects the final `event_guidance` classification. | Evidence profile: targeted_forbidden_symbol_scan; CS-350 `rg` check. |
| AC9 | Public API route surface is unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`; `TestClient`. |
| AC10 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks evidence paths. |
| AC11 | RG-149 reflects the final `event_guidance` classification. | Evidence profile: targeted_forbidden_symbol_scan; RG-149 `rg` check. |

## Implementation Tasks

- [ ] Task 1: Audit all `event_guidance` references in code, tests, seeds, docs, and governance. (AC: AC1, AC6)
- [ ] Task 2: Persist the product-trigger decision with proof commands and final outcome. (AC: AC1)
- [ ] Task 3: For a kept use case, define the canonical non-legacy event input contract and version marker. (AC: AC2, AC4)
- [ ] Task 4: For a deleted use case, remove the canonical contract, adapter branch, seed prompt, and governance mapping. (AC: AC2, AC3, AC4, AC5)
- [ ] Task 5: Update backend tests so they prove no `chart_json` or `natal_data` reaches `event_guidance`. (AC: AC2, AC3, AC4, AC5, AC7)
- [ ] Task 6: Update CS-350 documentation and RG-149 only for the final classification. (AC: AC8, AC11)
- [ ] Task 7: Persist before and after scans, decision record, OpenAPI snapshots, and validation output. (AC: AC1, AC6, AC9, AC10)
- [ ] Task 8: Run targeted and full backend validation from the activated venv. (AC: AC2, AC3, AC4, AC5, AC7, AC9, AC10)

## Files to Inspect First

- `_story_briefs/cs-359-migrer-event-guidance-hors-chart-json-legacy.md`
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/audits/prompt-generation-document-review/2026-05-27-2246/03-parallel-legacy-processes-audit.md`
- `_condamad/architecture/prompt-generation-document-review/2026-05-27-2338/archi-parallel-legacy-prompt-generation-report.md`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/ops/llm/bootstrap/seed_guidance_prompts.py`
- `backend/app/domain/llm/governance/data/prompt_governance_registry.json`
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py`
- `backend/tests/integration/test_llm_runtime_suppression.py`
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`

## Runtime Source of Truth

- Primary source of truth:
  - `CanonicalUseCaseContract` entries in `canonical_use_case_registry.py`.
  - `AIEngineAdapter.generate_guidance` request construction and subfeature routing.
  - `seed_guidance_prompts.py` published guidance prompt declarations.
  - `PromptGovernanceRegistry` loaded from `prompt_governance_registry.json`.
  - `AST guard` over `event_guidance`, `chart_json`, and `natal_data` in backend LLM files.
  - `pytest` tests for LLM legacy extinction, prompt governance, runtime suppression, and astrology input boundaries.
  - `app.routes`, `app.openapi()`, and `TestClient` for public API neutrality.
- Secondary evidence:
  - CS-350 prompt-generation cartography and RG-149.
  - Targeted `rg` scans over backend app, backend tests, and `_condamad` docs.
- Static scans alone are not sufficient for this story because:
  - A live adapter or governance branch can be provider-capable even when only seed and test references look dormant.

## Contract Shape

- Contract type:
  - Backend internal LLM guidance use-case contract.
- Fields:
  - `event_guidance`: canonical use-case key to migrate or delete.
  - `event_description`: required string for a kept use case.
  - canonical event context field: required non-legacy object for a kept use case.
  - `chart_json`: forbidden old prompt carrier.
  - `natal_data`: forbidden old prompt carrier.
- Allowed final outcome `migrated`:
  - `event_guidance` remains a canonical use case only with a versioned non-legacy event input.
  - Required input fields include `event_description` and the new canonical event context field.
  - Required input fields exclude `chart_json`, `natal_data`, `legacy_astrology_input`, and wildcard astrology carriers.
  - Prompt placeholders exclude `chart_json` and `natal_data`.
  - Provider-bound payload tests prove the canonical event input is rendered without old carriers.
- Allowed final outcome `deleted`:
  - `event_guidance` is absent from canonical contracts, adapter subfeature routing, guidance seeds, governance mappings, and active tests.
  - Residual docs or historical audit mentions are classified as historical context or updated to closed classification.
- Required fields:
  - `event_description` for a kept use case.
  - The canonical non-legacy event context field for a kept use case.
- Optional fields:
  - `locale`, `context_lines`, `objective`, and `time_horizon` only when explicitly owned by the guidance family.
- Forbidden fields:
  - `chart_json`
  - `natal_data`
  - `legacy_astrology_input`
  - `chart_json_v2`
  - `natal_data_v2`
- Status codes:
  - none; this story changes backend internal LLM contracts and no public HTTP route.
- Serialization names:
  - The kept canonical event input uses one snake_case key and is documented in the decision artifact.
- Frontend type impact:
  - none.
- Generated contract impact:
  - `app.openapi()` must remain unchanged for public API paths.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/evidence/event-guidance-scan-before.txt`
  - `_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/evidence/openapi-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/evidence/event-guidance-scan-after.txt`
  - `_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/evidence/openapi-after.json`
- Expected invariant:
  - The only intended backend LLM surface delta is migration or deletion of `event_guidance`.
  - Public API paths from `app.openapi()` remain unchanged.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Use-case contract | `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | adapter branch constants |
| Guidance prompt seed | `backend/app/ops/llm/bootstrap/seed_guidance_prompts.py` | provider client code |
| Guidance placeholder governance | `backend/app/domain/llm/governance/data/prompt_governance_registry.json` | tests or docs only |
| Runtime guidance request | `backend/app/domain/llm/runtime/adapter.py` | frontend or API router |
| Classification docs | `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` | backend comments only |
| Story evidence | `_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/evidence/**` | application source |

## Removal Classification Rules

- `canonical-active`: a kept `event_guidance` contract uses the new non-legacy event input and has a proven product trigger.
- `external-active`: a caller outside backend LLM guidance still invokes `event_guidance` and requires user decision before deletion.
- `historical-facade`: a contract, seed, adapter branch, or test only preserves the old `chart_json` prompt carrier.
- `dead`: a contract, seed, adapter branch, or governance row has zero active product trigger after bounded scans.
- `needs-user-decision`: a trigger exists but the canonical non-legacy event input cannot be defined from repository evidence.

## Removal Audit Format

The implementation must persist this table in:

`_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/evidence/event-guidance-decision.md`

Allowed decisions are `keep`, `delete`, `replace-consumer` and `needs-user-decision`.

The removal audit is a persisted audit artifact and must be committed with the story execution evidence.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `event_guidance` contract | use case | historical-facade or canonical-active | exact callers | event input or none | exact decision | `rg`, `pytest`, `AST guard` | exact risk |
| `chart_json` prompt carrier | field | historical-facade | seeds or runtime | non-legacy event input or none | delete | `rg`, `pytest` | provider leakage |
| `event_guidance` seed | seed | historical-facade or dead | bootstrap | canonical seed or none | exact decision | `rg`, `pytest` | stale prompt |

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Use-case declaration | `canonical_use_case_registry.py` | adapter-only constants or docs-only rows |
| Guidance prompt placeholders | `prompt_governance_registry.json` | local test allowlists |
| Guidance seed content | `seed_guidance_prompts.py` | provider client or frontend code |
| Runtime guidance routing | `AIEngineAdapter.generate_guidance` | public API router or frontend code |
| Classification evidence | CS-350 docs, RG-149, and story evidence | comments without validation proof |

## Delete-Only Rule

- Items classified as `historical-facade` or `dead` must be deleted.
- Items classified as removable are deleted, not repointed.
- Items classified as removable are deleted, not hidden behind a soft-disabled branch.
- Do not preserve a wrapper, compatibility alias, shim module, old-key serializer, re-export, or dormant seed.
- Do not add `chart_json_v2`, `natal_data_v2`, `legacy_astrology_input`, wildcard placeholders, or renamed legacy carriers.
- A kept `event_guidance` path must replace the old carrier with a canonical non-legacy event input and tests that fail on old carriers.

## External Usage Blocker

- Any `external-active` item must not be deleted.
- Any `external-active` item must block deletion until the user records a user decision.
- The blocker must name the item, consumer, proof command, deletion risk, user decision, and safest next action.
- No item may be classified as `needs-user-decision` without `rg`, `pytest`, `AST guard`, or generated-contract proof.
- A blocker must not keep `event_guidance` as debt; it must stop implementation until the canonical input or deletion decision is supplied.

## Migration Decision Rules

- `migrated`: a real product trigger exists and a canonical event input is defined without `chart_json` or `natal_data`.
- `deleted`: no real product trigger exists after code, tests, docs, and seed audit.
- `blocked`: a real product trigger exists but the canonical non-legacy event input needs an owner decision.
- `retained-debt`: forbidden outcome.

The implementation must persist the selected outcome in:

`_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/evidence/event-guidance-decision.md`

Required decision table:

| Item | Evidence command | Product trigger | Final outcome | Code action | Test proof | Residual risk |
|---|---|---|---|---|---|---|
| `event_guidance` | `rg`, `pytest`, `AST guard` | `yes`, `no`, or `blocked` | `migrated`, `deleted`, or `blocked` | exact files | exact tests | exact risk |

## Mandatory Reuse / DRY Constraints

- Reuse existing `CanonicalUseCaseContract`, `PromptGovernanceRegistry`, `AIEngineAdapter`, and guidance seed patterns.
- Reuse current LLM legacy extinction and prompt governance tests before adding new test modules.
- Keep one canonical event input contract when `event_guidance` is migrated.
- Do not duplicate guidance prompt rendering logic in tests or docs.
- Do not add external packages.
- Do not create a second registry or local placeholder allowlist for this use case.

## No Legacy / Forbidden Paths

- No legacy prompt carrier may remain required or prompt-visible for `event_guidance`.
- No compatibility prompt carrier may be added for `event_guidance`.
- No fallback prompt carrier may be added for `event_guidance`.
- Forbidden prompt-carrier keys: `chart_json`, `natal_data`, `legacy_astrology_input`, `chart_json_v2`, and `natal_data_v2`.
- Forbidden implementation surfaces: `frontend/src/**`, public API routers, DB migrations, provider policy, unrelated guidance use cases, and natal use cases.
- Forbidden outcome: preserving `event_guidance` as dormant debt.

## Reintroduction Guard

- Add or update deterministic `pytest` coverage so `event_guidance` cannot require `chart_json` or `natal_data`.
- Add or update an architecture guard against reintroduction of removed or forbidden prompt carriers.
- Add or update an architecture guard that fails if the removed surface is reintroduced.
- Add or update an `AST guard` that fails when `event_guidance` reintroduces forbidden prompt carriers.
- The guard must check at least one deterministic source:
  - canonical use-case contract fields;
  - prompt governance placeholders;
  - guidance seed declarations;
  - adapter routing branches;
  - forbidden symbols or states.
- Required forbidden examples:
  - `event_guidance` requiring `chart_json`;
  - `event_guidance` requiring `natal_data`;
  - `event_guidance` preserved as a dormant seed, compatibility alias, fallback, or shim.
- Guard residual occurrences with:
  - `rg -n "event_guidance|chart_json|natal_data" backend/app backend/tests _condamad`
- Guard public API neutrality with:
  - `python -c "from app.main import app; assert app.routes; assert app.openapi()['paths']"`
- Guard CS-350 and RG-149 alignment with:
  - `rg -n "event_guidance.*migration obligatoire|event_guidance" _condamad/docs/prompt-generation-cartography _condamad/stories/regression-guardrails.md`

## Generated Contract Check

- Generated contract check: applicable
- Required generated evidence:
  - `python -c "from app.main import app; assert app.routes; assert app.openapi()['paths']"`
  - `python -c "from app.main import app; assert 'event_guidance' not in str(app.openapi())"`
  - `python -c "from app.main import app; assert 'chart_json' not in str(app.openapi())"`
- Expected result:
  - Public OpenAPI paths are unchanged by this backend internal LLM convergence.

## Regression Guardrails

Scope vector:

- Operation: migrate with deletion allowed.
- Domain: backend-domain, LLM prompt generation, guidance use-case contract.
- Paths: `backend/app/domain/llm`, `backend/app/ops/llm/bootstrap`, `backend/tests`, `_condamad/docs/prompt-generation-cartography`.
- Contracts: no-legacy, prompt-governance, runtime-contract, classification-doc.

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Public API routing must remain unchanged. | `app.routes`; `app.openapi()`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Prompt-generation validation must target collected pytest files. | targeted `pytest`; bounded `rg`. |
| RG-149 `CS-350-prompt-generation-current-implementation` | CS-350 must preserve final `event_guidance` classification. | CS-350 `rg`; RG-149 `rg`. |

Non-applicable examples:

- RG-041 entitlement documentation is out of scope because this story changes guidance prompt contracts only.
- RG-047 frontend inline styles are out of scope because no TSX or CSS surface is touched.
- RG-052 frontend CSS namespace migration is out of scope because no frontend migration is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Decision record | `_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/evidence/event-guidance-decision.md` | Persist final outcome. |
| Before scan | `_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/evidence/event-guidance-scan-before.txt` | Capture initial hits. |
| After scan | `_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/evidence/event-guidance-scan-after.txt` | Classify residual hits. |
| Before OpenAPI snapshot | `_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/evidence/openapi-before.json` | Prove public baseline. |
| After OpenAPI snapshot | `_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/evidence/openapi-after.json` | Prove public neutrality. |
| Validation output | `_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/evidence/validation.txt` | Store final command output. |
| Review output | `_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this story.

## Batch Migration Plan

- Batch migration plan: applicable

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| decision | `event_guidance` debt | `migrated` or `deleted` | docs, evidence | none | `python` path check | owner trigger unclear |
| contract | `chart_json` input schema | canonical event input or no contract | registry | contract tests | `pytest`, `AST guard` | undefined input |
| seed | `chart_json` prompt seed | canonical seed or no seed | bootstrap | seed tests | `rg`, `pytest` | missing trigger |
| runtime | adapter event branch | canonical routing or no branch | adapter | runtime tests | `pytest`, `AST guard` | hidden caller |
| docs | mandatory migration marker | migrated or deleted classification | CS-350, RG-149 | doc scans | `rg` | docs disagree |

- Stop condition:
  - `event_guidance` is migrated to a canonical non-legacy input or fully deleted.
  - No active runtime contract, seed, governance row, or adapter branch can feed `chart_json` or `natal_data` to this use case.

## Expected Files to Modify

Likely files:

- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - migrate or delete the `event_guidance` contract.
- `backend/app/domain/llm/runtime/adapter.py` - align guidance routing with the final decision.
- `backend/app/ops/llm/bootstrap/seed_guidance_prompts.py` - migrate or delete the `event_guidance` seed.
- `backend/app/domain/llm/governance/data/prompt_governance_registry.json` - align guidance placeholders.
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - update final classification.
- `_condamad/stories/regression-guardrails.md` - update RG-149 only when final classification changes.
- `_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/evidence/**` - persist decision and validation evidence.

Likely tests:

- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py`
- `backend/tests/integration/test_llm_runtime_suppression.py`
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- `backend/tests/architecture/test_llm_legacy_extinction.py`

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no public endpoint is changed.
- `backend/app/infra/**` - out of scope; no persistence or external adapter is touched.
- `backend/alembic/**` - out of scope; no migration is touched.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - natal carrier remains separate and unchanged.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

Run all Python commands after activating the venv.

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `pytest -q tests/llm_orchestration/test_llm_legacy_extinction.py`
- VC6: `pytest -q tests/llm_orchestration/test_prompt_governance_registry.py`
- VC7: `pytest -q tests/integration/test_llm_runtime_suppression.py`
- VC8: `pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- VC9: `pytest -q tests/architecture/test_llm_legacy_extinction.py`
- VC10: `pytest -q`
- VC11: `python -c "from app.main import app; assert app.routes; assert app.openapi()['paths']"`
- VC12: `rg -n "event_guidance|chart_json|natal_data" app tests ../_condamad`
- VC13: `rg -n "event_guidance.*migration obligatoire|event_guidance" ../_condamad/docs/prompt-generation-cartography ../_condamad/stories/regression-guardrails.md`
- VC14: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/evidence/event-guidance-decision.md').exists()"`
- VC15: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/evidence/validation.txt').exists()"`

## Regression Risks

- A dormant seed may keep provider-capable `chart_json` rendering even after the canonical contract changes.
- A test may classify `event_guidance` as supported while runtime code deletes it, causing governance drift.
- A kept use case may incorrectly reuse `llm_astrology_input_v1`, mixing non-natal event guidance with modern natal prompt ownership.
- Residual `chart_json` hits may be valid negative guards or historical docs, but they must be classified.
- CS-350 or RG-149 may continue to describe mandatory migration after the implementation reaches `migrated` or `deleted`.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python, pip, pytest, or ruff command.
- Work from `backend` for VC3 through VC12 after venv activation.
- Persist the final migration decision before changing tests to match it.
- Do not keep `event_guidance` as dormant debt under any name.
- Do not use `natal_data`, `chart_json_v2`, or `legacy_astrology_input` as replacement input.

## References

- `_story_briefs/cs-359-migrer-event-guidance-hors-chart-json-legacy.md`
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/audits/prompt-generation-document-review/2026-05-27-2246/03-parallel-legacy-processes-audit.md`
- `_condamad/architecture/prompt-generation-document-review/2026-05-27-2338/archi-parallel-legacy-prompt-generation-report.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/ops/llm/bootstrap/seed_guidance_prompts.py`
- `backend/app/domain/llm/governance/data/prompt_governance_registry.json`
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py`
- `backend/tests/integration/test_llm_runtime_suppression.py`
