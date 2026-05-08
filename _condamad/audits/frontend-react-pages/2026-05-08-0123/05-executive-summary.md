<!-- Synthese executive de l'audit CONDAMAD des pages React du frontend. -->

# Executive Summary - frontend-react-pages

## Bottom Line

The React pages are confusing because they are carrying feature ownership that should live elsewhere. The strongest signals are the 3035-line `AdminPromptsPage.tsx` with `@ts-nocheck`, repeated direct admin `apiFetch` usage across pages, duplicate page helper responsibilities, and stale/duplicate page barrel exports.

## Findings By Severity

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 2 |
| Medium | 4 |
| Low | 0 |
| Info | 0 |

## Highest-Value Next Action

Start with `SC-006` if you want a guardrail first, or `SC-001` if you want immediate structural cleanup. The pragmatic sequence is:

1. Add page-architecture guards with allowlisted existing debt.
2. Extract `AdminPromptsPage` one tab/slice at a time.
3. Centralize admin API hooks/contracts.
4. Clean barrels and route aliases once canonical owners are clear.

## Decision Needed

Decide whether `/today`, `/natal-chart`, and `/birth-profile` are supported public aliases or legacy redirects to remove. Without that decision, route cleanup should not delete them.

## Validation Status

Audit artifacts were generated under:

`_condamad/audits/frontend-react-pages/2026-05-08-0123/`

Application code was not modified. Audit validation was run from an activated `.venv`.
