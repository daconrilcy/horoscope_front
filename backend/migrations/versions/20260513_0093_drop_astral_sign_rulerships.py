"""Supprime l'ancienne table de maîtrises de signes.

Revision ID: 20260513_0093
Revises: 20260513_0092
Create Date: 2026-05-13
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260513_0093"
down_revision: Union[str, Sequence[str], None] = "20260513_0092"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

EXPECTED_TRADITIONAL_RULERSHIPS = {
    "aries": "mars",
    "taurus": "venus",
    "gemini": "mercury",
    "cancer": "moon",
    "leo": "sun",
    "virgo": "mercury",
    "libra": "venus",
    "scorpio": "mars",
    "sagittarius": "jupiter",
    "capricorn": "saturn",
    "aquarius": "saturn",
    "pisces": "jupiter",
}


def _table_exists(table_name: str) -> bool:
    """Vérifie l'existence d'une table avant opération destructive."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _index_exists(table_name: str, index_name: str) -> bool:
    """Vérifie l'existence d'un index avant suppression ou création."""
    if not _table_exists(table_name):
        return False
    indexes = sa.inspect(op.get_bind()).get_indexes(table_name)
    return index_name in {index["name"] for index in indexes}


def _traditional_rulerships_from_dignities() -> list[tuple[str, str]]:
    """Extrait les maîtrises traditionnelles primaires sans masquer les doublons."""
    rows = op.get_bind().execute(
        sa.text(
            """
            SELECT astral_signs.code AS sign_code, astral_planets.code AS planet_code
            FROM astral_planet_sign_dignities
            JOIN astral_signs
                ON astral_planet_sign_dignities.astral_sign_id = astral_signs.id
            JOIN astral_planets
                ON astral_planet_sign_dignities.astral_planet_id = astral_planets.id
            JOIN astral_dignity_type
                ON astral_planet_sign_dignities.astral_dignity_type_id =
                    astral_dignity_type.id
            JOIN astral_systems
                ON astral_planet_sign_dignities.astral_system_id = astral_systems.id
            WHERE astral_dignity_type.code = 'domicile'
                AND astral_systems.name = 'traditional'
                AND astral_planet_sign_dignities.is_primary IS TRUE
            """
        )
    )
    return [(str(row.sign_code), str(row.planet_code)) for row in rows]


def _validate_traditional_rulerships() -> None:
    """Bloque la suppression si les dignités ne portent pas les douze maîtrises."""
    rows = _traditional_rulerships_from_dignities()
    actual = dict(rows)
    if len(rows) != len(EXPECTED_TRADITIONAL_RULERSHIPS) or actual != (
        EXPECTED_TRADITIONAL_RULERSHIPS
    ):
        raise RuntimeError(
            "astral_planet_sign_dignities must contain the 12 primary traditional domiciles "
            "before dropping astral_sign_rulerships"
        )


def upgrade() -> None:
    """Supprime l'alias SQL historique après validation de la source canonique."""
    _validate_traditional_rulerships()
    if _table_exists("astral_sign_rulerships"):
        op.drop_table("astral_sign_rulerships")


def downgrade() -> None:
    """Recrée l'ancienne table à partir des dignités pour permettre un retour arrière."""
    if not _table_exists("astral_sign_rulerships"):
        op.create_table(
            "astral_sign_rulerships",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("astral_sign_id", sa.Integer(), nullable=False),
            sa.Column("planet_id", sa.Integer(), nullable=False),
            sa.Column("rulership_type", sa.String(length=32), nullable=False),
            sa.Column("system", sa.String(length=32), nullable=False),
            sa.Column("weight", sa.Float(), nullable=False),
            sa.Column("is_primary", sa.Boolean(), nullable=False),
            sa.ForeignKeyConstraint(["astral_sign_id"], ["astral_signs.id"]),
            sa.ForeignKeyConstraint(["planet_id"], ["astral_planets.id"]),
            sa.UniqueConstraint("astral_sign_id", "planet_id", "rulership_type", "system"),
        )
    for column_name in ("astral_sign_id", "planet_id"):
        index_name = op.f(f"ix_astral_sign_rulerships_{column_name}")
        if not _index_exists("astral_sign_rulerships", index_name):
            op.create_index(index_name, "astral_sign_rulerships", [column_name], unique=False)

    op.execute(sa.text("DELETE FROM astral_sign_rulerships"))
    op.execute(
        sa.text(
            """
            INSERT INTO astral_sign_rulerships (
                astral_sign_id,
                planet_id,
                rulership_type,
                system,
                weight,
                is_primary
            )
            SELECT
                astral_planet_sign_dignities.astral_sign_id,
                astral_planet_sign_dignities.astral_planet_id,
                'domicile',
                astral_systems.name,
                astral_planet_sign_dignities.weight,
                astral_planet_sign_dignities.is_primary
            FROM astral_planet_sign_dignities
            JOIN astral_dignity_type
                ON astral_planet_sign_dignities.astral_dignity_type_id =
                    astral_dignity_type.id
            JOIN astral_systems
                ON astral_planet_sign_dignities.astral_system_id = astral_systems.id
            WHERE astral_dignity_type.code = 'domicile'
                AND astral_systems.name = 'traditional'
                AND astral_planet_sign_dignities.is_primary IS TRUE
            """
        )
    )
