"""add astrologer_profile to users

Revision ID: 20260320_0050
Revises: a63994cb990f
Create Date: 2026-03-20 00:50:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260320_0050"
down_revision = "a63994cb990f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "astrologer_profile", sa.String(length=32), nullable=False, server_default="standard"
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "astrologer_profile")
