"""Repository SQLAlchemy pour les donnees de reference astrologiques stables."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import DEFAULT_ASPECT_ORBS
from app.infra.db.models.reference import (
    AspectModel,
    AstralSignModel,
    HouseModel,
    PlanetModel,
    ReferenceVersionModel,
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
                HouseModel,
                AspectModel,
            )
        )

    def has_complete_version_data(self) -> bool:
        """Indique si chaque table structurelle stable contient au moins une entree."""
        return all(
            self.db.scalar(select(model.id).limit(1)) is not None
            for model in (
                PlanetModel,
                AstralSignModel,
                HouseModel,
                AspectModel,
            )
        )

    def seed_version_defaults(self) -> None:
        """Insere les entrees manquantes du vocabulaire invariant."""
        planet_rows = [
            ("sun", "Sun"),
            ("moon", "Moon"),
            ("mercury", "Mercury"),
            ("venus", "Venus"),
            ("mars", "Mars"),
            ("jupiter", "Jupiter"),
            ("saturn", "Saturn"),
            ("uranus", "Uranus"),
            ("neptune", "Neptune"),
            ("pluto", "Pluto"),
        ]
        for code, name in planet_rows:
            if self.db.scalar(select(PlanetModel.id).where(PlanetModel.code == code)) is None:
                self.db.add(PlanetModel(code=code, name=name))

        sign_rows = [
            ("aries", "Aries"),
            ("taurus", "Taurus"),
            ("gemini", "Gemini"),
            ("cancer", "Cancer"),
            ("leo", "Leo"),
            ("virgo", "Virgo"),
            ("libra", "Libra"),
            ("scorpio", "Scorpio"),
            ("sagittarius", "Sagittarius"),
            ("capricorn", "Capricorn"),
            ("aquarius", "Aquarius"),
            ("pisces", "Pisces"),
        ]
        for code, name in sign_rows:
            if (
                self.db.scalar(select(AstralSignModel.id).where(AstralSignModel.code == code))
                is None
            ):
                self.db.add(AstralSignModel(code=code, name=name))

        house_rows = [
            (1, "Self"),
            (2, "Resources"),
            (3, "Communication"),
            (4, "Home"),
            (5, "Creativity"),
            (6, "Health"),
            (7, "Partnership"),
            (8, "Transformation"),
            (9, "Beliefs"),
            (10, "Career"),
            (11, "Community"),
            (12, "Subconscious"),
        ]
        for number, name in house_rows:
            if self.db.scalar(select(HouseModel.id).where(HouseModel.number == number)) is None:
                self.db.add(HouseModel(number=number, name=name))

        aspect_rows = [
            ("conjunction", "Conjunction", 0),
            ("sextile", "Sextile", 60),
            ("square", "Square", 90),
            ("trine", "Trine", 120),
            ("opposition", "Opposition", 180),
        ]
        for code, name, angle in aspect_rows:
            if self.db.scalar(select(AspectModel.id).where(AspectModel.code == code)) is None:
                self.db.add(
                    AspectModel(
                        code=code,
                        name=name,
                        angle=angle,
                        default_orb_deg=DEFAULT_ASPECT_ORBS[code],
                    )
                )

    def get_reference_data(self, version: str) -> dict[str, object]:
        """Retourne le vocabulaire stable expose pour une version existante."""
        model = self.get_version(version)
        if model is None:
            return {}

        planets = self.db.scalars(select(PlanetModel).order_by(PlanetModel.code)).all()
        signs = self.db.scalars(select(AstralSignModel).order_by(AstralSignModel.code)).all()
        houses = self.db.scalars(select(HouseModel).order_by(HouseModel.number)).all()
        aspects = self.db.scalars(
            select(AspectModel).order_by(AspectModel.angle, AspectModel.code)
        ).all()
        return {
            "version": model.version,
            "planets": [{"code": item.code, "name": item.name} for item in planets],
            "signs": [{"code": item.code, "name": item.name} for item in signs],
            "houses": [{"number": item.number, "name": item.name} for item in houses],
            "aspects": [
                {
                    "code": item.code,
                    "name": item.name,
                    "angle": item.angle,
                    "default_orb_deg": item.default_orb_deg,
                }
                for item in aspects
            ],
        }
