"""Contrats purs du contexte charge pour le moteur de prediction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class CalibrationData:
    """Decrit les ancres statistiques utilisees pour calibrer les scores."""

    p05: float | None
    p25: float | None
    p50: float | None
    p75: float | None
    p95: float | None
    sample_size: int | None
    calibration_label: str | None = "provisional"


@dataclass(frozen=True)
class LoadedPredictionContext:
    """Regroupe le contexte reference/ruleset deja charge pour le calcul."""

    prediction_context: Any
    ruleset_context: Any
    calibrations: Mapping[str, Any | None]
    is_provisional_calibration: bool
    calibration_label: str
    language: str = "fr"
