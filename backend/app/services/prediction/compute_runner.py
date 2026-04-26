from __future__ import annotations

import concurrent.futures
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.prediction.engine_orchestrator import EngineOrchestrator
from app.services.prediction.types import DailyPredictionServiceError

if TYPE_CHECKING:
    from datetime import date

    from sqlalchemy.orm import Session

    from app.core.config import DailyEngineMode
    from app.prediction.context_loader import PredictionContextLoader
    from app.prediction.schemas import EngineInput, PersistablePredictionBundle

logger = logging.getLogger()


@dataclass(frozen=True)
class ComputeResult:
    bundle: PersistablePredictionBundle

    @property
    def engine_output(self):
        return self.bundle.to_engine_output()


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

    def run_with_timeout(
        self,
        db: Session,
        engine_input: EngineInput,
        *,
        engine_mode: DailyEngineMode | None = None,
    ) -> ComputeResult:
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

        kwargs = {
            "engine_input": engine_input,
            "include_editorial_text": True,
        }
        if engine_mode is not None:
            kwargs["engine_mode"] = engine_mode

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(orchestrator.run, **kwargs)
            try:
                bundle = future.result(timeout=30)
                return ComputeResult(bundle=bundle)
            except concurrent.futures.TimeoutError:
                try:
                    db.expire_all()
                except Exception:
                    pass
                raise DailyPredictionServiceError(
                    "timeout", "Calcul trop long — service temporairement dégradé"
                ) from None
