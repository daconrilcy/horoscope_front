from __future__ import annotations

from typing import Annotated, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.llm_orchestration.models import EVIDENCE_ID_REGEX

_SECTION_KEY_VALUES = (
    "overall",
    "career",
    "relationships",
    "inner_life",
    "daily_life",
    "strengths",
    "challenges",
    "tarot_spread",
    "event_context",
    "self_image",
    "emotions",
    "mind_communication",
    "motivations",
    "stress_patterns",
    "growth_levers",
    "patterns",
    "triggers",
    "protection_strategies",
    "integration_path",
    "repair_plan",
    "leadership_signature",
    "motivation_drivers",
    "team_dynamics",
    "decision_style",
    "work_environment",
    "pitfalls",
    "practical_playbook",
    "creative_engine",
    "inspiration_sources",
    "blockers",
    "joy_practices",
    "romance_vibe",
    "integration",
    "needs_in_love",
    "attraction_style",
    "conflict_style",
    "intimacy_boundaries",
    "relationship_growth",
    "partner_archetype",
    "emotional_fit",
    "communication_fit",
    "commitment_style",
    "red_flags",
    "selection_criteria",
    "tribe_signature",
    "collaboration_mode",
    "social_energy",
    "recognition_needs",
    "actions",
    "values_core",
    "security_needs",
    "sharing_boundaries",
    "decision_hygiene",
    "practical_rules",
    "comfort_zone",
    "growth_direction",
    "integration_steps",
    "weekly_practice",
)

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
    "self_image",
    "emotions",
    "mind_communication",
    "motivations",
    "stress_patterns",
    "growth_levers",
    "patterns",
    "triggers",
    "protection_strategies",
    "integration_path",
    "repair_plan",
    "leadership_signature",
    "motivation_drivers",
    "team_dynamics",
    "decision_style",
    "work_environment",
    "pitfalls",
    "practical_playbook",
    "creative_engine",
    "inspiration_sources",
    "blockers",
    "joy_practices",
    "romance_vibe",
    "integration",
    "needs_in_love",
    "attraction_style",
    "conflict_style",
    "intimacy_boundaries",
    "relationship_growth",
    "partner_archetype",
    "emotional_fit",
    "communication_fit",
    "commitment_style",
    "red_flags",
    "selection_criteria",
    "tribe_signature",
    "collaboration_mode",
    "social_energy",
    "recognition_needs",
    "actions",
    "values_core",
    "security_needs",
    "sharing_boundaries",
    "decision_hygiene",
    "practical_rules",
    "comfort_zone",
    "growth_direction",
    "integration_steps",
    "weekly_practice",
]

_CHAT_INTENTS = Literal[
    "clarify_question",
    "ask_birth_data",
    "explain_natal_basics",
    "offer_natal_interpretation",
    "offer_tarot_reading",
    "offer_event_guidance",
    "handoff_to_support",
    "close_conversation",
]

# Shared constrained types
_EvidenceItem = Annotated[str, Field(pattern=EVIDENCE_ID_REGEX)]
_HighlightItem = Annotated[str, Field(max_length=360)]
_AdviceItem = Annotated[str, Field(max_length=360)]
_DisclaimerItemV1 = Annotated[str, Field(max_length=200)]
_DisclaimerItemV2 = Annotated[str, Field(max_length=300)]
_SafetyNoteItem = Annotated[str, Field(max_length=200)]
_SuggestedReplyItemV1 = Annotated[str, Field(min_length=1, max_length=80)]
_SuggestedReplyItemV2 = Annotated[str, Field(min_length=1, max_length=120)]


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
    disclaimers: List[_DisclaimerItemV1] = Field(..., max_length=3)


class AstroResponseV2(BaseModel):
    """Extended structured response for premium complete interpretations (Story 30-2)."""

    title: str = Field(..., min_length=1, max_length=160)
    summary: str = Field(..., min_length=1, max_length=2800)
    sections: List[AstroSectionV2] = Field(..., min_length=2, max_length=10)
    highlights: List[_HighlightItem] = Field(..., min_length=3, max_length=12)
    advice: List[_AdviceItem] = Field(..., min_length=3, max_length=12)
    evidence: List[_EvidenceItem] = Field(default_factory=list, max_length=80)
    disclaimers: List[_DisclaimerItemV2] = Field(..., max_length=3)


class AstroSectionV3(BaseModel):
    """Section premium v3 — contenu obligatoirement substantiel (min 280 chars)."""

    key: _SECTION_KEYS
    heading: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=280, max_length=6500)


class AstroSectionErrorV3(BaseModel):
    """Section mode erreur v3 — pas de contrainte de densité premium."""

    key: _SECTION_KEYS
    heading: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=12000)


class AstroResponseV3(BaseModel):
    """Réponse structurée v3 — sans disclaimers LLM, densité premium obligatoire (Story 30-8)."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=160)
    summary: str = Field(..., min_length=900, max_length=2800)
    sections: List[AstroSectionV3] = Field(..., min_length=5, max_length=20)
    highlights: List[_HighlightItem] = Field(..., min_length=5, max_length=12)
    advice: List[_AdviceItem] = Field(..., min_length=5, max_length=12)
    evidence: List[_EvidenceItem] = Field(..., max_length=80)
    # Pas de champ disclaimers — gérés côté application via DisclaimerRegistry


class AstroErrorResponseV3(BaseModel):
    """Structure mode erreur v3 — valide, sans contraintes de densité premium."""

    model_config = ConfigDict(extra="forbid")

    error_code: Literal["insufficient_data", "calculation_failed"]
    message: str = Field(..., min_length=1, max_length=500)
    title: str = Field(..., min_length=1, max_length=160)
    summary: str = Field(..., min_length=1, max_length=500)
    sections: List[AstroSectionErrorV3] = Field(default_factory=list, max_length=2)
    highlights: List[_HighlightItem] = Field(default_factory=list, max_length=3)
    advice: List[_AdviceItem] = Field(default_factory=list, max_length=3)
    evidence: List[_EvidenceItem] = Field(default_factory=list, max_length=5)


class ChatResponseV1(BaseModel):
    """Canonical structured response for interactive chat."""

    message: str = Field(..., min_length=1, max_length=2500)
    suggested_replies: List[_SuggestedReplyItemV1] = Field(..., min_length=1, max_length=5)
    intent: Optional[_CHAT_INTENTS] = Field(...)
    confidence: Optional[float] = Field(..., ge=0, le=1)
    safety_notes: List[_SafetyNoteItem] = Field(default_factory=list, max_length=3)


class ChatResponseV2(BaseModel):
    """Extended structured response for premium chat (GPT-5 optimization)."""

    message: str = Field(..., min_length=1, max_length=4000)
    suggested_replies: List[_SuggestedReplyItemV2] = Field(..., min_length=1, max_length=8)
    intent: Optional[_CHAT_INTENTS] = Field(...)
    confidence: Optional[float] = Field(..., ge=0, le=1)
    safety_notes: List[_SafetyNoteItem] = Field(default_factory=list, max_length=5)
