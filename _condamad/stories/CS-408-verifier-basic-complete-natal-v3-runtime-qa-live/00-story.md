# Story CS-408 verifier-basic-complete-natal-v3-runtime-qa-live: Verifier Basic Complete Natal V3 Runtime Et QA Live
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-403-verifier-basic-complete-natal-v3-en-runtime-et-qa-live.md`.
- Selected mode: Repo-informed story in Fast Story Writer Mode.
- Source problem: Basic complete doit prouver en runtime qu'il utilise le pipeline natal V3, sans provider reel non controle.
- Source stakes: resolution d'assembly, metas gateway, persistance, rejet V1/V2, quota, DOM public et rapport QA.
- Dependencies from source: CS-401, CS-402, CS-398 and CS-399 must be treated as expected upstream contracts.
- Source-alignment evidence: objectif, AC, taches, preuves et guardrails couvrent toutes les primitives du brief sans deplacer le sujet.

## Objective

Produire une preuve runtime et QA authentifiee que Basic complete utilise `natal_interpretation`,
`natal/interpretation/basic/fr-FR`, `AstroResponse_v3` et `narrative_natal_reading_v1`, sans masquer un retour court V1/V2.

## Target State

- Une generation Basic complete nouvelle utilise `natal_interpretation`, pas `natal_interpretation_short`.
- La resolution observee pointe vers `natal/interpretation/basic/fr-FR`.
- Les metas gateway exposent `schema_version="v3"`, `validation_status`, `repair_attempted` et `fallback_triggered`.
- Une fixture Basic V3 valide persiste `narrative_natal_reading_v1` avec `used_astrological_elements` non vide.
- Une sortie courte V1/V2 injectee sur le chemin Basic complete est rejetee, auditee et absente des routes publiques.
- Le quota `natal_chart_long` reste debite uniquement apres acceptation persistante.
- Le DOM `/natal` montre la lecture narrative moderne sans fuite technique publique.
- Le rapport QA natal existant documente l'avant/apres, la cause racine et les fichiers touches.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-403-verifier-basic-complete-natal-v3-en-runtime-et-qa-live.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted; next available story number is `CS-408`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted lookup found `RG-149` to `RG-158` for natal V3 scope.
- Evidence 4: `resolve_guardrails.py` ran with backend runtime, frontend QA, quota and public DOM scope vectors.
- Evidence 5: `backend/app/domain/llm/runtime/adapter.py` maps `natal_interpretation` to the `interpretation` subfeature.
- Evidence 6: `backend/app/services/llm_generation/natal/interpretation_service.py` persists meta, payload and narrative reading data.
- Evidence 7: `backend/app/api/v1/routers/public/natal_interpretation.py` consumes quota only after non-rejected, non-cached response.
- Evidence 8: `frontend/src/features/natal-chart/NatalNarrativeReading.tsx` renders accessible narrative accordions.
- Repository structure alert: expected `backend`, `backend/app`, `backend/tests`, `frontend` and `frontend/src` roots exist.
- Scope vector:
  - operation `update`, domain `natal-runtime-qa`
  - paths `backend/app/domain/llm/runtime`, `backend/app/services/llm_generation/natal`, `backend/app/api/v1/routers/public`
  - paths `frontend/src/pages/NatalChartPage.tsx`, `frontend/src/features/natal-chart/NatalNarrativeReading.tsx`
  - tests `backend/tests/integration`, `backend/tests/unit`, `frontend/src/tests`
  - contracts `natal_interpretation`, `AstroResponse_v3`, `narrative_natal_reading_v1`, quota, public DOM

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| Basic complete generation | in scope | AC1, AC2, AC3, Task 1 |
| Fake gateway | in scope | AC1, AC3, AC5, Task 1 |
| `natal_interpretation` | in scope | AC1, Task 1 |
| `natal/interpretation/basic/fr-FR` | in scope | AC2, Task 2 |
| `AstroResponse_v3` | in scope | AC3, AC4, Task 3 |
| `narrative_natal_reading_v1` | in scope | AC4, AC9, Task 4 |
| `used_astrological_elements` | in scope | AC4, Task 4 |
| V1/V2 short output | in scope | AC5, AC6, Task 5 |
| Public metas | in scope | AC7, Task 6 |
| Quota after acceptance | in scope | AC8, Task 7 |
| Public `/natal` DOM | in scope | AC9, AC10, Task 8 |
| QA browser authenticated | in scope | AC11, Task 9 |
| QA closure report | in scope | AC12, Task 10 |
| Provider real calls | out of scope | Non-goals |
| Frontend restyle | out of scope | Non-goals |
| Astrology calculations | out of scope | Non-goals |

## Domain Boundary

- Domain: natal-runtime-qa
- In scope:
  - Backend integration evidence for Basic complete V3 resolution with fake gateway.
  - Backend catalog or seed evidence for `natal/interpretation/basic`.
  - Backend rejection evidence for injected V1/V2 short output.
  - Backend quota evidence for reject versus accept paths.
  - Frontend QA evidence limited to `/natal` public narrative rendering and denylist DOM checks.
  - QA closure report update for the natal Basic complete before and after state.
- Out of scope:
  - Real provider calls, frontend styles, commercial quota policy, `/natal` page redesign, astrology calculation changes and DB migrations.
- Explicit non-goals:
  - No frontend route rewrite, no prompt rewrite, no quota pricing change, no provider smoke against production credentials.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend runtime and QA evidence contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add tests, fixtures and QA artifacts proving the existing CS-401, CS-402, CS-398 and CS-399 contracts.
  - Add only targeted runtime guards required to make the proof deterministic.
  - Keep provider calls fake or locally controlled for automated tests.
  - Keep frontend implementation unchanged unless a public DOM leak or missing narrative rendering is proven.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: live QA requires a real provider call or production-like external dependency.
- Additional validation rules:
  - Use `pytest -q backend/tests/integration/test_natal_basic_complete_v3_runtime.py` for end-to-end fake-gateway runtime proof.
  - Use `pytest -q backend/tests/unit/test_natal_interpretation_service_v3_schema_guard.py` for V1/V2 rejection proof.
  - Use `pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py` for quota acceptance proof.
  - Use `pytest -q backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` for public boundary proof.
  - Use `app.routes`, `app.openapi()`, loaded config or generated manifest evidence for route and contract runtime checks.
  - Use `AST guard` or targeted `rg` for forbidden frontend fallback and backend downgrade patterns.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, fake gateway, `app.routes`, `app.openapi()` and runtime metas prove Basic complete V3. |
| Baseline Snapshot | yes | Before and after QA artifacts prove Basic complete moved from V2/free evidence to V3/basic evidence. |
| Ownership Routing | yes | Gateway, service, route, frontend and QA report responsibilities must stay canonical. |
| Allowlist Exception | no | No tolerance register is authorized for hiding V1/V2 Basic complete output. |
| Contract Shape | yes | Use case, assembly target, schema, public metas and narrative payload have exact required fields. |
| Batch Migration | no | No historical data migration or bulk remediation is in scope. |
| Reintroduction Guard | yes | Free/V1 routing and frontend masking must stay absent from Basic complete proof. |
| Persistent Evidence | yes | Runtime, frontend and QA artifacts must be persisted for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Basic complete uses `natal_interpretation`. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_natal_basic_complete_v3_runtime.py`. |
| AC2 | Basic complete uses the basic assembly. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_natal_basic_complete_v3_runtime.py` and VC6. |
| AC3 | Basic complete runtime uses schema V3. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_natal_basic_complete_v3_runtime.py`. |
| AC4 | Accepted Basic complete persists narrative. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_natal_basic_complete_v3_runtime.py`. |
| AC5 | Injected short V1/V2 output is rejected. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_natal_interpretation_service_v3_schema_guard.py`. |
| AC6 | Rejected short output stays private. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`. |
| AC7 | Public metas expose the expected V3 status fields. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_natal_basic_complete_v3_runtime.py`. |
| AC8 | Quota is consumed only after acceptance. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`. |
| AC9 | `/natal` renders modern narrative. | Evidence profile: frontend_typecheck_no_orphan; `pnpm --dir frontend test -- natalNarrativeReading`. |
| AC10 | `/natal` public DOM has no leak. | Evidence profile: frontend_typecheck_no_orphan; `pnpm --dir frontend test -- natalPublicDomGuard`. |
| AC11 | Authenticated QA evidence is recorded. | Evidence profile: baseline_before_after_diff; `python` checks the QA report path. |
| AC12 | QA report names the root cause. | Evidence profile: baseline_before_after_diff; `python` checks the QA report path. |
| AC13 | App runtime contracts remain loadable. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`. |
| AC14 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |
| AC15 | QA report names changed files. | Evidence profile: baseline_before_after_diff; `python` checks the QA report path. |

## Implementation Tasks

- [ ] Task 1: Add fake-gateway integration proof for Basic complete `natal_interpretation`. (AC: AC1, AC3, AC7)
- [ ] Task 2: Add catalog or seed proof that `natal/interpretation/basic/fr-FR` exists and is published. (AC: AC2, AC14)
- [ ] Task 3: Add or update a valid Basic V3 fixture with `AstroResponse_v3` shape. (AC: AC3, AC4)
- [ ] Task 4: Assert persisted `narrative_natal_reading_v1` and non-empty `used_astrological_elements`. (AC: AC4)
- [ ] Task 5: Inject a V1/V2 short output into Basic complete and assert audited rejection. (AC: AC5, AC6)
- [ ] Task 6: Assert public metas `use_case`, `schema_version`, `validation_status`, `repair_attempted`, `fallback_triggered`. (AC: AC7)
- [ ] Task 7: Assert quota is unchanged on rejection and debited once on acceptance. (AC: AC8)
- [ ] Task 8: Verify `/natal` public DOM renders `NatalNarrativeReading` without technical leak tokens. (AC: AC9, AC10)
- [ ] Task 9: Run authenticated browser QA with the test user when local controlled runtime is available. (AC: AC11)
- [ ] Task 10: Update the natal QA closure report with root cause, before and after proof and changed files. (AC: AC12, AC15)
- [ ] Task 11: Record `app.routes` and `app.openapi()` runtime evidence for public route contract loadability. (AC: AC13)
- [ ] Task 12: Persist validation output and QA artifacts under this story directory. (AC: AC14)

## Files to Inspect First

- `_story_briefs/cs-401-router-basic-complete-vers-assembly-natale-v3.md`
- `_story_briefs/cs-402-refuser-downgrade-schema-v3-lecture-natale-complete.md`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/features/natal-chart/NatalNarrativeReading.tsx`
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`

## Runtime Source of Truth

- Primary source of truth:
  - `pytest`, fake gateway calls, `TestClient`, `app.routes`, `app.openapi()`, gateway metas and persisted payload assertions.
- Runtime evidence:
  - `pytest -q backend/tests/integration/test_natal_basic_complete_v3_runtime.py`.
  - `pytest -q backend/tests/unit/test_natal_interpretation_service_v3_schema_guard.py`.
  - `pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`.
  - `pytest -q backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`.
- Secondary evidence:
  - Targeted `rg` scans for free/V1 routing and frontend fallback masking.
  - `python -B -c "from app.main import app; assert app.routes; assert app.openapi()"`.
- Static scans alone are not sufficient for this story because:
  - Assembly resolution, quota, persistence and DOM behavior must be proven from runtime or browser-visible evidence.

## Contract Shape

- Contract type:
  - Backend runtime QA contract plus public `/natal` rendering proof.
- Fields:
  - `use_case`: `natal_interpretation`.
  - `assembly_target`: `natal/interpretation/basic/fr-FR`.
  - `output_schema`: `AstroResponse_v3`.
  - `schema_version`: `v3` for accepted Basic complete.
  - `validation_status`: accepted state for valid V3, rejected state for injected V1/V2.
  - `repair_attempted`: `false` for the valid Basic V3 fixture path.
  - `fallback_triggered`: `false` for the valid Basic V3 fixture path.
  - `narrative_natal_reading_v1`: present for accepted Basic complete public data.
  - `used_astrological_elements`: non-empty for accepted Basic complete narrative chapters.
- Required fields:
  - `use_case`, `schema_version`, `validation_status`, `repair_attempted`, `fallback_triggered`, `narrative_natal_reading_v1`.
- Optional fields:
  - `latency_ms`, `request_id`, `prompt_version_id`, `tokens_in`, `tokens_out`.
- Status codes:
  - Existing natal public routes must keep their documented success and rejection status behavior.
- Serialization names:
  - Existing public response names stay unchanged.
- Frontend type impact:
  - No new public TypeScript contract is authorized unless the tests prove the current type omits an existing backend field.
- Generated contract impact:
  - `app.openapi()` remains loadable for the existing natal public endpoints.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-408-verifier-basic-complete-natal-v3-runtime-qa-live/evidence/basic-complete-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-408-verifier-basic-complete-natal-v3-runtime-qa-live/evidence/basic-complete-after.json`
- Expected invariant:
  - The only intended observable delta is Basic complete proof showing V3 basic assembly evidence instead of free/V1 evidence.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Gateway assembly resolution | `backend/app/domain/llm/runtime/gateway.py` | frontend |
| Gateway request adaptation | `backend/app/domain/llm/runtime/adapter.py` | API router |
| Natal persistence and rejection | `backend/app/services/llm_generation/natal/interpretation_service.py` | frontend |
| Public quota consumption | `backend/app/api/v1/routers/public/natal_interpretation.py` | gateway |
| Public narrative rendering | `frontend/src/features/natal-chart/NatalNarrativeReading.tsx` | backend fixtures |
| Page composition QA | `frontend/src/pages/NatalChartPage.tsx` | CSS-only changes |
| QA report | `_condamad/reports/**` or existing natal QA closure report path | source code comments |

## Mandatory Reuse / DRY Constraints

- Reuse existing fake gateway, `GatewayResult`, `NatalExecutionInput`, quota gate and narrative rejection test helpers.
- Reuse the existing public DOM guard tests; extend the same test family rather than creating duplicate scanners.
- Reuse existing Basic V3 fixture conventions and place the fixture beside the owning natal test fixtures.
- Keep the proof focused on Basic complete; do not duplicate CS-401 or CS-402 implementation logic.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy route or UI path may mask absence of `narrative_natal_reading_v1`.
- No compatibility route path may expose rejected Basic complete payloads.
- No fallback route path may translate Basic complete to `natal_interpretation_short`.
- No shim or alias may present V1/V2 short output as accepted Basic complete V3.
- Forbidden backend behavior: Basic complete resolves `natal/interpretation/free`.
- Forbidden backend behavior: Basic complete persists `schema_version="v2"` as a newly accepted reading.
- Forbidden frontend behavior: public `/natal` renders technical tokens instead of the narrative reading.

## Reintroduction Guard

- Guard source:
  - `rg -n "natal_interpretation_short|natal/interpretation/free|schema_version.*v2" backend/app backend/tests`
- Frontend guard:
  - `rg -n "visibility_expression|audit_input|interpretive_signal_ids|projection_version|ni-evidence-tags|ni-projections" frontend/src`
- Runtime guard:
  - `pytest -q backend/tests/integration/test_natal_basic_complete_v3_runtime.py`.
  - `pytest -q backend/tests/unit/test_natal_interpretation_service_v3_schema_guard.py`.
  - `pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`.
- Forbidden reintroduction:
  - Basic complete evidence relying on cached invalid readings.
  - QA report accepting a pass without runtime fixture or browser-visible proof.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-149 | scope -> natal prompt process -> modern natal remains assembly-governed. | runtime `pytest`; catalog scan. |
| RG-150 | scope -> rejected payload boundary -> rejected outputs stay outside public routes. | boundary `pytest`; public scan. |
| RG-152 | scope -> accepted complete reading -> `narrative_natal_reading_v1` persists. | runtime `pytest`. |
| RG-153 | scope -> `/natal` composition -> page remains centered on narrative reading. | frontend `pnpm` tests. |
| RG-154 | scope -> public DOM -> technical tokens stay out of public narrative DOM. | DOM guard `pnpm` tests. |
| RG-155 | scope -> semantic integrity -> empty sources and padding stay rejected. | schema guard `pytest`. |
| RG-156 | scope -> Basic editorial matter -> support elements remain diverse. | runtime `pytest`. |
| RG-157 | scope -> quota -> debit stays after accepted persistence. | quota `pytest`. |
| RG-158 | scope -> narrative accordions -> modern accordions remain expected rendering. | frontend `pnpm` tests. |

- Resolver note: generic resolver returned older backend and frontend universal IDs; route-only and style-only IDs were rejected from local scope.
- Non-applicable example: DB migration guardrails are out of scope because no schema migration is authorized.
- Non-applicable example: auth model guardrails are out of scope because the test user is used only for bounded QA.
- Non-applicable example: style guardrails are out of scope because no CSS or visual redesign is authorized.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline before | `_condamad/stories/CS-408-verifier-basic-complete-natal-v3-runtime-qa-live/evidence/basic-complete-before.json` | Record pre-proof Basic complete evidence. |
| Baseline after | `_condamad/stories/CS-408-verifier-basic-complete-natal-v3-runtime-qa-live/evidence/basic-complete-after.json` | Record final Basic complete V3 evidence. |
| Backend validation | `_condamad/stories/CS-408-verifier-basic-complete-natal-v3-runtime-qa-live/evidence/backend-validation.txt` | Keep backend lint, tests and scans. |
| Frontend validation | `_condamad/stories/CS-408-verifier-basic-complete-natal-v3-runtime-qa-live/evidence/frontend-validation.txt` | Keep frontend tests, lint and build output. |
| QA report | `_condamad/reports/cs-400-cloture-qa-live-lecture-natale.md` | Update the existing natal QA closure report. |
| QA notes | `_condamad/stories/CS-408-verifier-basic-complete-natal-v3-runtime-qa-live/evidence/qa-live-report.md` | Keep authenticated QA notes and screenshots index. |
| Review output | `_condamad/stories/CS-408-verifier-basic-complete-natal-v3-runtime-qa-live/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | No tolerance entry is authorized for Basic complete free/V1 masking. | permanent zero-entry register |

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration, historical data conversion or bulk remediation is in scope.

## Dependencies / Sequencing

- Depends on: CS-401, CS-402, CS-398 and CS-399.
- Sequencing rule: implementation must verify upstream contracts before treating this story as final QA closure.
- Blocker rule: if upstream evidence contradicts the expected Basic V3 path, stop and record the blocker in the QA report.

## Expected Files to Modify

Likely files:

- `_condamad/stories/CS-408-verifier-basic-complete-natal-v3-runtime-qa-live/evidence/**` - persisted proof artifacts.

Likely tests:

- `backend/tests/integration/test_natal_basic_complete_v3_runtime.py` - new fake-gateway runtime proof.
- `backend/tests/unit/test_natal_interpretation_service_v3_schema_guard.py` - V1/V2 rejection proof.
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py` - reject versus accept quota proof.
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` - public boundary proof.
- `frontend/src/tests/**` - public DOM and narrative rendering test updates.

Likely implementation-created paths:

- `backend/tests/integration/test_natal_basic_complete_v3_runtime.py`
- `backend/tests/unit/test_natal_interpretation_service_v3_schema_guard.py`
- `_condamad/stories/CS-408-verifier-basic-complete-natal-v3-runtime-qa-live/evidence/qa-live-report.md`
- `_condamad/reports/cs-400-cloture-qa-live-lecture-natale.md`

Files not expected to change:

- `frontend/src/**/*.css` - out of scope; no styling change is authorized.
- `backend/alembic/**` - out of scope; no migration is authorized.
- `backend/app/domain/astrology/**` - out of scope; no calculation change is authorized.
- `backend/app/services/entitlement/**` - out of scope unless quota tests prove a direct acceptance timing defect.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `python -B -m pytest -q tests/integration/test_natal_basic_complete_v3_runtime.py --tb=short`
- VC6: `rg -n "natal/interpretation/basic|published|is_published" app tests`
- VC7: `python -B -m pytest -q tests/unit/test_natal_interpretation_service_v3_schema_guard.py --tb=short`
- VC8: `python -B -m pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short`
- VC9: `python -B -m pytest -q tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short`
- VC10: `python -B -c "from app.main import app; assert app.routes; assert app.openapi()"`
- VC11: `rg -n "natal_interpretation_short|natal/interpretation/free|schema_version.*v2" app tests`
- VC12: `cd ..`
- VC13: `pnpm --dir frontend test -- NatalChartPage natalNarrativeReading natalPublicDomGuard`
- VC14: `pnpm --dir frontend lint`
- VC15: `pnpm --dir frontend build`
- VC16: `rg -n "visibility_expression|audit_input|interpretive_signal_ids|projection_version|ni-evidence-tags|ni-projections" frontend/src`
- VC17: `python -B -c "from pathlib import Path; assert Path('_condamad/reports/cs-400-cloture-qa-live-lecture-natale.md').exists()"`
- VC18: `python -B -c "from pathlib import Path; assert Path('_condamad/stories/CS-408-verifier-basic-complete-natal-v3-runtime-qa-live/evidence/qa-live-report.md').exists()"`

`rg` scan details:

- VC10 forbidden pattern: `natal_interpretation_short`, `natal/interpretation/free`, or accepted `schema_version` v2 in Basic complete proof.
- VC10 allowed fixture pattern: explicit rejected V1/V2 fixtures and free short tests.
- VC10 roots: `app` and `tests` after `cd backend`.
- VC10 expected false positives: rejected short fixture names and free short tests must be classified in `backend-validation.txt`.
- VC15 forbidden pattern: public technical leak tokens and legacy public evidence UI class names.
- VC15 allowed fixture pattern: denylist test assertions and non-public test fixture strings.
- VC15 roots: `frontend/src`.
- VC15 expected false positives: guard test fixtures only, recorded in `frontend-validation.txt`.

## Regression Risks

- QA can accidentally validate a cached invalid reading instead of a forced Basic complete generation.
- Fake gateway tests can prove only fixtures if they do not assert resolved assembly and metas.
- Frontend tests can mask backend failure if the DOM test uses mocked happy data only.
- Quota proof can miss the rejection path if the injected V1/V2 output is not wired through Basic complete.
- Live QA can become flaky if it uses a real provider instead of controlled local runtime.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep Python commands inside the activated `.venv`.
- Keep comments and docstrings in French for new or significantly modified application files.
- Do not update `_condamad/stories/regression-guardrails.md` during implementation of this story.
- Use the test user `daconrilcy@hotmail.com` only for bounded authenticated QA on local controlled runtime.
- Do not trigger uncontrolled real provider calls.

## References

- `_story_briefs/cs-403-verifier-basic-complete-natal-v3-en-runtime-et-qa-live.md`
- `_story_briefs/cs-401-router-basic-complete-vers-assembly-natale-v3.md`
- `_story_briefs/cs-402-refuser-downgrade-schema-v3-lecture-natale-complete.md`
- `_condamad/stories/regression-guardrails.md#RG-149`
- `_condamad/stories/regression-guardrails.md#RG-150`
- `_condamad/stories/regression-guardrails.md#RG-152`
- `_condamad/stories/regression-guardrails.md#RG-153`
- `_condamad/stories/regression-guardrails.md#RG-154`
- `_condamad/stories/regression-guardrails.md#RG-155`
- `_condamad/stories/regression-guardrails.md#RG-156`
- `_condamad/stories/regression-guardrails.md#RG-157`
- `_condamad/stories/regression-guardrails.md#RG-158`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/features/natal-chart/NatalNarrativeReading.tsx`
