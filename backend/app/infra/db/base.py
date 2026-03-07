from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all ORM models once so Base.metadata stays stable across tests and app startup.
from app.infra.db import models as _models  # noqa: E402,F401
