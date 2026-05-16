"""Relie les profils localisés et les utilisateurs au référentiel des langues.

Revision ID: 20260516_0118
Revises: 20260516_0117
Create Date: 2026-05-16
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260516_0118"
down_revision: Union[str, Sequence[str], None] = "20260516_0117"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

HOUSE_TABLE = "astral_house_interpretation_profiles"
ASPECT_TABLE = "astral_aspect_interpretation_profiles"

HOUSE_OLD_UNIQUE = "uq_astral_house_interpretation_profiles_version_house_language_system"
HOUSE_NEW_UNIQUE = "uq_astral_house_interpretation_profiles_scope"
HOUSE_LANGUAGE_FK = "fk_astral_house_interpretation_profiles_language_id"

ASPECT_OLD_UNIQUE = "uq_astral_aspect_interpretation_profiles_version_aspect_system_language"
ASPECT_NEW_UNIQUE = "uq_astral_aspect_interpretation_profiles_scope"
ASPECT_LANGUAGE_FK = "fk_astral_aspect_interpretation_profiles_language_id"

USER_LANGUAGE_FK = "fk_users_default_language_id"


def _table_exists(table_name: str) -> bool:
    """Indique si une table existe dans le schéma courant."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _columns(table_name: str) -> set[str]:
    """Retourne les colonnes disponibles pour une table."""
    if not _table_exists(table_name):
        return set()
    return {str(column["name"]) for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def _index_exists(table_name: str, index_name: str) -> bool:
    """Indique si un index existe déjà."""
    if not _table_exists(table_name):
        return False
    return index_name in {
        str(index["name"]) for index in sa.inspect(op.get_bind()).get_indexes(table_name)
    }


def _unique_constraint_names(table_name: str) -> set[str]:
    """Retourne les contraintes uniques nommées d'une table."""
    return {
        str(constraint["name"])
        for constraint in sa.inspect(op.get_bind()).get_unique_constraints(table_name)
        if constraint["name"]
    }


def _foreign_key_names(table_name: str) -> set[str]:
    """Retourne les clés étrangères nommées d'une table."""
    return {
        str(foreign_key["name"])
        for foreign_key in sa.inspect(op.get_bind()).get_foreign_keys(table_name)
        if foreign_key["name"]
    }


def _languages_path() -> Path:
    """Retourne le seed canonique des langues."""
    return Path(__file__).resolve().parents[3] / "docs" / "db_seeder" / "languages.json"


def _load_language_rows() -> list[dict[str, object]]:
    """Charge les lignes de langues depuis le nouvel emplacement documentaire."""
    with _languages_path().open(encoding="utf-8") as stream:
        raw = json.load(stream)
    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("docs/db_seeder/languages.json must contain a non-empty data list")
    return [dict(row) for row in rows]


def _seed_languages() -> None:
    """Garantit les langues avant de créer les nouvelles clés étrangères."""
    if not _table_exists("languages"):
        return
    for row in _load_language_rows():
        op.get_bind().execute(
            sa.text(
                """
                INSERT INTO languages (id, code, name)
                SELECT :id, :code, :name
                WHERE NOT EXISTS (
                    SELECT 1 FROM languages WHERE id = :id OR code = :code
                )
                """
            ),
            {"id": int(row["id"]), "code": str(row["code"]), "name": str(row["name"])},
        )


def _add_language_id_column(table_name: str) -> None:
    """Ajoute `language_id` tant que la colonne texte historique existe."""
    table_columns = _columns(table_name)
    if "language_id" not in table_columns:
        op.add_column(table_name, sa.Column("language_id", sa.Integer(), nullable=True))
    if "language" in table_columns:
        op.execute(
            sa.text(
                f"""
                UPDATE {table_name}
                SET language_id = (
                    SELECT languages.id
                    FROM languages
                    WHERE languages.code = {table_name}.language
                )
                WHERE language_id IS NULL
                """
            )
        )


def _upgrade_profile_language(
    table_name: str,
    old_unique: str,
    new_unique: str,
    fk_name: str,
    unique_columns: list[str],
) -> None:
    """Remplace la colonne `language` par une FK `language_id`."""
    if not _table_exists(table_name):
        return
    _add_language_id_column(table_name)
    with op.batch_alter_table(table_name) as batch_op:
        unique_names = _unique_constraint_names(table_name)
        fk_names = _foreign_key_names(table_name)
        if old_unique in unique_names:
            batch_op.drop_constraint(old_unique, type_="unique")
        if new_unique not in unique_names:
            batch_op.create_unique_constraint(new_unique, unique_columns)
        if fk_name not in fk_names:
            batch_op.create_foreign_key(fk_name, "languages", ["language_id"], ["id"])
        batch_op.alter_column("language_id", existing_type=sa.Integer(), nullable=False)
        if "language" in _columns(table_name):
            batch_op.drop_column("language")
    index_name = f"ix_{table_name}_language_id"
    if not _index_exists(table_name, index_name):
        op.create_index(index_name, table_name, ["language_id"], unique=False)


def _downgrade_profile_language(
    table_name: str,
    old_unique: str,
    new_unique: str,
    fk_name: str,
    old_unique_columns: list[str],
) -> None:
    """Restaure la colonne texte `language` pour rollback."""
    if not _table_exists(table_name):
        return
    table_columns = _columns(table_name)
    if "language" not in table_columns:
        op.add_column(table_name, sa.Column("language", sa.String(length=16), nullable=True))
    if "language_id" in table_columns:
        op.execute(
            sa.text(
                f"""
                UPDATE {table_name}
                SET language = (
                    SELECT languages.code
                    FROM languages
                    WHERE languages.id = {table_name}.language_id
                )
                WHERE language IS NULL
                """
            )
        )
    index_name = f"ix_{table_name}_language_id"
    if _index_exists(table_name, index_name):
        op.drop_index(index_name, table_name=table_name)
    with op.batch_alter_table(table_name) as batch_op:
        unique_names = _unique_constraint_names(table_name)
        fk_names = _foreign_key_names(table_name)
        if new_unique in unique_names:
            batch_op.drop_constraint(new_unique, type_="unique")
        if fk_name in fk_names:
            batch_op.drop_constraint(fk_name, type_="foreignkey")
        if old_unique not in unique_names:
            batch_op.create_unique_constraint(old_unique, old_unique_columns)
        batch_op.alter_column("language", existing_type=sa.String(length=16), nullable=False)
        if "language_id" in _columns(table_name):
            batch_op.drop_column("language_id")


def upgrade() -> None:
    """Applique les références SQL aux langues et expose la préférence utilisateur."""
    _seed_languages()
    _upgrade_profile_language(
        HOUSE_TABLE,
        HOUSE_OLD_UNIQUE,
        HOUSE_NEW_UNIQUE,
        HOUSE_LANGUAGE_FK,
        ["reference_version_id", "house_id", "language_id", "astral_system_id"],
    )
    _upgrade_profile_language(
        ASPECT_TABLE,
        ASPECT_OLD_UNIQUE,
        ASPECT_NEW_UNIQUE,
        ASPECT_LANGUAGE_FK,
        ["reference_version_id", "aspect_id", "astral_system_id", "language_id"],
    )
    if _table_exists("users") and "default_language_id" not in _columns("users"):
        with op.batch_alter_table("users") as batch_op:
            batch_op.add_column(sa.Column("default_language_id", sa.Integer(), nullable=True))
            batch_op.create_foreign_key(
                USER_LANGUAGE_FK, "languages", ["default_language_id"], ["id"]
            )
        op.create_index("ix_users_default_language_id", "users", ["default_language_id"])


def downgrade() -> None:
    """Restaure les colonnes texte historiques et retire la préférence utilisateur."""
    if _table_exists("users") and "default_language_id" in _columns("users"):
        if _index_exists("users", "ix_users_default_language_id"):
            op.drop_index("ix_users_default_language_id", table_name="users")
        with op.batch_alter_table("users") as batch_op:
            if USER_LANGUAGE_FK in _foreign_key_names("users"):
                batch_op.drop_constraint(USER_LANGUAGE_FK, type_="foreignkey")
            batch_op.drop_column("default_language_id")
    _downgrade_profile_language(
        ASPECT_TABLE,
        ASPECT_OLD_UNIQUE,
        ASPECT_NEW_UNIQUE,
        ASPECT_LANGUAGE_FK,
        ["reference_version_id", "aspect_id", "astral_system_id", "language"],
    )
    _downgrade_profile_language(
        HOUSE_TABLE,
        HOUSE_OLD_UNIQUE,
        HOUSE_NEW_UNIQUE,
        HOUSE_LANGUAGE_FK,
        ["reference_version_id", "house_id", "language", "astral_system_id"],
    )
