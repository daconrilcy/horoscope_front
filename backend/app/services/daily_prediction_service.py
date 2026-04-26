"""Facade publique minimale du service de prediction quotidienne."""

from app.services.prediction.types import ComputeMode, DailyPredictionServiceError
from app.services.prediction.service import DailyPredictionService, ServiceResult

__all__ = [
    "ComputeMode",
    "DailyPredictionService",
    "DailyPredictionServiceError",
    "ServiceResult",
]
