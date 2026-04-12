"""add input_schema to assembly

Revision ID: 8b2d52442493
Revises: 8a839be9fea4
Create Date: 2026-04-11 15:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8b2d52442493"
down_revision: Union[str, Sequence[str], None] = "8a839be9fea4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Story 66.29: Add input_schema column to llm_assembly_configs for Stage 1.5 validation support
    op.add_column("llm_assembly_configs", sa.Column("input_schema", sa.JSON(), nullable=True))

    # Backfill: Sync input_schema and interaction metadata from legacy llm_use_case_configs
    # We join assembly -> prompt_version -> use_case_config
    connection = op.get_bind()

    # 1. Backfill input_schema
    connection.execute(
        sa.text("""
        UPDATE llm_assembly_configs
        SET input_schema = (
            SELECT ucc.input_schema
            FROM llm_use_case_configs ucc
            JOIN llm_prompt_versions lpv ON ucc.key = lpv.use_case_key
            WHERE lpv.id = llm_assembly_configs.feature_template_ref
        )
        WHERE input_schema IS NULL;
    """)
    )

    # 2. Backfill output_contract_ref (from ucc.output_schema_id)
    connection.execute(
        sa.text("""
        UPDATE llm_assembly_configs
        SET output_contract_ref = (
            SELECT ucc.output_schema_id
            FROM llm_use_case_configs ucc
            JOIN llm_prompt_versions lpv ON ucc.key = lpv.use_case_key
            WHERE lpv.id = llm_assembly_configs.feature_template_ref
        )
        WHERE output_contract_ref IS NULL;
    """)
    )

    # 3. Backfill interaction_mode and user_question_policy
    # (Only if they are at their default values to avoid overwriting intentional overrides)
    connection.execute(
        sa.text("""
        UPDATE llm_assembly_configs
        SET interaction_mode = (
            SELECT ucc.interaction_mode
            FROM llm_use_case_configs ucc
            JOIN llm_prompt_versions lpv ON ucc.key = lpv.use_case_key
            WHERE lpv.id = llm_assembly_configs.feature_template_ref
        )
        WHERE interaction_mode = 'structured';
    """)
    )

    connection.execute(
        sa.text("""
        UPDATE llm_assembly_configs
        SET user_question_policy = (
            SELECT ucc.user_question_policy
            FROM llm_use_case_configs ucc
            JOIN llm_prompt_versions lpv ON ucc.key = lpv.use_case_key
            WHERE lpv.id = llm_assembly_configs.feature_template_ref
        )
        WHERE user_question_policy = 'none';
    """)
    )


def downgrade() -> None:
    op.drop_column("llm_assembly_configs", "input_schema")
