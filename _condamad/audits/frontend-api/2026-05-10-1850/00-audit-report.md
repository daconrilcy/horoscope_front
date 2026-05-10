# Frontend API Domain Audit - 2026-05-10-1850

## Scope

- Domain key: `frontend-api`
- Target: `frontend/src/api`
- Mode: read-only audit plus CONDAMAD audit artifacts
- Archetype: frontend API client boundary, No Legacy / DRY, dependency direction
- Closure status: `blocked`

## Prior Audit And Guardrail History

| Source | Status | Evidence | Notes |
|---|---|---|---|
| Prior `_condamad/audits/frontend-api/**` | none | E-012 | No prior audit for this exact domain. |
| Related frontend audits | consulted as context | E-012 | Existing audits cover components, pages, layouts, design-system, and App CSS, not this API folder directly. |
| `_condamad/stories/regression-guardrails.md` | consulted | E-011 | Applicable invariants: RG-053, RG-057, RG-064, RG-069. |

## Findings Summary

| Severity | Findings |
|---|---|
| Critical | none |
| High | F-001, F-002 |
| Medium | F-003, F-004, F-005, F-006 |
| Low | none |
| Info | none |

## Findings

See `02-finding-register.md` for the full register. The active implementation findings are:

- F-001: direct backend `fetch` calls bypass the central transport helper.
- F-002: error and response envelope handling is duplicated.
- F-003: large API files own too many concerns.
- F-004: an API module imports from the public `@api` barrel.
- F-005: `support.ts` mixes support and ops persona ownership.
- F-006: the flat barrel-based organization needs a public API policy decision.

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `frontend/src/api/adminContent.ts` | intentional-public-export | E-001,E-010,E-014 | Exported via `index.ts` and consumed through `@api` by `AdminContentPage`. | Needs future split under admin/content. |
| `frontend/src/api/adminDashboard.ts` | used | E-001,E-010,E-014 | Imported directly by `AdminDashboardPage`. | none |
| `frontend/src/api/adminLogs.ts` | used | E-001,E-010,E-014 | Imported directly by `AdminLogsPage`. | none |
| `frontend/src/api/adminOperations.ts` | used | E-001,E-010,E-014 | Imported by several admin pages. | Surface mixes AI, entitlements, exports, support. |
| `frontend/src/api/adminPrompts.ts` | used | E-001,E-002,E-010,E-014,E-015 | Consumed by admin prompts feature and i18n type modules. | Large public surface requires staged split. |
| `frontend/src/api/adminUsers.ts` | used | E-001,E-010,E-014 | Imported by admin user pages. | none |
| `frontend/src/api/astrologers.ts` | used | E-001,E-010,E-014 | Used by pages/features and typed components. | Contains mock/export helpers that require separate No Legacy review before deletion. |
| `frontend/src/api/auth.ts` | intentional-public-export | E-001,E-010,E-014 | Consumed through `@api` by auth feature forms. | none |
| `frontend/src/api/authMe.ts` | used | E-001,E-010,E-014 | Used by guards, layouts, and settings. | none |
| `frontend/src/api/b2bAstrology.ts` | needs-user-decision | E-001,E-009,E-014 | Exported and tested, but no runtime consumer found under current scan. | Barrel public intent is ambiguous. |
| `frontend/src/api/b2bBilling.ts` | needs-user-decision | E-001,E-009,E-014 | Exported and tested, but no runtime consumer found under current scan. | Barrel public intent is ambiguous. |
| `frontend/src/api/b2bEditorial.ts` | needs-user-decision | E-001,E-009,E-014 | Exported and tested, but no non-test runtime consumer was found for `useB2BEditorialConfig`. | Barrel public intent is ambiguous. |
| `frontend/src/api/b2bReconciliation.ts` | used | E-001,E-010,E-014 | Runtime consumer `B2BReconciliationPanel`. | none |
| `frontend/src/api/b2bUsage.ts` | needs-user-decision | E-001,E-009,E-014 | Exported and tested, but no runtime consumer found under current scan. | Barrel public intent is ambiguous. |
| `frontend/src/api/billing.ts` | used | E-001,E-010,E-014 | Used by chat, settings, subscription, billing success, and admin pricing. | Direct fetch drift remains under F-001. |
| `frontend/src/api/birthProfile.ts` | used | E-001,E-010,E-014 | Used by `BirthProfilePage`, `useBirthData`, and tests. | none |
| `frontend/src/api/chat.ts` | used | E-001,E-010,E-014 | Used by `ChatPage` and chat component types. | none |
| `frontend/src/api/client.ts` | used | E-001,E-004,E-010,E-014 | Central API transport and `ApiError` owner. | Needs more shared parsing helpers. |
| `frontend/src/api/consultations.ts` | used | E-001,E-010,E-014 | Used by consultation pages/features/store. | none |
| `frontend/src/api/dailyPrediction.ts` | used | E-001,E-010,E-014 | Request owner consumed by `useDailyPrediction`. | none |
| `frontend/src/api/enterpriseCredentials.ts` | used | E-001,E-010,E-014 | Runtime consumer `EnterpriseCredentialsPanel`. | Direct fetch drift remains under F-001. |
| `frontend/src/api/geocoding.ts` | used | E-001,E-003,E-010,E-014 | Used by birth profile, consultation form, and utility wrapper; direct calls target backend `/v1/geocoding/*` proxy endpoints. | Uses a domain-specific timeout path that must be preserved or explicitly reimplemented when converging transport. |
| `frontend/src/api/guidance.ts` | needs-user-decision | E-001,E-009,E-014 | Exported and tested, but no non-test runtime consumer was found for guidance request functions or hooks. | Barrel public intent and feature roadmap are ambiguous. |
| `frontend/src/api/help.ts` | used | E-001,E-010,E-014 | Used by support pages. | Direct fetch drift remains under F-001. |
| `frontend/src/api/index.ts` | intentional-public-export | E-001,E-010,E-014 | Configured alias `@api` maps to this public facade. | F-006 requires decision whether this remains canonical. |
| `frontend/src/api/natalChart.ts` | used | E-001,E-002,E-010,E-014,E-015 | Used by natal page and natal feature interpretation. | Large public surface requires split. |
| `frontend/src/api/opsMonitoring.ts` | needs-user-decision | E-001,E-009,E-014 | Exported by barrel, but no runtime consumer found under current scan. | Barrel public intent is ambiguous. |
| `frontend/src/api/opsPersona.ts` | used | E-001,E-007,E-008,E-014 | Canonical owner for ops persona hooks; consumed indirectly by `support.ts`. | Support re-export should be removed or justified. |
| `frontend/src/api/privacy.ts` | used | E-001,E-010,E-014 | Used by delete-account settings modal and tests. | none |
| `frontend/src/api/support.ts` | used | E-001,E-007,E-008,E-010,E-014 | Used by support ops feature through `@api`. | Cross-domain ops re-export and placeholder endpoint remain. |
| `frontend/src/api/useBirthData.ts` | used | E-001,E-010,E-014 | Used by daily horoscope page, dashboard summary, and prefetch helper. | Naming should move under domain subfolder if F-006 chooses domain entrypoints. |
| `frontend/src/api/useDailyPrediction.ts` | used | E-001,E-006,E-010,E-014 | Used by daily horoscope page, dashboard summary, prefetch helper, hook wrapper, and tests. | Contains in-domain barrel import. |
| `frontend/src/api/userSettings.ts` | used | E-001,E-010,E-014 | Used by astrologers pages and account settings. | none |

## Organization Review

Recommended target if the project keeps an API client layer:

```text
frontend/src/api/
  core/
    client.ts
    errors.ts
    queryKeys.ts
  public/
    auth/
    astrologers/
    billing/
    birth-profile/
    daily-prediction/
    geocoding/
    help/
    privacy/
    support/
  features/
    chat/
    consultations/
    natal-chart/
    guidance/
  admin/
    content/
    dashboard/
    logs/
    operations/
    prompts/
    users/
  b2b/
    astrology/
    billing/
    editorial/
    reconciliation/
    usage/
    credentials/
  ops/
    monitoring/
    persona/
  index.ts
```

The migration should preserve behavior first, then reduce the global barrel after the public facade decision in F-006.

## Closure Analysis

Active in-domain findings remain: F-001 through F-006. No finding is closed by current evidence. F-006 blocks deletion/classification of public-export-only B2B/Ops/guidance modules because repository evidence cannot prove whether `@api` is meant as an external public facade or a convenience barrel.

Implementation files implicated by active findings are enumerated in `03-story-candidates.md`. Governance/test files are not currently owned by this audit except proposed guard files in SC-004.

## Deferred Non-Domain Context

Backend runtime verification for support search-by-email and B2B/Ops endpoints is deferred to a backend API contract audit.
