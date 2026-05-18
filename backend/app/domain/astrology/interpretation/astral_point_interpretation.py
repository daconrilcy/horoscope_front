"""Contrats éditoriaux séparés du calcul des points astraux.

Ce module enrichit une position brute avec un profil et des mots-clés déjà
chargés, sans donner au calcul natal la responsabilité de lire l'éditorial.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.domain.astrology.natal_calculation import NatalAstralPointPosition, NatalResult


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
class InterpretedAstralPoint:
    """Vue interprétative séparée d'un point astral natal objectif."""

    code: str
    variant_code: str | None
    sign: str
    house: int | None
    title: str
    summary: str | None
    micro_note: str | None
    core_keywords: tuple[str, ...]
    shadow_keywords: tuple[str, ...]
    prompt_hints: tuple[str, ...]

    def to_prompt_context(self) -> dict[str, object]:
        """Sérialise la vue pour le contexte LLM sans exposer le profil DB brut."""
        return {
            "code": self.code,
            "variant_code": self.variant_code,
            "sign": self.sign,
            "house": self.house,
            "title": self.title,
            "summary": self.summary,
            "micro_note": self.micro_note,
            "core_keywords": list(self.core_keywords),
            "shadow_keywords": list(self.shadow_keywords),
            "prompt_hints": list(self.prompt_hints),
        }


class AstralPointInterpretationProfileLoader(Protocol):
    """Contrat minimal du chargeur de profils utilisé par le service domaine."""

    def load_profile_for_position(
        self,
        point_position: NatalAstralPointPosition,
        *,
        language_code: str = "en",
        tradition: str = "modern_western",
    ) -> AstralPointInterpretationProfile | None:
        """Charge un profil éditorial compatible avec la position fournie."""
        ...


class AstralPointInterpretationEnricher:
    """Assemble une position calculée avec un profil éditorial explicite."""

    def enrich(
        self,
        *,
        point_position: NatalAstralPointPosition,
        interpretation_profile: AstralPointInterpretationProfile,
    ) -> InterpretedAstralPoint:
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
        return InterpretedAstralPoint(
            code=point_position.code,
            variant_code=point_position.variant_code,
            sign=point_position.sign,
            house=point_position.house,
            title=interpretation_profile.title,
            summary=interpretation_profile.summary,
            micro_note=interpretation_profile.micro_note,
            core_keywords=interpretation_profile.keywords.core,
            shadow_keywords=interpretation_profile.keywords.shadow,
            prompt_hints=(
                *interpretation_profile.keywords.psychological,
                *interpretation_profile.keywords.spiritual,
            ),
        )


class AstralPointInterpretationService:
    """Construit le contexte interprétatif des points à partir du résultat natal."""

    def __init__(
        self,
        profile_loader: AstralPointInterpretationProfileLoader,
        *,
        enricher: AstralPointInterpretationEnricher | None = None,
    ) -> None:
        self.profile_loader = profile_loader
        self.enricher = enricher or AstralPointInterpretationEnricher()

    def build_context(
        self,
        natal_result: NatalResult,
        *,
        language_code: str = "en",
        tradition: str = "modern_western",
    ) -> tuple[InterpretedAstralPoint, ...]:
        """Assemble les points interprétés sans modifier le résultat natal brut."""
        interpreted_points: list[InterpretedAstralPoint] = []
        for point_position in natal_result.points:
            profile = self.profile_loader.load_profile_for_position(
                point_position,
                language_code=language_code,
                tradition=tradition,
            )
            if profile is None:
                continue
            interpreted_points.append(
                self.enricher.enrich(
                    point_position=point_position,
                    interpretation_profile=profile,
                )
            )
        return tuple(interpreted_points)
