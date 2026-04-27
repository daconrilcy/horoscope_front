# Report Output Contract

## Required files

- `00-audit-report.md`
- `01-evidence-log.md`
- `02-finding-register.md`
- `03-story-candidates.md`
- `04-risk-matrix.md`
- `05-executive-summary.md`

## Finding register columns

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|

## Rules

- Finding IDs are unique.
- Evidence IDs are unique.
- Story candidate IDs are unique.
- Severity is mandatory.
- Confidence is mandatory.
- Severity values are `Critical`, `High`, `Medium`, `Low`, or `Info`.
- Confidence values are `High`, `Medium`, or `Low`.
- Story candidate values are `yes`, `no`, or `needs-user-decision`.
- Evidence result values are `PASS`, `FAIL`, `SKIPPED`, or `LIMITATION`.
- Evidence is mandatory for every finding.
- Every finding evidence cell must reference at least one existing `E-xxx` evidence ID.
- Finding detail evidence must include the same evidence IDs used by the finding table row.
- High or Critical findings require a recommended action or `needs-user-decision`.
- `Story candidate` equal to `yes` requires a matching entry in `03-story-candidates.md`.
- Story candidates must reference existing findings whose `Story candidate` value is `yes`.
- Risk matrix rows must reference known findings, and every finding must appear in the risk matrix.
- Evidence log must contain at least one command/source or an explicit limitation.
