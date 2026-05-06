# Hardcoded values after

| Item | Decision | Proof | Risk |
|---|---|---|---|
| AdminSettings cluster | migrated to `--admin-settings-*` local semantic variables and existing type tokens | `npm run test -- design-system theme-tokens visual-smoke AdminSettingsPage AdminEntitlementsPage AdminUserDetailPage PersonasAdmin` PASS | low |
| AdminEntitlements cluster | migrated to `--admin-entitlements-*` local semantic variables and existing type tokens | same command PASS | low |
| Registry | updated | `token-namespace-registry.md` classifies both local namespaces | low |

No pending marker remains. Remaining literals are variable owner definitions or classified local values, not duplicate consumers.
