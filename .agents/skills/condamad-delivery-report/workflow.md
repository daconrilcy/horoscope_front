# CONDAMAD Delivery Report Workflow

## Goal

Produce a concise, evidence-based closure report for one story or a coherent
story group. Connect trigger, story scope/ACs, changes, validation/review
evidence, provenance, deviations, residual risks, next actions, and final
status. Do not rewrite story scope, ACs, source findings, or review verdicts.

## Source Precedence

1. Current user instruction for target/output.
2. Provided source documents or reports.
3. Story `00-story.md` and explicit ACs.
4. Capsule generated files and final evidence.
5. Review artifacts and validation logs.
6. Repository diff, file contents, tests, docs.
7. Clearly labeled inference.

## Inputs

Accept story capsules, story keys/ranges, initiative names, branches, commit
ranges, diffs, source documents, test logs, CI output, or review artifacts.

For each capsule, prefer only the files needed for the report:

```text
00-story.md
generated/03-acceptance-traceability.md
generated/04-target-files.md
generated/06-validation-plan.md
generated/07-no-legacy-dry-guardrails.md
generated/10-final-evidence.md
generated/11-code-review.md
```

Use optional files only when the required set is insufficient:

```text
generated/01-execution-brief.md
generated/02-context-map.md
generated/05-implementation-plan.md
generated/09-dev-log.md
_condamad/stories/story-status.md
_condamad/stories/regression-guardrails.md
```

## Search Discipline

Keep selection commands narrow:

- Start from named story directories, target-file lists, changed files, or known
  symbols/tests.
- Prefer `rg --files <capsule-or-target-dir>` and `rg "<symbol|AC|story-key>"
  <narrow paths>` before repository-wide search.
- Avoid broad `rg` over the repo unless no capsule, diff, target file, or source
  document identifies the evidence location.
- When broad search is unavoidable, include a specific pattern and exclude noisy
  build/vendor/cache outputs; do not exclude named CONDAMAD capsule `generated/`
  evidence.

## Statuses

Delivery status values, per story and initiative:

- `Delivered`
- `Partially delivered`
- `Implemented but not validated`
- `Not evidenced`
- `Out of scope`
- `Requires business/QA validation`

Rules:

- `Delivered`: implementation evidence exists; required validation is `PASS` or
  explicitly external; no blocking unresolved required review finding.
- `Partially delivered`: required outcomes are mixed between delivered and
  missing/incomplete/not evidenced.
- `Implemented but not validated`: implementation evidence exists, but
  validation is missing, skipped, failed, not run, unverifiable, or too weak.
- `Not evidenced`: implementation or validation cannot be proven.
- `Out of scope`: explicit story/decision/implementation exclusion.
- `Requires business/QA validation`: repository evidence is complete, but
  acceptance depends on external QA, data, production, legal, user, or business
  confirmation.

For initiative status, choose the most restrictive applicable status:
`Not evidenced` / `Implemented but not validated`, then `Partially delivered`,
then `Requires business/QA validation`, then `Delivered`.

Validation result values:

- `PASS`
- `FAIL`
- `SKIPPED`
- `NOT RUN`
- `EXTERNALLY REQUIRED`

Use `EXTERNALLY REQUIRED` only when validation cannot be completed from the repo
or available logs.

Validation scope values: `targeted`, `full suite`, `manual`, `external`.

## Evidence Rule

Every meaningful claim needs at least one anchor: path, symbol, command/test,
validation result, review finding, AC, diff/range, changed file, log, or source
document section. If no anchor exists, put the claim in `Evidence gaps`.

Do not infer completion from file existence alone; explain what each path or
symbol proves.

## Workflow Steps

1. `steps/step-01-scope-and-sources.md`
2. `steps/step-02-evidence-collection.md`
3. `steps/step-03-traceability-matrix.md`
4. `steps/step-04-report-and-status.md`

## Output Locations

Default story-local report:

```text
_condamad/stories/<story-key>/generated/12-delivery-report.md
```

Default consolidated report:

```text
_condamad/reports/<initiative-or-story-range>-delivery-report.md
```

For multi-story initiatives, write the consolidated report. Add story-local
reports only when useful and not duplicative.

If the canonical path already exists, replace it only for an explicitly
refreshed current report. Otherwise write:

```text
<canonical-stem>-YYYYMMDD-HHMMSS.md
```

## Required Structure

Use `references/report-template.md`:

```md
# Delivery Report - <initiative or story range>

## 0. Report metadata
## 1. Executive summary
## 2. Initial context and trigger
## 3. Story scope
## 4. Implementation summary
## 5. Traceability matrix
## 6. Evidence of completion
## 7. Validation results
## 8. Deviations, limits and assumptions
## 9. Residual risks
## 10. Evidence gaps
## 11. Recommended next actions
## 12. Final delivery status
```

## Quality Bar

Complete reports must identify provenance, missing provenance, story statuses,
AC/outcome traceability, validation scope/results, source-trigger closure,
residual risks, evidence gaps, and concrete next actions derived from gaps,
risks, or deferred scope.

## Final Response

Keep chat short: report path, covered story keys/initiative, final status,
material validation/evidence gaps, and highest-priority next action.
