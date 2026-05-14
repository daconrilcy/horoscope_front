"""Normalise les aspects astraux et leurs référentiels de valence.

Revision ID: 20260514_0102
Revises: 20260514_0101
Create Date: 2026-05-14
"""

from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260514_0102"
down_revision: Union[str, Sequence[str], None] = "20260514_0101"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ASPECT_FAMILIES = ("major", "minor", "advanced")
DEFAULT_VALENCES = ("positive", "negative", "neutral", "contextual")
INTERPRETIVE_VALENCES = (
    "supportive",
    "harmonious",
    "dynamic_challenging",
    "polarizing",
    "amplifying",
)
ASPECTS = (
    ("conjunction", "Conjunction", 0.0, "major"),
    ("sextile", "Sextile", 60.0, "major"),
    ("square", "Square", 90.0, "major"),
    ("trine", "Trine", 120.0, "major"),
    ("opposition", "Opposition", 180.0, "major"),
    ("semi_sextile", "Semi-sextile", 30.0, "minor"),
    ("semi_square", "Semi-square", 45.0, "minor"),
    ("quintile", "Quintile", 72.0, "minor"),
    ("sesquiquadrate", "Sesquiquadrate", 135.0, "minor"),
    ("quincunx", "Quincunx", 150.0, "minor"),
    ("biquintile", "Biquintile", 144.0, "minor"),
    ("septile", "Septile", 51.428571, "advanced"),
    ("biseptile", "Biseptile", 102.857143, "advanced"),
    ("triseptile", "Triseptile", 154.285714, "advanced"),
    ("novile", "Novile", 40.0, "advanced"),
    ("binovile", "Binovile", 80.0, "advanced"),
    ("quadranovile", "Quadranovile", 160.0, "advanced"),
    ("decile", "Decile", 36.0, "advanced"),
    ("tredecile", "Tredecile", 108.0, "advanced"),
    ("quindecile", "Quindecile", 165.0, "advanced"),
)
PROFILE_SEED = (
    ("conjunction", 1.5, "contextual", "amplifying", 0.0, "fusion_intensification", 1.0, True),
    ("sextile", 0.8, "positive", "supportive", 0.55, "cooperative_opportunity", 0.9, False),
    ("square", 1.25, "negative", "dynamic_challenging", -0.65, "friction_activation", 1.0, True),
    ("trine", 1.0, "positive", "harmonious", 0.75, "harmonious_flow", 1.0, False),
    ("opposition", 1.35, "contextual", "polarizing", -0.35, "polarity_awareness", 1.0, True),
    (
        "semi_sextile",
        0.35,
        "contextual",
        "subtle_adjustment",
        0.05,
        "minor_adaptation",
        0.65,
        False,
    ),
    ("semi_square", 0.45, "negative", "minor_friction", -0.35, "irritation_pressure", 0.55, True),
    ("quintile", 0.4, "positive", "creative", 0.35, "creative_patterning", 0.55, False),
    (
        "sesquiquadrate",
        0.45,
        "negative",
        "indirect_tension",
        -0.35,
        "accumulated_pressure",
        0.55,
        True,
    ),
    ("quincunx", 0.65, "contextual", "adjustment", -0.2, "incongruent_adaptation", 0.65, True),
    ("biquintile", 0.35, "positive", "refined_creative", 0.3, "creative_refinement", 0.55, False),
    ("septile", 0.25, "contextual", "symbolic_fated", 0.0, "symbolic_compulsion", 0.35, False),
    ("biseptile", 0.25, "contextual", "symbolic_fated", 0.0, "symbolic_compulsion", 0.35, False),
    ("triseptile", 0.25, "contextual", "symbolic_fated", 0.0, "symbolic_compulsion", 0.35, False),
    ("novile", 0.25, "positive", "spiritual_integration", 0.2, "inner_completion", 0.35, False),
    ("binovile", 0.25, "positive", "spiritual_integration", 0.2, "inner_completion", 0.35, False),
    (
        "quadranovile",
        0.25,
        "positive",
        "spiritual_integration",
        0.2,
        "inner_completion",
        0.35,
        False,
    ),
    ("decile", 0.25, "positive", "creative_ordering", 0.25, "creative_harmonic", 0.35, False),
    ("tredecile", 0.25, "positive", "creative_ordering", 0.25, "creative_harmonic", 0.35, False),
    ("quindecile", 0.3, "contextual", "obsessive_focus", -0.1, "intensified_fixation", 0.4, True),
)
MODERN_DEFINITIONS = {
    "conjunction": (True, True, False, 8.0, 100, 1.5, 1.5),
    "opposition": (True, True, False, 8.0, 95, 1.35, 1.35),
    "square": (True, True, False, 6.0, 90, 1.25, 1.25),
    "trine": (True, True, False, 6.0, 85, 1.0, 1.0),
    "sextile": (True, True, False, 4.0, 80, 0.8, 0.8),
    "quincunx": (True, False, True, 3.0, 60, 0.65, 0.35),
    "semi_square": (True, False, True, 2.0, 45, 0.45, 0.25),
    "sesquiquadrate": (True, False, True, 2.0, 44, 0.45, 0.25),
    "semi_sextile": (True, False, True, 2.0, 40, 0.35, 0.15),
    "quintile": (True, False, True, 2.0, 35, 0.4, 0.1),
    "biquintile": (True, False, True, 2.0, 34, 0.35, 0.1),
    "septile": (False, False, True, 1.0, 20, 0.25, 0.0),
    "biseptile": (False, False, True, 1.0, 19, 0.25, 0.0),
    "triseptile": (False, False, True, 1.0, 18, 0.25, 0.0),
    "novile": (False, False, True, 1.0, 17, 0.25, 0.0),
    "binovile": (False, False, True, 1.0, 16, 0.25, 0.0),
    "quadranovile": (False, False, True, 1.0, 15, 0.25, 0.0),
    "decile": (False, False, True, 1.0, 14, 0.25, 0.0),
    "tredecile": (False, False, True, 1.0, 13, 0.25, 0.0),
    "quindecile": (False, False, True, 1.5, 12, 0.3, 0.0),
}
SYSTEM_OVERRIDES = {
    "traditional": {
        "conjunction": (True, True, False, 8.0, 100, 1.5, 1.5),
        "opposition": (True, True, False, 8.0, 95, 1.35, 1.35),
        "square": (True, True, False, 6.0, 90, 1.25, 1.25),
        "trine": (True, True, False, 6.0, 85, 1.0, 1.0),
        "sextile": (True, True, False, 4.0, 80, 0.8, 0.8),
    },
    "hellenistic": {
        "conjunction": (True, True, False, 8.0, 100, 1.45, 1.45),
        "opposition": (True, True, False, 8.0, 95, 1.35, 1.35),
        "square": (True, True, False, 6.0, 90, 1.25, 1.25),
        "trine": (True, True, False, 6.0, 85, 1.0, 1.0),
        "sextile": (True, True, False, 4.0, 80, 0.75, 0.75),
    },
    "medieval": {
        "conjunction": (True, True, False, 8.0, 100, 1.5, 1.5),
        "opposition": (True, True, False, 8.0, 95, 1.35, 1.35),
        "square": (True, True, False, 6.0, 90, 1.25, 1.25),
        "trine": (True, True, False, 6.0, 85, 1.0, 1.0),
        "sextile": (True, True, False, 4.0, 80, 0.8, 0.8),
    },
}


def _table_exists(table_name: str) -> bool:
    """Indique si une table existe dans le schéma courant."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _column_exists(table_name: str, column_name: str) -> bool:
    """Indique si une colonne existe dans une table."""
    return column_name in {
        column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)
    }


def _index_exists(table_name: str, index_name: str) -> bool:
    """Indique si un index existe sur une table."""
    return index_name in {
        index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)
    }


def _foreign_key_exists(
    table_name: str,
    constrained_columns: tuple[str, ...],
    referred_table: str,
) -> bool:
    """Indique si une clé étrangère équivalente existe déjà."""
    return any(
        tuple(foreign_key["constrained_columns"]) == constrained_columns
        and foreign_key["referred_table"] == referred_table
        for foreign_key in sa.inspect(op.get_bind()).get_foreign_keys(table_name)
    )


def _create_catalog_table_if_missing(table_name: str, name_length: int) -> None:
    """Crée un catalogue id/name uniquement s'il n'existe pas déjà."""
    if _table_exists(table_name):
        return
    op.create_table(
        table_name,
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=name_length), nullable=False),
        sa.UniqueConstraint("name"),
    )


def _rename_table_if_needed(old_name: str, new_name: str) -> None:
    """Renomme une table précréée avec un ancien nom si nécessaire."""
    if _table_exists(old_name) and not _table_exists(new_name):
        op.rename_table(old_name, new_name)


def _create_index_if_missing(table_name: str, index_name: str, columns: list[str]) -> None:
    """Crée un index uniquement s'il n'existe pas déjà."""
    if not _index_exists(table_name, index_name):
        op.create_index(index_name, table_name, columns)


def _seed_catalog(table_name: str, names: tuple[str, ...]) -> None:
    """Insère les valeurs simples d'un catalogue id/name."""
    table = sa.table(table_name, sa.column("name", sa.String()))
    for name in names:
        op.execute(sa.insert(table).values(name=name).prefix_with("OR IGNORE", dialect="sqlite"))


def _ids_by_name(table_name: str) -> dict[str, int]:
    """Retourne le mapping name -> id pour un catalogue."""
    rows = op.get_bind().execute(sa.text(f"SELECT id, name FROM {table_name}")).mappings()
    return {str(row["name"]): int(row["id"]) for row in rows}


def _ids_by_code(table_name: str) -> dict[str, int]:
    """Retourne le mapping code -> id pour une table de référence."""
    rows = op.get_bind().execute(sa.text(f"SELECT id, code FROM {table_name}")).mappings()
    return {str(row["code"]): int(row["id"]) for row in rows}


def _seed_aspects() -> None:
    """Insère ou met à jour les aspects et familles issus du JSON."""
    families = _ids_by_name("astral_aspect_families")
    connection = op.get_bind()
    for code, name, angle, family_name in ASPECTS:
        family_id = families[family_name]
        row = connection.execute(
            sa.text("SELECT id FROM astral_aspects WHERE code = :code"),
            {"code": code},
        ).first()
        if row is None:
            connection.execute(
                sa.text(
                    """
                    INSERT INTO astral_aspects (code, name, angle, family)
                    VALUES (:code, :name, :angle, :family)
                    """
                ),
                {"code": code, "name": name, "angle": angle, "family": family_id},
            )
            continue
        connection.execute(
            sa.text(
                """
                UPDATE astral_aspects
                SET name = :name, angle = :angle, family = :family
                WHERE code = :code
                """
            ),
            {"code": code, "name": name, "angle": angle, "family": family_id},
        )


def _profile_json(aspect_code: str, kind: str) -> str:
    """Construit les paramètres JSON communs aux profils d'aspects."""
    exact_orb = 1.0 if aspect_code in {"conjunction", "square", "trine", "opposition"} else 0.5
    if aspect_code in {
        "septile",
        "biseptile",
        "triseptile",
        "novile",
        "binovile",
        "quadranovile",
        "decile",
        "tredecile",
    }:
        exact_orb = 0.3
    if aspect_code == "quincunx":
        exact_orb = 0.6
    if aspect_code == "quindecile":
        exact_orb = 0.4
    if kind == "strength":
        return json.dumps(
            {
                "exact_orb_deg": exact_orb,
                "strong_ratio": 0.33,
                "moderate_ratio": 0.66,
                "weak_ratio": 1.0,
            }
        )
    applying = 1.0
    exact = 1.1
    separating = 0.9
    if aspect_code in {"conjunction", "square", "opposition"}:
        applying = 1.15 if aspect_code == "conjunction" else 1.2
        exact = 1.3 if aspect_code == "conjunction" else 1.35
        separating = 0.85 if aspect_code == "conjunction" else 0.8
    elif aspect_code in {"sextile", "trine"}:
        applying = 1.05
        exact = 1.15 if aspect_code == "sextile" else 1.2
    elif aspect_code in {"semi_square", "sesquiquadrate", "quincunx", "quindecile"}:
        applying = 1.1
        exact = 1.25 if aspect_code == "quincunx" else 1.2
        separating = 0.85
    return json.dumps(
        {
            "applying_multiplier": applying,
            "exact_multiplier": exact,
            "separating_multiplier": separating,
        }
    )


def _seed_profiles() -> None:
    """Alimente les profils d'aspects pour chaque version existante."""
    connection = op.get_bind()
    aspect_ids = _ids_by_code("astral_aspects")
    version_ids = [
        int(row[0])
        for row in connection.execute(sa.text("SELECT id FROM astral_reference_versions")).all()
    ]
    for version_id in version_ids:
        for (
            code,
            intensity,
            default_valence,
            interpretive,
            polarity,
            energy,
            orb,
            phase,
        ) in PROFILE_SEED:
            aspect_id = aspect_ids[code]
            existing = connection.execute(
                sa.text(
                    """
                    SELECT id FROM astral_aspect_profiles
                    WHERE reference_version_id = :version_id AND aspect_id = :aspect_id
                    """
                ),
                {"version_id": version_id, "aspect_id": aspect_id},
            ).first()
            params = {
                "version_id": version_id,
                "aspect_id": aspect_id,
                "intensity": intensity,
                "default_valence": default_valence,
                "interpretive": interpretive,
                "polarity": polarity,
                "energy": energy,
                "orb": orb,
                "phase": phase,
                "phase_json": _profile_json(code, "phase"),
                "strength_json": _profile_json(code, "strength"),
                "micro_note": None,
            }
            if existing is None:
                connection.execute(
                    sa.text(
                        """
                        INSERT INTO astral_aspect_profiles (
                            reference_version_id, aspect_id, intensity_weight,
                            default_valence, interpretive_valence, polarity_score,
                            energy_type, orb_multiplier, phase_sensitive,
                            phase_behavior_json, strength_thresholds_json, micro_note
                        )
                        VALUES (
                            :version_id, :aspect_id, :intensity, :default_valence,
                            :interpretive, :polarity, :energy, :orb, :phase,
                            :phase_json, :strength_json, :micro_note
                        )
                        """
                    ),
                    params,
                )
                continue
            connection.execute(
                sa.text(
                    """
                    UPDATE astral_aspect_profiles
                    SET intensity_weight = :intensity,
                        default_valence = :default_valence,
                        interpretive_valence = :interpretive,
                        polarity_score = :polarity,
                        energy_type = :energy,
                        orb_multiplier = :orb,
                        phase_sensitive = :phase,
                        phase_behavior_json = :phase_json,
                        strength_thresholds_json = :strength_json,
                        micro_note = :micro_note
                    WHERE reference_version_id = :version_id AND aspect_id = :aspect_id
                    """
                ),
                params,
            )


def _seed_definitions() -> None:
    """Alimente les définitions d'aspects pour chaque version et système."""
    connection = op.get_bind()
    aspect_ids = _ids_by_code("astral_aspects")
    system_ids = _ids_by_name("astral_systems")
    version_ids = [
        int(row[0])
        for row in connection.execute(sa.text("SELECT id FROM astral_reference_versions")).all()
    ]
    for version_id in version_ids:
        for system_name in ("modern", "traditional", "hellenistic", "medieval"):
            definitions = dict(MODERN_DEFINITIONS)
            if system_name != "modern":
                definitions = {
                    code: (
                        SYSTEM_OVERRIDES[system_name].get(code)
                        if code in SYSTEM_OVERRIDES[system_name]
                        else (False, *values[1:6], 0.0)
                    )
                    for code, values in MODERN_DEFINITIONS.items()
                }
            for code, values in definitions.items():
                params = {
                    "version_id": version_id,
                    "aspect_id": aspect_ids[code],
                    "system_id": system_ids[system_name],
                    "is_enabled": values[0],
                    "is_major": values[1],
                    "is_minor": values[2],
                    "orb": values[3],
                    "priority": values[4],
                    "interpretation": values[5],
                    "scoring": values[6],
                    "micro_note": None,
                }
                existing = connection.execute(
                    sa.text(
                        """
                        SELECT id FROM astral_aspect_definitions
                        WHERE reference_version_id = :version_id
                            AND aspect_id = :aspect_id
                            AND astral_system_id = :system_id
                        """
                    ),
                    params,
                ).first()
                if existing is None:
                    connection.execute(
                        sa.text(
                            """
                            INSERT INTO astral_aspect_definitions (
                                reference_version_id, aspect_id, astral_system_id,
                                is_enabled, is_major, is_minor, default_orb_deg,
                                display_priority, interpretation_weight,
                                scoring_weight, micro_note
                            )
                            VALUES (
                                :version_id, :aspect_id, :system_id, :is_enabled,
                                :is_major, :is_minor, :orb, :priority,
                                :interpretation, :scoring, :micro_note
                            )
                            """
                        ),
                        params,
                    )
                    continue
                connection.execute(
                    sa.text(
                        """
                        UPDATE astral_aspect_definitions
                        SET is_enabled = :is_enabled,
                            is_major = :is_major,
                            is_minor = :is_minor,
                            default_orb_deg = :orb,
                            display_priority = :priority,
                            interpretation_weight = :interpretation,
                            scoring_weight = :scoring,
                            micro_note = :micro_note
                        WHERE reference_version_id = :version_id
                            AND aspect_id = :aspect_id
                            AND astral_system_id = :system_id
                        """
                    ),
                    params,
                )


def upgrade() -> None:
    """Applique la normalisation des aspects et injecte les valeurs de référence."""
    _rename_table_if_needed("astal_aspect_families", "astral_aspect_families")
    _create_catalog_table_if_missing("astral_aspect_families", 32)
    _create_catalog_table_if_missing("astral_default_valence", 32)
    _create_catalog_table_if_missing("astral_interpretive_valence", 64)
    _seed_catalog("astral_aspect_families", ASPECT_FAMILIES)
    _seed_catalog("astral_default_valence", DEFAULT_VALENCES)
    _seed_catalog("astral_interpretive_valence", INTERPRETIVE_VALENCES)

    needs_aspect_rebuild = not _column_exists("astral_aspects", "family") or _column_exists(
        "astral_aspects", "default_orb_deg"
    )
    if needs_aspect_rebuild:
        with op.batch_alter_table("astral_aspects", recreate="always") as batch_op:
            if not _column_exists("astral_aspects", "family"):
                batch_op.add_column(sa.Column("family", sa.Integer(), nullable=True))
            batch_op.alter_column("angle", existing_type=sa.Integer(), type_=sa.Float())
            if _column_exists("astral_aspects", "default_orb_deg"):
                batch_op.drop_column("default_orb_deg")
    elif not _foreign_key_exists("astral_aspects", ("family",), "astral_aspect_families"):
        with op.batch_alter_table("astral_aspects", recreate="always") as batch_op:
            batch_op.alter_column("angle", existing_type=sa.Integer(), type_=sa.Float())

    _seed_aspects()
    if not _foreign_key_exists("astral_aspects", ("family",), "astral_aspect_families"):
        with op.batch_alter_table("astral_aspects", recreate="always") as batch_op:
            batch_op.alter_column("family", existing_type=sa.Integer(), nullable=False)
            batch_op.create_foreign_key(
                "fk_astral_aspects_family_astral_aspect_families",
                "astral_aspect_families",
                ["family"],
                ["id"],
            )
    elif _column_exists("astral_aspects", "family"):
        with op.batch_alter_table("astral_aspects", recreate="always") as batch_op:
            batch_op.alter_column("family", existing_type=sa.Integer(), nullable=False)

    profile_columns = (
        (
            "interpretive_valence",
            sa.Column("interpretive_valence", sa.String(length=64), nullable=True),
        ),
        ("polarity_score", sa.Column("polarity_score", sa.Float(), nullable=True)),
        ("energy_type", sa.Column("energy_type", sa.String(length=64), nullable=True)),
        ("phase_behavior_json", sa.Column("phase_behavior_json", sa.Text(), nullable=True)),
        (
            "strength_thresholds_json",
            sa.Column("strength_thresholds_json", sa.Text(), nullable=True),
        ),
    )
    missing_profile_columns = [
        column
        for column_name, column in profile_columns
        if not _column_exists("astral_aspect_profiles", column_name)
    ]
    if missing_profile_columns:
        with op.batch_alter_table("astral_aspect_profiles", recreate="always") as batch_op:
            for column in missing_profile_columns:
                batch_op.add_column(column)

    if not _table_exists("astral_aspect_definitions"):
        op.create_table(
            "astral_aspect_definitions",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("reference_version_id", sa.Integer(), nullable=False),
            sa.Column("aspect_id", sa.Integer(), nullable=False),
            sa.Column("astral_system_id", sa.Integer(), nullable=False),
            sa.Column("is_enabled", sa.Boolean(), nullable=False),
            sa.Column("is_major", sa.Boolean(), nullable=False),
            sa.Column("is_minor", sa.Boolean(), nullable=False),
            sa.Column("default_orb_deg", sa.Float(), nullable=True),
            sa.Column("display_priority", sa.Integer(), nullable=True),
            sa.Column("interpretation_weight", sa.Float(), nullable=False),
            sa.Column("scoring_weight", sa.Float(), nullable=False),
            sa.Column("micro_note", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(["reference_version_id"], ["astral_reference_versions.id"]),
            sa.ForeignKeyConstraint(["aspect_id"], ["astral_aspects.id"]),
            sa.ForeignKeyConstraint(["astral_system_id"], ["astral_systems.id"]),
            sa.UniqueConstraint("reference_version_id", "aspect_id", "astral_system_id"),
        )
    _create_index_if_missing(
        "astral_aspect_definitions",
        "ix_astral_aspect_definitions_reference_version_id",
        ["reference_version_id"],
    )
    _create_index_if_missing(
        "astral_aspect_definitions",
        "ix_astral_aspect_definitions_aspect_id",
        ["aspect_id"],
    )
    _create_index_if_missing(
        "astral_aspect_definitions",
        "ix_astral_aspect_definitions_astral_system_id",
        ["astral_system_id"],
    )
    _seed_profiles()
    _seed_definitions()
    with op.batch_alter_table("astral_aspect_profiles", recreate="always") as batch_op:
        batch_op.alter_column(
            "interpretive_valence", existing_type=sa.String(length=64), nullable=False
        )
        batch_op.alter_column("polarity_score", existing_type=sa.Float(), nullable=False)
        batch_op.alter_column("energy_type", existing_type=sa.String(length=64), nullable=False)
        batch_op.alter_column("phase_behavior_json", existing_type=sa.Text(), nullable=False)
        batch_op.alter_column("strength_thresholds_json", existing_type=sa.Text(), nullable=False)


def downgrade() -> None:
    """Revient au modèle précédent des aspects."""
    op.drop_index(
        "ix_astral_aspect_definitions_astral_system_id",
        table_name="astral_aspect_definitions",
    )
    op.drop_index("ix_astral_aspect_definitions_aspect_id", table_name="astral_aspect_definitions")
    op.drop_index(
        "ix_astral_aspect_definitions_reference_version_id",
        table_name="astral_aspect_definitions",
    )
    op.drop_table("astral_aspect_definitions")
    with op.batch_alter_table("astral_aspect_profiles", recreate="always") as batch_op:
        batch_op.drop_column("strength_thresholds_json")
        batch_op.drop_column("phase_behavior_json")
        batch_op.drop_column("energy_type")
        batch_op.drop_column("polarity_score")
        batch_op.drop_column("interpretive_valence")
    with op.batch_alter_table("astral_aspects", recreate="always") as batch_op:
        batch_op.add_column(sa.Column("default_orb_deg", sa.Float(), nullable=True))
        batch_op.drop_constraint(
            "fk_astral_aspects_family_astral_aspect_families", type_="foreignkey"
        )
        batch_op.drop_column("family")
        batch_op.alter_column("angle", existing_type=sa.Float(), type_=sa.Integer())
    op.execute(
        sa.text(
            """
            UPDATE astral_aspects
            SET default_orb_deg = CASE code
                WHEN 'conjunction' THEN 8.0
                WHEN 'sextile' THEN 4.0
                WHEN 'square' THEN 6.0
                WHEN 'trine' THEN 6.0
                WHEN 'opposition' THEN 8.0
                ELSE 2.0
            END
            """
        )
    )
    with op.batch_alter_table("astral_aspects", recreate="always") as batch_op:
        batch_op.alter_column("default_orb_deg", existing_type=sa.Float(), nullable=False)
    op.drop_table("astral_interpretive_valence")
    op.drop_table("astral_default_valence")
    op.drop_table("astral_aspect_families")
