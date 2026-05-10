<!-- Scan initial des imports @api internes au domaine API avant CS-134. -->

# CS-134 - Imports @api internes before

Commande executee depuis `frontend`:

```powershell
rg -n 'from [''"]@api' src/api -g "*.ts" -g "*.tsx"
```

## Hits initiaux

| Fichier | Ligne | Import interdit |
|---|---:|---|
| `src/api/useDailyPrediction.ts` | 3 | `import { ApiError } from "@api";` |

## Regle attendue

Aucun fichier sous `frontend/src/api` ne doit importer le barrel public `@api`.
