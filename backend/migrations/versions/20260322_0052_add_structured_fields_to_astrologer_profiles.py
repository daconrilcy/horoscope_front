"""add structured fields to astrologer_profiles

Revision ID: 20260322_0052
Revises: c5c208c81831
Create Date: 2026-03-22 21:05:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260322_0052"
down_revision = "c5c208c81831"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("astrologer_profiles", sa.Column("age", sa.Integer(), nullable=True))
    op.add_column(
        "astrologer_profiles",
        sa.Column(
            "professional_background",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
    )
    op.add_column(
        "astrologer_profiles",
        sa.Column(
            "key_skills",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
    )
    op.add_column(
        "astrologer_profiles",
        sa.Column(
            "behavioral_style",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
    )


def downgrade() -> None:
    op.drop_column("astrologer_profiles", "behavioral_style")
    op.drop_column("astrologer_profiles", "key_skills")
    op.drop_column("astrologer_profiles", "professional_background")
    op.drop_column("astrologer_profiles", "age")
