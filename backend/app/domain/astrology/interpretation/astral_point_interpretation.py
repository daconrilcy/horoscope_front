"""Contrats éditoriaux séparés du calcul des points astraux.

Ce module enrichit une position brute avec un profil et des mots-clés déjà
chargés, sans donner au calcul natal la responsabilité de lire l'éditorial.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.astrology.natal_calculation import NatalAstralPointPosition


@dataclass(frozen=True, slots=True)
class AstralPointInterpretationKeywords:
    """Mots-clés éditoriaux groupés pour un point astral."""

    core: tuple[str, ...]
    shadow: tuple[str, ...]
    psychological: tuple[str, ...]
    spiritual: tuple[str, ...]
    relationship: tuple[str, ...]
    career: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AstralPointInterpretationProfile:
    """Profil éditorial typé associé à un point astral canonique."""

    profile_id: int
    point_code: str
    variant_code: str | None
    language_code: str
    tradition: str
    title: str
    summary: str | None
    micro_note: str | None
    keywords: AstralPointInterpretationKeywords


@dataclass(frozen=True, slots=True)
class AstralPointEditorialInterpretation:
    """Interprétation éditoriale prête à être consommée par un service narratif."""

    point_code: str
    variant_code: str | None
    longitude: float
    sign: str
    house: int | None
    title: str
    summary: str | None
    micro_note: str | None
    keywords: AstralPointInterpretationKeywords
    source_profile_id: int


class AstralPointInterpretationEnricher:
    """Assemble une position calculée avec un profil éditorial explicite."""

    def enrich(
        self,
        *,
        point_position: NatalAstralPointPosition,
        interpretation_profile: AstralPointInterpretationProfile,
    ) -> AstralPointEditorialInterpretation:
        """Retourne une interprétation éditoriale sans recalculer la position."""
        if point_position.code != interpretation_profile.point_code:
            raise ValueError(
                "astral point interpretation profile does not match position: "
                f"{point_position.code}/{interpretation_profile.point_code}"
            )
        if (
            interpretation_profile.variant_code is not None
            and point_position.variant_code != interpretation_profile.variant_code
        ):
            raise ValueError(
                "astral point interpretation profile variant does not match position: "
                f"{point_position.variant_code}/{interpretation_profile.variant_code}"
            )
        return AstralPointEditorialInterpretation(
            point_code=point_position.code,
            variant_code=point_position.variant_code,
            longitude=point_position.longitude,
            sign=point_position.sign,
            house=point_position.house,
            title=interpretation_profile.title,
            summary=interpretation_profile.summary,
            micro_note=interpretation_profile.micro_note,
            keywords=interpretation_profile.keywords,
            source_profile_id=interpretation_profile.profile_id,
        )
