# Story CS-311 suivi-analytics-erreurs-etats-degrades-projections-natal: Track Natal Projection Analytics Errors And Degraded States
Status: ready-to-dev

## Trigger / Source

- Source type: product observability brief with repository-informed boundary.
- Source reference: `_story_briefs/cs-311-suivi-analytics-erreurs-etats-degrades-projections-natal.md`.
- Selected mode: Repo-informed story with Fast Story Writer Mode.
- Problem statement: `/natal` projection failures, missing birth-data empty states, and degraded-without-time states need minimal analytics without leaks.
- Source stakes: improve production observability, preserve privacy, keep backend access decisions authoritative, and cover retry and empty-state behavior.
- Source-alignment evidence: PASS; objective, ACs, tasks, evidence, validation, and guardrails preserve every included scope item from the brief.

## Objective

Instrument the frontend `/natal` projection flow with minimal analytics events for request, success, API error, entitlement denial,
missing birth-data empty state, degraded-without-time state, and retry while keeping event payloads public and redacted.

## Target State

- Existing analytics ownership is inventoried before any new event helper or event name is added.
- `/natal` projection analytics reuse `frontend/src/hooks/useAnalytics.ts` or a single frontend analytics owner derived from it.
- The tracked event catalog covers projection request started, success, API error, entitlement denied, missing birth-data empty state,
  degraded-without-time state, and retry.
- Analytics payloads contain only non-sensitive fields such as public projection type, UI state, public error code, and public plan code already exposed.
- Analytics payloads never include prompts, provider payloads, replay snapshots, raw runtime data, raw birth data, exact coordinates, secrets, or raw AI output.
- Frontend tests prove the event sequence and redaction for success, API error, entitlement denied, empty state, degraded state, and retry.
- Observability limits are documented in the story evidence or an existing docs owner without creating an admin dashboard.
- Backend routes, entitlement decisions, projection builders, persistence, prompts, providers, auth, DB schema, and migrations remain unchanged.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-311-suivi-analytics-erreurs-etats-degrades-projections-natal.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-311` after `CS-310`.
- Evidence 3: `frontend/src/hooks/useAnalytics.ts` - existing analytics hook owner inspected.
- Evidence 4: `frontend/src/api/astrologyProjections.ts` - projection API hook and retry behavior inspected.
- Evidence 5: `frontend/src/features/natal-chart/NatalInterpretation.tsx` - projection orchestration owner inspected.
- Evidence 6: `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - projection state rendering owner inspected.
- Evidence 7: `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md` - prior projection wiring proof read.
- Evidence 8: `docs/architecture/astrology-disclaimer-projection-policy.md` - application-owned disclaimer policy read.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - scoped resolver output and targeted ID lookup consulted.
- Source-alignment evidence: PASS; every brief prerequisite, included scope item, expected validation command, and risk maps to an AC or task.

## Domain Boundary

- Domain: frontend-analytics
- In scope:
  - `/natal` projection analytics and error tracking for B2C projection UI states.
  - Event catalog and redaction policy for projection started, success, API error, entitlement denied, missing birth-data empty,
    degraded without birth time, and retry.
  - Reuse of the existing frontend analytics owner and targeted frontend tests.
  - Documentation of tracked errors and observability limits.
  - Evidence artifacts under the CS-311 capsule.
- Out of scope:
  - Backend routes, backend entitlement decisions, DB schema, auth, i18n expansion, styling redesign, build tooling, migrations, and admin dashboards.
  - New external analytics provider, alerting system, generated client, provider payload capture, replay storage, and app-wide instrumentation.
- Explicit non-goals:
  - No new analytics vendor or dependency.
  - No tracking of full projection payloads, prompts, raw AI answers, birth input, exact coordinates, secrets, or provider responses.
  - No silent frontend override of backend entitlement decisions.
  - No instrumentation outside `/natal` projections.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a frontend analytics instrumentation and redaction contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Change only frontend analytics ownership, `/natal` projection instrumentation, tests, documentation, and CS-311 evidence.
  - Keep `frontend/src/hooks/useAnalytics.ts` or its existing analytics ownership as the canonical tracking path.
  - Keep `frontend/src/api/astrologyProjections.ts` as the projection HTTP hook owner.
  - Keep `frontend/src/features/natal-chart/NatalInterpretation.tsx` as the projection orchestration owner.
  - Keep `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` as the projection display owner.
  - Preserve backend projection route shape, entitlement policy, builders, persistence, prompts, providers, auth, DB schema, and migrations unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: analytics product naming, provider changes, or privacy policy scope exceeds this minimal `/natal` projection tracking.
- Additional validation rules:
  - The event catalog must list exactly the minimum event family required by the brief.
  - Each event payload must document allowed fields and forbidden sensitive fields.
  - Frontend tests must assert that sensitive keys are absent from tracked payloads.
  - Retry tracking must be caused by the user retry action, not by React Query internal retry attempts.
  - Entitlement denied tracking must preserve backend as the source of access decisions.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Vitest and Testing Library prove tracked event behavior from rendered `/natal` projection states. |
| Baseline Snapshot | yes | Existing analytics owner, CS-303 evidence, and CS-311 event catalog prove the only allowed surface delta. |
| Ownership Routing | yes | Analytics, API hook, orchestration, display, tests, and docs owners must remain clear. |
| Allowlist Exception | no | No allowlist handling or broad waiver is authorized for analytics redaction. |
| Contract Shape | yes | Event names, allowed payload fields, forbidden fields, and documentation artifact fields are exact. |
| Batch Migration | no | No batch migration or app-wide instrumentation is in scope. |
| Reintroduction Guard | yes | Sensitive payload keys, direct vendor bypass, backend access override, and unrelated surfaces must stay absent. |
| Persistent Evidence | yes | Event catalog, redaction proof, validation log, and review handoff must be kept. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The event catalog lists seven projection events. | Evidence profile: json_contract_shape; `python` checks CS-311 event catalog artifact. |
| AC2 | Analytics uses the existing frontend owner. | Evidence profile: ast_architecture_guard; `rg` checks `useAnalytics` ownership in `frontend/src`. |
| AC3 | Success state emits a projection success event. | Evidence profile: json_contract_shape; `vitest` runs `frontend/src/tests/natalInterpretation.test.tsx`. |
| AC4 | API error state emits a public error event. | Evidence profile: json_contract_shape; `vitest` runs `frontend/src/tests/natalInterpretation.test.tsx`. |
| AC5 | Entitlement denial emits a public denied event. | Evidence profile: json_contract_shape; `vitest` runs `frontend/src/tests/natalInterpretation.test.tsx`. |
| AC6 | Missing birth-data or empty-display state emits a redacted empty event. | Evidence profile: json_contract_shape; `vitest` state assertions. |
| AC7 | Degraded-without-time state emits a redacted degraded event. | Evidence profile: json_contract_shape; `vitest` state assertions. |
| AC8 | User retry emits a retry event. | Evidence profile: json_contract_shape; `vitest` runs `frontend/src/tests/natalInterpretation.test.tsx`. |
| AC9 | Tracked payloads exclude sensitive keys. | Evidence profile: targeted_forbidden_symbol_scan; `vitest` redaction assertions and `rg` sensitive-key scan pass. |
| AC10 | Observability limits are documented. | Evidence profile: baseline_before_after_diff; `python` checks CS-311 observability artifact. |
| AC11 | Frontend validation passes. | Evidence profile: frontend_typecheck_no_orphan; `pnpm lint` and `vitest` commands from `frontend`. |
| AC12 | Story evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-311 evidence and validation artifacts. |

## Implementation Tasks

- [ ] Task 1: Inspect the brief, analytics hook, projection API hook, natal orchestration, display component, CS-303 evidence, and disclaimer policy. (AC: AC1, AC2)
- [ ] Task 2: Create the CS-311 event catalog with event names, trigger states, allowed fields, and forbidden fields. (AC: AC1, AC9, AC10)
- [ ] Task 3: Reuse the existing analytics owner for `/natal` projection events without adding a provider or dependency. (AC: AC2)
- [ ] Task 4: Instrument projection request started and success from the orchestration owner. (AC: AC3)
- [ ] Task 5: Instrument API error and entitlement denial with public error codes only. (AC: AC4, AC5, AC9)
- [ ] Task 6: Instrument missing birth-data empty state and degraded-without-time state without reading raw payload internals. (AC: AC6, AC7, AC9)
- [ ] Task 7: Instrument user retry from the displayed retry action. (AC: AC8)
- [ ] Task 8: Add or update frontend tests for event emission, retry behavior, and sensitive-key redaction. (AC: AC3, AC4, AC5, AC6, AC7, AC8, AC9)
- [ ] Task 9: Document tracked errors, observability limits, and validation output under the CS-311 capsule or existing docs owner. (AC: AC10, AC12)
- [ ] Task 10: Run frontend validations and persist final evidence. (AC: AC11, AC12)

## Files to Inspect First

- `_story_briefs/cs-311-suivi-analytics-erreurs-etats-degrades-projections-natal.md` - source brief.
- `frontend/src/hooks/useAnalytics.ts` - existing analytics owner.
- `frontend/src/api/astrologyProjections.ts` - projection API hook and retry behavior.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - projection orchestration owner.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - projection state rendering owner.
- `frontend/src/tests/useAnalytics.test.tsx` - analytics hook tests.
- `frontend/src/tests/natalInterpretation.test.tsx` - projection state component tests.
- `frontend/src/tests/natalChartApi.test.tsx` - API wrapper tests.
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md` - prior projection wiring evidence.
- `docs/architecture/astrology-disclaimer-projection-policy.md` - policy boundary for application-owned messages.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics natalInterpretation natalChartApi` from `frontend`.
  - `node .\scripts\run-vite-logged.mjs vitest vitest run` from `frontend`.
  - `pnpm lint` from `frontend`.
  - Testing Library assertions over `/natal` projection states and `useAnalytics` spy output.
  - `AST guard` over frontend imports and direct analytics vendor calls.
- Secondary evidence:
  - Event catalog, redaction proof, observability limits, sensitive-key scan, and validation log under the CS-311 capsule.
  - Targeted `rg` scans for sensitive keys and direct analytics vendor bypass outside the owner.
- Static scans alone are not sufficient because:
  - The story must prove event emission from rendered projection states and user retry behavior.

## Contract Shape

- Contract type:
  - Frontend analytics event catalog and redacted event payload contract.
- Fields:
  - `event_name`: stable event identifier for the projection analytics event.
  - `route`: `/natal`.
  - `projection_type`: public projection type when available.
  - `state`: started, success, api_error, entitlement_denied, empty, degraded, or retry.
  - `state_reason`: public reason such as missing_birth_data or missing_birth_time when the UI already exposes the degraded or empty state.
  - `public_error_code`: public error code for failed states.
  - `plan_code`: public plan code already exposed by the projection response.
  - `source`: public source label such as chart_id or birth_input when already exposed.
  - `sensitive_fields_checked`: list of forbidden field names covered by tests or scan.
  - `evidence_path`: persisted artifact path.
- Required fields:
  - `event_name`
  - `route`
  - `state`
  - `sensitive_fields_checked`
  - `evidence_path`
- Optional fields:
  - `projection_type`
  - `public_error_code`
  - `plan_code`
  - `source`
  - `state_reason`
- Status codes:
  - Frontend analytics maps HTTP `403` to entitlement_denied and other API failures to api_error without changing backend responses.
- Serialization names:
  - Event payload keys are emitted exactly as listed in the event catalog.
- Frontend type impact:
  - Analytics event types and local helper types may expand only for `/natal` projection events.
- Backend type impact:
  - none; backend request and response contracts remain unchanged.
- Generated contract impact:
  - no generated client, OpenAPI output, manifest, or schema generation is authorized.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/baseline-summary.md`
- Comparison after implementation:
  - `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/event-catalog.json`
  - `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/redaction-proof.md`
  - `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/observability-limits.md`
  - `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/validation.txt`
- Expected invariant:
  - The only intended behavior delta is minimal redacted frontend analytics for `/natal` projections.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Analytics tracking hook | `frontend/src/hooks/useAnalytics.ts` | Component-local vendor call |
| Projection HTTP state | `frontend/src/api/astrologyProjections.ts` | Analytics hook |
| Projection orchestration | `frontend/src/features/natal-chart/NatalInterpretation.tsx` | API client direct UI renderer |
| Projection state display | `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` | Analytics provider adapter |
| Analytics hook tests | `frontend/src/tests/useAnalytics.test.tsx` | Manual-only proof |
| Projection analytics tests | `frontend/src/tests/natalInterpretation.test.tsx` | Backend-only proof |
| API wrapper tests | `frontend/src/tests/natalChartApi.test.tsx` | UI component fixtures |
| Observability documentation | CS-311 `evidence/` or existing docs owner | Source comments only |

## Mandatory Reuse / DRY Constraints

- Reuse the existing analytics hook or its single derived owner for all event emission.
- Reuse existing projection query state, `ApiError`, public projection types, and existing component tests.
- Reuse existing Testing Library and Vitest setup; do not add a new frontend test framework.
- Reuse existing `/natal` UI state owners and CSS classes; no styling work is expected.
- Do not add external packages, generated clients, duplicate projection parsers, duplicate analytics adapters, or app-wide tracking layers.
- Do not duplicate sensitive-key lists across runtime and tests; keep a single local list or shared helper inside the analytics/test boundary.

## No Legacy / Forbidden Paths

- No legacy analytics path may be added for `/natal` projections.
- No compatibility analytics adapter may be added for this story.
- No fallback tracking path may bypass the existing analytics owner.
- Do not create aliases, shims, wrappers, duplicate analytics clients, or duplicate projection clients.
- Do not add direct Plausible, Matomo, fetch, or console event calls from projection UI components.
- Do not add inline `style` attributes in TSX files.
- Do not change backend projection builders, prompts, providers, DB schema, migrations, auth, pricing, Stripe, or public API route shape.

## Reintroduction Guard

- Guard path 1: analytics payloads only contain public projection state fields listed in the event catalog.
- Guard path 2: sensitive keys remain absent from tracked payloads and public `/natal` output.
- Guard path 3: backend `403` entitlement remains a displayed denial state and is not converted into a frontend access grant.
- Guard path 4: retry analytics is emitted from the user retry action only.
- Guard path 5: analytics provider calls remain routed through the canonical frontend owner.
- Required deterministic guards:
  - `rg -n "birth_date|birth_time|birth_place|latitude|longitude|provider_response|raw_runtime|replay_snapshot|prompt|api_key|password" src`.
  - `rg -n "plausible\\(|_paq\\.push|console\\.debug\\(\\`\\[Analytics" frontend/src/features frontend/src/components frontend/src/api`.
  - `rg -n "fetch\\(.*/v1/astrology/projections|axios\\(.*/v1/astrology/projections" frontend/src`.
  - `rg -n "style=" frontend/src/features/natal-chart frontend/src/components/natal-interpretation -g "*.tsx"`.
  - `git diff --name-only -- frontend docs _condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal`.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-047 `CS-029-encadrer-styles-inline-statiques-frontend` | Touched TSX files keep static styles out of inline attributes. | `rg` inline-style scan; `pnpm lint`. |
| Story-local analytics owner guard | `/natal` projection events must use the existing analytics owner. | `rg` owner scan; `vitest`. |
| Story-local sensitive analytics guard | Event payloads must exclude birth, prompt, provider, replay, secret, and raw AI fields. | Redaction tests; `rg` scan. |
| Story-local entitlement guard | Frontend analytics must not alter backend access decisions. | `vitest`; API state assertions. |

Non-applicable examples that prevent scope drift:

- Resolver returned backend docs and prediction guardrails that are non-local to this frontend analytics story; store that note in evidence only.
- RG-007 is not selected because admin LLM observability endpoints are not edited.
- RG-041 is not selected because entitlement documentation is not edited.
- RG-052 is not selected because CSS namespace migration is not edited.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline summary | `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/baseline-summary.md` | Record source context. |
| Event catalog | `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/event-catalog.json` | Define event names and payload fields. |
| Redaction proof | `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/redaction-proof.md` | Prove sensitive fields are excluded. |
| Observability limits | `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/observability-limits.md` | Document limits. |
| Sensitive-key scan | `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/sensitive-key-scan.txt` | Record forbidden key scan output. |
| Validation log | `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/validation.txt` | Keep final validation commands. |
| Final evidence | `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/generated/10-final-evidence.md` | Summarize implementation evidence. |
| Review output | `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/generated/11-code-review.md` | Keep generated review. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling, test suppression, or broad waiver is authorized.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `frontend/src/hooks/useAnalytics.ts` - extend analytics event typing or redaction helper through the existing owner.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - emit projection started, success, error, denied, empty, degraded, and retry events.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - route the user retry action through tracked orchestration.
- `frontend/src/tests/useAnalytics.test.tsx` - cover analytics owner behavior and event typing.
- `frontend/src/tests/natalInterpretation.test.tsx` - cover projection analytics events and redaction.
- `frontend/src/tests/natalChartApi.test.tsx` - cover public error code behavior only when API wrapper behavior changes.
- `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/event-catalog.json` - define event catalog.
- `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/redaction-proof.md` - record sensitive-field proof.
- `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/observability-limits.md` - document limits.
- `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/validation.txt` - persist validation output.

Likely tests:

- `frontend/src/tests/useAnalytics.test.tsx` - analytics hook tests.
- `frontend/src/tests/natalInterpretation.test.tsx` - projection UI state and analytics tests.
- `frontend/src/tests/natalChartApi.test.tsx` - projection API wrapper tests.

Files not expected to change:

- `backend/app/**` - out of scope; backend projection runtime and public contracts remain unchanged.
- `backend/alembic/**` - out of scope; no migration is touched.
- `frontend/package.json` - out of scope; no package or script change is authorized.
- `_condamad/stories/regression-guardrails.md` - out of scope; normal story generation must not enrich the registry.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: create event catalog, redaction proof, observability limits, sensitive-key scan, final evidence, and validation log under the CS-311 capsule.
- VC2: from `frontend`, run `pnpm lint`.
- VC3: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics natalInterpretation natalChartApi`.
- VC4: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run`.
- VC5: from `frontend`, run `rg -n "birth_date|birth_time|birth_place|latitude|longitude|provider_response|raw_runtime|replay_snapshot|prompt|api_key|password" src`.
- VC6: from repo root, run `rg -n "plausible\\(|_paq\\.push|console\\.debug\\(\\`\\[Analytics" frontend/src/features frontend/src/components frontend/src/api`.
- VC7: from repo root, run `rg -n "fetch\\(.*/v1/astrology/projections|axios\\(.*/v1/astrology/projections" frontend/src`.
- VC8: from repo root, run `rg -n "style=" frontend/src/features/natal-chart frontend/src/components/natal-interpretation -g "*.tsx"`.
- VC9: with venv active, run `python -B` to assert CS-311 event catalog, redaction proof, observability limits, and validation artifacts exist.

## Regression Risks

- Analytics could capture sensitive projection context while trying to explain errors.
- Retry tracking could count internal query retries instead of the user retry action.
- Entitlement denial could be blurred with generic API failure and weaken product visibility.
- Event emission could be duplicated across the API hook, orchestration component, and display component.
- A narrow analytics change could bypass the existing hook or introduce direct vendor calls in UI components.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Start by writing the event catalog before changing instrumentation.
- Keep backend entitlement decisions as the source of access truth.
- Keep every style change in CSS and reuse existing variables; no style change is expected.
- Persist redaction proof before final validation.

## References

- `_story_briefs/cs-311-suivi-analytics-erreurs-etats-degrades-projections-natal.md`
- `frontend/src/hooks/useAnalytics.ts`
- `frontend/src/api/astrologyProjections.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/tests/useAnalytics.test.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/natalChartApi.test.tsx`
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md`
- `docs/architecture/astrology-disclaimer-projection-policy.md`
- `_condamad/stories/regression-guardrails.md`
