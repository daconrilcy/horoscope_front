# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | CS-262 final evidence exists. | `_condamad/stories/CS-262-audit-existing-prompt-version-answer-id-storage/generated/10-final-evidence.md` created. | Python existence check in validation transcript. | PASS |
| AC2 | The six audit files are cited. | Final evidence cites `00-audit-report.md`, `01-evidence-log.md`, `02-finding-register.md`, `03-story-candidates.md`, `04-risk-matrix.md`, `05-executive-summary.md`. | `rg` filename checks in validation transcript. | PASS |
| AC3 | Traceability fields are classified. | Field matrix classifies `answer_id`, `prompt_version`, `provider`, `model`, `full_prompt`, `prompt_ref`, `prompt_payload_snapshot`. | `rg` field scan in validation transcript. | PASS |
| AC4 | Current runtime evidence is used. | Final evidence cites CS-288 model, repository and schema tests. | Targeted pytest commands in validation transcript. | PASS |
| AC5 | CS-288 resolved gaps are separated. | `resolved-by-CS-288` section separates resolved storage/provenance fields. | `rg` scan for `CS-288` and `resolved-by-CS-288`. | PASS |
| AC6 | Open decisions remain explicit. | `full_prompt` and `prompt_payload_snapshot` remain `open-decision` with retention and DPO notes. | `rg` scan for `open-decision`, `retention` and `DPO`. | PASS |
| AC7 | CS-262 tracker status is reconciled. | `_condamad/stories/story-status.md` row for CS-262 moved to `ready-to-review` after final evidence creation. | Python tracker row check in validation transcript. | PASS |
| AC8 | Application source stays unchanged. | No backend app, backend test, frontend source or migration file edited. | Scoped `git status --short -- backend/app backend/tests frontend/src backend/migrations` in validation transcript. | PASS |
| AC9 | Validation evidence is persisted. | `_condamad/stories/CS-262-audit-existing-prompt-version-answer-id-storage/generated/10-final-evidence-validation.txt` created. | Python transcript existence check in validation transcript. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
