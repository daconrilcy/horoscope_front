"""Repository SQLAlchemy pour les donnees de reference astrologiques stables."""

from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from app.infra.db.models.interpretation_reference import (
    AstralHouseAxisDefinitionModel,
    AstralHouseAxisMemberModel,
    AstralPointInterpretationProfileModel,
)
from app.infra.db.models.prediction_reference import (
    AspectProfileModel,
    AstralAspectDefinitionModel,
    AstralAspectOrbRuleModel,
)
from app.infra.db.models.reference import (
    AspectModel,
    AstralAnglePointModel,
    AstralAspectFamilyModel,
    AstralAstrologicalRoleModel,
    AstralCalculationTypeModel,
    AstralConstellationModel,
    AstralDignityTypeModel,
    AstralFixedStarDefinitionModel,
    AstralFixedStarKeywordModel,
    AstralFixedStarModel,
    AstralHemisphereModel,
    AstralHouseModalityModel,
    AstralObjectTypeModel,
    AstralPlanetDefinitionModel,
    AstralPointAliasModel,
    AstralPointCalculationVariantModel,
    AstralPointFamilyModel,
    AstralPointInterpretationKeywordModel,
    AstralPointModel,
    AstralReferenceEpochModel,
    AstralReferenceSourceModel,
    AstralSignModel,
    AstralSpeedModel,
    AstralSystemModel,
    AstralTypicalPolarityModel,
    AstralZodiacalReferenceSystemCategoryModel,
    AstralZodiacalReferenceSystemModel,
    HouseModel,
    LanguageModel,
    PlanetModel,
    ReferenceVersionModel,
)
from app.infra.db.models.translation_reference import (
    AstralFixedStarKeywordTranslationModel,
    AstralPointInterpretationKeywordTranslationModel,
)
from app.infra.db.repositories.astrology_reference_sources import (
    load_aspect_family_names,
    load_aspect_rows,
    load_astral_angle_point_rows,
    load_astral_astrological_role_rows,
    load_astral_calculation_type_rows,
    load_astral_constellation_rows,
    load_astral_fixed_star_definition_rows,
    load_astral_fixed_star_keyword_rows,
    load_astral_fixed_star_keyword_translation_rows,
    load_astral_fixed_star_rows,
    load_astral_hemisphere_rows,
    load_astral_house_modality_rows,
    load_astral_object_type_rows,
    load_astral_planet_definition_rows,
    load_astral_planet_rows,
    load_astral_point_alias_rows,
    load_astral_point_calculation_variant_rows,
    load_astral_point_family_rows,
    load_astral_point_interpretation_keyword_rows,
    load_astral_point_interpretation_keyword_translation_rows,
    load_astral_point_interpretation_profile_rows,
    load_astral_point_rows,
    load_astral_reference_epoch_rows,
    load_astral_reference_source_rows,
    load_astral_sign_rows,
    load_astral_speed_rows,
    load_astral_system_names,
    load_astral_typical_polarity_rows,
    load_astral_zodiacal_reference_system_category_rows,
    load_astral_zodiacal_reference_system_rows,
    load_house_axis_definition_rows,
    load_house_axis_member_rows,
    load_language_rows,
    load_structural_reference_rows,
)


class ReferenceRepository:
    """Accede au vocabulaire astrologique stable et aux versions de parametrage."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_version(self, version: str) -> ReferenceVersionModel | None:
        """Retourne la version de parametrage demandee."""
        return self.db.scalar(
            select(ReferenceVersionModel).where(ReferenceVersionModel.version == version)
        )

    def create_version(self, version: str, description: str = "") -> ReferenceVersionModel:
        """Cree une version de parametrage sans dupliquer le vocabulaire stable."""
        model = ReferenceVersionModel(version=version, description=description)
        self.db.add(model)
        self.db.flush()
        return model

    def has_version_data(self) -> bool:
        """Indique si le vocabulaire stable a deja ete initialise."""
        return any(
            self.db.scalar(select(model.id).limit(1)) is not None
            for model in (
                PlanetModel,
                AstralSignModel,
                AstralDignityTypeModel,
                AstralSystemModel,
                HouseModel,
                AspectModel,
            )
        )

    def seed_version_defaults(self) -> None:
        """Synchronise le vocabulaire invariant depuis les sources JSON canoniques."""
        for row in load_astral_planet_rows():
            code = str(row["code"])
            planet = self.db.scalar(select(PlanetModel).where(PlanetModel.code == code))
            payload = {
                "id": int(row["id"]),
                "name": str(row["name"]),
                "swe_id": int(row["swe_id"]),
            }
            if planet is None:
                self.db.add(PlanetModel(code=code, **payload))
            else:
                planet.name = payload["name"]
                planet.swe_id = payload["swe_id"]

        for row in load_astral_sign_rows():
            code = str(row["code"])
            sign = self.db.scalar(select(AstralSignModel).where(AstralSignModel.code == code))
            payload = {"id": int(row["id"]), "name": str(row["name"])}
            if sign is None:
                self.db.add(AstralSignModel(code=code, **payload))
            else:
                sign.name = payload["name"]

        for row in load_astral_hemisphere_rows():
            key = str(row["key"])
            hemisphere = self.db.scalar(
                select(AstralHemisphereModel).where(AstralHemisphereModel.key == key)
            )
            payload = {
                "id": int(row["id"]),
                "display_name": str(row["display_name"]),
                "description": str(row["description"]),
                "usage_note": None if row.get("usage_note") is None else str(row["usage_note"]),
            }
            if hemisphere is None:
                self.db.add(AstralHemisphereModel(key=key, **payload))
            else:
                for field_name, value in payload.items():
                    if field_name != "id":
                        setattr(hemisphere, field_name, value)
        self.db.flush()

        hemisphere_ids = {row.id for row in self.db.scalars(select(AstralHemisphereModel)).all()}
        for row in load_astral_constellation_rows():
            key = str(row["key"])
            hemisphere_id = None if row.get("hemisphere_id") is None else int(row["hemisphere_id"])
            if hemisphere_id is not None and hemisphere_id not in hemisphere_ids:
                raise ValueError(f"unknown hemisphere id for constellation {key}: {hemisphere_id}")
            constellation = self.db.scalar(
                select(AstralConstellationModel).where(AstralConstellationModel.key == key)
            )
            payload = {
                "id": int(row["id"]),
                "display_name": str(row["display_name"]),
                "latin_name": str(row["latin_name"]),
                "abbreviation": str(row["abbreviation"]),
                "zodiacal": bool(row["zodiacal"]),
                "hemisphere_id": hemisphere_id,
                "notes": None if row.get("notes") is None else str(row["notes"]),
            }
            if constellation is None:
                self.db.add(AstralConstellationModel(key=key, **payload))
            else:
                for field_name, value in payload.items():
                    if field_name != "id":
                        setattr(constellation, field_name, value)

        for row in load_astral_zodiacal_reference_system_category_rows():
            key = str(row["key"])
            category = self.db.scalar(
                select(AstralZodiacalReferenceSystemCategoryModel).where(
                    AstralZodiacalReferenceSystemCategoryModel.key == key
                )
            )
            payload = {
                "id": int(row["id"]),
                "display_name": str(row["display_name"]),
                "description": str(row["description"]),
                "usage_note": None if row.get("usage_note") is None else str(row["usage_note"]),
            }
            if category is None:
                self.db.add(AstralZodiacalReferenceSystemCategoryModel(key=key, **payload))
            else:
                for field_name, value in payload.items():
                    if field_name != "id":
                        setattr(category, field_name, value)
        self.db.flush()

        category_ids = {
            row.id
            for row in self.db.scalars(select(AstralZodiacalReferenceSystemCategoryModel)).all()
        }
        for row in load_astral_zodiacal_reference_system_rows():
            key = str(row["key"])
            category_id = int(row["category_id"])
            if category_id not in category_ids:
                raise ValueError(
                    f"unknown zodiacal reference system category id for {key}: {category_id}"
                )
            system = self.db.scalar(
                select(AstralZodiacalReferenceSystemModel).where(
                    AstralZodiacalReferenceSystemModel.key == key
                )
            )
            payload = {
                "id": int(row["id"]),
                "display_name": str(row["display_name"]),
                "category_id": category_id,
                "description": str(row["description"]),
                "requires_ayanamsha": bool(row["requires_ayanamsha"]),
                "usage_note": None if row.get("usage_note") is None else str(row["usage_note"]),
            }
            if system is None:
                self.db.add(AstralZodiacalReferenceSystemModel(key=key, **payload))
            else:
                for field_name, value in payload.items():
                    if field_name != "id":
                        setattr(system, field_name, value)

        for row in load_astral_reference_epoch_rows():
            key = str(row["key"])
            epoch = self.db.scalar(
                select(AstralReferenceEpochModel).where(AstralReferenceEpochModel.key == key)
            )
            payload = {
                "id": int(row["id"]),
                "display_name": str(row["display_name"]),
                "description": str(row["description"]),
                "epoch_type": str(row["epoch_type"]),
                "julian_year": None
                if row.get("julian_year") is None
                else float(row["julian_year"]),
                "iso_datetime": None
                if row.get("iso_datetime") is None
                else str(row["iso_datetime"]),
                "is_standard": bool(row["is_standard"]),
                "usage_note": None if row.get("usage_note") is None else str(row["usage_note"]),
            }
            if epoch is None:
                self.db.add(AstralReferenceEpochModel(key=key, **payload))
            else:
                for field_name, value in payload.items():
                    if field_name != "id":
                        setattr(epoch, field_name, value)

        for row in load_astral_reference_source_rows():
            key = str(row["key"])
            source = self.db.scalar(
                select(AstralReferenceSourceModel).where(AstralReferenceSourceModel.key == key)
            )
            payload = {
                "id": int(row["id"]),
                "display_name": str(row["display_name"]),
                "category": str(row["category"]),
                "publisher": None if row.get("publisher") is None else str(row["publisher"]),
                "website": None if row.get("website") is None else str(row["website"]),
                "is_canonical": bool(row["is_canonical"]),
                "usage_note": None if row.get("usage_note") is None else str(row["usage_note"]),
            }
            if source is None:
                self.db.add(AstralReferenceSourceModel(key=key, **payload))
            else:
                for field_name, value in payload.items():
                    if field_name != "id":
                        setattr(source, field_name, value)

        self._seed_language_defaults()
        self.seed_fixed_star_defaults()
        self.seed_astral_point_defaults()

        for row in load_structural_reference_rows("dignity_types"):
            code = str(row["code"])
            dignity_type = self.db.scalar(
                select(AstralDignityTypeModel).where(AstralDignityTypeModel.code == code)
            )
            if dignity_type is None:
                self.db.add(AstralDignityTypeModel(code=code, name=str(row["name"])))
            else:
                dignity_type.name = str(row["name"])

        for name in load_astral_system_names():
            if (
                self.db.scalar(select(AstralSystemModel.id).where(AstralSystemModel.name == name))
                is None
            ):
                self.db.add(AstralSystemModel(name=name))

        for row in load_structural_reference_rows("houses"):
            number = int(row["number"])
            house = self.db.scalar(select(HouseModel).where(HouseModel.number == number))
            if house is None:
                self.db.add(HouseModel(number=number, name=str(row["name"])))
            else:
                house.name = str(row["name"])

        for name in load_aspect_family_names():
            if (
                self.db.scalar(
                    select(AstralAspectFamilyModel.id).where(AstralAspectFamilyModel.name == name)
                )
                is None
            ):
                self.db.add(AstralAspectFamilyModel(name=name))
        self.db.flush()
        families = {
            row.name: row.id for row in self.db.scalars(select(AstralAspectFamilyModel)).all()
        }

        for source_row in load_aspect_rows():
            code = str(source_row["code"])
            family_name = str(source_row["family"])
            if family_name not in families:
                raise ValueError(f"unknown aspect family: {family_name}")
            aspect = self.db.scalar(select(AspectModel).where(AspectModel.code == code))
            if aspect is None:
                self.db.add(
                    AspectModel(
                        code=code,
                        name=str(source_row["name"]),
                        angle=float(source_row["angle"]),
                        family=families[family_name],
                    )
                )
            else:
                aspect.name = str(source_row["name"])
                aspect.angle = float(source_row["angle"])
                aspect.family = families[family_name]
        self.db.flush()
        self.seed_astral_object_reference_defaults()
        self.seed_house_axis_defaults()

    def seed_astral_object_reference_defaults(self) -> None:
        """Synchronise les référentiels structurels des objets astrologiques."""
        for row in load_astral_angle_point_rows():
            code = str(row["code"])
            angle = self.db.scalar(
                select(AstralAnglePointModel).where(AstralAnglePointModel.code == code)
            )
            payload = {
                "id": int(row["id"]),
                "short_label": str(row["short_label"]),
                "full_name": str(row["full_name"]),
                "axis": str(row["axis"]),
                "opposite_angle_code": (
                    None
                    if row.get("opposite_angle_code") is None
                    else str(row["opposite_angle_code"])
                ),
                "associated_house": int(row["associated_house"]),
                "description": str(row["description"]),
            }
            if angle is None:
                self.db.add(AstralAnglePointModel(code=code, **payload))
            else:
                for field_name, value in payload.items():
                    if field_name != "id":
                        setattr(angle, field_name, value)

        for row in load_astral_astrological_role_rows():
            self._upsert_code_label_description(AstralAstrologicalRoleModel, row)

        for row in load_astral_calculation_type_rows():
            self._upsert_code_label_description(AstralCalculationTypeModel, row)

        for row in load_astral_object_type_rows():
            self._upsert_code_label_description(AstralObjectTypeModel, row)

        for row in load_astral_speed_rows():
            speed = self.db.scalar(
                select(AstralSpeedModel).where(AstralSpeedModel.name == str(row["name"]))
            )
            if speed is None:
                self.db.add(
                    AstralSpeedModel(
                        id=int(row["id"]),
                        name=str(row["name"]),
                        speed_rank=None
                        if row.get("speed_rank") is None
                        else int(row["speed_rank"]),
                    )
                )
            else:
                speed.speed_rank = None if row.get("speed_rank") is None else int(row["speed_rank"])

        for row in load_astral_typical_polarity_rows():
            polarity = self.db.scalar(
                select(AstralTypicalPolarityModel).where(
                    AstralTypicalPolarityModel.name == str(row["name"])
                )
            )
            if polarity is None:
                self.db.add(AstralTypicalPolarityModel(id=int(row["id"]), name=str(row["name"])))
            else:
                polarity.name = str(row["name"])

        for row in load_astral_house_modality_rows():
            name = str(row["name"])
            modality = self.db.scalar(
                select(AstralHouseModalityModel).where(AstralHouseModalityModel.name == name)
            )
            if modality is None:
                self.db.add(AstralHouseModalityModel(id=int(row["id"]), name=name))
            else:
                modality.name = name

        self.db.flush()
        self.seed_planet_definition_defaults()

    def seed_planet_definition_defaults(self) -> None:
        """Synchronise les definitions planetaires structurelles canoniques."""
        for row in load_astral_planet_definition_rows():
            planet_definition = self.db.scalar(
                select(AstralPlanetDefinitionModel).where(
                    AstralPlanetDefinitionModel.planet_id == int(row["planet_id"])
                )
            )
            payload = {
                "object_type_id": int(row["object_type_id"]),
                "astrological_role_id": int(row["astrological_role_id"]),
                "calculation_type_id": int(row["calculation_type_id"]),
                "speed_rank": int(row["speed_rank"]),
                "speed_class_id": int(row["speed_class_id"]),
                "typical_polarity_id": int(row["typical_polarity_id"]),
                "is_physical_body": bool(row["is_physical_body"]),
                "is_luminary": bool(row["is_luminary"]),
                "is_planet": bool(row["is_planet"]),
                "is_visible_to_naked_eye": bool(row["is_visible_to_naked_eye"]),
                "micro_note": None if row.get("micro_note") is None else str(row["micro_note"]),
            }
            if planet_definition is None:
                self.db.add(
                    AstralPlanetDefinitionModel(
                        id=int(row["id"]),
                        planet_id=int(row["planet_id"]),
                        **payload,
                    )
                )
                continue
            for field_name, value in payload.items():
                setattr(planet_definition, field_name, value)

    def _upsert_code_label_description(
        self,
        model_class: type[
            AstralAstrologicalRoleModel | AstralCalculationTypeModel | AstralObjectTypeModel
        ],
        row: dict[str, object],
    ) -> None:
        """Synchronise une table simple identifiée par `code`."""
        code = str(row["code"])
        model = self.db.scalar(select(model_class).where(model_class.code == code))
        payload = {
            "id": int(row["id"]),
            "label": str(row["label"]),
            "description": str(row["description"]),
        }
        if model is None:
            self.db.add(model_class(code=code, **payload))
            return
        model.label = payload["label"]
        model.description = payload["description"]

    def seed_house_axis_defaults(self) -> None:
        """Synchronise les axes de maisons structurels depuis les sources canoniques."""
        self._seed_language_defaults()

        source_system_names = load_astral_system_names()
        system_ids_by_source_id = {
            index: self.db.scalar(
                select(AstralSystemModel.id).where(AstralSystemModel.name == name)
            )
            for index, name in enumerate(source_system_names, start=1)
        }
        language_ids_by_source_id = {
            int(row["id"]): self.db.scalar(
                select(LanguageModel.id).where(LanguageModel.code == str(row["code"]))
            )
            for row in load_language_rows()
        }
        axis_definitions_by_source_id: dict[int, int] = {}
        for row in load_house_axis_definition_rows():
            source_axis_id = int(row["id"])
            system_id = system_ids_by_source_id[int(row["astral_system_id"])]
            language_id = language_ids_by_source_id[int(row["language_id"])]
            if system_id is None or language_id is None:
                raise ValueError("house axis seed requires canonical systems and languages")
            key = str(row["key"])
            axis = self.db.scalar(
                select(AstralHouseAxisDefinitionModel).where(
                    AstralHouseAxisDefinitionModel.astral_system_id == system_id,
                    AstralHouseAxisDefinitionModel.language_id == language_id,
                    AstralHouseAxisDefinitionModel.key == key,
                )
            )
            if axis is None:
                axis = AstralHouseAxisDefinitionModel(
                    astral_system_id=system_id,
                    key=key,
                    title=str(row["title"]),
                    summary=str(row["summary"]),
                    language_id=language_id,
                    micro_note=None if row.get("micro_note") is None else str(row["micro_note"]),
                )
                self.db.add(axis)
                self.db.flush()
            else:
                axis.title = str(row["title"])
                axis.summary = str(row["summary"])
                axis.micro_note = None if row.get("micro_note") is None else str(row["micro_note"])
            axis_definitions_by_source_id[source_axis_id] = axis.id

        house_ids = {house.id for house in self.db.scalars(select(HouseModel)).all()}
        for row in load_house_axis_member_rows():
            house_id = int(row["house_id"])
            opposite_house_id = int(row["opposite_house_id"])
            axis_id = axis_definitions_by_source_id[int(row["axis_id"])]
            if house_id not in house_ids or opposite_house_id not in house_ids:
                raise ValueError("house axis seed requires canonical astral houses")
            member = self.db.scalar(
                select(AstralHouseAxisMemberModel).where(
                    AstralHouseAxisMemberModel.house_id == house_id,
                )
            )
            if member is None:
                self.db.add(
                    AstralHouseAxisMemberModel(
                        axis_id=axis_id,
                        house_id=house_id,
                        opposite_house_id=opposite_house_id,
                    )
                )
            else:
                member.axis_id = axis_id
                member.opposite_house_id = opposite_house_id

    def _seed_language_defaults(self) -> None:
        """Synchronise les langues avant les seeds localisés."""
        for row in load_language_rows():
            code = str(row["code"])
            language = self.db.scalar(select(LanguageModel).where(LanguageModel.code == code))
            if language is None:
                self.db.add(LanguageModel(id=int(row["id"]), code=code, name=str(row["name"])))
            else:
                language.name = str(row["name"])
        self.db.flush()

    def seed_fixed_star_defaults(self) -> None:
        """Synchronise les étoiles fixes et leurs définitions dans l'ordre canonique."""
        for row in load_astral_fixed_star_rows():
            key = str(row["key"])
            fixed_star = self.db.scalar(
                select(AstralFixedStarModel).where(AstralFixedStarModel.key == key)
            )
            payload = {"id": int(row["id"]), "display_name": str(row["display_name"])}
            if fixed_star is None:
                self.db.add(AstralFixedStarModel(key=key, **payload))
            else:
                fixed_star.display_name = payload["display_name"]
        self.db.flush()

        for row in load_astral_fixed_star_keyword_rows():
            keyword_group = self.db.get(AstralFixedStarKeywordModel, int(row["id"]))
            payload = {
                "keywords_json": json.dumps(
                    list(row["keywords_json"]),
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
            }
            if keyword_group is None:
                self.db.add(AstralFixedStarKeywordModel(id=int(row["id"]), **payload))
            else:
                keyword_group.keywords_json = payload["keywords_json"]
        self.db.flush()

        self._seed_fixed_star_keyword_translations()
        self._seed_fixed_star_definitions()

    def _seed_fixed_star_keyword_translations(self) -> None:
        """Synchronise les traductions des mots-clés d'étoiles fixes."""
        language_ids = {row.code: row.id for row in self.db.scalars(select(LanguageModel)).all()}
        keyword_ids = {row.id for row in self.db.scalars(select(AstralFixedStarKeywordModel)).all()}
        for row in load_astral_fixed_star_keyword_translation_rows():
            keyword_id = int(row["astral_fixed_star_keywords_id"])
            if keyword_id not in keyword_ids:
                raise ValueError(f"unknown fixed star keyword id: {keyword_id}")
            translations = row.get("translations")
            if not isinstance(translations, dict):
                raise ValueError("fixed star keyword translation row must contain translations")
            for locale, translated_values in translations.items():
                language_id = language_ids.get(str(locale))
                if language_id is None:
                    raise ValueError(f"unknown fixed star keyword translation locale: {locale}")
                if not isinstance(translated_values, dict):
                    raise ValueError("fixed star keyword translation values must be objects")
                model = self.db.scalar(
                    select(AstralFixedStarKeywordTranslationModel).where(
                        AstralFixedStarKeywordTranslationModel.astral_fixed_star_keywords_id
                        == keyword_id,
                        AstralFixedStarKeywordTranslationModel.language_id == language_id,
                    )
                )
                keywords_json = json.dumps(
                    list(translated_values["keywords_json"]),
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                if model is None:
                    self.db.add(
                        AstralFixedStarKeywordTranslationModel(
                            astral_fixed_star_keywords_id=keyword_id,
                            language_id=language_id,
                            keywords_json=keywords_json,
                        )
                    )
                else:
                    model.keywords_json = keywords_json
        self.db.flush()

    def _seed_fixed_star_definitions(self) -> None:
        """Synchronise les définitions des étoiles fixes après leurs dépendances."""
        fixed_star_ids = {row.id for row in self.db.scalars(select(AstralFixedStarModel)).all()}
        keyword_ids = {row.id for row in self.db.scalars(select(AstralFixedStarKeywordModel)).all()}
        constellation_ids = {
            row.id for row in self.db.scalars(select(AstralConstellationModel)).all()
        }
        zodiacal_reference_system_ids = {
            row.id for row in self.db.scalars(select(AstralZodiacalReferenceSystemModel)).all()
        }
        reference_epoch_ids = {
            row.id for row in self.db.scalars(select(AstralReferenceEpochModel)).all()
        }
        zodiac_sign_ids = {row.id for row in self.db.scalars(select(AstralSignModel)).all()}
        source_ids = {row.id for row in self.db.scalars(select(AstralReferenceSourceModel)).all()}
        for row in load_astral_fixed_star_definition_rows():
            fixed_star_id = int(row["fixed_star_id"])
            dependency_checks = {
                "fixed star": (fixed_star_id, fixed_star_ids),
                "constellation": (int(row["constellation_id"]), constellation_ids),
                "zodiacal reference system": (
                    int(row["zodiacal_reference_system_id"]),
                    zodiacal_reference_system_ids,
                ),
                "reference epoch": (int(row["reference_epoch_id"]), reference_epoch_ids),
                "zodiac sign": (int(row["zodiac_sign_id"]), zodiac_sign_ids),
                "fixed star keywords": (
                    int(row["astral_fixed_star_keywords_id"]),
                    keyword_ids,
                ),
                "source": (int(row["source_id"]), source_ids),
            }
            for label, (dependency_id, known_ids) in dependency_checks.items():
                if dependency_id not in known_ids:
                    raise ValueError(f"unknown {label} id for fixed star {fixed_star_id}")
            definition = self.db.scalar(
                select(AstralFixedStarDefinitionModel).where(
                    AstralFixedStarDefinitionModel.fixed_star_id == fixed_star_id
                )
            )
            payload = {
                "constellation_id": int(row["constellation_id"]),
                "zodiacal_reference_system_id": int(row["zodiacal_reference_system_id"]),
                "reference_epoch_id": int(row["reference_epoch_id"]),
                "ecliptic_longitude_deg": float(row["ecliptic_longitude_deg"]),
                "zodiac_sign_id": int(row["zodiac_sign_id"]),
                "zodiac_degree": float(row["zodiac_degree"]),
                "declination_deg": None
                if row.get("declination_deg") is None
                else float(row["declination_deg"]),
                "right_ascension_deg": None
                if row.get("right_ascension_deg") is None
                else float(row["right_ascension_deg"]),
                "visual_magnitude": None
                if row.get("visual_magnitude") is None
                else float(row["visual_magnitude"]),
                "astral_fixed_star_keywords_id": int(row["astral_fixed_star_keywords_id"]),
                "is_active": bool(row["is_active"]),
                "source_id": int(row["source_id"]),
                "notes": None if row.get("notes") is None else str(row["notes"]),
            }
            if definition is None:
                self.db.add(
                    AstralFixedStarDefinitionModel(
                        id=int(row["id"]),
                        fixed_star_id=fixed_star_id,
                        **payload,
                    )
                )
                continue
            for field_name, value in payload.items():
                setattr(definition, field_name, value)

    def seed_astral_point_defaults(self) -> None:
        """Synchronise les points astrologiques calculés et leurs profils stables."""
        for row in load_astral_point_family_rows():
            code = str(row["code"])
            family = self.db.scalar(
                select(AstralPointFamilyModel).where(AstralPointFamilyModel.code == code)
            )
            payload = {
                "id": int(row["id"]),
                "display_name": str(row["display_name"]),
                "description": str(row["description"]),
            }
            if family is None:
                self.db.add(AstralPointFamilyModel(code=code, **payload))
            else:
                family.display_name = payload["display_name"]
                family.description = payload["description"]
        self.db.flush()

        family_codes = {row.code for row in self.db.scalars(select(AstralPointFamilyModel)).all()}
        for row in load_astral_point_rows():
            code = str(row["code"])
            point_family = str(row["point_family"])
            if point_family not in family_codes:
                raise ValueError(f"unknown astral point family: {point_family}")
            point = self.db.scalar(select(AstralPointModel).where(AstralPointModel.code == code))
            payload = {
                "id": int(row["id"]),
                "display_name": str(row["display_name"]),
                "point_family": point_family,
                "astronomical_type": str(row["astronomical_type"]),
                "is_physical_body": bool(row["is_physical_body"]),
                "description": str(row["description"]),
            }
            if point is None:
                self.db.add(AstralPointModel(code=code, **payload))
            else:
                for field_name, value in payload.items():
                    if field_name != "id":
                        setattr(point, field_name, value)
        self.db.flush()

        self._seed_astral_point_calculation_variants()
        self._seed_astral_point_aliases()
        self._seed_astral_point_interpretation_keywords()
        self._seed_astral_point_interpretation_profiles()
        self._seed_astral_point_interpretation_keyword_translations()

    def _seed_astral_point_calculation_variants(self) -> None:
        """Synchronise les variantes de calcul des points astrologiques."""
        point_codes = {row.code for row in self.db.scalars(select(AstralPointModel)).all()}
        for row in load_astral_point_calculation_variant_rows():
            point_code = str(row["astral_point_code"])
            variant_code = str(row["variant_code"])
            if point_code not in point_codes:
                raise ValueError(f"unknown astral point for variant: {point_code}")
            variant = self.db.scalar(
                select(AstralPointCalculationVariantModel).where(
                    AstralPointCalculationVariantModel.astral_point_code == point_code,
                    AstralPointCalculationVariantModel.variant_code == variant_code,
                )
            )
            payload = {
                "id": int(row["id"]),
                "display_name": str(row["display_name"]),
                "calculation_mode": str(row["calculation_mode"]),
                "is_default": bool(row["is_default"]),
                "description": str(row["description"]),
            }
            if variant is None:
                self.db.add(
                    AstralPointCalculationVariantModel(
                        astral_point_code=point_code,
                        variant_code=variant_code,
                        **payload,
                    )
                )
            else:
                for field_name, value in payload.items():
                    if field_name != "id":
                        setattr(variant, field_name, value)
        self.db.flush()

    def _seed_astral_point_aliases(self) -> None:
        """Synchronise les alias et clés moteur des points astrologiques."""
        language_ids = {row.code: row.id for row in self.db.scalars(select(LanguageModel)).all()}
        variant_keys = {
            (row.astral_point_code, row.variant_code)
            for row in self.db.scalars(select(AstralPointCalculationVariantModel)).all()
        }
        for row in load_astral_point_alias_rows():
            point_code = str(row["astral_point_code"])
            variant_code = None if row.get("variant_code") is None else str(row["variant_code"])
            if variant_code is not None and (point_code, variant_code) not in variant_keys:
                raise ValueError(f"unknown astral point variant: {point_code}/{variant_code}")
            language_id = language_ids.get(str(row["language"]))
            if language_id is None:
                raise ValueError(f"unknown astral point alias language: {row['language']}")
            alias = str(row["alias"])
            source = str(row["source"])
            model = self.db.scalar(
                select(AstralPointAliasModel).where(
                    AstralPointAliasModel.astral_point_code == point_code,
                    AstralPointAliasModel.variant_code == variant_code,
                    AstralPointAliasModel.alias == alias,
                    AstralPointAliasModel.language_id == language_id,
                    AstralPointAliasModel.source == source,
                )
            )
            payload = {
                "id": int(row["id"]),
                "engine_key": None if row.get("engine_key") is None else str(row["engine_key"]),
                "is_primary": bool(row["is_primary"]),
            }
            if model is None:
                self.db.add(
                    AstralPointAliasModel(
                        astral_point_code=point_code,
                        variant_code=variant_code,
                        alias=alias,
                        language_id=language_id,
                        source=source,
                        **payload,
                    )
                )
            else:
                model.engine_key = payload["engine_key"]
                model.is_primary = payload["is_primary"]
        self.db.flush()

    def _seed_astral_point_interpretation_keywords(self) -> None:
        """Synchronise les groupes de mots-clés des points astrologiques."""
        keyword_fields = (
            "core_keywords_json",
            "shadow_keywords_json",
            "psychological_keywords_json",
            "spiritual_keywords_json",
            "relationship_keywords_json",
            "career_keywords_json",
        )
        for row in load_astral_point_interpretation_keyword_rows():
            keyword_set = self.db.get(AstralPointInterpretationKeywordModel, int(row["id"]))
            payload = {
                field_name: json.dumps(
                    list(row[field_name]),
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                for field_name in keyword_fields
            }
            if keyword_set is None:
                self.db.add(AstralPointInterpretationKeywordModel(id=int(row["id"]), **payload))
            else:
                for field_name, value in payload.items():
                    setattr(keyword_set, field_name, value)
        self.db.flush()

    def _seed_astral_point_interpretation_profiles(self) -> None:
        """Synchronise les profils éditoriaux des points astrologiques."""
        language_ids = {row.code: row.id for row in self.db.scalars(select(LanguageModel)).all()}
        keyword_ids = {
            row.id for row in self.db.scalars(select(AstralPointInterpretationKeywordModel)).all()
        }
        for row in load_astral_point_interpretation_profile_rows():
            point_code = str(row["astral_point_code"])
            variant_code = None if row.get("variant_code") is None else str(row["variant_code"])
            language_id = language_ids.get(str(row["locale"]))
            if language_id is None:
                raise ValueError(f"unknown astral point profile locale: {row['locale']}")
            keyword_set_id = int(row["keyword_set_id"])
            if keyword_set_id not in keyword_ids:
                raise ValueError(f"unknown astral point keyword set: {keyword_set_id}")
            tradition = str(row["tradition"])
            profile = self.db.scalar(
                select(AstralPointInterpretationProfileModel).where(
                    AstralPointInterpretationProfileModel.astral_point_code == point_code,
                    AstralPointInterpretationProfileModel.variant_code == variant_code,
                    AstralPointInterpretationProfileModel.language_id == language_id,
                    AstralPointInterpretationProfileModel.tradition == tradition,
                )
            )
            payload = {
                "id": int(row["id"]),
                "keyword_set_id": keyword_set_id,
                "title": str(row["title"]),
                "summary": None if row.get("summary") is None else str(row["summary"]),
                "micro_note": None if row.get("micro_note") is None else str(row["micro_note"]),
            }
            if profile is None:
                self.db.add(
                    AstralPointInterpretationProfileModel(
                        astral_point_code=point_code,
                        variant_code=variant_code,
                        language_id=language_id,
                        tradition=tradition,
                        **payload,
                    )
                )
            else:
                for field_name, value in payload.items():
                    if field_name != "id":
                        setattr(profile, field_name, value)
        self.db.flush()

    def _seed_astral_point_interpretation_keyword_translations(self) -> None:
        """Synchronise les traductions des mots-clés de points astrologiques."""
        language_ids = {row.code: row.id for row in self.db.scalars(select(LanguageModel)).all()}
        keyword_ids = {
            row.id for row in self.db.scalars(select(AstralPointInterpretationKeywordModel)).all()
        }
        keyword_fields = (
            "core_keywords_json",
            "shadow_keywords_json",
            "psychological_keywords_json",
            "spiritual_keywords_json",
            "relationship_keywords_json",
            "career_keywords_json",
        )
        for row in load_astral_point_interpretation_keyword_translation_rows():
            keyword_set_id = int(row["keyword_set_id"])
            if keyword_set_id not in keyword_ids:
                raise ValueError(f"unknown astral point keyword set: {keyword_set_id}")
            translations = row.get("translations")
            if not isinstance(translations, dict):
                raise ValueError("astral point keyword translation row must contain translations")
            for locale, translated_values in translations.items():
                language_id = language_ids.get(str(locale))
                if language_id is None:
                    raise ValueError(f"unknown astral point keyword translation locale: {locale}")
                if not isinstance(translated_values, dict):
                    raise ValueError("astral point keyword translation values must be objects")
                model = self.db.scalar(
                    select(AstralPointInterpretationKeywordTranslationModel).where(
                        AstralPointInterpretationKeywordTranslationModel.keyword_set_id
                        == keyword_set_id,
                        AstralPointInterpretationKeywordTranslationModel.language_id == language_id,
                    )
                )
                payload = {
                    field_name: json.dumps(
                        list(translated_values[field_name]),
                        ensure_ascii=False,
                        separators=(",", ":"),
                    )
                    for field_name in keyword_fields
                }
                if model is None:
                    self.db.add(
                        AstralPointInterpretationKeywordTranslationModel(
                            keyword_set_id=keyword_set_id,
                            language_id=language_id,
                            **payload,
                        )
                    )
                else:
                    for field_name, value in payload.items():
                        setattr(model, field_name, value)
        self.db.flush()

    def get_reference_data(self, version: str) -> dict[str, object]:
        """Retourne le vocabulaire stable expose pour une version existante."""
        model = self.get_version(version)
        if model is None:
            return {}

        planets = self.db.scalars(select(PlanetModel).order_by(PlanetModel.code)).all()
        signs = self.db.scalars(select(AstralSignModel).order_by(AstralSignModel.id)).all()
        houses = self.db.scalars(select(HouseModel).order_by(HouseModel.number)).all()
        systems = self.db.execute(
            select(
                AstralSystemModel.name,
                AstralSystemModel.inherits_from_system_id,
            ).order_by(AstralSystemModel.name)
        ).all()
        system_name_by_id = {
            row.id: row.name for row in self.db.scalars(select(AstralSystemModel)).all()
        }
        aspects = self.db.execute(
            select(
                AspectModel,
                AstralAspectFamilyModel.name,
                AstralAspectDefinitionModel.is_enabled,
                AstralAspectDefinitionModel.is_major,
                AstralAspectDefinitionModel.is_minor,
                AstralAspectDefinitionModel.default_orb_deg,
                AspectProfileModel.default_valence,
                AspectProfileModel.interpretive_valence,
                AspectProfileModel.energy_type,
            )
            .join(AstralAspectFamilyModel, AspectModel.family == AstralAspectFamilyModel.id)
            .outerjoin(
                AstralSystemModel,
                AstralSystemModel.name == "modern",
            )
            .outerjoin(
                AstralAspectDefinitionModel,
                (AstralAspectDefinitionModel.aspect_id == AspectModel.id)
                & (AstralAspectDefinitionModel.reference_version_id == model.id)
                & (AstralAspectDefinitionModel.astral_system_id == AstralSystemModel.id),
            )
            .outerjoin(
                AspectProfileModel,
                (AspectProfileModel.aspect_id == AspectModel.id)
                & (AspectProfileModel.reference_version_id == model.id),
            )
            .order_by(AspectModel.angle, AspectModel.code)
        ).all()
        SourcePlanetModel = aliased(PlanetModel)
        TargetPlanetModel = aliased(PlanetModel)
        orb_rules = self.db.execute(
            select(
                AstralAspectOrbRuleModel,
                AspectModel.code.label("aspect_code"),
                AstralSystemModel.name.label("system_code"),
                SourcePlanetModel.code.label("source_planet_code"),
                TargetPlanetModel.code.label("target_planet_code"),
            )
            .join(AspectModel, AstralAspectOrbRuleModel.aspect_id == AspectModel.id)
            .join(
                AstralSystemModel, AstralAspectOrbRuleModel.astral_system_id == AstralSystemModel.id
            )
            .outerjoin(
                SourcePlanetModel,
                AstralAspectOrbRuleModel.source_planet_id == SourcePlanetModel.id,
            )
            .outerjoin(
                TargetPlanetModel,
                AstralAspectOrbRuleModel.target_planet_id == TargetPlanetModel.id,
            )
            .where(AstralAspectOrbRuleModel.reference_version_id == model.id)
            .order_by(
                AstralSystemModel.name,
                AspectModel.code,
                AstralAspectOrbRuleModel.priority.desc(),
            )
        ).all()
        return {
            "version": model.version,
            "planets": [
                {"code": item.code, "name": item.name, "swe_id": item.swe_id} for item in planets
            ],
            "signs": [{"code": item.code, "name": item.name} for item in signs],
            "houses": [{"number": item.number, "name": item.name} for item in houses],
            "house_axes": self._get_house_axes(),
            "astral_systems": [
                {
                    "code": name,
                    "name": name,
                    "inherits_from_system_code": (
                        None if parent_id is None else system_name_by_id.get(int(parent_id))
                    ),
                }
                for name, parent_id in systems
            ],
            "aspects": [
                {
                    "code": aspect.code,
                    "name": aspect.name,
                    "angle": aspect.angle,
                    "family": family_name,
                    "is_enabled": is_enabled,
                    "is_major": is_major,
                    "is_minor": is_minor,
                    "default_orb_deg": default_orb_deg,
                    "default_valence": default_valence,
                    "interpretive_valence": interpretive_valence,
                    "energy_type": energy_type,
                }
                for (
                    aspect,
                    family_name,
                    is_enabled,
                    is_major,
                    is_minor,
                    default_orb_deg,
                    default_valence,
                    interpretive_valence,
                    energy_type,
                ) in aspects
            ],
            "aspect_orb_rules": [
                {
                    "aspect_code": aspect_code,
                    "system_code": system_code,
                    "calculation_context": rule.calculation_context,
                    "source_body_type": rule.source_body_type,
                    "source_planet_code": source_planet_code,
                    "source_point_code": rule.source_point_code,
                    "target_body_type": rule.target_body_type,
                    "target_planet_code": target_planet_code,
                    "target_point_code": rule.target_point_code,
                    "orb_deg": rule.orb_deg,
                    "priority": rule.priority,
                    "is_enabled": rule.is_enabled,
                    "micro_note": rule.micro_note,
                }
                for (
                    rule,
                    aspect_code,
                    system_code,
                    source_planet_code,
                    target_planet_code,
                ) in orb_rules
            ],
        }

    def _get_house_axes(self) -> list[dict[str, object]]:
        """Charge les axes de maisons localises depuis les tables canoniques."""
        AxisHouseModel = aliased(HouseModel)
        OppositeHouseModel = aliased(HouseModel)
        rows = self.db.execute(
            select(
                AxisHouseModel.number.label("house_number"),
                OppositeHouseModel.number.label("opposite_house"),
                AstralHouseAxisDefinitionModel.key.label("theme"),
            )
            .select_from(AstralHouseAxisMemberModel)
            .join(AxisHouseModel, AstralHouseAxisMemberModel.house_id == AxisHouseModel.id)
            .join(
                OppositeHouseModel,
                AstralHouseAxisMemberModel.opposite_house_id == OppositeHouseModel.id,
            )
            .join(
                AstralHouseAxisDefinitionModel,
                AstralHouseAxisMemberModel.axis_id == AstralHouseAxisDefinitionModel.id,
            )
            .join(LanguageModel, AstralHouseAxisDefinitionModel.language_id == LanguageModel.id)
            .join(
                AstralSystemModel,
                AstralHouseAxisDefinitionModel.astral_system_id == AstralSystemModel.id,
            )
            .where(
                LanguageModel.code == "en",
                AstralSystemModel.name == "modern",
            )
            .order_by(AxisHouseModel.number)
        ).all()

        return [
            {
                "house_number": row.house_number,
                "opposite_house": row.opposite_house,
                "theme": row.theme,
            }
            for row in rows
        ]
