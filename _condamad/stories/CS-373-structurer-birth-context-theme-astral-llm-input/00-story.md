# Story CS-373 structurer-birth-context-theme-astral-llm-input: Structure Theme Astral Birth Context For LLM Input
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-373-structurer-birth-context-theme-astral-llm-input-v1.md`.
- Selected mode: Repo-informed story.
- Source problem statement: `input_data.birth_context` exposes mainly `chart_id`, `locale`, and `chart_type`, so the LLM lacks normalized birth data.
- Source stakes:
  - User impact: generated theme astral text can miss basic date, time, place, country, timezone, or precision context.
  - Technical risk: relying on `chart_id` parsing makes a human-readable identifier behave like a data contract.
  - Closure expectation: runtime contracts, builder, schema, tests, examples, and JSON structure docs expose the same normalized context.
  - Forbidden regression: no unnecessary personal data may be added to the LLM-visible payload.
- Source-alignment evidence: objective, ACs, tasks, validation, and guardrails preserve every included item from the brief.

## Objective

Add normalized, minimized birth context fields to `input_data.birth_context` for the `theme_astral_llm_input_v1` provider payload.

## Target State

- `ChartInterpretationInputRuntimeData` carries an explicit birth context projection owned by the interpretation input boundary.
- `ChartInterpretationInputBuilder` receives or reconstructs birth context from canonical natal runtime inputs without parsing `chart_id`.
- `ThemeAstralProviderPayloadBuilder._birth_context` emits date, local time, place, country, timezone, coordinates, and precision flags.
- `THEME_ASTRAL_INPUT_SCHEMA` documents or validates the `birth_context` subkeys required by the versioned input contract.
- Provider payload tests prove the structured birth context for representative free, basic, and premium payloads.
- CS-371 example payloads for `1973-04-24 11:00 Paris France` are regenerated and aligned with the documentation.
- Documentation states that birth date, time, place, country, and timezone are visible in provider payloads, not only in `intermediate-data.json`.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-373-structurer-birth-context-theme-astral-llm-input-v1.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-373` after `CS-372`.
- Evidence 3: `backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py` - runtime contract lacks structured birth fields.
- Evidence 4: `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` - `_birth_context` currently emits only `chart_id`, `locale`, and `chart_type`.
- Evidence 5: `backend/app/domain/llm/configuration/theme_astral_contracts.py` - `THEME_ASTRAL_INPUT_SCHEMA` currently treats `input_data` as a generic object.
- Evidence 6: `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1` - scoped example directory exists.
- Evidence 7: `.agents/skills/condamad-story-writer/scripts/resolve_guardrails.py` - resolver returned scoped guardrails `RG-002` and `RG-022`.

## Domain Boundary

- Domain: backend-llm-prompt-contract
- In scope:
  - `ChartInterpretationInputRuntimeData` birth context contract.
  - `ChartInterpretationInputBuilder` birth context handoff from canonical natal runtime data.
  - `ThemeAstralProviderPayloadBuilder._birth_context` structured payload projection.
  - `THEME_ASTRAL_INPUT_SCHEMA` birth context subkeys for `theme_astral_llm_input_v1`.
  - Provider payload tests, prompt contract persistence tests, CS-371 example regeneration, and JSON structure documentation.
- Out of scope:
  - Frontend UI, auth, i18n, styling, unrelated API routes, unrelated DB schema, build tooling, and migrations.
  - Astrological calculation accuracy changes.
  - Real LLM provider calls.
  - Adding personal data not required to write a theme astral.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
  - No change to the astrological computation engine.
  - No parsing of `chart_id` as the canonical source of birth data.
  - No new provider integration or prompt text rewrite.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only normalized birth context fields required by `theme_astral_llm_input_v1`.
  - Keep `chart_id` as a technical identifier, not as the source of structured birth fields.
  - Include coordinates only when canonical runtime data provides them.
  - Represent unavailable birth data through `birth_context.precision` or `input_data.limits`.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: no canonical runtime source can provide birth date, local time, place, country, or timezone.
- Additional validation rules:
  - `AST guard` must prove `_birth_context` does not parse `chart_id`.
  - `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` must prove provider payload shape.
  - `pytest -q backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py` must prove handoff payload shape.
  - Targeted `rg` scans must prove examples and docs expose normalized birth fields.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Runtime data, builder tests, and `AST guard` prove birth fields come from canonical inputs. |
| Baseline Snapshot | yes | Before and after payload artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Runtime contract, provider projection, schema, examples, and docs have distinct owners. |
| Allowlist Exception | no | No allowlist handling is authorized for birth context enrichment. |
| Contract Shape | yes | The birth context JSON fields and precision flags are exact contract values. |
| Batch Migration | no | No batch conversion or database migration is in scope. |
| Reintroduction Guard | yes | `chart_id` parsing and unrelated personal fields must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Runtime birth data has a canonical contract. | Evidence profile: json_contract_shape; `pytest`; `tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`. |
| AC2 | Provider payload exposes structured birth date. | Evidence profile: json_contract_shape; `pytest`; provider payload test path. |
| AC3 | Provider payload exposes structured birth place. | Evidence profile: json_contract_shape; `pytest`; provider payload test path. |
| AC4 | Provider payload represents missing precision. | Evidence profile: json_contract_shape; `pytest`; `tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`. |
| AC5 | Coordinates are emitted only from canonical data. | Evidence profile: ast_architecture_guard; `AST guard`; `pytest` provider tests. |
| AC6 | The versioned input schema covers birth context. | Evidence profile: json_contract_shape; `pytest`; `tests/integration/test_theme_astral_prompt_contract_persistence.py`. |
| AC7 | Bigbang handoff preserves structured birth context. | Evidence profile: json_contract_shape; `pytest`; bigbang test path. |
| AC8 | CS-371 provider examples expose Paris birth fields. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans scoped example payloads. |
| AC9 | JSON structure docs describe provider-visible birth fields. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans scoped docs and README. |
| AC10 | No unnecessary personal fields are added. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans provider builder, tests, and examples. |
| AC11 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks the story evidence directory. |

## Implementation Tasks

- [ ] Task 1: Inspect source files and identify the canonical natal runtime source for birth date, local time, place, country, timezone, and coordinates. (AC: AC1)
- [ ] Task 2: Add a typed birth context projection to `ChartInterpretationInputRuntimeData`. (AC: AC1, AC4)
- [ ] Task 3: Update `ChartInterpretationInputBuilder` to populate birth context without parsing `chart_id`. (AC: AC1, AC5)
- [ ] Task 4: Update `_birth_context` to emit normalized date, time, place, coordinates, and precision flags. (AC: AC2, AC3, AC4, AC5)
- [ ] Task 5: Update `THEME_ASTRAL_INPUT_SCHEMA` with the versioned `birth_context` shape. (AC: AC6)
- [ ] Task 6: Update provider payload and bigbang tests for structured birth context. (AC: AC2, AC3, AC4, AC7)
- [ ] Task 7: Regenerate CS-371 Paris example payloads and update example documentation. (AC: AC8, AC9)
- [ ] Task 8: Update JSON structure documentation so birth fields are provider-visible. (AC: AC9)
- [ ] Task 9: Add targeted guards against `chart_id` parsing and unrelated personal fields. (AC: AC5, AC10)
- [ ] Task 10: Persist before and after payload evidence plus final validation output. (AC: AC11)

## Files to Inspect First

- `backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py`
- `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py`
- `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`
- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/free-provider-payload.json`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/basic-provider-payload.json`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/premium-provider-payload.json`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/README.md`

## Runtime Source of Truth

- Primary source of truth:
  - `ChartInterpretationInputRuntimeData`.
  - `ChartInterpretationInputBuilder`.
  - Canonical natal runtime attributes used by the builder.
  - `ThemeAstralProviderPayloadBuilder._birth_context`.
  - `THEME_ASTRAL_INPUT_SCHEMA`.
  - `AST guard` proving no `chart_id` parsing path.
- Secondary evidence:
  - Targeted `rg` scans for structured field names in provider examples and docs.
- Static scans alone are not sufficient for this story because:
  - Provider payload construction and handoff shape must be proven by runtime tests.

## Contract Shape

- Contract type:
  - Versioned JSON input contract for `theme_astral_llm_input_v1`.
- Fields:
  - `chart_id`: technical identifier retained as nullable string.
  - `birth_date`: ISO date string or null.
  - `birth_time_local`: local time string or null.
  - `birth_place.city`: city string or null.
  - `birth_place.country`: country string or null.
  - `birth_place.timezone`: timezone string or null.
  - `birth_place.latitude`: float or null, emitted only from canonical data.
  - `birth_place.longitude`: float or null, emitted only from canonical data.
  - `precision.birth_time_known`: boolean.
  - `precision.coordinates_known`: boolean.
  - `locale`: locale string or null.
  - `chart_type`: chart type string.
- Required fields:
  - `chart_id`
  - `birth_date`
  - `birth_time_local`
  - `birth_place`
  - `precision`
  - `locale`
  - `chart_type`
- Optional fields:
  - none newly authorized beyond nullable values in the required structure.
- Status codes:
  - none; this backend domain story does not define an HTTP response contract.
- Serialization names:
  - `birth_date` is emitted as `birth_date`.
  - `birth_time_local` is emitted as `birth_time_local`.
  - `birth_place` is emitted as `birth_place`.
  - `precision` is emitted as `precision`.
- Frontend type impact:
  - none.
- Generated contract impact:
  - Regenerated CS-371 provider examples must expose the structured birth context.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-373-structurer-birth-context-theme-astral-llm-input/evidence/birth-context-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-373-structurer-birth-context-theme-astral-llm-input/evidence/birth-context-after.json`
- Expected invariant:
  - The only intended provider payload delta is enriched `input_data.birth_context` and matching schema, docs, tests, and examples.
- Required proof:
  - Before and after artifacts must include representative provider payload snippets plus the targeted validation command results.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Birth context runtime contract | `chart_interpretation_input_contracts.py` | Provider builder ad hoc dictionaries |
| Birth context population | `chart_interpretation_input_builder.py` | `chart_id` string parsing |
| Provider-visible projection | `theme_astral_provider_payload_builder.py` | Prompt template text |
| Versioned input schema | `theme_astral_contracts.py` | Generated examples as source of truth |
| Example payload evidence | `_condamad/examples/prompt-generation-cartography` | Runtime tests as documentation copy |
| JSON structure documentation | `_condamad/docs/prompt-generation-cartography` | Backend comments as public contract |

## Mandatory Reuse / DRY Constraints

- Reuse the typed runtime birth context projection in provider payload code and tests.
- Do not duplicate birth context assembly logic in tests, examples, or docs.
- Keep `_birth_context` as a projection function, not a source reconstruction function.
- Reuse existing provider payload builder tests and example generation workflow.
- Keep documentation aligned with runtime field names from the contract owner.

## No Legacy / Forbidden Paths

- No legacy parsing of `chart_id` may populate birth date, local time, place, country, timezone, or coordinates.
- No compatibility carrier may leave date, time, or place only inside `chart_id`.
- No fallback string parsing may reconstruct missing birth fields from human-readable identifiers.
- No duplicated birth context builder may be introduced outside the interpretation input and provider payload ownership path.
- No unrelated personal fields may be added to the LLM-visible payload.

## Reintroduction Guard

- Forbidden runtime symbols or states:
  - string parsing of `chart_id` inside `_birth_context`;
  - date, time, or place available only in `chart_id`;
  - `birth_context` examples missing `birth_date`, `birth_time_local`, `birth_place`, or `precision`;
  - unrelated personal fields in provider payloads.
- Required deterministic guard:
  - `python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py --tb=short`
  - `python -B -m pytest -q tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py --tb=short`
  - `rg -n "split\\(|fromisoformat|chart_id.*birth|birth.*chart_id" app/domain/llm/runtime app/domain/astrology/interpretation tests`
  - targeted `rg` from `backend` over the CS-371 Paris example directory.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend logic must not drift into unrelated API routing surfaces. | Targeted `rg`; backend `pytest`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Prompt-generation validation paths must point to collected pytest files. | `pytest` paths listed in Validation Plan. |
| Registry gap `birth-context-theme-astral` | No exact birth context guardrail was found for this contract. | Resolver output and targeted registry `rg`. |

Non-applicable examples retained to prevent scope drift:

- `RG-047` frontend inline styles is out of scope because no TSX or CSS surface is touched.
- `RG-052` frontend CSS namespaces is out of scope because no design-token or stylesheet migration is authorized.
- `RG-041` entitlement documentation is out of scope because no entitlement doc or security claim is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before payload snapshot | `_condamad/stories/CS-373-structurer-birth-context-theme-astral-llm-input/evidence/birth-context-before.json` | Capture current minimal birth context. |
| After payload snapshot | `_condamad/stories/CS-373-structurer-birth-context-theme-astral-llm-input/evidence/birth-context-after.json` | Prove structured birth context. |
| Schema snapshot | `_condamad/stories/CS-373-structurer-birth-context-theme-astral-llm-input/evidence/input-schema-after.json` | Prove schema shape. |
| Guard scan output | `_condamad/stories/CS-373-structurer-birth-context-theme-astral-llm-input/evidence/reintroduction-guard.txt` | Keep scan evidence. |
| Validation output | `_condamad/stories/CS-373-structurer-birth-context-theme-astral-llm-input/evidence/validation.txt` | Keep final lint and test commands. |
| Review output | `_condamad/stories/CS-373-structurer-birth-context-theme-astral-llm-input/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for birth context enrichment.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py` - typed birth context runtime contract.
- `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py` - canonical birth context population.
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` - provider-visible `birth_context` projection.
- `backend/app/domain/llm/configuration/theme_astral_contracts.py` - versioned input schema for birth context.
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` - provider payload birth context tests.
- `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py` - schema persistence proof.
- `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py` - handoff proof.
- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md` - JSON structure documentation.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/*-provider-payload.json` - regenerated examples.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/README.md` - example interpretation note.

Likely tests:

- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py`
- `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no API route is touched.
- `backend/app/infra/**` - out of scope; no persistence adapter change is authorized.
- `backend/alembic/**` - out of scope; no schema migration is authorized by this story.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

All Python commands must run after:

- `.\.venv\Scripts\Activate.ps1`

From `backend`:

- VC1: `ruff format .`
- VC2: `ruff check .`
- VC3: `python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py --tb=short`
- VC4: `python -B -m pytest -q tests/integration/test_theme_astral_prompt_contract_persistence.py --tb=short`
- VC5: `python -B -m pytest -q tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py --tb=short`
- VC6: `python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py --tb=short`
- VC7: `rg -n "split\\(|fromisoformat|chart_id.*birth|birth.*chart_id" app/domain/llm/runtime app/domain/astrology/interpretation tests`
- VC8: `rg -n "birth_date|birth_time_local|birth_place|precision|coordinates_known" app/domain/llm app/domain/astrology tests`

From repository root:

- VC9: `rg -n "birth_date|birth_time_local|birth_place|Europe/Paris|Paris|France|1973-04-24|11:00"`
  `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1`
- VC10: `rg -n "scenario complet.*intermediate|chart_id"`
  `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
  `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/README.md`
- VC11: `rg -n "first_name|last_name|email|phone|address|birth_name" backend/app/domain/llm/runtime backend/tests`
  `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1`
- VC12: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-373-structurer-birth-context-theme-astral-llm-input/evidence/validation.txt').exists()"`

Interpretation rule:

- VC7 must return no runtime parsing path for `chart_id`; test fixtures may mention blocked strings only as guard evidence.
- VC10 may still find `chart_id` as technical identifier, but not wording that birth data is only auditable through `intermediate-data.json`.
- VC11 must return no unrelated personal field in provider payload code, tests, or regenerated examples.

## Regression Risks

- Adding fields only in examples would leave runtime provider payloads unchanged.
- Adding provider fields without a typed runtime contract would preserve ad hoc ownership.
- Parsing `chart_id` would turn a display identifier into a hidden contract.
- Emitting coordinates without precision flags would make missing or derived data ambiguous.
- Adding unrelated personal data would broaden the LLM-visible payload beyond the source brief.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all new or significantly modified Python files documented with French module comments and French docstrings for public or non-trivial code.
- Do not add a base folder under `backend/` without explicit user agreement.
- Do not parse `chart_id` to derive birth context fields.
- Keep LLM-visible personal data minimized to the fields authorized by this story.

## References

- `_story_briefs/cs-373-structurer-birth-context-theme-astral-llm-input-v1.md`
- `backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py`
- `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py`
- `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`
- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1`
