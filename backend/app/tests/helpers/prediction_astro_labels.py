"""Fournit un contrat de libelles astrologiques reutilisable pour les tests."""

from __future__ import annotations

from app.domain.prediction.public_astro_vocabulary import PublicAstroVocabulary


class TestPredictionAstroLabels:
    """Expose des libelles canoniques stables pour les tests de prediction."""

    effective_language_code = "fr"

    _SIGNS = {
        "aries": "Belier",
        "leo": "Lion",
    }
    _PLANETS = {
        "sun": "Soleil",
        "moon": "Lune",
        "mercury": "Mercure",
        "venus": "Venus",
        "mars": "Mars",
        "jupiter": "Jupiter",
        "saturn": "Saturne",
        "north_node": "Noeud Nord",
    }
    _ASPECTS = {
        "conjunction": "Conjonction",
        "trine": "Trigone",
        "sextile": "Sextile",
        "square": "Carre",
    }
    _HOUSES = {
        10: "Maison X",
        "10": "Maison X",
    }

    def sign_label(self, sign_code: str | None) -> str:
        """Retourne un libelle de signe sans recreer le resolver applicatif."""
        return self._SIGNS.get(sign_code or "", sign_code or "")

    def planet_label(self, planet_code: str | None) -> str:
        """Retourne un libelle de planete sans dependance DB dans les tests."""
        return self._PLANETS.get(planet_code or "", planet_code or "")

    def aspect_label(self, aspect_code: str | None) -> str:
        """Retourne un libelle d'aspect stable pour les assertions publiques."""
        return self._ASPECTS.get(aspect_code or "", aspect_code or "")

    def house_label(self, house_number: int | str | None) -> str:
        """Retourne un libelle de maison stable pour les assertions publiques."""
        return self._HOUSES.get(house_number, str(house_number or ""))


def make_test_prediction_astro_labels() -> TestPredictionAstroLabels:
    """Construit le contrat de libelles injecte dans les tests."""
    return TestPredictionAstroLabels()


def make_test_public_astro_vocabulary() -> PublicAstroVocabulary:
    """Construit l'adaptateur public injecte dans les politiques de projection."""
    return PublicAstroVocabulary(make_test_prediction_astro_labels())
