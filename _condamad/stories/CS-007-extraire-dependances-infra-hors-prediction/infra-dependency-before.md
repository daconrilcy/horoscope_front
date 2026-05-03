# Infra dependency baseline before CS-007

Command:

```powershell
rg -n "sqlalchemy|Session|DailyPredictionRepository|PredictionReferenceRepository|PredictionRulesetRepository|from app\\.infra" backend/app/prediction -g "*.py"
```

Result before implementation:

```text
backend/app/prediction\calibrator.py:4:from app.infra.db.repositories.prediction_schemas import CalibrationData
backend/app/prediction\context_loader.py:6:from sqlalchemy import select
backend/app/prediction\context_loader.py:7:from sqlalchemy.orm import Session
backend/app/prediction\context_loader.py:10:from app.infra.db.models.reference import ReferenceVersionModel
backend/app/prediction\context_loader.py:11:from app.infra.db.repositories.prediction_reference_repository import PredictionReferenceRepository
backend/app/prediction\context_loader.py:12:from app.infra.db.repositories.prediction_ruleset_repository import PredictionRulesetRepository
backend/app/prediction\context_loader.py:13:from app.infra.db.repositories.prediction_schemas import (
backend/app/prediction\context_loader.py:51:        db: Session,
backend/app/prediction\context_loader.py:83:        ref_repo = PredictionReferenceRepository(db)
backend/app/prediction\context_loader.py:84:        ruleset_repo = PredictionRulesetRepository(db)
backend/app/prediction\context_loader.py:183:        ref_repo: PredictionReferenceRepository,
backend/app/prediction\public_projection.py:10:from sqlalchemy.orm import Session
backend/app/prediction\public_projection.py:78:        db: Session | None = None,
backend/app/prediction\persistence_service.py:8:from sqlalchemy import delete as sa_delete
backend/app/prediction\persistence_service.py:9:from sqlalchemy.exc import IntegrityError
backend/app/prediction\persistence_service.py:10:from sqlalchemy.orm import Session
backend/app/prediction\persistence_service.py:12:from app.infra.db.models.daily_prediction import (
backend/app/prediction\persistence_service.py:18:from app.infra.db.repositories.daily_prediction_repository import DailyPredictionRepository
backend/app/prediction\persistence_service.py:19:from app.infra.db.repositories.prediction_reference_repository import PredictionReferenceRepository
backend/app/prediction\persistence_service.py:51:        db: Session | None = None,
backend/app/prediction\persistence_service.py:90:        repo = DailyPredictionRepository(db)
backend/app/prediction\persistence_service.py:193:        db: Session,
backend/app/prediction\persistence_service.py:197:        ref_repo = PredictionReferenceRepository(db)
backend/app/prediction\persistence_service.py:266:        db: Session,
backend/app/prediction\persistence_service.py:323:        db: Session,
```

Classification:

- `context_loader.py`: active legacy target for migration in CS-007.
- `persistence_service.py`: active legacy target for migration in CS-007.
- `public_projection.py`: not a target of CS-007; covered by CS-009/RG-029.
- `calibrator.py`: not a target of CS-007; candidate for later classification under namespace growth/legacy stories.
