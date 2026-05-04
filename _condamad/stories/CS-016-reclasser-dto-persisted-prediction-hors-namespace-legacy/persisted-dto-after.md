# Inventaire apres implementation CS-016

Date locale: 2026-05-04.

## Owners canoniques apres patch

| Surface | Owner canonique | Statut |
|---|---|---|
| Snapshots persisted DB | `app.domain.prediction.persisted_snapshot` | PASS |
| Scores relatifs persisted | `app.domain.prediction.persisted_relative_score` | PASS |
| Baseline utilisateur | `app.domain.prediction.persisted_baseline` | PASS |
| CalibrationData | `app.domain.prediction.context` | PASS |

## Repositories DB

Les repositories DB consomment les DTO persisted depuis `app.domain.prediction`:

- `backend/app/infra/db/repositories/daily_prediction_repository.py`
- `backend/app/infra/db/repositories/user_prediction_baseline_repository.py`
- `backend/app/infra/db/repositories/prediction_schemas.py`

## Preuve anti legacy

Commandes de référence:

```powershell
rg -n "app\.prediction\.persisted|app\.prediction\.context" app/infra/db/repositories -g "*.py"
rg -n "from app\.prediction\.persisted|from app\.prediction\.context" app tests -g "*.py"
```

Résultat attendu et observé: aucun hit actif.

## Guard ajoute

`backend/app/tests/unit/test_daily_prediction_guardrails.py::test_prediction_repositories_do_not_import_legacy_persisted_dtos` bloque les imports suivants depuis `app/infra/db/repositories`:

- `app.prediction.context`
- `app.prediction.persisted_baseline`
- `app.prediction.persisted_relative_score`
- `app.prediction.persisted_snapshot`
