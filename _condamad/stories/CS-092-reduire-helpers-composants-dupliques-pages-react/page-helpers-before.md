<!-- Baseline CS-092 des helpers dupliques. -->

# CS-092 Before

Date: 2026-05-08

Cluster choisi: decision support pour erreurs API 5xx.

| Helper | Copies initiales |
|---|---|
| `shouldLogSupportForApiError` | `BirthProfilePage.tsx`, `NatalChartPage.tsx` |

Commande baseline: `rg -n "shouldLogSupportForApiError\\(" src/pages/BirthProfilePage.tsx src/pages/NatalChartPage.tsx`.
