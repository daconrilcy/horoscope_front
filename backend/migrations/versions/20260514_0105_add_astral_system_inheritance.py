"""Ajoute l'heritage explicite des systemes astrologiques.

Revision ID: 20260514_0105
Revises: 20260514_0104
Create Date: 2026-05-14
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260514_0105"
down_revision: Union[str, Sequence[str], None] = "20260514_0104"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute la self-FK et initialise l'heritage connu."""
    with op.batch_alter_table("astral_systems", recreate="always") as batch_op:
        batch_op.add_column(sa.Column("inherits_from_system_id", sa.Integer(), nullable=True))
        batch_op.create_index(
            "ix_astral_systems_inherits_from_system_id",
            ["inherits_from_system_id"],
            unique=False,
        )
        batch_op.create_foreign_key(
            "fk_astral_systems_inherits_from_system_id",
            "astral_systems",
            ["inherits_from_system_id"],
            ["id"],
        )

    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            UPDATE astral_systems
            SET inherits_from_system_id = (
                SELECT parent.id
                FROM astral_systems AS parent
                WHERE parent.name = 'traditional'
            )
            WHERE name IN ('hellenistic', 'medieval')
            """
        )
    )
    connection.execute(
        sa.text(
            """
            DELETE FROM astral_aspect_orb_rules
            WHERE astral_system_id IN (
                SELECT id
                FROM astral_systems
                WHERE name IN ('hellenistic', 'medieval')
            )
            AND EXISTS (
                SELECT 1
                FROM astral_aspect_orb_rules AS parent_rule
                JOIN astral_systems AS parent_system
                    ON parent_rule.astral_system_id = parent_system.id
                WHERE parent_system.name = 'traditional'
                    AND parent_rule.reference_version_id =
                        astral_aspect_orb_rules.reference_version_id
                    AND parent_rule.aspect_id = astral_aspect_orb_rules.aspect_id
                    AND parent_rule.calculation_context =
                        astral_aspect_orb_rules.calculation_context
                    AND parent_rule.source_body_type = astral_aspect_orb_rules.source_body_type
                    AND (
                        parent_rule.source_planet_id =
                            astral_aspect_orb_rules.source_planet_id
                        OR (
                            parent_rule.source_planet_id IS NULL
                            AND astral_aspect_orb_rules.source_planet_id IS NULL
                        )
                    )
                    AND (
                        parent_rule.source_point_code =
                            astral_aspect_orb_rules.source_point_code
                        OR (
                            parent_rule.source_point_code IS NULL
                            AND astral_aspect_orb_rules.source_point_code IS NULL
                        )
                    )
                    AND parent_rule.target_body_type = astral_aspect_orb_rules.target_body_type
                    AND (
                        parent_rule.target_planet_id =
                            astral_aspect_orb_rules.target_planet_id
                        OR (
                            parent_rule.target_planet_id IS NULL
                            AND astral_aspect_orb_rules.target_planet_id IS NULL
                        )
                    )
                    AND (
                        parent_rule.target_point_code =
                            astral_aspect_orb_rules.target_point_code
                        OR (
                            parent_rule.target_point_code IS NULL
                            AND astral_aspect_orb_rules.target_point_code IS NULL
                        )
                    )
                    AND parent_rule.orb_deg = astral_aspect_orb_rules.orb_deg
                    AND parent_rule.priority = astral_aspect_orb_rules.priority
                    AND parent_rule.is_enabled = astral_aspect_orb_rules.is_enabled
            )
            """
        )
    )


def downgrade() -> None:
    """Supprime la self-FK d'heritage des systemes astrologiques."""
    with op.batch_alter_table("astral_systems", recreate="always") as batch_op:
        batch_op.drop_constraint("fk_astral_systems_inherits_from_system_id", type_="foreignkey")
        batch_op.drop_index("ix_astral_systems_inherits_from_system_id")
        batch_op.drop_column("inherits_from_system_id")
