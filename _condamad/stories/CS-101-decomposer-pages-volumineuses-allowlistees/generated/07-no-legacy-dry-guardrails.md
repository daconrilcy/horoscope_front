<!-- Garde-fous No Legacy et DRY CS-101. -->

# CS-101 No Legacy / DRY Guardrails

Forbidden:

- wildcard or folder-wide `PAGE_SIZE_EXCEPTIONS`;
- `maxLines` increases;
- temporary exceptions outside AdminPrompts;
- duplicate active rendering of extracted sections in both page and owner;
- compatibility wrappers, aliases, re-exports, or silent fallbacks;
- backend changes.

Required evidence:

- before/after line-count inventory;
- allowlist diff proving closed target entries removed;
- `npm run test -- page-architecture`;
- targeted page tests;
- static scans for inline styles, direct HTTP, `any`, and legacy vocabulary in touched files.
