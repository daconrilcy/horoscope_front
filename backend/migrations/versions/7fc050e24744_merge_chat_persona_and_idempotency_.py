"""merge chat persona and idempotency branches

Revision ID: 7fc050e24744
Revises: 2219fc77cb83, 20260306_0030
Create Date: 2026-03-06 21:49:51.096394
"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "7fc050e24744"
down_revision: Union[str, Sequence[str], None] = ("2219fc77cb83", "20260306_0030")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
