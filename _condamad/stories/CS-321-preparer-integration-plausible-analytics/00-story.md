# Story CS-321 preparer-integration-plausible-analytics: Prepare Plausible Analytics Integration
Status: done

## Trigger / Source

Mode: Repo-informed story.

Source brief: `_story_briefs/cs-321-preparer-integration-plausible-analytics.md`.

CS-316 and CS-318 show that local analytics emission and redaction are repository-ready, while the configured local provider remains `noop`.
The current product decision is to prepare Plausible as the target provider without activating unproven production collection.

Source-alignment evidence: this story preserves the brief stakes by requiring Plausible configuration documentation, local `noop` default proof,
centralized provider calls through `useAnalytics`, redacted Plausible payload tests, and a persisted activation procedure for later CS-318 resumption.

## Objective

Prepare the frontend analytics layer for Plausible by documenting the required environment variables, keeping `noop` as the local default,
and proving that Plausible dispatch remains centralized and redacted before any real external activation.

## Target State

- Plausible is the documented target provider for frontend analytics configuration.
- `.env.example` or an owning operations document lists the exact Plausible variables required for activation.
- Local development keeps `noop` as the default when Plausible variables are not configured.
- `frontend/src/hooks/useAnalytics.ts` remains the only frontend source allowed to call `window.plausible`.
- Tests prove Plausible dispatch uses only sanitized props and never forwards sensitive analytics fields.
- A staging or production activation procedure explains the external validation path before real collection is accepted.
- CS-318 can later resume with a concrete Plausible environment and no Matomo setup drift.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-321-preparer-integration-plausible-analytics.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-321`.
- Evidence 3: `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/generated/10-final-evidence.md` - local `noop` closure reviewed.
- Evidence 4: `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/generated/10-final-evidence.md` - external provider blocker reviewed.
- Evidence 5: `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/evidence/external-access-blocker.md` - provider access gap reviewed.
- Evidence 6: `frontend/src/config/analytics.ts` - existing `plausible`, `matomo`, and `noop` provider config inspected.
- Evidence 7: `frontend/src/hooks/useAnalytics.ts` - central Plausible dispatch and redaction boundary inspected.
- Evidence 8: `frontend/src/tests/useAnalytics.test.tsx` - current Plausible redaction coverage inspected.
- Evidence 9: `.env.example` - analytics variables are not yet documented there.
- Evidence 10: `_condamad/stories/regression-guardrails.md` - registry consulted through resolver output and targeted ID lookup.

## Domain Boundary

- Domain: frontend-analytics-provider-config
- In scope:
  - Plausible provider configuration documentation for frontend runtime variables.
  - Local default behavior proving `noop` remains active without Plausible configuration.
  - Central `useAnalytics` Plausible dispatch and redaction tests.
  - Bounded operations documentation for staging or production activation validation.
  - Targeted scans preventing direct provider calls outside the analytics hook.
- Out of scope:
  - Backend API, database schema, auth, i18n, styling, build tooling, migrations, prompts, persistence, replay, dashboard, and alerting.
  - Matomo configuration, provider account creation, domain ownership setup, and external dashboard provisioning.
  - CS-311 event taxonomy changes and feature-level analytics event additions.
- Explicit non-goals:
  - No production analytics collection is activated by this story.
  - No Plausible script installation is accepted without documented environment and validation procedure.
  - No direct provider call may be added in components, pages, API clients, or business hooks.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a frontend analytics provider-configuration readiness contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Prepare only Plausible configuration, documentation, and tests.
  - Keep local default analytics provider as `noop` without configured Plausible variables.
  - Keep provider dispatch centralized in `frontend/src/hooks/useAnalytics.ts`.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: Plausible activation requires domain credentials, account access, or production collection approval.
- Additional validation rules:
  - Loaded config evidence must prove the local default remains `noop`.
  - Runtime provider tests must cover configured Plausible dispatch with sanitized props.
  - Static scans must prove no direct provider call exists outside `frontend/src/hooks/useAnalytics.ts`.
  - Activation documentation must state that external validation is required before production collection.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Loaded frontend config, Vitest, and hook dispatch prove Plausible readiness. |
| Baseline Snapshot | yes | CS-316 and CS-318 evidence define the current `noop` and external blocker baseline. |
| Ownership Routing | yes | Config, hook, tests, and documentation need canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this Plausible preparation. |
| Contract Shape | yes | The Plausible environment variables and activation procedure have exact keys and states. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Direct provider calls and Matomo setup must stay outside this story. |
| Persistent Evidence | yes | Final validation and activation-readiness evidence must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Plausible is the documented target provider. | Evidence profile: json_contract_shape; `rg` checks Plausible variable documentation. |
| AC2 | Local default remains `noop`. | Evidence profile: json_contract_shape; `vitest`; loaded config check in `frontend/src/tests/useAnalytics.test.tsx`. |
| AC3 | Plausible dispatch remains centralized. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans provider calls outside `useAnalytics.ts`. |
| AC4 | Plausible receives redacted props. | Evidence profile: json_contract_shape; `vitest run useAnalytics` proves sanitized payload dispatch. |
| AC5 | Activation procedure is documented. | Evidence profile: baseline_before_after_diff; `rg` checks staging and production validation text. |
| AC6 | CS-318 resumption path is explicit. | Evidence profile: external_usage_blocker; `python` checks final evidence or activation document text. |
| AC7 | Frontend validation stays green. | Evidence profile: frontend_typecheck_no_orphan; `pnpm lint` and targeted `vitest` output are persisted. |

## Implementation Tasks

- [x] Task 1: Read CS-316 and CS-318 final evidence plus the external access blocker before editing. (AC: AC1, AC5, AC6)
- [x] Task 2: Document Plausible variables in `.env.example` or the canonical operations document. (AC: AC1, AC5)
- [x] Task 3: Keep `ANALYTICS_CONFIG` defaulting to `noop` without Plausible variables. (AC: AC2)
- [x] Task 4: Add or adjust `useAnalytics` tests for configured Plausible dispatch and sanitized props. (AC: AC2, AC4)
- [x] Task 5: Guard against direct `plausible(` calls outside `frontend/src/hooks/useAnalytics.ts`. (AC: AC3)
- [x] Task 6: Document the staging and production validation procedure before real Plausible collection. (AC: AC5, AC6)
- [x] Task 7: Persist frontend validation output and final evidence in the CS-321 capsule. (AC: AC6, AC7)

## Files to Inspect First

- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/generated/10-final-evidence.md`
- `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/generated/10-final-evidence.md`
- `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/evidence/external-access-blocker.md`
- `frontend/src/config/analytics.ts`
- `frontend/src/hooks/useAnalytics.ts`
- `frontend/src/tests/useAnalytics.test.tsx`
- `.env.example`

## Runtime Source of Truth

- Primary source of truth:
  - Loaded frontend analytics configuration from `ANALYTICS_CONFIG`.
  - Runtime dispatch through `useAnalytics` under Vitest.
  - Plausible activation documentation committed in `.env.example` or the owning operations document.
  - Generated manifest `_condamad/stories/CS-321-preparer-integration-plausible-analytics/evidence/plausible-readiness.json`.
- Secondary evidence:
  - CS-316 local `noop` final evidence, CS-318 external blocker, targeted `rg` scans, targeted Vitest, and `pnpm lint`.
- Static scans alone are not sufficient for this story because:
  - The local default and redacted Plausible dispatch must be proven through loaded config and hook tests.

## Contract Shape

- Contract type:
  - Frontend analytics provider configuration and activation-readiness evidence.
- Fields:
  - `provider`: `plausible` as target provider; `noop` as unconfigured local default.
  - `enabled`: boolean value derived from the loaded frontend analytics config.
  - `domain`: Plausible site domain variable documented as `VITE_ANALYTICS_DOMAIN`.
  - `apiHost`: Plausible host variable documented as `VITE_ANALYTICS_API_HOST`.
  - `activation_state`: `local_noop`, `staging_ready`, or `production_validation_required`.
  - `redaction_status`: `pass` only when sensitive props are absent from provider dispatch.
  - `cs318_resume_condition`: concrete Plausible environment or external validation access required.
- Required fields:
  - `provider`, `enabled`, `activation_state`, `redaction_status`, and `cs318_resume_condition`.
- Optional fields:
  - `domain`, `apiHost`, `validated_at`, `operator`, and `external_reference`.
- Status codes:
  - No HTTP status-code contract is owned by this frontend analytics readiness story.
- Serialization names:
  - JSON keys are emitted exactly as listed in this section.
- Frontend type impact:
  - Any config or hook change must remain typed under the existing frontend TypeScript configuration.
- Generated contract impact:
  - `generated/10-final-evidence.md` must summarize Plausible readiness, local default, redaction proof, and activation blocker state.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/generated/10-final-evidence.md`
  - `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/generated/10-final-evidence.md`
  - `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/evidence/external-access-blocker.md`
  - `frontend/src/config/analytics.ts`
  - `frontend/src/hooks/useAnalytics.ts`
  - `.env.example`
- Comparison after implementation:
  - `_condamad/stories/CS-321-preparer-integration-plausible-analytics/evidence/plausible-readiness.json`
  - `_condamad/stories/CS-321-preparer-integration-plausible-analytics/evidence/validation-frontend.txt`
  - `_condamad/stories/CS-321-preparer-integration-plausible-analytics/generated/10-final-evidence.md`
- Expected invariant:
  - The intended delta is Plausible readiness documentation and tests while local analytics collection remains `noop` by default.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Analytics provider config | `frontend/src/config/analytics.ts` | Components, pages, and feature hooks |
| Analytics provider dispatch | `frontend/src/hooks/useAnalytics.ts` | `frontend/src/features/**`, `frontend/src/pages/**`, and `frontend/src/api/**` |
| Plausible variable documentation | `.env.example` or canonical operations docs | Inline component comments |
| Plausible redaction tests | `frontend/src/tests/useAnalytics.test.tsx` | Feature component tests duplicating provider logic |
| CS-321 evidence | `_condamad/stories/CS-321-preparer-integration-plausible-analytics/evidence/` | Provider dashboard-only notes |

## Mandatory Reuse / DRY Constraints

- Reuse `ANALYTICS_CONFIG` as the single provider selection and environment source.
- Reuse `sanitizeAnalyticsProps` as the only redaction boundary before provider dispatch.
- Reuse existing `useAnalytics` tests as the Plausible dispatch test surface.
- Reuse CS-316 and CS-318 evidence as the baseline; do not create a second provider-ingestion narrative.
- Keep Plausible variable names centralized in `.env.example` or one operations document.

## No Legacy / Forbidden Paths

- No legacy analytics provider path may be added for this preparation.
- No compatibility provider path may be added for this preparation.
- No fallback production sink, shim provider, mocked external sink, or feature-level direct provider call may be introduced.
- Do not add Matomo configuration, dashboard, alerting, backend, persistence, prompt, replay, style, or migration changes.
- Do not preserve legacy behavior through hidden mappers, aliases, broad allowlists, or duplicated event catalogs.

## Reintroduction Guard

- Guard target:
  - CS-321 must not activate real analytics collection without Plausible environment approval and validation documentation.
- Required guard:
  - `rg` verifies no direct `plausible(`, `window.plausible`, or `_paq` call appears outside `frontend/src/hooks/useAnalytics.ts`.
  - `vitest run useAnalytics` proves configured Plausible dispatch sends only sanitized props.
  - `rg` verifies Matomo variables or setup text were not introduced by this story.

## Regression Guardrails

| Guardrail | Local invariant | Evidence |
|---|---|---|
| RG-047 `inline-styles` | Analytics tests and docs must not add static inline TSX styles. | `pnpm lint`; targeted `rg`. |
| Registry gap `plausible-readiness` | No exact Plausible-readiness guardrail was resolved. | Resolver output and readiness manifest. |
| Registry gap `analytics-provider-boundary` | No exact provider-boundary guardrail was resolved. | Direct-call `rg` scan and `vitest`. |

Non-applicable examples: RG-027 prediction infra, RG-041 entitlement docs, and RG-042 LLM docs are not local to this frontend analytics scope.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Readiness manifest | `_condamad/stories/CS-321-preparer-integration-plausible-analytics/evidence/plausible-readiness.json` | Record target provider and local default. |
| Activation procedure | `_condamad/stories/CS-321-preparer-integration-plausible-analytics/evidence/plausible-activation-procedure.md` | Preserve validation handoff. |
| Direct-call scan | `_condamad/stories/CS-321-preparer-integration-plausible-analytics/evidence/provider-boundary-scan.txt` | Prove provider boundary. |
| Frontend validation | `_condamad/stories/CS-321-preparer-integration-plausible-analytics/evidence/validation-frontend.txt` | Preserve lint and Vitest output. |
| Final evidence | `_condamad/stories/CS-321-preparer-integration-plausible-analytics/generated/10-final-evidence.md` | Summarize final closure. |
| Review output | `_condamad/stories/CS-321-preparer-integration-plausible-analytics/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist required: no
- Reason: no allowlist handling is authorized for this Plausible preparation.
- Expiry / permanence: permanent not applicable because no allowlist entry exists.
- Required action: keep discovered provider, redaction, or activation defects either fixed narrowly or moved to a separate brief.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `.env.example` - document Plausible frontend environment variables and keep local defaults explicit.
- `frontend/src/config/analytics.ts` - adjust provider config only to keep local `noop` behavior deterministic.
- `frontend/src/hooks/useAnalytics.ts` - central provider boundary; change only for proven Plausible dispatch readiness.
- `frontend/src/tests/useAnalytics.test.tsx` - prove local default and configured Plausible redaction behavior.
- `_condamad/stories/CS-321-preparer-integration-plausible-analytics/evidence/plausible-readiness.json` - readiness manifest.
- `_condamad/stories/CS-321-preparer-integration-plausible-analytics/evidence/plausible-activation-procedure.md` - handoff procedure.
- `_condamad/stories/CS-321-preparer-integration-plausible-analytics/generated/10-final-evidence.md` - closure evidence.

Likely tests:

- `frontend/src/tests/useAnalytics.test.tsx` - central analytics provider and redaction behavior.

Files not expected to change:

- `backend/**` - out of scope; no backend surface is touched.
- `frontend/src/features/**` - out of scope unless a direct provider call already exists and must be removed.
- `frontend/src/pages/**` - out of scope; no page-level analytics provider calls are authorized.
- `frontend/src/api/**` - out of scope; API clients must not call analytics providers.
- `package.json` and lockfiles - out of scope; no dependency change is authorized.
- `_condamad/stories/regression-guardrails.md` - registry enrichment is not part of normal story implementation.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-321-preparer-integration-plausible-analytics\00-story.md`
- VC2: `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-321-preparer-integration-plausible-analytics\00-story.md`
- VC3: from `frontend`, `pnpm lint`
- VC4: from `frontend`, `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics`
- VC5: from `frontend`, `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics natalInterpretation natalChartApi`
- VC6: `rg -n "plausible\(|window\.plausible|_paq" frontend/src/features frontend/src/components frontend/src/pages frontend/src/api`
- VC7: `rg -n "VITE_ANALYTICS_PROVIDER|VITE_ANALYTICS_DOMAIN|VITE_ANALYTICS_API_HOST|VITE_ANALYTICS_ENABLED" .env.example frontend docs`
- VC8: `rg -n "matomo|MATOMO|_paq" .env.example frontend docs`
- VC9: `python` checks `evidence/plausible-readiness.json` and `generated/10-final-evidence.md` for CS-318 resume text.

## Regression Risks

- Plausible could be partially documented while local runtime accidentally stops defaulting to `noop`.
- A test-only provider helper could duplicate redaction logic outside `sanitizeAnalyticsProps`.
- Activation notes could be mistaken for production approval without external environment validation.
- Matomo vocabulary already exists in source types and must not expand into configuration or documentation for this story.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the Python virtual environment before any Python command in this repository.
- Do not enrich `_condamad/stories/regression-guardrails.md` during implementation.
- Keep Plausible activation blocked until staging or production observation is available and approved.
- Keep all markdown table rows below 180 characters.

## References

- `_story_briefs/cs-321-preparer-integration-plausible-analytics.md`
- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/generated/10-final-evidence.md`
- `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/generated/10-final-evidence.md`
- `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/evidence/external-access-blocker.md`
- `frontend/src/config/analytics.ts`
- `frontend/src/hooks/useAnalytics.ts`
- `frontend/src/tests/useAnalytics.test.tsx`
- `.env.example`
