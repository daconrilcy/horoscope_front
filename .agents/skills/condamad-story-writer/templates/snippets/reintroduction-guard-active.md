Use when the story removes, forbids, or converges away from a legacy route,
field, import, module, prefix, OpenAPI path, frontend route, or status.

The implementation must add or update an architecture guard that fails if the
removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- registered router prefixes
- importable Python modules
- frontend route table
- generated OpenAPI paths
- forbidden symbols or states

Required forbidden examples:

- `<removed or forbidden route prefix>`
- `<removed or forbidden import path>`
- `<removed or forbidden frontend route>`
- `<removed or forbidden legacy field>`

Guard evidence:

- Evidence profile: `reintroduction_guard`; `<command or test path>` checks `<forbidden symbol>`.
