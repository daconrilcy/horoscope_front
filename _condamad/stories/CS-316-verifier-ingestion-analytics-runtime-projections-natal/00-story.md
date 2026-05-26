# Story CS-316 verifier-ingestion-analytics-runtime-projections-natal: Verify Natal Projection Analytics Runtime Ingestion
Status: ready-to-dev

## Trigger / Source

Mode: Repo-informed story.

Source brief: `_story_briefs/cs-316-verifier-ingestion-analytics-runtime-projections-natal.md`.

CS-311 proves frontend emission and redaction for `/natal` projection analytics, but provider ingestion remains external evidence.
This story adds a bounded runtime smoke that uses the configured analytics sink only.

Source-alignment evidence: this story preserves the brief stakes by requiring provider discovery, seven CS-311 event names,
public-field payload matching, sensitive-field absence, and a documented external-validation state when no sink is available.

## Objective

Verify that the seven CS-311 `/natal` projection analytics events reach the configured analytics sink with redacted payloads,
without adding a provider, dashboard, alerting, backend change, persistence change, prompt change, or replay behavior.

## Target State

- The configured analytics sink is identified from existing frontend analytics configuration and runtime environment.
- A bounded smoke path can trigger `started`, `success`, `api_error`, `entitlement_denied`, `empty`, `degraded`, and `retry`.
- The ingestion evidence maps observed provider-side event names and public fields to `event-catalog.json`.
- Sensitive birth, coordinate, provider, raw runtime, replay, prompt, secret, and password fields are proven absent from ingested payloads.
- When no provider environment is available, the story closes with a persisted external-validation-required artifact.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-316-verifier-ingestion-analytics-runtime-projections-natal.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-316`.
- Evidence 3: `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/event-catalog.json` - event catalog read.
- Evidence 4: `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/redaction-proof.md` - redaction proof read.
- Evidence 5: `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/observability-limits.md` - limits read.
- Evidence 6: `frontend/src/hooks/useAnalytics.ts` - provider boundary and redaction hook inspected.
- Evidence 7: `frontend/src/features/natal-chart/NatalInterpretation.tsx` - `/natal` projection event emission inspected.
- Evidence 8: `frontend/src/config/analytics.ts` - current provider config source inspected.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - registry consulted through the resolver and targeted ID lookup.

## Domain Boundary

- Domain: frontend-analytics
- In scope:
  - Existing frontend analytics configuration discovery for Plausible, Matomo, or noop state.
  - Runtime smoke evidence for the seven CS-311 `/natal` projection events.
  - Provider-ingestion artifact capture or explicit external-validation-required artifact.
  - Redaction evidence against the CS-311 forbidden field list.
  - Existing CS-311 frontend tests and lint validation.
- Out of scope:
  - Backend API, database schema, auth model, i18n, styling refactor, build tooling, migrations, prompts, providers, and replay.
  - New analytics provider, dashboard, alerting, or permanent observability platform.
  - Real birth data, exact coordinates, secrets, provider raw dumps, and unredacted payload storage.
- Explicit non-goals:
  - No analytics provider implementation or provider replacement.
  - No modification of CS-311 event names, allowed public fields, or redaction boundaries without a separate story.
  - No broad browser QA pack outside the `/natal` analytics ingestion smoke.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a frontend analytics provider-ingestion smoke evidence contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only bounded smoke/evidence support for CS-311 analytics ingestion.
  - Keep application analytics emission semantics unchanged except for deterministic testability hooks required by this story.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: provider credentials, provider dashboard access, or staging analytics environment are unavailable.
- Additional validation rules:
  - Runtime proof must name the configured analytics provider and loaded frontend environment values.
  - Runtime proof must include the seven CS-311 event names from `event-catalog.json`.
  - Runtime proof must include a generated manifest: `evidence/analytics-ingestion-ledger.json`.
  - Provider-unavailable closure must include `evidence/external-validation-required.md` and keep CS-311 tests passing.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Configured provider state, browser/runtime event emission, and provider evidence prove ingestion. |
| Baseline Snapshot | yes | CS-311 catalog and redaction proof are the baseline for observed ingestion. |
| Ownership Routing | yes | Smoke code and evidence artifacts need canonical destinations. |
| Allowlist Exception | no | No allowlist handling is authorized for this single analytics verification. |
| Contract Shape | yes | The ingestion ledger has exact event, provider, field, redaction, and result keys. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | No new provider or direct feature-level provider calls may be introduced. |
| Persistent Evidence | yes | Provider proof or external-validation-required artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The configured analytics sink is recorded. | Evidence profile: json_contract_shape; `python` validates `evidence/analytics-runtime-config.json`. |
| AC2 | The seven CS-311 event names are covered. | Evidence profile: json_contract_shape; `python` validates `evidence/analytics-ingestion-ledger.json`. |
| AC3 | Runtime ingestion proof is captured. | Evidence profile: runtime_openapi_contract; `vitest`; loaded config; `frontend/src/tests/useAnalytics.test.tsx`. |
| AC4 | Public fields match the CS-311 catalog. | Evidence profile: json_contract_shape; `python` compares ledger fields to `event-catalog.json`. |
| AC5 | Sensitive fields are absent. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans the CS-316 evidence capsule. |
| AC6 | Provider-unavailable state is explicit. | Evidence profile: external_usage_blocker; `python` checks `evidence/external-validation-required.md`. |
| AC7 | CS-311 analytics tests remain green. | Evidence profile: frontend_typecheck_no_orphan; `pnpm lint` and targeted `vitest` output are persisted. |
| AC8 | Full frontend Vitest remains green. | Evidence profile: frontend_typecheck_no_orphan; `node .\scripts\run-vite-logged.mjs vitest vitest run`. |
| AC9 | Final evidence summarizes closure. | Evidence profile: baseline_before_after_diff; `python` checks `generated/10-final-evidence.md`. |

## Implementation Tasks

- [ ] Task 1: Read CS-311 catalog, redaction proof, and observability limits before touching code. (AC: AC1, AC2, AC4, AC5)
- [ ] Task 2: Identify the active sink from `ANALYTICS_CONFIG` and frontend runtime environment. (AC: AC1)
- [ ] Task 3: Add a bounded smoke harness or test helper that triggers the seven CS-311 event states. (AC: AC2, AC3)
- [ ] Task 4: Capture provider-side observations in `evidence/analytics-ingestion-ledger.json`. (AC: AC2, AC3, AC4)
- [ ] Task 5: Write `evidence/external-validation-required.md` when no provider sink is reachable. (AC: AC6)
- [ ] Task 6: Prove observed fields match `event-catalog.json` and forbidden fields are absent. (AC: AC4, AC5)
- [ ] Task 7: Persist targeted and full frontend validation output in the CS-316 evidence capsule. (AC: AC7, AC8)
- [ ] Task 8: Write `generated/10-final-evidence.md` with source alignment and final ingestion status. (AC: AC9)

## Files to Inspect First

- `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/event-catalog.json`
- `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/redaction-proof.md`
- `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/observability-limits.md`
- `frontend/src/config/analytics.ts`
- `frontend/src/hooks/useAnalytics.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/tests/useAnalytics.test.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/natalChartApi.test.tsx`

## Runtime Source of Truth

- Primary source of truth:
  - Loaded frontend analytics configuration from `ANALYTICS_CONFIG`.
  - Runtime/browser emission through `useAnalytics`.
  - Provider-side observation or explicit external-validation-required artifact.
  - Generated manifest `evidence/analytics-ingestion-ledger.json`.
- Secondary evidence:
  - CS-311 `event-catalog.json`, `redaction-proof.md`, targeted Vitest, full Vitest, and `pnpm lint`.
- Static scans alone are not sufficient for this story because:
  - The source gap is provider ingestion, not only frontend emission or redaction.

## Contract Shape

- Contract type:
  - Analytics ingestion evidence ledger and runtime config artifact.
- Fields:
  - `provider`: `plausible`, `matomo`, or `noop`.
  - `environment`: local or staging environment label used for the smoke.
  - `event_name`: one event name from CS-311 `event-catalog.json`.
  - `state`: one CS-311 projection analytics state.
  - `observed`: boolean provider-ingestion result.
  - `observed_fields`: public field names observed after redaction.
  - `forbidden_fields_present`: forbidden field names observed in provider evidence.
  - `result`: `pass`, `external_validation_required`, or `blocked`.
- Required fields:
  - `provider`, `environment`, `event_name`, `state`, `observed`, `observed_fields`, `forbidden_fields_present`, and `result`.
- Optional fields:
  - `provider_reference`, `captured_at`, `notes`, and `validation_reference`.
- Status codes:
  - No HTTP status-code contract is owned by the analytics ingestion ledger.
- Serialization names:
  - JSON keys are emitted exactly as listed in this section.
- Frontend type impact:
  - Any new helper or test file must remain typed under the existing frontend TypeScript configuration.
- Generated contract impact:
  - `generated/10-final-evidence.md` must summarize provider state, event coverage, redaction result, and closure status.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/event-catalog.json`
  - `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/redaction-proof.md`
  - `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/observability-limits.md`
- Comparison after implementation:
  - `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/analytics-runtime-config.json`
  - `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/analytics-ingestion-ledger.json`
  - `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/external-validation-required.md`
- Expected invariant:
  - The intended delta is provider-ingestion proof or explicit external-validation-required evidence for the CS-311 event catalog.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Analytics provider config | `frontend/src/config/analytics.ts` | Feature components |
| Analytics emission boundary | `frontend/src/hooks/useAnalytics.ts` | Direct provider calls in `frontend/src/features/**` |
| Natal projection instrumentation | `frontend/src/features/natal-chart/NatalInterpretation.tsx` | Backend or API client modules |
| Ingestion evidence | `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/` | Provider dashboard-only notes |
| Final evidence | `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/generated/10-final-evidence.md` | Repository root |

## Mandatory Reuse / DRY Constraints

- Reuse the CS-311 event catalog instead of redefining event names or allowed fields.
- Reuse `sanitizeAnalyticsProps` for redaction; do not duplicate the sensitive-field filter in feature code.
- Reuse `ANALYTICS_CONFIG` as the single provider selection source.
- Keep one canonical ingestion ledger; do not create parallel markdown and JSON ledgers for the same observed events.
- Keep smoke support focused on CS-311 projection analytics; do not duplicate natal projection API behavior.

## No Legacy / Forbidden Paths

- No legacy analytics event name may be added for this smoke.
- No compatibility analytics provider path may be added for this smoke.
- No fallback provider, shim provider, mocked production sink, or feature-level direct provider call may be introduced.
- Do not add dashboard, alerting, backend, persistence, prompt, provider, replay, or migration changes.
- Do not preserve legacy behavior through hidden mappers, aliases, broad allowlists, or duplicated event catalogs.

## Reintroduction Guard

- Guard target:
  - CS-316 must not satisfy ingestion verification using only CS-311 component tests.
- Required guard:
  - `python` validates `analytics-ingestion-ledger.json` contains all seven CS-311 event names or provider-unavailable closure.
  - `rg` verifies no direct `plausible(`, `_paq.push`, or new analytics provider call appears in `frontend/src/features`.

## Regression Guardrails

| Guardrail | Local invariant | Evidence |
|---|---|---|
| RG-047 `inline-styles` | A smoke UI helper must not add static inline TSX styles. | `rg` scan from `frontend`; `pnpm lint`. |
| RG-071 `NatalInterpretation` | Natal instrumentation must not grow into unrelated API or presentation ownership. | Targeted `vitest`; diff review. |
| Registry gap `analytics-ingestion` | No exact provider-ingestion guardrail was resolved. | Resolver output and CS-316 ledger validation. |

Non-applicable examples: RG-027 backend prediction infra, RG-041 entitlement documentation, and RG-042 LLM docs are not local to this
frontend analytics ingestion story.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Runtime config | `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/analytics-runtime-config.json` | Record provider state. |
| Ingestion ledger | `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/analytics-ingestion-ledger.json` | Map events to observations. |
| External validation note | `evidence/external-validation-required.md` | Document unavailable provider. |
| Redaction scan | `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/redaction-scan.txt` | Preserve sensitive-field scan. |
| Frontend validation | `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/validation-frontend.txt` | Preserve frontend command output. |
| Final evidence | `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/generated/10-final-evidence.md` | Summarize closure. |
| Review output | `generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist exception: not required
- Reason: no allowlist handling is authorized for this analytics ingestion verification.
- Permanence decision: permanently not authorized for this story.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | No allowlist entry is authorized for this story. | Permanently not authorized. |

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `frontend/src/hooks/useAnalytics.ts` - inspect or add deterministic smoke support at the central analytics boundary.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - inspect or add bounded state trigger support for smoke coverage.
- `frontend/src/tests/useAnalytics.test.tsx` - extend provider redaction coverage.
- `frontend/src/tests/natalInterpretation.test.tsx` - extend seven-state smoke coverage.
- `frontend/src/tests/natalChartApi.test.tsx` - keep projection API client coverage green.
- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/analytics-runtime-config.json` - add provider state.
- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/analytics-ingestion-ledger.json` - add observations.
- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/generated/10-final-evidence.md` - add final evidence.

Likely tests:

- `frontend/src/tests/useAnalytics.test.tsx` - central redaction and provider dispatch coverage.
- `frontend/src/tests/natalInterpretation.test.tsx` - `/natal` projection analytics states.
- `frontend/src/tests/natalChartApi.test.tsx` - projection API client regression coverage.

Files not expected to change:

- `backend/app/**` - out of scope; backend runtime and API contract stay unchanged.
- `backend/alembic/**` - out of scope; no migration is touched.
- `frontend/src/styles/**` - out of scope; no styling work is touched.
- `_condamad/stories/regression-guardrails.md` - registry enrichment is not part of normal story implementation.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `python -c "import json; d=json.load(open('evidence/analytics-runtime-config.json')); assert d['provider'] in {'plausible','matomo','noop'}"`
  - Run from `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal`.
- VC2: `python` validates all seven CS-311 event names in `evidence/analytics-ingestion-ledger.json`.
  - Run from `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal`.
- VC3: `python` compares ledger `observed_fields` and `forbidden_fields_present` against CS-311 `event-catalog.json`.
  - Run from repository root after activating `.venv` for Python.
- VC4: run this sensitive-field scan against the CS-316 evidence directory:
  - `rg -n "birth_date|birth_time|birth_place|latitude|longitude|provider_response|raw_runtime|replay_snapshot|prompt|api_key|password" evidence`
- VC5: from `frontend`, `pnpm lint`
- VC6: from `frontend`, `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics natalInterpretation natalChartApi`
- VC7: from `frontend`, `node .\scripts\run-vite-logged.mjs vitest vitest run`
- VC8: `rg -n "plausible\\(|_paq\\.push|VITE_ANALYTICS_PROVIDER" frontend/src/features frontend/src/components frontend/src/api`
- VC9: `python -c "from pathlib import Path; assert Path('generated/10-final-evidence.md').exists()"`
  - Run from `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal`.

## Regression Risks

- Provider access may be unavailable during implementation, leaving closure as external validation required rather than provider-proven.
- Provider dashboards may aggregate or delay events, so the ledger must record timestamps and provider references precisely.
- A smoke helper could accidentally duplicate redaction logic outside `useAnalytics`.
- Sensitive fields could be copied into evidence artifacts during provider observation capture.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Use `daconrilcy@hotmail.com` only for authenticated local or staging `/natal` access.
- Activate `.venv` before every Python command, including ledger validation scripts.
- Do not enrich `_condamad/stories/regression-guardrails.md` during implementation.
- Keep raw provider payloads out of committed evidence; persist only redacted field names and bounded provider references.

## References

- `_story_briefs/cs-316-verifier-ingestion-analytics-runtime-projections-natal.md`
- `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/event-catalog.json`
- `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/redaction-proof.md`
- `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/observability-limits.md`
- `frontend/src/config/analytics.ts`
- `frontend/src/hooks/useAnalytics.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
