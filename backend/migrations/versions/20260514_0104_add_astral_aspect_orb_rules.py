"""Ajoute les règles de surcharge des orbes d'aspects.

Revision ID: 20260514_0104
Revises: 20260514_0103
Create Date: 2026-05-14
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260514_0104"
down_revision: Union[str, Sequence[str], None] = "20260514_0103"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    """Indique si une table existe dans le schéma courant."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _check_constraint_exists(table_name: str, constraint_name: str) -> bool:
    """Indique si une contrainte CHECK existe déjà."""
    return constraint_name in {
        constraint["name"]
        for constraint in sa.inspect(op.get_bind()).get_check_constraints(table_name)
    }


def _research_path(file_name: str) -> Path:
    """Construit le chemin vers les JSON de référence astrologique."""
    migration_path = Path(__file__).resolve()
    candidates = (
        migration_path.parents[3] / "docs" / "db_seeder" / "astrology" / file_name,
        migration_path.parents[2] / "docs" / "db_seeder" / "astrology" / file_name,
        migration_path.parents[3] / "docs" / "recherches astro" / file_name,
        migration_path.parents[2] / "docs" / "recherches astro" / file_name,
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise RuntimeError(f"missing astrology seed {file_name}")


def _load_rule_groups() -> list[dict[str, object]]:
    """Charge les groupes de règles d'orbes depuis la source documentaire."""
    with _research_path("astral_aspect_orb_rules.json").open(encoding="utf-8") as stream:
        raw = json.load(stream)
    groups = raw.get("seed") if isinstance(raw, dict) else None
    if not isinstance(groups, list) or not groups:
        raise RuntimeError("astral_aspect_orb_rules.json must contain a non-empty seed list")
    return groups


def _resolve_rule_groups() -> list[dict[str, object]]:
    """Retourne seulement les règles physiques locales par système."""
    final_groups: list[dict[str, object]] = []
    for group in _load_rule_groups():
        system_code = str(group["astral_system_code"])
        if "copy_rules_from" in group:
            raise RuntimeError("copy_rules_from is forbidden for aspect orb rule groups")
        rules = [dict(rule) for rule in group.get("rules", [])]
        final_groups.append({"astral_system_code": system_code, "rules": rules})
    return final_groups


def _ids_by_code(table_name: str) -> dict[str, int]:
    """Retourne le mapping code -> id pour une table de référence."""
    rows = op.get_bind().execute(sa.text(f"SELECT id, code FROM {table_name}")).mappings()
    return {str(row["code"]): int(row["id"]) for row in rows}


def _system_ids_by_name() -> dict[str, int]:
    """Retourne le mapping name -> id des systèmes astrologiques."""
    rows = op.get_bind().execute(sa.text("SELECT id, name FROM astral_systems")).mappings()
    return {str(row["name"]): int(row["id"]) for row in rows}


def _create_orb_rules_table() -> None:
    """Crée la table de surcharges d'orbes si elle est absente."""
    if _table_exists("astral_aspect_orb_rules"):
        return
    op.create_table(
        "astral_aspect_orb_rules",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("reference_version_id", sa.Integer(), nullable=False),
        sa.Column("astral_system_id", sa.Integer(), nullable=False),
        sa.Column("aspect_id", sa.Integer(), nullable=False),
        sa.Column("calculation_context", sa.String(length=32), nullable=False),
        sa.Column("source_body_type", sa.String(length=32), nullable=False),
        sa.Column("source_planet_id", sa.Integer(), nullable=True),
        sa.Column("source_point_code", sa.String(length=32), nullable=True),
        sa.Column("target_body_type", sa.String(length=32), nullable=False),
        sa.Column("target_planet_id", sa.Integer(), nullable=True),
        sa.Column("target_point_code", sa.String(length=32), nullable=True),
        sa.Column("orb_deg", sa.Float(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False),
        sa.Column("micro_note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["reference_version_id"], ["astral_reference_versions.id"]),
        sa.ForeignKeyConstraint(["astral_system_id"], ["astral_systems.id"]),
        sa.ForeignKeyConstraint(["aspect_id"], ["astral_aspects.id"]),
        sa.ForeignKeyConstraint(["source_planet_id"], ["astral_planets.id"]),
        sa.ForeignKeyConstraint(["target_planet_id"], ["astral_planets.id"]),
        sa.CheckConstraint("orb_deg > 0", name="ck_astral_aspect_orb_rules_orb_deg_positive"),
        sa.CheckConstraint("priority >= 0", name="ck_astral_aspect_orb_rules_priority_positive"),
        sa.CheckConstraint(
            (
                "source_planet_id IS NULL OR source_body_type IN "
                "('planet', 'luminary', 'personal_planet', 'social_planet', "
                "'transpersonal_planet')"
            ),
            name="ck_astral_aspect_orb_rules_source_planet_type",
        ),
        sa.CheckConstraint(
            (
                "target_planet_id IS NULL OR target_body_type IN "
                "('planet', 'luminary', 'personal_planet', 'social_planet', "
                "'transpersonal_planet')"
            ),
            name="ck_astral_aspect_orb_rules_target_planet_type",
        ),
        sa.UniqueConstraint(
            "reference_version_id",
            "astral_system_id",
            "aspect_id",
            "calculation_context",
            "source_body_type",
            "source_planet_id",
            "source_point_code",
            "target_body_type",
            "target_planet_id",
            "target_point_code",
        ),
    )
    op.create_index(
        "ix_astral_aspect_orb_rules_reference_system_aspect",
        "astral_aspect_orb_rules",
        ["reference_version_id", "astral_system_id", "aspect_id"],
    )
    op.create_index(
        "ix_astral_aspect_orb_rules_calculation_context",
        "astral_aspect_orb_rules",
        ["calculation_context"],
    )
    op.create_index(
        "ix_astral_aspect_orb_rules_priority",
        "astral_aspect_orb_rules",
        ["priority"],
    )


def _enforce_enabled_aspect_default_orb() -> None:
    """Rend default_orb_deg obligatoire pour tout aspect activé."""
    constraint_name = "ck_astral_aspect_definitions_enabled_default_orb"
    if _check_constraint_exists("astral_aspect_definitions", constraint_name):
        return
    with op.batch_alter_table("astral_aspect_definitions", recreate="always") as batch_op:
        batch_op.create_check_constraint(
            constraint_name,
            "is_enabled IS NOT TRUE OR default_orb_deg IS NOT NULL",
        )


def _seed_orb_rules() -> None:
    """Insère les surcharges d'orbes pour chaque version existante."""
    connection = op.get_bind()
    version_ids = [
        int(row[0])
        for row in connection.execute(sa.text("SELECT id FROM astral_reference_versions")).all()
    ]
    if not version_ids:
        return
    aspect_ids = _ids_by_code("astral_aspects")
    system_ids = _system_ids_by_name()
    planet_ids = _ids_by_code("astral_planets")
    rules_table = sa.table(
        "astral_aspect_orb_rules",
        sa.column("id", sa.Integer()),
        sa.column("reference_version_id", sa.Integer()),
        sa.column("astral_system_id", sa.Integer()),
        sa.column("aspect_id", sa.Integer()),
        sa.column("calculation_context", sa.String()),
        sa.column("source_body_type", sa.String()),
        sa.column("source_planet_id", sa.Integer()),
        sa.column("source_point_code", sa.String()),
        sa.column("target_body_type", sa.String()),
        sa.column("target_planet_id", sa.Integer()),
        sa.column("target_point_code", sa.String()),
        sa.column("orb_deg", sa.Float()),
        sa.column("priority", sa.Integer()),
        sa.column("is_enabled", sa.Boolean()),
        sa.column("micro_note", sa.Text()),
    )
    for version_id in version_ids:
        for group in _resolve_rule_groups():
            system_id = system_ids[str(group["astral_system_code"])]
            for rule in group["rules"]:
                source_planet_code = rule.get("source_planet_code")
                target_planet_code = rule.get("target_planet_code")
                payload = {
                    "reference_version_id": version_id,
                    "astral_system_id": system_id,
                    "aspect_id": aspect_ids[str(rule["aspect_code"])],
                    "calculation_context": str(rule["calculation_context"]),
                    "source_body_type": str(rule["source_body_type"]),
                    "source_planet_id": (
                        None if source_planet_code is None else planet_ids[str(source_planet_code)]
                    ),
                    "source_point_code": rule.get("source_point_code"),
                    "target_body_type": str(rule["target_body_type"]),
                    "target_planet_id": (
                        None if target_planet_code is None else planet_ids[str(target_planet_code)]
                    ),
                    "target_point_code": rule.get("target_point_code"),
                    "orb_deg": float(rule["orb_deg"]),
                    "priority": int(rule["priority"]),
                    "is_enabled": bool(rule["is_enabled"]),
                    "micro_note": rule.get("micro_note"),
                }
                existing_id = connection.execute(
                    sa.select(rules_table.c.id).where(
                        rules_table.c.reference_version_id == payload["reference_version_id"],
                        rules_table.c.astral_system_id == payload["astral_system_id"],
                        rules_table.c.aspect_id == payload["aspect_id"],
                        rules_table.c.calculation_context == payload["calculation_context"],
                        rules_table.c.source_body_type == payload["source_body_type"],
                        rules_table.c.source_planet_id == payload["source_planet_id"],
                        rules_table.c.source_point_code == payload["source_point_code"],
                        rules_table.c.target_body_type == payload["target_body_type"],
                        rules_table.c.target_planet_id == payload["target_planet_id"],
                        rules_table.c.target_point_code == payload["target_point_code"],
                    )
                ).scalar_one_or_none()
                if existing_id is None:
                    connection.execute(sa.insert(rules_table).values(**payload))
                    continue
                connection.execute(
                    sa.update(rules_table)
                    .where(rules_table.c.id == existing_id)
                    .values(
                        orb_deg=payload["orb_deg"],
                        priority=payload["priority"],
                        is_enabled=payload["is_enabled"],
                        micro_note=payload["micro_note"],
                    )
                )


def upgrade() -> None:
    """Crée et seed les règles d'orbes spécifiques."""
    _create_orb_rules_table()
    _enforce_enabled_aspect_default_orb()
    _seed_orb_rules()


def downgrade() -> None:
    """Supprime les règles de surcharge d'orbes."""
    if _table_exists("astral_aspect_definitions") and _check_constraint_exists(
        "astral_aspect_definitions",
        "ck_astral_aspect_definitions_enabled_default_orb",
    ):
        with op.batch_alter_table("astral_aspect_definitions", recreate="always") as batch_op:
            batch_op.drop_constraint(
                "ck_astral_aspect_definitions_enabled_default_orb",
                type_="check",
            )
    if not _table_exists("astral_aspect_orb_rules"):
        return
    op.drop_index(
        "ix_astral_aspect_orb_rules_priority",
        table_name="astral_aspect_orb_rules",
    )
    op.drop_index(
        "ix_astral_aspect_orb_rules_calculation_context",
        table_name="astral_aspect_orb_rules",
    )
    op.drop_index(
        "ix_astral_aspect_orb_rules_reference_system_aspect",
        table_name="astral_aspect_orb_rules",
    )
    op.drop_table("astral_aspect_orb_rules")
