# Story CS-424 verifier-generation-prompts-basic-natal: Verifier Et Corriger Generation Prompts Basic Natal
Status: ready-to-dev

## Trigger / Source

Brief direct from `_story_briefs/cs-424-verifier-corriger-generation-prompts-basic-natal.md`.

The bounded problem is that CS-416 proves the Basic provider payload is confidential and plan-backed, but it does not prove that the final
`theme_astral_prompt_v1` prompt rendered to the provider tells the model how to turn that payload into a human Basic natal report.

Source-alignment evidence: this story preserves the brief stakes by targeting the final developer prompt, the provider user payload, published assembly
resolution, Basic prompt snapshots, and non-regression against raw carriers without changing API contracts, frontend rendering, or live provider calls.

## Objective

Prove and correct the final Basic natal prompt rendered for `theme_astral_prompt_v1` so it asks for a readable human report, consumes the enriched Basic
payload deliberately, keeps sources as annex material, and blocks mechanical wording or raw internal labels in the main reading.

## Target State

- The final Basic prompt rendered from the published `theme_astral/prompt_contract/expanded` assembly contains explicit Basic editorial instructions.
- The prompt instructs the provider to use `basic_natal_prompt_payload.sections`, `editorial_evidence`, `style_constraints`, `limitations`, and `disclaimers`.
- The prompt asks for an introduction, explanatory themes, a conclusion, and source annexes instead of a source list as main content.
- The prompt blocks observed mechanical phrases and raw English labels from the main reading.
- `LLMGateway.build_user_payload` and `assemble_developer_prompt` evidence prove the active Basic path uses `theme_astral_prompt_v1`.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-424-verifier-corriger-generation-prompts-basic-natal.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-424`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted guardrail IDs resolved for backend LLM Basic prompt scope.
- Evidence 4: `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/basic-payload-after.json` - upstream payload proof read.
- Evidence 5: `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/validation.txt` - upstream validation proof read.
- Evidence 6: `_story_briefs/cs-421-renforcer-contrat-redactionnel-basic-natal.md` - upstream editorial contract brief read.
- Evidence 7: backend roots and all source files named by the brief exist in this workspace.
- Evidence 8: targeted `rg` found `THEME_ASTRAL_PROMPT_TEMPLATE`, `theme_astral_prompt_v1`, `assemble_developer_prompt`, and `build_user_payload`.
- Evidence 9: resolver returned `RG-022` for prompt-generation validation paths; targeted registry search confirmed the brief-specific Basic LLM IDs.

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| `THEME_ASTRAL_PROMPT_TEMPLATE` | in scope | AC1, AC2, AC3, AC4, tasks 1-4, expected files. |
| `theme_astral_prompt_v1` | in scope | AC1, AC7, AC9, AC10, runtime source of truth. |
| `theme_astral/prompt_contract/expanded` Basic assembly | in scope | AC1, AC9, AC10, tasks 1 and 6. |
| `assemble_developer_prompt` | in scope | AC1, AC2, AC3, AC4, AC7, snapshots. |
| `LLMGateway.build_user_payload` | in scope | AC5, AC8, tasks 5 and 8. |
| `basic_natal_prompt_payload` | in scope | AC2, AC5, AC8, RG-164, RG-165. |
| `sections`, `editorial_evidence`, `style_constraints` | in scope | AC2, AC3, AC4, contract shape. |
| `limitations` and `disclaimers` | in scope | AC7, contract shape. |
| prompt snapshots before and after | in scope | AC11, persistent evidence. |
| `natal_interpretation` old prompt path | in scope as forbidden route | AC10, reintroduction guard. |
| free and premium profiles | in scope for non-regression | AC12, validation plan. |
| live provider call | out of scope | non-goals and validation plan. |
| frontend rendering | out of scope | non-goals and files not expected to change. |
| public API contract | out of scope | domain boundary and required contracts. |

## Domain Boundary

- Domain: backend-llm-prompt
- In scope:
  - Backend LLM prompt template, assembly resolution, provider payload handoff, and tests for Basic natal final prompt rendering.
  - Snapshot evidence for final Basic developer prompt and user payload without live provider execution.
  - Routing proof that Basic uses the published `theme_astral_prompt_v1` assembly.
- Out of scope:
  - Frontend UI, database schema, auth, i18n routing, styling, build tooling, migrations, quotas, and public API schema changes.
- Explicit non-goals:
  - No frontend route, screen, CSS, or client generation.
  - No provider live call in automated tests.
  - No change to old prompt families outside proof that the Basic active path does not use them.
  - No competing Basic prompt family.
  - No change to the Basic provider payload except the minimal CS-421-compatible adaptation required by the final prompt proof.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend LLM final prompt rendering contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Update only the Basic final prompt guidance or targeted assembly path required to consume the enriched Basic payload.
  - Keep `theme_astral_prompt_v1` as the canonical published prompt contract.
  - Preserve free and premium handoff contracts for the same prompt family.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the Basic final prompt cannot become readable without creating a competing prompt family.
- Additional validation rules:
  - Runtime evidence must include `pytest -q backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py --tb=short`.
  - Runtime evidence must include `pytest -q backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py --tb=short`.
  - Runtime evidence must include `pytest -q backend/tests/llm_orchestration/test_assembly_resolution.py -k "theme_astral or basic or prompt_contract" --tb=short`.
  - Runtime evidence must include `AST guard`, rendered prompt snapshot, or generated manifest proving the active Basic assembly.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Rendered assembly, `LLMGateway.build_user_payload`, and pytests prove the final prompt path. |
| Baseline Snapshot | yes | Before and after prompt artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Basic guidance must live in payload, delivery profile, or targeted condition rather than a competing prompt family. |
| Allowlist Exception | no | No broad allowlist handling is authorized for this prompt contract. |
| Contract Shape | yes | The prompt must state exact Basic report, source, style, safety, and carrier rules. |
| Batch Migration | no | No batch migration or historical regeneration is in scope. |
| Reintroduction Guard | yes | Old prompt paths and raw carriers must stay out of the active Basic final prompt path. |
| Persistent Evidence | yes | Prompt snapshots, user payload snapshot, scans, and validation output must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Basic final prompt renders from the published assembly. | `pytest -q backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py --tb=short`. |
| AC2 | Basic final prompt tells how to use enriched payload sections. | `pytest -q backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py --tb=short`. |
| AC3 | Basic final prompt asks for a human report. | `pytest -q backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py --tb=short`. |
| AC4 | Basic final prompt imposes source annex usage. | `pytest -q backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py --tb=short`. |
| AC5 | User payload keeps Basic enriched data private. | `pytest -q backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py --tb=short`. |
| AC6 | Baseline mechanical phrases are blocked. | `pytest -q backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py --tb=short`; `rg` denylist. |
| AC7 | Safety constraints stay explicit in the final prompt. | `pytest -q backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py --tb=short`. |
| AC8 | Forbidden carriers stay absent from final prompt. | `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py --tb=short`; `rg` scan. |
| AC9 | Published assemblies stay unique by depth. | `pytest -q backend/tests/llm_orchestration/test_assembly_resolution.py`. |
| AC10 | Basic active path does not use old prompt keys. | `pytest -q backend/tests/llm_orchestration/test_assembly_resolution.py`. |
| AC11 | Prompt evidence artifacts are persisted. | `python -B -c` checks story evidence paths. |
| AC12 | Non-Basic handoff contracts remain unchanged. | `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py --tb=short`. |
| AC13 | Durable Basic final-prompt guard creates `RG-171`. | Targeted `Select-String` or `rg` evidence on `RG-171`. |

## Implementation Tasks

- [ ] Task 1: Render the current Basic final prompt from `theme_astral/prompt_contract/expanded` and persist the before snapshot. (AC: AC1, AC11)
- [ ] Task 2: Add tests proving the rendered Basic prompt consumes `basic_natal_prompt_payload` editorial fields. (AC: AC2, AC3, AC4)
- [ ] Task 3: Update `THEME_ASTRAL_PROMPT_TEMPLATE` or targeted assembly guidance to instruct the Basic report shape. (AC: AC2, AC3, AC4)
- [ ] Task 4: Keep Basic-specific rules targeted through payload, delivery profile, or an explicit Basic condition. (AC: AC2, AC12)
- [ ] Task 5: Extend handoff tests for final prompt plus `LLMGateway.build_user_payload` without live provider calls. (AC: AC5, AC8)
- [ ] Task 6: Add routing proof that Basic uses `theme_astral_prompt_v1` instead of old prompt keys. (AC: AC9, AC10)
- [ ] Task 7: Persist after snapshots for final prompt, user payload, scans, and validation output. (AC: AC11)
- [ ] Task 8: Run regression tests for Basic and non-Basic handoff contracts. (AC: AC8, AC12)
- [ ] Task 9: Add `RG-171` to the guardrail registry when the durable final-prompt guard is implemented. (AC: AC13)

## Files to Inspect First

- `_story_briefs/cs-424-verifier-corriger-generation-prompts-basic-natal.md`
- `_story_briefs/cs-421-renforcer-contrat-redactionnel-basic-natal.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/basic-payload-after.json`
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/validation.txt`
- `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`
- `backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `backend/tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py`
- `backend/tests/llm_orchestration/test_assembly_resolution.py`

## Runtime Source of Truth

- Primary source of truth:
  - `assemble_developer_prompt`, `LLMGateway.build_user_payload`, published assembly records, `AST guard`, and generated prompt manifest.
- Runtime evidence:
  - `pytest -q backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py --tb=short`.
  - `pytest -q backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py --tb=short`.
  - `pytest -q backend/tests/llm_orchestration/test_assembly_resolution.py -k "theme_astral or basic or prompt_contract" --tb=short`.
- Secondary evidence:
  - Rendered prompt snapshots, generated manifest output, and targeted `rg` scans for forbidden carriers or old prompt keys.
- Static scans alone are not sufficient for this story because:
  - The final prompt must be proven from the loaded assembly and provider payload path.

## Contract Shape

- Contract type:
  - Backend LLM developer prompt plus provider user payload handoff.
- Fields:
  - `developer_prompt`: rendered `theme_astral_prompt_v1` instructions for Basic.
  - `input_data.basic_natal_prompt_payload`: enriched Basic material consumed by the final prompt.
  - `delivery_profile`: depth and report constraints used by the final prompt.
  - `output_contract`: response contract that remains unchanged.
- Required fields:
  - `developer_prompt`
  - `input_data.basic_natal_prompt_payload`
  - `delivery_profile`
  - `output_contract`
- Required Basic prompt instructions:
  - Use `basic_natal_prompt_payload.sections` as the report structure.
  - Use `editorial_evidence` as annex source material, not main prose.
  - Respect `style_constraints`, `limitations`, and `disclaimers`.
  - Write an introduction, explanatory themes, and a conclusion.
  - Vulgarize astrology labels in French and avoid raw English labels as main content.
  - Reject mechanical phrases observed in the baseline.
- Required payload checks:
  - `input_data.basic_natal_prompt_payload` remains present for Basic.
  - Raw carriers, PII, scores, paths, internal IDs, and commercial labels remain absent.
- Optional fields:
  - none for the prompt contract proof.
- Status codes:
  - No HTTP status code contract changes are in scope.
- Serialization names:
  - Existing snake_case payload keys stay canonical.
- Frontend type impact:
  - none; frontend rendering is out of scope.
- Generated contract impact:
  - snapshots must show the authorized final prompt and user payload shape.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-424-verifier-generation-prompts-basic-natal/evidence/basic-final-prompt-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-424-verifier-generation-prompts-basic-natal/evidence/basic-final-prompt-after.txt`
  - `_condamad/stories/CS-424-verifier-generation-prompts-basic-natal/evidence/basic-user-payload-after.json`
- Expected invariant:
  - The only intended surface delta is targeted Basic final prompt guidance and proof artifacts for the published assembly.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Prompt seed template | `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py` | New competing Basic prompt family. |
| Prompt contract schema | `backend/app/domain/llm/configuration/theme_astral_contracts.py` | Runtime gateway branching. |
| Published assembly resolution | `backend/app/domain/llm/configuration/assembly_resolver.py` | Old prompt key routing. |
| Provider user payload handoff | `backend/app/domain/llm/runtime/gateway.py` | Tests only or frontend code. |
| Basic payload shape | `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` | Prompt seed owning Basic business rules. |

## Mandatory Reuse / DRY Constraints

- Reuse `theme_astral_prompt_v1`; do not create a second Basic prompt family.
- Reuse the existing assembly resolver and seed bootstrap path.
- Reuse the CS-421 Basic payload editorial fields rather than duplicating Basic rules inside unrelated layers.
- Keep denied phrase patterns in one owned test or contract helper when code needs reuse.
- Keep snapshots generated from runtime assembly rendering, not handcrafted text fixtures.

## No Legacy / Forbidden Paths

- No legacy prompt key may become active for Basic.
- No compatibility prompt key may be added for Basic.
- No fallback prompt path may bypass the published assembly.
- No old `natal_interpretation` or `natal_interpretation_short` prompt may serve the Basic active path.
- No raw `chart_json`, `natal_data`, PII, scores, paths, prompt hints, audit inputs, coordinates, or internal IDs may enter the final Basic prompt or user payload.

## Reintroduction Guard

- Guard old prompt keys with an assembly resolution pytest and a bounded `rg` scan.
- Guard raw carriers with provider payload tests and a bounded `rg` scan.
- Guard mechanical baseline phrases with rendered prompt tests and a bounded `rg` scan.
- Guard Basic prompt targeting by proving the guidance is attached to payload, delivery profile, or explicit Basic condition.

## Regression Guardrails

Scope vector: update, backend-llm-prompt, `theme_astral_prompt_v1`, Basic natal payload, assembly resolver, provider handoff, no raw carriers.

| Guardrail | Scope -> invariant -> evidence |
|---|---|
| RG-018 `block-supported-family-prompt-fallbacks` | Basic prompt path -> no prompt fallback ownership -> assembly pytest plus fallback `rg` scan. |
| RG-021 `classify-converge-remaining-prompt-fallbacks` | Prompt governance -> no unaudited canonical fallback -> assembly pytest plus fallback `rg` scan. |
| RG-022 `align-prompt-generation-story-validation-paths` | Prompt-generation story -> validation paths are collected -> listed `pytest` paths. |
| RG-149 `prompt-generation-current-implementation` | Provider-capable prompt map -> Basic stays classified distinctly -> prompt-generation scan or documented no-change. |
| RG-152 `public-technical-boundary` | Prompt and payload -> no raw technical carriers -> payload pytest plus carrier `rg` scan. |
| RG-155 `semantic-integrity` | Basic final prompt -> no padding or source-list main prose -> rendered prompt pytest. |
| RG-164 `basic-plan-owner` | Basic material -> `BasicNatalReadingPlan` remains owner -> payload builder pytest. |
| RG-165 `basic-payload-privacy` | Basic user payload -> no PII, scores, paths, raw IDs -> payload pytest plus carrier `rg` scan. |
| RG-166 `basic-validation` | Basic draft path -> accepted output remains plan-backed -> upstream validator tests stay green. |
| RG-167 `basic-runtime-engine` | Basic complete -> `basic-natal-reading-v1` remains active -> assembly or pipeline pytest. |
| RG-168 `basic-public-contract` | Public Basic V2 -> canonical contract remains unchanged -> public contract regression tests. |

Needs-investigation: `RG-169` is cited by CS-421 as an implementation-created editorial-quality invariant, but it is not present in the registry.

Registry gap: the brief asks to add future `RG-171` when implementation creates the durable final-prompt invariant; this story requires that registry update.

Non-applicable examples:

- RG-047 is frontend inline-style-focused; this story does not touch TSX or CSS.
- RG-052 is frontend CSS-migration-focused; this story does not touch style assets.
- RG-002 is backend API-route-focused; this story does not change route registration.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Prompt baseline | `_condamad/stories/CS-424-verifier-generation-prompts-basic-natal/evidence/basic-final-prompt-before.txt` | Capture current Basic final prompt. |
| Prompt after | `_condamad/stories/CS-424-verifier-generation-prompts-basic-natal/evidence/basic-final-prompt-after.txt` | Prove authorized prompt guidance. |
| User payload after | `_condamad/stories/CS-424-verifier-generation-prompts-basic-natal/evidence/basic-user-payload-after.json` | Prove provider handoff shape. |
| Scan classification | `_condamad/stories/CS-424-verifier-generation-prompts-basic-natal/evidence/scan-classification.md` | Classify scan hits. |
| Validation output | `_condamad/stories/CS-424-verifier-generation-prompts-basic-natal/evidence/validation.txt` | Keep executed validation proof. |
| Review output | `_condamad/stories/CS-424-verifier-generation-prompts-basic-natal/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no broad allowlist is authorized; scan hits must be classified as tests, guards, historical evidence, or blockers.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py` - adjust the canonical prompt template or targeted Basic section.
- `backend/app/domain/llm/configuration/theme_astral_contracts.py` - update contract tests or schema hooks only for prompt guidance proof.
- `backend/app/domain/llm/configuration/assembly_resolver.py` - inspect or adjust assembly rendering only if the active path misses Basic guidance.
- `backend/app/domain/llm/runtime/gateway.py` - inspect handoff path and add proof only if gateway payload assembly omits required data.
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` - minimal CS-421-compatible payload adaptation only when required.
- `_condamad/stories/CS-424-verifier-generation-prompts-basic-natal/evidence/*.txt` - persist prompt snapshots and validation output.
- `_condamad/stories/CS-424-verifier-generation-prompts-basic-natal/evidence/*.json` - persist user payload snapshot.
- `_condamad/stories/regression-guardrails.md` - add `RG-171` when implementation installs the durable Basic final-prompt guard.

Likely tests:

- `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`
- `backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `backend/tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py`
- `backend/tests/llm_orchestration/test_assembly_resolution.py`

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no public API route is changed.
- `backend/app/infra/**` - out of scope; no persistence or external adapter is touched.
- `backend/alembic/**` - out of scope; no migration is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

All Python commands must run after `.\\.venv\\Scripts\\Activate.ps1`. Backend test commands run from the `backend` directory.

- VC1: from `backend` run `ruff format .`.
- VC2: from `backend` run `ruff check .`.
- VC3: from `backend` run `python -B -m pytest -q tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py --tb=short`.
- VC4: from `backend` run `python -B -m pytest -q tests/integration/llm/test_theme_astral_provider_payload_handoff.py --tb=short`.
- VC5: from `backend` run provider payload pytests:
  `python -B -m pytest -q tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py tests/llm_orchestration/test_theme_astral_provider_payload_builder.py --tb=short`.
- VC6: from `backend` run `python -B -m pytest -q tests/llm_orchestration/test_assembly_resolution.py -k "theme_astral or basic or prompt_contract" --tb=short`.
- VC7: forbidden pattern `PROMPT_FALLBACK_CONFIGS|fallback_target_use_case`;
  allowed fixture pattern `test|denylist|classification`; scan roots `backend/app/domain/llm backend/app/ops/llm backend/tests/llm_orchestration`;
  expected false positives are historical fallback governance tests only.
- VC8: forbidden pattern `chart_json|natal_data|audit_input|ranking_score|weighted_score|condition_axis|prompt_hint|user_id|email|latitude|longitude`;
  allowed fixture pattern `test|denylist|private|audit`;
  scan roots `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py backend/tests/integration/llm backend/tests/llm_orchestration`;
  expected false positives are negative tests, denylist constants, or private audit assertions.
- VC9: forbidden pattern `cette lecture s'appuie uniquement|Ce repere retient|avec une confiance editoriale controlee`;
  allowed fixture pattern `test|denylist|baseline|evidence`; scan roots `backend/app/ops/llm/bootstrap backend/tests/integration/llm backend/tests/llm_orchestration`;
  expected false positives are negative tests or before-snapshot assertions.
- VC10: from repository root run `python -B -c` path checks for `basic-final-prompt-before.txt`, `basic-final-prompt-after.txt`,
  `basic-user-payload-after.json`, and `validation.txt`.
- VC11: targeted registry check proves `RG-171` exists after the durable Basic final-prompt guard is added.

## Regression Risks

- Prompt correction could live only in tests while provider execution still uses a generic template; AC1, AC9, and runtime source checks constrain this.
- Basic guidance could be hardcoded globally and alter free or premium behavior; AC12 and ownership routing constrain this.
- Source annex rules could still let the model list `editorial_evidence` as main prose; AC4 and RG-155 constrain this.
- Privacy carriers could reappear through prompt snapshots or user payload rendering; AC5, AC8, and RG-165 constrain this.
- Old prompt keys could remain in the Basic active path; AC10 and reintroduction guards constrain this.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all new or significantly changed applicative files documented with a French top-of-file comment and French docstrings.
- Do not call a live provider from automated tests.
- Persist before and after artifacts before requesting review.

## References

- `_story_briefs/cs-424-verifier-corriger-generation-prompts-basic-natal.md`
- `_story_briefs/cs-421-renforcer-contrat-redactionnel-basic-natal.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/basic-payload-after.json`
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/validation.txt`
- `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`
- `backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `backend/tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py`
- `backend/tests/llm_orchestration/test_assembly_resolution.py`
