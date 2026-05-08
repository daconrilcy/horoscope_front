# No Legacy / DRY Guardrails - CS-100

## Canonical ownership

- Route entrypoint: `frontend/src/pages/admin/AdminPromptsPage.tsx`.
- Admin prompts feature owner: `frontend/src/features/admin-prompts/**`.
- API contract owner: `frontend/src/api/adminPrompts.ts`.

## Forbidden patterns

- Local duplicate catalogue, consommation ou release section in `AdminPromptsPage.tsx`.
- `apiFetch(` in page or feature UI files.
- `@ts-nocheck` or `@ts-ignore`.
- Compatibility re-export or alias preserving an obsolete section owner.
- Wildcard/folder-wide `PAGE_SIZE_EXCEPTIONS`.

## Required evidence

- Before/after ownership inventories.
- Negative scan for TS/API bypasses.
- Page architecture test.
- Targeted AdminPrompts tests.

## Exceptions

None for the extracted sections.
