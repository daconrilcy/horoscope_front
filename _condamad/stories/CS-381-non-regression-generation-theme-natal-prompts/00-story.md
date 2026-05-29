# Story CS-381 non-regression-generation-theme-natal-prompts: Prove Natal Generation And Enriched Prompt Regression
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-381-non-regression-generation-theme-natal-et-enrichissement-prompts.md`.
- Selected mode: Repo-informed story.
- Problem statement: after CS-363 to CS-378, natal chart creation can return `200 OK` while the client rendering or
  enriched `theme_astral` prompt payload regresses in the same user flow.
- Source-alignment evidence: the story preserves the brief stakes by proving `POST /v1/users/me/natal-chart`, latest
  reload, expert rendering, provider payload enrichment, and legacy-carrier guards in one bounded validation slice.

## Objective

Add an automated non-regression validation proving that a logged-in user can generate a natal chart with known birth time
while the public UI payload and the enriched `theme_astral_llm_input_v1` provider payload remain distinct and coherent.

## Target State

- A local end-to-end or integration scenario logs in and saves birth data for `1973-04-24 11:00`, Paris, France.
- `POST /v1/users/me/natal-chart` returns an exploitable public natal chart payload with complete traditional conditions.
- `GET /v1/users/me/natal-chart/latest` reloads the same public contract after creation.
- The expert panel projection renders without a React error boundary for the generated chart.
- Backend validation proves `theme_astral_llm_input_v1` includes structured `birth_context` and prompt-visible enrichment.
- Provider payload validation proves `chart_json` and `natal_data` are not the primary prompt source.
- No real LLM provider call is part of standard validation.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-381-non-regression-generation-theme-natal-et-enrichissement-prompts.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-381`.
- Evidence 3: targeted inventory found existing natal frontend tests under `frontend/src/tests` and e2e specs under `frontend/e2e`.
- Evidence 4: targeted reads found `POST /me/natal-chart` and `GET /me/natal-chart/latest` in `backend/app/api/v1/routers/public/users.py`.
- Evidence 5: targeted reads found `traditional_conditions` consumption in `frontend/src/features/natal-chart/NatalExpertPanel.tsx`.
- Evidence 6: targeted reads found `birth_context` and prompt payload assembly in `theme_astral_provider_payload_builder.py`.
- Evidence 7: `resolve_guardrails.py` selected backend API, prompt-generation, and frontend validation guardrails for this scope.
- Source stakes retained: real user flow proof, no provider dependency, public/provider payload separation, no legacy carrier revival.

## Domain Boundary

- Domain: natal-generation-regression-validation
- In scope:
  - End-to-end or integration validation for birth profile save and natal chart generation.
  - API assertions for `POST /v1/users/me/natal-chart` and `GET /v1/users/me/natal-chart/latest`.
  - UI assertion for `NatalExpertPanel` rendering without React error boundary.
  - Backend provider-payload assertion for `theme_astral_llm_input_v1` enrichment.
  - Guards preventing `chart_json` or `natal_data` from becoming the primary prompt source.
- Out of scope:
  - Real LLM provider calls, commercial plan changes, auth redesign, DB schema changes, i18n changes, styling work, and migrations.
- Explicit non-goals:
  - No new prompt editorial content.
  - No full browser matrix.
  - No broad city coverage beyond the Paris fixture.
  - No committed `.env` file or secret.
  - No frontend redesign or CSS refactor.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a cross-stack natal regression validation contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add or extend tests and evidence only around natal generation and prompt payload enrichment.
  - Keep production route behavior, public payload names, and provider payload names unchanged.
  - Keep real provider execution optional and outside standard CI validation.
- Additional validation rules:
  - `TestClient` or Playwright network assertions must inspect `POST /v1/users/me/natal-chart`.
  - Runtime API proof must name `app.routes` and `app.openapi()` for the natal endpoints.
  - Backend prompt validation must assert structured `birth_context` and enriched prompt-visible blocks.
  - Static guards must fail on primary prompt construction from `chart_json` or `natal_data`.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the local environment cannot provide a deterministic geocoding fixture or mock for Paris.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `TestClient`, Playwright, `app.routes`, and `app.openapi()` prove the real natal route flow. |
| Baseline Snapshot | yes | Before/after artifacts prove public generation and provider enrichment coexist. |
| Ownership Routing | yes | UI payload, API route, and provider payload assertions must stay in their canonical owners. |
| Allowlist Exception | no | No broad allowlist handling is authorized for this non-regression proof. |
| Contract Shape | yes | Public payload fields and provider prompt fields are separate contracts. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Legacy carrier sources and real provider calls must stay outside standard validation. |
| Persistent Evidence | yes | Validation output and scenario notes must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Login flow creates a natal chart. | Evidence profile: json_contract_shape; `pnpm --dir frontend test:e2e -- --grep "natal"`. |
| AC2 | Known time returns traditions. | Evidence profile: json_contract_shape; `TestClient`; `pytest -q backend/tests/integration/astrology/test_natal_generation_regression.py`. |
| AC3 | Latest reload keeps contract. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/integration/astrology/test_natal_generation_regression.py`. |
| AC4 | Expert panel renders the generated payload. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalExpertPanel BirthProfilePage`. |
| AC5 | Provider payload keeps birth context. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`. |
| AC6 | Enriched prompt blocks stay present. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`. |
| AC7 | UI payload stays provider-distinct. | Evidence profile: ast_architecture_guard; `AST guard`; `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`. |
| AC8 | Legacy carrier sources do not drive prompts. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans `chart_json` and `natal_data` prompt handoff usage. |
| AC9 | Standard validation skips real providers. | Evidence profile: targeted_forbidden_symbol_scan; `pytest`; `rg -n "provider_smoke" backend/tests frontend/e2e`. |
| AC10 | Runtime route inventory includes natal endpoints. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`. |
| AC11 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect existing natal E2E, frontend unit, backend API, and provider payload tests. (AC: AC1, AC5)
- [ ] Task 2: Add or extend the login and birth-profile scenario using isolated fixture data or the authorized test user. (AC: AC1)
- [ ] Task 3: Assert `POST /v1/users/me/natal-chart` status and payload shape for known birth time. (AC: AC2)
- [ ] Task 4: Assert `GET /v1/users/me/natal-chart/latest` reloads the same public contract. (AC: AC3)
- [ ] Task 5: Assert `NatalExpertPanel` renders generated public payload without a page-level error state. (AC: AC4)
- [ ] Task 6: Add backend prompt payload assertions for `birth_context` and enriched prompt-visible blocks. (AC: AC5, AC6)
- [ ] Task 7: Add architecture guards separating public UI payload from provider prompt payload. (AC: AC7, AC8)
- [ ] Task 8: Add route inventory proof for `app.routes` and `app.openapi()` covering both natal endpoints. (AC: AC10)
- [ ] Task 9: Document local preconditions and persist validation outputs under story evidence. (AC: AC9, AC11)

## Files to Inspect First

- `frontend/e2e/**` - existing browser scenarios and login helpers.
- `frontend/src/pages/BirthProfilePage.tsx` - birth profile save and post-generation query behavior.
- `frontend/src/features/birth-profile/components/BirthProfileNatalGenerationSection.tsx` - generation CTA behavior.
- `frontend/src/features/natal-chart/NatalExpertPanel.tsx` - expert rendering witness.
- `frontend/src/api/natal-chart/index.ts` - public natal chart API client.
- `backend/app/api/v1/routers/public/users.py` - `POST /me/natal-chart` and latest route ownership.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - natal generation and handoff service.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - canonical LLM input boundary.
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` - provider payload enrichment owner.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/**` - fixture evidence.
- `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/00-story.md` - expected prior repair context.
- `_condamad/stories/CS-380-durcir-natal-expert-panel-contre-payloads-partiels/00-story.md` - expected prior UI hardening context.

## Runtime Source of Truth

- Primary source of truth:
  - `TestClient` or Playwright network assertions for `POST /v1/users/me/natal-chart`.
  - `TestClient` or Playwright network assertions for `GET /v1/users/me/natal-chart/latest`.
  - `app.routes` and `app.openapi()` loaded from the FastAPI app for route inventory proof.
  - Vitest or Playwright rendering proof for `NatalExpertPanel`.
  - Backend pytest assertions over the provider payload builder.
- Secondary evidence:
  - Targeted `rg` scans for forbidden primary prompt handoff from `chart_json` or `natal_data`.
- Static scans alone are not sufficient for this story because:
  - The brief requires coexistence proof in a real generation flow after API `200 OK`.

## Contract Shape

- Contract type:
  - Existing API route behavior, public JSON payload, and provider prompt JSON payload.
- Fields:
  - `traditional_conditions`: complete in the public payload when birth time is known.
  - `traditional_conditions`: absent only for a controlled `no_time` degraded state.
  - `birth_context`: structured inside `theme_astral_llm_input_v1`.
  - `theme_astral_llm_input_v1`: provider payload input version under test.
  - `chart_json`: runtime-only or audit-only carrier, not the primary prompt source.
  - `natal_data`: runtime-only or audit-only carrier, not the primary prompt source.
- Required fields:
  - `traditional_conditions` for the known-time Paris scenario.
  - `birth_context` in provider prompt input.
  - Enriched prompt-visible blocks already introduced by CS-363 to CS-378.
- Optional fields:
  - `traditional_conditions` may be absent only in the explicit `no_time` degraded scenario.
- Status codes:
  - `200` for successful `POST /v1/users/me/natal-chart`.
  - `200` for successful `GET /v1/users/me/natal-chart/latest`.
- Serialization names:
  - Existing snake_case API names stay unchanged.
- Frontend type impact:
  - Frontend test fixtures may be extended, but public API type names must stay unchanged.
- Generated contract impact:
  - `app.openapi()` must continue exposing both natal chart endpoints with their existing methods.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts/evidence/natal-regression-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts/evidence/natal-regression-after.txt`
- Expected invariant:
  - The intended delta is added validation coverage and persisted evidence, not a production contract change.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Public natal route assertions | `backend/tests/integration/astrology` | Provider payload builder tests |
| Browser generation flow | `frontend/e2e` | Backend unit tests |
| Expert panel render assertion | `frontend/src/tests/NatalExpertPanel.test.tsx` | API client normalization |
| Provider payload enrichment | `backend/tests/integration/llm` or `backend/tests/llm_orchestration` | Frontend fixtures |
| LLM input boundary guard | `backend/tests/architecture` | E2E-only assertions |

## Mandatory Reuse / DRY Constraints

- Reuse existing login helpers, API clients, natal chart fixtures, and provider payload fixture builders.
- Reuse the Paris `1973-04-24 11:00` example already present in prompt-generation cartography artifacts.
- Keep public payload assertions and provider payload assertions separate instead of duplicating the same fixture shape.
- Do not add external packages.
- Do not duplicate geocoding setup when an existing mock or fixture can be reused.

## No Legacy / Forbidden Paths

- No legacy carrier may become the source of truth for prompt construction.
- No compatibility adapter may merge public UI payload and provider prompt payload.
- No fallback provider call may run during standard local or CI validation.
- Forbidden primary prompt sources: `chart_json`, `natal_data`.
- Forbidden validation shortcut: proving only builders without exercising natal chart creation.

## Reintroduction Guard

- Keep `chart_json` and `natal_data` out of primary prompt handoff assertions.
- Keep real provider smoke tests opt-in through existing markers or environment gates.
- Require deterministic guards:
  - `rg -n "chart_json|natal_data" backend/app/services/llm_generation/natal backend/app/domain/llm/runtime backend/tests`
  - `rg -n "provider_smoke|OPENAI_API_KEY|ANTHROPIC_API_KEY" backend/tests frontend/e2e`
  - `python -c "from app.main import app; paths={getattr(r,'path','') for r in app.routes}; assert '/v1/users/me/natal-chart' in paths"`
  - `python -c "from app.main import app; assert '/v1/users/me/natal-chart' in app.openapi()['paths']"`

## Regression Guardrails

| Guardrail | Applied invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Route validation stays in API tests, not route business logic moves. | `pytest`; route diff review. |
| RG-003 `converge-api-v1-route-architecture` | Natal endpoints remain registered through canonical API routing. | `app.routes`; `app.openapi()`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Prompt validation commands point to collected pytest files. | `pytest`; collected paths. |
| RG-047 `CS-029-encadrer-styles-inline-statiques-frontend` | UI assertion work must not add inline TSX style. | `rg` style scan; `pnpm lint`. |
| Registry gap | No exact guardrail for natal generation plus enriched prompt coexistence was selected. | Local E2E and pytest proof. |

Non-applicable examples:

- RG-007 is not selected because admin LLM observability endpoints are outside scope.
- RG-027 is not selected because prediction domain infra is outside scope.
- RG-041 is not selected because entitlement documentation is outside scope.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Scenario preconditions | `_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts/evidence/preconditions.md` | Document local services, data, and mocks. |
| Baseline output | `_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts/evidence/natal-regression-before.txt` | Capture pre-implementation failure or gap. |
| Final output | `_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts/evidence/natal-regression-after.txt` | Prove the complete scenario. |
| Validation output | `_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts/evidence/validation.txt` | Keep command results. |
| Review output | `_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no broad allowlist handling is authorized for this non-regression proof.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `frontend/e2e/*natal*.spec.ts` - add or extend the browser generation scenario.
- `frontend/src/tests/BirthProfilePage.test.tsx` - cover generation page behavior without a browser dependency.
- `frontend/src/tests/NatalExpertPanel.test.tsx` - prove expert panel render for generated public payload.
- `backend/tests/integration/astrology/test_natal_generation_regression.py` - assert public route payloads with `TestClient`.
- `backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py` - assert provider payload enrichment.
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` - assert prompt-visible enriched blocks.
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` - guard payload separation.
- `_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts/evidence/**` - persist evidence artifacts.

Likely tests:

- `backend/tests/integration/astrology/test_natal_generation_regression.py`
- `backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`
- `frontend/src/tests/NatalExpertPanel.test.tsx`
- `frontend/src/tests/BirthProfilePage.test.tsx`
- `frontend/e2e/*natal*.spec.ts`

Files not expected to change:

- `backend/app/infra/**` - no persistence adapter change is in scope.
- `backend/alembic/**` - no schema migration is in scope.
- `frontend/src/styles/**` - no global styling work is in scope.
- `backend/app/domain/llm/configuration/**` - no prompt editorial change is in scope.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1; ruff format backend`
- VC2: `.\.venv\Scripts\Activate.ps1; ruff check backend`
- VC3: `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -B -m pytest -q backend/tests --tb=short -k "natal_chart or theme_astral or llm_astrology_input"`
- VC4: `pnpm --dir frontend lint`
- VC5: `pnpm --dir frontend test -- NatalExpertPanel BirthProfilePage natalChartApi`
- VC6: `pnpm --dir frontend build`
- VC7: `pnpm --dir frontend test:e2e -- --grep "natal"`
- VC8: `rg -n "chart_json|natal_data" backend/app/services/llm_generation/natal backend/app/domain/llm/runtime backend/tests`
- VC9: `rg -n "style=" frontend/e2e frontend/src/tests frontend/src/features/natal-chart frontend/src/pages`
- VC10: `rg -n "provider_smoke|OPENAI_API_KEY|ANTHROPIC_API_KEY" backend/tests frontend/e2e`
- VC11: `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -c "from app.main import app; assert any('natal-chart' in r.path for r in app.routes)"`
- VC12: `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -c "from app.main import app; assert '/v1/users/me/natal-chart' in app.openapi()['paths']"`
- VC13: `.\.venv\Scripts\Activate.ps1; python -c "import os; assert os.path.isdir('_condamad/stories/CS-381-non-regression-generation-theme-natal-prompts/evidence')"`

## Regression Risks

- A test could pass by checking only backend builders while the generated page still crashes after API `200 OK`.
- A browser scenario could prove only UI rendering while losing enriched provider prompt assertions.
- A permissive fixture could normalize `traditional_conditions` absence for known birth time.
- A provider smoke test could leak into standard validation and require external credentials.
- A static scan could flag audit-only mentions of `chart_json` or `natal_data`; findings must be classified by source role.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep the public UI payload and provider LLM payload distinct.
- Use existing fixtures and helpers before adding new ones.
- Keep real provider execution opt-in and outside the default validation path.
- Persist local preconditions and validation output under this story evidence directory.

## References

- `_story_briefs/cs-381-non-regression-generation-theme-natal-et-enrichissement-prompts.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/00-story.md`
- `_condamad/stories/CS-380-durcir-natal-expert-panel-contre-payloads-partiels/00-story.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
