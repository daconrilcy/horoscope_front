"""migration a prediction reference tables

Revision ID: 20260307_0032
Revises: 20260307_0031
Create Date: 2026-03-07
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260307_0032"
down_revision: Union[str, Sequence[str], None] = "20260307_0031"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. prediction_categories
    op.create_table(
        "prediction_categories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("reference_version_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("display_name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_public", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.ForeignKeyConstraint(["reference_version_id"], ["reference_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference_version_id", "code"),
    )
    op.create_index(
        op.f("ix_prediction_categories_reference_version_id"),
        "prediction_categories",
        ["reference_version_id"],
        unique=False,
    )

    # 2. planet_profiles
    op.create_table(
        "planet_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("planet_id", sa.Integer(), nullable=False),
        sa.Column("class_code", sa.String(length=32), nullable=False),
        sa.Column("speed_rank", sa.Integer(), server_default="0", nullable=False),
        sa.Column("speed_class", sa.String(length=16), nullable=False),
        sa.Column("weight_intraday", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("weight_day_climate", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("typical_polarity", sa.String(length=16), nullable=True),
        sa.Column("orb_active_deg", sa.Float(), nullable=True),
        sa.Column("orb_peak_deg", sa.Float(), nullable=True),
        sa.Column("keywords_json", sa.Text(), nullable=True),
        sa.Column("micro_note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["planet_id"], ["planets.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("planet_id"),
    )
    op.create_index(
        op.f("ix_planet_profiles_planet_id"),
        "planet_profiles",
        ["planet_id"],
        unique=True,
    )

    # 3. house_profiles
    op.create_table(
        "house_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("house_id", sa.Integer(), nullable=False),
        sa.Column("house_kind", sa.String(length=16), nullable=False),
        sa.Column("visibility_weight", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("base_priority", sa.Integer(), server_default="0", nullable=False),
        sa.Column("keywords_json", sa.Text(), nullable=True),
        sa.Column("micro_note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["house_id"], ["houses.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("house_id"),
    )
    op.create_index(
        op.f("ix_house_profiles_house_id"),
        "house_profiles",
        ["house_id"],
        unique=True,
    )

    # 4. planet_category_weights
    op.create_table(
        "planet_category_weights",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("planet_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column(
            "influence_role", sa.String(length=16), server_default="secondary", nullable=False
        ),
        sa.ForeignKeyConstraint(["category_id"], ["prediction_categories.id"]),
        sa.ForeignKeyConstraint(["planet_id"], ["planets.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("planet_id", "category_id"),
    )
    op.create_index(
        op.f("ix_planet_category_weights_category_id"),
        "planet_category_weights",
        ["category_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_planet_category_weights_planet_id"),
        "planet_category_weights",
        ["planet_id"],
        unique=False,
    )

    # 5. house_category_weights
    op.create_table(
        "house_category_weights",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("house_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("routing_role", sa.String(length=16), server_default="secondary", nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["prediction_categories.id"]),
        sa.ForeignKeyConstraint(["house_id"], ["houses.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("house_id", "category_id"),
    )
    op.create_index(
        op.f("ix_house_category_weights_category_id"),
        "house_category_weights",
        ["category_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_house_category_weights_house_id"),
        "house_category_weights",
        ["house_id"],
        unique=False,
    )

    # 6. astro_points
    op.create_table(
        "astro_points",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("reference_version_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("point_type", sa.String(length=32), server_default="angle", nullable=False),
        sa.Column("is_enabled", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.ForeignKeyConstraint(["reference_version_id"], ["reference_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference_version_id", "code"),
    )
    op.create_index(
        op.f("ix_astro_points_reference_version_id"),
        "astro_points",
        ["reference_version_id"],
        unique=False,
    )

    # 7. point_category_weights
    op.create_table(
        "point_category_weights",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("point_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["prediction_categories.id"]),
        sa.ForeignKeyConstraint(["point_id"], ["astro_points.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("point_id", "category_id"),
    )
    op.create_index(
        op.f("ix_point_category_weights_category_id"),
        "point_category_weights",
        ["category_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_point_category_weights_point_id"),
        "point_category_weights",
        ["point_id"],
        unique=False,
    )

    # 8. sign_rulerships
    op.create_table(
        "sign_rulerships",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("reference_version_id", sa.Integer(), nullable=False),
        sa.Column("sign_id", sa.Integer(), nullable=False),
        sa.Column("planet_id", sa.Integer(), nullable=False),
        sa.Column(
            "rulership_type", sa.String(length=32), server_default="domicile", nullable=False
        ),
        sa.Column("weight", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("is_primary", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.ForeignKeyConstraint(["planet_id"], ["planets.id"]),
        sa.ForeignKeyConstraint(["reference_version_id"], ["reference_versions.id"]),
        sa.ForeignKeyConstraint(["sign_id"], ["signs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference_version_id", "sign_id", "planet_id", "rulership_type"),
    )
    op.create_index(
        op.f("ix_sign_rulerships_planet_id"),
        "sign_rulerships",
        ["planet_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_sign_rulerships_reference_version_id"),
        "sign_rulerships",
        ["reference_version_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_sign_rulerships_sign_id"),
        "sign_rulerships",
        ["sign_id"],
        unique=False,
    )

    # 9. aspect_profiles
    op.create_table(
        "aspect_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("aspect_id", sa.Integer(), nullable=False),
        sa.Column("intensity_weight", sa.Float(), server_default="1.0", nullable=False),
        sa.Column(
            "default_valence", sa.String(length=16), server_default="contextual", nullable=False
        ),
        sa.Column("orb_multiplier", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("phase_sensitive", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("micro_note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["aspect_id"], ["aspects.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("aspect_id"),
    )
    op.create_index(
        op.f("ix_aspect_profiles_aspect_id"),
        "aspect_profiles",
        ["aspect_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_aspect_profiles_aspect_id"), table_name="aspect_profiles")
    op.drop_table("aspect_profiles")
    op.drop_index(op.f("ix_sign_rulerships_sign_id"), table_name="sign_rulerships")
    op.drop_index(op.f("ix_sign_rulerships_reference_version_id"), table_name="sign_rulerships")
    op.drop_index(op.f("ix_sign_rulerships_planet_id"), table_name="sign_rulerships")
    op.drop_table("sign_rulerships")
    op.drop_index(op.f("ix_point_category_weights_point_id"), table_name="point_category_weights")
    op.drop_index(
        op.f("ix_point_category_weights_category_id"),
        table_name="point_category_weights",
    )
    op.drop_table("point_category_weights")
    op.drop_index(op.f("ix_astro_points_reference_version_id"), table_name="astro_points")
    op.drop_table("astro_points")
    op.drop_index(
        op.f("ix_house_category_weights_house_id"),
        table_name="house_category_weights",
    )
    op.drop_index(
        op.f("ix_house_category_weights_category_id"),
        table_name="house_category_weights",
    )
    op.drop_table("house_category_weights")
    op.drop_index(
        op.f("ix_planet_category_weights_planet_id"),
        table_name="planet_category_weights",
    )
    op.drop_index(
        op.f("ix_planet_category_weights_category_id"),
        table_name="planet_category_weights",
    )
    op.drop_table("planet_category_weights")
    op.drop_index(op.f("ix_house_profiles_house_id"), table_name="house_profiles")
    op.drop_table("house_profiles")
    op.drop_index(op.f("ix_planet_profiles_planet_id"), table_name="planet_profiles")
    op.drop_table("planet_profiles")
    op.drop_index(
        op.f("ix_prediction_categories_reference_version_id"), table_name="prediction_categories"
    )
    op.drop_table("prediction_categories")
