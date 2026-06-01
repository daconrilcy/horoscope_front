# Commentaire global: migration des slots publics theme natal et runs LLM techniques.
"""Create theme natal public reading slots and LLM generation runs."""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260601_0142"
down_revision: Union[str, Sequence[str], None] = "20260530_0141"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SLOT_STATUSES = (
    "empty",
    "generating",
    "accepted",
    "rejected",
    "failed_retriable",
    "superseded",
)
RUN_STATUSES = (
    "generating",
    "accepted",
    "rejected",
    "failed_retriable",
    "superseded",
)


def upgrade() -> None:
    """Cree la separation structurelle entre slot public et tentative LLM."""
    op.create_table(
        "theme_natal_reading_slots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("chart_id", sa.String(length=64), nullable=False),
        sa.Column("feature", sa.String(length=64), nullable=False),
        sa.Column("reading_kind", sa.String(length=64), nullable=False),
        sa.Column("product_plan", sa.String(length=32), nullable=False),
        sa.Column("output_variant", sa.String(length=64), nullable=False),
        sa.Column("persona_profile_id", sa.UUID(), nullable=True),
        sa.Column("contract_version", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("public_payload", sa.JSON(), nullable=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_generation_run_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            f"status IN {SLOT_STATUSES}",
            name="ck_theme_natal_reading_slots_status",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_theme_natal_reading_slots_chart_id",
        "theme_natal_reading_slots",
        ["chart_id"],
    )
    op.create_index(
        "ix_theme_natal_reading_slots_created_at",
        "theme_natal_reading_slots",
        ["created_at"],
    )
    op.create_index(
        "ix_theme_natal_reading_slots_public_lookup",
        "theme_natal_reading_slots",
        ["user_id", "chart_id", "status", "created_at"],
    )
    op.create_index(
        "ix_theme_natal_reading_slots_source_generation_run_id",
        "theme_natal_reading_slots",
        ["source_generation_run_id"],
    )
    op.create_index(
        "ix_theme_natal_reading_slots_user_id", "theme_natal_reading_slots", ["user_id"]
    )
    op.create_index(
        "uq_theme_natal_reading_slots_null_persona",
        "theme_natal_reading_slots",
        [
            "user_id",
            "chart_id",
            "feature",
            "reading_kind",
            "product_plan",
            "output_variant",
            "contract_version",
        ],
        unique=True,
        postgresql_where=sa.text("persona_profile_id IS NULL"),
        sqlite_where=sa.text("persona_profile_id IS NULL"),
    )
    op.create_index(
        "uq_theme_natal_reading_slots_with_persona",
        "theme_natal_reading_slots",
        [
            "user_id",
            "chart_id",
            "feature",
            "reading_kind",
            "product_plan",
            "output_variant",
            "persona_profile_id",
            "contract_version",
        ],
        unique=True,
        postgresql_where=sa.text("persona_profile_id IS NOT NULL"),
        sqlite_where=sa.text("persona_profile_id IS NOT NULL"),
    )

    op.create_table(
        "llm_generation_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("slot_id", sa.Integer(), nullable=False),
        sa.Column("client_request_id", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("raw_provider_response", sa.JSON(), nullable=True),
        sa.Column("parsed_raw_response", sa.JSON(), nullable=True),
        sa.Column("validation_errors", sa.JSON(), nullable=True),
        sa.Column("rejection_reason", sa.JSON(), nullable=True),
        sa.Column("prompt_hash", sa.String(length=128), nullable=True),
        sa.Column("data_hash", sa.String(length=128), nullable=True),
        sa.Column("engine_profile_version", sa.String(length=128), nullable=True),
        sa.Column("output_schema_version", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            f"status IN {RUN_STATUSES}",
            name="ck_llm_generation_runs_status",
        ),
        sa.ForeignKeyConstraint(["slot_id"], ["theme_natal_reading_slots.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_llm_generation_runs_created_at", "llm_generation_runs", ["created_at"])
    op.create_index("ix_llm_generation_runs_slot_id", "llm_generation_runs", ["slot_id"])
    op.create_index(
        "ix_llm_generation_runs_slot_status",
        "llm_generation_runs",
        ["slot_id", "status", "created_at"],
    )
    op.create_index(
        "uq_llm_generation_runs_slot_client_request",
        "llm_generation_runs",
        ["slot_id", "client_request_id"],
        unique=True,
    )


def downgrade() -> None:
    """Supprime les tables cible sans toucher aux interpretations legacy."""
    op.drop_index("uq_llm_generation_runs_slot_client_request", table_name="llm_generation_runs")
    op.drop_index("ix_llm_generation_runs_slot_status", table_name="llm_generation_runs")
    op.drop_index("ix_llm_generation_runs_slot_id", table_name="llm_generation_runs")
    op.drop_index("ix_llm_generation_runs_created_at", table_name="llm_generation_runs")
    op.drop_table("llm_generation_runs")

    op.drop_index(
        "uq_theme_natal_reading_slots_with_persona",
        table_name="theme_natal_reading_slots",
    )
    op.drop_index(
        "uq_theme_natal_reading_slots_null_persona",
        table_name="theme_natal_reading_slots",
    )
    op.drop_index("ix_theme_natal_reading_slots_user_id", table_name="theme_natal_reading_slots")
    op.drop_index(
        "ix_theme_natal_reading_slots_source_generation_run_id",
        table_name="theme_natal_reading_slots",
    )
    op.drop_index(
        "ix_theme_natal_reading_slots_public_lookup",
        table_name="theme_natal_reading_slots",
    )
    op.drop_index("ix_theme_natal_reading_slots_created_at", table_name="theme_natal_reading_slots")
    op.drop_index("ix_theme_natal_reading_slots_chart_id", table_name="theme_natal_reading_slots")
    op.drop_table("theme_natal_reading_slots")
