"""Purge les tables locales astrology/LLM et ajoute les dates partielles.

Revision ID: 20260622_0144
Revises: 20260601_0143
Create Date: 2026-06-22
"""

from __future__ import annotations

from collections.abc import Iterable

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260622_0144"
down_revision = "20260601_0143"
branch_labels = None
depends_on = None


LEGACY_TABLES: tuple[str, ...] = (
    "astral_chart_planet_dignity_results",
    "astrologer_prompt_profiles",
    "astrologer_reviews",
    "astrologer_profiles",
    "calibration_raw_days",
    "category_calibrations",
    "chart_results",
    "chat_messages",
    "chat_conversations",
    "consultation_third_party_usages",
    "consultation_third_party_profiles",
    "consultation_templates",
    "daily_prediction_category_scores",
    "daily_prediction_time_blocks",
    "daily_prediction_turning_points",
    "daily_prediction_runs",
    "editorial_template_versions",
    "enterprise_editorial_configs",
    "house_system_resolutions",
    "interpretation_references",
    "llm_call_log_operational_metadata",
    "llm_call_logs",
    "llm_canonical_consumption_aggregates",
    "llm_generation_runs",
    "llm_release_snapshots",
    "llm_replay_snapshots",
    "llm_active_releases",
    "llm_assembly_configs",
    "llm_execution_profiles",
    "llm_output_schemas",
    "llm_personas",
    "llm_prompt_versions",
    "llm_sample_payloads",
    "llm_use_case_configs",
    "pdf_templates",
    "persisted_projections",
    "persona_configs",
    "prediction_categories",
    "prediction_references",
    "prediction_rulesets",
    "ruleset_event_types",
    "ruleset_parameters",
    "theme_natal_reading_slots",
    "translation_references",
    "user_natal_interpretations",
    "user_prediction_baselines",
)


def _table_names() -> set[str]:
    """Retourne les tables visibles dans la connexion courante."""
    return set(sa.inspect(op.get_bind()).get_table_names())


def _column_names(table_name: str) -> set[str]:
    """Retourne les colonnes existantes d'une table."""
    inspector = sa.inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return set()
    return {str(column["name"]) for column in inspector.get_columns(table_name)}


def _drop_existing_tables(table_names: Iterable[str]) -> None:
    """Supprime les tables legacy présentes, dans l'ordre fourni."""
    existing = _table_names()
    for table_name in table_names:
        if table_name in existing:
            op.drop_table(table_name)
            existing.remove(table_name)


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    """Ajoute une colonne uniquement si elle n'existe pas déjà."""
    if column.name not in _column_names(table_name):
        op.add_column(table_name, column)


def _drop_column_if_present(table_name: str, column_name: str) -> None:
    """Supprime une colonne uniquement si elle existe encore."""
    if column_name in _column_names(table_name):
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.drop_column(column_name)


def upgrade() -> None:
    """Applique la purge destructive des surfaces locales externalisées."""
    if "user_birth_profiles" in _table_names():
        _add_column_if_missing("user_birth_profiles", sa.Column("birth_year", sa.Integer()))
        _add_column_if_missing("user_birth_profiles", sa.Column("birth_month", sa.Integer()))
        _add_column_if_missing("user_birth_profiles", sa.Column("birth_day", sa.Integer()))
        _add_column_if_missing(
            "user_birth_profiles",
            sa.Column("birth_date_precision", sa.String(length=16), nullable=True),
        )
        op.execute(
            """
            UPDATE user_birth_profiles
            SET
                birth_year = COALESCE(birth_year, CAST(strftime('%Y', birth_date) AS INTEGER)),
                birth_month = COALESCE(birth_month, CAST(strftime('%m', birth_date) AS INTEGER)),
                birth_day = COALESCE(birth_day, CAST(strftime('%d', birth_date) AS INTEGER)),
                birth_date_precision = COALESCE(birth_date_precision, 'full')
            WHERE birth_date IS NOT NULL
            """
        )
        op.execute(
            """
            UPDATE user_birth_profiles
            SET birth_date_precision = COALESCE(birth_date_precision, 'year')
            WHERE birth_date IS NULL
            """
        )
        with op.batch_alter_table("user_birth_profiles") as batch_op:
            batch_op.alter_column("birth_date", existing_type=sa.Date(), nullable=True)
            batch_op.alter_column(
                "birth_date_precision",
                existing_type=sa.String(length=16),
                nullable=False,
            )

    if "users" in _table_names():
        _drop_column_if_present("users", "astrologer_profile")
        _drop_column_if_present("users", "default_astrologer_id")

    if "user_token_usage_logs" in _table_names():
        _drop_column_if_present("user_token_usage_logs", "llm_call_log_id")

    _drop_existing_tables(LEGACY_TABLES)


def downgrade() -> None:
    """La purge destructive des tables externalisées n'est pas réversible."""
    raise RuntimeError("Destructive externalization purge cannot be downgraded")
