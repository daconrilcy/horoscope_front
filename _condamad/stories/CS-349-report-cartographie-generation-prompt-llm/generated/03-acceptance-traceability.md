# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The final report exists. | `_condamad/reports/prompt-generation-cartography/2026-05-27-0000/report-prompt-generation-cartography.md` | Python path check in `validation-output.md` returned PASS. | PASS |
| AC2 | CS-343 through CS-350 are mapped. | `report-prompt-generation-cartography.md` sections 2, 3 and 5; `evidence-sources.md` source inventory. | `rg -n "CS-343\|CS-348\|CS-350" ...` returned PASS. | PASS |
| AC3 | Important claims have anchors. | `evidence-sources.md` matrix uses `Story`, `Artifact`, `Claim`, `Evidence path`, `Gap`, `Validation evidence`, `Next action`. | `rg -n "Evidence path\|Source\|Evidence gap" ...` returned PASS. | PASS |
| AC4 | Missing proof is labeled. | CS-350 documentation absence, no real provider call and bounded semantic guard are labeled `Evidence gap`. | `rg -n "Evidence gap" ...` returned PASS. | PASS |
| AC5 | Contradictions are visible. | `report-prompt-generation-cartography.md` section `Gaps ou contradictions` names output schema ownership split and audit-correctness distinction. | `rg -n "contradiction\|Gaps" ...` returned PASS. | PASS |
| AC6 | Validation evidence is included. | `validation-output.md` records commands and skipped checks; report section 7 summarizes validation. | `rg -n "Validation evidence\|validation" ...` returned PASS. | PASS |
| AC7 | Residual risks are included. | `report-prompt-generation-cartography.md` section `Risques residuels`. | `rg -n "residual risk\|Risques residuels" ...` returned PASS. | PASS |
| AC8 | Application code remains unchanged. | CS-349 edits are limited to `_condamad/reports/**`, CS-349 generated evidence and `story-status.md`. | `git status --short -- backend/app backend/tests frontend/src` returned no entries. | PASS |
| AC9 | Source evidence is persisted. | `evidence-sources.md` and `validation-output.md` exist under the report folder. | Python path check in `validation-output.md` returned PASS. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
