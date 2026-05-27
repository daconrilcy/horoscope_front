# Finding Register - prompt-generation-cartography - 2026-05-27-1800

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-canonical-owner | CS-343 source-map deliverable | E-001, E-004, E-005, E-006, E-010, E-012 | The prompt-generation surface map now separates runtime, configuration, seed, test, audit and historical/debt surfaces for later audits. | Preserve this inventory as baseline for CS-344 to CS-350. | no |
| F-002 | Medium | High | legacy-surface | Prompt-generation debt and archival carriers | E-003, E-010, E-012 | Legacy/debt carriers remain present as classified historical, bootstrap or governance surfaces; later audits must not treat text hits as active prompt ownership. | Route each classified debt or archival carrier to the bounded follow-up audit CS-344 to CS-350 before any runtime refactor. | yes |
| F-003 | Info | High | dependency-direction-violation | LLM prompt-generation dependency direction | E-007, E-008, E-009 | The audited LLM domain/service prompt surfaces keep the API/FastAPI boundary clear under current evidence. | Keep RG-002/RG-022 and architecture tests in follow-up story validation plans. | no |

## F-001 Surface inventory baseline produced

- Severity: Info
- Confidence: High
- Category: missing-canonical-owner
- Domain: CS-343 source-map deliverable
- Evidence: E-001, E-004, E-005, E-006, E-010, E-012
- Expected rule: CS-343 must create a reproducible inventory without changing runtime behavior.
- Actual state: The audit folder contains a surface inventory that classifies priority owners, symbols, statuses and prompt influence boundaries.
- Impact: The prompt-generation surface map now separates runtime, configuration, seed, test, audit and historical/debt surfaces for later audits.
- Recommended action: Preserve this inventory as baseline for CS-344 to CS-350.
- Story candidate: no
- Suggested archetype: no-story

## F-002 Debt and archival carriers require bounded follow-up

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: Prompt-generation debt and archival carriers
- Evidence: E-003, E-010, E-012
- Expected rule: Legacy text, migration backfills, bootstrap cleanup and audit evidence must be classified before they can influence implementation decisions.
- Actual state: `chart_json`, `natal_data`, `evidence`, provider fallback metadata and legacy migration/bootstrap carriers still appear in executable, test, seed and archival scopes, with different roles.
- Impact: Legacy/debt carriers remain present as classified historical, bootstrap or governance surfaces; later audits must not treat text hits as active prompt ownership.
- Recommended action: Route each classified debt or archival carrier to the bounded follow-up audit CS-344 to CS-350 before any runtime refactor.
- Story candidate: yes
- Suggested archetype: legacy-surface-audit

## F-003 Dependency direction remains guarded

- Severity: Info
- Confidence: High
- Category: dependency-direction-violation
- Domain: LLM prompt-generation dependency direction
- Evidence: E-007, E-008, E-009
- Expected rule: Domain and service LLM prompt-generation code must not depend on API/FastAPI types.
- Actual state: Targeted scans returned no API/FastAPI imports in the audited LLM domain/service paths, and targeted architecture tests passed.
- Impact: The audited LLM domain/service prompt surfaces keep the API/FastAPI boundary clear under current evidence.
- Recommended action: Keep RG-002/RG-022 and architecture tests in follow-up story validation plans.
- Story candidate: no
- Suggested archetype: no-story
