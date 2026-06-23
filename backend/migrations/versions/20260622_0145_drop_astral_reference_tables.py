"""Supprime les référentiels astrologiques locaux Astral.

Revision ID: 20260622_0145
Revises: 20260622_0144
Create Date: 2026-06-22
"""

from __future__ import annotations

from alembic import op

revision = "20260622_0145"
down_revision = "20260622_0144"
branch_labels = None
depends_on = None

ASTRAL_REFERENCE_TABLES = (
    "astral_accidental_dignity_categories",
    "astral_accidental_dignity_condition_schemas",
    "astral_accidental_dignity_expression_tendencies",
    "astral_accidental_dignity_rules",
    "astral_accidental_dignity_score_weights",
    "astral_accidental_dignity_types",
    "astral_advanced_condition_score_profiles",
    "astral_advanced_condition_types",
    "astral_advanced_condition_weights",
    "astral_angle_points",
    "astral_aspect_definitions",
    "astral_aspect_families",
    "astral_aspect_interpretation_profile_translations",
    "astral_aspect_interpretation_profiles",
    "astral_aspect_orb_rules",
    "astral_aspect_profiles",
    "astral_aspect_translations",
    "astral_aspects",
    "astral_astrological_roles",
    "astral_calculation_types",
    "astral_condition_operators",
    "astral_constellations",
    "astral_decan_system_code",
    "astral_default_valence",
    "astral_diginity_score_profiles",
    "astral_dignity_functional_effects",
    "astral_dignity_intensity_effects",
    "astral_dignity_type",
    "astral_dominance_factor_types",
    "astral_dominance_score_profiles",
    "astral_dominance_score_weights",
    "astral_elements",
    "astral_essential_dignity_categories",
    "astral_essential_dignity_expression_tendencies",
    "astral_essential_dignity_rules",
    "astral_essential_dignity_score_weights",
    "astral_essential_dignity_types",
    "astral_face_decans",
    "astral_fixed_star_definitions",
    "astral_fixed_star_keyword_translations",
    "astral_fixed_star_keywords",
    "astral_fixed_stars",
    "astral_heliacal_conditions",
    "astral_hemispheres",
    "astral_horizon_positions",
    "astral_house_axis_definitions",
    "astral_house_axis_members",
    "astral_house_category_weights",
    "astral_house_interpretation_profile_translations",
    "astral_house_interpretation_profiles",
    "astral_house_modalities",
    "astral_house_systems",
    "astral_house_translations",
    "astral_houses",
    "astral_interpretation_adapter_rules",
    "astral_interpretation_signal_types",
    "astral_interpretation_themes",
    "astral_interpretive_valence",
    "astral_modalities",
    "astral_object_types",
    "astral_planet_category_weights",
    "astral_planet_condition_signal_profiles",
    "astral_planet_definitions",
    "astral_planet_interpretation_profile_translations",
    "astral_planet_interpretation_profiles",
    "astral_planet_motion_states",
    "astral_planet_natures",
    "astral_planet_sign_dignities",
    "astral_planet_translations",
    "astral_planets",
    "astral_point_aliases",
    "astral_point_calculation_variants",
    "astral_point_families",
    "astral_point_interpretation_keyword_translations",
    "astral_point_interpretation_keywords",
    "astral_point_interpretation_profile_translations",
    "astral_point_interpretation_profiles",
    "astral_points",
    "astral_polarities",
    "astral_prediction_daily_house_profiles",
    "astral_prediction_daily_planet_profiles",
    "astral_reference_epochs",
    "astral_reference_sources",
    "astral_reference_versions",
    "astral_ruler_assignments_role",
    "astral_sect",
    "astral_sign_fertility_classes",
    "astral_sign_form_classes",
    "astral_sign_genders",
    "astral_sign_profiles",
    "astral_sign_seasonal_quadrants",
    "astral_sign_translations",
    "astral_sign_voice_classes",
    "astral_signs",
    "astral_sources",
    "astral_speed",
    "astral_speed_relations",
    "astral_systems",
    "astral_term_bounds",
    "astral_term_system_code",
    "astral_triplicity_ruler_assignments",
    "astral_typical_polarities",
    "astral_zodiacal_reference_system_categories",
    "astral_zodiacal_reference_systems",
    "astro_points",
)


def upgrade() -> None:
    """Supprime les tables de référentiel astrologique encore présentes."""
    for table_name in ASTRAL_REFERENCE_TABLES:
        op.drop_table(table_name, if_exists=True)


def downgrade() -> None:
    """La purge des référentiels locaux est irréversible."""
    raise RuntimeError("Cannot downgrade local Astral reference table purge")
