# Repository des sources du materiau interpretatif theme astral.
"""Charge les profils editoriaux DB sous forme de sources pour le builder domaine."""

from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.astrology.interpretation.interpretation_material_contracts import (
    InterpretationMaterialSource,
    interpretation_material_key,
)
from app.infra.db.models import (
    AspectModel,
    AstralAspectInterpretationProfileModel,
    AstralPlanetInterpretationProfileModel,
    AstralSystemModel,
    HouseInterpretationProfileModel,
    HouseModel,
    LanguageModel,
    PlanetModel,
    ReferenceVersionModel,
)


class InterpretationMaterialSourceRepository:
    """Adapte les profils d'interpretation existants vers le contrat source domaine."""

    def __init__(self, db: Session) -> None:
        """Conserve la session SQLAlchemy dans l'owner infra uniquement."""
        self.db = db

    def load_sources(
        self,
        *,
        reference_version: str,
        language_code: str = "en",
        astral_system: str = "modern",
    ) -> tuple[InterpretationMaterialSource, ...]:
        """Charge les sources planetes, maisons et aspects pour une version donnee."""
        version = self._load_reference_version(reference_version)
        language = self._load_language(language_code)
        system = self._load_system(astral_system)
        return (
            *self._load_planet_sources(version.id, language.id, system.id, version.version),
            *self._load_house_sources(version.id, language.id, system.id, version.version),
            *self._load_aspect_sources(version.id, language.id, system.id, version.version),
        )

    def _load_reference_version(self, version: str) -> ReferenceVersionModel:
        """Resout la version de reference demandee."""
        row = self.db.scalar(
            select(ReferenceVersionModel).where(ReferenceVersionModel.version == version)
        )
        if row is None:
            raise ValueError(f"unknown reference version: {version}")
        return row

    def _load_language(self, language_code: str) -> LanguageModel:
        """Resout la langue editoriale demandee."""
        normalized = language_code.strip().lower().replace("_", "-").split("-", maxsplit=1)[0]
        row = self.db.scalar(
            select(LanguageModel).where(LanguageModel.code == (normalized or "en"))
        )
        if row is None and normalized != "en":
            row = self.db.scalar(select(LanguageModel).where(LanguageModel.code == "en"))
        if row is None:
            raise ValueError(f"unknown interpretation material language: {language_code}")
        return row

    def _load_system(self, astral_system: str) -> AstralSystemModel:
        """Resout le systeme astrologique editorial."""
        row = self.db.scalar(
            select(AstralSystemModel).where(AstralSystemModel.name == astral_system)
        )
        if row is None:
            raise ValueError(f"unknown interpretation material system: {astral_system}")
        return row

    def _load_planet_sources(
        self,
        version_id: int,
        language_id: int,
        system_id: int,
        version: str,
    ) -> tuple[InterpretationMaterialSource, ...]:
        """Charge les profils planetaires utilises par les faits planete-signe."""
        rows = self.db.execute(
            select(AstralPlanetInterpretationProfileModel, PlanetModel.code)
            .join(PlanetModel, AstralPlanetInterpretationProfileModel.planet_id == PlanetModel.id)
            .where(
                AstralPlanetInterpretationProfileModel.reference_version_id == version_id,
                AstralPlanetInterpretationProfileModel.language_id == language_id,
                AstralPlanetInterpretationProfileModel.astral_system_id == system_id,
            )
            .order_by(PlanetModel.code)
        ).all()
        return tuple(
            _source_from_profile(
                section="planet_sign_interpretations",
                source_owner="astral_planet_interpretation_profiles",
                source_id=f"planet:{planet_code}",
                source_version=version,
                theme=profile.title,
                summary=profile.summary,
                micro_note=profile.micro_note,
                keywords=_json_fields(
                    profile.core_keywords_json,
                    profile.psychological_expression_json,
                    profile.spiritual_expression_json,
                ),
                risk=_joined_json(profile.shadow_keywords_json, profile.conflict_patterns_json),
                resource=_joined_json(profile.growth_patterns_json, profile.dos_json),
                writing_hints=_json_fields(profile.prompt_hints_json),
                base_weight=0.3,
                planet_code=planet_code,
            )
            for profile, planet_code in rows
        )

    def _load_house_sources(
        self,
        version_id: int,
        language_id: int,
        system_id: int,
        version: str,
    ) -> tuple[InterpretationMaterialSource, ...]:
        """Charge les profils de maisons utilises par les faits planete-maison."""
        rows = self.db.execute(
            select(HouseInterpretationProfileModel, HouseModel.number)
            .join(HouseModel, HouseInterpretationProfileModel.house_id == HouseModel.id)
            .where(
                HouseInterpretationProfileModel.reference_version_id == version_id,
                HouseInterpretationProfileModel.language_id == language_id,
                HouseInterpretationProfileModel.astral_system_id == system_id,
            )
            .order_by(HouseModel.number)
        ).all()
        return tuple(
            _source_from_profile(
                section="planet_house_interpretations",
                source_owner="astral_house_interpretation_profiles",
                source_id=f"house:{house_number}",
                source_version=version,
                theme=profile.title,
                summary=profile.summary,
                micro_note=profile.micro_note,
                keywords=_json_fields(
                    profile.core_keywords_json,
                    profile.psychological_keywords_json,
                    profile.spiritual_keywords_json,
                ),
                risk=_joined_json(profile.shadow_keywords_json, profile.donts_json),
                resource=_joined_json(profile.material_keywords_json, profile.dos_json),
                writing_hints=_json_fields(profile.prompt_hints_json),
                base_weight=0.25,
                house_number=house_number,
            )
            for profile, house_number in rows
        )

    def _load_aspect_sources(
        self,
        version_id: int,
        language_id: int,
        system_id: int,
        version: str,
    ) -> tuple[InterpretationMaterialSource, ...]:
        """Charge les profils d'aspects utilises par les faits d'aspect."""
        rows = self.db.execute(
            select(AstralAspectInterpretationProfileModel, AspectModel.code)
            .join(AspectModel, AstralAspectInterpretationProfileModel.aspect_id == AspectModel.id)
            .where(
                AstralAspectInterpretationProfileModel.reference_version_id == version_id,
                AstralAspectInterpretationProfileModel.language_id == language_id,
                AstralAspectInterpretationProfileModel.astral_system_id == system_id,
            )
            .order_by(AspectModel.code)
        ).all()
        return tuple(
            _source_from_profile(
                section="aspect_interpretations",
                source_owner="astral_aspect_interpretation_profiles",
                source_id=f"aspect:{aspect_code}",
                source_version=version,
                theme=profile.title,
                summary=profile.summary,
                micro_note=profile.micro_note,
                keywords=_json_fields(
                    profile.core_keywords_json,
                    profile.psychological_keywords_json,
                    profile.spiritual_keywords_json,
                ),
                risk=_joined_json(profile.shadow_keywords_json, profile.conflict_patterns_json),
                resource=_joined_json(profile.growth_patterns_json, profile.dos_json),
                writing_hints=_json_fields(profile.prompt_hints_json),
                base_weight=0.35,
                aspect_code=aspect_code,
            )
            for profile, aspect_code in rows
        )


def _source_from_profile(
    *,
    section: str,
    source_owner: str,
    source_id: str,
    source_version: str,
    theme: str,
    summary: str | None,
    micro_note: str | None,
    keywords: tuple[str, ...],
    risk: str,
    resource: str,
    writing_hints: tuple[str, ...],
    base_weight: float,
    planet_code: str | None = None,
    house_number: int | None = None,
    aspect_code: str | None = None,
) -> InterpretationMaterialSource:
    """Convertit un profil DB sans inventer de texte absent."""
    return InterpretationMaterialSource(
        section=interpretation_material_key(section),
        source_owner=source_owner,
        source_id=source_id,
        source_version=source_version,
        theme=theme,
        keywords=keywords,
        interpretive_text=_first_text(summary, micro_note),
        writing_hint=writing_hints[0] if writing_hints else None,
        risk=risk,
        resource=resource,
        base_weight=base_weight,
        planet_code=planet_code,
        house_number=house_number,
        aspect_code=aspect_code,
    )


def _json_fields(*raw_values: str | None) -> tuple[str, ...]:
    """Extrait des listes JSON DB en tuple de textes non vides."""
    values: list[str] = []
    for raw_value in raw_values:
        if raw_value is None:
            continue
        try:
            decoded = json.loads(raw_value)
        except json.JSONDecodeError:
            continue
        if not isinstance(decoded, list):
            continue
        values.extend(str(item).strip() for item in decoded if str(item).strip())
    return tuple(values)


def _joined_json(*raw_values: str | None) -> str:
    """Produit une note compacte depuis des champs JSON deja sources."""
    return "; ".join(_json_fields(*raw_values))


def _first_text(*values: str | None) -> str | None:
    """Retourne le premier texte source non vide."""
    return next((value.strip() for value in values if value and value.strip()), None)


__all__ = ["InterpretationMaterialSourceRepository"]
