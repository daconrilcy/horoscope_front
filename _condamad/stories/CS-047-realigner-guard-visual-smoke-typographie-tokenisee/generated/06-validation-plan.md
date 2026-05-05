<!-- Plan de validation CS-047. -->

# CS-047 Validation Plan

| Command | Purpose | Expected | Mandatory |
|---|---|---|---|
| `npm run test -- visual-smoke css-fallback design-system inline-style theme-tokens legacy-style` | guards cibles | PASS | yes |
| `npm run test` | regression Vitest complete | PASS | yes |
| `npm run lint` | type/lint frontend | PASS | yes |
| `npm run build` | build frontend | PASS | yes |
| `rg -n "18px\|12px\|font-weight.*500" src/tests/visual-smoke.test.tsx` | negative scan | zero-hit | yes |

