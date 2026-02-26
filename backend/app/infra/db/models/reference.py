from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    event,
)
from sqlalchemy.orm import Mapped, Session, mapped_column, object_session, relationship

from app.infra.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ReferenceVersionModel(Base):
    __tablename__ = "reference_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(255), default="")
    is_locked: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    planets: Mapped[list["PlanetModel"]] = relationship(back_populates="reference_version")
    signs: Mapped[list["SignModel"]] = relationship(back_populates="reference_version")
    houses: Mapped[list["HouseModel"]] = relationship(back_populates="reference_version")
    aspects: Mapped[list["AspectModel"]] = relationship(back_populates="reference_version")
    characteristics: Mapped[list["AstroCharacteristicModel"]] = relationship(
        back_populates="reference_version"
    )


class PlanetModel(Base):
    __tablename__ = "planets"
    __table_args__ = (UniqueConstraint("reference_version_id", "code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("reference_versions.id"),
        index=True,
    )
    code: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(64))

    reference_version: Mapped[ReferenceVersionModel] = relationship(back_populates="planets")


class SignModel(Base):
    __tablename__ = "signs"
    __table_args__ = (UniqueConstraint("reference_version_id", "code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("reference_versions.id"),
        index=True,
    )
    code: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(64))

    reference_version: Mapped[ReferenceVersionModel] = relationship(back_populates="signs")


class HouseModel(Base):
    __tablename__ = "houses"
    __table_args__ = (UniqueConstraint("reference_version_id", "number"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("reference_versions.id"),
        index=True,
    )
    number: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(64))

    reference_version: Mapped[ReferenceVersionModel] = relationship(back_populates="houses")


class AspectModel(Base):
    __tablename__ = "aspects"
    __table_args__ = (UniqueConstraint("reference_version_id", "code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("reference_versions.id"),
        index=True,
    )
    code: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(64))
    angle: Mapped[int] = mapped_column(Integer)
    default_orb_deg: Mapped[float] = mapped_column(Float, nullable=False)

    reference_version: Mapped[ReferenceVersionModel] = relationship(back_populates="aspects")


class AstroCharacteristicModel(Base):
    __tablename__ = "astro_characteristics"
    __table_args__ = (
        UniqueConstraint(
            "reference_version_id",
            "entity_type",
            "entity_code",
            "trait",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_version_id: Mapped[int] = mapped_column(
        ForeignKey("reference_versions.id"),
        index=True,
    )
    entity_type: Mapped[str] = mapped_column(String(32), index=True)
    entity_code: Mapped[str] = mapped_column(String(64), index=True)
    trait: Mapped[str] = mapped_column(String(64))
    value: Mapped[str] = mapped_column(Text)

    reference_version: Mapped[ReferenceVersionModel] = relationship(
        back_populates="characteristics"
    )


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


@event.listens_for(PlanetModel, "before_update")
@event.listens_for(SignModel, "before_update")
@event.listens_for(HouseModel, "before_update")
@event.listens_for(AspectModel, "before_update")
@event.listens_for(AstroCharacteristicModel, "before_update")
def _prevent_update_on_locked_reference_version(
    mapper: object, connection: object, target: object
) -> None:
    del mapper, connection
    _ensure_reference_version_is_mutable(target)
