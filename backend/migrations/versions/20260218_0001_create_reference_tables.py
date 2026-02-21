"""create reference tables

Revision ID: 20260218_0001
Revises:
Create Date: 2026-02-18
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260218_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reference_versions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_reference_versions_version",
        "reference_versions",
        ["version"],
        unique=True,
    )

    op.create_table(
        "planets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("reference_version_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["reference_version_id"], ["reference_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference_version_id", "code"),
    )
    op.create_index(
        "ix_planets_reference_version_id",
        "planets",
        ["reference_version_id"],
        unique=False,
    )
    op.create_index("ix_planets_code", "planets", ["code"], unique=False)

    op.create_table(
        "signs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("reference_version_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["reference_version_id"], ["reference_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference_version_id", "code"),
    )
    op.create_index(
        "ix_signs_reference_version_id",
        "signs",
        ["reference_version_id"],
        unique=False,
    )
    op.create_index("ix_signs_code", "signs", ["code"], unique=False)

    op.create_table(
        "houses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("reference_version_id", sa.Integer(), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["reference_version_id"], ["reference_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference_version_id", "number"),
    )
    op.create_index(
        "ix_houses_reference_version_id",
        "houses",
        ["reference_version_id"],
        unique=False,
    )

    op.create_table(
        "aspects",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("reference_version_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("angle", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["reference_version_id"], ["reference_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference_version_id", "code"),
    )
    op.create_index(
        "ix_aspects_reference_version_id",
        "aspects",
        ["reference_version_id"],
        unique=False,
    )
    op.create_index("ix_aspects_code", "aspects", ["code"], unique=False)

    op.create_table(
        "astro_characteristics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("reference_version_id", sa.Integer(), nullable=False),
        sa.Column("entity_type", sa.String(length=32), nullable=False),
        sa.Column("entity_code", sa.String(length=64), nullable=False),
        sa.Column("trait", sa.String(length=64), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["reference_version_id"], ["reference_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "reference_version_id",
            "entity_type",
            "entity_code",
            "trait",
        ),
    )
    op.create_index(
        "ix_astro_characteristics_reference_version_id",
        "astro_characteristics",
        ["reference_version_id"],
        unique=False,
    )
    op.create_index(
        "ix_astro_characteristics_entity_type",
        "astro_characteristics",
        ["entity_type"],
        unique=False,
    )
    op.create_index(
        "ix_astro_characteristics_entity_code",
        "astro_characteristics",
        ["entity_code"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_astro_characteristics_entity_code", table_name="astro_characteristics")
    op.drop_index("ix_astro_characteristics_entity_type", table_name="astro_characteristics")
    op.drop_index(
        "ix_astro_characteristics_reference_version_id",
        table_name="astro_characteristics",
    )
    op.drop_table("astro_characteristics")

    op.drop_index("ix_aspects_code", table_name="aspects")
    op.drop_index("ix_aspects_reference_version_id", table_name="aspects")
    op.drop_table("aspects")

    op.drop_index("ix_houses_reference_version_id", table_name="houses")
    op.drop_table("houses")

    op.drop_index("ix_signs_code", table_name="signs")
    op.drop_index("ix_signs_reference_version_id", table_name="signs")
    op.drop_table("signs")

    op.drop_index("ix_planets_code", table_name="planets")
    op.drop_index("ix_planets_reference_version_id", table_name="planets")
    op.drop_table("planets")

    op.drop_index("ix_reference_versions_version", table_name="reference_versions")
    op.drop_table("reference_versions")
