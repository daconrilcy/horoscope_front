<!-- Audit CS-091 apres centralisation API admin. -->

# CS-091 After

Date: 2026-05-08

Owners canoniques ajoutes:

- `frontend/src/api/adminDashboard.ts`
- `frontend/src/api/adminLogs.ts`
- `frontend/src/api/adminUsers.ts`

Pages migrees:

- `AdminDashboardPage.tsx`
- `AdminLogsPage.tsx`
- `AdminUsersPage.tsx`
- `AdminUserDetailPage.tsx`

Scan apres:

- `rg -n "apiFetch\\(" src/pages/admin/AdminDashboardPage.tsx src/pages/admin/AdminLogsPage.tsx src/pages/admin/AdminUsersPage.tsx src/pages/admin/AdminUserDetailPage.tsx`: zero hit.
