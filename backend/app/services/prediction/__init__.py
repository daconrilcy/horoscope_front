"""Package canonique des services de prediction quotidienne."""

from app.services.prediction.relative_scoring_service import RelativeScoringService
from app.services.prediction.service import DailyPredictionService, ServiceResult
from app.services.prediction.types import ComputeMode, DailyPredictionServiceError

__all__ = [
    "ComputeMode",
    "DailyPredictionService",
    "DailyPredictionServiceError",
    "RelativeScoringService",
    "ServiceResult",
]
