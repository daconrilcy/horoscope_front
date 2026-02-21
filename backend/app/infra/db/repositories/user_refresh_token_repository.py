from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.user_refresh_token import UserRefreshTokenModel


class UserRefreshTokenRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_user_id(self, user_id: int) -> UserRefreshTokenModel | None:
        return self.db.scalar(
            select(UserRefreshTokenModel).where(UserRefreshTokenModel.user_id == user_id).limit(1)
        )

    def upsert_current_jti(self, user_id: int, jti: str) -> UserRefreshTokenModel:
        existing = self.get_by_user_id(user_id)
        if existing is not None:
            existing.current_jti = jti
            self.db.flush()
            return existing
        created = UserRefreshTokenModel(user_id=user_id, current_jti=jti)
        self.db.add(created)
        self.db.flush()
        return created
