# Frontend Validation Contract

## Required command discovery

Read `frontend/package.json` before running validation. Prefer exact scripts
when present:

```powershell
pnpm lint
pnpm typecheck
pnpm test
pnpm test:e2e
```

If names differ, run the closest equivalent and report the script name used.
Do not use npm, yarn, or bun unless the repository is not a pnpm project.

## Validation order

Run checks from the frontend root:

1. Targeted tests for changed behavior.
2. Applicable guards from `_condamad/stories/regression-guardrails.md`.
3. `pnpm lint`.
4. `pnpm typecheck`.
5. `pnpm test`.
6. `pnpm test:e2e` for changed user flows or when required by the task.
7. Local app startup when the task changes runtime integration or UI behavior.

If the local app starts a long-running dev server, keep it running only when
the user needs a URL or when browser validation is required.

## Regression guardrail evidence

Before completing a frontend task, read
`_condamad/stories/regression-guardrails.md` and identify applicable rows.

For each applicable row, record:

- `RG-XXX` ID;
- why it applies;
- exact guard command, scan, snapshot, or audit expected by the registry;
- result: `PASS`, `FAIL`, `FIXED_AFTER_FAIL`, `NOT_RUN`, or `BLOCKED`;
- allowed differences, if any.

When the task creates a durable frontend invariant, add a new registry row
using the next `RG-XXX` ID. Good frontend invariants include:

- canonical design-token ownership;
- prohibited hardcoded visual values after migration;
- typographic role ownership;
- inline-style allowlist boundaries;
- CSS fallback allowlist boundaries;
- legacy style surface ownership;
- design-system anti-drift guards;
- route ownership or feature ownership rules;
- central HTTP client boundaries;
- critical E2E flow guards.

Do not add registry rows for one-off implementation details that are not meant
to be protected across future stories.

## Test expectations

Use Vitest + Testing Library for:

- rendering states;
- user interactions;
- form validation;
- query hook consumers with mocked data;
- error and empty states;
- accessibility-relevant labels and roles.

Use Playwright for:

- login and auth flows;
- navigation across pages;
- dashboard or settings critical flows;
- regressions involving routing, layout, dialogs, or real browser behavior.

## Static guard checks

Use targeted searches after implementation when relevant:

```powershell
rg "fetch\\(|axios\\." frontend/src
rg "\\bany\\b" frontend/src
rg "style=\\{\\{" frontend/src
rg "zustand|from ['\\\"]zustand|createStore|create\\(" frontend/src/stores frontend/src/features
rg "from ['\\\"]\\.\\./\\.\\./features|from ['\\\"]@/features" frontend/src/features
rg "queryKey:" frontend/src
rg "data\\.ts|utils\\.ts|helpers\\.ts|misc\\.ts" frontend/src/features
rg --files frontend/src | rg "index\\.ts$"
```

Interpret results with judgment:

- Direct HTTP calls outside the central client are findings unless explicitly
  justified.
- `any` in generated or third-party adapter code may be acceptable only with a
  boundary comment.
- Inline styles are forbidden unless unavoidable and documented.
- Zustand/store scan results are heuristic. Zustand usage must be justified by
  cross-page client state; unrelated `create(` hits are not findings.
- Inspect modified `src/components/ui` files manually. Findings include
  business props, API calls, feature-specific text, app-specific state,
  TanStack Query usage, or feature imports.
- Cross-feature imports must be justified or replaced by shared code in
  `components/common`, `lib`, or `hooks`.
- Query keys must be stable structured arrays without duplicate shapes for the
  same resource.
- Generic feature-local filenames must be justified by a narrow responsibility
  or renamed to a domain-specific convention.
- Barrel files must follow the repository's existing convention and must not
  create circular imports or ambiguous ownership.

## Evidence classification

Report each validation as:

- `PASS`: command completed successfully.
- `FAIL`: command failed and remains unresolved.
- `FIXED_AFTER_FAIL`: command failed, code was changed, then passed.
- `NOT_RUN`: command was skipped with reason and risk.
- `BLOCKED`: command could not run due to missing dependency, config, secret,
  service, or environment.

Do not classify a skipped E2E suite as passing.

Do not claim validation passed unless the command was actually run and
completed successfully.

## Local startup

When runtime UI behavior changed, run the app locally if feasible:

```powershell
pnpm dev
```

If a port is occupied, use the repository's supported Vite port override or the
next available port. Provide the final URL in the response only when the server
is still running or the user requested it.
