# Inventaire avant implementation CS-016

Date locale: 2026-05-04.

## Constat du worktree initial

Le worktree au démarrage de CS-016 contenait déjà la migration physique du namespace `backend/app/prediction`: le dossier legacy n'existe plus. L'inventaire sert donc de baseline observée avant le patch CS-016, pas de reproduction de l'audit historique.

## Owners présents

| Surface | Etat observe |
|---|---|
| `backend/app/domain/prediction/persisted_snapshot.py` | Présent, owner canonique de `PersistedPredictionSnapshot` et DTO associés. |
| `backend/app/domain/prediction/persisted_relative_score.py` | Présent, owner canonique de `PersistedRelativeScore`. |
| `backend/app/domain/prediction/persisted_baseline.py` | Présent, owner canonique de `PersistedUserBaseline` et `V3Granularity`. |
| `backend/app/domain/prediction/context.py` | Présent, owner canonique de `CalibrationData` et `LoadedPredictionContext`. |
| `backend/app/prediction` | Absent. |

## Import baseline

Commande de référence:

```powershell
rg -n "from app\.(domain\.prediction|prediction)\.(persisted|context)|app\.prediction\.persisted|app\.prediction\.context" backend/app/infra/db/repositories backend/app/services backend/app/tests backend/tests -g "*.py"
```

Résultat observé:

- Imports canoniques `app.domain.prediction.*` présents dans les repositories, services et tests.
- Aucun import actif `app.prediction.persisted_*`.
- Aucun import actif `app.prediction.context`.

## Risque résiduel avant patch

Le guard existant bloquait globalement `app.prediction`, mais ne nommait pas explicitement la règle RG-036 des DTO persisted dans les repositories DB.
