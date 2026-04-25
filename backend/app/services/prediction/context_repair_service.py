"""Repare le contexte de prediction sans dependre d un script backend."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from sqlalchemy import select

from app.core.config import settings
from app.core.versions import LEGACY_RULESET_VERSION
from app.infra.db.models.reference import ReferenceVersionModel

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger()


class PredictionContextRepairService:
    """Repare les donnees de contexte manquantes ou verrouillees pour la prediction."""

    def try_repair(
        self,
        db: Session,
        reference_version: str,
        ruleset_version: str,
        reference_version_id: int | None = None,
    ) -> bool:
        """Tente une reparation idempotente quand le runtime local l autorise."""
        if settings.app_env in {"production", "prod"}:
            return False

        allowed_reference_versions = {
            settings.active_reference_version,
            LEGACY_RULESET_VERSION,
        }
        allowed_ruleset_versions = {
            settings.active_ruleset_version,
            LEGACY_RULESET_VERSION,
        }
        if reference_version and reference_version not in allowed_reference_versions:
            return False
        if ruleset_version and ruleset_version not in allowed_ruleset_versions:
            return False

        logger.warning(
            "prediction.context_repair_triggered",
            extra={"reference_version": reference_version, "ruleset_version": ruleset_version},
        )

        try:
            if reference_version:
                self._auto_seed_reference_version(db, version=reference_version)
            if ruleset_version:
                self._auto_seed_prediction_ruleset(
                    db,
                    ruleset_version=ruleset_version,
                    expected_reference_version_id=reference_version_id,
                )
            logger.info("prediction.context_repair_success")
            return True
        except Exception as e:
            logger.error("prediction.context_repair_failed", extra={"error": str(e)})
            return False

    def _auto_seed_reference_version(self, db: Session, *, version: str) -> None:
        from app.services.reference_data_service import ReferenceDataService

        if version != LEGACY_RULESET_VERSION:
            ReferenceDataService.seed_reference_version(db, LEGACY_RULESET_VERSION)
        ReferenceDataService.seed_reference_version(db, version)

    def _auto_seed_prediction_ruleset(
        self,
        db: Session,
        *,
        ruleset_version: str,
        expected_reference_version_id: int | None,
    ) -> None:
        from app.services.prediction.reference_seed_service import (
            PredictionReferenceSeedAbortError,
            run_prediction_reference_seed,
        )

        try:
            run_prediction_reference_seed(db)
            db.commit()
            return
        except PredictionReferenceSeedAbortError as exc:
            db.rollback()
            if not self._repair_locked_incomplete_reference_version(
                db,
                expected_reference_version_id=expected_reference_version_id,
                error_text=str(exc),
            ):
                raise

        try:
            run_prediction_reference_seed(db)
            db.commit()
        except PredictionReferenceSeedAbortError:
            db.rollback()
            raise

    def _repair_locked_incomplete_reference_version(
        self,
        db: Session,
        *,
        expected_reference_version_id: int | None,
        error_text: str,
    ) -> bool:
        if "LOCKED but is incomplete" not in error_text:
            return False

        version_model = None
        if expected_reference_version_id is not None:
            version_model = db.get(ReferenceVersionModel, expected_reference_version_id)
        if version_model is None:
            version_model = db.scalar(
                select(ReferenceVersionModel).where(
                    ReferenceVersionModel.version == settings.active_reference_version
                )
            )
        if version_model is None or not version_model.is_locked:
            return False

        logger.warning(
            "prediction.ruleset_autoseed_repair",
            extra={
                "reference_version": version_model.version,
                "reference_version_id": version_model.id,
            },
        )
        version_model.is_locked = False
        db.commit()
        return True
