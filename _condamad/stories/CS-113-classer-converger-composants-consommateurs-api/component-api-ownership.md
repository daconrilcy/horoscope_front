<!-- Decisions d'ownership CS-113 pour les composants consommateurs d'API. -->

# CS-113 Component API Ownership

| File | Decision | Owner | Proof | Exit condition |
|---|---|---|---|---|
| `components/AdminGuard.tsx` | keep exact container | admin routing | allowlist + guard | migrer vers guard route-level |
| `components/B2B*.tsx` | keep exact containers | enterprise dashboard | allowlist + guard | migrer sous feature enterprise/b2b |
| `components/B2BReconciliationPanel.tsx` | keep exact container | enterprise dashboard | allowlist + guard | migrer sous feature enterprise/b2b |
| `components/EnterpriseCredentialsPanel.tsx` | keep exact container | enterprise dashboard | allowlist + guard | migrer sous feature enterprise/b2b |
| `components/NatalInterpretation.tsx` | keep narrow container | natal chart page | split + guard | migrer sous feature natal-chart |
| `components/natal-interpretation/NatalInterpretationPersonaSelector.tsx` | keep exact sub-container | natal chart page | allowlist + guard | migrer avec container natal |
| `components/OpsMonitoringPanel.tsx`, `OpsPersonaPanel.tsx`, `SupportOpsPanel.tsx` | keep exact containers | admin operations | allowlist + guard | migrer sous feature admin-ops |
| `components/PrivacyPanel.tsx`, `settings/DeleteAccountModal.tsx` | keep exact containers | settings privacy | allowlist + guard | migrer sous settings/privacy |
| `components/SignInForm.tsx`, `SignUpForm.tsx` | keep exact containers | auth pages | allowlist + guard | migrer sous feature auth |
| `components/dashboard/useDashboardAstroSummary.ts` | keep exact hook | dashboard summary | allowlist + guard | migrer sous dashboard/hooks |
| `components/layout/Header.tsx`, `Sidebar.tsx`, `BottomNav.tsx` | keep exact layout containers | app layout | allowlist + guard | remplacer par props/provider route-level |
| `components/ui/UpgradeCTA/UpgradeCTA.test.tsx` | keep type-only test import | ui tests | allowlist + guard | extraire type neutre si sortie du domaine billing |

Aucune wildcard, exception dossier ou escape hatch n'a ete ajoutee.
