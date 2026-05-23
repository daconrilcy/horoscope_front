Use when the story changes API routes, config, runtime registration, generated
contracts, persistence behavior, or architecture rules.

- Primary source of truth:
  - <runtime artifact: app.openapi(), AST guard, loaded config, DB schema, route table, generated manifest>
- Secondary evidence:
  - <rg scans, lint, static inspection>
- Static scans alone are not sufficient for this story because:
  - <reason>
