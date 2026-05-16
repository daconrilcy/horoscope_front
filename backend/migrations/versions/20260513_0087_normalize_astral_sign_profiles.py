"""normalise astral sign profiles

Revision ID: 20260513_0087
Revises: 20260512_0086
Create Date: 2026-05-13
"""

import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260513_0087"
down_revision: Union[str, Sequence[str], None] = "20260512_0086"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SIGN_PROFILE_DATA = (
    ("aries", "fire", "cardinal", "yang"),
    ("taurus", "earth", "fixed", "yin"),
    ("gemini", "air", "mutable", "yang"),
    ("cancer", "water", "cardinal", "yin"),
    ("leo", "fire", "fixed", "yang"),
    ("virgo", "earth", "mutable", "yin"),
    ("libra", "air", "cardinal", "yang"),
    ("scorpio", "water", "fixed", "yin"),
    ("sagittarius", "fire", "mutable", "yang"),
    ("capricorn", "earth", "cardinal", "yin"),
    ("aquarius", "air", "fixed", "yang"),
    ("pisces", "water", "mutable", "yin"),
)

SIGN_ROWS = (
    ("aries", "Aries"),
    ("taurus", "Taurus"),
    ("gemini", "Gemini"),
    ("cancer", "Cancer"),
    ("leo", "Leo"),
    ("virgo", "Virgo"),
    ("libra", "Libra"),
    ("scorpio", "Scorpio"),
    ("sagittarius", "Sagittarius"),
    ("capricorn", "Capricorn"),
    ("aquarius", "Aquarius"),
    ("pisces", "Pisces"),
)


def _drop_index_if_exists(index_name: str, table_name: str) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    indexes = {index["name"] for index in inspector.get_indexes(table_name)}
    if index_name in indexes:
        op.drop_index(index_name, table_name=table_name)


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _drop_empty_table_if_exists(table_name: str) -> None:
    if not _table_exists(table_name):
        return
    row_count = op.get_bind().execute(sa.text(f"SELECT COUNT(*) FROM {table_name}")).scalar_one()
    if row_count:
        raise RuntimeError(f"refusing to drop non-empty pre-existing table {table_name}")
    op.drop_table(table_name)


def _rename_index(table_name: str, old_name: str, new_name: str, columns: list[str]) -> None:
    _drop_index_if_exists(old_name, table_name)
    op.create_index(new_name, table_name, columns, unique=False)


def _load_sign_keywords() -> dict[str, dict[str, list[str]]]:
    """Charge les mots-clés des signes depuis la source documentaire canonique."""
    migration_path = Path(__file__).resolve()
    candidate_paths = (
        migration_path.parents[3]
        / "docs"
        / "db_seeder"
        / "astrology"
        / "astral_sign_keywords.json",
        migration_path.parents[2]
        / "docs"
        / "db_seeder"
        / "astrology"
        / "astral_sign_keywords.json",
        migration_path.parents[3] / "docs" / "recherches astro" / "astral_sign_keywords.json",
        migration_path.parents[2] / "docs" / "recherches astro" / "astral_sign_keywords.json",
    )
    keywords_path = next((path for path in candidate_paths if path.exists()), None)
    if keywords_path is None:
        raise RuntimeError("missing astrology seed astral_sign_keywords.json")
    with keywords_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("signs keywords source must contain a non-empty data list")
    return {
        str(row["code"]): {
            "keywords": [str(value) for value in row["keywords_json"]],
            "shadow_keywords": [str(value) for value in row["shadow_keywords_json"]],
        }
        for row in rows
    }


def _required_keyword_list(
    keywords_by_sign: dict[str, dict[str, list[str]]],
    sign_code: str,
    field_name: str,
) -> list[str]:
    """Valide la présence d'une liste de mots-clés pour un signe."""
    sign_keywords = keywords_by_sign.get(sign_code)
    if sign_keywords is None:
        raise RuntimeError(f"missing keywords for sign {sign_code}")
    values = sign_keywords.get(field_name)
    if not isinstance(values, list) or not values:
        raise RuntimeError(f"missing {field_name} for sign {sign_code}")
    return [str(value) for value in values]


def _ensure_astral_signs() -> None:
    """Garantit la présence des douze signes avant de créer leurs profils."""
    op.get_bind().execute(
        sa.text(
            """
            INSERT INTO astral_signs (code, name)
            SELECT :code, :name
            WHERE NOT EXISTS (
                SELECT 1 FROM astral_signs WHERE code = :code
            )
            """
        ),
        [{"code": code, "name": name} for code, name in SIGN_ROWS],
    )


def _seed_astral_sign_profiles() -> None:
    """Alimente les taxonomies et les profils structurels des douze signes."""
    op.bulk_insert(
        sa.table(
            "astral_elements",
            sa.column("code", sa.String),
            sa.column("name", sa.String),
        ),
        [
            {"code": "fire", "name": "Fire"},
            {"code": "earth", "name": "Earth"},
            {"code": "air", "name": "Air"},
            {"code": "water", "name": "Water"},
        ],
    )
    op.bulk_insert(
        sa.table(
            "astral_modalities",
            sa.column("code", sa.String),
            sa.column("name", sa.String),
        ),
        [
            {"code": "cardinal", "name": "Cardinal"},
            {"code": "fixed", "name": "Fixed"},
            {"code": "mutable", "name": "Mutable"},
        ],
    )
    op.bulk_insert(
        sa.table(
            "astral_polarities",
            sa.column("code", sa.String),
            sa.column("name", sa.String),
        ),
        [
            {"code": "yang", "name": "Yang"},
            {"code": "yin", "name": "Yin"},
        ],
    )

    bind = op.get_bind()
    keywords_by_sign = _load_sign_keywords()
    profile_rows = []
    for sign_code, element_code, modality_code, polarity_code in SIGN_PROFILE_DATA:
        profile_rows.append(
            {
                "sign_code": sign_code,
                "element_code": element_code,
                "modality_code": modality_code,
                "polarity_code": polarity_code,
                "keywords_json": json.dumps(
                    _required_keyword_list(keywords_by_sign, sign_code, "keywords"),
                    ensure_ascii=False,
                ),
                "shadow_keywords_json": json.dumps(
                    _required_keyword_list(keywords_by_sign, sign_code, "shadow_keywords"),
                    ensure_ascii=False,
                ),
            }
        )
    bind.execute(
        sa.text(
            """
            INSERT INTO astral_sign_profiles (
                astral_sign_id,
                astral_element_id,
                astral_modality_id,
                astral_polarity_id,
                keywords_json,
                shadow_keywords_json
            )
            SELECT
                astral_signs.id,
                astral_elements.id,
                astral_modalities.id,
                astral_polarities.id,
                :keywords_json,
                :shadow_keywords_json
            FROM astral_signs
            JOIN astral_elements ON astral_elements.code = :element_code
            JOIN astral_modalities ON astral_modalities.code = :modality_code
            JOIN astral_polarities ON astral_polarities.code = :polarity_code
            WHERE astral_signs.code = :sign_code
            """
        ),
        profile_rows,
    )


def _ensure_downgrade_reference_version() -> None:
    """Prépare un rollback vers l'ancien modèle versionné des signes."""
    bind = op.get_bind()
    sign_count = bind.execute(sa.text("SELECT COUNT(*) FROM astral_signs")).scalar_one()
    version_count = bind.execute(sa.text("SELECT COUNT(*) FROM reference_versions")).scalar_one()
    if sign_count == 0 or version_count > 0:
        return
    bind.execute(
        sa.text(
            """
            INSERT INTO reference_versions (version, description, created_at, is_locked)
            VALUES (
                'rollback-cs-152',
                'Version technique créée pour rollback des signes astraux',
                CURRENT_TIMESTAMP,
                0
            )
            """
        )
    )


def _rebuild_astral_sign_rulerships() -> None:
    op.create_table(
        "_astral_sign_rulerships_new",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("astral_sign_id", sa.Integer(), nullable=False),
        sa.Column("planet_id", sa.Integer(), nullable=False),
        sa.Column("rulership_type", sa.String(length=32), nullable=False),
        sa.Column("system", sa.String(length=32), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["astral_sign_id"], ["astral_signs.id"]),
        sa.ForeignKeyConstraint(["planet_id"], ["planets.id"]),
        sa.UniqueConstraint("astral_sign_id", "planet_id", "rulership_type", "system"),
    )
    op.execute(
        """
        INSERT INTO _astral_sign_rulerships_new (
            id,
            astral_sign_id,
            planet_id,
            rulership_type,
            system,
            weight,
            is_primary
        )
        SELECT
            MIN(id),
            sign_id,
            planet_id,
            rulership_type,
            'traditional',
            MAX(weight),
            MAX(is_primary)
        FROM astral_sign_rulerships
        GROUP BY sign_id, planet_id, rulership_type
        """
    )
    op.drop_table("astral_sign_rulerships")
    op.rename_table("_astral_sign_rulerships_new", "astral_sign_rulerships")
    op.create_index(
        op.f("ix_astral_sign_rulerships_astral_sign_id"),
        "astral_sign_rulerships",
        ["astral_sign_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_astral_sign_rulerships_planet_id"),
        "astral_sign_rulerships",
        ["planet_id"],
        unique=False,
    )


def upgrade() -> None:
    """Applique le schema canonique des profils de signes astraux."""
    for table_name in (
        "astral_sign_profiles",
        "astral_sign_rulerships",
        "astral_elements",
        "astral_modalities",
        "astral_polarities",
        "astral_signs",
    ):
        _drop_empty_table_if_exists(table_name)

    op.rename_table("signs", "astral_signs")
    _rename_index("astral_signs", "ix_signs_code", op.f("ix_astral_signs_code"), ["code"])
    _ensure_astral_signs()

    op.create_table(
        "astral_elements",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.Column("name", sa.String(length=32), nullable=False),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_astral_elements_code"), "astral_elements", ["code"], unique=False)
    op.create_table(
        "astral_modalities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.Column("name", sa.String(length=32), nullable=False),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_astral_modalities_code"), "astral_modalities", ["code"], unique=False)
    op.create_table(
        "astral_polarities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.Column("name", sa.String(length=32), nullable=False),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_astral_polarities_code"), "astral_polarities", ["code"], unique=False)
    op.create_table(
        "astral_sign_profiles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("astral_sign_id", sa.Integer(), nullable=False),
        sa.Column("astral_element_id", sa.Integer(), nullable=False),
        sa.Column("astral_modality_id", sa.Integer(), nullable=False),
        sa.Column("astral_polarity_id", sa.Integer(), nullable=False),
        sa.Column("keywords_json", sa.Text(), nullable=True),
        sa.Column("shadow_keywords_json", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["astral_sign_id"], ["astral_signs.id"]),
        sa.ForeignKeyConstraint(["astral_element_id"], ["astral_elements.id"]),
        sa.ForeignKeyConstraint(["astral_modality_id"], ["astral_modalities.id"]),
        sa.ForeignKeyConstraint(["astral_polarity_id"], ["astral_polarities.id"]),
        sa.UniqueConstraint("astral_sign_id"),
    )
    op.create_index(
        op.f("ix_astral_sign_profiles_astral_sign_id"),
        "astral_sign_profiles",
        ["astral_sign_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_astral_sign_profiles_astral_element_id"),
        "astral_sign_profiles",
        ["astral_element_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_astral_sign_profiles_astral_modality_id"),
        "astral_sign_profiles",
        ["astral_modality_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_astral_sign_profiles_astral_polarity_id"),
        "astral_sign_profiles",
        ["astral_polarity_id"],
        unique=False,
    )
    _seed_astral_sign_profiles()

    op.rename_table("sign_rulerships", "astral_sign_rulerships")
    _rebuild_astral_sign_rulerships()


def downgrade() -> None:
    """Restaure les noms historiques pour rollback Alembic."""
    _ensure_downgrade_reference_version()
    op.create_table(
        "_sign_rulerships_old",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("reference_version_id", sa.Integer(), nullable=False),
        sa.Column("sign_id", sa.Integer(), nullable=False),
        sa.Column("planet_id", sa.Integer(), nullable=False),
        sa.Column("rulership_type", sa.String(length=32), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["reference_version_id"], ["reference_versions.id"]),
        sa.ForeignKeyConstraint(["sign_id"], ["astral_signs.id"]),
        sa.ForeignKeyConstraint(["planet_id"], ["planets.id"]),
        sa.UniqueConstraint("reference_version_id", "sign_id", "planet_id", "rulership_type"),
    )
    op.execute(
        """
        INSERT INTO _sign_rulerships_old (
            id,
            reference_version_id,
            sign_id,
            planet_id,
            rulership_type,
            weight,
            is_primary
        )
        SELECT
            id,
            (SELECT MIN(id) FROM reference_versions),
            astral_sign_id,
            planet_id,
            rulership_type,
            weight,
            is_primary
        FROM astral_sign_rulerships
        """
    )
    op.drop_table("astral_sign_rulerships")
    op.rename_table("_sign_rulerships_old", "sign_rulerships")
    op.create_index(op.f("ix_sign_rulerships_sign_id"), "sign_rulerships", ["sign_id"])
    op.create_index(op.f("ix_sign_rulerships_planet_id"), "sign_rulerships", ["planet_id"])
    op.create_index(
        op.f("ix_sign_rulerships_reference_version_id"),
        "sign_rulerships",
        ["reference_version_id"],
    )

    op.drop_table("astral_sign_profiles")
    op.drop_table("astral_polarities")
    op.drop_table("astral_modalities")
    op.drop_table("astral_elements")

    _drop_index_if_exists(op.f("ix_astral_signs_code"), "astral_signs")
    op.rename_table("astral_signs", "signs")
    op.create_index("ix_signs_code", "signs", ["code"], unique=False)
