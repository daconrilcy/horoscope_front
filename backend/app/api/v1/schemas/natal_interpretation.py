from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.llm_orchestration.schemas import AstroResponseV1


class NatalInterpretationRequest(BaseModel):
    use_case_level: Literal["short", "complete"] = Field(
        default="short", description="short=free, complete=premium"
    )
    persona_id: Optional[str] = Field(
        default=None, description="Optional for short, recommended for complete level."
    )
    locale: str = Field(default="fr-FR", pattern=r"^[a-z]{2}-[A-Z]{2}$")
    question: Optional[str] = Field(default=None, max_length=500)


class InterpretationMeta(BaseModel):
    level: Literal["short", "complete"]
    use_case: str
    persona_id: Optional[str] = None
    persona_name: Optional[str] = None
    prompt_version_id: Optional[str] = None
    validation_status: str
    repair_attempted: bool = False
    fallback_triggered: bool = False
    was_fallback: bool = False  # Story 29.2 requirement
    latency_ms: Optional[int] = None
    request_id: Optional[str] = None


class NatalInterpretationData(BaseModel):
    chart_id: str
    use_case: str
    interpretation: AstroResponseV1
    meta: InterpretationMeta
    degraded_mode: Optional[str] = None


class NatalInterpretationResponse(BaseModel):
    data: NatalInterpretationData
