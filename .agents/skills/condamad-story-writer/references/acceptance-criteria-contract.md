# Acceptance Criteria Contract

<!-- Contrat de criteres d'acceptation verifiables pour CONDAMAD. -->

## Required Format

Acceptance criteria must be a markdown table:

```md
| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | ... | test / guard / grep / command |
```

`Verification` is also accepted as the evidence column name.

## Rules

- AC identifiers must be sequential: `AC1`, `AC2`, `AC3`.
- Every AC must describe observable behavior or architecture state.
- Every AC must include validation evidence.
- Do not use subjective requirements like "clean", "better", or "improved"
  without a measurable test or command.
- Do not put implementation tasks inside ACs. ACs describe what must be true,
  not every step to get there.

## Strong Evidence Examples

Good validation evidence includes:

- targeted pytest or Vitest command;
- architecture guard test;
- negative `rg` scan proving an import or symbol is gone;
- lint/type check command;
- concrete test path;
- documented manual check with a precise expected result.

Weak evidence includes:

- "review manually" without target;
- "works";
- "as needed";
- "covered by tests" without naming tests or commands.

Manual evidence must be structured:

```md
Manual check: open `/admin/prompts`, select feature/subscription/locale, verify only active canonical prompts appear.
```
