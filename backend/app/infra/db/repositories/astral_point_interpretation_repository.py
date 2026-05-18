"""Repository des profils éditoriaux de points astraux.

Le repository charge les profils et mots-clés depuis les tables dédiées afin que
les services d'interprétation enrichissent les positions sans coupler le calcul natal.
"""

from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.astrology.interpretation.astral_point_interpretation import (
    AstralPointInterpretationKeywords,
    AstralPointInterpretationProfile,
)
from app.domain.astrology.natal_calculation import NatalAstralPointPosition
from app.infra.db.models.interpretation_reference import AstralPointInterpretationProfileModel
from app.infra.db.models.reference import LanguageModel


class AstralPointInterpretationRepository:
    """Charge les profils interprétatifs utilisables par les services natals."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def load_profile_for_position(
        self,
        point_position: NatalAstralPointPosition,
        *,
        language_code: str = "en",
        tradition: str = "modern_western",
    ) -> AstralPointInterpretationProfile | None:
        """Charge le profil le plus précis pour une position de point astral."""
        exact_profile = self._load_profile(
            point_code=point_position.code,
            variant_code=point_position.variant_code,
            language_code=language_code,
            tradition=tradition,
        )
        if exact_profile is not None:
            return exact_profile
        return self._load_profile(
            point_code=point_position.code,
            variant_code=None,
            language_code=language_code,
            tradition=tradition,
        )

    def _load_profile(
        self,
        *,
        point_code: str,
        variant_code: str | None,
        language_code: str,
        tradition: str,
    ) -> AstralPointInterpretationProfile | None:
        """Charge un profil exact, avec ses mots-clés éditoriaux."""
        row = self.db.execute(
            select(AstralPointInterpretationProfileModel, LanguageModel.code.label("language_code"))
            .join(
                LanguageModel, AstralPointInterpretationProfileModel.language_id == LanguageModel.id
            )
            .where(
                AstralPointInterpretationProfileModel.astral_point_code == point_code,
                AstralPointInterpretationProfileModel.variant_code.is_(variant_code)
                if variant_code is None
                else AstralPointInterpretationProfileModel.variant_code == variant_code,
                LanguageModel.code == language_code,
                AstralPointInterpretationProfileModel.tradition == tradition,
            )
        ).first()
        if row is None:
            return None
        profile, resolved_language_code = row
        keyword_set = profile.keyword_set
        return AstralPointInterpretationProfile(
            profile_id=profile.id,
            point_code=profile.astral_point_code,
            variant_code=profile.variant_code,
            language_code=resolved_language_code,
            tradition=profile.tradition,
            title=profile.title,
            summary=profile.summary,
            micro_note=profile.micro_note,
            keywords=AstralPointInterpretationKeywords(
                core=self._parse_keyword_tuple(keyword_set.core_keywords_json),
                shadow=self._parse_keyword_tuple(keyword_set.shadow_keywords_json),
                psychological=self._parse_keyword_tuple(keyword_set.psychological_keywords_json),
                spiritual=self._parse_keyword_tuple(keyword_set.spiritual_keywords_json),
                relationship=self._parse_keyword_tuple(keyword_set.relationship_keywords_json),
                career=self._parse_keyword_tuple(keyword_set.career_keywords_json),
            ),
        )

    def _parse_keyword_tuple(self, raw: str) -> tuple[str, ...]:
        """Convertit un champ JSON DB en tuple de chaînes non vides."""
        values = json.loads(raw)
        if not isinstance(values, list):
            raise ValueError("astral point interpretation keywords must be a JSON list")
        return tuple(str(value) for value in values if str(value).strip())
