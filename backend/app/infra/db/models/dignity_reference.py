"""Modèles SQLAlchemy des dignités astrologiques et de leurs résultats."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.datetime_provider import utc_now
from app.infra.db.base import Base
from app.infra.db.models.reference import AstralSystemModel


class AstralSourceModel(Base):
    """Source documentaire utilisée par les référentiels de dignités."""

    __tablename__ = "astral_sources"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    author: Mapped[str] = mapped_column(String(128), nullable=False)
    era: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_historical: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class AstralDignityFunctionalEffectModel(Base):
    """Effet fonctionnel partagé par les dignités essentielles et accidentelles."""

    __tablename__ = "astral_dignity_functional_effects"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class AstralDignityIntensityEffectModel(Base):
    """Intensité partagée par les dignités essentielles et accidentelles."""

    __tablename__ = "astral_dignity_intensity_effects"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class AstralEssentialDignityCategoryModel(Base):
    """Catégorie stable des dignités essentielles."""

    __tablename__ = "astral_essential_dignity_categories"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class AstralEssentialDignityExpressionTendencyModel(Base):
    """Tendance d'expression propre aux dignités essentielles."""

    __tablename__ = "astral_essential_dignity_expression_tendencies"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class AstralEssentialDignityTypeModel(Base):
    """Type canonique de dignité essentielle."""

    __tablename__ = "astral_essential_dignity_types"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("astral_essential_dignity_categories.id"), nullable=False, index=True
    )
    functional_effect_id: Mapped[int] = mapped_column(
        ForeignKey("astral_dignity_functional_effects.id"), nullable=False, index=True
    )
    expression_tendency_id: Mapped[int] = mapped_column(
        ForeignKey("astral_essential_dignity_expression_tendencies.id"),
        nullable=False,
        index=True,
    )
    intensity_effect_id: Mapped[int] = mapped_column(
        ForeignKey("astral_dignity_intensity_effects.id"), nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    category: Mapped["AstralEssentialDignityCategoryModel"] = relationship()
    functional_effect: Mapped["AstralDignityFunctionalEffectModel"] = relationship()
    expression_tendency: Mapped["AstralEssentialDignityExpressionTendencyModel"] = relationship()
    intensity_effect: Mapped["AstralDignityIntensityEffectModel"] = relationship()


class AstralAccidentalDignityCategoryModel(Base):
    """Catégorie stable des dignités accidentelles."""

    __tablename__ = "astral_accidental_dignity_categories"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class AstralAccidentalDignityExpressionTendencyModel(Base):
    """Tendance d'expression propre aux dignités accidentelles."""

    __tablename__ = "astral_accidental_dignity_expression_tendencies"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class AstralAccidentalDignityConditionSchemaModel(Base):
    """Schéma logique décrivant la forme du JSON de condition accidentelle."""

    __tablename__ = "astral_accidental_dignity_condition_schemas"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class AstralAccidentalDignityTypeModel(Base):
    """Type canonique de dignité accidentelle."""

    __tablename__ = "astral_accidental_dignity_types"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("astral_accidental_dignity_categories.id"), nullable=False, index=True
    )
    functional_effect_id: Mapped[int] = mapped_column(
        ForeignKey("astral_dignity_functional_effects.id"), nullable=False, index=True
    )
    expression_tendency_id: Mapped[int] = mapped_column(
        ForeignKey("astral_accidental_dignity_expression_tendencies.id"),
        nullable=False,
        index=True,
    )
    intensity_effect_id: Mapped[int] = mapped_column(
        ForeignKey("astral_dignity_intensity_effects.id"), nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    category: Mapped["AstralAccidentalDignityCategoryModel"] = relationship()
    functional_effect: Mapped["AstralDignityFunctionalEffectModel"] = relationship()
    expression_tendency: Mapped["AstralAccidentalDignityExpressionTendencyModel"] = relationship()
    intensity_effect: Mapped["AstralDignityIntensityEffectModel"] = relationship()


class AstralTermSystemCodeModel(Base):
    """Système de bornes de termes astrologiques."""

    __tablename__ = "astral_term_system_code"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class AstralDecanSystemCodeModel(Base):
    """Système de décans ou faces astrologiques."""

    __tablename__ = "astral_decan_system_code"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class AstralSectModel(Base):
    """Secte diurne, nocturne ou commune utilisée par les règles."""

    __tablename__ = "astral_sect"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class AstralRulerAssignmentsRoleModel(Base):
    """Rôle d'une planète dans une attribution de maîtrise."""

    __tablename__ = "astral_ruler_assignments_role"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class AstralPlanetMotionStateModel(Base):
    """État de mouvement planétaire utilisable dans les règles accidentelles."""

    __tablename__ = "astral_planet_motion_states"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class AstralSpeedRelationModel(Base):
    """Relation de vitesse planétaire par rapport à la moyenne."""

    __tablename__ = "astral_speed_relations"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class AstralHeliacalConditionModel(Base):
    """Condition héliaque relative au Soleil."""

    __tablename__ = "astral_heliacal_conditions"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class AstralHorizonPositionModel(Base):
    """Position d'un astre par rapport à l'horizon."""

    __tablename__ = "astral_horizon_positions"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class AstralSignGenderModel(Base):
    """Genre traditionnel associé aux signes dans certaines règles."""

    __tablename__ = "astral_sign_genders"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class AstralPlanetNatureModel(Base):
    """Nature bénéfique ou maléfique utilisée par les règles d'aspect."""

    __tablename__ = "astral_planet_natures"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class AstralConditionOperatorModel(Base):
    """Opérateur logique réutilisable dans les conditions JSON."""

    __tablename__ = "astral_condition_operators"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class AstralDiginityScoreProfileModel(Base):
    """Profil de scoring des dignités, orthographié comme la table source."""

    __tablename__ = "astral_diginity_score_profiles"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    astral_system_id: Mapped[int] = mapped_column(
        ForeignKey("astral_systems.id"), nullable=False, index=True
    )
    profile_family_source_id: Mapped[int] = mapped_column(
        ForeignKey("astral_sources.id"), nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    astral_system: Mapped["AstralSystemModel"] = relationship()
    profile_family_source: Mapped["AstralSourceModel"] = relationship()


class AstralTermBoundModel(Base):
    """Borne de terme pour un signe, un système et une planète."""

    __tablename__ = "astral_term_bounds"
    __table_args__ = (
        UniqueConstraint(
            "reference_version_id",
            "term_system_id",
            "sign_id",
            "order_index",
            name="uq_astral_term_bounds_scope",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    term_system_id: Mapped[int] = mapped_column(
        ForeignKey("astral_term_system_code.id"), nullable=False, index=True
    )
    sign_id: Mapped[int] = mapped_column(ForeignKey("astral_signs.id"), nullable=False, index=True)
    planet_id: Mapped[int] = mapped_column(
        ForeignKey("astral_planets.id"), nullable=False, index=True
    )
    degree_start: Mapped[float] = mapped_column(Float, nullable=False)
    degree_end: Mapped[float] = mapped_column(Float, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_versions.id"), nullable=False, index=True
    )


class AstralFaceDecanModel(Base):
    """Décan ou face planétaire pour un signe et un système."""

    __tablename__ = "astral_face_decans"
    __table_args__ = (
        UniqueConstraint(
            "reference_version_id",
            "decan_system_id",
            "sign_id",
            "decan_index",
            name="uq_astral_face_decans_scope",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    decan_system_id: Mapped[int] = mapped_column(
        ForeignKey("astral_decan_system_code.id"), nullable=False, index=True
    )
    sign_id: Mapped[int] = mapped_column(ForeignKey("astral_signs.id"), nullable=False, index=True)
    decan_index: Mapped[int] = mapped_column(Integer, nullable=False)
    degree_start: Mapped[float] = mapped_column(Float, nullable=False)
    degree_end: Mapped[float] = mapped_column(Float, nullable=False)
    planet_id: Mapped[int] = mapped_column(
        ForeignKey("astral_planets.id"), nullable=False, index=True
    )
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_versions.id"), nullable=False, index=True
    )


class AstralEssentialDignityRuleModel(Base):
    """Règle essentielle reliant planète, signe et type de dignité."""

    __tablename__ = "astral_essential_dignity_rules"
    __table_args__ = (
        UniqueConstraint(
            "reference_version_id",
            "astral_system_id",
            "planet_id",
            "sign_id",
            "essential_dignity_types_id",
            name="uq_astral_essential_dignity_rules_scope",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    planet_id: Mapped[int] = mapped_column(
        ForeignKey("astral_planets.id"), nullable=False, index=True
    )
    sign_id: Mapped[int] = mapped_column(ForeignKey("astral_signs.id"), nullable=False, index=True)
    essential_dignity_types_id: Mapped[int] = mapped_column(
        ForeignKey("astral_essential_dignity_types.id"), nullable=False, index=True
    )
    degree_start: Mapped[float] = mapped_column(Float, nullable=False)
    degree_end: Mapped[float] = mapped_column(Float, nullable=False)
    astral_system_id: Mapped[int] = mapped_column(
        ForeignKey("astral_systems.id"), nullable=False, index=True
    )
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_versions.id"), nullable=False, index=True
    )
    source_id: Mapped[int] = mapped_column(ForeignKey("astral_sources.id"), nullable=False)
    micro_note: Mapped[str] = mapped_column(Text, nullable=False)


class AstralTriplicityRulerAssignmentModel(Base):
    """Attribution de maître de triplicité par élément et secte."""

    __tablename__ = "astral_triplicity_ruler_assignments"
    __table_args__ = (
        UniqueConstraint(
            "reference_version_id",
            "element_id",
            "sect_id",
            "planet_id",
            "role_id",
            "astral_system_id",
            name="uq_astral_triplicity_ruler_assignments_scope",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    element_id: Mapped[int] = mapped_column(
        ForeignKey("astral_elements.id"), nullable=False, index=True
    )
    sect_id: Mapped[int] = mapped_column(ForeignKey("astral_sect.id"), nullable=False, index=True)
    planet_id: Mapped[int] = mapped_column(
        ForeignKey("astral_planets.id"), nullable=False, index=True
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("astral_ruler_assignments_role.id"), nullable=False, index=True
    )
    astral_system_id: Mapped[int] = mapped_column(
        ForeignKey("astral_systems.id"), nullable=False, index=True
    )
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_versions.id"), nullable=False, index=True
    )
    source_id: Mapped[int] = mapped_column(ForeignKey("astral_sources.id"), nullable=False)
    micro_note: Mapped[str] = mapped_column(Text, nullable=False)


class AstralEssentialDignityScoreWeightModel(Base):
    """Poids de scoring d'une dignité essentielle pour un profil."""

    __tablename__ = "astral_essential_dignity_score_weights"
    __table_args__ = (
        UniqueConstraint(
            "score_profile_id",
            "essential_dignity_types_id",
            name="uq_astral_essential_dignity_score_weights_scope",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    score_profile_id: Mapped[int] = mapped_column(
        ForeignKey("astral_diginity_score_profiles.id"), nullable=False, index=True
    )
    essential_dignity_types_id: Mapped[int] = mapped_column(
        ForeignKey("astral_essential_dignity_types.id"), nullable=False, index=True
    )
    score_value: Mapped[float] = mapped_column(Float, nullable=False)
    functional_weight: Mapped[float] = mapped_column(Float, nullable=False)
    expression_weight: Mapped[float] = mapped_column(Float, nullable=False)
    intensity_weight: Mapped[float] = mapped_column(Float, nullable=False)
    visibility_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    stability_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    coherence_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    support_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    constraint_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    notes: Mapped[str] = mapped_column(Text, nullable=False)


class AstralAccidentalDignityRuleModel(Base):
    """Règle accidentelle avec condition JSON normalisée par identifiants."""

    __tablename__ = "astral_accidental_dignity_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    accidental_dignity_type_id: Mapped[int] = mapped_column(
        ForeignKey("astral_accidental_dignity_types.id"), nullable=False, index=True
    )
    planet_id: Mapped[int | None] = mapped_column(
        ForeignKey("astral_planets.id"), nullable=True, index=True
    )
    condition_schema_id: Mapped[int] = mapped_column(
        ForeignKey("astral_accidental_dignity_condition_schemas.id"),
        nullable=False,
        index=True,
    )
    condition_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    astral_system_id: Mapped[int] = mapped_column(
        ForeignKey("astral_systems.id"), nullable=False, index=True
    )
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_versions.id"), nullable=False, index=True
    )
    micro_note: Mapped[str] = mapped_column(Text, nullable=False)


class AstralAccidentalDignityScoreWeightModel(Base):
    """Poids de scoring d'une dignité accidentelle pour un profil."""

    __tablename__ = "astral_accidental_dignity_score_weights"
    __table_args__ = (
        UniqueConstraint(
            "score_profile_id",
            "accidental_dignity_type_id",
            name="uq_astral_accidental_dignity_score_weights_scope",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    score_profile_id: Mapped[int] = mapped_column(
        ForeignKey("astral_diginity_score_profiles.id"), nullable=False, index=True
    )
    accidental_dignity_type_id: Mapped[int] = mapped_column(
        ForeignKey("astral_accidental_dignity_types.id"), nullable=False, index=True
    )
    score_value: Mapped[float] = mapped_column(Float, nullable=False)
    functional_weight: Mapped[float] = mapped_column(Float, nullable=False)
    expression_weight: Mapped[float] = mapped_column(Float, nullable=False)
    intensity_weight: Mapped[float] = mapped_column(Float, nullable=False)
    visibility_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    stability_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    coherence_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    support_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    constraint_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    notes: Mapped[str] = mapped_column(Text, nullable=False)


class AstralPlanetConditionSignalProfileModel(Base):
    """Profil referentiel versionne d'un signal de condition planetaire."""

    __tablename__ = "astral_planet_condition_signal_profiles"
    __table_args__ = (
        UniqueConstraint(
            "reference_version_id",
            "condition_axis",
            "signal_code",
            "signal_level",
            name="uq_astral_planet_condition_signal_profiles_scope",
        ),
        CheckConstraint(
            "level_min <= level_max",
            name="ck_astral_planet_condition_signal_profiles_range",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    condition_axis: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    level_min: Mapped[float] = mapped_column(Float, nullable=False)
    level_max: Mapped[float] = mapped_column(Float, nullable=False)
    signal_code: Mapped[str] = mapped_column(String(96), nullable=False, index=True)
    signal_label: Mapped[str] = mapped_column(String(128), nullable=False)
    signal_level: Mapped[str] = mapped_column(String(64), nullable=False)
    interpretation_use: Mapped[str] = mapped_column(String(128), nullable=False)
    priority_weight: Mapped[float] = mapped_column(Float, nullable=False)
    prompt_hint: Mapped[str] = mapped_column(String(160), nullable=False)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_versions.id"), nullable=False, index=True
    )


class AstralDominanceFactorTypeModel(Base):
    """Type de facteur factuel utilise par le moteur de dominance planetaire."""

    __tablename__ = "astral_dominance_factor_types"
    __table_args__ = (
        UniqueConstraint(
            "reference_version_id",
            "code",
            name="uq_astral_dominance_factor_types_scope",
        ),
        CheckConstraint(
            "default_weight >= 0",
            name="ck_astral_dominance_factor_types_weight",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    default_weight: Mapped[float] = mapped_column(Float, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_versions.id"), nullable=False, index=True
    )


class AstralChartPlanetDignityResultModel(Base):
    """Résultat runtime/audit du calcul de dignité d'une planète."""

    __tablename__ = "astral_chart_planet_dignity_results"
    __table_args__ = (
        UniqueConstraint(
            "chart_result_id",
            "planet_id",
            "score_profile_id",
            "reference_version_id",
            name="uq_astral_chart_planet_dignity_results_scope",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chart_result_id: Mapped[int] = mapped_column(
        ForeignKey("chart_results.id"), nullable=False, index=True
    )
    planet_id: Mapped[int] = mapped_column(
        ForeignKey("astral_planets.id"), nullable=False, index=True
    )
    score_profile_id: Mapped[int] = mapped_column(
        ForeignKey("astral_diginity_score_profiles.id"), nullable=False, index=True
    )
    astral_system_id: Mapped[int] = mapped_column(
        ForeignKey("astral_systems.id"), nullable=False, index=True
    )
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("astral_reference_versions.id"), nullable=False, index=True
    )
    essential_score: Mapped[float] = mapped_column(Float, nullable=False)
    accidental_score: Mapped[float] = mapped_column(Float, nullable=False)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    functional_strength_score: Mapped[float] = mapped_column(Float, nullable=False)
    expression_quality_score: Mapped[float] = mapped_column(Float, nullable=False)
    intensity_score: Mapped[float] = mapped_column(Float, nullable=False)
    essential_breakdown_json: Mapped[list[object]] = mapped_column(JSON, nullable=False)
    accidental_breakdown_json: Mapped[list[object]] = mapped_column(JSON, nullable=False)
    condition_summary_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    calculation_context_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
