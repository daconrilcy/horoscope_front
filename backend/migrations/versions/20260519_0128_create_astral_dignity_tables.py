"""Crée les tables de dignités astrologiques et de résultats runtime.

Revision ID: 20260519_0128
Revises: 20260518_0127
Create Date: 2026-05-19
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260519_0128"
down_revision: Union[str, Sequence[str], None] = "20260518_0127"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    """Indique si une table existe déjà dans le schéma courant."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _create_lookup_table(table_name: str, code_length: int = 64) -> None:
    """Crée une table de référentiel code/label/description si elle manque."""
    if _table_exists(table_name):
        return
    op.create_table(
        table_name,
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=code_length), nullable=False),
        sa.Column("label", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.UniqueConstraint("code", name=f"uq_{table_name}_code"),
    )
    op.create_index(f"ix_{table_name}_code", table_name, ["code"], unique=False)


def upgrade() -> None:
    """Crée le référentiel complet de dignités et la table d'audit runtime."""
    if not _table_exists("astral_sources"):
        op.create_table(
            "astral_sources",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("code", sa.String(length=64), nullable=False),
            sa.Column("label", sa.String(length=128), nullable=False),
            sa.Column("source_type", sa.String(length=64), nullable=False),
            sa.Column("author", sa.String(length=128), nullable=False),
            sa.Column("era", sa.String(length=64), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("url", sa.String(length=255), nullable=True),
            sa.Column("is_historical", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.UniqueConstraint("code", name="uq_astral_sources_code"),
        )
        op.create_index("ix_astral_sources_code", "astral_sources", ["code"], unique=False)

    for table_name in (
        "astral_dignity_functional_effects",
        "astral_dignity_intensity_effects",
        "astral_essential_dignity_categories",
        "astral_essential_dignity_expression_tendencies",
        "astral_accidental_dignity_categories",
        "astral_accidental_dignity_expression_tendencies",
        "astral_accidental_dignity_condition_schemas",
        "astral_term_system_code",
        "astral_decan_system_code",
        "astral_ruler_assignments_role",
        "astral_planet_motion_states",
        "astral_speed_relations",
        "astral_heliacal_conditions",
        "astral_horizon_positions",
        "astral_sign_genders",
        "astral_planet_natures",
        "astral_condition_operators",
    ):
        _create_lookup_table(table_name)
    _create_lookup_table("astral_sect", code_length=32)

    if not _table_exists("astral_essential_dignity_types"):
        op.create_table(
            "astral_essential_dignity_types",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("code", sa.String(length=64), nullable=False),
            sa.Column("label", sa.String(length=128), nullable=False),
            sa.Column("category_id", sa.Integer(), nullable=False),
            sa.Column("functional_effect_id", sa.Integer(), nullable=False),
            sa.Column("expression_tendency_id", sa.Integer(), nullable=False),
            sa.Column("intensity_effect_id", sa.Integer(), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("sort_order", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["category_id"], ["astral_essential_dignity_categories.id"]),
            sa.ForeignKeyConstraint(
                ["functional_effect_id"], ["astral_dignity_functional_effects.id"]
            ),
            sa.ForeignKeyConstraint(
                ["expression_tendency_id"],
                ["astral_essential_dignity_expression_tendencies.id"],
            ),
            sa.ForeignKeyConstraint(
                ["intensity_effect_id"], ["astral_dignity_intensity_effects.id"]
            ),
            sa.UniqueConstraint("code", name="uq_astral_essential_dignity_types_code"),
        )
        op.create_index(
            "ix_astral_essential_dignity_types_code",
            "astral_essential_dignity_types",
            ["code"],
        )

    if not _table_exists("astral_accidental_dignity_types"):
        op.create_table(
            "astral_accidental_dignity_types",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("code", sa.String(length=64), nullable=False),
            sa.Column("label", sa.String(length=128), nullable=False),
            sa.Column("category_id", sa.Integer(), nullable=False),
            sa.Column("functional_effect_id", sa.Integer(), nullable=False),
            sa.Column("expression_tendency_id", sa.Integer(), nullable=False),
            sa.Column("intensity_effect_id", sa.Integer(), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("sort_order", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["category_id"], ["astral_accidental_dignity_categories.id"]),
            sa.ForeignKeyConstraint(
                ["functional_effect_id"], ["astral_dignity_functional_effects.id"]
            ),
            sa.ForeignKeyConstraint(
                ["expression_tendency_id"],
                ["astral_accidental_dignity_expression_tendencies.id"],
            ),
            sa.ForeignKeyConstraint(
                ["intensity_effect_id"], ["astral_dignity_intensity_effects.id"]
            ),
            sa.UniqueConstraint("code", name="uq_astral_accidental_dignity_types_code"),
        )
        op.create_index(
            "ix_astral_accidental_dignity_types_code",
            "astral_accidental_dignity_types",
            ["code"],
        )

    if not _table_exists("astral_diginity_score_profiles"):
        op.create_table(
            "astral_diginity_score_profiles",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("code", sa.String(length=64), nullable=False),
            sa.Column("label", sa.String(length=128), nullable=False),
            sa.Column("astral_system_id", sa.Integer(), nullable=False),
            sa.Column("profile_family_source_id", sa.Integer(), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.ForeignKeyConstraint(["astral_system_id"], ["astral_systems.id"]),
            sa.ForeignKeyConstraint(["profile_family_source_id"], ["astral_sources.id"]),
            sa.UniqueConstraint("code", name="uq_astral_diginity_score_profiles_code"),
        )
        op.create_index(
            "ix_astral_diginity_score_profiles_code",
            "astral_diginity_score_profiles",
            ["code"],
        )

    if not _table_exists("astral_term_bounds"):
        op.create_table(
            "astral_term_bounds",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("term_system_id", sa.Integer(), nullable=False),
            sa.Column("sign_id", sa.Integer(), nullable=False),
            sa.Column("planet_id", sa.Integer(), nullable=False),
            sa.Column("degree_start", sa.Float(), nullable=False),
            sa.Column("degree_end", sa.Float(), nullable=False),
            sa.Column("order_index", sa.Integer(), nullable=False),
            sa.Column("reference_version_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["term_system_id"], ["astral_term_system_code.id"]),
            sa.ForeignKeyConstraint(["sign_id"], ["astral_signs.id"]),
            sa.ForeignKeyConstraint(["planet_id"], ["astral_planets.id"]),
            sa.ForeignKeyConstraint(["reference_version_id"], ["astral_reference_versions.id"]),
            sa.UniqueConstraint(
                "reference_version_id",
                "term_system_id",
                "sign_id",
                "order_index",
                name="uq_astral_term_bounds_scope",
            ),
        )

    if not _table_exists("astral_face_decans"):
        op.create_table(
            "astral_face_decans",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("decan_system_id", sa.Integer(), nullable=False),
            sa.Column("sign_id", sa.Integer(), nullable=False),
            sa.Column("decan_index", sa.Integer(), nullable=False),
            sa.Column("degree_start", sa.Float(), nullable=False),
            sa.Column("degree_end", sa.Float(), nullable=False),
            sa.Column("planet_id", sa.Integer(), nullable=False),
            sa.Column("reference_version_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["decan_system_id"], ["astral_decan_system_code.id"]),
            sa.ForeignKeyConstraint(["sign_id"], ["astral_signs.id"]),
            sa.ForeignKeyConstraint(["planet_id"], ["astral_planets.id"]),
            sa.ForeignKeyConstraint(["reference_version_id"], ["astral_reference_versions.id"]),
            sa.UniqueConstraint(
                "reference_version_id",
                "decan_system_id",
                "sign_id",
                "decan_index",
                name="uq_astral_face_decans_scope",
            ),
        )

    if not _table_exists("astral_essential_dignity_rules"):
        op.create_table(
            "astral_essential_dignity_rules",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("planet_id", sa.Integer(), nullable=False),
            sa.Column("sign_id", sa.Integer(), nullable=False),
            sa.Column("essential_dignity_types_id", sa.Integer(), nullable=False),
            sa.Column("degree_start", sa.Float(), nullable=False),
            sa.Column("degree_end", sa.Float(), nullable=False),
            sa.Column("astral_system_id", sa.Integer(), nullable=False),
            sa.Column("reference_version_id", sa.Integer(), nullable=False),
            sa.Column("source_id", sa.Integer(), nullable=False),
            sa.Column("micro_note", sa.Text(), nullable=False),
            sa.ForeignKeyConstraint(["planet_id"], ["astral_planets.id"]),
            sa.ForeignKeyConstraint(["sign_id"], ["astral_signs.id"]),
            sa.ForeignKeyConstraint(
                ["essential_dignity_types_id"], ["astral_essential_dignity_types.id"]
            ),
            sa.ForeignKeyConstraint(["astral_system_id"], ["astral_systems.id"]),
            sa.ForeignKeyConstraint(["reference_version_id"], ["astral_reference_versions.id"]),
            sa.ForeignKeyConstraint(["source_id"], ["astral_sources.id"]),
            sa.UniqueConstraint(
                "reference_version_id",
                "astral_system_id",
                "planet_id",
                "sign_id",
                "essential_dignity_types_id",
                name="uq_astral_essential_dignity_rules_scope",
            ),
        )

    if not _table_exists("astral_triplicity_ruler_assignments"):
        op.create_table(
            "astral_triplicity_ruler_assignments",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("element_id", sa.Integer(), nullable=False),
            sa.Column("sect_id", sa.Integer(), nullable=False),
            sa.Column("planet_id", sa.Integer(), nullable=False),
            sa.Column("role_id", sa.Integer(), nullable=False),
            sa.Column("astral_system_id", sa.Integer(), nullable=False),
            sa.Column("reference_version_id", sa.Integer(), nullable=False),
            sa.Column("source_id", sa.Integer(), nullable=False),
            sa.Column("micro_note", sa.Text(), nullable=False),
            sa.ForeignKeyConstraint(["element_id"], ["astral_elements.id"]),
            sa.ForeignKeyConstraint(["sect_id"], ["astral_sect.id"]),
            sa.ForeignKeyConstraint(["planet_id"], ["astral_planets.id"]),
            sa.ForeignKeyConstraint(["role_id"], ["astral_ruler_assignments_role.id"]),
            sa.ForeignKeyConstraint(["astral_system_id"], ["astral_systems.id"]),
            sa.ForeignKeyConstraint(["reference_version_id"], ["astral_reference_versions.id"]),
            sa.ForeignKeyConstraint(["source_id"], ["astral_sources.id"]),
            sa.UniqueConstraint(
                "reference_version_id",
                "element_id",
                "sect_id",
                "planet_id",
                "role_id",
                "astral_system_id",
                name="uq_astral_triplicity_ruler_assignments_scope",
            ),
        )

    if not _table_exists("astral_essential_dignity_score_weights"):
        op.create_table(
            "astral_essential_dignity_score_weights",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("score_profile_id", sa.Integer(), nullable=False),
            sa.Column("essential_dignity_types_id", sa.Integer(), nullable=False),
            sa.Column("score_value", sa.Float(), nullable=False),
            sa.Column("functional_weight", sa.Float(), nullable=False),
            sa.Column("expression_weight", sa.Float(), nullable=False),
            sa.Column("intensity_weight", sa.Float(), nullable=False),
            sa.Column("notes", sa.Text(), nullable=False),
            sa.ForeignKeyConstraint(["score_profile_id"], ["astral_diginity_score_profiles.id"]),
            sa.ForeignKeyConstraint(
                ["essential_dignity_types_id"], ["astral_essential_dignity_types.id"]
            ),
            sa.UniqueConstraint(
                "score_profile_id",
                "essential_dignity_types_id",
                name="uq_astral_essential_dignity_score_weights_scope",
            ),
        )

    if not _table_exists("astral_accidental_dignity_rules"):
        op.create_table(
            "astral_accidental_dignity_rules",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("accidental_dignity_type_id", sa.Integer(), nullable=False),
            sa.Column("planet_id", sa.Integer(), nullable=True),
            sa.Column("condition_schema_id", sa.Integer(), nullable=False),
            sa.Column("condition_json", sa.JSON(), nullable=False),
            sa.Column("astral_system_id", sa.Integer(), nullable=False),
            sa.Column("reference_version_id", sa.Integer(), nullable=False),
            sa.Column("micro_note", sa.Text(), nullable=False),
            sa.ForeignKeyConstraint(
                ["accidental_dignity_type_id"], ["astral_accidental_dignity_types.id"]
            ),
            sa.ForeignKeyConstraint(["planet_id"], ["astral_planets.id"]),
            sa.ForeignKeyConstraint(
                ["condition_schema_id"], ["astral_accidental_dignity_condition_schemas.id"]
            ),
            sa.ForeignKeyConstraint(["astral_system_id"], ["astral_systems.id"]),
            sa.ForeignKeyConstraint(["reference_version_id"], ["astral_reference_versions.id"]),
        )

    if not _table_exists("astral_accidental_dignity_score_weights"):
        op.create_table(
            "astral_accidental_dignity_score_weights",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("score_profile_id", sa.Integer(), nullable=False),
            sa.Column("accidental_dignity_type_id", sa.Integer(), nullable=False),
            sa.Column("score_value", sa.Float(), nullable=False),
            sa.Column("functional_weight", sa.Float(), nullable=False),
            sa.Column("expression_weight", sa.Float(), nullable=False),
            sa.Column("intensity_weight", sa.Float(), nullable=False),
            sa.Column("notes", sa.Text(), nullable=False),
            sa.ForeignKeyConstraint(["score_profile_id"], ["astral_diginity_score_profiles.id"]),
            sa.ForeignKeyConstraint(
                ["accidental_dignity_type_id"], ["astral_accidental_dignity_types.id"]
            ),
            sa.UniqueConstraint(
                "score_profile_id",
                "accidental_dignity_type_id",
                name="uq_astral_accidental_dignity_score_weights_scope",
            ),
        )

    if not _table_exists("astral_chart_planet_dignity_results"):
        op.create_table(
            "astral_chart_planet_dignity_results",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("chart_result_id", sa.Integer(), nullable=False),
            sa.Column("planet_id", sa.Integer(), nullable=False),
            sa.Column("score_profile_id", sa.Integer(), nullable=False),
            sa.Column("astral_system_id", sa.Integer(), nullable=False),
            sa.Column("reference_version_id", sa.Integer(), nullable=False),
            sa.Column("essential_score", sa.Float(), nullable=False),
            sa.Column("accidental_score", sa.Float(), nullable=False),
            sa.Column("total_score", sa.Float(), nullable=False),
            sa.Column("functional_strength_score", sa.Float(), nullable=False),
            sa.Column("expression_quality_score", sa.Float(), nullable=False),
            sa.Column("intensity_score", sa.Float(), nullable=False),
            sa.Column("essential_breakdown_json", sa.JSON(), nullable=False),
            sa.Column("accidental_breakdown_json", sa.JSON(), nullable=False),
            sa.Column("condition_summary_json", sa.JSON(), nullable=False),
            sa.Column("calculation_context_json", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["chart_result_id"], ["chart_results.id"]),
            sa.ForeignKeyConstraint(["planet_id"], ["astral_planets.id"]),
            sa.ForeignKeyConstraint(["score_profile_id"], ["astral_diginity_score_profiles.id"]),
            sa.ForeignKeyConstraint(["astral_system_id"], ["astral_systems.id"]),
            sa.ForeignKeyConstraint(["reference_version_id"], ["astral_reference_versions.id"]),
            sa.UniqueConstraint(
                "chart_result_id",
                "planet_id",
                "score_profile_id",
                "reference_version_id",
                name="uq_astral_chart_planet_dignity_results_scope",
            ),
        )


def downgrade() -> None:
    """Supprime les tables créées pour les dignités astrologiques."""
    for table_name in (
        "astral_chart_planet_dignity_results",
        "astral_accidental_dignity_score_weights",
        "astral_accidental_dignity_rules",
        "astral_essential_dignity_score_weights",
        "astral_triplicity_ruler_assignments",
        "astral_essential_dignity_rules",
        "astral_face_decans",
        "astral_term_bounds",
        "astral_diginity_score_profiles",
        "astral_accidental_dignity_types",
        "astral_essential_dignity_types",
        "astral_condition_operators",
        "astral_planet_natures",
        "astral_sign_genders",
        "astral_horizon_positions",
        "astral_heliacal_conditions",
        "astral_speed_relations",
        "astral_planet_motion_states",
        "astral_ruler_assignments_role",
        "astral_sect",
        "astral_decan_system_code",
        "astral_term_system_code",
        "astral_accidental_dignity_condition_schemas",
        "astral_accidental_dignity_expression_tendencies",
        "astral_accidental_dignity_categories",
        "astral_essential_dignity_expression_tendencies",
        "astral_essential_dignity_categories",
        "astral_dignity_intensity_effects",
        "astral_dignity_functional_effects",
        "astral_sources",
    ):
        if _table_exists(table_name):
            op.drop_table(table_name)
