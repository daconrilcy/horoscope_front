from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.infra.db.models.reference import (
    AspectModel,
    AstroCharacteristicModel,
    HouseModel,
    PlanetModel,
    ReferenceVersionModel,
    SignModel,
)


class ReferenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_version(self, version: str) -> ReferenceVersionModel | None:
        return self.db.scalar(
            select(ReferenceVersionModel).where(ReferenceVersionModel.version == version)
        )

    def create_version(self, version: str, description: str = "") -> ReferenceVersionModel:
        model = ReferenceVersionModel(version=version, description=description)
        self.db.add(model)
        self.db.flush()
        return model

    def clear_version_data(self, reference_version_id: int) -> None:
        for model in (
            AstroCharacteristicModel,
            AspectModel,
            HouseModel,
            SignModel,
            PlanetModel,
        ):
            self.db.execute(delete(model).where(model.reference_version_id == reference_version_id))

    def has_version_data(self, reference_version_id: int) -> bool:
        return any(
            self.db.scalar(
                select(model.id).where(model.reference_version_id == reference_version_id).limit(1)
            )
            is not None
            for model in (
                PlanetModel,
                SignModel,
                HouseModel,
                AspectModel,
                AstroCharacteristicModel,
            )
        )

    def seed_version_defaults(self, reference_version_id: int) -> None:
        self.db.add_all(
            [
                PlanetModel(
                    reference_version_id=reference_version_id,
                    code="sun",
                    name="Sun",
                ),
                PlanetModel(
                    reference_version_id=reference_version_id,
                    code="moon",
                    name="Moon",
                ),
                PlanetModel(
                    reference_version_id=reference_version_id,
                    code="mercury",
                    name="Mercury",
                ),
                PlanetModel(
                    reference_version_id=reference_version_id,
                    code="venus",
                    name="Venus",
                ),
                PlanetModel(
                    reference_version_id=reference_version_id,
                    code="mars",
                    name="Mars",
                ),
                PlanetModel(
                    reference_version_id=reference_version_id,
                    code="jupiter",
                    name="Jupiter",
                ),
                PlanetModel(
                    reference_version_id=reference_version_id,
                    code="saturn",
                    name="Saturn",
                ),
                PlanetModel(
                    reference_version_id=reference_version_id,
                    code="uranus",
                    name="Uranus",
                ),
                PlanetModel(
                    reference_version_id=reference_version_id,
                    code="neptune",
                    name="Neptune",
                ),
                PlanetModel(
                    reference_version_id=reference_version_id,
                    code="pluto",
                    name="Pluto",
                ),
            ]
        )
        self.db.add_all(
            [
                SignModel(reference_version_id=reference_version_id, code="aries", name="Aries"),
                SignModel(reference_version_id=reference_version_id, code="taurus", name="Taurus"),
            ]
        )
        self.db.add_all(
            [
                HouseModel(reference_version_id=reference_version_id, number=1, name="Self"),
                HouseModel(reference_version_id=reference_version_id, number=2, name="Resources"),
                HouseModel(
                    reference_version_id=reference_version_id,
                    number=3,
                    name="Communication",
                ),
                HouseModel(reference_version_id=reference_version_id, number=4, name="Home"),
                HouseModel(reference_version_id=reference_version_id, number=5, name="Creativity"),
                HouseModel(reference_version_id=reference_version_id, number=6, name="Health"),
                HouseModel(
                    reference_version_id=reference_version_id,
                    number=7,
                    name="Partnership",
                ),
                HouseModel(
                    reference_version_id=reference_version_id,
                    number=8,
                    name="Transformation",
                ),
                HouseModel(reference_version_id=reference_version_id, number=9, name="Beliefs"),
                HouseModel(reference_version_id=reference_version_id, number=10, name="Career"),
                HouseModel(
                    reference_version_id=reference_version_id,
                    number=11,
                    name="Community",
                ),
                HouseModel(
                    reference_version_id=reference_version_id,
                    number=12,
                    name="Subconscious",
                ),
            ]
        )
        self.db.add_all(
            [
                AspectModel(
                    reference_version_id=reference_version_id,
                    code="conjunction",
                    name="Conjunction",
                    angle=0,
                ),
                AspectModel(
                    reference_version_id=reference_version_id,
                    code="sextile",
                    name="Sextile",
                    angle=60,
                ),
                AspectModel(
                    reference_version_id=reference_version_id,
                    code="square",
                    name="Square",
                    angle=90,
                ),
                AspectModel(
                    reference_version_id=reference_version_id,
                    code="trine",
                    name="Trine",
                    angle=120,
                ),
                AspectModel(
                    reference_version_id=reference_version_id,
                    code="opposition",
                    name="Opposition",
                    angle=180,
                ),
            ]
        )
        self.db.add_all(
            [
                AstroCharacteristicModel(
                    reference_version_id=reference_version_id,
                    entity_type="planet",
                    entity_code="sun",
                    trait="element",
                    value="fire",
                ),
                AstroCharacteristicModel(
                    reference_version_id=reference_version_id,
                    entity_type="sign",
                    entity_code="aries",
                    trait="modality",
                    value="cardinal",
                ),
            ]
        )

    def clone_version_data(self, source_version_id: int, target_version_id: int) -> None:
        planets = self.db.scalars(
            select(PlanetModel).where(PlanetModel.reference_version_id == source_version_id)
        ).all()
        signs = self.db.scalars(
            select(SignModel).where(SignModel.reference_version_id == source_version_id)
        ).all()
        houses = self.db.scalars(
            select(HouseModel).where(HouseModel.reference_version_id == source_version_id)
        ).all()
        aspects = self.db.scalars(
            select(AspectModel).where(AspectModel.reference_version_id == source_version_id)
        ).all()
        characteristics = self.db.scalars(
            select(AstroCharacteristicModel).where(
                AstroCharacteristicModel.reference_version_id == source_version_id
            )
        ).all()

        self.db.add_all(
            [
                PlanetModel(
                    reference_version_id=target_version_id,
                    code=item.code,
                    name=item.name,
                )
                for item in planets
            ]
        )
        self.db.add_all(
            [
                SignModel(
                    reference_version_id=target_version_id,
                    code=item.code,
                    name=item.name,
                )
                for item in signs
            ]
        )
        self.db.add_all(
            [
                HouseModel(
                    reference_version_id=target_version_id,
                    number=item.number,
                    name=item.name,
                )
                for item in houses
            ]
        )
        self.db.add_all(
            [
                AspectModel(
                    reference_version_id=target_version_id,
                    code=item.code,
                    name=item.name,
                    angle=item.angle,
                )
                for item in aspects
            ]
        )
        self.db.add_all(
            [
                AstroCharacteristicModel(
                    reference_version_id=target_version_id,
                    entity_type=item.entity_type,
                    entity_code=item.entity_code,
                    trait=item.trait,
                    value=item.value,
                )
                for item in characteristics
            ]
        )

    def get_reference_data(self, version: str) -> dict[str, object]:
        model = self.get_version(version)
        if model is None:
            return {}

        planets = self.db.scalars(
            select(PlanetModel)
            .where(PlanetModel.reference_version_id == model.id)
            .order_by(PlanetModel.code)
        ).all()
        signs = self.db.scalars(
            select(SignModel)
            .where(SignModel.reference_version_id == model.id)
            .order_by(SignModel.code)
        ).all()
        houses = self.db.scalars(
            select(HouseModel)
            .where(HouseModel.reference_version_id == model.id)
            .order_by(HouseModel.number)
        ).all()
        aspects = self.db.scalars(
            select(AspectModel)
            .where(AspectModel.reference_version_id == model.id)
            .order_by(AspectModel.angle, AspectModel.code)
        ).all()
        characteristics = self.db.scalars(
            select(AstroCharacteristicModel)
            .where(AstroCharacteristicModel.reference_version_id == model.id)
            .order_by(
                AstroCharacteristicModel.entity_type,
                AstroCharacteristicModel.entity_code,
                AstroCharacteristicModel.trait,
            )
        ).all()

        return {
            "version": model.version,
            "planets": [{"code": item.code, "name": item.name} for item in planets],
            "signs": [{"code": item.code, "name": item.name} for item in signs],
            "houses": [{"number": item.number, "name": item.name} for item in houses],
            "aspects": [
                {"code": item.code, "name": item.name, "angle": item.angle} for item in aspects
            ],
            "characteristics": [
                {
                    "entity_type": item.entity_type,
                    "entity_code": item.entity_code,
                    "trait": item.trait,
                    "value": item.value,
                }
                for item in characteristics
            ],
        }
