# Target Files

## Must Read

- `_condamad/stories/CS-084-migrer-cluster-settings-valeurs-visuelles-typographiques/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `frontend/package.json`
- `frontend/src/pages/settings/Settings.css`
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

## Must Search

- `rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" frontend/src/pages/settings/Settings.css`
- `rg -n "font-size:|font-weight:|line-height:|letter-spacing:" frontend/src/pages/settings/Settings.css`
- `rg -n "box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," frontend/src/pages/settings/Settings.css`
- `rg -n "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only" frontend/src/pages/settings/Settings.css`
- `rg -n -- "--settings-" frontend/src --glob "*.css"`

## Likely Modified

- `frontend/src/pages/settings/Settings.css`
- `frontend/src/tests/design-system-guards.test.ts`
- `_condamad/stories/CS-084-migrer-cluster-settings-valeurs-visuelles-typographiques/hardcoded-values-before.md`
- `_condamad/stories/CS-084-migrer-cluster-settings-valeurs-visuelles-typographiques/hardcoded-values-after.md`
- `_condamad/stories/CS-084-migrer-cluster-settings-valeurs-visuelles-typographiques/generated/*`
- `_condamad/stories/story-status.md`

## Conditional

- `frontend/src/styles/token-namespace-registry.md` seulement si un owner durable change.
- `frontend/src/styles/typography-roles.md` seulement si un role durable manque.
- `frontend/src/styles/css-fallback-allowlist.md` seulement si l'exception `--usage-progress` change.

## Forbidden Unless Directly Justified

- `frontend/src/App.css`
- `frontend/src/pages/settings/Settings.tsx`
- `backend/**`
- `frontend/package.json`
- tout fichier hors cluster non requis par les guards.
