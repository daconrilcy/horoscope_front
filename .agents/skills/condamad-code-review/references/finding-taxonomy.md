<!-- Taxonomie des constats de revue CONDAMAD. -->

# Finding Taxonomy

## Severities

### Critical

Security, data-loss, privilege escalation, destructive migration, or production
outage risk. The story must not be accepted.

### High

Acceptance criterion failure, major regression, active legacy preserved against
story intent, missing authorization, broken integration path, or validation gap
that prevents trust in the implementation.

### Medium

Material edge case, incomplete error handling, partial evidence, maintainability
risk that can realistically cause future defects, or missing targeted test for a
risky path.

### Low

Minor correctness or evidence weakness that should be cleaned up but does not
block acceptance alone.

## Buckets

Use exactly one bucket per finding:

- `patch`: actionable defect with an unambiguous fix.
- `decision_needed`: ambiguous product/architecture decision; cannot be fixed
  safely without user input.
- `defer`: real issue that is pre-existing or outside story scope.
- `dismiss`: false positive or non-actionable noise. Do not include dismissed
  items in final findings except as a count.

## Finding Format

Use this normalized structure internally and in persisted review artifacts:

```md
### CR-<number> <Severity> - <Title>

- Bucket: patch / decision_needed / defer
- Location: `path:line`
- Source layer: diff / acceptance / validation / no-legacy / edge / security
- Evidence: concise proof from diff, story, tests, or search
- Impact: user, system, security, data, or maintainability consequence
- Suggested fix: smallest credible fix
```

## Deduplication Rule

If multiple layers find the same issue, keep one finding with the highest
severity justified by evidence and list merged source layers.

## Dismissal Rule

Dismiss only when there is concrete contrary evidence. "Probably fine" is not a
dismissal reason.

