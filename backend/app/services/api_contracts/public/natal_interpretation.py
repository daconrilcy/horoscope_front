# Commentaire global: schemas Pydantic des endpoints publics d'interpretation natale.
"""Schemas Pydantic des endpoints publics d'interpretation natale."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, SerializerFunctionWrapHandler, model_serializer

from app.domain.astrology.reading import BasicNatalInterpretationV2
from app.domain.llm.prompting.narrative_natal_reading_v1 import NarrativeNatalReadingV1
from app.domain.llm.prompting.schemas import (
    AstroErrorResponseV3,
    AstroFreeResponseV1,
    AstroResponseV1,
    AstroResponseV2,
    AstroResponseV3,
)

NatalInterpretationModule = Literal[
    "NATAL_PSY_PROFILE",
    "NATAL_SHADOW_INTEGRATION",
    "NATAL_LEADERSHIP_WORKSTYLE",
    "NATAL_CREATIVITY_JOY",
    "NATAL_RELATIONSHIP_STYLE",
    "NATAL_COMMUNITY_NETWORKS",
    "NATAL_VALUES_SECURITY",
    "NATAL_EVOLUTION_PATH",
]


class InterpretationMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    id: Optional[int] = None
    level: Literal["short", "complete"]
    use_case: str
    persona_id: Optional[str] = None
    persona_name: Optional[str] = None
    prompt_version_id: Optional[str] = None
    schema_version: str = "v1"  # v1, v2 or v3
    validation_status: str
    repair_attempted: bool = False
    fallback_triggered: bool = False
    was_fallback: bool = False  # Story 29.2 requirement
    latency_ms: Optional[int] = None
    request_id: Optional[str] = None
    cached: bool = False
    persisted_at: Optional[datetime] = None
    module: Optional[NatalInterpretationModule] = None


class NatalInterpretationData(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    chart_id: str
    use_case: str
    interpretation: (
        AstroResponseV3
        | AstroErrorResponseV3
        | AstroResponseV2
        | AstroResponseV1
        | AstroFreeResponseV1
    )
    meta: InterpretationMeta
    degraded_mode: Optional[str] = None
    narrative_natal_reading_v1: Optional[NarrativeNatalReadingV1] = None
    basic_natal_interpretation_v2: Optional[BasicNatalInterpretationV2] = None

    @model_serializer(mode="wrap")
    def serialize_without_internal_evidence(
        self, handler: SerializerFunctionWrapHandler
    ) -> dict[str, object]:
        """Retire les codes evidence backend-only du JSON d'interpretation public."""
        payload = handler(self)
        if not isinstance(payload, dict):
            raise TypeError("Natal interpretation public payload must be a dictionary")
        interpretation = payload.get("interpretation")
        if isinstance(interpretation, dict):
            interpretation.pop("evidence", None)
        return payload


class NatalChartLongEntitlementInfo(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    remaining: Optional[int] = None
    limit: Optional[int] = None
    window_end: Optional[datetime] = None  # None pour les quotas lifetime
    variant_code: Optional[str] = None  # "single_astrologer" | "multi_astrologer"


class NatalInterpretationResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: NatalInterpretationData
    disclaimers: list[str] = Field(default_factory=list)
    entitlement_info: Optional[NatalChartLongEntitlementInfo] = None


class NatalInterpretationListItem(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    id: int
    chart_id: str
    level: Literal["short", "complete"]
    persona_id: Optional[str] = None
    persona_name: Optional[str] = None
    module: Optional[str] = None
    created_at: datetime
    use_case: str
    prompt_version_id: Optional[str] = None
    was_fallback: bool = False


class NatalInterpretationListResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    items: list[NatalInterpretationListItem]
    total: int
    limit: int
    offset: int


class NatalPdfTemplateItem(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    key: str
    name: str
    description: Optional[str] = None
    locale: str
    is_default: bool


class NatalPdfTemplateListResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    items: list[NatalPdfTemplateItem]
