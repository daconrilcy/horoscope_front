"""
Service de calcul de thèmes natals.

Ce module orchestre le calcul des thèmes natals en utilisant les données
de référence et les règles de calcul astrologique.
"""

from __future__ import annotations

from collections.abc import Callable

from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.astrology.natal_calculation import (
    NatalCalculationError,
    NatalResult,
    build_natal_result,
)
from app.domain.astrology.natal_preparation import BirthInput
from app.services.reference_data_service import ReferenceDataService


class NatalCalculationService:
    """
    Service de calcul de thèmes natals.

    Coordonne le chargement des données de référence et l'exécution
    des calculs astrologiques.
    """

    @staticmethod
    def calculate(
        db: Session,
        birth_input: BirthInput,
        reference_version: str | None = None,
        timeout_check: Callable[[], None] | None = None,
    ) -> NatalResult:
        """
        Calcule un thème natal complet.

        Args:
            db: Session de base de données.
            birth_input: Données de naissance.
            reference_version: Version des données de référence (optionnel).
            timeout_check: Callback de vérification de timeout (optionnel).

        Returns:
            Résultat du calcul natal.

        Raises:
            NatalCalculationError: Si la version de référence n'existe pas.
        """
        resolved_version = reference_version or settings.active_reference_version

        if timeout_check is not None:
            timeout_check()
        reference_data = ReferenceDataService.get_active_reference_data(
            db,
            version=resolved_version,
        )
        if timeout_check is not None:
            timeout_check()

        if not reference_data:
            raise NatalCalculationError(
                code="reference_version_not_found",
                message="reference version not found",
                details={"version": resolved_version},
            )

        return build_natal_result(
            birth_input=birth_input,
            reference_data=reference_data,
            ruleset_version=settings.ruleset_version,
            timeout_check=timeout_check,
        )
