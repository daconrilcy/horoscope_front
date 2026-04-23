# Helpers d'index SQLAlchemy pour les modèles DB LLM.
"""Centralise les conventions d'index partiels réutilisées par les modèles LLM."""

from __future__ import annotations

from typing import Any

from sqlalchemy import Index
from sqlalchemy.sql.elements import ColumnElement


def published_unique_index(
    name: str,
    *expressions: Any,
    status_column: ColumnElement[Any],
    published_value: str = "published",
) -> Index:
    """Construit l'index partiel qui impose un seul enregistrement publié par scope."""
    published_predicate = status_column == published_value
    return Index(
        name,
        *expressions,
        unique=True,
        postgresql_where=published_predicate,
        sqlite_where=published_predicate,
    )
