# Infra dependency scan after CS-007

Command:

```powershell
cd backend
rg -n "sqlalchemy|Session|DailyPredictionRepository|PredictionReferenceRepository|PredictionRulesetRepository|from app\\.infra" app/prediction -g "*.py"
```

Result after implementation:

```text
<zero hit>
```

Classification:

- `context_loader.py`: removed from `app.prediction`; implementation moved to `app.services.prediction.context_loader`.
- `persistence_service.py`: removed from `app.prediction`; implementation moved to `app.services.prediction.persistence_service`.
- `calibrator.py`: the calibration DTO dependency was moved to pure `app.prediction.context`.
- `public_projection.py`: the SQLAlchemy `Session` type dependency was removed from `app.prediction`.

Conclusion:

- The DB loader, persistence, SQLAlchemy and repository dependencies targeted by CS-007 are no longer under `app.prediction`.
- Old import paths `app.prediction.context_loader` and `app.prediction.persistence_service` have no active backend consumers.
