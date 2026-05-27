# Story Candidates - prompt-generation-cartography - 2026-05-27-1800

## SC-001 Classify debt carriers in bounded follow-up audits

- Source finding: F-002
- Suggested story title: Route prompt-generation debt carriers to CS-344 through CS-350
- Suggested archetype: legacy-surface-audit
- Primary domain: backend prompt-generation follow-up audits
- Required contracts: Runtime Source of Truth; Baseline Snapshot; Ownership Routing; Reintroduction Guard; Persistent Evidence
- Draft objective: Use this inventory as the baseline for CS-344, CS-345, CS-346, CS-347, CS-348, CS-349 and CS-350 so each later audit resolves only its bounded owner instead of reclassifying all text hits.
- Must include: exact carrier selection from `01-surface-inventory-audit.md`; before/after evidence; no wildcard allowlist; explicit prompt-visible versus validation-only versus audit-only versus runtime-only boundary; No Legacy scan for `chart_json`, `natal_data`, `evidence`, `provider` and fallback wording.
- Validation hints: rerun targeted `rg` scans from E-004, E-010, E-011 and E-012; rerun the targeted pytest command from E-007 for natal input boundaries; verify `git status --short -- backend/app backend/tests backend/migrations frontend/src` before closure.
- Blockers: stop if a later audit needs a product decision to keep a debt carrier as runtime input, or if a surface cannot be classified from source/test evidence.

## Exhaustive Files To Modify

### F-002

- Application files: none for CS-343.
- Governance/test files: none for CS-343.
- Audit/story artifacts: later audits should select from the exact surfaces listed in `01-surface-inventory-audit.md`.
- Stop condition: no follow-up story is needed for CS-343 once this audit folder validates and runtime/test/frontend source roots remain unchanged.

## Deferred Non-Domain Context

- CS-344 owns configuration, assembly, placeholders and prompt registry details.
- CS-345 owns gateway handoff, provider execution and provider fallback classification.
- CS-346 owns natal astrology input sources and mapping completeness.
- CS-347 owns output validation, persistence and observability.
- CS-348 to CS-350 own synthesis, delivery report and Mermaid documentation.
