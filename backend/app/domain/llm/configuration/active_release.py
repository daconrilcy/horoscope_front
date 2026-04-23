"""Lecture release active — évite les imports circulaires coherence ↔ release."""

from __future__ import annotations

import uuid
from typing import Optional, Union

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.infra.db.models.llm.llm_release import LlmActiveReleaseModel


async def get_active_release_id(session: Union[AsyncSession, Session]) -> Optional[uuid.UUID]:
    """Identifiant du snapshot de release actuellement activé (Story 66.32)."""
    stmt = (
        select(LlmActiveReleaseModel.release_snapshot_id)
        .order_by(desc(LlmActiveReleaseModel.activated_at))
        .limit(1)
    )
    if isinstance(session, AsyncSession):
        res = await session.execute(stmt)
    else:
        res = session.execute(stmt)
    return res.scalar_one_or_none()
