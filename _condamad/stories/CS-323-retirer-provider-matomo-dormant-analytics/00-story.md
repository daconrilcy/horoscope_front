# Story CS-323 retirer-provider-matomo-dormant-analytics: Retirer Le Provider Matomo Dormant De L'Analytics Frontend
Status: ready-to-dev

## 1. Objective

Retirer le provider Matomo dormant du chemin actif analytics frontend.
Le frontend doit conserver uniquement `noop` comme defaut local et `plausible` comme provider prepare.

## 2. Trigger / Source

- Source type: brief direct
- Source reference: `_story_briefs/cs-323-retirer-provider-matomo-dormant-analytics.md`
- Reason for change: Matomo reste dans le type provider et dans une branche `_paq` non utilisee, ce qui augmente la surface de maintenance.
- Source-alignment evidence: la story couvre le retrait du type, de la branche `_paq`, des tests, des docs/env examples et du scan final.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend-analytics`
- In scope:
  - Retirer `matomo` de `AnalyticsProvider`.
  - Supprimer le type et la branche `_paq` dans `frontend/src/hooks/useAnalytics.ts`.
  - Conserver les comportements `noop` et Plausible.
  - Mettre a jour les tests analytics frontend.
  - Mettre a jour les mentions de configuration active dans `.env.example` et docs concernees.
  - Persister les preuves de scan et validation dans la capsule CS-323.
- Out of scope:
  - Activer Plausible en production.
  - Ajouter un nouveau provider analytics.
  - Modifier la taxonomie des evenements.
  - Modifier l'instrumentation metier CS-311.
  - Modifier backend, DB, migrations, prompts, providers LLM, auth, i18n, style ou build tooling.
- Explicit non-goals:
  - No frontend route, screen, client generation, backend API, database schema, auth, i18n, styling, build tooling, or migration change.
  - No provider shim or dormant provider replacement.
  - No direct provider call outside `frontend/src/hooks/useAnalytics.ts`.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: the story removes an inactive frontend analytics provider branch and forbids dormant provider preservation.
- Behavior change allowed: constrained
- Behavior change constraints:
  - `noop` remains the local default provider.
  - Plausible remains the only prepared external provider.
  - CS-311 and CS-316 analytics payload redaction remains unchanged.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: a production, staging, public doc, or external analytics surface proves Matomo is actively required.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Vitest proves provider behavior and redaction through the loaded frontend modules. |
| Baseline Snapshot | yes | Before and after scans prove the removed provider surface and the only allowed surface delta. |
| Ownership Routing | yes | Provider calls must remain centralized in `useAnalytics`. |
| Allowlist Exception | no | No allowlist entry is authorized for Matomo or `_paq`. |
| Contract Shape | yes | `AnalyticsProvider` must expose only `plausible` and `noop`. |
| Batch Migration | no | This is one bounded provider removal, not a multi-batch migration. |
| Reintroduction Guard | yes | Matomo symbols and `_paq` must stay absent from active frontend source. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - loaded config from `frontend/src/config/analytics.ts`
  - AST guard through TypeScript and Vitest module loading
  - `frontend/src/config/analytics.ts`
  - `frontend/src/hooks/useAnalytics.ts`
  - `frontend/src/tests/useAnalytics.test.tsx`
  - Vitest execution through `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics`
- Secondary evidence:
  - Targeted `rg` scans for `matomo`, `_paq`, direct provider calls, and sensitive field names.
- Static scans alone are not sufficient for this story because:
  - Provider behavior and redaction must be proven by executable frontend tests.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/evidence/provider-scan-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/evidence/provider-scan-after.txt`
- Expected invariant:
  - The only allowed active frontend analytics surface delta is removal of Matomo and `_paq`.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Provider selection | `frontend/src/config/analytics.ts` | Feature, component, page, API or test-only provider config |
| Provider emission | `frontend/src/hooks/useAnalytics.ts` | Direct calls in features, components, pages or API modules |
| Redaction list | `SENSITIVE_ANALYTICS_FIELD_NAMES` in `useAnalytics.ts` | Duplicate sensitive-field list in tests or features |

## 4e. Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no Matomo, `_paq`, compatibility provider, fallback provider, or broad allowlist handling is authorized.

## 4f. Contract Shape

- Contract type:
  - frontend TypeScript provider union and hook behavior.
- Fields:
  - `AnalyticsProvider`: union of `plausible` and `noop`.
  - `ANALYTICS_CONFIG.provider`: loaded from `VITE_ANALYTICS_PROVIDER` and defaulting to `noop`.
  - `SENSITIVE_ANALYTICS_FIELD_NAMES`: unchanged sensitive field catalog.
- Required fields:
  - `plausible`
  - `noop`
- Optional fields:
  - none
- Status codes:
  - no HTTP status code contract is touched.
- Serialization names:
  - Plausible event props remain sanitized before emission.
- Frontend type impact:
  - TypeScript must reject `matomo` as an `AnalyticsProvider`.
- Generated contract impact:
  - no generated API contract or generated client is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before provider scan | `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/evidence/provider-scan-before.txt` | Capture current Matomo and `_paq` hits. |
| After provider scan | `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/evidence/provider-scan-after.txt` | Prove no active frontend hits remain. |
| Validation log | `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/evidence/validation-frontend.txt` | Persist lint, Vitest and scan outcomes. |
| Removal audit | `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/evidence/removal-audit.md` | Classify removed symbols and risks. |
| Review output | `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## 4i. Reintroduction Guard

- Guard target: forbidden symbols `matomo`, `_paq`, and direct provider calls outside `useAnalytics`.
- Architecture guard against reintroduction required: AST guard plus targeted `rg` scans.
- Architecture guard against reintroduction: required
  - AST guard: TypeScript plus Vitest must load the analytics config and hook without Matomo.
  - `rg -n "matomo|_paq" frontend/src .env.example docs _story_briefs`
  - `rg -n "plausible\(" frontend/src/features frontend/src/components frontend/src/pages frontend/src/api`
- Reintroduced forbidden symbols must fail the guard before review handoff.
- Guard evidence: Evidence profile: `reintroduction_guard`; `pnpm lint`, targeted Vitest, and targeted `rg` scans.

## 5. Current State Evidence

- Evidence 1: `_story_briefs/cs-323-retirer-provider-matomo-dormant-analytics.md` - source brief read for this story.
- Evidence 2: `_story_briefs/cs-321-preparer-integration-plausible-analytics.md` - Plausible decision source confirms Matomo is not configured.
- Evidence 3: `frontend/src/config/analytics.ts` - `AnalyticsProvider` currently includes `matomo`.
- Evidence 4: `frontend/src/hooks/useAnalytics.ts` - current hook contains `_paq` typing and a Matomo branch.
- Evidence 5: `frontend/src/tests/useAnalytics.test.tsx` - existing tests cover `noop`, Plausible and sensitive-field redaction.
- Evidence 6: `.env.example` - analytics provider variables are documented with empty local provider and Plausible host.
- Evidence 7: `_condamad/stories/story-status.md` - tracker consulted to assign the story number.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - local guardrail registry consulted through resolver and targeted analytics search.
- Evidence 9: CS-316 and CS-318 final evidence - analytics redaction and provider validation history reviewed.
- Registry gap: no exact analytics-provider guardrail exists for Matomo or `_paq`; the story uses local reintroduction scans instead.
- Source-alignment review result: objective, target state, ACs, tasks, evidence and non-goals preserve all CS-323 source stakes.

## 6. Target State

- `AnalyticsProvider` exposes only `plausible` and `noop`.
- `useAnalytics.ts` contains no `_paq` type, no Matomo branch and no inactive provider path.
- Plausible continues to emit only sanitized props.
- `noop` remains the local default.
- `.env.example` and docs do not present Matomo as a configured active option.
- The capsule contains before/after scans and validation evidence.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Scope vector:
  - operation `remove`
  - domain `frontend-analytics`
  - paths `frontend/src/config/analytics.ts`, `frontend/src/hooks/useAnalytics.ts`, `frontend/src/tests/useAnalytics.test.tsx`
  - contracts `analytics-provider`, `no-legacy`, `redaction`
- Applicable invariants:
  - Registry gap: no exact analytics-provider guardrail is registered; enforce local `matomo|_paq` scans in this story.
- Needs-investigation:
  - none
- Non-applicable examples:
  - `RG-047` style inline guard is out of scope because this story does not touch TSX styling.
  - `RG-052` CSS namespace guard is out of scope because no CSS token namespace changes are allowed.
  - `RG-027` prediction infra boundary is out of scope because this story only touches frontend analytics.
- Required regression evidence:
  - `pnpm lint`
  - `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics`
  - `rg -n "matomo|_paq" frontend/src .env.example docs _story_briefs`
  - `rg -n "plausible\(" frontend/src/features frontend/src/components frontend/src/pages frontend/src/api`
- Allowed differences:
  - `matomo` may remain in historical `_story_briefs` and CONDAMAD evidence, but active `frontend/src` must be clear.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `AnalyticsProvider` excludes `matomo`. | Evidence profile: `field_removed`; `pnpm lint`; `rg -n "matomo" frontend/src/config/analytics.ts`. |
| AC2 | `_paq` is absent from active hook source. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "_paq" frontend/src/hooks/useAnalytics.ts`. |
| AC3 | `noop` remains the local default. | Evidence profile: `frontend_typecheck_no_orphan`; `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics`. |
| AC4 | Plausible still receives sanitized props. | Evidence profile: `json_contract_shape`; `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics`. |
| AC5 | Direct provider calls stay centralized. | Evidence profile: `repo_wide_negative_scan`; `rg` direct-call scan over frontend app surfaces. |
| AC6 | Docs omit active Matomo option. | Evidence profile: `targeted_forbidden_symbol_scan`; AST guard plus `rg -n "matomo|_paq" frontend/src .env.example docs`. |
| AC7 | Redaction runtime covered. | Evidence profile: `frontend_typecheck_no_orphan`; AST guard; `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics`. |
| AC8 | No backend Matomo path exists. | Evidence profile: `repo_wide_negative_scan`; AST guard plus `rg -n "matomo|_paq" backend`. |
| AC9 | Persistent evidence artifacts exist. | Evidence profile: `baseline_before_after_diff`; `python` checks CS-323 evidence paths. |

## 8. Implementation Tasks

- [ ] Task 1: Capture provider baseline scan and removal audit for `matomo` and `_paq`. (AC: AC1, AC2, AC6, AC9)
- [ ] Task 2: Remove `matomo` from `AnalyticsProvider` and keep `noop` local default behavior. (AC: AC1, AC3)
- [ ] Task 3: Delete `_paq` typing and the Matomo branch from `useAnalytics.ts`. (AC: AC2, AC4)
- [ ] Task 4: Update analytics tests to prove `noop`, Plausible and redaction behavior. (AC: AC3, AC4, AC7)
- [ ] Task 5: Update `.env.example` or docs that present Matomo as an active option. (AC: AC6)
- [ ] Task 6: Capture final scans and validation logs in the CS-323 evidence folder. (AC: AC5, AC6, AC8, AC9)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/config/analytics.ts`
  - `frontend/src/hooks/useAnalytics.ts`
  - `frontend/src/tests/useAnalytics.test.tsx`
  - existing analytics event and redaction catalog.
- Do not recreate:
  - duplicate provider config.
  - duplicate sensitive-field list outside the existing hook module.
  - parallel analytics hook.
  - provider abstraction for a removed provider.
- Shared abstraction allowed only if:
  - it removes duplicated active Plausible/noop logic without adding a new provider path.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- legacy provider path
- compatibility provider path
- fallback provider path
- transitional alias
- duplicate active implementation
- preserving old path through re-export
- direct provider call outside `frontend/src/hooks/useAnalytics.ts`

Specific forbidden symbols / paths:

- `matomo` in active `frontend/src`
- `_paq` in active `frontend/src`
- `window._paq`
- `AnalyticsProvider = 'plausible' | 'matomo' | 'noop'`
- `VITE_ANALYTICS_PROVIDER=matomo`

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: `noop`, Plausible provider config, Plausible emission and redaction logic.
- `external-active`: any public production/staging doc or external analytics surface proving Matomo is required.
- `historical-facade`: dormant `matomo` provider type or `_paq` branch preserved for a provider not currently used.
- `dead`: `matomo` or `_paq` active code with no first-party production, test, docs or external consumer.
- `needs-user-decision`: any Matomo reference whose active external consumer cannot be ruled out by the required scans.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation for that item. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions for the audit: `keep`, `delete`, `replace-consumer`, `needs-user-decision`.

Audit output path:

- `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/evidence/removal-audit.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Analytics provider config | `frontend/src/config/analytics.ts` | feature, component, page, API or doc-only provider config |
| Analytics provider emission | `frontend/src/hooks/useAnalytics.ts` | direct provider call in `features`, `components`, `pages` or `api` |
| Analytics redaction | `SENSITIVE_ANALYTICS_FIELD_NAMES` and `sanitizeAnalyticsProps` | duplicate redaction map in UI code |
| Analytics provider tests | `frontend/src/tests/useAnalytics.test.tsx` | test-only provider branch outside the hook contract |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting Matomo to Plausible
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated provider active
- preserving the old provider through re-export
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If Matomo is classified as `external-active`, it must not be deleted.
The dev agent must stop and record exact evidence, consumer, risk and required user decision in `removal-audit.md`.

## 16. Generated Contract Check

- Generated contract check: required for the frontend type contract.
- Type contract source: `frontend/src/config/analytics.ts`.
- Required check:
  - `pnpm lint` must type-check the `AnalyticsProvider` union after `matomo` removal.
  - `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics` must load the analytics modules.
- Reason: the removed field is a frontend TypeScript provider value, not an OpenAPI or generated client field.

## 17. Files to Inspect First

- `_story_briefs/cs-321-preparer-integration-plausible-analytics.md`
- `_story_briefs/cs-323-retirer-provider-matomo-dormant-analytics.md`
- `frontend/src/config/analytics.ts`
- `frontend/src/hooks/useAnalytics.ts`
- `frontend/src/tests/useAnalytics.test.tsx`
- `.env.example`
- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/generated/10-final-evidence.md`
- `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md`

## 18. Expected Files to Modify

Likely files:

- `frontend/src/config/analytics.ts` - remove `matomo` from the provider union.
- `frontend/src/hooks/useAnalytics.ts` - remove `_paq` typing and Matomo branch.
- `frontend/src/tests/useAnalytics.test.tsx` - keep or adapt tests for `noop`, Plausible and redaction.
- `.env.example` - remove any Matomo active-provider wording discovered during implementation.
- `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/evidence/provider-scan-before.txt` - baseline scan.
- `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/evidence/provider-scan-after.txt` - final scan.
- `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/evidence/removal-audit.md` - classification proof.
- `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/evidence/validation-frontend.txt` - validation output.

Likely tests:

- `frontend/src/tests/useAnalytics.test.tsx`

Files not expected to change:

- `backend/**` - out of scope; no backend surface is touched.
- `shared/**` - out of scope; no shared contract is touched.
- `frontend/package.json` - no dependency change is authorized.
- `frontend/src/features/**` - only scans are expected; no feature instrumentation change is authorized.
- `frontend/src/components/**` - only scans are expected; no component provider call is authorized.
- `frontend/src/pages/**` - only scans are expected; no page provider call is authorized.

## 19. Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## 20. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics
node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics natalInterpretation natalChartApi
node .\scripts\run-vite-logged.mjs vitest vitest run
Pop-Location
rg -n "matomo|_paq" frontend/src .env.example docs _story_briefs
rg -n "plausible\(" frontend/src/features frontend/src/components frontend/src/pages frontend/src/api
rg -n "birth_date|birth_time|birth_place|latitude|longitude|provider_response|raw_runtime|replay_snapshot|prompt|api_key|password" frontend/src/hooks frontend/src/tests
.\.venv\Scripts\Activate.ps1
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/00-story.md
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/00-story.md
```

## 21. Regression Risks

- Risk: Plausible redaction breaks while deleting provider code.
  - Guardrail: AC4 and AC7 require targeted Vitest over analytics and natal projection surfaces.
- Risk: Matomo remains reachable through a type, window field, branch or env example.
  - Guardrail: AC1, AC2 and AC6 require targeted scans.
- Risk: Direct provider calls move into features or pages.
  - Guardrail: AC5 requires direct-call scan outside the hook owner.
- Risk: Historical CONDAMAD mentions are mistaken for active app code.
  - Guardrail: AC6 scopes active documentation separately from `_story_briefs` history.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 23. References

- `_story_briefs/cs-323-retirer-provider-matomo-dormant-analytics.md` - source brief.
- `_story_briefs/cs-321-preparer-integration-plausible-analytics.md` - Plausible preparation decision.
- `frontend/src/config/analytics.ts` - current provider union.
- `frontend/src/hooks/useAnalytics.ts` - current provider emission owner.
- `frontend/src/tests/useAnalytics.test.tsx` - analytics behavior and redaction tests.
- `.env.example` - frontend analytics env documentation.
- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/generated/10-final-evidence.md` - redaction evidence context.
- `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/generated/10-final-evidence.md` - provider validation context.
- `_condamad/stories/regression-guardrails.md` - guardrail registry consulted.
