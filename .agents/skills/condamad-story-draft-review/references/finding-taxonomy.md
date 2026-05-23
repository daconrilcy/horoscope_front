<!-- Taxonomie des constats de revue CONDAMAD. -->

# Finding Taxonomy

## Severities

### Critical

Story contract defect that would make implementation unsafe, destructive,
ambiguous, or impossible to validate. The story must not be accepted.

### High

Acceptance criterion failure, missing or invalid validation evidence, active
legacy allowed against story intent, broken scope boundary, or review artifact
drift that prevents trust in the story contract.

### Medium

Material story ambiguity, partial evidence, incomplete non-goals, guardrail gap,
or missing targeted test expectation for a risky path.

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
- Source layer: source / acceptance / validation / no-legacy / guardrail / artifact
- Evidence: concise proof from story text, validator output, strict lint, or source brief
- Impact: implementation-readiness, validation, scope, or reviewability consequence
- Suggested fix: smallest credible story-artifact fix
```

## Deduplication Rule

If multiple layers find the same issue, keep one finding with the highest
severity justified by evidence and list merged source layers.

## Dismissal Rule

Dismiss only when there is concrete contrary evidence. "Probably fine" is not a
dismissal reason.
