from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.user import UserModel


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, email: str, password_hash: str, role: str) -> UserModel:
        model = UserModel(email=email, password_hash=password_hash, role=role)
        self.db.add(model)
        self.db.flush()
        return model

    def get_by_email(self, email: str) -> UserModel | None:
        return self.db.scalar(select(UserModel).where(UserModel.email == email))

    def get_by_id(self, user_id: int) -> UserModel | None:
        return self.db.scalar(select(UserModel).where(UserModel.id == user_id))
