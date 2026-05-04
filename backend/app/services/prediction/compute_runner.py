"""Runner de calcul prediction avec isolation thread/session DB."""

from __future__ import annotations

import concurrent.futures
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.services.prediction.engine_orchestrator import EngineOrchestrator
from app.services.prediction.types import DailyPredictionServiceError

if TYPE_CHECKING:
    from datetime import date

    from sqlalchemy.orm import Session

    from app.core.config import DailyEngineMode
    from app.prediction.schemas import EngineInput, PersistablePredictionBundle
    from app.services.prediction.context_loader import PredictionContextLoader

logger = logging.getLogger()

_COMPUTE_TIMEOUT_SECONDS = 30


@dataclass(frozen=True)
class ComputeResult:
    """Resultat de calcul expose au service de prediction."""

    bundle: PersistablePredictionBundle

    @property
    def engine_output(self):
        """Retourne la projection moteur legacy du bundle persistant."""
        return self.bundle.to_engine_output()


class PredictionComputeRunner:
    """
    Execute le moteur de prediction avec timeout sans partager la session DB.
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
        Execute le moteur avec timeout apres prechargement du contexte DB.

        Le contexte prediction est charge avec la session appelante avant la
        creation du worker. Le thread de calcul recoit ensuite un loader pur
        qui retourne ce contexte precharge; il ne capture donc pas la session
        SQLAlchemy appelante si le timeout laisse le worker survivre.
        """
        loaded_context = self.context_loader.load(
            db,
            engine_input.reference_version,
            engine_input.ruleset_version,
            engine_input.local_date,
        )

        def ctx_loader(ref: str, rule: str, dt: date) -> object:
            expected = (
                engine_input.reference_version,
                engine_input.ruleset_version,
                engine_input.local_date,
            )
            requested = (ref, rule, dt)
            if requested != expected:
                raise DailyPredictionServiceError(
                    "context_mismatch",
                    "Contexte prediction precharge incompatible avec la demande moteur",
                )
            return loaded_context

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

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        future = executor.submit(orchestrator.run, **kwargs)
        try:
            bundle = future.result(timeout=_COMPUTE_TIMEOUT_SECONDS)
            return ComputeResult(bundle=bundle)
        except concurrent.futures.TimeoutError:
            future.cancel()
            raise DailyPredictionServiceError(
                "timeout", "Calcul trop long — service temporairement dégradé"
            ) from None
        finally:
            executor.shutdown(wait=False, cancel_futures=True)
