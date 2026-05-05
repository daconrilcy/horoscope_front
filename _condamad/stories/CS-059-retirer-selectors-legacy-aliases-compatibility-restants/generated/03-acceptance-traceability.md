# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Baseline et scope auditable. | Artefact before/after story. | Inventaire story + scans cibles. | PASS |
| AC2 | Migration ou suppression conforme au scope. | Fichiers frontend listés dans les preuves. | Guards design-system cibles. | PASS |
| AC3 | Registres/contrats synchronises. | Allowlists ou registres mis a jour si applicables. | Tests de policy Vitest. | PASS |
| AC4 | Blockers explicitement conserves. | Exceptions premium/admin/alias documentees. | Scans cibles et artefacts after. | PASS |
| AC5 | Non-regression et qualite. | Aucun nouveau legacy/fallback/inline non classe. | Tests, lint et scans finaux. | PASS |

Notes: AC1 baseline before/after cree; AC2 selectors chat migrables quittent App.css; AC3 aucun alias retire sans consommateurs; AC4 admin external-active bloque; AC5 registry et guard legacy-style synchronises.
