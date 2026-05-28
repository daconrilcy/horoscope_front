# Story CS-366 provider-payload-builder-theme-astral: Implement Stable Theme Astral Provider Payload Builder
Status: ready-to-dev

## Trigger / Source

- Mode: Repo-informed story from implementation brief.
- Source brief: `_story_briefs/cs-366-implementer-provider-payload-builder-theme-astral-stable-par-feature.md`.
- Source problem: `theme_astral` needs one stable provider payload skeleton for `free`, `basic`, and `premium`.
- Source stakes:
  - User impact: generated theme astral text must receive the same contract shape whatever the commercial plan.
  - Technical risk: plan labels, duplicated prompt data, or profile-specific shapes can leak into the LLM handoff.
  - Closure expectation: implement a canonical provider payload builder backed by CS-363, CS-364, and CS-365.
  - Forbidden regression: no provider call, no frontend UI, no DB migration, and no broad old-carrier cleanup in this story.
- Source-alignment review: PASS. Objective, target state, ACs, tasks, evidence, non-goals, and guardrails map to the brief stakes.

## Objective

Implement the canonical `theme_astral` provider payload builder.

The builder must assemble one stable JSON skeleton from runtime contract data, safety rules, astrologer voice, feature context,
resolved `delivery_profile`, calculated input data, sourced `interpretation_material`, and versioned `output_contract`.

## Target State

The backend can build a provider payload for `theme_astral` with the same top-level keys for `free`, `basic`, and `premium`:

- `runtime_contract`
- `safety_contract`
- `astrologer_voice`
- `feature_context`
- `delivery_profile`
- `input_data`
- `output_contract`

The nested `input_data` keys are stable:

- `birth_context`
- `astrological_facts`
- `interpretation_material`
- `selected_themes`
- `limits`

Commercial plan remains a backend-only input. The LLM receives `delivery_profile` values and never receives `plan`, `free`,
`basic`, or `premium` as commercial labels.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-366-implementer-provider-payload-builder-theme-astral-stable-par-feature.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-366`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/00-story.md` - architecture story read.
- Evidence 5: `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/00-story.md` - persistence story read.
- Evidence 6: `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/00-story.md` - material builder story read.
- Evidence 7: `backend/app/domain/llm/runtime/gateway.py` and `backend/app/domain/llm/runtime/contracts.py` - runtime handoff owners read.
- Evidence 8: targeted `rg` checked `theme_astral`, payload contract, delivery, voice, material, and output terms in backend paths.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - scoped guardrails resolved with `resolve_guardrails.py`.
- Repository structure alert: none. `backend`, `backend/app`, and `backend/tests` exist.
- Repository structure alert: `_condamad/architecture/theme-astral-prompt-contract/**/archi-theme-astral-prompt-contract-v1.md` is absent.
- Assumption risk: CS-363, CS-364, and CS-365 may be implemented before this story starts; blockers must cite missing deliverables.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend provider payload builder for `theme_astral`.
  - Runtime assembly from CS-363 stable skeleton and CS-364 versioned contract family.
  - Reuse of CS-365 `interpretation_material` builder output.
  - Mapping backend commercial plan to `delivery_profile` without LLM-visible commercial labels.
  - Injecting `astrologer_voice` as style, tone, vocabulary, and emphases.
  - Injecting astrological facts from engine outputs and interpretation material from audited owners.
  - Emitting explicit versioned `output_contract`.
  - Unit and integration tests for shape, profile values, non-exposure, voice, material, and handoff.
- Out of scope:
  - Frontend UI, auth, i18n, styling, build tooling, DB migrations, provider LLM calls, and global old-carrier cleanup.
  - Source text table changes, prompt prose rewrite, output schema persistence changes, and guardrail registry maintenance.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
  - No real LLM or provider call.
  - No DB model or Alembic migration change.
  - No global cleanup of old prompt carrier surfaces.

Named brief primitives in scope:

- `runtime_contract`
- `safety_contract`
- `astrologer_voice`
- `feature_context`
- `delivery_profile`
- `input_data`
- `birth_context`
- `astrological_facts`
- `interpretation_material`
- `selected_themes`
- `limits`
- `output_contract`
- `free`
- `basic`
- `premium`
- `factory`
- `resolver`
- `runtime`
- `catalog`
- `contract`
- `profile`
- `prompt`
- `renderer`

Named brief primitives out of scope:

- Provider LLM call.
- Frontend UI.
- DB migration.
- Source text table edits.
- Global old-carrier cleanup.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend provider payload builder contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the canonical `theme_astral` provider payload builder, resolver wiring, and tests.
  - Preserve one skeleton for `free`, `basic`, and `premium`.
  - Keep commercial plan labels outside the provider-visible payload.
  - Reuse CS-365 interpretation material instead of reconstructing sourced material in the payload builder.
  - Keep astrological truth owned by engine outputs and tables, not by astrologer voice.
  - Keep developer prompt and user payload data non-duplicated.
  - Keep provider gateway calls, DB schema, frontend, and source text tables unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-363, CS-364, or CS-365 deliverables are missing or contradict the provider skeleton.
- Additional validation rules:
  - `AST guard` must prove the builder has one canonical owner and no parallel profile-specific builder.
  - A full `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` path must prove payload shape.
  - A full `pytest -q backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py` path must prove handoff behavior.
  - Tests must prove `free`, `basic`, and `premium` share identical top-level and `input_data` keys.
  - Tests must prove commercial labels are absent from provider-visible payload content.
  - Tests must prove `delivery_profile`, `interpretation_material`, `astrologer_voice`, and `output_contract` are present.
  - Tests must prove quantity budgets vary by resolved delivery profile without changing the skeleton.
  - Targeted `rg` must prove no duplicate material block is copied into both developer prompt and user payload.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `AST guard`, full `pytest` paths, loaded resolver, and gateway handoff prove runtime payload behavior. |
| Baseline Snapshot | yes | Before and after payload artifacts prove the only allowed surface delta is the provider payload builder. |
| Ownership Routing | yes | Builder, resolver, gateway handoff, astrology input, and tests need canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this provider payload story. |
| Contract Shape | yes | The provider payload has exact top-level, nested input, profile, voice, material, and output fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Commercial labels, duplicate prompt data, and profile-specific key sets must stay absent. |
| Persistent Evidence | yes | Payload snapshots, scans, validation output, and review handoff must persist. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The builder has one canonical owner. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks builder ownership. |
| AC2 | Top-level payload keys are stable. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`. |
| AC3 | `input_data` keys are stable. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`. |
| AC4 | Commercial labels stay hidden. | Evidence profile: targeted_forbidden_symbol_scan; `pytest`; `rg` checks provider payload outputs. |
| AC5 | `delivery_profile` is emitted. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`. |
| AC6 | `interpretation_material` is emitted. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`. |
| AC7 | Profile quantities vary. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`. |
| AC8 | Voice changes style fields only. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`. |
| AC9 | Truth data stays engine-owned. | Evidence profile: ast_architecture_guard; `AST guard`; `pytest` checks fact sources. |
| AC10 | `output_contract` is versioned. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`. |
| AC11 | Handoff uses the built payload. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`. |
| AC12 | Prompt data is not duplicated. | Evidence profile: targeted_forbidden_symbol_scan; `pytest`; `rg` checks developer prompt and user payload builders. |
| AC13 | Protected surfaces stay unchanged. | Evidence profile: repo_wide_negative_scan; `python` checks bounded git diff. |
| AC14 | Story evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks evidence and generated paths. |

## Implementation Tasks

- [ ] Task 1: Read CS-363, CS-364, and CS-365 deliverables or record exact blocker evidence. (AC: AC1, AC14)
- [ ] Task 2: Map the provider payload builder to one canonical backend owner before editing code. (AC: AC1)
- [ ] Task 3: Define the stable payload contract with the exact top-level and `input_data` skeleton. (AC: AC2, AC3)
- [ ] Task 4: Resolve backend plan into `delivery_profile` values without emitting commercial labels. (AC: AC4, AC5, AC7)
- [ ] Task 5: Inject CS-365 `interpretation_material` into `input_data` without rebuilding sourced material. (AC: AC6, AC9)
- [ ] Task 6: Inject `astrologer_voice` as style, tone, vocabulary, and emphases only. (AC: AC8, AC9)
- [ ] Task 7: Inject engine-owned birth context, astrological facts, selected themes, and limits. (AC: AC3, AC9)
- [ ] Task 8: Emit explicit versioned `output_contract` from the canonical contract family. (AC: AC10)
- [ ] Task 9: Wire the built payload into the runtime handoff without provider calls. (AC: AC11)
- [ ] Task 10: Add tests comparing `free`, `basic`, and `premium` skeletons and value budgets. (AC: AC2, AC3, AC7)
- [ ] Task 11: Add tests and scans proving commercial labels and duplicate prompt data are absent. (AC: AC4, AC12)
- [ ] Task 12: Run validation commands, persist output, and prove protected surfaces stay unchanged. (AC: AC13, AC14)

## Files to Inspect First

- `_story_briefs/cs-366-implementer-provider-payload-builder-theme-astral-stable-par-feature.md` - source scope.
- `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/00-story.md` - architecture prerequisite.
- `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/00-story.md` - persistence prerequisite.
- `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/00-story.md` - material prerequisite.
- `_condamad/architecture/theme-astral-prompt-contract/**/archi-theme-astral-prompt-contract-v1.md` - expected architecture deliverable.
- `backend/app/domain/llm/runtime/gateway.py` - runtime handoff owner.
- `backend/app/domain/llm/runtime/contracts.py` - runtime request and plan contracts.
- `backend/app/domain/llm/configuration/**` - assembly, output contract, execution profile, and resolver owners.
- `backend/app/domain/astrology/interpretation/**` - LLM input and interpretation material owners.
- `backend/app/services/llm_generation/natal/**` - natal generation service boundary.
- `backend/tests/llm_orchestration/**` - orchestration test patterns.
- `backend/tests/unit/domain/astrology/**` - astrology material and input tests.
- `backend/tests/integration/llm/**` - LLM integration handoff tests.

## Runtime Source of Truth

- Primary source of truth:
  - Loaded provider payload builder tests under `backend/tests/llm_orchestration`.
  - Integration handoff test `backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`.
  - `AST guard` for builder ownership, runtime wiring, profile mapping, and prompt data placement.
  - Loaded config or resolver check for the active `theme_astral` output contract family.
- Secondary evidence:
  - Targeted `rg` scans for skeleton keys, commercial labels, duplicate prompt data, and protected surfaces.
  - Before and after provider payload snapshots persisted under the CS-366 evidence folder.
- Static scans alone are not sufficient for this story because:
  - Profile value changes, hidden commercial labels, and handoff payload content require loaded builder and integration tests.

## Contract Shape

- Contract type:
  - Backend provider payload mapping for `theme_astral`.
- Fields:
  - `runtime_contract`: runtime metadata and contract identifiers needed by the provider handoff.
  - `safety_contract`: safety and non-invention rules.
  - `astrologer_voice`: style, tone, vocabulary, and emphases.
  - `feature_context`: feature, subfeature, locale, and use-case context without commercial labels.
  - `delivery_profile`: resolved density, quantity, budget, section, and length rules.
  - `input_data.birth_context`: normalized birth context.
  - `input_data.astrological_facts`: calculated facts from engine outputs.
  - `input_data.interpretation_material`: sourced material from CS-365 builder output.
  - `input_data.selected_themes`: selected theme identifiers and labels governed by profile values.
  - `input_data.limits`: missing data, unavailable sections, and uncertainty notes.
  - `output_contract`: explicit versioned response contract reference and schema shape.
- Required fields:
  - `runtime_contract`
  - `safety_contract`
  - `astrologer_voice`
  - `feature_context`
  - `delivery_profile`
  - `input_data`
  - `birth_context`
  - `astrological_facts`
  - `interpretation_material`
  - `selected_themes`
  - `limits`
  - `output_contract`
- Optional fields:
  - none.
- Status codes:
  - none; no API route is created or changed.
- Serialization names:
  - JSON payload keys are emitted exactly as listed in Required fields.
- Frontend type impact:
  - none.
- Generated contract impact:
  - output contract reference must come from the versioned `theme_astral` contract family.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-366-provider-payload-builder-theme-astral/evidence/provider-payload-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-366-provider-payload-builder-theme-astral/evidence/provider-payload-after.json`
- Expected invariant:
  - The only intended backend surface delta is the provider payload builder, resolver wiring, handoff connection, and targeted tests.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Provider payload builder | `backend/app/domain/llm/runtime/` | `backend/app/services/llm_generation/natal/` duplicate builder |
| Delivery profile resolution | `backend/app/domain/llm/configuration/**` or runtime plan resolver | provider payload literals |
| Interpretation material input | `backend/app/domain/astrology/interpretation/**` | prompt text builder |
| Astrologer voice input | persona or assembly resolver owner | astrological fact builder |
| Output contract reference | versioned LLM contract family owner | hardcoded user payload text |
| Unit orchestration tests | `backend/tests/llm_orchestration/` | frontend tests |
| Integration handoff tests | `backend/tests/integration/llm/` | live provider tests |
| Story evidence | `_condamad/stories/CS-366-provider-payload-builder-theme-astral/evidence/` | backend app code |

## Mandatory Reuse / DRY Constraints

- Reuse CS-363 target skeleton, CS-364 versioned contract family, and CS-365 material builder outputs.
- Reuse existing runtime request, execution plan, assembly resolver, persona, and output contract concepts.
- Reuse existing natal generation boundaries instead of creating a second service pathway.
- Use one builder and one skeleton for `free`, `basic`, and `premium`.
- Keep commercial plan mapping in one backend resolver or policy owner.
- Do not duplicate the same structured data between developer prompt and user payload.
- Do not introduce new dependencies.

## No Legacy / Forbidden Paths

- No legacy payload builder may become the active `theme_astral` target.
- No compatibility payload builder may be added for profile-specific shapes.
- No fallback payload builder may fabricate missing material or output contracts.
- No commercial labels `plan`, `free`, `basic`, or `premium` may appear in the provider-visible payload.
- No profile-specific top-level key set may be emitted.
- No duplicate copy of the same `interpretation_material` may appear in both developer prompt and user payload.
- No astrologer voice may own astrological truth, facts, tables, or engine outputs.
- Do not edit frontend files, DB migrations, source text tables, real provider clients, or guardrail registry entries.

## Reintroduction Guard

- Require tests that compare top-level keys and nested `input_data` keys across all three plans.
- Require tests that search serialized provider payloads for commercial labels and fail on any match.
- Require tests that verify quantity, length, section, and budget values vary through `delivery_profile` only.
- Require tests that prove `interpretation_material` is present in every plan and sourced from CS-365 output.
- Require `rg` guards for duplicate prompt data in developer prompt and user payload assembly paths.
- Require bounded git diff guards for frontend, migrations, source text tables, and provider client surfaces.

## Regression Guardrails

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend app layout remains canonical and no API router ownership is hijacked. | `AST guard`; `rg` ownership scan. |
| RG-022 `align-prompt-generation-story-validation-paths` | Prompt-generation validations must target collected pytest paths. | `pytest` paths; validation artifact. |
| Registry gap | No exact guardrail covers `theme_astral` provider payload skeleton and plan hiding. | Resolver output saved in evidence. |

Non-applicable examples:

- `RG-047` frontend inline styles is out of scope because no frontend source is touched.
- `RG-052` frontend CSS namespace migration is out of scope because no style source is touched.
- `RG-041` entitlement documentation is out of scope because no entitlement surface is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Source availability | `_condamad/stories/CS-366-provider-payload-builder-theme-astral/evidence/source-availability.txt` | Prove required sources. |
| Provider payload before | `_condamad/stories/CS-366-provider-payload-builder-theme-astral/evidence/provider-payload-before.json` | Store baseline payload shape. |
| Provider payload after | `_condamad/stories/CS-366-provider-payload-builder-theme-astral/evidence/provider-payload-after.json` | Store final payload shape. |
| Plan hiding proof | `_condamad/stories/CS-366-provider-payload-builder-theme-astral/evidence/plan-hiding-proof.txt` | Prove commercial labels stay hidden. |
| Duplication proof | `_condamad/stories/CS-366-provider-payload-builder-theme-astral/evidence/no-duplication-proof.txt` | Prove prompt data is not duplicated. |
| Validation output | `_condamad/stories/CS-366-provider-payload-builder-theme-astral/evidence/validation.txt` | Store validation commands. |
| Review output | `_condamad/stories/CS-366-provider-payload-builder-theme-astral/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist Exception: not applicable
- Reason: no allowlist handling is authorized for this provider payload story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` - canonical provider payload builder.
- `backend/app/domain/llm/runtime/contracts.py` - typed payload or handoff contracts only when the owner map proves it belongs there.
- `backend/app/domain/llm/runtime/gateway.py` - connect built payload to existing handoff without real provider calls.
- `backend/app/domain/llm/configuration/**` - expose resolved delivery and output contract data through existing owners.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - provide material and facts to the payload builder.
- `_condamad/stories/CS-366-provider-payload-builder-theme-astral/evidence/**` - persist required evidence artifacts.
- `_condamad/stories/CS-366-provider-payload-builder-theme-astral/generated/11-code-review.md` - generated review handoff.

Likely tests:

- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` - payload shape, profile values, voice, and plan hiding.
- `backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py` - runtime handoff without provider calls.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` - adapt input contract coverage for payload source data.
- `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py` - adapt audit-only boundary coverage.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no migration is authorized.
- `backend/app/infra/db/models/**` - out of scope; no schema model change is authorized.
- `backend/app/infra/db/repositories/**` - out of scope; CS-365 owns sourced material access.
- `_condamad/stories/regression-guardrails.md` - out of scope; no registry enrichment is authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

All Python commands must run after `.\.venv\Scripts\Activate.ps1`.
Run backend quality commands from `backend` after activation.
Run VC15 from `_condamad/stories/CS-366-provider-payload-builder-theme-astral`.

- VC1: `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- VC2: `pytest -q backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`
- VC3: `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`
- VC4: `pytest -q backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py`
- VC5: `rg -n "runtime_contract|safety_contract|astrologer_voice|feature_context|delivery_profile" backend/app backend/tests`
- VC6: `rg -n "birth_context|astrological_facts|interpretation_material|selected_themes|limits|output_contract" backend/app backend/tests`
- VC7: `rg -n "theme_astral|ThemeAstral|provider_payload|ProviderPayloadBuilder" backend/app backend/tests`
- VC8: `rg -n "free|basic|premium|plan" backend/app/domain/llm backend/tests/llm_orchestration backend/tests/integration/llm`
- VC9: `rg -n "developer_prompt|user_payload|build_user_payload|compose_structured_messages" backend/app/domain/llm/runtime backend/tests`
- VC10: `python -c "import subprocess; subprocess.run(['git','diff','--quiet','--','frontend/src','backend/migrations'], check=True)"`
- VC11: `python -c "import subprocess; subprocess.run(['git','diff','--quiet','--','backend/app/infra/db/models'], check=True)"`
- VC12: `python -c "import subprocess; subprocess.run(['git','diff','--quiet','--','backend/app/infra/db/repositories'], check=True)"`
- VC13: `ruff format .`
- VC14: `ruff check .`
- VC15: `python -c "from pathlib import Path; assert Path('evidence/validation.txt').exists()"`
- VC16: `pytest -q tests/llm_orchestration tests/unit/domain/astrology tests/integration/llm --tb=short`
- VC17: `rg -n "theme_astral|delivery_profile|astrologer_voice|interpretation_material|output_contract|runtime_contract|safety_contract" app tests`

## Regression Risks

- The builder could emit different skeleton keys per commercial plan.
- Commercial labels could leak into provider-visible payload content.
- Delivery profile values could be duplicated in prompt text and payload JSON.
- `interpretation_material` could be rebuilt or fabricated instead of reused from the material owner.
- Astrologer voice could alter factual astrology or sourced interpretation truth.
- Output contract could be hardcoded outside the versioned contract family.
- Runtime handoff tests could pass with a stub that does not exercise the loaded builder.

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
- Do not modify frontend files, migrations, DB models, DB repositories, source text tables, or guardrail registry entries.
- Persist validation output under the CS-366 story evidence folder.

## References

- `_story_briefs/cs-366-implementer-provider-payload-builder-theme-astral-stable-par-feature.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/00-story.md`
- `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/00-story.md`
- `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/00-story.md`
- `_condamad/architecture/theme-astral-prompt-contract/**/archi-theme-astral-prompt-contract-v1.md`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/runtime/contracts.py`
- `backend/app/domain/llm/configuration/**`
- `backend/app/domain/astrology/interpretation/**`
- `backend/app/services/llm_generation/natal/**`
- `backend/tests/llm_orchestration/**`
- `backend/tests/unit/domain/astrology/**`
- `backend/tests/integration/llm/**`
