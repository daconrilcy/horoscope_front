"""Repository SQLAlchemy pour les donnees de reference astrologiques stables."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.prediction_reference import AstralAspectDefinitionModel
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

ASPECT_FAMILY_ROWS = ("major", "minor", "advanced")
ASPECT_ROWS = (
    ("conjunction", "Conjunction", 0.0, "major"),
    ("sextile", "Sextile", 60.0, "major"),
    ("square", "Square", 90.0, "major"),
    ("trine", "Trine", 120.0, "major"),
    ("opposition", "Opposition", 180.0, "major"),
    ("semi_sextile", "Semi-sextile", 30.0, "minor"),
    ("semi_square", "Semi-square", 45.0, "minor"),
    ("quintile", "Quintile", 72.0, "minor"),
    ("sesquiquadrate", "Sesquiquadrate", 135.0, "minor"),
    ("quincunx", "Quincunx", 150.0, "minor"),
    ("biquintile", "Biquintile", 144.0, "minor"),
    ("septile", "Septile", 51.428571, "advanced"),
    ("biseptile", "Biseptile", 102.857143, "advanced"),
    ("triseptile", "Triseptile", 154.285714, "advanced"),
    ("novile", "Novile", 40.0, "advanced"),
    ("binovile", "Binovile", 80.0, "advanced"),
    ("quadranovile", "Quadranovile", 160.0, "advanced"),
    ("decile", "Decile", 36.0, "advanced"),
    ("tredecile", "Tredecile", 108.0, "advanced"),
    ("quindecile", "Quindecile", 165.0, "advanced"),
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

    def has_complete_version_data(self) -> bool:
        """Indique si chaque table structurelle stable contient au moins une entree."""
        return all(
            self.db.scalar(select(model.id).limit(1)) is not None
            for model in (
                PlanetModel,
                AstralSignModel,
                HouseModel,
                AspectModel,
                AstralAspectFamilyModel,
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

        dignity_type_rows = [
            ("domicile", "Domicile"),
            ("detriment", "Detriment"),
            ("exaltation", "Exaltation"),
            ("fall", "Fall"),
        ]
        for code, name in dignity_type_rows:
            if (
                self.db.scalar(
                    select(AstralDignityTypeModel.id).where(AstralDignityTypeModel.code == code)
                )
                is None
            ):
                self.db.add(AstralDignityTypeModel(code=code, name=name))

        for name in ("traditional", "modern", "hellenistic", "medieval"):
            if (
                self.db.scalar(select(AstralSystemModel.id).where(AstralSystemModel.name == name))
                is None
            ):
                self.db.add(AstralSystemModel(name=name))

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

        for name in ASPECT_FAMILY_ROWS:
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

        for code, name, angle, family_name in ASPECT_ROWS:
            if self.db.scalar(select(AspectModel.id).where(AspectModel.code == code)) is None:
                self.db.add(
                    AspectModel(
                        code=code,
                        name=name,
                        angle=angle,
                        family=families[family_name],
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
        return {
            "version": model.version,
            "planets": [{"code": item.code, "name": item.name} for item in planets],
            "signs": [{"code": item.code, "name": item.name} for item in signs],
            "houses": [{"number": item.number, "name": item.name} for item in houses],
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
        }
