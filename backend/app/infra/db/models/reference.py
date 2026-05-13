"""Modèles SQLAlchemy des données de référence astrologiques."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, Session, mapped_column, object_session

from app.core.datetime_provider import utc_now
from app.infra.db.base import Base


class ReferenceVersionModel(Base):
    __tablename__ = "reference_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(255), default="")
    is_locked: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class PlanetModel(Base):
    __tablename__ = "planets"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(64))


class SignModel(Base):
    __tablename__ = "signs"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(64))


class HouseModel(Base):
    __tablename__ = "houses"
    __table_args__ = (UniqueConstraint("number"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    number: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(64))


class AspectModel(Base):
    __tablename__ = "aspects"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(64))
    angle: Mapped[int] = mapped_column(Integer)
    default_orb_deg: Mapped[float] = mapped_column(Float, nullable=False)


def _ensure_reference_version_is_mutable(target: object) -> None:
    session = object_session(target)
    if session is None or not isinstance(session, Session):
        return
    reference_version_id = getattr(target, "reference_version_id", None)
    if reference_version_id is None:
        return
    version = session.get(ReferenceVersionModel, reference_version_id)
    if version is not None and version.is_locked:
        raise ValueError("reference version is immutable")
