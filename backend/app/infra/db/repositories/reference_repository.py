"""Repository SQLAlchemy pour les donnees de reference astrologiques stables."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from app.infra.db.models.interpretation_reference import (
    AstralHouseAxisDefinitionModel,
    AstralHouseAxisMemberModel,
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
    AstralDignityTypeModel,
    AstralHouseModalityModel,
    AstralObjectTypeModel,
    AstralPlanetDefinitionModel,
    AstralSignModel,
    AstralSpeedModel,
    AstralSystemModel,
    AstralTypicalPolarityModel,
    HouseModel,
    LanguageModel,
    PlanetModel,
    ReferenceVersionModel,
)
from app.infra.db.repositories.astrology_reference_sources import (
    load_aspect_family_names,
    load_aspect_rows,
    load_astral_angle_point_rows,
    load_astral_astrological_role_rows,
    load_astral_calculation_type_rows,
    load_astral_house_modality_rows,
    load_astral_object_type_rows,
    load_astral_planet_definition_rows,
    load_astral_speed_rows,
    load_astral_system_names,
    load_astral_typical_polarity_rows,
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
        for row in load_structural_reference_rows("planets"):
            code = str(row["code"])
            planet = self.db.scalar(select(PlanetModel).where(PlanetModel.code == code))
            if planet is None:
                self.db.add(PlanetModel(code=code, name=str(row["name"])))
            else:
                planet.name = str(row["name"])

        for row in load_structural_reference_rows("signs"):
            code = str(row["code"])
            sign = self.db.scalar(select(AstralSignModel).where(AstralSignModel.code == code))
            if sign is None:
                self.db.add(AstralSignModel(code=code, name=str(row["name"])))
            else:
                sign.name = str(row["name"])

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
        for row in load_language_rows():
            code = str(row["code"])
            language = self.db.scalar(select(LanguageModel).where(LanguageModel.code == code))
            if language is None:
                self.db.add(LanguageModel(code=code, name=str(row["name"])))
            else:
                language.name = str(row["name"])
        self.db.flush()

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

    def get_reference_data(self, version: str) -> dict[str, object]:
        """Retourne le vocabulaire stable expose pour une version existante."""
        model = self.get_version(version)
        if model is None:
            return {}

        planets = self.db.scalars(select(PlanetModel).order_by(PlanetModel.code)).all()
        signs = self.db.scalars(select(AstralSignModel).order_by(AstralSignModel.code)).all()
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
            "planets": [{"code": item.code, "name": item.name} for item in planets],
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
