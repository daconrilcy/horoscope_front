"""add user visibility flags to billing_plans

Revision ID: 20260402_0066
Revises: 20260401_0065
Create Date: 2026-04-02 19:05:00
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260402_0066"
down_revision = "20260401_0065"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("billing_plans")}

    if "is_visible_to_users" not in existing_columns:
        op.add_column(
            "billing_plans",
            sa.Column(
                "is_visible_to_users",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
        )
    if "is_available_to_users" not in existing_columns:
        op.add_column(
            "billing_plans",
            sa.Column(
                "is_available_to_users",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
        )

    op.execute(
        sa.text(
            """
            UPDATE billing_plans
            SET is_visible_to_users = false,
                is_available_to_users = false
            WHERE code = 'trial'
            """
        )
    )

def downgrade() -> None:
    op.drop_column("billing_plans", "is_available_to_users")
    op.drop_column("billing_plans", "is_visible_to_users")
