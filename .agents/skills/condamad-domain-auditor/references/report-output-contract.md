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
- Evidence entries must be specific enough to reproduce: command/source,
  repository-relative inspected path, inspected symbol/surface when applicable,
  result, and limitation when relevant.
- Negative evidence must state the searched target and exclusions.
- Every file or bounded surface in the audited inventory must appear in a file
  usage classification section unless the report states that no file-level
  inventory applies to the selected domain.

## Closure Status

`00-audit-report.md` must include a domain closure status:

- `closed`: no implementation story remains for the audited domain;
- `open`: at least one in-domain implementation finding remains;
- `phased-with-map`: multiple bounded implementation slices remain and the
  report provides the complete surface plus stop condition;
- `blocked`: a user, product, or technical decision is required before
  implementation;
- `non-domain`: residual issues belong to another audit domain.

`03-story-candidates.md` must include an `Exhaustive Files To Modify` section
for every open or phased implementation finding. Use explicit `none` entries
when no application or governance/test file remains.

Residual concerns outside the audited domain must be placed in a separate
deferred non-domain section and must not keep the audited domain open.

## File Usage Classification

`00-audit-report.md` must include a `File Usage Classification` section for
audits that inspect files, exports, routes, components, services, test helpers,
or other concrete repository surfaces.

Use a table with these columns:

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|

Rules:

- `Surface` must be a repository-relative file path, optionally followed by a
  symbol, export, route, selector, or contract name.
- `Classification` must be one of `used`, `intentional-public-export`,
  `test-only`, `delete-candidate`, `needs-user-decision`, or `out-of-domain`.
- `Evidence` must reference existing `E-xxx` IDs.
- `delete-candidate` rows must include negative usage evidence and a rationale
  proving the surface is not an intentional public export or test-only owner.
- `intentional-public-export` rows must name the public contract, entrypoint,
  registration, or convention that makes the export intentional.
- `needs-user-decision` rows must state the concrete decision required.
