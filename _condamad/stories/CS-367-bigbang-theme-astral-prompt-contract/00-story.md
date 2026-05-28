# Story CS-367 bigbang-theme-astral-prompt-contract: Bigbang Theme Astral Prompt Contract
Status: ready-to-dev

## Trigger / Source

- Mode: Repo-informed story from implementation brief.
- Source brief: `_story_briefs/cs-367-bigbang-remplacer-ancien-contrat-prompt-theme-astral-supprimer-legacy.md`.
- Source problem: `theme_astral` must switch to one new prompt construction contract without a durable second runtime path.
- Source stakes:
  - User impact: theme astral generation must keep working after the contract switch without plan-specific prompt drift.
  - Technical risk: old carriers, old use cases, old prompt seeds, and stale tests can keep a second runtime path alive.
  - Closure expectation: remove replaced legacy surfaces and make `theme_astral_prompt_v1` the only active prompt contract.
  - Forbidden regression: commercial plan must not be exposed to the LLM and examples must keep one stable structure.
- Source-alignment review: PASS. Objective, target state, ACs, tasks, evidence, non-goals, and guardrails map to the brief stakes.

## Objective

Switch `theme_astral` to the canonical prompt construction path in one backend-domain change.

The only active path must be:

`calculs astrologiques -> interpretation_material -> theme_astral_llm_input_v1 -> provider payload stable -> output_contract`.

## Target State

`theme_astral_prompt_v1` is the only active prompt contract for theme astral provider payload construction.

The runtime no longer feeds theme astral prompts from:

- `chart_json`
- `natal_data`
- `llm_astrology_input_v1` as the prompt-visible contract for this feature
- `natal_interpretation_short`
- `NATAL_SHORT_PROMPT`
- `NATAL_COMPLETE_PROMPT`
- plan-specific natal prompts

Examples and docs describe one stable payload structure across delivery profiles. Reversal is limited to Git or deployment rollback.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-367-bigbang-remplacer-ancien-contrat-prompt-theme-astral-supprimer-legacy.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-367`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `.agents/skills/condamad-story-writer/references/removal-story-contract.md` - removal contract read for this story.
- Evidence 5: `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/00-story.md` - material prerequisite read.
- Evidence 6: `_condamad/stories/CS-366-provider-payload-builder-theme-astral/00-story.md` - provider payload prerequisite read.
- Evidence 7: targeted `rg` found old-carrier and old-prompt tokens in backend services, bootstrap, tests, docs, and examples.
- Evidence 8: targeted `rg` found no current `theme_astral_prompt_v1` or `theme_astral_llm_input_v1` token in backend app paths.
- Evidence 9: scoped guardrail resolver returned `RG-002` and `RG-022` as local guardrails for backend prompt-generation scope.
- Repository structure alert: `_condamad/architecture/theme-astral-prompt-contract/**/archi-theme-astral-prompt-contract-v1.md` is absent.
- Assumption risk: CS-365 and CS-366 may be implemented before this story starts; implementation must inspect their final files first.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Theme astral prompt contract runtime switch.
  - Removal of replaced theme astral prompt use cases, prompt seeds, assemblies, mocks, and tests.
  - Blocking `chart_json` and `natal_data` as prompt-visible carriers for `theme_astral`.
  - Blocking plan-specific natal prompts as `theme_astral` provider inputs.
  - Architecture tests that prevent reintroduction of the old theme astral path.
  - Example JSON and docs updates for one stable payload structure.
  - Local backend lint and test validation without external provider calls.
- Out of scope:
  - Frontend UI, auth, i18n, styling, build tooling, DB schema design, unrelated features, and real LLM provider calls.
  - Rewriting business copy beyond the minimum required by the contract switch.
  - Guardrail registry maintenance or enrichment.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
  - No temporary compatibility pathway for the old theme astral prompt contract.
  - No provider LLM call.
  - No migration of features other than `theme_astral`.

Named brief primitives in scope:

- `theme_astral`
- `theme_astral_prompt_v1`
- `theme_astral_llm_input_v1`
- `interpretation_material`
- `provider payload stable`
- `output_contract`
- `chart_json`
- `natal_data`
- `llm_astrology_input_v1`
- `natal_interpretation_short`
- `NATAL_SHORT_PROMPT`
- `NATAL_COMPLETE_PROMPT`
- `delivery_profile`
- `astrologer_voice`
- tests, mocks, examples, docs, and architecture guards

Named brief primitives out of scope:

- other features
- real provider LLM call
- frontend UI
- auth
- i18n
- styling
- unrelated DB schema work

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: the story removes old prompt carriers, prompt constants, mocks, and assemblies that preserve old feature behavior.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Activate only the canonical `theme_astral_prompt_v1` path for `theme_astral`.
  - Preserve one provider payload skeleton across delivery profiles.
  - Keep commercial plan labels outside LLM-visible payloads.
  - Replace old active consumers with the canonical contract before deleting replaced surfaces.
  - Keep unrelated natal features and non-theme-astral use cases unchanged unless the removal audit proves shared ownership.
  - Keep provider clients, frontend files, and unrelated persistence surfaces unchanged.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: a removed candidate is classified `external-active` or has an unresolved non-theme-astral consumer.
- Additional validation rules:
  - `AST guard` must prove theme astral runtime uses one canonical prompt construction path.
  - A full `pytest -q tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py` path must prove runtime handoff.
  - A full `pytest -q tests/architecture/test_theme_astral_prompt_contract_guard.py` path must prove reintroduction guards.
  - Targeted `rg` must prove old carrier and old prompt tokens have no active theme astral consumer.
  - Runtime checks must prove `app.routes` and `app.openapi()` are unchanged by this backend-domain story.
  - Startup proof must use `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`.
  - The removal audit must classify every candidate before deletion.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `AST guard`, pytest, `app.routes`, and `app.openapi()` prove runtime and public API boundaries. |
| Baseline Snapshot | yes | Before and after scans prove the only allowed surface delta is the theme astral prompt contract switch. |
| Ownership Routing | yes | Contract, runtime, examples, docs, and tests need canonical owners before deletion. |
| Allowlist Exception | no | No allowlist handling is authorized for this bigbang switch. |
| Contract Shape | yes | `theme_astral_prompt_v1` and provider payload fields must keep one stable shape. |
| Batch Migration | yes | A finite candidate list must be classified and migrated in one batch. |
| Reintroduction Guard | yes | Old carriers, prompt seeds, use cases, and tests must not return as active theme astral paths. |
| Persistent Evidence | yes | Audit, snapshots, scans, validation output, and review handoff must persist. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Theme astral path is unique. | `pytest -q tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py` |
| AC2 | `chart_json` cannot feed theme astral. | Evidence profile: targeted_forbidden_symbol_scan; `pytest`; `rg` checks backend theme astral consumers. |
| AC3 | `natal_data` cannot feed theme astral. | Evidence profile: targeted_forbidden_symbol_scan; `pytest`; `rg` checks backend theme astral consumers. |
| AC4 | Old plan prompts are inactive. | Evidence profile: python_module_removed; architecture guard pytest; `rg`. |
| AC5 | Commercial plan is hidden from LLM. | `pytest -q tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py` |
| AC6 | Example payload shapes are stable. | Evidence profile: json_contract_shape; `python` checks example JSON keys. |
| AC7 | Old tests are replaced. | Evidence profile: repo_wide_negative_scan; `rg` checks old assertions and new contract tests. |
| AC8 | Reintroduction guard fails old path. | Evidence profile: reintroduction_guard; architecture guard pytest. |
| AC9 | Public API routes are unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`. |
| AC10 | Story evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks evidence and generated paths. |
| AC11 | Local startup command is exact. | `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000` |

## Implementation Tasks

- [ ] Task 1: Read CS-365, CS-366, and current backend owners before editing. (AC: AC1, AC10)
- [ ] Task 2: Write the removal audit and classify every old carrier, prompt, seed, assembly, test, mock, example, and doc token. (AC: AC2, AC3, AC4, AC7)
- [ ] Task 3: Route every active theme astral consumer to `theme_astral_prompt_v1` and `theme_astral_llm_input_v1`. (AC: AC1)
- [ ] Task 4: Delete candidates classified `historical-facade` or `dead` after their consumers are replaced. (AC: AC4, AC7)
- [ ] Task 5: Block `chart_json` and `natal_data` as prompt-visible inputs for theme astral. (AC: AC2, AC3)
- [ ] Task 6: Remove or replace tests and mocks that validate the old theme astral prompt path. (AC: AC7)
- [ ] Task 7: Add architecture tests that fail on old carriers, old prompt constants, and old use cases. (AC: AC8)
- [ ] Task 8: Update examples so all delivery profiles share the stable provider payload shape. (AC: AC6)
- [ ] Task 9: Update prompt-generation docs to describe the canonical theme astral path only. (AC: AC1, AC6)
- [ ] Task 10: Prove public API routes and OpenAPI stay unchanged. (AC: AC9)
- [ ] Task 11: Prove or document the exact local backend startup command. (AC: AC11)
- [ ] Task 12: Run validation commands and persist output under this story evidence folder. (AC: AC10)

## Files to Inspect First

- `_story_briefs/cs-367-bigbang-remplacer-ancien-contrat-prompt-theme-astral-supprimer-legacy.md` - source scope.
- `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/00-story.md` - material prerequisite.
- `_condamad/stories/CS-366-provider-payload-builder-theme-astral/00-story.md` - provider payload prerequisite.
- `_condamad/architecture/theme-astral-prompt-contract/**/archi-theme-astral-prompt-contract-v1.md` - expected architecture deliverable.
- `backend/app/domain/llm/**` - prompt contract, runtime, configuration, and gateway owners.
- `backend/app/domain/astrology/interpretation/**` - theme astral input and interpretation material owners.
- `backend/app/services/llm_generation/natal/**` - current natal runtime and old carrier boundaries.
- `backend/app/ops/llm/bootstrap/**` - prompt seeds and use case bootstrap surfaces.
- `backend/tests/**` - expected tests path from project contract.
- `backend/app/tests/**` - existing test path observed in this workspace.
- `_condamad/examples/prompt-generation-cartography/**` - provider payload examples.
- `_condamad/docs/prompt-generation-cartography/**` - prompt cartography docs.

## Runtime Source of Truth

- Primary source of truth:
  - Integration test `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`.
  - Architecture guard `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py`.
  - `AST guard` over backend prompt construction imports and constants.
  - Loaded app boundary checks using `app.routes` and `app.openapi()`.
- Secondary evidence:
  - Targeted `rg` scans for old carriers, old prompt constants, new contract tokens, docs, and examples.
  - Before and after snapshots persisted under the CS-367 evidence folder.
- Static scans alone are not sufficient for this story because:
  - Runtime handoff, output shape, and public API boundary stability require loaded tests and app introspection.

## Contract Shape

- Contract type:
  - Backend prompt construction and provider payload contract for `theme_astral`.
- Fields:
  - `theme_astral_prompt_v1`: canonical prompt contract identifier.
  - `theme_astral_llm_input_v1`: canonical feature input contract.
  - `interpretation_material`: sourced interpretive material from CS-365.
  - `delivery_profile`: LLM-visible delivery profile values without commercial labels.
  - `astrologer_voice`: style and voice input, not fact ownership.
  - `output_contract`: versioned output response contract.
- Required fields:
  - `theme_astral_prompt_v1`
  - `theme_astral_llm_input_v1`
  - `interpretation_material`
  - `delivery_profile`
  - `astrologer_voice`
  - `output_contract`
- Optional fields:
  - none.
- Status codes:
  - none; no API route is created or changed.
- Serialization names:
  - JSON payload keys must match the canonical CS-366 provider payload shape.
- Frontend type impact:
  - none.
- Generated contract impact:
  - `app.openapi()` must be unchanged because this story does not change public API routes.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/evidence/legacy-scan-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/evidence/legacy-scan-after.txt`
- Expected invariant:
  - The only intended surface delta is removal of replaced theme astral prompt path surfaces and activation of the canonical contract path.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Theme astral prompt contract | `backend/app/domain/llm/**` canonical contract owner | prompt seed constants as runtime truth |
| Theme astral input contract | `backend/app/domain/astrology/interpretation/**` | `chart_json` or `natal_data` carrier builders |
| Provider payload shape | `backend/app/domain/llm/runtime/**` | plan-specific prompt assemblies |
| Runtime orchestration | `backend/app/services/llm_generation/natal/**` | duplicated feature-specific service path |
| Bootstrap updates | `backend/app/ops/llm/bootstrap/**` | old prompt constants kept active |
| Architecture guard tests | `backend/tests/architecture/**` | docs-only guard |
| Integration tests | `backend/tests/integration/llm/**` | live provider tests |
| Story evidence | `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/evidence/` | backend app code |

## Mandatory Reuse / DRY Constraints

- Reuse CS-365 `interpretation_material` output instead of rebuilding material in prompt code.
- Reuse CS-366 provider payload builder shape instead of introducing a second theme astral payload builder.
- Reuse existing gateway and execution request abstractions without adding provider clients.
- Keep one canonical mapping from commercial plan to `delivery_profile`.
- Keep one architecture guard for old prompt carriers instead of scattered ad hoc checks.
- Keep validation scans centralized in this story evidence and backend tests.
- Do not introduce new dependencies.

## No Legacy / Forbidden Paths

- No legacy theme astral prompt path may stay active.
- No compatibility prompt path may stay active for theme astral.
- No fallback path may feed theme astral from old carriers.
- No alias, shim, or wrapper may preserve old theme astral prompt behavior.
- No `chart_json` or `natal_data` carrier may be prompt-visible for theme astral.
- No `llm_astrology_input_v1` prompt-visible contract may remain the active theme astral contract.
- No `natal_interpretation_short`, `NATAL_SHORT_PROMPT`, or `NATAL_COMPLETE_PROMPT` may act as theme astral runtime truth.
- Do not edit frontend files, auth, i18n, styling, provider clients, unrelated feature runtime, or guardrail registry entries.

## Removal Classification Rules

- `canonical-active`: keep only when the item is the canonical `theme_astral_prompt_v1` path or a shared non-theme-astral owner.
- `external-active`: keep or escalate only when an external consumer is proven by public docs, generated contracts, or explicit audit evidence.
- `historical-facade`: delete when the item delegates to or preserves an old carrier, prompt, assembly, mock, or use case for theme astral.
- `dead`: delete when scans show zero active consumers in production code, tests, docs, examples, generated contracts, and known surfaces.
- `needs-user-decision`: record exact ambiguity and stop deletion for that item until the user decides.

## Removal Audit Format

The implementation must persist this table in:

`_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/evidence/removal-audit.md`

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Every row must use one allowed classification and one allowed decision: `keep`, `delete`, `replace-consumer`, or `needs-user-decision`.

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Theme astral prompt contract | `theme_astral_prompt_v1` owner under backend LLM domain | old natal prompt constants and old prompt seeds |
| Theme astral input payload | `theme_astral_llm_input_v1` owner under astrology interpretation domain | old carrier contracts |
| Interpretation material | CS-365 material builder owner | prompt text constants and provider payload fabrication |
| Provider payload | CS-366 provider payload builder owner | plan-specific prompt assemblies |
| Output contract | versioned output contract owner | divergent per-plan output schemas |

## Delete-Only Rule

- Items classified `historical-facade` or `dead` must be deleted, not repointed after consumers are moved.
- No wrapper may preserve old theme astral prompt behavior.
- No alias may preserve old theme astral prompt behavior.
- Deleted candidates must not be soft-disabled or preserved through re-export.
- Shared non-theme-astral owners may stay only after the removal audit proves they are not active theme astral surfaces.

## External Usage Blocker

- External usage blocker: active
- Rule: items classified `external-active` must not be deleted without explicit user decision.
- Required evidence: exact file path, generated artifact, public doc, or command output proving the external consumer and deletion risk.

## Generated Contract Check

- Generated contract check: active
- Required evidence:
  - `python` check over `app.openapi()` proving no public API path changed.
  - `python` check over `app.routes` proving no runtime route was added or removed by this backend-domain story.
  - Local startup proof or exact command: `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`.
  - JSON example shape check proving provider payload examples use the canonical theme astral contract.

## Reintroduction Guard

- The implementation must require an architecture guard so old theme astral prompt paths cannot be reintroduced.
- The architecture guard must check importable Python modules and forbidden symbols.
- Add or update an architecture guard that fails on active theme astral use of `chart_json`, `natal_data`, or old prompt constants.
- Add or update tests that fail if `natal_interpretation_short` is selected as the theme astral runtime prompt contract.
- Add a bounded `rg` guard for `llm_astrology_input_v1`, `NATAL_SHORT_PROMPT`, and `NATAL_COMPLETE_PROMPT` in theme astral paths.
- Add a JSON shape guard for examples across delivery profiles.
- Add loaded app checks for `app.routes` and `app.openapi()` to prove public API stability.

## Regression Guardrails

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend app layout and public API routes stay stable. | `app.routes`; `app.openapi()`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Backend pytest paths must match collected paths. | `pytest` paths; validation artifact. |
| Registry gap | No exact guardrail covers theme astral old-carrier bigbang removal. | Resolver output saved in evidence. |

Non-applicable examples:

- `RG-047` frontend inline styles is out of scope because no frontend source is touched.
- `RG-052` frontend CSS namespace migration is out of scope because no style source is touched.
- `RG-041` entitlement documentation is out of scope because no entitlement documentation surface is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Removal audit | `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/evidence/removal-audit.md` | Classify candidates. |
| Legacy scan before | `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/evidence/legacy-scan-before.txt` | Store old-token baseline. |
| Legacy scan after | `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/evidence/legacy-scan-after.txt` | Prove active old path absence. |
| Canonical scan | `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/evidence/canonical-scan.txt` | Prove canonical tokens. |
| Route contract proof | `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/evidence/route-contract-proof.txt` | Prove API stability. |
| Example shape proof | `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/evidence/example-shape-proof.txt` | Prove stable examples. |
| Validation output | `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/evidence/validation.txt` | Store validation commands. |
| Review output | `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/generated/11-code-review.md` | Separate review file. |

## Allowlist / Exception Register

- Allowlist Exception: not applicable
- Reason: no allowlist handling is authorized for this bigbang switch.

## Batch Migration Plan

- Batch migration plan: active
- Batch scope:
  - Identify every candidate matching old carriers, old prompt constants, old use cases, old tests, old mocks, examples, and docs.
  - Classify each candidate in the removal audit before editing.
  - Replace active theme astral consumers with the canonical path.
  - Delete candidates classified `historical-facade` or `dead`.
  - Stop on `external-active` or `needs-user-decision` rows.
- Stop condition:
  - Runtime tests, architecture guard, example shape proof, and negative scans all pass.

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| B1 | old carriers | `theme_astral_llm_input_v1` | theme astral runtime | integration and guard tests | `rg` negative scan | unresolved shared consumer |
| B2 | old natal prompt constants | `theme_astral_prompt_v1` | bootstrap consumers | architecture guard tests | `rg` negative scan | external-active candidate |
| B3 | old examples and docs | canonical payload shape | JSON examples and docs | JSON shape checks | example shape proof | missing canonical payload output |

## Expected Files to Modify

Likely files:

- `backend/app/domain/llm/**` - canonical prompt contract, runtime, configuration, and guard ownership.
- `backend/app/domain/astrology/interpretation/**` - canonical theme astral input and material handoff.
- `backend/app/services/llm_generation/natal/**` - route theme astral runtime to the canonical contract.
- `backend/app/ops/llm/bootstrap/**` - remove or replace old active prompt seed surfaces.
- `_condamad/examples/prompt-generation-cartography/**` - update provider payload examples.
- `_condamad/docs/prompt-generation-cartography/**` - update prompt cartography docs.
- `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/evidence/**` - persist required evidence.
- `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/generated/11-code-review.md` - generated review handoff.

Likely tests:

- `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py` - runtime handoff without provider calls.
- `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py` - old-carrier and old-prompt reintroduction guard.
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` - adapt canonical payload coverage.
- `backend/tests/unit/domain/astrology/interpretation/test_interpretation_material_builder.py` - keep material handoff covered.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no migration is authorized.
- `backend/app/infra/db/models/**` - out of scope unless an existing model reference is only a proven stale test fixture.
- `backend/app/infra/db/repositories/**` - out of scope unless CS-365 ownership needs a read-only adapter already present.
- `_condamad/stories/regression-guardrails.md` - out of scope; no registry enrichment is authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

All Python commands must run after `.\.venv\Scripts\Activate.ps1`.
Run backend quality commands from `backend` after activation.

- VC1: `pytest -q tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`
- VC2: `pytest -q tests/architecture/test_theme_astral_prompt_contract_guard.py`
- VC3: `pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- VC4: `pytest -q tests/unit/domain/astrology/interpretation/test_interpretation_material_builder.py`
- VC5: `python -c "from app.main import app; assert isinstance(app.openapi(), dict)"`
- VC6: `python -c "from app.main import app; assert all(getattr(r, 'path', '') for r in app.routes)"`
- VC7: `rg -n "chart_json|natal_data|llm_astrology_input_v1|natal_interpretation_short" app tests`
- VC8: `rg -n "NATAL_SHORT_PROMPT|NATAL_COMPLETE_PROMPT|natal_interpretation_short" app tests`
- VC9: `rg -n "theme_astral_prompt_v1|theme_astral_llm_input_v1|interpretation_material|output_contract" app tests`
- VC10: `rg -n "delivery_profile|astrologer_voice|free|basic|premium|plan" app tests`
- VC11: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/evidence/removal-audit.md').exists()"`
- VC12: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/evidence/validation.txt').exists()"`
- VC13: `python -c "import subprocess; subprocess.run(['git','diff','--quiet','--','../frontend/src','migrations'], check=True)"`
- VC14: `ruff format .`
- VC15: `ruff check .`
- VC16: `pytest -q tests --tb=short`
- VC17: `rg -n "chart_json|natal_data|llm_astrology_input_v1|natal_interpretation_short|NATAL_SHORT_PROMPT|NATAL_COMPLETE_PROMPT" app tests`
- VC18: `rg -n "theme_astral_prompt_v1|theme_astral_llm_input_v1|interpretation_material|delivery_profile|astrologer_voice" app tests`
- VC19: `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`

## Regression Risks

- A stale test or mock could keep validating the old theme astral path.
- A bootstrap seed could continue to register old prompt constants as active runtime truth.
- The provider payload could leak commercial plan labels instead of delivery profile values.
- Examples could drift from runtime payload shape and hide a per-profile schema difference.
- Deleting a shared natal surface without classification could break a non-theme-astral feature.
- Route or OpenAPI changes could appear accidentally during backend-domain cleanup.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.venv` before every Python, Ruff, or Pytest command.
- Add the required French global file comment and French docstrings in new or materially changed Python files.
- Do not make real provider calls.
- Do not modify frontend files, migrations, unrelated features, provider clients, or guardrail registry entries.
- Persist validation output under the CS-367 story evidence folder.

## References

- `_story_briefs/cs-367-bigbang-remplacer-ancien-contrat-prompt-theme-astral-supprimer-legacy.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `.agents/skills/condamad-story-writer/references/removal-story-contract.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/00-story.md`
- `_condamad/stories/CS-366-provider-payload-builder-theme-astral/00-story.md`
- `_condamad/architecture/theme-astral-prompt-contract/**/archi-theme-astral-prompt-contract-v1.md`
- `backend/app/domain/llm/**`
- `backend/app/domain/astrology/interpretation/**`
- `backend/app/services/llm_generation/natal/**`
- `backend/app/ops/llm/bootstrap/**`
- `backend/tests/**`
- `backend/app/tests/**`
- `_condamad/examples/prompt-generation-cartography/**`
- `_condamad/docs/prompt-generation-cartography/**`
