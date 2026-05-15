"""Repository SQLAlchemy pour les donnees de reference astrologiques stables."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from app.infra.db.models.prediction_reference import (
    AstralAspectDefinitionModel,
    AstralAspectOrbRuleModel,
)
from app.infra.db.models.reference import (
    AspectModel,
    AstralAspectFamilyModel,
    AstralDignityTypeModel,
    AstralSignModel,
    AstralSystemModel,
    HouseModel,
    PlanetModel,
    ReferenceVersionModel,
)
from app.infra.db.repositories.astrology_reference_sources import (
    load_aspect_family_names,
    load_aspect_rows,
    load_astral_system_names,
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
                AstralAspectDefinitionModel.default_orb_deg,
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
                    "default_orb_deg": default_orb_deg,
                }
                for aspect, family_name, default_orb_deg in aspects
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
