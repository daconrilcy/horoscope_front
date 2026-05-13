"""Modèles SQLAlchemy des données de référence astrologiques."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, Session, mapped_column, object_session, relationship

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
    """Planète astrologique stable utilisée comme vocabulaire canonique."""

    __tablename__ = "astral_planets"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(64))


class AstralSignModel(Base):
    """Signe astrologique stable, indépendant des versions de paramétrage."""

    __tablename__ = "astral_signs"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(64))


class AstralElementModel(Base):
    """Taxonomie stable des éléments astrologiques."""

    __tablename__ = "astral_elements"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)


class AstralModalityModel(Base):
    """Taxonomie stable des modalités astrologiques."""

    __tablename__ = "astral_modalities"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)


class AstralPolarityModel(Base):
    """Taxonomie stable des polarités astrologiques."""

    __tablename__ = "astral_polarities"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)


class AstralDignityTypeModel(Base):
    """Taxonomie stable des types de dignités astrologiques."""

    __tablename__ = "astral_dignity_type"
    __table_args__ = (UniqueConstraint("code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)


class AstralSignProfileModel(Base):
    """Profil structurel canonique d'un signe astrologique."""

    __tablename__ = "astral_sign_profiles"
    __table_args__ = (UniqueConstraint("astral_sign_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    astral_sign_id: Mapped[int] = mapped_column(
        ForeignKey("astral_signs.id"), nullable=False, index=True
    )
    astral_element_id: Mapped[int] = mapped_column(
        ForeignKey("astral_elements.id"), nullable=False, index=True
    )
    astral_modality_id: Mapped[int] = mapped_column(
        ForeignKey("astral_modalities.id"), nullable=False, index=True
    )
    astral_polarity_id: Mapped[int] = mapped_column(
        ForeignKey("astral_polarities.id"), nullable=False, index=True
    )
    keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    shadow_keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    sign: Mapped["AstralSignModel"] = relationship()
    element: Mapped["AstralElementModel"] = relationship()
    modality: Mapped["AstralModalityModel"] = relationship()
    polarity: Mapped["AstralPolarityModel"] = relationship()


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
