<!-- Inventaire avant CS-113 des composants consommateurs d'API ou de feature. -->

# CS-113 Component API Imports Before

Commande:

```powershell
rg -n 'apiFetch\(|\bfetch\(|axios|from [''\"].*(api|features)' frontend/src/components -g '*.ts' -g '*.tsx'
```

Resultat initial: hits exacts sur `AdminGuard.tsx`, panels B2B/admin/ops, `NatalInterpretation.tsx`, layouts auth, `DeleteAccountModal.tsx`, formulaires auth, hook dashboard, et test `UpgradeCTA`.

Statut: surface `F-001` confirmee avant implementation.
