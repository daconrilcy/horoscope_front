"""Rebranche les aspects astraux sur la table canonique des familles.

Revision ID: 20260515_0113
Revises: 20260515_0112
Create Date: 2026-05-15
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260515_0113"
down_revision: Union[str, Sequence[str], None] = "20260515_0112"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OLD_TABLE = "astal_aspect_families"
NEW_TABLE = "astral_aspect_families"
ASPECT_TABLE = "astral_aspects"
NEW_FK_NAME = "fk_astral_aspects_family_astral_aspect_families"
NAMING_CONVENTION = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}


def _table_exists(table_name: str) -> bool:
    """Indique si une table existe dans le schéma courant."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _family_foreign_keys() -> list[dict[str, object]]:
    """Retourne les clés étrangères portées par `astral_aspects.family`."""
    return [
        foreign_key
        for foreign_key in sa.inspect(op.get_bind()).get_foreign_keys(ASPECT_TABLE)
        if tuple(foreign_key["constrained_columns"]) == ("family",)
    ]


def _copy_missing_legacy_families() -> None:
    """Copie les familles absentes depuis l'ancienne table vers la table canonique."""
    if not _table_exists(OLD_TABLE) or not _table_exists(NEW_TABLE):
        return
    op.execute(
        sa.text(
            f"""
            INSERT INTO {NEW_TABLE} (name)
            SELECT old.name
            FROM {OLD_TABLE} AS old
            WHERE NOT EXISTS (
                SELECT 1
                FROM {NEW_TABLE} AS new
                WHERE new.name = old.name
            )
            """
        )
    )


def _retarget_family_ids() -> None:
    """Remappe les IDs de famille des aspects vers les lignes de la table canonique."""
    if not all(_table_exists(table) for table in (OLD_TABLE, NEW_TABLE, ASPECT_TABLE)):
        return
    op.execute(
        sa.text(
            f"""
            UPDATE {ASPECT_TABLE}
            SET family = (
                SELECT new.id
                FROM {OLD_TABLE} AS old
                JOIN {NEW_TABLE} AS new ON new.name = old.name
                WHERE old.id = {ASPECT_TABLE}.family
            )
            WHERE EXISTS (
                SELECT 1
                FROM {OLD_TABLE} AS old
                JOIN {NEW_TABLE} AS new ON new.name = old.name
                WHERE old.id = {ASPECT_TABLE}.family
                    AND new.id != {ASPECT_TABLE}.family
            )
            """
        )
    )


def _rebuild_aspect_family_fk() -> None:
    """Reconstruit la contrainte FK quand elle pointe l'ancien nom ou manque."""
    if not all(_table_exists(table) for table in (NEW_TABLE, ASPECT_TABLE)):
        return
    family_foreign_keys = _family_foreign_keys()
    if len(family_foreign_keys) == 1 and family_foreign_keys[0]["referred_table"] == NEW_TABLE:
        return

    with op.batch_alter_table(
        ASPECT_TABLE,
        recreate="always",
        naming_convention=NAMING_CONVENTION,
    ) as batch_op:
        for foreign_key in family_foreign_keys:
            referred_table = str(foreign_key["referred_table"])
            constraint_name = foreign_key["name"] or f"fk_{ASPECT_TABLE}_family_{referred_table}"
            batch_op.drop_constraint(constraint_name, type_="foreignkey")
        batch_op.create_foreign_key(
            NEW_FK_NAME,
            NEW_TABLE,
            ["family"],
            ["id"],
        )


def upgrade() -> None:
    """Supprime la dépendance à l'ancienne table et retire cette table."""
    _copy_missing_legacy_families()
    _retarget_family_ids()
    _rebuild_aspect_family_fk()
    if _table_exists(OLD_TABLE):
        op.drop_table(OLD_TABLE)


def downgrade() -> None:
    """Ne restaure pas l'ancien nom fautif de table."""
    return
