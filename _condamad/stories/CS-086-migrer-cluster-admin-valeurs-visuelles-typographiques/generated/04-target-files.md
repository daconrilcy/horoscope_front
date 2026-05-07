# Target Files

## Must inspect before implementation

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/audits/frontend-design-system/2026-05-07-1730/00-audit-report.md`
- `_condamad/audits/frontend-design-system/2026-05-07-1730/01-evidence-log.md`
- `_condamad/audits/frontend-design-system/2026-05-07-1730/02-finding-register.md`
- `_condamad/audits/frontend-design-system/2026-05-07-1730/03-story-candidates.md`
- `frontend/package.json`
- `frontend/src/layouts/AdminLayout.css`
- `frontend/src/pages/admin/*.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/premium-theme.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/styles/legacy-style-surface-registry.md`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`
- `frontend/src/tests/inline-style-policy.test.ts`
- `frontend/src/tests/legacy-style-policy.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`

## Required searches before editing

```powershell
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(|font-size:|font-weight:|line-height:|letter-spacing:|box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," frontend/src/layouts/AdminLayout.css frontend/src/pages/admin -g "*.css"
rg -n "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only|PASS with limitation|TODO" frontend/src/layouts/AdminLayout.css frontend/src/pages/admin -g "*.css"
rg -n -- "--settings-|--help-|--chat-|--app-|--landing-" frontend/src/layouts/AdminLayout.css frontend/src/pages/admin -g "*.css"
```

## Likely modified files

- `frontend/src/layouts/AdminLayout.css`
- `frontend/src/pages/admin/*.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/tests/design-system-guards.test.ts`
- `_condamad/stories/CS-086-migrer-cluster-admin-valeurs-visuelles-typographiques/hardcoded-values-before.md`
- `_condamad/stories/CS-086-migrer-cluster-admin-valeurs-visuelles-typographiques/hardcoded-values-after.md`
- `_condamad/stories/CS-086-migrer-cluster-admin-valeurs-visuelles-typographiques/generated/*.md`
- `_condamad/stories/story-status.md`

## Forbidden unless directly justified

- `frontend/package.json`
- `frontend/src/pages/admin/*.tsx`
- `frontend/src/App.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/pages/landing/**`
- `backend/**`
