"""Adapte les libelles astrologiques publics a partir d'un contrat canonique."""

from __future__ import annotations

from typing import Any, Protocol

from app.domain.astrology.planet_catalog import load_default_planet_catalog, planet_codes
from app.domain.astrology.zodiac import ordered_sign_codes


class PredictionAstroLabels(Protocol):
    """Contrat minimal attendu par prediction pour afficher les libelles astro."""

    effective_language_code: str

    def sign_label(self, sign_code: str | None) -> str:
        """Retourne le libelle du signe resolu par le proprietaire canonique."""

    def planet_label(self, planet_code: str | None) -> str:
        """Retourne le libelle de la planete resolu par le proprietaire canonique."""

    def aspect_label(self, aspect_code: str | None) -> str:
        """Retourne le libelle de l'aspect resolu par le proprietaire canonique."""

    def house_label(self, house_number: int | str | None) -> str:
        """Retourne le libelle de maison resolu par le proprietaire canonique."""


class PublicAstroVocabulary:
    """Formate les labels prediction sans posseder de traduction locale."""

    _STAR_DATA: dict[str, dict[str, Any]] = {
        "regulus": {"display_name": "Regulus", "lon": 150.0},
        "algol": {"display_name": "Algol", "lon": 56.0},
        "spica": {"display_name": "Spica", "lon": 203.0},
        "antares": {"display_name": "Antares", "lon": 249.0},
        "aldebaran": {"display_name": "Aldebaran", "lon": 69.0},
        "sirius": {"display_name": "Sirius", "lon": 103.0},
        "fomalhaut": {"display_name": "Fomalhaut", "lon": 333.0},
        "betelgeuse": {"display_name": "Betelgeuse", "lon": 88.0},
        "achernar": {"display_name": "Achernar", "lon": 45.0},
        "vega": {"display_name": "Vega", "lon": 285.0},
    }
    _ASPECT_TONES: dict[str, str] = {
        "trine": "fluidité",
        "sextile": "fluidité",
        "square": "ajustement",
        "opposition": "ajustement",
        "conjunction": "intensification",
        "quincunx": "adaptation",
    }

    def __init__(self, labels: PredictionAstroLabels) -> None:
        """Initialise l'adaptateur avec des libelles deja resolus hors domaine."""
        self._labels = labels
        self._sign_codes = ordered_sign_codes()
        self._planet_codes_by_runtime = {
            item.runtime_code.lower(): item.code for item in load_default_planet_catalog()
        }
        self._planet_codes_by_runtime.update(
            dict(zip(("so", "lu", "me", "ve", "ma", "ju", "sa", "ur", "ne", "pl"), planet_codes()))
        )

    @property
    def effective_language_code(self) -> str:
        """Expose la langue effective du contrat injecte."""
        return self._labels.effective_language_code

    def planet(self, code: str | None) -> str:
        """Retourne le libelle de planete depuis le contrat canonique."""
        if not code:
            return ""
        normalized = self._normalize_planet_code(code)
        if normalized.startswith("prog_"):
            base_label = self.planet(normalized[5:])
            return f"{base_label} Progressé".strip()
        return self._labels.planet_label(normalized) or normalized

    def sign(self, code: str | None) -> str:
        """Retourne le libelle de signe depuis le contrat canonique."""
        normalized = self._normalize_sign_code(code)
        return self._labels.sign_label(normalized) or normalized

    def aspect(self, code: str | None) -> str:
        """Retourne le libelle d'aspect depuis le contrat canonique."""
        normalized = self._normalize_code(code)
        return self._labels.aspect_label(normalized) or normalized

    def house(self, number: int | str | None) -> str:
        """Retourne le libelle de maison depuis le contrat canonique."""
        return self._labels.house_label(number) or ("" if number is None else str(number))

    def event_kind(self, code: str | None) -> str:
        """Expose le type d'evenement sans mapping editorial local."""
        return self._normalize_code(code)

    def star(self, key: str | None) -> str:
        """Retourne le nom propre d'etoile fixe non DB-backed."""
        normalized = self._normalize_code(key)
        return str(self._STAR_DATA.get(normalized, {}).get("display_name") or normalized)

    def aspect_tone(self, code: str | None) -> str:
        """Retourne une tonalite technique non traduite pour le rendu prediction."""
        return self._ASPECT_TONES.get(self._normalize_code(code), "nuance")

    def _normalize_planet_code(self, code: str) -> str:
        """Aligne les codes runtime historiques sur les codes DB canoniques."""
        normalized = self._normalize_code(code)
        if normalized.startswith("prog_"):
            return f"prog_{self._normalize_planet_code(normalized[5:])}"
        return self._planet_codes_by_runtime.get(normalized, normalized)

    def _normalize_sign_code(self, code: str | None) -> str:
        """Aligne les abreviations zodiacales sur les codes DB canoniques."""
        normalized = self._normalize_code(code)
        if not normalized:
            return ""
        if normalized in self._sign_codes:
            return normalized
        matches = [sign_code for sign_code in self._sign_codes if sign_code.startswith(normalized)]
        return matches[0] if len(matches) == 1 else normalized

    @staticmethod
    def _normalize_code(code: str | None) -> str:
        """Normalise un code technique sans le traduire localement."""
        return "" if code is None else str(code).strip().lower()


def fixed_star_longitudes() -> dict[str, float]:
    """Retourne les longitudes techniques des etoiles fixes supportees."""
    return {
        key: float(star_data["lon"]) for key, star_data in PublicAstroVocabulary._STAR_DATA.items()
    }


def fixed_star_display_name(key: str | None) -> str:
    """Retourne le nom propre technique d'une etoile fixe."""
    normalized = "" if key is None else str(key).strip().lower()
    return str(
        PublicAstroVocabulary._STAR_DATA.get(normalized, {}).get("display_name") or normalized
    )
