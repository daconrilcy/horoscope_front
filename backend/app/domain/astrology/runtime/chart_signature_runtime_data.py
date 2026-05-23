"""Contrats runtime de balance et signature du theme natal.

Ces dataclasses decrivent une synthese structurelle purement astrologique,
derivee des runtime deja calcules.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BalanceScoreRuntimeData:
    """Score normalise d'une famille de balance astrologique."""

    code: str
    score: float
    rank: int

    def __post_init__(self) -> None:
        """Valide le bornage du score et du rang."""
        if not self.code.strip():
            raise ValueError("balance score requires a code")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("balance score must be between 0 and 1")
        if self.rank < 1:
            raise ValueError("balance rank must be positive")


@dataclass(frozen=True, slots=True)
class DominanceRankRuntimeData:
    """Element de classement de dominance structurelle."""

    code: str
    score: float
    rank: int
    source: str

    def __post_init__(self) -> None:
        """Valide une entree de dominance sourcee."""
        if not self.code.strip() or not self.source.strip():
            raise ValueError("dominance rank requires code and source")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("dominance rank score must be between 0 and 1")
        if self.rank < 1:
            raise ValueError("dominance rank must be positive")


@dataclass(frozen=True, slots=True)
class ChartSignatureRuntimeData:
    """Resume non narratif de la signature astrologique dominante."""

    primary_element: str | None
    primary_modality: str | None
    primary_polarity: str | None
    primary_seasonal_quadrant: str | None
    primary_fertility: str | None
    primary_voice: str | None
    primary_form: str | None
    primary_sign: str | None
    primary_planet: str | None
    primary_house: int | None


@dataclass(frozen=True, slots=True)
class ChartBalanceRuntimeData:
    """Balance globale du theme natal et classements dominants."""

    elements: tuple[BalanceScoreRuntimeData, ...]
    modalities: tuple[BalanceScoreRuntimeData, ...]
    polarities: tuple[BalanceScoreRuntimeData, ...]
    seasonal_quadrants: tuple[BalanceScoreRuntimeData, ...]
    fertility: tuple[BalanceScoreRuntimeData, ...]
    voices: tuple[BalanceScoreRuntimeData, ...]
    forms: tuple[BalanceScoreRuntimeData, ...]
    dominant_signs: tuple[DominanceRankRuntimeData, ...]
    dominant_planets: tuple[DominanceRankRuntimeData, ...]
    dominant_houses: tuple[DominanceRankRuntimeData, ...]
    dominant_aspects: tuple[DominanceRankRuntimeData, ...]
    synthesis: ChartSignatureRuntimeData
    version: str = "1"
