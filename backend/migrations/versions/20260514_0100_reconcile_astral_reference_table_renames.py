"""Réconcilie les renommages astraux si des tables vides ont été précréées.

Revision ID: 20260514_0100
Revises: 20260514_0099
Create Date: 2026-05-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260514_0100"
down_revision: Union[str, Sequence[str], None] = "20260514_0099"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_RENAMES = (
    ("reference_versions", "astral_reference_versions"),
    ("aspects", "astral_aspects"),
    ("aspect_profiles", "astral_aspect_profiles"),
    ("planet_category_weights", "astral_planet_category_weights"),
)

DROP_EMPTY_NEW_TABLE_ORDER = (
    ("aspect_profiles", "astral_aspect_profiles"),
    ("planet_category_weights", "astral_planet_category_weights"),
    ("aspects", "astral_aspects"),
    ("reference_versions", "astral_reference_versions"),
)

INDEX_SPECS = (
    ("ix_astral_reference_versions_version", "astral_reference_versions", ["version"]),
    ("ix_astral_aspects_code", "astral_aspects", ["code"]),
    (
        "ix_astral_aspect_profiles_reference_version_id",
        "astral_aspect_profiles",
        ["reference_version_id"],
    ),
    ("ix_astral_aspect_profiles_aspect_id", "astral_aspect_profiles", ["aspect_id"]),
    (
        "ix_astral_planet_category_weights_reference_version_id",
        "astral_planet_category_weights",
        ["reference_version_id"],
    ),
    (
        "ix_astral_planet_category_weights_planet_id",
        "astral_planet_category_weights",
        ["planet_id"],
    ),
    (
        "ix_astral_planet_category_weights_category_id",
        "astral_planet_category_weights",
        ["category_id"],
    ),
)


def _table_exists(table_name: str) -> bool:
    """Indique si une table existe dans le schéma courant."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _row_count(table_name: str) -> int:
    """Compte les lignes d'une table existante."""
    return int(op.get_bind().execute(sa.text(f"SELECT COUNT(*) FROM {table_name}")).scalar_one())


def _index_table(index_name: str) -> str | None:
    """Retourne la table propriétaire d'un index existant."""
    inspector = sa.inspect(op.get_bind())
    for table_name in inspector.get_table_names():
        if index_name in {index["name"] for index in inspector.get_indexes(table_name)}:
            return table_name
    return None


def _drop_index_if_exists(index_name: str) -> None:
    """Supprime un index uniquement s'il existe."""
    table_name = _index_table(index_name)
    if table_name is not None:
        op.drop_index(index_name, table_name=table_name)


def _create_index_if_missing(index_name: str, table_name: str, columns: list[str]) -> None:
    """Crée un index attendu uniquement si la table existe et l'index manque."""
    if _table_exists(table_name) and _index_table(index_name) is None:
        op.create_index(index_name, table_name, columns, unique=False)


def _drop_precreated_empty_tables() -> None:
    """Supprime les tables astrales vides créées avant le renommage Alembic."""
    for old_table, new_table in DROP_EMPTY_NEW_TABLE_ORDER:
        if not (_table_exists(old_table) and _table_exists(new_table)):
            continue
        if _row_count(new_table) != 0:
            raise RuntimeError(
                f"Cannot reconcile {old_table} -> {new_table}: both tables contain data"
            )
        op.drop_table(new_table)


def _rename_remaining_old_tables() -> None:
    """Renomme les anciennes tables restantes vers les noms astraux."""
    for old_table, new_table in TABLE_RENAMES:
        if _table_exists(old_table) and not _table_exists(new_table):
            op.rename_table(old_table, new_table)


def upgrade() -> None:
    """Finalise le renommage quand une base locale contient les deux générations."""
    for index_name, _table_name, _columns in INDEX_SPECS:
        _drop_index_if_exists(index_name)
    _drop_precreated_empty_tables()
    _rename_remaining_old_tables()
    for index_name, table_name, columns in INDEX_SPECS:
        _create_index_if_missing(index_name, table_name, columns)


def downgrade() -> None:
    """Restaure les anciens noms si cette migration est rollbackée isolément."""
    for index_name, _table_name, _columns in INDEX_SPECS:
        _drop_index_if_exists(index_name)
    for old_table, new_table in reversed(TABLE_RENAMES):
        if _table_exists(new_table) and not _table_exists(old_table):
            op.rename_table(new_table, old_table)
