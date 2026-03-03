from __future__ import annotations

from typing import Annotated, List, Literal, Optional

from pydantic import BaseModel, Field

_SECTION_KEYS = Literal[
    "overall",
    "career",
    "relationships",
    "inner_life",
    "daily_life",
    "strengths",
    "challenges",
    "tarot_spread",
    "event_context",
]

# Shared constrained types
_EvidenceItem = Annotated[str, Field(pattern=r"^[A-Z0-9_\.:-]{3,80}$")]
_HighlightItem = Annotated[str, Field(max_length=360)]
_AdviceItem = Annotated[str, Field(max_length=360)]
_DisclaimerItemV1 = Annotated[str, Field(max_length=200)]
_DisclaimerItemV2 = Annotated[str, Field(max_length=300)]


class AstroSection(BaseModel):
    key: _SECTION_KEYS
    heading: str = Field(..., min_length=1, max_length=80)
    content: str = Field(..., min_length=1, max_length=2500)


class AstroSectionV2(BaseModel):
    """Extended section with wider content limit for premium interpretations."""

    key: _SECTION_KEYS
    heading: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=6500)


class AstroResponseV1(BaseModel):
    """Canonical structured response for astrological interpretations."""

    title: str = Field(..., min_length=1, max_length=120)
    summary: str = Field(..., min_length=1, max_length=1200)
    sections: List[AstroSection] = Field(..., min_length=2, max_length=8)
    highlights: List[_HighlightItem] = Field(..., min_length=3, max_length=10)
    advice: List[_AdviceItem] = Field(..., min_length=3, max_length=10)
    evidence: List[_EvidenceItem] = Field(default_factory=list, max_length=40)
    disclaimers: List[_DisclaimerItemV1] = Field(default_factory=list)


class AstroResponseV2(BaseModel):
    """Extended structured response for premium complete interpretations (Story 30-2)."""

    title: str = Field(..., min_length=1, max_length=160)
    summary: str = Field(..., min_length=1, max_length=2800)
    sections: List[AstroSectionV2] = Field(..., min_length=2, max_length=10)
    highlights: List[_HighlightItem] = Field(..., min_length=3, max_length=12)
    advice: List[_AdviceItem] = Field(..., min_length=3, max_length=12)
    evidence: List[_EvidenceItem] = Field(default_factory=list, max_length=80)
    disclaimers: List[_DisclaimerItemV2] = Field(default_factory=list)


class ChatResponseV1(BaseModel):
    """Canonical structured response for interactive chat."""

    message: str = Field(..., min_length=1, max_length=2500)
    suggested_replies: List[str] = Field(..., max_length=5)
    intent: Optional[
        Literal[
            "clarify_question",
            "ask_birth_data",
            "explain_natal_basics",
            "offer_natal_interpretation",
            "offer_tarot_reading",
            "offer_event_guidance",
            "handoff_to_support",
            "close_conversation",
        ]
    ] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)
    safety_notes: List[str] = Field(default_factory=list, max_length=3)
