from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.models.reference import ReferenceVersionModel
from app.infra.db.repositories.prediction_ruleset_repository import PredictionRulesetRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResolvedCalibrationRuntime:
    reference_version: str
    ruleset_version: str


def resolve_project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def resolve_calibration_runtime(
    db: Session,
    *,
    requested_reference_version: str | None = None,
    requested_ruleset_version: str | None = None,
) -> ResolvedCalibrationRuntime:
    ruleset_version = requested_ruleset_version or settings.active_ruleset_version
    requested_reference = requested_reference_version or settings.active_reference_version

    ruleset_repo = PredictionRulesetRepository(db)
    ruleset = ruleset_repo.get_ruleset(ruleset_version)
    if ruleset is None:
        raise ValueError(
            "Prediction ruleset "
            f"{ruleset_version!r} not found in the configured database. "
            "Seed prediction reference data first with "
            "`python scripts/seed_31_prediction_reference_v2.py`."
        )

    linked_reference = db.scalar(
        select(ReferenceVersionModel).where(
            ReferenceVersionModel.id == ruleset.reference_version_id
        )
    )
    if linked_reference is None:
        raise ValueError(
            "Prediction ruleset "
            f"{ruleset_version!r} points to missing reference_version_id "
            f"{ruleset.reference_version_id}."
        )

    requested_reference_model = db.scalar(
        select(ReferenceVersionModel).where(ReferenceVersionModel.version == requested_reference)
    )

    if requested_reference_model is None:
        logger.info(
            "Calibration reference version %s not found; using ruleset-linked reference %s.",
            requested_reference,
            linked_reference.version,
        )
        return ResolvedCalibrationRuntime(
            reference_version=linked_reference.version,
            ruleset_version=ruleset.version,
        )

    if requested_reference_model.id != linked_reference.id:
        logger.info(
            "Calibration reference version %s overridden by ruleset-linked reference %s "
            "for ruleset %s.",
            requested_reference,
            linked_reference.version,
            ruleset.version,
        )
        return ResolvedCalibrationRuntime(
            reference_version=linked_reference.version,
            ruleset_version=ruleset.version,
        )

    return ResolvedCalibrationRuntime(
        reference_version=requested_reference_model.version,
        ruleset_version=ruleset.version,
    )
