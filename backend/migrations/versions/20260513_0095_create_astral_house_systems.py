"""Crée le référentiel canonique des systèmes de maisons astrales.

Revision ID: 20260513_0095
Revises: 20260513_0094
Create Date: 2026-05-13
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260513_0095"
down_revision: Union[str, Sequence[str], None] = "20260513_0094"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

HOUSE_SYSTEM_ROWS = (
    {
        "code": "placidus",
        "name": "Placidus",
        "description": (
            "Quadrant house system widely used in modern Western astrology. Houses are "
            "calculated from time-based divisions of the diurnal arc."
        ),
        "astronomical_family": "quadrant",
        "supports_polar_regions": False,
        "is_quadrant_based": True,
        "requires_precise_birth_time": True,
        "sort_order": 10,
    },
    {
        "code": "whole_sign",
        "name": "Whole Sign",
        "description": (
            "Ancient house system where each house corresponds to one full zodiac sign, "
            "starting from the Ascendant sign."
        ),
        "astronomical_family": "sign_based",
        "supports_polar_regions": True,
        "is_quadrant_based": False,
        "requires_precise_birth_time": False,
        "sort_order": 20,
    },
    {
        "code": "equal",
        "name": "Equal House",
        "description": (
            "House system where all houses are exactly 30 degrees, starting from the "
            "Ascendant degree."
        ),
        "astronomical_family": "ascendant_based",
        "supports_polar_regions": True,
        "is_quadrant_based": False,
        "requires_precise_birth_time": True,
        "sort_order": 30,
    },
    {
        "code": "porphyry",
        "name": "Porphyry",
        "description": (
            "Quadrant house system dividing each quadrant between Ascendant, Midheaven, "
            "Descendant and Imum Coeli into three equal parts."
        ),
        "astronomical_family": "quadrant",
        "supports_polar_regions": True,
        "is_quadrant_based": True,
        "requires_precise_birth_time": True,
        "sort_order": 40,
    },
)


def _house_system_id_subquery(code_column: str) -> str:
    """Construit la sous-requête SQL de résolution d'un code historique."""
    return f"(SELECT id FROM astral_house_systems WHERE astral_house_systems.code = {code_column})"


def _table_exists(table_name: str) -> bool:
    """Vérifie si une table existe pour rendre la migration reprenable."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _index_exists(table_name: str, index_name: str) -> bool:
    """Vérifie si un index existe déjà sur une table."""
    if not _table_exists(table_name):
        return False
    indexes = sa.inspect(op.get_bind()).get_indexes(table_name)
    return index_name in {index["name"] for index in indexes}


def _column_exists(table_name: str, column_name: str) -> bool:
    """Vérifie si une colonne existe déjà sur une table."""
    if not _table_exists(table_name):
        return False
    columns = sa.inspect(op.get_bind()).get_columns(table_name)
    return column_name in {column["name"] for column in columns}


def _seed_house_systems() -> None:
    """Injecte les systèmes manquants sans dupliquer les lignes existantes."""
    bind = op.get_bind()
    for row in HOUSE_SYSTEM_ROWS:
        bind.execute(
            sa.text(
                """
                INSERT INTO astral_house_systems (
                    code,
                    name,
                    description,
                    astronomical_family,
                    supports_polar_regions,
                    is_quadrant_based,
                    requires_precise_birth_time,
                    sort_order,
                    is_active,
                    created_at,
                    updated_at
                )
                SELECT
                    :code,
                    :name,
                    :description,
                    :astronomical_family,
                    :supports_polar_regions,
                    :is_quadrant_based,
                    :requires_precise_birth_time,
                    :sort_order,
                    1,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                WHERE NOT EXISTS (
                    SELECT 1 FROM astral_house_systems WHERE code = :code
                )
                """
            ),
            row,
        )


def upgrade() -> None:
    """Crée le référentiel et remplace les codes runtime par des clés étrangères."""
    if not _table_exists("astral_house_systems"):
        op.create_table(
            "astral_house_systems",
            sa.Column(
                "id",
                sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                sa.Identity(always=True),
                primary_key=True,
            ),
            sa.Column("code", sa.String(length=50), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("astronomical_family", sa.String(length=50), nullable=False),
            sa.Column(
                "supports_polar_regions", sa.Boolean(), nullable=False, server_default=sa.true()
            ),
            sa.Column("is_quadrant_based", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column(
                "requires_precise_birth_time",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="100"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.CheckConstraint(
                "astronomical_family IN ('quadrant', 'sign_based', 'ascendant_based')",
                name="chk_astral_house_systems_astronomical_family",
            ),
            sa.UniqueConstraint("code"),
        )
    if not _index_exists("astral_house_systems", "ix_astral_house_systems_code"):
        op.create_index(
            "ix_astral_house_systems_code", "astral_house_systems", ["code"], unique=False
        )
    _seed_house_systems()
    op.execute(
        sa.text(
            "UPDATE prediction_rulesets SET house_system = 'porphyry' "
            "WHERE house_system = 'porphyre'"
        )
    )
    op.execute(
        sa.text(
            "UPDATE daily_prediction_runs SET house_system_effective = 'porphyry' "
            "WHERE house_system_effective = 'porphyre'"
        )
    )
    op.execute(
        sa.text(
            "UPDATE user_prediction_baselines SET house_system_effective = 'porphyry' "
            "WHERE house_system_effective = 'porphyre'"
        )
    )

    if not _column_exists("prediction_rulesets", "house_system_id"):
        op.add_column(
            "prediction_rulesets", sa.Column("house_system_id", sa.Integer(), nullable=True)
        )
    op.execute(
        sa.text(
            "UPDATE prediction_rulesets SET house_system_id = "
            f"{_house_system_id_subquery('prediction_rulesets.house_system')}"
        )
    )
    with op.batch_alter_table("prediction_rulesets") as batch_op:
        batch_op.alter_column("house_system_id", existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key(
            "fk_prediction_rulesets_house_system_id_astral_house_systems",
            "astral_house_systems",
            ["house_system_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        batch_op.create_index("ix_prediction_rulesets_house_system_id", ["house_system_id"])
        batch_op.drop_column("house_system")

    if not _column_exists("daily_prediction_runs", "house_system_effective_id"):
        op.add_column(
            "daily_prediction_runs",
            sa.Column("house_system_effective_id", sa.Integer(), nullable=True),
        )
    op.execute(
        sa.text(
            "UPDATE daily_prediction_runs SET house_system_effective_id = "
            f"{_house_system_id_subquery('daily_prediction_runs.house_system_effective')} "
            "WHERE house_system_effective IS NOT NULL"
        )
    )
    with op.batch_alter_table("daily_prediction_runs") as batch_op:
        batch_op.create_foreign_key(
            "fk_daily_prediction_runs_house_system_effective_id_astral_house_systems",
            "astral_house_systems",
            ["house_system_effective_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        batch_op.create_index(
            "ix_daily_prediction_runs_house_system_effective_id",
            ["house_system_effective_id"],
        )
        batch_op.drop_column("house_system_effective")

    if not _column_exists("user_prediction_baselines", "house_system_effective_id"):
        op.add_column(
            "user_prediction_baselines",
            sa.Column("house_system_effective_id", sa.Integer(), nullable=True),
        )
    op.execute(
        sa.text(
            "UPDATE user_prediction_baselines SET house_system_effective_id = "
            f"{_house_system_id_subquery('user_prediction_baselines.house_system_effective')}"
        )
    )
    with op.batch_alter_table("user_prediction_baselines") as batch_op:
        batch_op.drop_constraint("uq_user_prediction_baseline", type_="unique")
        batch_op.alter_column(
            "house_system_effective_id", existing_type=sa.Integer(), nullable=False
        )
        batch_op.create_foreign_key(
            "fk_user_prediction_baselines_house_system_effective_id_astral_house_systems",
            "astral_house_systems",
            ["house_system_effective_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        batch_op.create_index(
            "ix_user_prediction_baselines_house_system_effective_id",
            ["house_system_effective_id"],
        )
        batch_op.create_unique_constraint(
            "uq_user_prediction_baseline",
            [
                "user_id",
                "category_id",
                "granularity_type",
                "granularity_value",
                "window_start_date",
                "window_end_date",
                "reference_version_id",
                "ruleset_id",
                "house_system_effective_id",
            ],
        )
        batch_op.drop_column("house_system_effective")


def downgrade() -> None:
    """Restaure les codes texte historiques pour rollback."""
    op.add_column(
        "user_prediction_baselines",
        sa.Column("house_system_effective", sa.String(length=50), nullable=True),
    )
    op.execute(
        sa.text(
            """
            UPDATE user_prediction_baselines
            SET house_system_effective = (
                SELECT code
                FROM astral_house_systems
                WHERE astral_house_systems.id =
                    user_prediction_baselines.house_system_effective_id
            )
            """
        )
    )
    with op.batch_alter_table("user_prediction_baselines") as batch_op:
        batch_op.drop_constraint("uq_user_prediction_baseline", type_="unique")
        batch_op.drop_index("ix_user_prediction_baselines_house_system_effective_id")
        batch_op.drop_constraint(
            "fk_user_prediction_baselines_house_system_effective_id_astral_house_systems",
            type_="foreignkey",
        )
        batch_op.alter_column(
            "house_system_effective", existing_type=sa.String(length=50), nullable=False
        )
        batch_op.create_unique_constraint(
            "uq_user_prediction_baseline",
            [
                "user_id",
                "category_id",
                "granularity_type",
                "granularity_value",
                "window_start_date",
                "window_end_date",
                "reference_version_id",
                "ruleset_id",
                "house_system_effective",
            ],
        )
        batch_op.drop_column("house_system_effective_id")

    op.add_column(
        "daily_prediction_runs",
        sa.Column("house_system_effective", sa.String(length=50), nullable=True),
    )
    op.execute(
        sa.text(
            """
            UPDATE daily_prediction_runs
            SET house_system_effective = (
                SELECT code
                FROM astral_house_systems
                WHERE astral_house_systems.id = daily_prediction_runs.house_system_effective_id
            )
            WHERE house_system_effective_id IS NOT NULL
            """
        )
    )
    with op.batch_alter_table("daily_prediction_runs") as batch_op:
        batch_op.drop_index("ix_daily_prediction_runs_house_system_effective_id")
        batch_op.drop_constraint(
            "fk_daily_prediction_runs_house_system_effective_id_astral_house_systems",
            type_="foreignkey",
        )
        batch_op.drop_column("house_system_effective_id")

    op.add_column(
        "prediction_rulesets",
        sa.Column("house_system", sa.String(length=50), nullable=True),
    )
    op.execute(
        sa.text(
            """
            UPDATE prediction_rulesets
            SET house_system = (
                SELECT code
                FROM astral_house_systems
                WHERE astral_house_systems.id = prediction_rulesets.house_system_id
            )
            """
        )
    )
    with op.batch_alter_table("prediction_rulesets") as batch_op:
        batch_op.drop_index("ix_prediction_rulesets_house_system_id")
        batch_op.drop_constraint(
            "fk_prediction_rulesets_house_system_id_astral_house_systems",
            type_="foreignkey",
        )
        batch_op.alter_column("house_system", existing_type=sa.String(length=50), nullable=False)
        batch_op.drop_column("house_system_id")

    op.drop_index("ix_astral_house_systems_code", table_name="astral_house_systems")
    op.drop_table("astral_house_systems")
