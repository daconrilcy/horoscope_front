<!-- Baseline avant migration du cluster admin CS-086. -->

# CS-086 Hardcoded Values Before

## Scope

Cluster borne aux fichiers:

- `frontend/src/layouts/AdminLayout.css`
- `frontend/src/pages/admin/AdminAiGenerationsPage.css`
- `frontend/src/pages/admin/AdminContentPage.css`
- `frontend/src/pages/admin/AdminDashboardPage.css`
- `frontend/src/pages/admin/AdminEntitlementsPage.css`
- `frontend/src/pages/admin/AdminLogsPage.css`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/pages/admin/AdminSamplePayloadsAdmin.css`
- `frontend/src/pages/admin/AdminSettingsPage.css`
- `frontend/src/pages/admin/AdminSupportPage.css`
- `frontend/src/pages/admin/AdminUserDetailPage.css`
- `frontend/src/pages/admin/AdminUsersPage.css`
- `frontend/src/pages/admin/PersonasAdmin.css`

## Baseline command

```powershell
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(|font-size:|font-weight:|line-height:|letter-spacing:|box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," frontend/src/layouts/AdminLayout.css frontend/src/pages/admin -g "*.css" --count
```

## Initial counts

| File | Count |
|---|---:|
| `frontend/src/layouts/AdminLayout.css` | 19 |
| `frontend/src/pages/admin/AdminAiGenerationsPage.css` | 12 |
| `frontend/src/pages/admin/AdminContentPage.css` | 8 |
| `frontend/src/pages/admin/AdminDashboardPage.css` | 35 |
| `frontend/src/pages/admin/AdminEntitlementsPage.css` | 34 |
| `frontend/src/pages/admin/AdminLogsPage.css` | 28 |
| `frontend/src/pages/admin/AdminPromptsPage.css` | 180 |
| `frontend/src/pages/admin/AdminSamplePayloadsAdmin.css` | 9 |
| `frontend/src/pages/admin/AdminSettingsPage.css` | 20 |
| `frontend/src/pages/admin/AdminSupportPage.css` | 19 |
| `frontend/src/pages/admin/AdminUserDetailPage.css` | 37 |
| `frontend/src/pages/admin/AdminUsersPage.css` | 17 |
| `frontend/src/pages/admin/PersonasAdmin.css` | 10 |

## Pre-migration observations

- No `var(--token, literal)` fallback was detected in the scoped admin CSS baseline.
- Existing `fallback` hits are selector names in `AdminPromptsPage.css` for prompt graph business concepts; they are not CSS compatibility mechanisms.
- `--admin-settings-*` and `--admin-entitlements-*` already exist as documented admin semantic namespaces.
