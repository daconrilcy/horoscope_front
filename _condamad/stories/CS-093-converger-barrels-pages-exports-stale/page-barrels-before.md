<!-- Baseline CS-093 des barrels pages. -->

# CS-093 Before

Date: 2026-05-08

| Barrel | Etat initial |
|---|---|
| `frontend/src/pages/admin/index.ts` | Exports stale `PricingAdmin`, `MonitoringAdmin`; exports dupliques `AdminUsersPage`, `AdminSupportPage`, `AdminAiGenerationsPage`, `AdminLogsPage`. |
| `frontend/src/pages/index.ts` | Exports publics inchanges, non modifies par cette story. |

Commande baseline: `rg -n "export" src/pages`.
