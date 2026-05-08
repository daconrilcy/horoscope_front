<!-- Baseline CS-091 des appels API admin directs. -->

# CS-091 Before

Date: 2026-05-08

Cluster audite: dashboard, logs, users, user detail.

| Page | Appels directs initiaux |
|---|---:|
| `AdminDashboardPage.tsx` | 3 |
| `AdminLogsPage.tsx` | 6 |
| `AdminUsersPage.tsx` | 1 |
| `AdminUserDetailPage.tsx` | 3 |

Commande baseline: `rg -n "apiFetch\\(" src/pages/admin/AdminDashboardPage.tsx src/pages/admin/AdminLogsPage.tsx src/pages/admin/AdminUsersPage.tsx src/pages/admin/AdminUserDetailPage.tsx`.
