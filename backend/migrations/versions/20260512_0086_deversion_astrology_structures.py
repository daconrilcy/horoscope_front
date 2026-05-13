"""deversion astrology structure tables

Revision ID: 20260512_0086
Revises: 20260512_0085
Create Date: 2026-05-12
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260512_0086"
down_revision: Union[str, Sequence[str], None] = "20260512_0085"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _drop_index_if_exists(index_name: str, table_name: str) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    indexes = {index["name"] for index in inspector.get_indexes(table_name)}
    if index_name in indexes:
        op.drop_index(index_name, table_name=table_name)


def _add_version_column(table_name: str) -> None:
    op.add_column(table_name, sa.Column("reference_version_id", sa.Integer(), nullable=True))
    op.create_index(
        op.f(f"ix_{table_name}_reference_version_id"),
        table_name,
        ["reference_version_id"],
        unique=False,
    )


def _backfill_profile_versions() -> None:
    op.execute(
        """
        UPDATE planet_profiles
        SET reference_version_id = (
            SELECT planets.reference_version_id
            FROM planets
            WHERE planets.id = planet_profiles.planet_id
        )
        """
    )
    op.execute(
        """
        UPDATE house_profiles
        SET reference_version_id = (
            SELECT houses.reference_version_id
            FROM houses
            WHERE houses.id = house_profiles.house_id
        )
        """
    )
    op.execute(
        """
        UPDATE aspect_profiles
        SET reference_version_id = (
            SELECT aspects.reference_version_id
            FROM aspects
            WHERE aspects.id = aspect_profiles.aspect_id
        )
        """
    )


def _backfill_weight_versions() -> None:
    for table_name in (
        "planet_category_weights",
        "house_category_weights",
        "point_category_weights",
    ):
        op.execute(
            f"""
            UPDATE {table_name}
            SET reference_version_id = (
                SELECT prediction_categories.reference_version_id
                FROM prediction_categories
                WHERE prediction_categories.id = {table_name}.category_id
            )
            """
        )


def _fill_missing_version_ids() -> None:
    for table_name in (
        "planet_profiles",
        "house_profiles",
        "aspect_profiles",
        "planet_category_weights",
        "house_category_weights",
        "point_category_weights",
    ):
        op.execute(
            f"""
            UPDATE {table_name}
            SET reference_version_id = (
                SELECT MIN(id) FROM reference_versions
            )
            WHERE reference_version_id IS NULL
            """
        )


def _canonicalize_foreign_keys() -> None:
    remaps = (
        ("planet_profiles", "planet_id", "planets", "code"),
        ("planet_category_weights", "planet_id", "planets", "code"),
        ("sign_rulerships", "planet_id", "planets", "code"),
        ("house_profiles", "house_id", "houses", "number"),
        ("house_category_weights", "house_id", "houses", "number"),
        ("sign_rulerships", "sign_id", "signs", "code"),
        ("aspect_profiles", "aspect_id", "aspects", "code"),
        ("point_category_weights", "point_id", "astro_points", "code"),
    )
    for source_table, source_column, target_table, business_key in remaps:
        op.execute(
            f"""
            UPDATE {source_table}
            SET {source_column} = (
                SELECT MIN(canonical.id)
                FROM {target_table} AS canonical
                WHERE canonical.{business_key} = (
                    SELECT current_row.{business_key}
                    FROM {target_table} AS current_row
                    WHERE current_row.id = {source_table}.{source_column}
                )
            )
            """
        )


def _delete_duplicate_structures() -> None:
    duplicate_specs = (
        ("planets", "code"),
        ("signs", "code"),
        ("houses", "number"),
        ("aspects", "code"),
        ("astro_points", "code"),
    )
    for table_name, business_key in duplicate_specs:
        op.execute(
            f"""
            DELETE FROM {table_name}
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM {table_name}
                GROUP BY {business_key}
            )
            """
        )


def _deauthorize_structure_table(table_name: str, business_key: str) -> None:
    _drop_index_if_exists(f"ix_{table_name}_reference_version_id", table_name)
    with op.batch_alter_table(table_name, recreate="always") as batch_op:
        batch_op.drop_column("reference_version_id")
        batch_op.create_unique_constraint(f"uq_{table_name}_{business_key}", [business_key])


def _version_parametric_table(
    table_name: str,
    unique_columns: list[str],
    *,
    drop_unique_index: str | None = None,
    drop_unique_constraint: str | None = None,
) -> None:
    if drop_unique_index is not None:
        _drop_index_if_exists(drop_unique_index, table_name)
    with op.batch_alter_table(table_name, recreate="always") as batch_op:
        if drop_unique_constraint is not None:
            batch_op.drop_constraint(drop_unique_constraint, type_="unique")
        batch_op.alter_column("reference_version_id", nullable=False)
        batch_op.create_foreign_key(
            f"fk_{table_name}_reference_version_id",
            "reference_versions",
            ["reference_version_id"],
            ["id"],
        )
        batch_op.create_unique_constraint(
            f"uq_{table_name}_{'_'.join(unique_columns)}",
            unique_columns,
        )
    if drop_unique_index is not None:
        indexed_column = unique_columns[1]
        op.create_index(drop_unique_index, table_name, [indexed_column], unique=False)


def upgrade() -> None:
    """Separe le vocabulaire stable des parametrages versionnes."""
    for table_name in (
        "planet_profiles",
        "house_profiles",
        "aspect_profiles",
        "planet_category_weights",
        "house_category_weights",
        "point_category_weights",
    ):
        _add_version_column(table_name)

    _backfill_profile_versions()
    _backfill_weight_versions()
    _fill_missing_version_ids()
    _canonicalize_foreign_keys()
    _delete_duplicate_structures()

    _deauthorize_structure_table("planets", "code")
    _deauthorize_structure_table("signs", "code")
    _deauthorize_structure_table("houses", "number")
    _deauthorize_structure_table("aspects", "code")
    _deauthorize_structure_table("astro_points", "code")

    _version_parametric_table(
        "planet_profiles",
        ["reference_version_id", "planet_id"],
        drop_unique_index=op.f("ix_planet_profiles_planet_id"),
        drop_unique_constraint="uq_planet_profiles_planet_id",
    )
    _version_parametric_table(
        "house_profiles",
        ["reference_version_id", "house_id"],
        drop_unique_index=op.f("ix_house_profiles_house_id"),
        drop_unique_constraint="uq_house_profiles_house_id",
    )
    _version_parametric_table(
        "aspect_profiles",
        ["reference_version_id", "aspect_id"],
        drop_unique_index=op.f("ix_aspect_profiles_aspect_id"),
        drop_unique_constraint="uq_aspect_profiles_aspect_id",
    )
    _version_parametric_table(
        "planet_category_weights",
        ["reference_version_id", "planet_id", "category_id"],
        drop_unique_constraint="uq_planet_category_weights_planet_id_category_id",
    )
    _version_parametric_table(
        "house_category_weights",
        ["reference_version_id", "house_id", "category_id"],
        drop_unique_constraint="uq_house_category_weights_house_id_category_id",
    )
    _version_parametric_table(
        "point_category_weights",
        ["reference_version_id", "point_id", "category_id"],
        drop_unique_constraint="uq_point_category_weights_point_id_category_id",
    )


def downgrade() -> None:
    """Rattache les structures au premier snapshot pour rollback."""
    op.add_column("planets", sa.Column("reference_version_id", sa.Integer(), nullable=True))
    op.add_column("signs", sa.Column("reference_version_id", sa.Integer(), nullable=True))
    op.add_column("houses", sa.Column("reference_version_id", sa.Integer(), nullable=True))
    op.add_column("aspects", sa.Column("reference_version_id", sa.Integer(), nullable=True))
    op.add_column("astro_points", sa.Column("reference_version_id", sa.Integer(), nullable=True))
    for table_name in ("planets", "signs", "houses", "aspects", "astro_points"):
        op.execute(
            f"""
            UPDATE {table_name}
            SET reference_version_id = (
                SELECT MIN(id) FROM reference_versions
            )
            WHERE reference_version_id IS NULL
            """
        )
        with op.batch_alter_table(table_name, recreate="always") as batch_op:
            batch_op.alter_column("reference_version_id", nullable=False)
            batch_op.create_foreign_key(
                f"fk_{table_name}_reference_version_id",
                "reference_versions",
                ["reference_version_id"],
                ["id"],
            )
        op.create_index(
            f"ix_{table_name}_reference_version_id",
            table_name,
            ["reference_version_id"],
            unique=False,
        )

    for table_name in (
        "planet_profiles",
        "house_profiles",
        "aspect_profiles",
        "planet_category_weights",
        "house_category_weights",
        "point_category_weights",
    ):
        _drop_index_if_exists(f"ix_{table_name}_reference_version_id", table_name)
        with op.batch_alter_table(table_name, recreate="always") as batch_op:
            batch_op.drop_column("reference_version_id")
