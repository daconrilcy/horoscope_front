"""Enrichit les profils structurels des signes astraux.

Revision ID: 20260523_0137
Revises: 20260519_0136
Create Date: 2026-05-23
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260523_0137"
down_revision: Union[str, Sequence[str], None] = "20260519_0136"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PROFILE_TABLE = "astral_sign_profiles"
SEASONAL_TABLE = "astral_sign_seasonal_quadrants"
FERTILITY_TABLE = "astral_sign_fertility_classes"
VOICE_TABLE = "astral_sign_voice_classes"
FORM_TABLE = "astral_sign_form_classes"


def _catalog_data() -> dict[str, object]:
    """Charge le catalogue structurel utilise comme source de migration."""
    migration_path = Path(__file__).resolve()
    candidate_paths = (
        migration_path.parents[3]
        / "docs"
        / "db_seeder"
        / "astrology"
        / "astral_structural_reference_catalog.json",
        migration_path.parents[2]
        / "docs"
        / "db_seeder"
        / "astrology"
        / "astral_structural_reference_catalog.json",
    )
    catalog_path = next((path for path in candidate_paths if path.exists()), None)
    if catalog_path is None:
        raise RuntimeError("missing astrology seed astral_structural_reference_catalog.json")
    with catalog_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    data = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(data, dict):
        raise RuntimeError("structural reference catalog must contain a data object")
    return data


def _taxonomy_rows(catalog_key: str) -> list[dict[str, str]]:
    """Retourne les lignes d'une taxonomie du catalogue structurel."""
    rows = _catalog_data().get(catalog_key)
    if not isinstance(rows, list) or not rows:
        raise RuntimeError(f"structural reference catalog must contain {catalog_key}")
    return [{"code": str(row["code"]), "name": str(row["name"])} for row in rows]


def _sign_rows() -> list[dict[str, str]]:
    """Retourne les douze lignes signe enrichies du catalogue structurel."""
    rows = _catalog_data().get("signs")
    required_fields = {
        "code",
        "seasonal_quadrant",
        "fertility",
        "voice",
        "form",
    }
    if not isinstance(rows, list) or len(rows) != 12:
        raise RuntimeError("structural reference catalog must contain twelve sign rows")
    sign_rows: list[dict[str, str]] = []
    for row in rows:
        if not isinstance(row, dict) or not required_fields <= set(row):
            raise RuntimeError("each sign row must expose all structural classification fields")
        sign_rows.append({field_name: str(row[field_name]) for field_name in required_fields})
    return sign_rows


def _create_taxonomy_table(table_name: str, code_length: int, name_length: int) -> None:
    """Cree une table de taxonomie signe avec un code unique."""
    op.create_table(
        table_name,
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=code_length), nullable=False),
        sa.Column("name", sa.String(length=name_length), nullable=False),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f(f"ix_{table_name}_code"), table_name, ["code"], unique=False)


def _insert_taxonomy(table_name: str, rows: list[dict[str, str]]) -> None:
    """Insere les lignes d'une taxonomie depuis le catalogue."""
    op.bulk_insert(
        sa.table(
            table_name,
            sa.column("code", sa.String),
            sa.column("name", sa.String),
        ),
        rows,
    )


def _assign_profile_classifications() -> None:
    """Renseigne les nouvelles references non nulles des profils de signes."""
    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            UPDATE astral_sign_profiles
            SET
                seasonal_quadrant_id = (
                    SELECT astral_sign_seasonal_quadrants.id
                    FROM astral_sign_seasonal_quadrants
                    WHERE astral_sign_seasonal_quadrants.code = :seasonal_quadrant
                ),
                fertility_class_id = (
                    SELECT astral_sign_fertility_classes.id
                    FROM astral_sign_fertility_classes
                    WHERE astral_sign_fertility_classes.code = :fertility
                ),
                voice_class_id = (
                    SELECT astral_sign_voice_classes.id
                    FROM astral_sign_voice_classes
                    WHERE astral_sign_voice_classes.code = :voice
                ),
                form_class_id = (
                    SELECT astral_sign_form_classes.id
                    FROM astral_sign_form_classes
                    WHERE astral_sign_form_classes.code = :form
                )
            WHERE astral_sign_id = (
                SELECT astral_signs.id
                FROM astral_signs
                WHERE astral_signs.code = :code
            )
            """
        ),
        _sign_rows(),
    )
    missing_count = bind.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM astral_sign_profiles
            WHERE seasonal_quadrant_id IS NULL
                OR fertility_class_id IS NULL
                OR voice_class_id IS NULL
                OR form_class_id IS NULL
            """
        )
    ).scalar_one()
    if missing_count:
        raise RuntimeError("structural sign profile classification backfill is incomplete")


def upgrade() -> None:
    """Ajoute les taxonomies et references structurelles des signes."""
    _create_taxonomy_table(SEASONAL_TABLE, 16, 32)
    _create_taxonomy_table(FERTILITY_TABLE, 32, 64)
    _create_taxonomy_table(VOICE_TABLE, 32, 64)
    _create_taxonomy_table(FORM_TABLE, 32, 64)
    _insert_taxonomy(SEASONAL_TABLE, _taxonomy_rows("sign_seasonal_quadrants"))
    _insert_taxonomy(FERTILITY_TABLE, _taxonomy_rows("sign_fertility_classes"))
    _insert_taxonomy(VOICE_TABLE, _taxonomy_rows("sign_voice_classes"))
    _insert_taxonomy(FORM_TABLE, _taxonomy_rows("sign_form_classes"))

    op.add_column(PROFILE_TABLE, sa.Column("seasonal_quadrant_id", sa.Integer(), nullable=True))
    op.add_column(PROFILE_TABLE, sa.Column("fertility_class_id", sa.Integer(), nullable=True))
    op.add_column(PROFILE_TABLE, sa.Column("voice_class_id", sa.Integer(), nullable=True))
    op.add_column(PROFILE_TABLE, sa.Column("form_class_id", sa.Integer(), nullable=True))
    _assign_profile_classifications()

    with op.batch_alter_table(PROFILE_TABLE) as batch_op:
        batch_op.alter_column("seasonal_quadrant_id", existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column("fertility_class_id", existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column("voice_class_id", existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column("form_class_id", existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key(
            "fk_astral_sign_profiles_seasonal_quadrant_id",
            SEASONAL_TABLE,
            ["seasonal_quadrant_id"],
            ["id"],
        )
        batch_op.create_foreign_key(
            "fk_astral_sign_profiles_fertility_class_id",
            FERTILITY_TABLE,
            ["fertility_class_id"],
            ["id"],
        )
        batch_op.create_foreign_key(
            "fk_astral_sign_profiles_voice_class_id",
            VOICE_TABLE,
            ["voice_class_id"],
            ["id"],
        )
        batch_op.create_foreign_key(
            "fk_astral_sign_profiles_form_class_id",
            FORM_TABLE,
            ["form_class_id"],
            ["id"],
        )
        batch_op.create_index(
            op.f("ix_astral_sign_profiles_seasonal_quadrant_id"),
            ["seasonal_quadrant_id"],
        )
        batch_op.create_index(
            op.f("ix_astral_sign_profiles_fertility_class_id"),
            ["fertility_class_id"],
        )
        batch_op.create_index(op.f("ix_astral_sign_profiles_voice_class_id"), ["voice_class_id"])
        batch_op.create_index(op.f("ix_astral_sign_profiles_form_class_id"), ["form_class_id"])


def downgrade() -> None:
    """Retire les references structurelles ajoutees aux profils de signes."""
    with op.batch_alter_table(PROFILE_TABLE) as batch_op:
        batch_op.drop_index(op.f("ix_astral_sign_profiles_form_class_id"))
        batch_op.drop_index(op.f("ix_astral_sign_profiles_voice_class_id"))
        batch_op.drop_index(op.f("ix_astral_sign_profiles_fertility_class_id"))
        batch_op.drop_index(op.f("ix_astral_sign_profiles_seasonal_quadrant_id"))
        batch_op.drop_constraint("fk_astral_sign_profiles_form_class_id", type_="foreignkey")
        batch_op.drop_constraint("fk_astral_sign_profiles_voice_class_id", type_="foreignkey")
        batch_op.drop_constraint("fk_astral_sign_profiles_fertility_class_id", type_="foreignkey")
        batch_op.drop_constraint("fk_astral_sign_profiles_seasonal_quadrant_id", type_="foreignkey")
        batch_op.drop_column("form_class_id")
        batch_op.drop_column("voice_class_id")
        batch_op.drop_column("fertility_class_id")
        batch_op.drop_column("seasonal_quadrant_id")

    op.drop_table(FORM_TABLE)
    op.drop_table(VOICE_TABLE)
    op.drop_table(FERTILITY_TABLE)
    op.drop_table(SEASONAL_TABLE)
