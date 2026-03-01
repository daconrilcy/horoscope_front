from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class AstroSection(BaseModel):
    key: Literal[
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
    heading: str = Field(..., min_length=1, max_length=80)
    content: str = Field(..., min_length=1, max_length=2500)

class AstroResponseV1(BaseModel):
    """Canonical structured response for astrological interpretations."""
    title: str = Field(..., min_length=1, max_length=120)
    summary: str = Field(..., min_length=1, max_length=1200)
    sections: List[AstroSection] = Field(..., min_length=2, max_length=8)
    highlights: List[str] = Field(..., min_length=3, max_length=10)
    advice: List[str] = Field(..., min_length=3, max_length=10)
    evidence: List[str] = Field(..., min_length=2, max_length=40)
    disclaimers: List[str] = Field(default_factory=list)

class ChatResponseV1(BaseModel):
    """Canonical structured response for interactive chat."""
    message: str = Field(..., min_length=1, max_length=2500)
    suggested_replies: List[str] = Field(..., max_length=5)
    intent: Optional[Literal[
        "clarify_question",
        "ask_birth_data",
        "explain_natal_basics",
        "offer_natal_interpretation",
        "offer_tarot_reading",
        "offer_event_guidance",
        "handoff_to_support",
        "close_conversation",
    ]] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)
    safety_notes: List[str] = Field(default_factory=list, max_length=3)
