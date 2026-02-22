"""
Service de persistance des résultats de thèmes natals.

Ce module gère la sauvegarde et la récupération des résultats de calculs
de thèmes natals pour l'audit et la traçabilité.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.domain.astrology.natal_calculation import NatalResult
from app.domain.astrology.natal_preparation import BirthInput
from app.infra.db.repositories.chart_result_repository import ChartResultRepository


class ChartResultAuditRecord(BaseModel):
    """Enregistrement d'audit d'un résultat de thème natal."""

    chart_id: str
    reference_version: str
    ruleset_version: str
    input_hash: str
    result: NatalResult
    created_at: datetime


class ChartResultServiceError(Exception):
    """Exception levée lors d'erreurs du service de résultats."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        """
        Initialise une erreur de résultat de thème.

        Args:
            code: Code d'erreur unique.
            message: Message descriptif de l'erreur.
            details: Dictionnaire optionnel de détails supplémentaires.
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ChartResultService:
    """
    Service de gestion des résultats de thèmes natals.

    Persiste les résultats avec un hash des entrées pour permettre
    la vérification de reproductibilité et l'audit.
    """

    @staticmethod
    def compute_input_hash(
        birth_input: BirthInput,
        reference_version: str,
        ruleset_version: str,
    ) -> str:
        """Calcule un hash SHA-256 des données d'entrée pour garantir l'unicité."""
        payload = {
            "birth_input": birth_input.model_dump(mode="json"),
            "reference_version": reference_version,
            "ruleset_version": ruleset_version,
        }
        normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @staticmethod
    def persist_trace(
        db: Session,
        birth_input: BirthInput,
        natal_result: NatalResult,
        user_id: int | None = None,
    ) -> str:
        """
        Persiste un résultat de thème natal pour audit.

        Args:
            db: Session de base de données.
            birth_input: Données de naissance utilisées.
            natal_result: Résultat du calcul.
            user_id: Identifiant de l'utilisateur (optionnel).

        Returns:
            Identifiant unique du thème créé.

        Raises:
            ChartResultServiceError: Si les versions sont manquantes.
        """
        if not natal_result.reference_version:
            raise ChartResultServiceError(
                code="invalid_chart_result",
                message="reference version is required",
                details={"field": "reference_version"},
            )
        if not natal_result.ruleset_version:
            raise ChartResultServiceError(
                code="invalid_chart_result",
                message="ruleset version is required",
                details={"field": "ruleset_version"},
            )

        result_payload = natal_result.model_dump()
        if not result_payload:
            raise ChartResultServiceError(
                code="invalid_chart_result",
                message="result payload is required",
                details={"field": "result_payload"},
            )

        repo = ChartResultRepository(db)
        input_hash = ChartResultService.compute_input_hash(
            birth_input,
            natal_result.reference_version,
            natal_result.ruleset_version,
        )
        chart_id = str(uuid.uuid4())

        repo.create(
            user_id=user_id,
            chart_id=chart_id,
            reference_version=natal_result.reference_version,
            ruleset_version=natal_result.ruleset_version,
            input_hash=input_hash,
            result_payload=result_payload,
        )
        return chart_id

    @staticmethod
    def get_audit_record(db: Session, chart_id: str) -> ChartResultAuditRecord:
        """
        Récupère l'enregistrement d'audit d'un thème natal.

        Args:
            db: Session de base de données.
            chart_id: Identifiant du thème.

        Returns:
            Enregistrement d'audit complet.

        Raises:
            ChartResultServiceError: Si le thème n'existe pas.
        """
        model = ChartResultRepository(db).get_by_chart_id(chart_id)
        if model is None:
            raise ChartResultServiceError(
                code="chart_result_not_found",
                message="chart result not found",
                details={"chart_id": chart_id},
            )
        return ChartResultAuditRecord(
            chart_id=model.chart_id,
            reference_version=model.reference_version,
            ruleset_version=model.ruleset_version,
            input_hash=model.input_hash,
            result=NatalResult.model_validate(model.result_payload),
            created_at=model.created_at,
        )
