"""
Service de préparation des données natales.

Ce module prépare et valide les données de naissance avant le calcul
du thème natal.
"""

from app.domain.astrology.natal_preparation import (
    BirthInput,
    BirthPreparedData,
    prepare_birth_data,
)


class NatalPreparationService:
    """
    Service de préparation des données de naissance.

    Valide et normalise les données d'entrée avant le calcul astrologique.
    """

    @staticmethod
    def prepare(payload: BirthInput, *, tt_enabled: bool = False) -> BirthPreparedData:
        """
        Prépare les données de naissance pour le calcul.

        Args:
            payload: Données de naissance brutes.
            tt_enabled: Si True, calcule ΔT et JD TT (story 22.2).

        Returns:
            Données préparées et validées.
        """
        return prepare_birth_data(payload, tt_enabled=tt_enabled)
