# Repository canonique des projections persistées.
"""Centralise les écritures et lectures filtrées des projections internes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.infra.db.models.projection_persistence import PersistedProjectionModel

ProjectionAccessRole = Literal["owner", "internal_audit", "admin"]


@dataclass(frozen=True, slots=True)
class ProjectionAccessScope:
    """Décrit le périmètre de lecture autorisé pour une projection."""

    role: ProjectionAccessRole
    user_id: int | None = None


class ProjectionRepository:
    """Persiste et relit les projections avec filtres explicites."""

    def __init__(self, db: Session) -> None:
        """Initialise le repository avec la session SQLAlchemy courante."""
        self.db = db

    def create(
        self,
        *,
        chart_id: str,
        user_id: int,
        projection_type: str,
        projection_version: str,
        projection_hash: str,
        payload: dict[str, object],
        source_versions: dict[str, object],
        source: str,
        generated_at: datetime | None = None,
    ) -> PersistedProjectionModel:
        """Ajoute une projection persistée complète."""
        model = PersistedProjectionModel(
            chart_id=chart_id,
            user_id=user_id,
            projection_type=projection_type,
            projection_version=projection_version,
            projection_hash=projection_hash,
            payload=payload,
            source_versions=source_versions,
            source=source,
        )
        if generated_at is not None:
            model.generated_at = generated_at
        self.db.add(model)
        self.db.flush()
        return model

    def get_latest_for_scope(
        self,
        *,
        projection_type: str,
        projection_version: str,
        access_scope: ProjectionAccessScope,
    ) -> PersistedProjectionModel | None:
        """Relit la dernière projection en exigeant type, version et scope."""
        statement = (
            select(PersistedProjectionModel)
            .where(PersistedProjectionModel.projection_type == projection_type)
            .where(PersistedProjectionModel.projection_version == projection_version)
            .order_by(
                desc(PersistedProjectionModel.generated_at),
                desc(PersistedProjectionModel.id),
            )
            .limit(1)
        )
        statement = _apply_access_scope(statement, access_scope)
        return self.db.scalar(statement)

    def get_by_hash_for_scope(
        self,
        *,
        projection_type: str,
        projection_version: str,
        projection_hash: str,
        access_scope: ProjectionAccessScope,
    ) -> PersistedProjectionModel | None:
        """Relit une projection par identité auditée et scope explicite."""
        statement = (
            select(PersistedProjectionModel)
            .where(PersistedProjectionModel.projection_type == projection_type)
            .where(PersistedProjectionModel.projection_version == projection_version)
            .where(PersistedProjectionModel.projection_hash == projection_hash)
            .limit(1)
        )
        statement = _apply_access_scope(statement, access_scope)
        return self.db.scalar(statement)


def _apply_access_scope(statement, access_scope: ProjectionAccessScope):
    """Ajoute le filtre de propriétaire pour les lectures owner."""
    if access_scope.role == "owner":
        if access_scope.user_id is None:
            raise ValueError("Projection owner access requires user_id")
        return statement.where(PersistedProjectionModel.user_id == access_scope.user_id)
    if access_scope.role in {"internal_audit", "admin"}:
        return statement
    raise ValueError("Unsupported projection access role")
