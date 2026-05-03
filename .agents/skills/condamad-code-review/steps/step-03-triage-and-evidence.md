<!-- Etape de normalisation, dedoublonnage et preuve des constats. -->

# Step 3 - Triage and Evidence

## Objective

Turn raw adversarial observations into a short list of actionable findings.

## Actions

1. Normalize findings using the taxonomy in
   `references/finding-taxonomy.md`.
2. Deduplicate overlapping findings.
3. Verify each remaining finding against repository evidence.
4. Assign one severity: Critical, High, Medium, or Low.
5. Assign one bucket: `patch`, `decision_needed`, `defer`, or `dismiss`.
6. Drop dismissed findings from final output, but keep a dismissal count.
7. For deferred findings, explain why they are outside current story scope.
8. For `decision_needed`, state the exact decision required.
9. For `patch`, state the smallest credible fix.
10. Determine final verdict:
    - `BLOCKING` for Critical issue, High AC failure, security/data risk,
      active forbidden legacy, false validation claim, or missing validation
      evidence required by the story or definition of done;
    - `CHANGES_REQUESTED` for material patch findings;
    - `ACCEPTABLE_WITH_LIMITATIONS` when no required patch remains, but optional
      or full-regression validation could not be run and residual risk is
      documented;
    - `CLEAN` only when no actionable issue remains and False CLEAN Prevention
      conditions do not apply.

## Evidence Requirements

Every non-dismissed finding must include:

- file and line when possible;
- evidence from diff, story, tests, command output, or search;
- impact;
- suggested fix or decision required.

If exact line numbers are unavailable, cite the narrowest function/class/file
and say why a precise line was not available.

## Persisted Review

If a CONDAMAD capsule exists, write or update
`generated/11-code-review.md` with:

- review target;
- inputs reviewed;
- findings;
- commands run by reviewer;
- verdict;
- residual risks.

Replace the full file on each review run. Do not append multiple contradictory
reviews to the same artifact.

If the reviewed story is tracked in `_condamad/stories/story-status.md`, update
the matching registry row after writing the review artifact:

- `done` for an accepted review verdict with required evidence complete;
- `ready-to-review` for `BLOCKING` or `CHANGES_REQUESTED`.

Do not modify implementation files in this step.
