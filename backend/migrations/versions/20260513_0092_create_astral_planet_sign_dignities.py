"""Cree et alimente les dignites planetaires par signe.

Revision ID: 20260513_0092
Revises: 20260513_0091
Create Date: 2026-05-13
"""

import json
from pathlib import Path
from typing import Any, Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260513_0092"
down_revision: Union[str, Sequence[str], None] = "20260513_0091"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SIGN_ROWS = (
    (1, "aries", "Aries"),
    (2, "taurus", "Taurus"),
    (3, "gemini", "Gemini"),
    (4, "cancer", "Cancer"),
    (5, "leo", "Leo"),
    (6, "virgo", "Virgo"),
    (7, "libra", "Libra"),
    (8, "scorpio", "Scorpio"),
    (9, "sagittarius", "Sagittarius"),
    (10, "capricorn", "Capricorn"),
    (11, "aquarius", "Aquarius"),
    (12, "pisces", "Pisces"),
)
PLANET_ROWS = (
    (1, "sun", "Sun"),
    (2, "moon", "Moon"),
    (3, "mercury", "Mercury"),
    (4, "venus", "Venus"),
    (5, "mars", "Mars"),
    (6, "jupiter", "Jupiter"),
    (7, "saturn", "Saturn"),
    (8, "uranus", "Uranus"),
    (9, "neptune", "Neptune"),
    (10, "pluto", "Pluto"),
)
SIGN_CODE_BY_SOURCE_ID = {source_id: code for source_id, code, _name in SIGN_ROWS}
PLANET_CODE_BY_SOURCE_ID = {source_id: code for source_id, code, _name in PLANET_ROWS}


def _source_path() -> Path:
    """Retourne le chemin du JSON source des dignites planetaires."""
    migration_path = Path(__file__).resolve()
    candidate_paths = (
        migration_path.parents[3]
        / "docs"
        / "db_seeder"
        / "astrology"
        / "planet_sign_diginities.json",
        migration_path.parents[2]
        / "docs"
        / "db_seeder"
        / "astrology"
        / "planet_sign_diginities.json",
        migration_path.parents[3] / "docs" / "recherches astro" / "planet_sign_diginities.json",
        migration_path.parents[2] / "docs" / "recherches astro" / "planet_sign_diginities.json",
    )
    source_path = next((path for path in candidate_paths if path.exists()), None)
    if source_path is None:
        raise RuntimeError("missing astrology seed planet_sign_diginities.json")
    return source_path


def _load_source_rows() -> list[dict[str, Any]]:
    """Charge et valide la structure minimale du JSON de dignites."""
    with _source_path().open(encoding="utf-8") as stream:
        raw = json.load(stream)
    if not isinstance(raw, list) or not raw:
        raise RuntimeError("planet sign dignities source must be a non-empty list")
    required_keys = {
        "id",
        "astral_sign_id",
        "planet_id",
        "dignity_type",
        "system",
        "weight",
        "is_primary",
    }
    for row in raw:
        if not isinstance(row, dict) or required_keys - row.keys():
            raise RuntimeError("planet sign dignity rows have an invalid structure")
    ids = [int(row["id"]) for row in raw]
    if len(ids) != len(set(ids)):
        raise RuntimeError("planet sign dignity ids must be unique")
    return raw


def _lookup_ids(table_name: str, key_column: str) -> dict[str, int]:
    """Construit une table de correspondance code ou nom vers identifiant."""
    bind = op.get_bind()
    rows = bind.execute(sa.text(f"SELECT id, {key_column} FROM {table_name}")).all()
    return {str(row[1]): int(row[0]) for row in rows}


def _table_exists(table_name: str) -> bool:
    """Vérifie si une table existe déjà dans la base migrée."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _index_exists(table_name: str, index_name: str) -> bool:
    """Vérifie si un index existe déjà pour éviter les doublons."""
    indexes = sa.inspect(op.get_bind()).get_indexes(table_name)
    return index_name in {index["name"] for index in indexes}


def _ensure_code_rows(table_name: str, rows: tuple[tuple[int, str, str], ...]) -> dict[str, int]:
    """Garantit les lignes code/nom utiles aux correspondances du JSON."""
    bind = op.get_bind()
    for _source_id, code, name in rows:
        bind.execute(
            sa.text(
                f"""
                INSERT INTO {table_name} (code, name)
                SELECT :code, :name
                WHERE NOT EXISTS (
                    SELECT 1 FROM {table_name} WHERE code = :code
                )
                """
            ),
            {"code": code, "name": name},
        )
    return _lookup_ids(table_name, "code")


def _seed_dignities() -> None:
    """Injecte les dignites en remplaçant les libelles par leurs FK."""
    op.execute(sa.text("DELETE FROM astral_planet_sign_dignities"))
    dignity_type_ids = _lookup_ids("astral_dignity_type", "code")
    system_ids = _lookup_ids("astral_systems", "name")
    sign_ids = _ensure_code_rows("astral_signs", SIGN_ROWS)
    planet_ids = _ensure_code_rows("astral_planets", PLANET_ROWS)
    insert_rows = []

    for source_row in _load_source_rows():
        source_sign_id = int(source_row["astral_sign_id"])
        source_planet_id = int(source_row["planet_id"])
        sign_code = SIGN_CODE_BY_SOURCE_ID.get(source_sign_id)
        planet_code = PLANET_CODE_BY_SOURCE_ID.get(source_planet_id)
        dignity_type = str(source_row["dignity_type"])
        system = str(source_row["system"])
        if sign_code not in sign_ids:
            raise RuntimeError(f"unknown astral_sign_id: {source_sign_id}")
        if planet_code not in planet_ids:
            raise RuntimeError(f"unknown astral_planet_id: {source_planet_id}")
        if dignity_type not in dignity_type_ids:
            raise RuntimeError(f"unknown dignity_type: {dignity_type}")
        if system not in system_ids:
            raise RuntimeError(f"unknown astral system: {system}")
        insert_rows.append(
            {
                "id": int(source_row["id"]),
                "astral_sign_id": sign_ids[sign_code],
                "astral_planet_id": planet_ids[planet_code],
                "astral_dignity_type_id": dignity_type_ids[dignity_type],
                "astral_system_id": system_ids[system],
                "weight": float(source_row["weight"]),
                "is_primary": bool(source_row["is_primary"]),
            }
        )

    op.bulk_insert(
        sa.table(
            "astral_planet_sign_dignities",
            sa.column("id", sa.Integer),
            sa.column("astral_sign_id", sa.Integer),
            sa.column("astral_planet_id", sa.Integer),
            sa.column("astral_dignity_type_id", sa.Integer),
            sa.column("astral_system_id", sa.Integer),
            sa.column("weight", sa.Float),
            sa.column("is_primary", sa.Boolean),
        ),
        insert_rows,
    )

    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            sa.text(
                """
                SELECT setval(
                    pg_get_serial_sequence('astral_planet_sign_dignities', 'id'),
                    COALESCE((SELECT MAX(id) FROM astral_planet_sign_dignities), 1),
                    true
                )
                """
            )
        )


def upgrade() -> None:
    """Cree la table des dignites planetaires par signe et systeme."""
    if not _table_exists("astral_planet_sign_dignities"):
        op.create_table(
            "astral_planet_sign_dignities",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("astral_sign_id", sa.Integer(), nullable=False),
            sa.Column("astral_planet_id", sa.Integer(), nullable=False),
            sa.Column("astral_dignity_type_id", sa.Integer(), nullable=False),
            sa.Column("astral_system_id", sa.Integer(), nullable=False),
            sa.Column("weight", sa.Float(), nullable=False),
            sa.Column("is_primary", sa.Boolean(), nullable=False),
            sa.ForeignKeyConstraint(["astral_sign_id"], ["astral_signs.id"]),
            sa.ForeignKeyConstraint(["astral_planet_id"], ["astral_planets.id"]),
            sa.ForeignKeyConstraint(["astral_dignity_type_id"], ["astral_dignity_type.id"]),
            sa.ForeignKeyConstraint(["astral_system_id"], ["astral_systems.id"]),
            sa.UniqueConstraint(
                "astral_sign_id",
                "astral_planet_id",
                "astral_dignity_type_id",
                "astral_system_id",
            ),
        )
    for column_name in (
        "astral_sign_id",
        "astral_planet_id",
        "astral_dignity_type_id",
        "astral_system_id",
    ):
        index_name = op.f(f"ix_astral_planet_sign_dignities_{column_name}")
        if not _index_exists("astral_planet_sign_dignities", index_name):
            op.create_index(
                index_name,
                "astral_planet_sign_dignities",
                [column_name],
                unique=False,
            )
    _seed_dignities()


def downgrade() -> None:
    """Supprime la table des dignites planetaires par signe."""
    for column_name in (
        "astral_system_id",
        "astral_dignity_type_id",
        "astral_planet_id",
        "astral_sign_id",
    ):
        op.drop_index(
            op.f(f"ix_astral_planet_sign_dignities_{column_name}"),
            table_name="astral_planet_sign_dignities",
        )
    op.drop_table("astral_planet_sign_dignities")
