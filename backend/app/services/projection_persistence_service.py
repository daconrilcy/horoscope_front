# Service applicatif de persistance des projections internes.
"""Orchestre builder réel, hash canonique et repository de projection."""

from __future__ import annotations

from typing import Any, Protocol

from app.domain.astrology.projections.projection_hash import (
    compute_projection_hash,
    projection_value_to_jsonable,
)
from app.infra.db.models.projection_persistence import PersistedProjectionModel
from app.infra.db.repositories.projection_repository import ProjectionRepository


class ProjectionPayloadBuilder(Protocol):
    """Contrat minimal d'un builder réel de projection."""

    def build(self, *args: Any, **kwargs: Any) -> Any:
        """Produit le payload de projection depuis les sources runtime."""


class ProjectionBuilderUnavailableError(RuntimeError):
    """Signale qu'aucun builder réel n'est disponible pour persister."""


class ProjectionPersistenceService:
    """Persiste uniquement les payloads produits par un builder explicite."""

    def __init__(self, repository: ProjectionRepository) -> None:
        """Initialise le service avec le repository canonique."""
        self.repository = repository

    def persist_from_builder(
        self,
        *,
        builder: ProjectionPayloadBuilder | None,
        projection_type: str,
        projection_version: str,
        chart_id: str,
        user_id: int,
        source_versions: Any,
        source: str,
        builder_args: tuple[Any, ...] = (),
        builder_kwargs: dict[str, Any] | None = None,
    ) -> PersistedProjectionModel:
        """Construit puis persiste une projection sans fallback synthétique."""
        if builder is None:
            raise ProjectionBuilderUnavailableError(
                "A real projection builder is required before persistence"
            )
        payload = builder.build(*builder_args, **(builder_kwargs or {}))
        payload_json = projection_payload_to_json(payload)
        projection_hash = compute_projection_hash(payload_json)
        return self.repository.create(
            chart_id=chart_id,
            user_id=user_id,
            projection_type=projection_type,
            projection_version=projection_version,
            projection_hash=projection_hash,
            payload=payload_json,
            source_versions=projection_metadata_to_json(source_versions),
            source=source,
        )


def projection_payload_to_json(payload: Any) -> dict[str, object]:
    """Convertit un payload de builder réel en objet JSON persistable."""
    jsonable = projection_value_to_jsonable(payload)
    if not isinstance(jsonable, dict):
        raise ValueError("Projection payload must serialize to a JSON object")
    return jsonable


def projection_metadata_to_json(metadata: Any) -> dict[str, object]:
    """Convertit les versions source typées en objet JSON persistable."""
    jsonable = projection_value_to_jsonable(metadata)
    if not isinstance(jsonable, dict):
        raise ValueError("Projection source_versions must serialize to a JSON object")
    return jsonable
