# CS-040 CSS fallback contract after

## Result

- Markdown registry rows: 120.
- Executable allowlist entries: 120.
- Active CSS fallback scan count: 117.
- Delta: 0, verified by 
pm run test -- css-fallback inline-style design-system theme-tokens.

## Contract

- Canonical executable owner: rontend/src/tests/design-system-allowlist.ts.
- Documented owner: rontend/src/styles/css-fallback-allowlist.md.
- Parity guard: rontend/src/tests/css-fallback-policy.test.ts compares both contracts as exact multisets and checks status/reason/exit metadata.
