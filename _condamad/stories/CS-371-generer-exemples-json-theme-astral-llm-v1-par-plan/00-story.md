# Story CS-371 generer-exemples-json-theme-astral-llm-v1-par-plan: Generate Theme Astral LLM V1 JSON Examples By Plan
Status: ready-to-review

## Trigger / Source

- Source brief: `_story_briefs/cs-371-generer-exemples-json-theme-astral-llm-v1-par-plan.md`.
- Selected mode: Repo-informed story, because examples must reflect the final backend contract and upstream source gaps.
- Source problem: `theme_astral` needs three complete final provider payload JSON examples for `free`, `basic`, and `premium`.
- Source stakes:
  - The three examples must use the same birth scenario and the same canonical JSON skeleton.
  - Plan differences must appear through density, depth, budgets, selected material, and return contract richness.
  - Payloads must contain resolved values only and must not be sent to any LLM provider.
  - `delivery_profile` must be visible while the commercial plan label stays outside LLM-visible content.
  - Examples must be generated from the final runtime path or a script reusing the same builders.
- Source-alignment evidence: PASS. Objective, ACs, tasks, validation, non-goals, and guardrails preserve the brief deliverables.

## Objective

Create complete JSON examples for the final `theme_astral` LLM v1 provider payload for `free`, `basic`, and `premium`.

The examples must use a person born on `1973-04-24` at `11:00` in Paris, France, and must document the generation method,
the intermediate data, the shared skeleton, the plan-specific density differences, and the no-provider-call proof.

## Target State

- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/README.md` exists.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/intermediate-data.json` exists.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/free-provider-payload.json` exists.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/basic-provider-payload.json` exists.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/premium-provider-payload.json` exists.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/structure-comparison.md` exists.
- The three provider payload files are valid JSON and share the same canonical skeleton.
- Each provider payload contains resolved values, `delivery_profile`, `astrologer_voice`, `safety_contract`, and `feature_context`.
- Each provider payload contains `input_data.birth_context`, `input_data.astrological_facts`, `input_data.interpretation_material`,
  `input_data.selected_themes`, `input_data.limits`, and `output_contract`.
- The examples are not sent to an LLM provider and no provider response is produced.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-371-generer-exemples-json-theme-astral-llm-v1-par-plan.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-371`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `_condamad/stories/CS-358-generer-exemples-json-prompts-theme-astral-par-plan/00-story.md` - prior example pattern read.
- Evidence 5: `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/00-story.md` - architecture story read.
- Evidence 6: `_condamad/stories/CS-366-provider-payload-builder-theme-astral/00-story.md` - provider payload builder story read.
- Evidence 7: `_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/00-story.md` - synthesis story read.
- Evidence 8: targeted `rg` checked `theme_astral`, `delivery_profile`, `interpretation_material`, and provider payload terms in backend paths.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped `resolve_guardrails.py` output.
- Repository structure alert: `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md` is absent now.
- Repository structure alert: `_condamad/architecture/theme-astral-prompt-contract` is absent now.
- Repository structure alert: `backend`, `backend/app/domain`, `backend/app/services`, `backend/app/ops`, and `backend/tests` exist.
- Registry gap: no exact guardrail covers complete `theme_astral` LLM v1 JSON examples by delivery profile.
- Assumption risk: CS-363 to CS-370 may be implemented before this story starts; implementation must verify final artifacts first.

## Domain Boundary

- Domain: documentation-examples
- In scope:
  - Example artifacts under `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/`.
  - Final provider payload JSON examples for `free`, `basic`, and `premium`.
  - `intermediate-data.json` with normalized birth context, astrological facts, sourced material, selected themes, limits, and profile inputs.
  - `structure-comparison.md` proving identical skeleton and increasing content density.
  - No-provider-call proof and validation evidence under the CS-371 story folder.
  - Read-only inspection of backend domain, services, ops, tests, CS-363 to CS-370 outputs, and final runtime builders.
- Out of scope:
  - Backend runtime edits, frontend UI, database schema, auth, i18n, styling, build tooling, migrations, provider calls, and prompt rewrite.
  - Changing the `theme_astral` contract, output schema, or delivery profile rules.
  - Guardrail registry maintenance or enrichment.
- Explicit non-goals:
  - No real LLM call.
  - No final prose response generated by an LLM.
  - No contract modification.
  - No frontend route, screen, client generation, or UI validation.

Named brief primitives in scope:

- `README.md`
- `intermediate-data.json`
- `free-provider-payload.json`
- `basic-provider-payload.json`
- `premium-provider-payload.json`
- `structure-comparison.md`
- `theme_astral`
- `delivery_profile`
- `astrologer_voice`
- `safety_contract`
- `feature_context`
- `input_data.birth_context`
- `input_data.astrological_facts`
- `input_data.interpretation_material`
- `input_data.selected_themes`
- `input_data.limits`
- `output_contract`
- `free`
- `basic`
- `premium`

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend-generated documentation example contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Create only example files and story evidence artifacts.
  - Generate payloads from the final runtime path or a local script that reuses the same backend builders.
  - Keep one canonical JSON skeleton for all three profiles.
  - Keep backend application files unchanged unless a focused local generator or test is required and approved by source ownership.
  - Keep frontend files, migrations, DB models, prompt seeds, and provider clients unchanged.
  - Never invoke a real LLM provider.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: final CS-363 to CS-370 artifacts are missing or contradict the `theme_astral` LLM v1 skeleton.
- Additional validation rules:
  - `python` JSON parsing must prove `intermediate-data.json` and all three provider payloads are valid.
  - `python` structure checks must prove the three provider payloads share the same key skeleton.
  - `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` must prove final builder behavior.
  - `pytest -q backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py` must prove no live provider call.
  - `rg` scans must prove required blocks, the birth scenario, resolved values, and no placeholder tokens.
  - `AST guard` or bounded git status evidence must prove protected runtime, frontend, migration, and provider-client files are unchanged.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Final builders, full `pytest` paths, no-provider handoff tests, and `AST guard` prove the examples mirror runtime. |
| Baseline Snapshot | yes | Before and after artifacts prove the only allowed surface delta is examples and story evidence. |
| Ownership Routing | yes | Examples belong under `_condamad/examples`, while runtime owners remain backend source truth. |
| Allowlist Exception | no | No allowlist handling is authorized for this example-generation story. |
| Contract Shape | yes | JSON files must expose exact canonical blocks, nested input data, profile values, and output contract. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Provider calls, placeholders, plan-label leakage, old payload carriers, and audit-only leakage must stay absent. |
| Persistent Evidence | yes | JSON checks, structure comparison, scans, validation output, and review handoff must persist. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The required example folder contains six deliverables. | Evidence profile: baseline_before_after_diff; `python` checks all expected paths. |
| AC2 | All example JSON files parse successfully. | Evidence profile: json_contract_shape; `python` loads four JSON files. |
| AC3 | The birth context matches the brief. | Evidence profile: json_contract_shape; `python` checks `1973-04-24`, `11:00`, and `Paris`. |
| AC4 | The three payloads share one skeleton. | Evidence profile: json_contract_shape; `python` compares recursive key skeletons. |
| AC5 | Provider payload values are resolved. | Evidence profile: targeted_forbidden_symbol_scan; `rg` rejects placeholders and invalid date text. |
| AC6 | `interpretation_material` is present. | Evidence profile: json_contract_shape; `python` checks non-empty material for each payload. |
| AC7 | Content density increases by profile. | Evidence profile: json_contract_shape; `python` compares facts, material, themes, limits, and output sections. |
| AC8 | No provider call is performed. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`. |
| AC9 | Comparison documentation explains differences. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks `structure-comparison.md`. |
| AC10 | README documents the generation method. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks README method and command terms. |
| AC11 | Commercial labels stay outside LLM content. | Evidence profile: json_contract_shape; `python` scans payload messages for plan labels. |
| AC12 | Persistent evidence is stored. | Evidence profile: baseline_before_after_diff; `python` checks evidence and generated paths. |

## Implementation Tasks

- [ ] Task 1: Read the final CS-363 to CS-370 artifacts and record missing source gaps in CS-371 evidence. (AC: AC10, AC12)
- [ ] Task 2: Inspect backend domain, services, ops, and tests to locate the final payload builder and no-provider test path. (AC: AC8)
- [ ] Task 3: Generate or capture `intermediate-data.json` from the final runtime path or shared backend builders. (AC: AC2, AC3, AC6)
- [ ] Task 4: Generate `free-provider-payload.json` with the canonical `theme_astral` skeleton. (AC: AC2, AC4, AC5, AC6)
- [ ] Task 5: Generate `basic-provider-payload.json` with the same skeleton and richer profile values. (AC: AC2, AC4, AC7)
- [ ] Task 6: Generate `premium-provider-payload.json` with the same skeleton and maximum profile density. (AC: AC2, AC4, AC7)
- [ ] Task 7: Create `structure-comparison.md` with skeleton proof and profile-difference summary. (AC: AC4, AC7, AC9)
- [ ] Task 8: Create README with scenario, generation method, source gaps, and commands executed. (AC: AC10)
- [ ] Task 9: Run JSON, skeleton, placeholder, no-provider, and protected-surface validations. (AC: AC1, AC2, AC5, AC8)
- [ ] Task 10: Persist validation output, guardrail resolver output, and review handoff artifacts. (AC: AC12)

## Files to Inspect First

- `_story_briefs/cs-371-generer-exemples-json-theme-astral-llm-v1-par-plan.md`
- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md` - expected upstream source path.
- `_condamad/architecture/theme-astral-prompt-contract/**/archi-theme-astral-prompt-contract-v1.md` - expected upstream source path.
- `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/00-story.md`
- `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/00-story.md`
- `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/00-story.md`
- `_condamad/stories/CS-366-provider-payload-builder-theme-astral/00-story.md`
- `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/00-story.md`
- `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/00-story.md`
- `_condamad/stories/CS-369-audit-review-adversariale-correction-theme-astral-prompt-contract/00-story.md`
- `_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/00-story.md`
- `backend/app/domain/**`
- `backend/app/services/**`
- `backend/app/ops/**`
- `backend/tests/**`

Assumption-risk note: the two expected upstream documentation paths are absent now and may be produced by CS-363 or CS-370 before implementation.

## Runtime Source of Truth

- Primary source of truth:
  - Final provider payload builder and delivery profile resolver in backend source.
  - `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`.
  - `pytest -q backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`.
  - `AST guard` for payload builder ownership, no-provider path, and protected-source stability.
- Secondary evidence:
  - CS-363 to CS-370 story outputs and final generated artifacts.
  - Targeted `rg` scans over generated examples for required blocks, placeholders, and no-provider markers.
- Static scans alone are not sufficient for this story because:
  - The payload examples must reflect the loaded runtime builder and no-provider handoff behavior.

## Contract Shape

- Contract type:
  - Static example artifacts for final `theme_astral` LLM v1 provider payloads.
- Fields:
  - `runtime_contract`: runtime metadata and contract identifiers.
  - `safety_contract`: safety and non-invention rules.
  - `astrologer_voice`: style, tone, vocabulary, and emphases.
  - `feature_context`: feature, locale, use-case context, and backend-visible scenario identifiers.
  - `delivery_profile`: resolved density, length, budget, section, and selection rules.
  - `input_data.birth_context`: normalized birth context for `1973-04-24`, `11:00`, Paris, France.
  - `input_data.astrological_facts`: calculated or recovered astrological facts for the birth context.
  - `input_data.interpretation_material`: sourced interpretation material from backend interpretation tables.
  - `input_data.selected_themes`: selected theme identifiers and labels governed by the delivery profile.
  - `input_data.limits`: missing data, uncertainty notes, and profile limits.
  - `output_contract`: versioned requested LLM response contract.
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
  - none for the canonical example payload skeleton.
- Status codes:
  - none; no API route is created or changed.
- Serialization names:
  - JSON keys must be emitted exactly as listed in the final contract and examples.
- Frontend type impact:
  - none.
- Generated contract impact:
  - none; examples consume the final contract and do not redefine it.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/examples-baseline.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/examples-after.txt`
- Expected invariant:
  - The only intended product artifact delta is the CS-371 examples folder plus CS-371 evidence artifacts.
- Runtime invariant:
  - Backend runtime files, frontend files, migrations, DB models, and provider clients remain unchanged.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Example README | `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/README.md` | `backend/app/**` |
| Provider payload examples | `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/*-provider-payload.json` | `frontend/src/**` |
| Intermediate data example | `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/intermediate-data.json` | `backend/app/domain/**` |
| Structure comparison | `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/structure-comparison.md` | Runtime code comments |
| Story execution evidence | `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/**` | `_condamad/examples/**` |
| Backend payload generation | Existing final builder owner | new parallel example-only builder |

## Mandatory Reuse / DRY Constraints

- Reuse the final `theme_astral` provider payload builder or a script that imports the same backend builders.
- Reuse CS-363 to CS-370 final artifacts as source context instead of redefining the contract.
- Reuse one canonical skeleton for `free`, `basic`, and `premium`.
- Centralize shared birth context, facts, and source material in `intermediate-data.json` or runtime output.
- Keep commercial profile differences explicit through `delivery_profile`, selected material, budgets, and output contract richness.
- Do not duplicate prompt-building logic in example-only code.
- Do not introduce new dependencies.

## No Legacy / Forbidden Paths

- No legacy payload carrier may be used as the source of these examples.
- No compatibility payload path may be created for profile-specific examples.
- No fallback payload builder may fabricate missing runtime contract blocks.
- No commercial label `plan`, `free`, `basic`, or `premium` may appear as LLM-visible instruction content.
- No provider response, API key, bearer token, credential, or secret may appear in the example folder.
- No unresolved placeholder token may appear in generated JSON or markdown.
- Do not edit frontend files, DB migrations, provider clients, prompt seeds, or guardrail registry entries.
- Do not preserve legacy behavior.

## Reintroduction Guard

- Guard generated examples for unresolved placeholders:
  - `rg -n "\{\{|TODO|TBD|example_value|24/04//1973" _condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1`
- Guard required contract blocks:
  - `rg -n "interpretation_material|delivery_profile|astrologer_voice|output_contract" _condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1`
  - `rg -n "1973-04-24|11:00|Paris" _condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1`
- Guard provider and secret leakage:
  - `rg -n "provider_response|api_key|OPENAI_API_KEY|sk-|Bearer|credential|secret" _condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1`
- Guard protected surfaces:
  - `python -c "import subprocess as s; assert not s.getoutput('git status --short -- backend/app frontend/src backend/migrations')"`

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `Routeurs API v1` | Backend app paths are source truth only and must not receive example content. | `AST guard`; bounded git status. |
| RG-022 `Plans de validation des stories prompt-generation` | Prompt-generation examples need explicit validation paths and persisted evidence. | `python` JSON checks; `pytest`. |
| Registry gap | No exact guardrail covers complete `theme_astral` LLM v1 JSON examples by profile. | Resolver output saved in evidence. |

Non-applicable examples:

- `RG-041` entitlement documentation is outside scope because no entitlement or frontend build surface is touched.
- `RG-047` inline TSX styling is outside scope because no TSX file is touched.
- `RG-052` CSS namespace migration is outside scope because no CSS or frontend migration is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Source coverage | `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/source-coverage.md` | List inspected sources and gaps. |
| Guardrail resolver output | `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/guardrails.txt` | Keep scoped guardrail selection. |
| Baseline snapshot | `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/examples-baseline.txt` | Record target folder state. |
| After snapshot | `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/examples-after.txt` | Record final example paths. |
| JSON validation | `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/json-validation.txt` | Prove JSON parsing and skeleton. |
| No-provider proof | `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/no-provider-proof.txt` | Prove provider was not called. |
| Validation output | `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/validation.txt` | Store validation command output. |
| Review output | `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this example-generation story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/README.md` - scenario and method.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/intermediate-data.json` - shared data.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/free-provider-payload.json` - free payload.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/basic-provider-payload.json` - basic payload.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/premium-provider-payload.json` - premium payload.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/structure-comparison.md` - comparison proof.
- `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/**` - validation handoff artifacts.
- `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/generated/11-code-review.md` - review handoff.

Likely tests:

- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` - payload shape, profile values, and plan hiding.
- `backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py` - runtime handoff without provider calls.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` - source input contract coverage.
- `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py` - audit-only boundary coverage.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no migration is authorized.
- `backend/app/infra/db/models/**` - out of scope; no schema model change is authorized.
- `backend/app/infra/db/repositories/**` - out of scope; sourced material access is read-only.
- `backend/app/infra/llm/**` - out of scope; no live provider client change is authorized.
- `_condamad/stories/regression-guardrails.md` - out of scope; no registry enrichment is authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

All Python commands must run after `.\.venv\Scripts\Activate.ps1`.
Run backend quality commands from `backend` after activation.

- VC1: `python -c "from pathlib import Path; p=Path('_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1'); assert p.exists()"`
- VC2: `python -B -m json.tool _condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/intermediate-data.json`
- VC3: `python -B -m json.tool _condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/free-provider-payload.json`
- VC4: `python -B -m json.tool _condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/basic-provider-payload.json`
- VC5: `python -B -m json.tool _condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/premium-provider-payload.json`
- VC6: `python` compares recursive key skeletons across free, basic, and premium payloads.
- VC7: `python` checks `birth_context`, non-empty `interpretation_material`, profile densities, and `output_contract`.
- VC8: `rg -n "\{\{|TODO|TBD|example_value|24/04//1973" _condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1`
- VC9: `rg -n "interpretation_material|delivery_profile|astrologer_voice|output_contract" _condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1`
- VC9b: `rg -n "1973-04-24|11:00|Paris" _condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1`
- VC10: `rg -n "provider_response|api_key|OPENAI_API_KEY|sk-|Bearer|credential|secret" _condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1`
- VC11: `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- VC12: `pytest -q backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`
- VC13: `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`
- VC14: `pytest -q backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py`
- VC15: `python -c "import subprocess as s; assert not s.getoutput('git status --short -- frontend/src backend/migrations')"`
- VC16: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/validation.txt').exists()"`
- VC17: `ruff format .`
- VC18: `ruff check .`
- VC19: `pytest -q`

## Regression Risks

- The examples could be hand-written and drift from the final runtime builder.
- The three payloads could diverge structurally instead of varying through `delivery_profile` and content density.
- Commercial plan labels could leak into LLM-visible messages.
- `interpretation_material` could be empty, fabricated, or not sourced from backend interpretation tables.
- Audit-only fields could appear in provider-visible payload content.
- Placeholder tokens or secret-like strings could be copied into example artifacts.
- A no-provider-call claim could be recorded without a runtime or test proof.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python, pip, pytest, or ruff command.
- Use the final backend builders or a script importing the same builders; do not handcraft payloads from memory.
- Record missing upstream artifacts in `source-coverage.md` rather than inventing final facts.
- Never call OpenAI, another LLM provider, or external provider runtime while producing these examples.
- Persist all validation outputs under the CS-371 evidence directory.

## References

- `_story_briefs/cs-371-generer-exemples-json-theme-astral-llm-v1-par-plan.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-358-generer-exemples-json-prompts-theme-astral-par-plan/00-story.md`
- `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/00-story.md`
- `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/00-story.md`
- `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/00-story.md`
- `_condamad/stories/CS-366-provider-payload-builder-theme-astral/00-story.md`
- `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/00-story.md`
- `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/00-story.md`
- `_condamad/stories/CS-369-audit-review-adversariale-correction-theme-astral-prompt-contract/00-story.md`
- `_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/00-story.md`
- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
- `_condamad/architecture/theme-astral-prompt-contract/**/archi-theme-astral-prompt-contract-v1.md`
- `backend/app/domain/**`
- `backend/app/services/**`
- `backend/app/ops/**`
- `backend/tests/**`
