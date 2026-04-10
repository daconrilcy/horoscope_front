"""merge epic 65 admin migration heads

Revision ID: 20260406_0067
Revises: 133a10b2582b, fe2d4b3a1c01
Create Date: 2026-04-06 12:55:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

revision: str = "20260406_0067"
down_revision: Union[str, Sequence[str], None] = ("133a10b2582b", "fe2d4b3a1c01")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge the admin content and support branches into a single head."""


def downgrade() -> None:
    """Split the merged branches back into separate heads."""
