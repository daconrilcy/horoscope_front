# Story CS-379 stabiliser-contrat-public-generation-theme-natal: Stabilize Public Natal Chart Generation Contract
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-379-stabiliser-contrat-public-generation-theme-natal-apres-enrichissement-prompts.md`.
- Selected mode: Repo-informed story.
- Problem statement: after prompt enrichment, `POST /v1/users/me/natal-chart` can publish partial `traditional_conditions`
  entries that make the existing natal expert consumer read missing `hayz.is_hayz`.
- Source-alignment evidence: this story keeps the first proof on the `POST` payload, then checks `GET /latest` and
  provider-payload boundaries without moving the fix to React.

## Objective

Restore a stable backend public JSON contract for generated natal charts while preserving the recent
`theme_astral_llm_input_v1` enrichment used by prompt/provider execution.

## Target State

- `POST /v1/users/me/natal-chart` returns a displayable public payload for a reliable full birth context.
- `GET /v1/users/me/natal-chart/latest` returns the same public contract after persistence reload.
- `traditional_conditions` is `null` only for reliable-calculation limits such as `no_time` or `no_location_no_time`.
- Every exposed traditional planet entry contains boolean `hayz.is_hayz` and boolean `rejoicing.is_rejoicing`.
- Prompt/provider payload construction remains separated from the public natal-chart payload.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-379-stabiliser-contrat-public-generation-theme-natal-apres-enrichissement-prompts.md` -
  source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-379`.
- Evidence 3: targeted `Test-Path` checks confirm the required backend and frontend source files exist.
- Evidence 4: targeted `rg` found `traditional_conditions` serialization in `backend/app/services/chart/json_builder.py`.
- Evidence 5: targeted `rg` found `hayz.is_hayz` and `rejoicing.is_rejoicing` consumption in
  `frontend/src/features/natal-chart/NatalExpertPanel.tsx`.
- Evidence 6: `resolve_guardrails.py` selected backend/API and prompt-generation validation guardrails for this scope.
- Source stakes retained: user-visible crash, public contract drift, plan-independent traditional block policy,
  prompt/provider enrichment preservation, and no UI-side fabricated astrology.

## Domain Boundary

- Domain: backend-api
- In scope:
  - Public natal-chart JSON projection for `POST /v1/users/me/natal-chart`.
  - Public natal-chart JSON projection for `GET /v1/users/me/natal-chart/latest`.
  - Backend normalization of exposed `traditional_conditions` sub-contracts.
  - Regression tests proving prompt/provider payload enrichment remains intact.
- Out of scope:
  - Frontend component edits, database schema, auth, i18n, styling, build tooling, migrations, and real LLM calls.
- Explicit non-goals:
  - No React crash masking or UI-side astrology value synthesis.
  - No prompt wording rewrite.
  - No provider invocation against a real external LLM.
  - No new public endpoint.

## Operation Contract

- Operation type: update
- Primary archetype: api-contract-change
- Archetype reason: the story stabilizes existing public API JSON responses and provider-boundary evidence.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Change only the public natal-chart projection and its direct backend normalization path.
  - Preserve `theme_astral_llm_input_v1` and provider payload enrichment outside justified public-projection fields.
  - Keep plan tier out of the decision that sets `traditional_conditions` to `null`.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: reliable full birth-context computation cannot produce a complete traditional condition entry.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, `TestClient`, and pytest prove API behavior. |
| Baseline Snapshot | yes | Before/after payload artifacts prove the intended public JSON delta. |
| Ownership Routing | yes | Public projection, domain normalization, runtime assembly, and provider payload owners must stay separated. |
| Allowlist Exception | no | No broad allowlist handling is authorized for this contract stabilization. |
| Contract Shape | yes | The response fields and traditional sub-contracts have exact shape rules. |
| Batch Migration | no | No batch migration or schema conversion is in scope. |
| Reintroduction Guard | yes | Prompt carriers and alternate projection paths must stay out of the new fix. |
| Persistent Evidence | yes | POST, latest, OpenAPI, and validation artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | POST publishes complete traditional entries. | Evidence profile: json_contract_shape; `pytest` covers the POST contract path. |
| AC2 | Latest reload preserves the same public shape. | Evidence profile: json_contract_shape; `pytest -q app/tests/integration/test_user_natal_chart_api.py -k latest`. |
| AC3 | Plan tier never nulls reliable traditional data. | Evidence profile: ast_architecture_guard; `pytest -q app/tests/integration/test_user_natal_chart_api.py -k plan`. |
| AC4 | No-time modes keep time-dependent blocks neutral. | Evidence profile: json_contract_shape; `pytest -q app/tests/unit/test_chart_json_builder.py -k no_time`. |
| AC5 | Runtime route metadata remains unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`. |
| AC6 | Prompt enrichment remains present. | Evidence profile: targeted_forbidden_symbol_scan; `pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`. |
| AC7 | Prompt carriers are not reintroduced. | Evidence profile: no_legacy_contract; `rg -n "chart_json\|natal_data\|legacy" app tests`. |
| AC8 | Invalid public contract stops success evidence. | Evidence profile: api_error_shape_contract; `pytest -q app/tests/integration/test_user_natal_chart_api.py -k contract`. |
| AC9 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |

## Implementation Tasks

- [ ] Task 1: Capture the failing `POST /v1/users/me/natal-chart` public payload shape before changing code. (AC: AC1, AC9)
- [ ] Task 2: Locate the contract drift across normalization, assembly, JSON building, persistence, and latest reload. (AC: AC1, AC2)
- [ ] Task 3: Stabilize only the canonical backend public projection boundary for traditional conditions. (AC: AC1, AC3)
- [ ] Task 4: Preserve time-dependent neutralization for `no_time` and `no_location_no_time`. (AC: AC4)
- [ ] Task 5: Prove `POST`, `GET /latest`, `app.routes`, and `app.openapi()` behavior from the loaded app. (AC: AC2, AC5)
- [ ] Task 6: Prove provider payload enrichment still exposes `theme_astral_llm_input_v1`. (AC: AC6)
- [ ] Task 7: Add guards against prompt-carrier reintroduction in the touched runtime path. (AC: AC7)
- [ ] Task 8: Persist before/after payload, OpenAPI, and validation artifacts under this story. (AC: AC8, AC9)

## Files to Inspect First

- `backend/app/services/chart/json_builder.py` - public chart JSON projection and traditional serialization.
- `backend/app/domain/astrology/advanced_conditions/traditional_condition_normalizer.py` - traditional condition normalization.
- `backend/app/domain/astrology/advanced_conditions/contracts.py` - traditional condition data contracts.
- `backend/app/domain/astrology/runtime/natal_result_assembler.py` - natal result assembly.
- `backend/app/domain/astrology/runtime/natal_calculation_nodes.py` - runtime production of traditional conditions.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - LLM input boundary.
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` - provider payload builder.
- `backend/app/tests/integration/test_user_natal_chart_api.py` - existing natal API integration surface.
- `backend/app/tests/unit/test_chart_json_builder.py` - existing chart JSON projection tests.
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` - provider enrichment tests.
- `frontend/src/api/natal-chart/index.ts` - public client type witness only; no frontend edit is expected.
- `frontend/src/features/natal-chart/NatalExpertPanel.tsx` - crash witness only; no frontend edit is expected.

## Runtime Source of Truth

- Primary source of truth:
  - `TestClient` calls against `POST /v1/users/me/natal-chart` and `GET /v1/users/me/natal-chart/latest`.
  - `app.routes` and `app.openapi()` from the loaded FastAPI app.
- Secondary evidence:
  - Targeted `rg` scans for prompt carriers and public projection ownership.
- Static scans alone are not sufficient for this story because:
  - POST response shape, persisted latest reload, and OpenAPI exposure must be proven from runtime behavior.

## Contract Shape

- Contract type:
  - Existing API responses and public JSON fields.
- Fields:
  - `traditional_conditions`: object for reliable full birth context, `null` for `no_time` and `no_location_no_time`.
  - `traditional_conditions.by_planet.hayz.is_hayz`: boolean for every exposed planet entry.
  - `traditional_conditions.by_planet.rejoicing.is_rejoicing`: boolean for every exposed planet entry.
  - `advanced_conditions`: preserved enriched block.
  - `dignities`: preserved enriched block.
  - `planet_condition_profiles`: preserved enriched block.
  - `planet_condition_signals`: preserved enriched block.
  - `dominant_planets`: preserved enriched block.
  - `interpretation_adapter`: preserved enriched block.
  - `theme_astral_llm_input_v1`: preserved provider payload contract outside the public projection.
- Required fields:
  - `hayz.is_hayz` and `rejoicing.is_rejoicing` for every traditional planet entry that remains exposed.
- Optional fields:
  - `traditional_conditions` may be `null` only when reliable traditional calculation is impossible.
- Status codes:
  - `200` for successful `POST /v1/users/me/natal-chart` only when the public payload contract is valid.
  - `200` for successful `GET /v1/users/me/natal-chart/latest` only when the persisted public payload contract is valid.
- Serialization names:
  - JSON keys remain snake_case as consumed by the existing frontend API types.
- Frontend type impact:
  - none; frontend files are only contract witnesses in this story.
- Generated contract impact:
  - `app.openapi()` must continue exposing both existing natal-chart paths without introducing a new route.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/evidence/post-before.json`
  - `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/evidence/latest-before.json`
  - `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/evidence/openapi-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/evidence/post-after.json`
  - `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/evidence/latest-after.json`
  - `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/evidence/openapi-after.json`
- Expected invariant:
  - The only intended public surface delta is completion or justified exclusion of invalid `traditional_conditions` entries.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Public chart JSON projection | `backend/app/services/chart/json_builder.py` | `frontend/src/**` |
| Traditional condition normalization | `backend/app/domain/astrology/advanced_conditions/**` | API router handlers |
| Natal runtime assembly | `backend/app/domain/astrology/runtime/**` | Provider payload builder |
| Prompt/provider payload | `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` | Public JSON patch path |

## Mandatory Reuse / DRY Constraints

- Reuse the existing normalizer, runtime assembly, and chart JSON builder entry points.
- Add shared helper logic only when it removes duplicate contract checks across POST and latest reload tests.
- Do not duplicate public payload shaping in API router code.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy prompt carrier may be used to repair the public natal-chart payload.
- No compatibility projection path may be added for this contract.
- No fallback route, alternate API path, or UI masking path may be added.
- Forbidden prompt-carrier surfaces for this story: `chart_json`, `natal_data`, broad legacy payload restoration.

## Reintroduction Guard

- Keep `chart_json` and `natal_data` out of the new theme-astral prompt/provider runtime path touched by this story.
- Keep the public projection separate from `theme_astral_llm_input_v1`.
- Require deterministic guards:
  - `rg -n "chart_json|natal_data|legacy" app tests`
  - `python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
  - `python -B -m pytest -q app/tests/integration/test_user_natal_chart_api.py -k "natal_chart or traditional_conditions"`

## Regression Guardrails

| Guardrail | Applied invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | API handlers must not absorb business projection logic. | `pytest`; route owner review. |
| RG-003 `converge-api-v1-route-architecture` | Existing natal API routes stay registered through the canonical app. | `app.routes`; `app.openapi()`. |
| RG-007 `converge-admin-llm-observability-router` | API/OpenAPI behavior must be proven at runtime for touched routes. | `python` OpenAPI check; `pytest`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Prompt-generation validation paths must stay collected and current. | `pytest` provider payload path. |
| Registry gap | No exact guardrail for public natal `traditional_conditions` shape was selected. | Add local story evidence only. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| POST baseline payload | `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/evidence/post-before.json` | Show pre-fix creation payload. |
| POST final payload | `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/evidence/post-after.json` | Prove creation payload shape. |
| Latest baseline payload | `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/evidence/latest-before.json` | Show pre-fix reload payload. |
| Latest final payload | `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/evidence/latest-after.json` | Prove reload payload shape. |
| OpenAPI baseline | `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/evidence/openapi-before.json` | Capture route contract before. |
| OpenAPI final | `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/evidence/openapi-after.json` | Capture route contract after. |
| Validation output | `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/evidence/validation.txt` | Keep command results. |
| Review output | `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no broad allowlist handling is authorized for this backend public-contract stabilization.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/services/chart/json_builder.py` - stabilize public traditional-condition serialization.
- `backend/app/domain/astrology/advanced_conditions/traditional_condition_normalizer.py` - enforce complete exposed entries.
- `backend/app/domain/astrology/advanced_conditions/contracts.py` - align contract types only for public-shape proof.
- `backend/app/domain/astrology/runtime/natal_result_assembler.py` - preserve runtime transfer into public projection.
- `backend/app/domain/astrology/runtime/natal_calculation_nodes.py` - preserve reliable and no-time condition policy.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - prove prompt enrichment boundary unchanged.
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` - prove provider payload boundary unchanged.
- `backend/app/tests/integration/test_user_natal_chart_api.py` - add POST and latest public contract tests.
- `backend/app/tests/unit/test_chart_json_builder.py` - add focused serialization and no-time tests.
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` - add or preserve enrichment proof.
- `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/evidence/**` - persist runtime evidence.

Likely tests:

- `backend/app/tests/integration/test_user_natal_chart_api.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`

Files not expected to change:

- `frontend/src/**` - out of scope; frontend is only a consumer witness.
- `backend/app/infra/**` - out of scope; no persistence adapter redesign is authorized.
- `backend/app/alembic/**` - out of scope; no database migration is authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `python -B -m pytest -q app/tests/integration/test_user_natal_chart_api.py -k "natal_chart or traditional_conditions" --tb=short`
- VC2: `python -B -m pytest -q app/tests/unit/test_chart_json_builder.py -k "traditional_conditions or no_time" --tb=short`
- VC3: `python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py --tb=short`
- VC4: `python -c "from app.main import app; assert any(getattr(r, 'path', '') == '/v1/users/me/natal-chart/latest' for r in app.routes)"`
- VC5: `python -c "from app.main import app; assert '/v1/users/me/natal-chart/latest' in app.openapi()['paths']"`
- VC6: `rg -n "chart_json|natal_data|legacy|llm_astrology_input_v1|theme_astral_llm_input_v1" app tests`
- VC7: `ruff format .`
- VC8: `ruff check .`
- VC9: `python -B -m pytest -q tests --tb=short -k "natal_chart or traditional_conditions or theme_astral_provider_payload"`

## Regression Risks

- A POST-only correction could leave persisted latest reload broken.
- A latest-only correction could hide the creation payload drift that triggers the crash.
- A plan-tier gate could incorrectly remove reliable traditional conditions.
- A prompt/provider change could reduce `theme_astral_llm_input_v1` enrichment.
- A UI patch could hide backend contract drift without fixing public API output.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the repository venv before every Python command.
- Start evidence capture with `POST /v1/users/me/natal-chart`, then compare `GET /v1/users/me/natal-chart/latest`.
- Keep frontend files read-only unless the user explicitly creates a separate frontend story.

## References

- `_story_briefs/cs-379-stabiliser-contrat-public-generation-theme-natal-apres-enrichissement-prompts.md`
- `_condamad/stories/regression-guardrails.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
