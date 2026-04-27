"""Exceptions applicatives partagées hors de la couche HTTP."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(kw_only=True)
class ApplicationError(Exception):
    """Erreur applicative typée convertible par la couche API."""

    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] | None = None
    request_id: str | None = None

    def __post_init__(self) -> None:
        """Initialise le message natif d'exception sans dépendance FastAPI."""
        if self.details is None:
            self.details = {}
        Exception.__init__(self, self.message)
