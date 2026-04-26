"""Schemas Pydantic des endpoints publics d'interpretation natale."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

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


class NatalInterpretationRequest(BaseModel):
    use_case_level: Literal["short", "complete"] = Field(
        default="short", description="short=free, complete=premium"
    )
    persona_id: Optional[str] = Field(
        default=None, description="Optional for short, recommended for complete level."
    )
    locale: str = Field(default="fr-FR", pattern=r"^[a-z]{2}-[A-Z]{2}$")
    question: Optional[str] = Field(default=None, max_length=500)
    force_refresh: bool = Field(
        default=False, description="If True, re-generate even if already exists."
    )
    module: Optional[NatalInterpretationModule] = Field(
        default=None,
        description="Optional thematic module for complete natal interpretation.",
    )


class InterpretationMeta(BaseModel):
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


class NatalChartLongEntitlementInfo(BaseModel):
    remaining: Optional[int] = None
    limit: Optional[int] = None
    window_end: Optional[datetime] = None  # None pour les quotas lifetime
    variant_code: Optional[str] = None  # "single_astrologer" | "multi_astrologer"


class NatalInterpretationResponse(BaseModel):
    data: NatalInterpretationData
    disclaimers: list[str] = Field(default_factory=list)
    entitlement_info: Optional[NatalChartLongEntitlementInfo] = None


class NatalInterpretationListItem(BaseModel):
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
    items: list[NatalInterpretationListItem]
    total: int
    limit: int
    offset: int


class NatalPdfTemplateItem(BaseModel):
    key: str
    name: str
    description: Optional[str] = None
    locale: str
    is_default: bool


class NatalPdfTemplateListResponse(BaseModel):
    items: list[NatalPdfTemplateItem]
