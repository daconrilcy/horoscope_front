<!-- Rapport d'audit CONDAMAD des pages React du frontend. -->

# Audit Report - frontend-react-pages

## Scope

- Domain key: `frontend-react-pages`
- Audit date: `2026-05-08-0123`
- Archetype: `legacy-surface-audit` with `no-legacy-dry-audit-contract`; additional mandatory checks for DRY, mono-owner, dependency direction, and test guards.
- Mode: read-only for application code; audit artifacts written under `_condamad/audits/**`.
- Audited surface: `frontend/src/pages/**`, page routing in `frontend/src/app/routes.tsx`, page-facing feature/component/API boundaries, and page-related tests.

## Context

The user reported confusing React page organization, chaotic structure, and repeated code between pages. The repository already has strong frontend design-system guardrails (`RG-044` through `RG-063`), but those protect styling/token drift more than page ownership and React module boundaries.

Relevant regression guardrails consulted:

- `RG-044` through `RG-063` protect frontend design-system, inline style, fallback, legacy CSS, and runtime compatibility surfaces.
- `RG-054` protects removed legacy admin redirects.
- No existing guardrail was found for React page size, page-owned API clients, page barrel exports, or page/domain ownership.

## Executive Finding Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 2 |
| Medium | 4 |
| Low | 0 |
| Info | 0 |

## Main Conclusion

The confusion is structural, not cosmetic. Several pages own too many responsibilities at once: route container, API orchestration, DTO definitions, local utilities, modal components, tab state, and detailed presentation. The most severe example is `frontend/src/pages/admin/AdminPromptsPage.tsx`, which is a 3035-line page with `// @ts-nocheck`, many internal helpers/components, and more than 50 local state/effect declarations. The same pattern appears at smaller scale in admin KPI/log pages, chat, birth profile, natal chart, astrologer profile, and subscription pages.

The repeated code is mainly caused by missing canonical owners:

- admin API calls and DTOs are implemented directly in pages with `apiFetch`;
- formatting/error/path helpers are duplicated inside page files;
- page barrels keep old or duplicate export paths active;
- route aliases and compatibility redirects remain mixed with canonical routes.

## Findings

See `02-finding-register.md` for details.

Top risks:

1. `F-001`: `AdminPromptsPage` is a high-risk monolith and bypasses TypeScript checking.
2. `F-002`: admin pages duplicate API/query/error responsibilities instead of using a canonical admin API layer.
3. `F-004` and `F-005`: legacy import/route surfaces remain active, which keeps old ownership paths available.

## Recommended Story Order

1. Extract a typed admin prompts feature boundary from `AdminPromptsPage`.
2. Create canonical admin API hooks/contracts and migrate direct `apiFetch` pages.
3. Converge page barrels and legacy route aliases with explicit user decisions for public redirects.
4. Add page architecture guards so this structure does not regress.

## Validation

Read-only evidence collection completed. Application lint/tests were not run because this audit did not modify application code. Audit artifact validation was run after report generation; see `01-evidence-log.md`.
