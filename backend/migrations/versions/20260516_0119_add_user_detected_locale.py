"""Ajoute la localisation détectée des utilisateurs.

Revision ID: 20260516_0119
Revises: 20260516_0118
Create Date: 2026-05-16
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260516_0119"
down_revision: Union[str, Sequence[str], None] = "20260516_0118"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    """Indique si la table existe avant une migration reprenable."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _columns(table_name: str) -> set[str]:
    """Retourne les colonnes existantes d'une table."""
    if not _table_exists(table_name):
        return set()
    return {str(column["name"]) for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def _column_lengths(table_name: str) -> dict[str, int | None]:
    """Retourne les longueurs déclarées des colonnes texte existantes."""
    if not _table_exists(table_name):
        return {}
    return {
        str(column["name"]): getattr(column["type"], "length", None)
        for column in sa.inspect(op.get_bind()).get_columns(table_name)
    }


def upgrade() -> None:
    """Expose la localisation navigateur comme métadonnée utilisateur persistée."""
    if not _table_exists("users"):
        return
    columns = _columns("users")
    column_lengths = _column_lengths("users")
    with op.batch_alter_table("users") as batch_op:
        if "detected_locale" not in columns:
            batch_op.add_column(sa.Column("detected_locale", sa.String(length=64), nullable=True))
        elif column_lengths.get("detected_locale") != 64:
            batch_op.alter_column(
                "detected_locale",
                existing_type=sa.String(length=column_lengths.get("detected_locale")),
                type_=sa.String(length=64),
                nullable=True,
            )
        if "detected_country_code" not in columns:
            batch_op.add_column(
                sa.Column("detected_country_code", sa.String(length=2), nullable=True)
            )
        if "detected_timezone" not in columns:
            batch_op.add_column(sa.Column("detected_timezone", sa.String(length=64), nullable=True))


def downgrade() -> None:
    """Retire les métadonnées de localisation détectée."""
    if not _table_exists("users"):
        return
    columns = _columns("users")
    with op.batch_alter_table("users") as batch_op:
        if "detected_timezone" in columns:
            batch_op.drop_column("detected_timezone")
        if "detected_country_code" in columns:
            batch_op.drop_column("detected_country_code")
        if "detected_locale" in columns:
            batch_op.drop_column("detected_locale")
