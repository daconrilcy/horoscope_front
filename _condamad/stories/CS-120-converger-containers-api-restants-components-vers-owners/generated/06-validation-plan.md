<!-- Plan de validation CONDAMAD pour CS-120. -->

# Validation Plan - CS-120

Run from `frontend/` unless the command explicitly says repository root.

| Command | Purpose | Expected success condition | Required |
|---|---|---|---|
| `npm run test -- component-architecture component-usage` | Guard API-free components boundary, stale exceptions and CS-117/CS-119 regressions. | Vitest exits 0. | yes |
| `npm run test -- B2BReconciliationPanel EnterpriseCredentialsPanel SupportOpsPanel UpgradeCTA` | Preserve moved panel and UI test behavior. | Vitest exits 0. | yes |
| `npm run test -- router DashboardPage SettingsPage BottomNavPremium` | Preserve route, dashboard, settings and mobile nav behavior. | Vitest exits 0. | yes |
| `npm run test -- Header Sidebar AppShell` | Preserve layout behavior after owner convergence. | Vitest exits 0. | yes |
| `npm run test -- design-system visual-smoke` | Keep touched component/UI style guardrails green. | Vitest exits 0. | yes |
| `npm run lint` | Validate TypeScript module graph and lint config. | Command exits 0. | yes |
| Targeted `rg` old-path scans from story section 21 | Prove old imports and stale allowlist rows are absent. | Exit 1 means zero hits and is PASS. | yes |
| Repository root Python persistence assertions after activating `.venv` | Prove required evidence files exist. | Each assertion exits 0. | yes |

If a command cannot run, record exact command, reason, risk and fallback
evidence in `generated/10-final-evidence.md`.
