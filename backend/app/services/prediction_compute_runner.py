from __future__ import annotations

import concurrent.futures
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.prediction.engine_orchestrator import EngineOrchestrator
from app.services.daily_prediction_types import DailyPredictionServiceError

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from datetime import date
    from app.prediction.context_loader import PredictionContextLoader
    from app.prediction.schemas import EngineInput, EngineOutput

logger = logging.getLogger()


@dataclass(frozen=True)
class ComputeResult:
    engine_output: EngineOutput


class PredictionComputeRunner:
    """
    Handles the execution of the prediction engine with timeout management.
    """

    def __init__(
        self,
        context_loader: PredictionContextLoader,
        orchestrator_proto: EngineOrchestrator | None = None,
    ) -> None:
        self.context_loader = context_loader
        self._orchestrator_proto = orchestrator_proto

    def run_with_timeout(self, db: Session, engine_input: EngineInput) -> ComputeResult:
        """
        Executes the engine with a 30s timeout.
        
        ⚠️ GIL Limitation: The compute thread continues in background after timeout.
        The session remains non thread-safe for ~30s after timeout.
        """
        def ctx_loader(ref: str, rule: str, dt: date) -> object:
            return self.context_loader.load(db, ref, rule, dt)

        if self._orchestrator_proto is not None:
            orchestrator = self._orchestrator_proto.with_context_loader(ctx_loader)
        else:
            orchestrator = EngineOrchestrator(prediction_context_loader=ctx_loader)

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                orchestrator.run,
                engine_input,
                include_editorial_text=True,
            )
            try:
                engine_output = future.result(timeout=30)
                return ComputeResult(engine_output=engine_output)
            except concurrent.futures.TimeoutError:
                try:
                    db.expire_all()
                except Exception:
                    pass
                raise DailyPredictionServiceError(
                    "timeout", "Calcul trop long — service temporairement dégradé"
                ) from None
