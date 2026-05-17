"""Formate les libellés astrologiques prediction depuis un contrat injecté."""

from __future__ import annotations

from typing import Protocol

from app.domain.astrology.planet_catalog import load_default_planet_catalog, planet_codes
from app.domain.astrology.zodiac import ordered_sign_codes


class PredictionAstroLabels(Protocol):
    """Contrat minimal attendu par prediction pour afficher les libellés astro."""

    effective_language_code: str

    def sign_label(self, sign_code: str | None) -> str:
        """Retourne le libellé du signe résolu par le propriétaire canonique."""

    def planet_label(self, planet_code: str | None) -> str:
        """Retourne le libellé de la planète résolu par le propriétaire canonique."""

    def aspect_label(self, aspect_code: str | None) -> str:
        """Retourne le libellé de l'aspect résolu par le propriétaire canonique."""

    def house_label(self, house_number: int | str | None) -> str:
        """Retourne le libellé de maison résolu par le propriétaire canonique."""


class AstroLabelFormatter:
    """Formate les labels prediction sans posséder de traduction locale."""

    def __init__(self, labels: PredictionAstroLabels) -> None:
        """Initialise le formateur avec des libellés déjà résolus hors domaine."""
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
        """Expose la langue effective du contrat injecté."""
        return self._labels.effective_language_code

    def planet(self, code: str | None) -> str:
        """Retourne le libellé de planète depuis le contrat canonique."""
        if not code:
            return ""
        normalized = self._normalize_planet_code(code)
        if normalized.startswith("prog_"):
            base_label = self.planet(normalized[5:])
            return f"{base_label} Progressé".strip()
        return self._labels.planet_label(normalized) or normalized

    def sign(self, code: str | None) -> str:
        """Retourne le libellé de signe depuis le contrat canonique."""
        normalized = self._normalize_sign_code(code)
        return self._labels.sign_label(normalized) or normalized

    def aspect(self, code: str | None) -> str:
        """Retourne le libellé d'aspect depuis le contrat canonique."""
        normalized = self._normalize_code(code)
        return self._labels.aspect_label(normalized) or normalized

    def house(self, number: int | str | None) -> str:
        """Retourne le libellé de maison depuis le contrat canonique."""
        return self._labels.house_label(number) or ("" if number is None else str(number))

    def event_kind(self, code: str | None) -> str:
        """Expose le type d'événement sans mapping éditorial local."""
        return self._normalize_code(code)

    def _normalize_planet_code(self, code: str) -> str:
        """Aligne les codes runtime historiques sur les codes DB canoniques."""
        normalized = self._normalize_code(code)
        if normalized.startswith("prog_"):
            return f"prog_{self._normalize_planet_code(normalized[5:])}"
        return self._planet_codes_by_runtime.get(normalized, normalized)

    def _normalize_sign_code(self, code: str | None) -> str:
        """Aligne les abréviations zodiacales sur les codes DB canoniques."""
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
