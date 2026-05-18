"""Repository du referentiel astrologique runtime.

Le repository lit les models SQLAlchemy existants, appelle le mapper infra et
retourne un contrat domaine immutable complet pour le calcul natal.
"""

from __future__ import annotations

from collections.abc import Mapping

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.astrology.planet_catalog import planet_codes
from app.domain.astrology.runtime.runtime_reference import AstrologyRuntimeReference
from app.infra.db.models.prediction_reference import AstralPlanetSignDignityModel
from app.infra.db.models.reference import (
    AstralAnglePointModel,
    AstralAstrologicalRoleModel,
    AstralElementModel,
    AstralHouseSystemModel,
    AstralModalityModel,
    AstralPlanetDefinitionModel,
    AstralPointAliasModel,
    AstralPointCalculationVariantModel,
    AstralPointModel,
    AstralPolarityModel,
    AstralSignModel,
    AstralSignProfileModel,
    AstralSystemModel,
    LanguageModel,
    PlanetModel,
    ReferenceVersionModel,
)
from app.infra.db.repositories.astrology_runtime_reference_mapper import (
    AstrologyRuntimeReferenceMapper,
)
from app.infra.db.repositories.prediction_reference_repository import PredictionReferenceRepository
from app.infra.db.repositories.reference_repository import ReferenceRepository


class AstrologyRuntimeReferenceError(Exception):
    """Erreur bloquante de chargement ou d'integrite du referentiel runtime."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class AstrologyRuntimeReferenceRepository:
    """Charge et valide la photographie runtime astrologique depuis la DB."""

    _REQUIRED_PLANETS = frozenset(planet_codes())
    _REQUIRED_ANGLE_POINTS = frozenset({"asc", "dsc", "mc", "ic"})
    _REQUIRED_HOUSE_SYSTEMS = frozenset({"placidus", "whole_sign", "equal", "porphyry"})

    def __init__(
        self,
        db: Session,
        mapper: AstrologyRuntimeReferenceMapper | None = None,
    ) -> None:
        self.db = db
        self.mapper = mapper or AstrologyRuntimeReferenceMapper()

    def load(self, version: str) -> AstrologyRuntimeReference:
        """Charge le referentiel complet pour la version demandee."""
        version_model = self.db.scalar(
            select(ReferenceVersionModel).where(ReferenceVersionModel.version == version)
        )
        if version_model is None:
            raise AstrologyRuntimeReferenceError(
                code="reference_version_not_found",
                message="reference version not found",
                details={"version": version},
            )

        payload = ReferenceRepository(self.db).get_reference_data(version)
        payload["signs"] = list(self._load_sign_profiles())
        prediction_repo = PredictionReferenceRepository(self.db)
        try:
            runtime_reference = self.mapper.map_payload(
                reference_version_id=version_model.id,
                reference_version=version_model.version,
                payload=payload,
                dignities=self._load_dignities(),
                sign_rulerships=prediction_repo.get_sign_rulerships(),
                planet_definitions=self._load_planet_definitions(),
                angle_points=self._load_angle_points(),
                astral_points=self._load_astral_points(),
                house_systems=self._load_house_systems(),
            )
        except ValueError as error:
            raise AstrologyRuntimeReferenceError(
                code="invalid_astrology_runtime_reference",
                message="astrology runtime reference is invalid",
                details={"field": "sign_profiles", "reason": str(error)},
            ) from error
        self._validate(runtime_reference)
        return runtime_reference

    def _load_planet_definitions(self) -> dict[str, dict[str, object]]:
        """Charge les definitions structurelles des planetes."""
        rows = self.db.execute(
            select(
                PlanetModel.code,
                AstralAstrologicalRoleModel.code.label("body_class"),
                AstralPlanetDefinitionModel.is_luminary,
            )
            .join(
                AstralPlanetDefinitionModel,
                PlanetModel.id == AstralPlanetDefinitionModel.planet_id,
            )
            .join(
                AstralAstrologicalRoleModel,
                AstralPlanetDefinitionModel.astrological_role_id == AstralAstrologicalRoleModel.id,
            )
        ).all()
        return {
            row.code: {"body_class": row.body_class, "is_luminary": row.is_luminary} for row in rows
        }

    def _load_sign_profiles(self) -> tuple[dict[str, object], ...]:
        """Charge les signes avec profils structurels sans modifier le payload public."""
        rows = self.db.execute(
            select(
                AstralSignModel.code,
                AstralSignModel.name,
                AstralElementModel.code.label("element_code"),
                AstralModalityModel.code.label("modality_code"),
                AstralPolarityModel.code.label("polarity_code"),
            )
            .outerjoin(
                AstralSignProfileModel,
                AstralSignProfileModel.astral_sign_id == AstralSignModel.id,
            )
            .outerjoin(
                AstralElementModel,
                AstralSignProfileModel.astral_element_id == AstralElementModel.id,
            )
            .outerjoin(
                AstralModalityModel,
                AstralSignProfileModel.astral_modality_id == AstralModalityModel.id,
            )
            .outerjoin(
                AstralPolarityModel,
                AstralSignProfileModel.astral_polarity_id == AstralPolarityModel.id,
            )
            .order_by(AstralSignModel.id)
        ).all()
        return tuple(
            {
                "code": row.code,
                "name": row.name,
                "element": row.element_code,
                "modality": row.modality_code,
                "polarity": row.polarity_code,
            }
            for row in rows
        )

    def _load_dignities(self) -> tuple[dict[str, object], ...]:
        """Charge les dignites planetaires canoniques."""
        rows = self.db.execute(
            select(
                AstralPlanetSignDignityModel,
                PlanetModel.code.label("planet_code"),
                AstralSystemModel.name.label("system"),
            )
            .join(PlanetModel, AstralPlanetSignDignityModel.astral_planet_id == PlanetModel.id)
            .join(
                AstralSystemModel,
                AstralPlanetSignDignityModel.astral_system_id == AstralSystemModel.id,
            )
        ).all()
        result: list[Mapping[str, object]] = []
        for dignity, planet_code, system in rows:
            result.append(
                {
                    "sign_code": dignity.sign.code,
                    "planet_code": planet_code,
                    "dignity_type": dignity.dignity_type.code,
                    "system": system,
                    "weight": dignity.weight,
                    "is_primary": dignity.is_primary,
                }
            )
        return tuple(result)

    def _load_angle_points(self) -> tuple[dict[str, object], ...]:
        """Charge les points d'angle structurels."""
        rows = self.db.scalars(select(AstralAnglePointModel).order_by(AstralAnglePointModel.code))
        return tuple(
            {
                "code": row.code,
                "short_label": row.short_label,
                "full_name": row.full_name,
                "axis": row.axis,
                "associated_house": row.associated_house,
            }
            for row in rows
        )

    def _load_astral_points(self) -> tuple[dict[str, object], ...]:
        """Charge les points astraux, variantes et aliases depuis les tables canoniques."""
        point_rows = self.db.scalars(select(AstralPointModel).order_by(AstralPointModel.id)).all()
        variant_rows = self.db.scalars(
            select(AstralPointCalculationVariantModel).order_by(
                AstralPointCalculationVariantModel.astral_point_code,
                AstralPointCalculationVariantModel.id,
            )
        ).all()
        alias_rows = self.db.execute(
            select(AstralPointAliasModel, LanguageModel.code.label("language_code"))
            .join(LanguageModel, AstralPointAliasModel.language_id == LanguageModel.id)
            .order_by(
                AstralPointAliasModel.astral_point_code,
                AstralPointAliasModel.variant_code,
                AstralPointAliasModel.id,
            )
        ).all()
        engine_keys_by_variant = {
            (alias.astral_point_code, alias.variant_code): alias.engine_key
            for alias, _language_code in alias_rows
            if alias.variant_code is not None and alias.engine_key is not None
        }
        variants_by_point: dict[str, list[Mapping[str, object]]] = {}
        for variant in variant_rows:
            variants_by_point.setdefault(variant.astral_point_code, []).append(
                {
                    "variant_code": variant.variant_code,
                    "display_name": variant.display_name,
                    "calculation_mode": variant.calculation_mode,
                    "engine_key": engine_keys_by_variant.get(
                        (variant.astral_point_code, variant.variant_code)
                    ),
                    "is_default": variant.is_default,
                }
            )
        aliases_by_point: dict[str, list[Mapping[str, object]]] = {}
        for alias, language_code in alias_rows:
            aliases_by_point.setdefault(alias.astral_point_code, []).append(
                {
                    "alias": alias.alias,
                    "language_code": language_code,
                    "source": alias.source,
                    "variant_code": alias.variant_code,
                    "engine_key": alias.engine_key,
                    "is_primary": alias.is_primary,
                }
            )
        return tuple(
            {
                "code": row.code,
                "display_name": row.display_name,
                "family_code": row.point_family,
                "astronomical_type": row.astronomical_type,
                "is_physical_body": row.is_physical_body,
                "variants": variants_by_point.get(row.code, []),
                "aliases": aliases_by_point.get(row.code, []),
            }
            for row in point_rows
        )

    def _load_house_systems(self) -> tuple[dict[str, object], ...]:
        """Charge les systemes de maisons actifs ou supportes."""
        rows = self.db.scalars(
            select(AstralHouseSystemModel).order_by(AstralHouseSystemModel.sort_order)
        )
        return tuple(
            {"code": row.code, "name": row.name, "is_active": row.is_active} for row in rows
        )

    def _validate(self, reference: AstrologyRuntimeReference) -> None:
        """Valide l'integrite bloquante du referentiel runtime."""
        self._expect_count("signs", len(reference.signs.items), 12)
        self._expect_count("houses", len(reference.houses.items), 12)
        planet_codes = set(reference.planets.codes)
        sign_codes = set(reference.signs.codes)
        house_numbers = set(reference.houses.numbers)
        aspect_codes = {item.code for item in reference.aspects.items}
        system_codes = {item.code for item in reference.systems.items}
        point_codes = {item.code for item in reference.astral_points.items}
        angle_point_codes = {item.code for item in reference.angle_points.items}
        missing_planets = self._REQUIRED_PLANETS - set(reference.planets.codes)
        if missing_planets:
            self._raise_integrity("planets", f"missing:{','.join(sorted(missing_planets))}")
        self._reject_unknown_codes(
            ("planets", planet_codes),
            ("signs", sign_codes),
            ("aspects", aspect_codes),
            ("systems", system_codes),
        )
        self._validate_sign_profiles(reference)
        missing_angles = self._REQUIRED_ANGLE_POINTS - {
            item.code for item in reference.angle_points.items
        }
        if missing_angles:
            self._raise_integrity("angle_points", f"missing:{','.join(sorted(missing_angles))}")
        for angle_point in reference.angle_points.items:
            if angle_point.associated_house not in house_numbers:
                self._raise_integrity("angle_points", "orphan_house")
        active_house_systems = {
            item.code for item in reference.house_systems.items if item.is_active
        }
        missing_house_systems = self._REQUIRED_HOUSE_SYSTEMS - active_house_systems
        if missing_house_systems:
            self._raise_integrity(
                "house_systems",
                f"missing:{','.join(sorted(missing_house_systems))}",
            )
        if not reference.aspects.items:
            self._raise_integrity("aspects", "missing")
        if not reference.astral_points.items:
            self._raise_integrity("astral_points", "missing")
        for point in reference.astral_points.items:
            if not point.variants:
                self._raise_integrity("astral_points", f"missing_variant:{point.code}")
            if point.default_variant_code is None:
                self._raise_integrity("astral_points", f"missing_default_variant:{point.code}")
        if not reference.aspects.orb_rules:
            self._raise_integrity("aspect_orb_rules", "missing")
        for rule in reference.aspects.orb_rules:
            if rule.aspect_code not in aspect_codes:
                self._raise_integrity("aspect_orb_rules", f"orphan_aspect:{rule.aspect_code}")
            if rule.system_code not in system_codes:
                self._raise_integrity("aspect_orb_rules", f"orphan_system:{rule.system_code}")
            for field, code in (
                ("source_planet_code", rule.source_planet_code),
                ("target_planet_code", rule.target_planet_code),
            ):
                if code is not None and code not in planet_codes:
                    self._raise_integrity("aspect_orb_rules", f"orphan_{field}:{code}")
            for field, code in (
                ("source_point_code", rule.source_point_code),
                ("target_point_code", rule.target_point_code),
            ):
                if code is not None and code not in point_codes and code not in angle_point_codes:
                    self._raise_integrity("aspect_orb_rules", f"orphan_{field}:{code}")
        if not reference.dignities.sign_rulerships:
            self._raise_integrity("sign_rulerships", "missing")
        if len(reference.dignities.sign_rulerships) != 12:
            self._raise_integrity("sign_rulerships", "expected_12")
        for sign_code, planet_code in reference.dignities.sign_rulerships.items():
            if sign_code not in sign_codes:
                self._raise_integrity("sign_rulerships", f"orphan_sign:{sign_code}")
            if planet_code not in planet_codes:
                self._raise_integrity("sign_rulerships", f"orphan_planet:{planet_code}")
        for dignity in reference.dignities.items:
            if dignity.sign_code not in sign_codes:
                self._raise_integrity("dignities", f"orphan_sign:{dignity.sign_code}")
            if dignity.planet_code not in planet_codes:
                self._raise_integrity("dignities", f"orphan_planet:{dignity.planet_code}")
            if dignity.system not in system_codes:
                self._raise_integrity("dignities", f"orphan_system:{dignity.system}")
        for axis in reference.house_axes:
            if axis.house_number not in house_numbers or axis.opposite_house not in house_numbers:
                self._raise_integrity("house_axes", "orphan_house")

    def _validate_sign_profiles(self, reference: AstrologyRuntimeReference) -> None:
        """Verifie que chaque signe porte un profil structurel DB-backed."""
        for sign in reference.signs.items:
            for field_name in ("element", "modality", "polarity"):
                value = getattr(sign, field_name)
                if not value.strip():
                    self._raise_integrity("sign_profiles", f"missing_{field_name}:{sign.code}")
                if value.strip().lower() == "unknown":
                    self._raise_integrity("sign_profiles", f"unknown_{field_name}:{sign.code}")

    def _reject_unknown_codes(self, *groups: tuple[str, set[str]]) -> None:
        """Refuse les sentinelles `unknown` dans les codes runtime canoniques."""
        for field, codes in groups:
            if any(code.strip().lower() == "unknown" for code in codes):
                self._raise_integrity(field, "unknown_forbidden")

    def _expect_count(self, field: str, actual: int, expected: int) -> None:
        if actual != expected:
            self._raise_integrity(field, f"expected_{expected}_actual_{actual}")

    def _raise_integrity(self, field: str, reason: str) -> None:
        raise AstrologyRuntimeReferenceError(
            code="invalid_astrology_runtime_reference",
            message="astrology runtime reference is invalid",
            details={"field": field, "reason": reason},
        )
