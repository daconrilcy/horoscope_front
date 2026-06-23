# Base declarative commune et chargement centralise des registres ORM.
"""Expose la base declarative et charge les registres de modeles SQLAlchemy."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarative partagee par tous les modeles SQLAlchemy applicatifs."""

    pass


# Charge les registres ORM une seule fois pour stabiliser Base.metadata.
from app.infra.db import models as _models  # noqa: E402,F401
