# Story CS-364 definir-persistence-versionnee-contrats-prompt-theme-astral: Define Versioned Theme Astral Prompt Contract Persistence
Status: ready-to-dev

## Trigger / Source

- Mode: Repo-informed story from implementation brief.
- Source brief: `_story_briefs/cs-364-definir-persistence-versionnee-contrats-prompt-theme-astral.md`.
- Source problem: theme astral prompt contracts need versioned DB persistence through existing LLM registry mechanisms.
- Source stakes:
  - User impact: prompt text, output contract, delivery policy, and astrologer/persona choice must change without heavy code edits.
  - Technical risk: a parallel registry or hardcoded prompt contract would duplicate existing LLM persistence surfaces.
  - Closure expectation: persist the versioned `theme_astral` prompt, input, response, delivery, persona, and assembly contracts.
  - Forbidden regression: no provider call, gateway change, frontend change, or new backend root folder.
- Source-alignment review: PASS. Objective, target state, ACs, tasks, evidence, non-goals, and guardrails map to the brief stakes.

## Objective

Define the minimal backend implementation work to persist the versioned `theme_astral` prompt contract family in the existing LLM registry.

The implementation must reuse existing LLM use cases, prompt versions, output schemas, assemblies, personas, execution profiles, and migrations.

## Target State

The backend can store and read the active versioned `theme_astral` prompt contract family:

- `theme_astral_prompt_contract_v1`
- `theme_astral_llm_input_v1`
- `theme_astral_response_contract_v1`
- `delivery_profile` resolved by depth without exposing commercial plan names to the LLM payload.
- `astrologer_voice` or canonical persona links.
- Prompt templates and assemblies associated with the canonical `theme_astral` use case.

Seeds are idempotent, invalid version combinations fail deterministically, and tests prove persistence, active-read selection, and contract coherence.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-364-definir-persistence-versionnee-contrats-prompt-theme-astral.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-364`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/00-story.md` - architecture prerequisite story read.
- Evidence 5: `backend/app/infra/db/models/llm/**` - targeted inspection found LLM assembly, prompt, output schema, persona, and release models.
- Evidence 6: `backend/app/ops/llm/bootstrap/**` - targeted inspection found existing LLM bootstrap seed owners.
- Evidence 7: `backend/app/domain/llm/configuration/**` - targeted inspection found assembly, prompt version, profile, and resolver owners.
- Evidence 8: `backend/migrations/versions/**llm**` - targeted inspection found existing LLM migration history.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - scoped guardrail IDs resolved through `resolve_guardrails.py`.
- Repository structure alert: `_condamad/architecture/theme-astral-prompt-contract/` is absent in this workspace.
- Repository structure alert: implementation must read or create the CS-363 architecture artifact before changing runtime or persistence code.
- Assumption risk: CS-363 may be implemented before this story starts; if the report is still absent, stop and record the missing architecture input.

## Domain Boundary

- Domain: backend-llm-persistence
- In scope:
  - Backend DB model, migration, domain schema, seed, and resolver changes for versioned `theme_astral` prompt contracts.
  - Reuse of existing LLM prompt version, output schema, assembly, persona, execution profile, and release mechanisms.
  - `theme_astral_prompt_contract_v1`, `theme_astral_llm_input_v1`, and `theme_astral_response_contract_v1`.
  - `delivery_profile` persistence and active-read resolution by depth.
  - `astrologer_voice` or canonical persona linkage without factual astrology ownership.
  - Idempotent seeds for prompt templates, output schema, assembly, persona link, and execution profile association.
  - Migration tests, seed tests, active-read tests, and invalid-version tests.
- Out of scope:
  - `interpretation_material` construction, gateway provider changes, provider calls, frontend UI, auth, i18n, styling, and build tooling.
  - New backend root folders, new parallel LLM registry, and guardrail registry maintenance.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
  - No real LLM or provider call.
  - No rewrite of the gateway provider.
  - No hardcoded prompt contract outside existing versioned registry mechanisms.

Named brief primitives in scope:

- `theme_astral_prompt_contract_v1`
- `theme_astral_llm_input_v1`
- `theme_astral_response_contract_v1`
- `delivery_profile`
- `astrologer_voice`
- `persona`
- `prompt templates`
- `assemblies`
- `use cases`
- `prompt versions`
- `output schemas`
- `execution profiles`
- `migrations LLM`
- `seeds idempotents`
- `factory`
- `resolver`
- `runtime`
- `catalog`
- `contract`
- `profile`
- `prompt`
- `DB`
- `migration`

Named brief primitives out of scope:

- `interpretation_material`
- Provider LLM call.
- Frontend runtime or UI.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend LLM persistence contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only versioned `theme_astral` contract persistence and active-read resolution.
  - Reuse existing LLM registry, assembly, prompt, schema, persona, execution profile, and release mechanisms.
  - Add a migration only after proving an existing table or field cannot store the required contract safely.
  - Keep commercial plan names out of provider-visible persisted payloads.
  - Keep astrological truth owned by engine outputs and tables, not by persona or astrologer voice.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the CS-363 architecture report is unavailable or contradicts the brief identifiers.
- Additional validation rules:
  - `theme_astral_prompt_contract_v1`, `theme_astral_llm_input_v1`, and `theme_astral_response_contract_v1` must have stable identifiers.
  - `delivery_profile` must be persisted or resolvable as depth and policy values without exposing commercial plan names.
  - `astrologer_voice` must link to persona-style data and must not own factual astrology.
  - Seeds must be idempotent and must not create duplicate active assemblies or schema versions.
  - Invalid contract, prompt, schema, persona, or profile version combinations must fail deterministically.
  - Any new migration must be minimal and tied to a documented missing field or table.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `AST guard`, loaded config, DB schema, generated manifest, and targeted `pytest` prove active-read behavior. |
| Baseline Snapshot | yes | Before and after DB or manifest artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | DB models, domain schemas, seeds, migrations, and tests need canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this persistence story. |
| Contract Shape | yes | Stable identifiers, JSON fields, and version references define the persisted contract family. |
| Batch Migration | yes | Existing and new persistence surfaces must be migrated in one coherent slice. |
| Reintroduction Guard | yes | Parallel registries, hardcoded prompt contracts, and plan leakage must stay absent. |
| Persistent Evidence | yes | Migration, seed, active-read, scan, and validation outputs must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Stable identifiers are persisted. | Evidence profile: json_contract_shape; `pytest -q tests/integration/test_theme_astral_prompt_contract_persistence.py`. |
| AC2 | Active-read returns the canonical family. | Evidence profile: ast_architecture_guard; `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py`. |
| AC3 | Prompt templates use versioned registry storage. | Evidence profile: targeted_forbidden_symbol_scan; `pytest`; `rg` checks prompt owners. |
| AC4 | Delivery profile hides plan names. | Evidence profile: targeted_forbidden_symbol_scan; `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py`. |
| AC5 | Astrologer voice links to persona style. | Evidence profile: json_contract_shape; `pytest -q tests/integration/test_theme_astral_prompt_contract_persistence.py`. |
| AC6 | Seeds are idempotent. | Evidence profile: json_contract_shape; `pytest -q tests/integration/test_theme_astral_prompt_contract_persistence.py`. |
| AC7 | Invalid version combinations fail. | Evidence profile: json_contract_shape; `pytest -q tests/integration/test_theme_astral_prompt_contract_persistence.py`. |
| AC8 | Migration state matches ORM metadata. | Evidence profile: baseline_before_after_diff; `backend/tests/integration/test_theme_astral_prompt_contract_migration.py`. |
| AC9 | No parallel registry is introduced. | Evidence profile: repo_wide_negative_scan; `rg` checks bounded backend LLM paths. |
| AC10 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks evidence paths. |

## Implementation Tasks

- [ ] Task 1: Read CS-363 architecture output and record a blocker when it is absent or contradictory. (AC: AC1)
- [ ] Task 2: Map each named contract primitive to existing LLM registry owners before editing code. (AC: AC1, AC9)
- [ ] Task 3: Add minimal domain or Pydantic schema objects for the versioned `theme_astral` contract family. (AC: AC1, AC7)
- [ ] Task 4: Add a minimal Alembic migration only for missing fields or tables proven by the owner map. (AC: AC8)
- [ ] Task 5: Add idempotent seeds for use case, prompt versions, output schema, assembly, persona link, and profile association. (AC: AC3, AC6)
- [ ] Task 6: Wire active-read resolution through existing LLM configuration services. (AC: AC2, AC4, AC5)
- [ ] Task 7: Add invalid-version validation for contract, prompt, schema, persona, and profile combinations. (AC: AC7)
- [ ] Task 8: Add targeted integration and migration tests for persistence, readback, seeds, and invalid versions. (AC: AC1, AC2, AC6, AC8)
- [ ] Task 9: Persist evidence artifacts and validation outputs under the CS-364 story folder. (AC: AC10)
- [ ] Task 10: Run bounded scans proving no parallel registry, prompt hardcoding, or commercial plan leakage was introduced. (AC: AC4, AC9)

## Files to Inspect First

- `_story_briefs/cs-364-definir-persistence-versionnee-contrats-prompt-theme-astral.md` - source scope.
- `_condamad/architecture/theme-astral-prompt-contract/**/archi-theme-astral-prompt-contract-v1.md` - architecture prerequisite.
- `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/00-story.md` - fallback prerequisite story.
- `backend/app/infra/db/models/llm/llm_assembly.py` - assembly persistence owner.
- `backend/app/infra/db/models/llm/llm_prompt.py` - prompt and use case persistence owner.
- `backend/app/infra/db/models/llm/llm_output_schema.py` - output schema persistence owner.
- `backend/app/infra/db/models/llm/llm_persona.py` - persona and astrologer voice persistence owner.
- `backend/app/infra/db/models/llm/llm_execution_profile.py` - execution profile persistence owner.
- `backend/app/infra/db/models/llm/llm_release.py` - release manifest persistence owner.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - canonical use case owner.
- `backend/app/domain/llm/configuration/assembly_resolver.py` - assembly and persona resolution owner.
- `backend/app/domain/llm/configuration/prompt_versions.py` - prompt version owner.
- `backend/app/domain/llm/configuration/execution_profile_registry.py` - execution profile registry owner.
- `backend/app/ops/llm/bootstrap/use_cases_seed.py` - use case and schema seed owner.
- `backend/app/ops/llm/bootstrap/seed_horoscope_narrator_assembly.py` - assembly seed pattern owner.
- `backend/migrations/versions/**llm**` - existing LLM migration history.
- `backend/tests/integration/test_llm_db_invariants.py` - DB invariant pattern.
- `backend/tests/integration/test_llm_governance_registry.py` - registry validation pattern.
- `backend/tests/integration/test_admin_llm_catalog.py` - catalog readback pattern.

## Runtime Source of Truth

- Primary source of truth:
  - CS-363 architecture report or explicit blocker artifact.
  - Loaded config and DB schema checks for the active `theme_astral` contract family.
  - Targeted `pytest -q tests/integration/test_theme_astral_prompt_contract_persistence.py`.
  - Targeted `pytest -q tests/integration/test_theme_astral_prompt_contract_migration.py`.
  - `AST guard` over backend LLM owner paths for schema, seed, resolver, and registry placement.
- Secondary evidence:
  - Bounded `rg` scans for contract identifiers, prompt hardcoding, commercial plan leakage, and parallel registry naming.
  - Generated manifest or seed report persisted under the CS-364 evidence folder.
- Static scans alone are not sufficient for this story because:
  - Persistence, active-read selection, seed idempotency, and invalid-version failures require runtime DB-backed tests.

## Contract Shape

- Contract type:
  - Versioned backend LLM persistence contract for `theme_astral`.
- Fields:
  - `theme_astral_prompt_contract_v1`: stable prompt contract identifier.
  - `theme_astral_llm_input_v1`: stable input contract identifier.
  - `theme_astral_response_contract_v1`: stable output contract identifier.
  - `delivery_profile`: depth, selection, length, and policy values visible to LLM.
  - `astrologer_voice`: persona-linked style, tone, vocabulary, and emphases.
  - `prompt_template_ref`: versioned prompt template reference.
  - `assembly_ref`: canonical assembly reference.
  - `output_schema_ref`: versioned output schema reference.
  - `execution_profile_ref`: canonical execution profile reference.
  - `active_from`: activation timestamp or release marker.
  - `status`: active, inactive, or draft state from existing registry vocabulary.
- Required fields:
  - `theme_astral_prompt_contract_v1`
  - `theme_astral_llm_input_v1`
  - `theme_astral_response_contract_v1`
  - `delivery_profile`
  - `prompt_template_ref`
  - `assembly_ref`
  - `output_schema_ref`
  - `execution_profile_ref`
- Optional fields:
  - `astrologer_voice`
  - `persona_ref`
- Status codes:
  - none; no API route is created or changed.
- Serialization names:
  - Persisted identifiers and JSON keys are emitted exactly as listed in Fields.
- Frontend type impact:
  - none.
- Generated contract impact:
  - generated manifest or seed report must expose the active contract family for review.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/evidence/baseline-llm-contracts.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/evidence/theme-astral-contract-manifest.json`
- Expected invariant:
  - The only intended backend surface delta is versioned `theme_astral` LLM persistence, seeds, schema, migration, and targeted tests.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| DB table or field mapping | `backend/app/infra/db/models/llm/**` | new backend root folder |
| Migration | `backend/migrations/versions/**` | seed-only runtime mutation |
| Domain contract schema | `backend/app/domain/llm/configuration/**` | API router module |
| Prompt contract seed | `backend/app/ops/llm/bootstrap/**` | provider gateway |
| Active assembly resolution | `backend/app/domain/llm/configuration/**` | prompt template text |
| Integration tests | `backend/tests/integration/**` | frontend tests |
| Evidence artifacts | `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/evidence/` | backend app code |

## Mandatory Reuse / DRY Constraints

- Reuse existing LLM assembly, prompt version, persona, output schema, execution profile, and release concepts.
- Reuse existing seed patterns under `backend/app/ops/llm/bootstrap/**`.
- Reuse existing LLM integration test patterns before adding new helpers.
- Reuse existing migration naming and SQLAlchemy model conventions.
- Do not duplicate registry tables when an existing table can store the contract safely.
- Do not hardcode prompt text, response schema, delivery profile, or persona links outside versioned registry or seed data.
- Do not introduce new dependencies.

## No Legacy / Forbidden Paths

- No legacy prompt contract path may be kept as the active theme astral target.
- No compatibility registry may be added for this contract family.
- No fallback registry may be added for this contract family.
- No new backend root folder may be added.
- No parallel LLM registry may be introduced outside the existing LLM persistence mechanisms.
- No provider gateway call may be added.
- No commercial plan name may be stored as LLM-visible prompt payload policy.
- No persona or astrologer voice may own astrological truth.

## Reintroduction Guard

- Forbid new tables or files named as a second prompt registry unless the owner map proves an existing model cannot support the contract.
- Require bounded `rg` scans for `theme_astral_prompt_contract`, `theme_astral_llm_input`, and `theme_astral_response_contract`.
- Require bounded `rg` scans proving `free`, `basic`, and `premium` are not emitted in LLM-visible delivery payloads.
- Require tests that seed twice and prove the active assembly, schema, prompt, persona, and profile records are not duplicated.
- Require tests that load the active contract family from DB rather than from a hardcoded runtime constant.

## Regression Guardrails

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend API routes remain outside this persistence slice. | `rg` source trace; targeted tests. |
| RG-022 `align-prompt-generation-story-validation-paths` | Prompt-generation validations must target collected pytest paths. | `pytest` targeted paths. |
| Registry gap | No exact guardrail covers theme astral versioned LLM contract persistence. | Resolver output saved in evidence. |

Non-applicable examples:

- `RG-047` frontend inline styles is out of scope because no frontend source is touched.
- `RG-052` frontend CSS namespace migration is out of scope because no style source is touched.
- `RG-041` entitlement documentation is out of scope because no entitlement surface is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline contracts | `evidence/baseline-llm-contracts.txt` | Prove starting LLM persistence state. |
| Owner map | `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/evidence/owner-map.md` | Map every primitive to canonical files. |
| Contract manifest | `evidence/theme-astral-contract-manifest.json` | Show active persisted contract family. |
| Seed idempotency | `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/evidence/seed-idempotency.txt` | Store repeat seed proof. |
| Migration check | `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/evidence/migration-check.txt` | Store DB schema validation. |
| Validation output | `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/evidence/validation.txt` | Store validation commands. |
| Review output | `generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist Exception: not applicable
- Reason: no allowlist handling is authorized for this backend persistence story.

## Batch Migration Plan

- Batch migration plan: required
- Reason: versioned contract persistence may require minimal schema and seed updates that must land coherently.

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| CS-364 | Missing contract records | Existing LLM registry | LLM resolver | Integration tests | `rg` backend LLM scan | CS-363 report missing |
| CS-364 | Missing output schema version | `llm_output_schemas` | Active-read path | Migration tests | DB schema check | Schema gap unresolved |
| CS-364 | Missing delivery profile mapping | Execution profile or assembly policy owner | Contract resolver | Seed tests | Plan leakage scan | Policy owner unresolved |
| CS-364 | Missing astrologer voice link | Persona or assembly persona reference | Assembly readback | Persona link tests | Voice truth scan | Persona owner unresolved |

- Stop condition:
  - Active DB-backed read returns the canonical `theme_astral` contract family and invalid version combinations fail deterministically.

## Expected Files to Modify

Likely files:

- `backend/app/infra/db/models/llm/**` - add or adapt minimal LLM persistence fields only when the owner map proves a gap.
- `backend/migrations/versions/**` - add one minimal Alembic migration only when schema support is missing.
- `backend/app/domain/llm/configuration/**` - add schema and active-read resolver logic for the contract family.
- `backend/app/ops/llm/bootstrap/**` - add idempotent seed data for prompt, schema, assembly, persona, and profile associations.
- `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/evidence/**` - persist required evidence artifacts.
- `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/generated/11-code-review.md` - generated review handoff.

Likely tests:

- `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py` - persistence, readback, idempotency, and invalid versions.
- `backend/tests/integration/test_theme_astral_prompt_contract_migration.py` - migration and ORM metadata coherence.
- `backend/tests/integration/test_llm_db_invariants.py` - extend shared LLM DB invariants only for reusable checks.
- `backend/tests/integration/test_llm_governance_registry.py` - extend registry coherence only for reusable checks.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no API route is created or changed.
- `backend/app/domain/astrology/**` - out of scope; this story does not construct `interpretation_material`.
- `backend/app/domain/llm/runtime/gateway.py` - out of scope; no provider gateway change is authorized.
- `_condamad/stories/regression-guardrails.md` - out of scope; no registry enrichment is authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

All Python commands must run after `.\.venv\Scripts\Activate.ps1`.
Run backend quality commands from `backend` after activation.
Run VC5 from `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral`.

- VC1: `pytest -q tests/integration/test_theme_astral_prompt_contract_persistence.py`
- VC2: `pytest -q tests/integration/test_theme_astral_prompt_contract_migration.py`
- VC3: `pytest -q tests/integration/test_llm_db_invariants.py`
- VC4: `pytest -q tests/integration/test_llm_governance_registry.py`
- VC5: `python -c "from pathlib import Path; assert Path('evidence/theme-astral-contract-manifest.json').exists()"`
- VC6: `rg -n "theme_astral_prompt_contract|theme_astral_llm_input|theme_astral_response_contract" backend/app backend/tests backend/migrations`
- VC7: `rg -n "delivery_profile|astrologer_voice|persona_ref|execution_profile_ref" backend/app backend/tests backend/migrations`
- VC8: `rg -n "free|basic|premium" backend/app backend/tests backend/migrations`
- VC9: `ruff format .`
- VC10: `ruff check .`
- VC11: `pytest -q tests --tb=short`

## Regression Risks

- A new table could duplicate existing LLM registry mechanisms instead of extending the canonical model.
- Prompt text or output schema could be hardcoded in runtime code instead of versioned seed or registry data.
- Commercial plan names could leak into provider-visible `delivery_profile` data.
- Persona or astrologer voice could start owning factual astrology instead of style.
- Seeds could create duplicate active prompt, schema, assembly, persona, or profile records.
- Invalid version combinations could be silently accepted by active-read logic.
- Migration tests could pass on a secondary SQLite file while `horoscope.db` remains inconsistent.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.venv` before every Python, Ruff, or Pytest command.
- Use `backend/pyproject.toml` as the only Python dependency source.
- Do not add a new backend root folder.
- Do not call a real LLM provider.
- Do not modify frontend files, API route files, gateway provider code, or the guardrail registry.
- Persist validation output under the CS-364 story evidence folder.

## References

- `_story_briefs/cs-364-definir-persistence-versionnee-contrats-prompt-theme-astral.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/00-story.md`
- `_condamad/architecture/theme-astral-prompt-contract/**/archi-theme-astral-prompt-contract-v1.md`
- `backend/app/infra/db/models/llm/**`
- `backend/migrations/versions/**`
- `backend/app/ops/llm/bootstrap/**`
- `backend/app/domain/llm/configuration/**`
- `backend/tests/**llm**`
