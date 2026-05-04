<!-- Preuve finale CONDAMAD pour CS-029. -->

# Final Evidence CS-029

Status: done

AC evidence:

- AC1 PASS: existing inline styles are inventoried by `inline-style-policy.test.ts`.
- AC2 PASS: audited static styles were moved from TSX to CSS.
- AC3 PASS: dynamic exceptions are persisted in `inline-style-allowlist.ts`.
- AC4 PASS: the inline-style guard compares every discovered `style=` attribute
  to `frontend/src/tests/design-system-allowlist.ts`.
- AC5 PASS: frontend lint passes.

Validation:

- `npm run test -- inline-style` PASS.
- `npm run test -- design-system` PASS.
- `rg -n "style=" src -g "*.tsx"` run as inventory evidence.
- `npm run lint` PASS.
- venv active: story validate/lint PASS.

Remaining risks: existing inline styles remain only as exact allowlisted
exceptions for future cleanup/migration.
