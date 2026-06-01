# Story CS-429 theme-natal-generation-contracts-strict-schemas: Theme Natal Generation Contracts And Strict Schemas
Status: done

## Trigger / Source

Brief direct from `_story_briefs/cs-429-theme-natal-generation-contracts-strict-schemas.md`.
The bounded problem is strict, versioned generation contracts for theme natal LLM outputs.

## Objective

Define distinct backend generation contracts for Free, Basic, and Premium theme natal readings.
Each contract owns its engine, data, prompt, raw output, public projection, persistence trace, and immutable snapshot metadata.

## Target State

- `theme_natal.reading.free_preview.v1` owns the Free preview generation contract.
- `theme_natal.reading.basic_full_reading.v1` owns the Basic full reading generation contract.
- `theme_natal.reading.premium_full_reading.v1` owns the Premium full reading generation contract.
- Every contract defines `engine_profile`, `data_contract`, `prompt_contract`, `output_contract`, and `persistence_contract`.
- Raw provider schemas and public projected schemas are separate for each output variant.
- Every JSON object in raw and public schemas sets `additionalProperties: false` recursively.
- Every generation references an immutable resolved contract snapshot, not a mutable registry object.
- Snapshot metadata is store-ready through version and hash fields named in the brief.

## Brief Primitive Ledger

| Primitive | Source expectation | Story mapping |
|---|---|---|
| `theme_natal.reading.free_preview.v1` | Define Free preview contract. | AC1, Task 1, Contract Shape. |
| `theme_natal.reading.basic_full_reading.v1` | Define Basic full contract. | AC2, Task 1, Contract Shape. |
| `theme_natal.reading.premium_full_reading.v1` | Define Premium full contract. | AC3, Task 1, Contract Shape. |
| `engine_profile` | Contract declares provider runtime profile. | AC4, Task 2. |
| `data_contract` | Contract classifies prompt-visible, validation-only, audit-only data. | AC5, Task 2. |
| `prompt_contract` | Contract pins prompt policy and version. | AC6, Task 2. |
| `output_contract` | Contract separates raw provider schema from public schema. | AC7, AC8, Task 3. |
| `persistence_contract` | Contract exposes store-ready snapshot fields. | AC9, Task 4. |
| Recursive schema strictness | All nested objects forbid unknown fields. | AC8, Task 3. |
| Immutable snapshot | Existing run keeps resolved snapshot after registry mutation. | AC10, Task 5. |
| Basic anti-collision | Basic avoids `AstroResponse_v3`, premium wording, and old natal keys. | AC11, Task 6. |
| Required validations | Preserve backend lint, tests, and scans from the brief. | Validation Plan. |
| Non-goals | Provider call, slot run persistence, API cutover, physical deletion. | Domain Boundary, Batch Migration Plan. |

## Current State Evidence

- Evidence 1: `_story_briefs/cs-429-theme-natal-generation-contracts-strict-schemas.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-429`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted guardrail IDs from the brief were read.
- Evidence 4: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer Mode contract read first.
- Evidence 5: `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - target contract model checked.
- Evidence 6: `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md` - upstream product variants checked.
- Evidence 7: `_story_briefs/cs-428-public-reading-slots-llm-generation-runs.md` - persistence dependency checked.
- Evidence 8: `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - current natal contracts still expose old use-case keys.
- Evidence 9: `backend/app/domain/llm/configuration/theme_astral_contracts.py` - current astral contract pattern checked for reuse.
- Evidence 10: `backend/app/domain/llm/prompting/schemas.py` - current Pydantic strict schema pattern checked.
- Evidence 11: `backend/app/domain/astrology/reading/basic_natal_contracts.py` - Basic public contract boundary checked.
- Source-alignment evidence: objectives, ACs, tasks, non-goals, and validations map to the brief without narrowing the requested contract split.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend generation contract definitions for the three theme natal reading variants.
  - Strict raw provider schemas and public projected schemas for each variant.
  - Contract snapshot hashing and immutable resolved-contract reference behavior.
  - Coherence tests for contract keys, schemas, prompt metadata, and snapshot stability.
- Out of scope:
  - Frontend UI, API cutover, provider calls, database migrations, auth, i18n, styling, build tooling, and physical historical code deletion.
- Explicit non-goals:
  - No real LLM provider request is added.
  - No public endpoint behavior is cut over in this story.
  - No persistence table or Alembic migration is added unless CS-428 is already delivered by implementation time.
  - No frontend route, screen, React state, generated client, or CSS edit is authorized.

Repository structure alert:

- `backend/app/domain/theme_natal` and `backend/tests/unit/domain/theme_natal` do not exist yet.
- Implementation must create those directories and files if the confirmed scope still owns the pure theme natal contract surface.
- This alert is non-blocking while `condamad_story_validate.py` and `condamad_story_lint.py --strict` pass.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only backend contract, schema, snapshot, and tests for theme natal generation.
  - Keep public API behavior unchanged until a later cutover story.
  - Keep provider execution disabled for this story.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-427 contract keys or CS-428 snapshot storage surfaces are unavailable at implementation start.
- Additional validation rules:
  - Runtime evidence must include `pytest -q backend/tests/unit/domain/theme_natal/test_generation_contracts.py`.
  - Runtime evidence must include `pytest -q backend/tests/llm_orchestration/test_theme_natal_generation_contracts.py`.
  - Architecture evidence must include an `AST guard` proving contract modules avoid FastAPI, SQLAlchemy, provider clients, and frontend imports.
  - Schema evidence must include a recursive JSON schema guard for every nested object in raw and public schemas.
  - Snapshot evidence must mutate a registry copy and prove an existing resolved snapshot remains unchanged.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, schema guards, snapshot tests, and `AST guard` prove backend contract behavior. |
| Baseline Snapshot | yes | Before and after artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Generation contracts must stay in backend domain/configuration owners. |
| Allowlist Exception | no | No allowlist handling is authorized for these contracts. |
| Contract Shape | yes | Contract keys, schema fields, versions, hashes, and persistence trace fields are closed. |
| Batch Migration | no | No batch migration or mass persistence conversion is in scope. |
| Reintroduction Guard | yes | Old natal use-case keys and broad schemas must stay out of Basic target contracts. |
| Persistent Evidence | yes | Validation, schema, scan, and snapshot artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Free preview has its own contract. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/theme_natal/test_generation_contracts.py`. |
| AC2 | Basic full has its own contract. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/theme_natal/test_generation_contracts.py`. |
| AC3 | Premium full has its own contract. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/theme_natal/test_generation_contracts.py`. |
| AC4 | Engine profiles are versioned. | Evidence profile: json_contract_shape; `pytest` checks `tests/unit/domain/theme_natal/test_generation_contracts.py`. |
| AC5 | Data visibility classes are explicit. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/theme_natal/test_generation_contracts.py`. |
| AC6 | Prompt contract versions are pinned. | Evidence profile: json_contract_shape; `pytest` checks `tests/unit/domain/theme_natal/test_generation_contracts.py`. |
| AC7 | Raw schemas differ from public schemas. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/theme_natal/test_generation_contracts.py`. |
| AC8 | Unknown fields are recursively rejected. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_theme_natal_generation_contracts.py`. |
| AC9 | Snapshot metadata is store-ready. | Evidence profile: json_contract_shape; `pytest` checks `tests/unit/domain/theme_natal/test_generation_contracts.py`. |
| AC10 | Resolved snapshots stay immutable. | Evidence profile: baseline_before_after_diff; `pytest -q backend/tests/llm_orchestration/test_theme_natal_generation_contracts.py`. |
| AC11 | Basic avoids old schema keys. | Evidence profile: targeted_forbidden_symbol_scan; `pytest -q backend/tests/llm_orchestration/test_theme_natal_generation_contracts.py`. |
| AC12 | Contract modules stay pure. | Evidence profile: ast_architecture_guard; `python` AST guard; `pytest` covers architecture checks. |
| AC13 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks evidence artifact paths. |

## Implementation Tasks

- [ ] Task 1: Add closed contract identities for Free preview, Basic full, and Premium full. (AC: AC1, AC2, AC3)
- [ ] Task 2: Define versioned engine, data, prompt, output, and persistence contract sections. (AC: AC4, AC5, AC6, AC9)
- [ ] Task 3: Define strict raw provider schemas and public projected schemas for each variant. (AC: AC7, AC8)
- [ ] Task 4: Add snapshot metadata fields and deterministic contract hash calculation. (AC: AC9, AC10)
- [ ] Task 5: Add tests proving resolved snapshots do not change after registry mutation. (AC: AC10)
- [ ] Task 6: Add Basic anti-collision tests and scans for old schema or prompt tokens. (AC: AC11)
- [ ] Task 7: Add an AST architecture guard for contract module purity. (AC: AC12)
- [ ] Task 8: Persist before, after, validation, schema, and scan artifacts under the story evidence directory. (AC: AC13)

## Files to Inspect First

- `_story_briefs/cs-429-theme-natal-generation-contracts-strict-schemas.md` - source contract.
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - target architecture and examples.
- `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md` - product variant dependency.
- `_story_briefs/cs-428-public-reading-slots-llm-generation-runs.md` - persistence and snapshot dependency.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - current canonical use-case registry.
- `backend/app/domain/llm/configuration/theme_astral_contracts.py` - reusable contract-family shape.
- `backend/app/domain/llm/prompting/schemas.py` - current strict Pydantic response schema pattern.
- `backend/app/domain/astrology/reading/basic_natal_contracts.py` - Basic public schema boundary.
- `backend/app/domain/theme_natal` - expected implementation-created path for pure theme natal contract ownership.
- `backend/tests/unit/domain/theme_natal` - expected implementation-created path for contract unit tests.
- `backend/tests/llm_orchestration` - expected owner for orchestration and snapshot behavior tests.

## Runtime Source of Truth

- Primary source of truth:
  - `pytest -q backend/tests/unit/domain/theme_natal/test_generation_contracts.py`.
  - `pytest -q backend/tests/llm_orchestration/test_theme_natal_generation_contracts.py`.
  - `AST guard` for imports in `backend/app/domain/theme_natal`.
- Secondary evidence:
  - Targeted `rg` scans for contract keys, hash fields, strict schema markers, and old Basic tokens.
- Static scans alone are not sufficient for this story because:
  - Snapshot immutability and recursive schema rejection must be proven by executable tests.

## Contract Shape

- Contract type:
  - Pure backend generation contract and strict JSON schema family.
- Fields:
  - `generation_contract_key`: one of the three theme natal reading contract keys.
  - `generation_contract_version`: contract semantic version string.
  - `generation_contract_snapshot_id`: immutable resolved contract snapshot identifier.
  - `generation_contract_hash`: deterministic hash of the resolved contract content.
  - `prompt_contract_version`: prompt contract version stored with the snapshot.
  - `output_schema_version`: raw and public output schema version stored with the snapshot.
  - `data_contract_version`: prompt-visible, validation-only, and audit-only data contract version.
  - `engine_profile_version`: provider runtime profile version.
  - `engine_profile`: model, provider, runtime parameters, and safety profile.
  - `data_contract`: prompt-visible, validation-only, and audit-only data visibility sections.
  - `prompt_contract`: prompt references, style references, safety policy, and forbidden content profile.
  - `output_contract`: raw provider schema, public projected schema, and projection policy.
  - `persistence_contract`: snapshot and audit fields required by later storage.
- Required fields:
  - All fields listed in the `Fields` block are required for a resolved contract snapshot.
- Optional fields:
  - none.
- Status codes:
  - No HTTP status code is introduced; this is not an API route story.
- Serialization names:
  - Serialization uses the exact snake_case field names listed in the `Fields` block.
- Frontend type impact:
  - none; frontend generated client changes are out of scope.
- Generated contract impact:
  - No OpenAPI surface changes in this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-429-theme-natal-generation-contracts-strict-schemas/evidence/contracts-before.txt`
  - `_condamad/stories/CS-429-theme-natal-generation-contracts-strict-schemas/evidence/basic-collision-scan-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-429-theme-natal-generation-contracts-strict-schemas/evidence/contracts-after.txt`
  - `_condamad/stories/CS-429-theme-natal-generation-contracts-strict-schemas/evidence/basic-collision-scan-after.txt`
- Expected invariant:
  - The only intended behavior delta is strict backend generation contracts for the three theme natal variants.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Generation contract identities | `backend/app/domain/theme_natal/generation_contracts.py` | `frontend/src/**`, `backend/app/api/**` |
| Strict schema definitions | `backend/app/domain/theme_natal/generation_schemas.py` | `backend/app/services/llm_generation/**` |
| Snapshot hashing | `backend/app/domain/theme_natal/generation_contracts.py` | `backend/app/infra/**` |
| Contract registry wiring | `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | `backend/app/api/**` |
| Contract unit tests | `backend/tests/unit/domain/theme_natal/test_generation_contracts.py` | `frontend/src/**` |
| Snapshot behavior tests | `backend/tests/llm_orchestration/test_theme_natal_generation_contracts.py` | `backend/tests/integration/**` |

## Mandatory Reuse / DRY Constraints

- Reuse the existing canonical registry model instead of adding a parallel registry format.
- Reuse the existing strict Pydantic and JSON schema patterns instead of duplicating hand-built validators.
- Keep variant keys in one backend domain owner.
- Keep hash and snapshot serialization in one pure helper.
- Do not duplicate Basic public privacy denylist logic.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy contract key may be used for new theme natal generation contracts.
- No compatibility contract key may be added for the three target variants.
- No fallback prompt path may own a supported theme natal contract.
- Do not make Basic and Premium share the same raw provider schema or public schema.
- Do not reference `AstroResponse_v3`, `EXIGENCE PREMIUM`, or `natal_interpretation` from the Basic target contract.
- Do not add frontend, API route, DB migration, provider client, or real provider call changes in this story.

## Reintroduction Guard

- Guard target contract keys with:
  - `rg -n "theme_natal\\.reading\\.(free_preview|basic_full_reading|premium_full_reading)\\.v1" backend/app backend/tests`.
- Guard snapshot fields with:
  - `rg -n "generation_contract_snapshot_id|generation_contract_hash|additionalProperties" backend/app backend/tests`.
- Guard Basic anti-collision tokens with:
  - `rg -n "AstroResponse_v3|EXIGENCE PREMIUM|natal_interpretation" backend/app/domain backend/tests/llm_orchestration`.
- Guard contract purity with:
  - `python -B -m pytest -q tests/unit/domain/theme_natal/test_generation_contracts.py --tb=short`.
- Expected result:
  - Contract keys, strict schemas, and snapshot fields appear only in canonical owners, tests, and persisted story evidence.

## Regression Guardrails

| Guardrail | scope -> invariant -> evidence |
|---|---|
| RG-018 | Prompt family -> supported natal contracts avoid prompt fallback ownership -> `rg` and llm orchestration `pytest`. |
| RG-021 | Prompt fallback registry -> remaining fallback keys stay classified -> `pytest` prompt governance evidence. |
| RG-149 | Prompt-generation map -> theme natal contract mapping stays explicit -> `rg` contract key scans. |
| RG-150 | Public boundary -> rejected provider payloads stay non-public -> `pytest` public-boundary evidence. |
| RG-152 | Public schema -> technical trace fields stay out of public output -> schema `pytest` and targeted `rg`. |
| RG-155 | Semantic integrity -> output contracts do not authorize padding -> orchestration `pytest`. |
| RG-164 | Basic contract -> Basic generation stays plan-backed -> unit `pytest`. |
| RG-165 | Basic payload -> Basic prompt data avoids PII, raw scores, and raw IDs -> schema `pytest` and `rg`. |
| RG-168 | Basic public contract -> unknown and technical public fields stay rejected -> unit `pytest`. |
| RG-171 | Basic prompt -> Basic does not route through old natal prompt keys -> orchestration `pytest` and `rg`. |

Needs-investigation:

- `RG-002` and `RG-022` were returned by the resolver, but this story does not touch API routers and uses the brief validations instead.
- `RG-047`, `RG-052`, and `RG-041` are non-applicable examples: no frontend style, CSS namespace, or entitlement documentation edit is in scope.
- Registry gap: no route-specific guardrail is expected because this is a backend contract story, not a public API route story.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation output | `_condamad/stories/CS-429-theme-natal-generation-contracts-strict-schemas/evidence/validation.txt` | Keep final command output. |
| Contract scan output | `_condamad/stories/CS-429-theme-natal-generation-contracts-strict-schemas/evidence/contracts-after.txt` | Prove contract keys. |
| Strict schema output | `_condamad/stories/CS-429-theme-natal-generation-contracts-strict-schemas/evidence/strict-schema-after.txt` | Prove schema strictness. |
| Snapshot output | `_condamad/stories/CS-429-theme-natal-generation-contracts-strict-schemas/evidence/snapshot-after.txt` | Prove immutable snapshots. |
| Basic collision scan | `_condamad/stories/CS-429-theme-natal-generation-contracts-strict-schemas/evidence/basic-collision-scan-after.txt` | Prove Basic isolation. |
| Review output | `_condamad/stories/CS-429-theme-natal-generation-contracts-strict-schemas/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this contract family.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/theme_natal/__init__.py` - expose pure domain symbols.
- `backend/app/domain/theme_natal/generation_contracts.py` - define contract identities, snapshots, hashes, and contract sections.
- `backend/app/domain/theme_natal/generation_schemas.py` - define strict raw provider and public projected schemas.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - register target contracts with canonical output schemas.
- `backend/tests/unit/domain/theme_natal/test_generation_contracts.py` - cover contract shape, hashes, strict schemas, and purity.
- `backend/tests/llm_orchestration/test_theme_natal_generation_contracts.py` - cover snapshot behavior and Basic anti-collision.
- `_condamad/stories/CS-429-theme-natal-generation-contracts-strict-schemas/evidence/contracts-before.txt` - before evidence.
- `_condamad/stories/CS-429-theme-natal-generation-contracts-strict-schemas/evidence/contracts-after.txt` - after evidence.
- `_condamad/stories/CS-429-theme-natal-generation-contracts-strict-schemas/evidence/strict-schema-after.txt` - schema evidence.
- `_condamad/stories/CS-429-theme-natal-generation-contracts-strict-schemas/evidence/snapshot-after.txt` - snapshot evidence.
- `_condamad/stories/CS-429-theme-natal-generation-contracts-strict-schemas/evidence/basic-collision-scan-after.txt` - scan evidence.

Likely tests:

- `backend/tests/unit/domain/theme_natal/test_generation_contracts.py` - contract shape, strict schemas, hashes, and architecture guard.
- `backend/tests/llm_orchestration/test_theme_natal_generation_contracts.py` - snapshot immutability and Basic/Premium collision checks.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no public endpoint cutover is authorized.
- `backend/app/infra/**` - out of scope; no persistence adapter is authorized.
- `backend/alembic/**` - out of scope; no migration is authorized.

## 20. Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: activate venv, then run from `backend`: `ruff format .`.
- VC2: activate venv, then run from `backend`: `ruff check .`.
- VC3: activate venv, then run from `backend`: `python -B -m pytest -q tests/unit tests/llm_orchestration -k "theme_natal or generation_contract or schema" --tb=short`.
- VC4: activate venv, then `python -B -m pytest -q backend/tests/unit/domain/theme_natal/test_generation_contracts.py`.
- VC5: activate venv, then `python -B -m pytest -q backend/tests/llm_orchestration/test_theme_natal_generation_contracts.py`.
- VC6 forbidden pattern: `theme_natal\.reading\.(free_preview|basic_full_reading|premium_full_reading)\.v1`.
- VC6 allowed fixture pattern: canonical contracts, tests, and story evidence.
- VC6 scan roots: `backend/app`, `backend/tests`.
- VC6 command: `rg -n "theme_natal\\.reading\\.(free_preview|basic_full_reading|premium_full_reading)\\.v1" backend/app backend/tests`.
- VC6 expected false positives: none; hits must be canonical owners or tests.
- VC7 forbidden pattern: `generation_contract_snapshot_id|generation_contract_hash|additionalProperties`.
- VC7 allowed fixture pattern: canonical contracts, schema tests, snapshot tests, and story evidence.
- VC7 scan roots: `backend/app`, `backend/tests`.
- VC7 command: `rg -n "generation_contract_snapshot_id|generation_contract_hash|additionalProperties" backend/app backend/tests`.
- VC7 expected false positives: existing strict schema definitions are allowed only when they use `additionalProperties: false`.
- VC8 forbidden pattern: `AstroResponse_v3|EXIGENCE PREMIUM|natal_interpretation`.
- VC8 allowed fixture pattern: tests that assert Basic rejects those tokens and story evidence.
- VC8 scan roots: `backend/app/domain`, `backend/tests/llm_orchestration`.
- VC8 command: `rg -n "AstroResponse_v3|EXIGENCE PREMIUM|natal_interpretation" backend/app/domain backend/tests/llm_orchestration`.
- VC8 expected false positives: old source contracts outside the new theme natal target owner and tests asserting rejection.
- VC9: activate venv, then run an `AST guard` through collected tests to reject FastAPI, SQLAlchemy, provider client, and frontend imports.

## Regression Risks

- CS-427 and CS-428 are currently ready-to-dev prerequisites; implementation must verify delivered surfaces before integration.
- Basic and Premium can accidentally share the same output contract unless tests assert different raw and public schemas.
- A mutable registry object can leak into runs unless snapshot tests mutate the registry copy.
- Basic can regress by referencing old natal prompt keys or premium wording.
- Recursive strictness can be incomplete on nested arrays and object items without a schema traversal test.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all Python commands under `.\.venv\Scripts\Activate.ps1`.
- Keep comments and docstrings in French for new backend application files.
- Keep provider execution, public API cutover, DB migrations, and frontend edits out of the implementation diff.

## References

- `_story_briefs/cs-429-theme-natal-generation-contracts-strict-schemas.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md`
- `_story_briefs/cs-428-public-reading-slots-llm-generation-runs.md`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/app/domain/llm/prompting/schemas.py`
- `backend/app/domain/astrology/reading/basic_natal_contracts.py`
