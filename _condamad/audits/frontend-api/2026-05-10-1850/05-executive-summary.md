# Executive Summary - frontend-api - 2026-05-10-1850

Domain closure status: blocked.

The frontend API layer is functional but not cleanly governed. The highest risk is transport drift: many modules call `fetch` directly and therefore bypass the central `apiFetch` timeout and token-expired cleanup. The second major risk is DRY: error parsing and envelope handling are reimplemented in many modules.

The folder also needs an organization decision. Current files are flat, `index.ts` re-exports most surfaces, and imports from the rest of the app mix `@api`, `@api/<domain>`, and relative paths. This makes it hard to prove which files are runtime-owned and which are test-only or stale public exports.

Findings:

| Severity | Count | Findings |
|---|---:|---|
| Critical | 0 | none |
| High | 2 | F-001, F-002 |
| Medium | 4 | F-003, F-004, F-005, F-006 |
| Low | 0 | none |
| Info | 0 | none |

Story candidates:

| Candidate | Source | Intent |
|---|---|---|
| SC-001 | F-001 | Full closure for transport convergence. |
| SC-002 | F-002 | Phased map for error/envelope centralization. |
| SC-003 | F-003 | Split large API modules into domain subfolders. |
| SC-004 | F-004 | Add import-boundary guard. |
| SC-005 | F-005 | Clarify support versus ops ownership. |
| SC-006 | F-006 | Blocked architecture decision for public API facade. |

Recommended next action: implement SC-004 first because it is small and prevents new import drift, then decide SC-006 before doing larger file moves. SC-001 can proceed independently if geocoding's custom timeout behavior is preserved by the transport convergence.
