---
name: condamad-delivery-report
description: >
  Generate an evidence-based CONDAMAD delivery closure report after completed
  stories. Use for delivery evidence, release evidence, story completion
  synthesis, initiative reports, or traceability reports linking an initial
  trigger to stories, acceptance criteria, implementation, validation, residual
  risks, and next actions. Optimized for CONDAMAD story capsules and multi-story
  initiatives.
---

# CONDAMAD Delivery Report

Use this skill after implementation/review work to prove:

```text
initial trigger -> stories -> acceptance criteria -> code changes -> validation evidence -> residual risk -> next action
```

Follow `workflow.md` and `references/report-template.md`. Load sibling
contracts when available:

- `../condamad-dev-story/references/condamad-principles.md`
- `../condamad-dev-story/references/validation-contract.md`
- `../condamad-dev-story/references/no-legacy-contract.md`
- `../condamad-code-review/SKILL.md` when review evidence exists or is expected

If a reference is missing, continue and record it as an `Evidence gap`.

## Non-Negotiable Behavior

- Evidence comes before prose; unsupported claims become `Not evidenced`.
- Every meaningful claim needs a concrete anchor: path, symbol, diff, command,
  result, log, AC, source document, or review finding.
- A file path is evidence only when the report states what behavior, contract,
  test, or decision it proves.
- Do not mark skipped validation as passing, soften review findings, or hide
  residual risks in prose.
- Do not edit implementation files while generating a report.
- Use only statuses and validation values from `workflow.md`.
- Prefer one consolidated initiative report for shared triggers; add story-local
  reports only when useful and not duplicative.
- Do not overwrite or soften existing evidence; surface contradictions as gaps,
  deviations, or risks.
