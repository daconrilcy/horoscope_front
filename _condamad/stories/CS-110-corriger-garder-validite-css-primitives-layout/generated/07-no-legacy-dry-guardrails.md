<!-- Guardrails No Legacy et DRY appliques a CS-110. -->

# No Legacy / DRY Guardrails CS-110

## Forbidden

- `padding: var(--layout-page-padding));`
- layout CSS parse-failure allowlist
- new spacing token replacing `--layout-page-padding`
- broad design-system exception

## Canonical owners

- Layout page spacing: `frontend/src/styles/design-tokens.css` token `--layout-page-padding`
- CSS validity guard: `frontend/src/tests/design-system-guards.test.ts`

## Evidence

| Pattern | Classification | Status |
|---|---|---|
| malformed padding declaration | active legacy removed | PASS |
| layout CSS syntax failures | guarded by design-system test | PASS |
