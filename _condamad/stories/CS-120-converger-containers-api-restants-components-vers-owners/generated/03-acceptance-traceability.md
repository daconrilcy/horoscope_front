<!-- Matrice de tracabilite des criteres d'acceptation de CS-120. -->

# Acceptance Traceability - CS-120

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Baseline captures every current E-010 hit before edits. | `component-api-remaining-before.md` lists every story/audit E-010 surface, consumers, tests and canonical target. | Before artifact plus pre-edit targeted `rg` evidence. | Passed |
| AC2 | The seven-batch closure map has one exact final decision per batch. | Old component API owners moved/deleted; `component-api-owner-migration.md` records one decision per batch. | `npm run test -- component-architecture component-usage` PASS; migration map complete. | Passed |
| AC3 | `COMPONENT_API_IMPORT_EXCEPTIONS` is reduced exactly. | `COMPONENT_API_IMPORT_EXCEPTIONS` is empty; no wildcard rows. | `npm run test -- component-architecture component-usage` PASS; stale-row scans zero-hit. | Passed |
| AC4 | Old component import paths are absent. | Consumers and tests import canonical owners; old files deleted without compatibility exports. | Targeted old-path `rg` scans zero-hit. | Passed |
| AC5 | Affected runtime UI remains equivalent. | Route/panel/layout/settings/dashboard imports repointed to canonical owners. | Targeted Vitest suites for B2B, enterprise, support, router, dashboard, settings, layout and UpgradeCTA all PASS. | Passed |
| AC6 | Regression guards for CS-117 to CS-119 pass. | Component architecture guard blocks CS-120 old owners; prior auth/natal/test-only guards remain active. | `npm run test -- component-architecture component-usage` PASS; design-system/visual-smoke PASS. | Passed |
| AC7 | Persistent after evidence proves closure or exact blocker status. | After inventory, owner migration map and final evidence persisted. | Python persistence assertions after venv activation PASS. | Passed |
