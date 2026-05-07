# Target Files

## Must read

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `frontend/package.json`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`
- `frontend/src/tests/inline-style-policy.test.ts`
- `frontend/src/tests/legacy-style-policy.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`

## Must search

- `rg -n "subscription|subscriptions|help" frontend/src/pages/HelpPage.css`
- `rg -n "HelpPage|help|subscription|subscriptions" frontend/src/tests/design-system-guards.test.ts`
- `rg -n "help/subscriptions|subscription-plan-card" frontend/src`

## Likely modified

- `frontend/src/pages/HelpPage.css`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/tests/design-system-guards.test.ts`
- `_condamad/stories/CS-088-migrer-surface-subscriptions-helppage-tokens-help/hardcoded-values-before.md`
- `_condamad/stories/CS-088-migrer-surface-subscriptions-helppage-tokens-help/hardcoded-values-after.md`
- `_condamad/stories/CS-088-migrer-surface-subscriptions-helppage-tokens-help/generated/10-final-evidence.md`
- `_condamad/stories/story-status.md`

## Forbidden unless justified

- `frontend/src/pages/HelpPage.tsx`
- `frontend/src/app/**`
- `frontend/package.json`
- `backend/**`
