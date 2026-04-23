"""Verrouille les invariants DB LLM de release, schema et payload QA.

Revision ID: 20260423_0074
Revises: 20260422_0073
Create Date: 2026-04-23 00:00:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260423_0074"
down_revision: Union[str, Sequence[str], None] = "20260422_0073"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Applique les contraintes canoniques ajoutees par la story 70-18."""
    with op.batch_alter_table("llm_output_schemas") as batch_op:
        batch_op.drop_index("ix_llm_output_schemas_name")
        batch_op.create_index("ix_llm_output_schemas_name", ["name"], unique=False)
        batch_op.create_unique_constraint(
            "uq_llm_output_schemas_name_version",
            ["name", "version"],
        )

    with op.batch_alter_table("llm_release_snapshots") as batch_op:
        batch_op.drop_index("ix_llm_release_snapshots_version")
        batch_op.create_index("ix_llm_release_snapshots_version", ["version"], unique=False)
        batch_op.create_unique_constraint(
            "uq_llm_release_snapshots_version",
            ["version"],
        )

    with op.batch_alter_table("llm_active_releases") as batch_op:
        batch_op.create_check_constraint("ck_llm_active_releases_singleton_id", "id = 1")

    with op.batch_alter_table("llm_sample_payloads") as batch_op:
        batch_op.add_column(
            sa.Column("subfeature", sa.String(length=64), nullable=False, server_default="")
        )
        batch_op.add_column(
            sa.Column("plan", sa.String(length=64), nullable=False, server_default="")
        )
        batch_op.drop_index("ix_llm_sample_payload_feature_locale_name_unique")
        batch_op.drop_index("ix_llm_sample_payload_feature_locale_default_unique")
        batch_op.create_index(
            "ix_llm_sample_payload_feature_locale_name_unique",
            ["feature", "subfeature", "plan", "locale", "name"],
            unique=True,
        )
        batch_op.create_index(
            "ix_llm_sample_payload_feature_locale_default_unique",
            ["feature", "subfeature", "plan", "locale"],
            unique=True,
            sqlite_where=sa.text("is_default = 1"),
            postgresql_where=sa.text("is_default = true"),
        )


def downgrade() -> None:
    """Retire les contraintes ajoutees en conservant les donnees existantes."""
    with op.batch_alter_table("llm_sample_payloads") as batch_op:
        batch_op.drop_index("ix_llm_sample_payload_feature_locale_default_unique")
        batch_op.drop_index("ix_llm_sample_payload_feature_locale_name_unique")
        batch_op.create_index(
            "ix_llm_sample_payload_feature_locale_name_unique",
            ["feature", "locale", "name"],
            unique=True,
        )
        batch_op.create_index(
            "ix_llm_sample_payload_feature_locale_default_unique",
            ["feature", "locale"],
            unique=True,
            sqlite_where=sa.text("is_default = 1"),
            postgresql_where=sa.text("is_default = true"),
        )
        batch_op.drop_column("plan")
        batch_op.drop_column("subfeature")

    with op.batch_alter_table("llm_active_releases") as batch_op:
        batch_op.drop_constraint("ck_llm_active_releases_singleton_id", type_="check")

    with op.batch_alter_table("llm_release_snapshots") as batch_op:
        batch_op.drop_constraint("uq_llm_release_snapshots_version", type_="unique")
        batch_op.drop_index("ix_llm_release_snapshots_version")
        batch_op.create_index("ix_llm_release_snapshots_version", ["version"], unique=False)

    with op.batch_alter_table("llm_output_schemas") as batch_op:
        batch_op.drop_constraint("uq_llm_output_schemas_name_version", type_="unique")
        batch_op.drop_index("ix_llm_output_schemas_name")
        batch_op.create_index("ix_llm_output_schemas_name", ["name"], unique=True)
