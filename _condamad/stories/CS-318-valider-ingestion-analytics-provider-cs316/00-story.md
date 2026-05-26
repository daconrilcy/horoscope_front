# Story CS-318 valider-ingestion-analytics-provider-cs316: Validate CS-316 Analytics Provider Ingestion
Status: ready-to-dev

## Trigger / Source

Mode: Repo-informed story.

Source brief: `_story_briefs/cs-318-valider-ingestion-analytics-provider-cs316.md`.

CS-316 is repository-complete, but the local analytics provider is `noop`; real Plausible or Matomo ingestion remains an external QA proof.

Source-alignment evidence: this story preserves the brief stakes by requiring provider/environment identification, seven CS-311 event checks,
redacted payload proof, frontend validation, and a precise external blocker when no observable analytics environment is available.

## Objective

Validate that the seven CS-311 and CS-316 `/natal` analytics events reach an observable Plausible or Matomo provider with redacted payloads,
or produce a bounded external blocker proving that no suitable provider environment was available during execution.

## Target State

- A staging or production analytics provider environment is identified with provider name, environment label, date, and access status.
- The seven CS-311 event names are triggered or each non-triggerable event is classified with a concrete reason.
- Provider-side evidence records event names and public fields without storing birth data, coordinates, prompts, secrets, or provider raw dumps.
- The acceptance report links CS-316 local evidence to the external provider result or to the external-access blocker.
- Existing CS-316 frontend analytics tests remain green after the validation pass.
- A proven emission or redaction defect is corrected in the narrowest owning frontend file or converted into a separate brief.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-318-valider-ingestion-analytics-provider-cs316.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-318`.
- Evidence 3: `_condamad/reports/CS-312-CS-316-delivery-report.md` - CS-316 external validation gap confirmed.
- Evidence 4: `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/generated/10-final-evidence.md` - CS-316 closure reviewed.
- Evidence 5: `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/analytics-runtime-config.json` - local `noop` provider confirmed.
- Evidence 6: `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/analytics-ingestion-ledger.json` - seven-event ledger reviewed.
- Evidence 7: `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/external-validation-required.md` - external handoff reviewed.
- Evidence 8: `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/event-catalog.json` - event catalog reviewed.
- Evidence 9: `frontend/src/hooks/useAnalytics.ts` - analytics boundary and redaction function inspected.
- Evidence 10: `frontend/src/features/natal-chart/NatalInterpretation.tsx` - `/natal` event emission points inspected.
- Evidence 11: `_condamad/stories/regression-guardrails.md` - registry consulted through resolver output and targeted analytics searches.

## Domain Boundary

- Domain: frontend-analytics-external-validation
- In scope:
  - Plausible or Matomo environment identification for `/natal` analytics ingestion.
  - External provider observation for `started`, `success`, `api_error`, `entitlement_denied`, `empty`, `degraded`, and `retry`.
  - Redacted payload comparison against the CS-311 public field catalog.
  - Persistent acceptance evidence under this CS-318 story capsule.
  - Existing CS-316 frontend lint and Vitest validation.
  - Narrow frontend emission or redaction bug fix only when provider evidence proves the defect.
- Out of scope:
  - Backend API, database schema, auth, i18n, styling, build tooling, migrations, prompts, persistence, providers LLM, and replay.
  - New analytics provider, dashboard, alerting system, event taxonomy, or monitoring platform.
  - Storage of real birth data, coordinates, prompts, raw AI output, secrets, passwords, or provider raw payload exports.
- Explicit non-goals:
  - No provider implementation or provider replacement.
  - No change to CS-311 event names, allowed fields, or redaction policy without a separate brief.
  - No broad QA campaign outside provider ingestion for `/natal` analytics events.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits an external analytics provider-ingestion acceptance contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Produce external provider evidence or an explicit external-access blocker.
  - Change frontend analytics source only when the provider run proves an emission or redaction defect.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: no authorized Plausible or Matomo environment can be accessed for observation.
- Additional validation rules:
  - The provider proof must name the provider, environment, capture date, and observer source.
  - The provider proof must cover all seven CS-311 event names or classify each non-triggerable event.
  - The proof must include a generated manifest: `evidence/provider-ingestion-ledger.json`.
  - Sensitive field checks must use the CS-311 forbidden field list, not a newly invented list.
  - Provider-unavailable closure must include `evidence/external-access-blocker.md`.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Provider dashboard or blocker evidence is the runtime truth for external ingestion. |
| Baseline Snapshot | yes | CS-316 local ledger and CS-311 catalog are the baseline for observed provider data. |
| Ownership Routing | yes | Evidence and any narrow bug fix need canonical destinations. |
| Allowlist Exception | no | No allowlist handling is authorized for this provider validation. |
| Contract Shape | yes | The provider ledger has exact provider, event, field, redaction, and status keys. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Direct provider calls and alternate event names must stay out of feature code. |
| Persistent Evidence | yes | Provider proof, blocker proof, and validation logs must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Provider environment is identified. | Evidence profile: external_usage_blocker; `python` checks provider or blocker fields. |
| AC2 | All seven events are accounted for. | Evidence profile: json_contract_shape; `python` validates `evidence/provider-ingestion-ledger.json` against CS-311 catalog. |
| AC3 | Observed payload fields are public. | Evidence profile: json_contract_shape; `python` compares ledger fields to `event-catalog.json`. |
| AC4 | Sensitive evidence is absent. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans CS-318 evidence for forbidden field names. |
| AC5 | Provider result is persisted. | Evidence profile: baseline_before_after_diff; `python` checks `evidence/provider-ingestion-acceptance.md`. |
| AC6 | CS-316 frontend validation stays green. | Evidence profile: frontend_typecheck_no_orphan; `pnpm lint` and targeted `vitest` output are persisted. |
| AC7 | Anomalies have a closure path. | Evidence profile: baseline_before_after_diff; `python` checks report text; Manual check: review fixed defects or brief paths. |

## Implementation Tasks

- [ ] Task 1: Read CS-316 final evidence, runtime config, ingestion ledger, external handoff, and CS-311 event catalog. (AC: AC1, AC2, AC3)
- [ ] Task 2: Identify the observable Plausible or Matomo environment and document access status. (AC: AC1)
- [ ] Task 3: Trigger or classify the seven CS-311 event states in the selected environment. (AC: AC2)
- [ ] Task 4: Capture provider-side observations in `evidence/provider-ingestion-ledger.json` without storing raw payload dumps. (AC: AC2, AC3)
- [ ] Task 5: Run the sensitive-field comparison and persist the redaction scan output. (AC: AC3, AC4)
- [ ] Task 6: Write `evidence/provider-ingestion-acceptance.md` or `evidence/external-access-blocker.md`. (AC: AC1, AC5)
- [ ] Task 7: Correct only a proven frontend emission or redaction defect, or create a separate brief for larger work. (AC: AC7)
- [ ] Task 8: Run and persist CS-316 frontend lint and Vitest validation after the provider validation pass. (AC: AC6)
- [ ] Task 9: Write `generated/10-final-evidence.md` with source alignment, final provider status, and reviewer focus. (AC: AC5, AC7)

## Files to Inspect First

- `_condamad/reports/CS-312-CS-316-delivery-report.md`
- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/generated/10-final-evidence.md`
- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/analytics-runtime-config.json`
- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/analytics-ingestion-ledger.json`
- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/external-validation-required.md`
- `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/event-catalog.json`
- `frontend/src/hooks/useAnalytics.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/tests/useAnalytics.test.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/natalChartApi.test.ts`

## Runtime Source of Truth

- Primary source of truth:
  - Observable Plausible or Matomo provider dashboard, export summary, or environment-owner confirmation.
  - Loaded config from `ANALYTICS_CONFIG` in the selected frontend environment.
  - `evidence/provider-ingestion-ledger.json` generated from the provider observation.
  - Generated manifest `evidence/provider-ingestion-ledger.json`.
  - `evidence/external-access-blocker.md` when provider access is unavailable.
- Secondary evidence:
  - CS-316 local `analytics-ingestion-ledger.json`, CS-311 `event-catalog.json`, targeted Vitest, full Vitest, and `pnpm lint`.
- Static scans alone are not sufficient for this story because:
  - The source gap is real provider ingestion, not only repository-local event emission.

## Contract Shape

- Contract type:
  - External analytics provider ingestion acceptance ledger.
- Fields:
  - `provider`: `plausible` or `matomo`; use `unavailable` only in blocker evidence.
  - `environment`: staging, production, or the exact approved environment label.
  - `captured_at`: ISO date or timestamp for the provider observation.
  - `event_name`: one event name from CS-311 `event-catalog.json`.
  - `state`: one CS-311 projection analytics state.
  - `observed`: boolean provider-ingestion result.
  - `trigger_status`: `triggered`, `not_triggerable`, or `blocked`.
  - `observed_fields`: public field names observed after redaction.
  - `forbidden_fields_present`: forbidden field names observed in provider evidence.
  - `result`: `pass`, `not_triggerable`, or `blocked_external_access`.
- Required fields:
  - `provider`, `environment`, `captured_at`, `event_name`, `state`, `observed`, `trigger_status`, `observed_fields`, and `result`.
- Optional fields:
  - `provider_reference`, `observer`, `notes`, `linked_bug_fix`, and `separate_brief`.
- Status codes:
  - No HTTP status-code contract is owned by the provider ingestion ledger.
- Serialization names:
  - JSON keys are emitted exactly as listed in this section.
- Frontend type impact:
  - Any proven bug fix must remain typed under the existing frontend TypeScript configuration.
- Generated contract impact:
  - `generated/10-final-evidence.md` must summarize provider status, seven-event coverage, redaction result, and closure state.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/analytics-runtime-config.json`
  - `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/analytics-ingestion-ledger.json`
  - `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/external-validation-required.md`
  - `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/event-catalog.json`
- Comparison after implementation:
  - `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/evidence/provider-environment.md`
  - `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/evidence/provider-ingestion-ledger.json`
  - `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/evidence/provider-ingestion-acceptance.md`
  - `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/evidence/external-access-blocker.md`
- Expected invariant:
  - The intended delta is external provider proof or a precise external-access blocker for the CS-316 ingestion gap.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Analytics provider config | `frontend/src/config/analytics.ts` | Feature components |
| Analytics emission boundary | `frontend/src/hooks/useAnalytics.ts` | Direct provider calls in `frontend/src/features/**` |
| Natal projection instrumentation | `frontend/src/features/natal-chart/NatalInterpretation.tsx` | Backend or API client modules |
| Provider validation evidence | `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/evidence/` | External-only dashboard notes |
| Final evidence | `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/generated/10-final-evidence.md` | Repository root |

## Mandatory Reuse / DRY Constraints

- Reuse the CS-311 event catalog for event names, allowed fields, and forbidden fields.
- Reuse CS-316 local ledger as the handoff baseline; do not create a second local event taxonomy.
- Reuse `sanitizeAnalyticsProps` as the redaction boundary when a code defect is proven.
- Reuse `ANALYTICS_CONFIG` as the provider selection source when frontend code is inspected.
- Keep one provider-ingestion ledger for the external result; do not split provider status across duplicate JSON files.

## No Legacy / Forbidden Paths

- No legacy analytics event name may be added during this validation.
- No compatibility analytics provider path may be added during this validation.
- No fallback provider, shim provider, mocked production sink, or feature-level direct provider call may be introduced.
- Do not add dashboard, alerting, backend, persistence, prompt, provider, replay, style, or migration changes.
- Do not preserve legacy behavior through hidden mappers, aliases, broad allowlists, or duplicated event catalogs.

## Reintroduction Guard

- Guard target:
  - CS-318 must not close external ingestion by restating CS-316 local `noop` evidence as provider proof.
- Required guard:
  - `python` validates `provider-ingestion-ledger.json` against the CS-311 event catalog or validates the external-access blocker.
  - `rg` verifies no direct `plausible(`, `_paq.push`, or new analytics provider call appears in `frontend/src/features`.

## Regression Guardrails

| Guardrail | Local invariant | Evidence |
|---|---|---|
| RG-047 `inline-styles` | A validation helper must not add static inline TSX styles. | `rg` scan from `frontend`; `pnpm lint`. |
| Registry gap `analytics-provider-ingestion` | No exact provider-ingestion guardrail was resolved. | Resolver output and provider ledger validation. |
| Registry gap `natal-analytics-redaction` | No exact `/natal` analytics redaction guardrail was resolved. | CS-311 catalog comparison and `rg` scan. |

Non-applicable examples: RG-027 backend prediction infra, RG-041 entitlement documentation, and RG-042 LLM docs are not local to this scope.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Environment | `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/evidence/provider-environment.md` | Record access status. |
| Provider ledger | `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/evidence/provider-ingestion-ledger.json` | Preserve seven-event provider observations. |
| Acceptance | `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/evidence/provider-ingestion-acceptance.md` | Summarize proof. |
| Access blocker | `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/evidence/external-access-blocker.md` | Preserve unavailable-provider proof. |
| Validation log | `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/evidence/validation-frontend.txt` | Preserve lint and Vitest command output. |
| Final evidence | `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/generated/10-final-evidence.md` | Summarize final closure for review. |
| Review output | `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist required: no
- Reason: no allowlist handling is authorized for this provider validation.
- Expiry / permanence: permanent not applicable because no allowlist entry exists.
- Required action: keep any discovered provider, event, or redaction defect either fixed narrowly or moved to a separate brief.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/evidence/provider-environment.md` - provider access status.
- `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/evidence/provider-ingestion-ledger.json` - provider observation ledger.
- `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/evidence/provider-ingestion-acceptance.md` - acceptance summary.
- `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/evidence/external-access-blocker.md` - external blocker proof.
- `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/evidence/validation-frontend.txt` - validation command output.
- `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/generated/10-final-evidence.md` - closure evidence.

Likely tests:

- `frontend/src/tests/useAnalytics.test.tsx` - validate analytics provider boundary and redaction behavior.
- `frontend/src/tests/natalInterpretation.test.tsx` - validate `/natal` event emission states.
- `frontend/src/tests/natalChartApi.test.ts` - validate natal API client behavior used by projection states.

Conditional files:

- `frontend/src/hooks/useAnalytics.ts` - only for a proven redaction or provider-call bug.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - only for a proven event emission bug.
- `frontend/src/tests/useAnalytics.test.tsx` - only for a proven analytics boundary bug.
- `frontend/src/tests/natalInterpretation.test.tsx` - only for a proven `/natal` event emission bug.

Files not expected to change:

- `backend/**` - out of scope; no backend surface is touched.
- `frontend/src/**/*.css` - out of scope; no styling surface is touched.
- `frontend/src/config/analytics.ts` - out of scope unless provider configuration itself is proven defective.
- `package.json` and lockfiles - out of scope; no dependency change is authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-318-valider-ingestion-analytics-provider-cs316\00-story.md`
- VC2: `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-318-valider-ingestion-analytics-provider-cs316\00-story.md`
- VC3: `python` validates that `evidence/provider-ingestion-ledger.json` contains seven events.
- VC4: `python` checks that provider acceptance evidence or external-access blocker evidence exists.
- VC5: `rg` scans CS-318 evidence for birth, coordinate, provider raw, replay, prompt, secret, and password field names.
- VC6: `rg -n "plausible\(|_paq\.push|trackEvent" frontend/src/features`
- VC7: Working directory `frontend`; `pnpm lint`
- VC8: Working directory `frontend`; `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics natalInterpretation natalChartApi`
- VC9: Working directory `frontend`; `node .\scripts\run-vite-logged.mjs vitest vitest run`

## Regression Risks

- External provider access may be unavailable, so the story can close only with a precise blocker and no simulated proof.
- Provider dashboards may expose raw payload details; the implementation must summarize public fields without committing raw sensitive exports.
- Triggering every event may require controlled user states; non-triggerable events need a concrete reason and reviewer-readable evidence.
- A provider-side anomaly may reveal a real frontend bug; only the narrow owning file may change inside this story.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the Python virtual environment before any Python command in this repository.
- Store provider proof as summarized evidence only; do not commit raw sensitive provider exports.
- Keep all markdown table rows below 180 characters.

## References

- `_story_briefs/cs-318-valider-ingestion-analytics-provider-cs316.md`
- `_condamad/reports/CS-312-CS-316-delivery-report.md`
- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/generated/10-final-evidence.md`
- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/analytics-runtime-config.json`
- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/analytics-ingestion-ledger.json`
- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/evidence/external-validation-required.md`
- `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/evidence/event-catalog.json`
- `frontend/src/hooks/useAnalytics.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
