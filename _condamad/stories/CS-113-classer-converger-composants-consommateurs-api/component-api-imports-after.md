<!-- Inventaire apres CS-113 des composants consommateurs d'API ou de feature. -->

# CS-113 Component API Imports After

Commande:

```powershell
rg -n 'apiFetch\(|\bfetch\(|axios|from [''\"].*(api|features)' frontend/src/components -g '*.ts' -g '*.tsx'
```

Resultat apres: hits restants exacts et couverts par `frontend/src/tests/component-architecture-allowlist.ts`.

Guard executable:

```powershell
cd frontend
npm run test -- component-architecture components
```

Resultat: PASS, 13 fichiers de tests / 131 tests.
