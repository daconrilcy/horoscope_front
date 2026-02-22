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
    def prepare(payload: BirthInput) -> BirthPreparedData:
        """
        Prépare les données de naissance pour le calcul.

        Args:
            payload: Données de naissance brutes.

        Returns:
            Données préparées et validées.
        """
        return prepare_birth_data(payload)
