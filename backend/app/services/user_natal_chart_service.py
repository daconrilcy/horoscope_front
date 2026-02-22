"""
Service de gestion des thèmes natals utilisateur.

Ce module gère la génération, la récupération et la vérification de
cohérence des thèmes natals des utilisateurs.
"""

from __future__ import annotations

import json
from datetime import datetime
from time import perf_counter

from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.astrology.natal_calculation import NatalCalculationError, NatalResult
from app.domain.astrology.natal_preparation import BirthInput
from app.infra.db.repositories.chart_result_repository import ChartResultRepository
from app.infra.db.repositories.user_birth_profile_repository import UserBirthProfileRepository
from app.services.chart_result_service import ChartResultService, ChartResultServiceError
from app.services.natal_calculation_service import NatalCalculationService
from app.services.user_birth_profile_service import (
    UserBirthProfileService,
    UserBirthProfileServiceError,
)


class UserNatalChartServiceError(Exception):
    """Exception levée lors d'erreurs de thème natal utilisateur."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        """
        Initialise une erreur de thème natal.

        Args:
            code: Code d'erreur unique.
            message: Message descriptif de l'erreur.
            details: Dictionnaire optionnel de détails supplémentaires.
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class UserNatalChartMetadata(BaseModel):
    """Métadonnées d'un thème natal (versions de référence et règles)."""

    reference_version: str
    ruleset_version: str


class UserNatalChartGenerationData(BaseModel):
    """Données d'un thème natal nouvellement généré."""

    chart_id: str
    result: NatalResult
    metadata: UserNatalChartMetadata


class UserNatalChartReadData(BaseModel):
    """Données d'un thème natal récupéré avec date de création."""

    chart_id: str
    result: NatalResult
    metadata: UserNatalChartMetadata
    created_at: datetime


class UserNatalChartConsistencyData(BaseModel):
    """Résultat de vérification de cohérence entre thèmes."""

    user_id: int
    consistent: bool
    reason: str
    mismatch_code: str | None = None
    latest_chart_id: str
    baseline_chart_id: str
    reference_version: str
    ruleset_version: str
    input_hash: str


class UserNatalChartService:
    """
    Service de gestion des thèmes natals utilisateur.

    Orchestre la génération, la récupération et la vérification de
    cohérence des thèmes natals avec gestion des timeouts.
    """
    @staticmethod
    def _normalize_payload(payload: dict[str, object]) -> str:
        """Normalise un payload pour comparaison déterministe."""
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def _validate_natal_result_payload(payload: dict[str, object], chart_id: str) -> NatalResult:
        """Valide et parse un payload de résultat natal."""
        try:
            return NatalResult.model_validate(payload)
        except ValidationError as error:
            raise UserNatalChartServiceError(
                code="invalid_chart_result_payload",
                message="stored chart payload is invalid",
                details={"chart_id": chart_id},
            ) from error

    @staticmethod
    def _claim_latest_legacy_chart_for_user(
        db: Session,
        user_id: int,
        birth_input: BirthInput,
    ) -> None:
        """Associe un thème natal legacy existant à un utilisateur si compatible."""
        profile_count = UserBirthProfileRepository(db).count_users_with_same_profile(
            birth_date=birth_input.birth_date,
            birth_time=birth_input.birth_time,
            birth_place=birth_input.birth_place,
            birth_timezone=birth_input.birth_timezone,
        )
        if profile_count != 1:
            return

        candidates = ChartResultRepository(db).get_legacy_candidates(limit=500)
        for candidate in candidates:
            expected_hash = ChartResultService.compute_input_hash(
                birth_input=birth_input,
                reference_version=candidate.reference_version,
                ruleset_version=candidate.ruleset_version,
            )
            if expected_hash == candidate.input_hash:
                candidate.user_id = user_id
                db.flush()
                return

    @staticmethod
    def generate_for_user(
        db: Session,
        user_id: int,
        reference_version: str | None = None,
    ) -> UserNatalChartGenerationData:
        """
        Génère un nouveau thème natal pour un utilisateur.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            reference_version: Version de référence à utiliser (optionnel).

        Returns:
            Thème natal généré avec métadonnées.

        Raises:
            UserNatalChartServiceError: Si le profil manque ou en cas de timeout.
        """
        try:
            profile = UserBirthProfileService.get_for_user(db, user_id=user_id)
        except UserBirthProfileServiceError as error:
            raise UserNatalChartServiceError(
                code=error.code,
                message=error.message,
                details=error.details,
            ) from error

        birth_input = BirthInput(
            birth_date=profile.birth_date,
            birth_time=profile.birth_time,
            birth_place=profile.birth_place,
            birth_timezone=profile.birth_timezone,
        )
        started_at = perf_counter()
        timeout_deadline = started_at + settings.natal_generation_timeout_seconds

        def _timeout_check() -> None:
            if perf_counter() > timeout_deadline:
                raise TimeoutError("natal generation timeout budget exceeded")

        try:
            result = NatalCalculationService.calculate(
                db=db,
                birth_input=birth_input,
                reference_version=reference_version,
                timeout_check=_timeout_check,
            )
        except TimeoutError as error:
            raise UserNatalChartServiceError(
                code="natal_generation_timeout",
                message="natal chart generation timed out",
                details={"retryable": "true"},
            ) from error
        except ConnectionError as error:
            raise UserNatalChartServiceError(
                code="natal_engine_unavailable",
                message="natal engine is unavailable",
                details={"retryable": "true"},
            ) from error
        except NatalCalculationError as error:
            raise UserNatalChartServiceError(
                code=error.code,
                message=error.message,
                details=error.details,
            ) from error

        elapsed_seconds = perf_counter() - started_at
        if elapsed_seconds > settings.natal_generation_timeout_seconds:
            raise UserNatalChartServiceError(
                code="natal_generation_timeout",
                message="natal chart generation timed out",
                details={
                    "retryable": "true",
                    "timeout_seconds": str(settings.natal_generation_timeout_seconds),
                },
            )

        try:
            chart_id = ChartResultService.persist_trace(
                db=db,
                birth_input=birth_input,
                natal_result=result,
                user_id=user_id,
            )
        except ChartResultServiceError as error:
            raise UserNatalChartServiceError(
                code=error.code,
                message=error.message,
                details=error.details,
            ) from error

        return UserNatalChartGenerationData(
            chart_id=chart_id,
            result=result,
            metadata=UserNatalChartMetadata(
                reference_version=result.reference_version,
                ruleset_version=result.ruleset_version,
            ),
        )

    @staticmethod
    def get_latest_for_user(db: Session, user_id: int) -> UserNatalChartReadData:
        """
        Récupère le dernier thème natal d'un utilisateur.

        Tente de récupérer un thème legacy si aucun n'est associé.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.

        Returns:
            Dernier thème natal avec métadonnées.

        Raises:
            UserNatalChartServiceError: Si aucun thème n'existe.
        """
        repo = ChartResultRepository(db)
        model = repo.get_latest_by_user_id(user_id)
        if model is None:
            try:
                profile = UserBirthProfileService.get_for_user(db, user_id=user_id)
            except UserBirthProfileServiceError as error:
                raise UserNatalChartServiceError(
                    code=error.code,
                    message=error.message,
                    details=error.details,
                ) from error
            birth_input = BirthInput(
                birth_date=profile.birth_date,
                birth_time=profile.birth_time,
                birth_place=profile.birth_place,
                birth_timezone=profile.birth_timezone,
            )
            UserNatalChartService._claim_latest_legacy_chart_for_user(
                db=db,
                user_id=user_id,
                birth_input=birth_input,
            )
            model = repo.get_latest_by_user_id(user_id)

        if model is None:
            raise UserNatalChartServiceError(
                code="natal_chart_not_found",
                message="natal chart not found",
                details={"user_id": str(user_id)},
            )

        try:
            result = NatalResult.model_validate(model.result_payload)
        except ValidationError as error:
            raise UserNatalChartServiceError(
                code="invalid_chart_result_payload",
                message="stored chart payload is invalid",
                details={"chart_id": model.chart_id},
            ) from error
        return UserNatalChartReadData(
            chart_id=model.chart_id,
            result=result,
            metadata=UserNatalChartMetadata(
                reference_version=model.reference_version,
                ruleset_version=model.ruleset_version,
            ),
            created_at=model.created_at,
        )

    @staticmethod
    def verify_consistency_for_user(db: Session, user_id: int) -> UserNatalChartConsistencyData:
        """
        Vérifie la cohérence entre les thèmes natals d'un utilisateur.

        Compare le dernier thème avec une baseline pour détecter les écarts.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.

        Returns:
            Résultat de la vérification de cohérence.

        Raises:
            UserNatalChartServiceError: Si pas assez de thèmes ou incohérence détectée.
        """
        repo = ChartResultRepository(db)
        latest = repo.get_latest_by_user_id(user_id=user_id)
        if latest is None:
            raise UserNatalChartServiceError(
                code="no_comparable_charts",
                message="not enough chart results to verify consistency",
                details={"user_id": str(user_id)},
            )

        baseline = repo.get_previous_comparable_for_chart(
            user_id=user_id,
            chart_id=latest.chart_id,
            input_hash=latest.input_hash,
            reference_version=latest.reference_version,
            ruleset_version=latest.ruleset_version,
        )
        if baseline is None:
            recent = repo.get_recent_by_user_id(user_id=user_id, limit=2)
            if len(recent) < 2:
                raise UserNatalChartServiceError(
                    code="no_comparable_charts",
                    message="not enough chart results to verify consistency",
                    details={"user_id": str(user_id)},
                )
            previous = recent[1]
            if (
                latest.reference_version != previous.reference_version
                or latest.ruleset_version != previous.ruleset_version
            ):
                raise UserNatalChartServiceError(
                    code="natal_result_mismatch",
                    message="natal results mismatch for version invariants",
                    details={
                        "user_id": str(user_id),
                        "latest_chart_id": latest.chart_id,
                        "baseline_chart_id": previous.chart_id,
                        "reference_version": latest.reference_version,
                        "ruleset_version": latest.ruleset_version,
                        "input_hash": latest.input_hash,
                        "reason": "version_mismatch",
                    },
                )

            if latest.input_hash != previous.input_hash:
                raise UserNatalChartServiceError(
                    code="natal_result_mismatch",
                    message="natal results mismatch for input hash invariant",
                    details={
                        "user_id": str(user_id),
                        "latest_chart_id": latest.chart_id,
                        "baseline_chart_id": previous.chart_id,
                        "reference_version": latest.reference_version,
                        "ruleset_version": latest.ruleset_version,
                        "input_hash": latest.input_hash,
                        "reason": "hash_mismatch",
                    },
                )
            raise UserNatalChartServiceError(
                code="no_comparable_charts",
                message="no comparable chart found with matching invariants",
                details={"user_id": str(user_id)},
            )

        latest_result = UserNatalChartService._validate_natal_result_payload(
            latest.result_payload,
            latest.chart_id,
        )
        baseline_result = UserNatalChartService._validate_natal_result_payload(
            baseline.result_payload,
            baseline.chart_id,
        )
        latest_payload = UserNatalChartService._normalize_payload(
            latest_result.model_dump(mode="json")
        )
        baseline_payload = UserNatalChartService._normalize_payload(
            baseline_result.model_dump(mode="json")
        )
        if latest_payload != baseline_payload:
            raise UserNatalChartServiceError(
                code="natal_result_mismatch",
                message="natal results mismatch for identical invariants",
                details={
                    "user_id": str(user_id),
                    "latest_chart_id": latest.chart_id,
                    "baseline_chart_id": baseline.chart_id,
                    "reference_version": latest.reference_version,
                    "ruleset_version": latest.ruleset_version,
                    "input_hash": latest.input_hash,
                    "reason": "payload_mismatch",
                },
            )

        return UserNatalChartConsistencyData(
            user_id=user_id,
            consistent=True,
            reason="match",
            latest_chart_id=latest.chart_id,
            baseline_chart_id=baseline.chart_id,
            reference_version=latest.reference_version,
            ruleset_version=latest.ruleset_version,
            input_hash=latest.input_hash,
        )
