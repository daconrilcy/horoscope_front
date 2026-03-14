from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class PrecisionLevel(str, Enum):
    high = "high"
    medium = "medium"
    limited = "limited"
    blocked = "blocked"


class ConsultationStatus(str, Enum):
    nominal = "nominal"
    degraded = "degraded"
    blocked = "blocked"


class UserProfileQuality(str, Enum):
    complete = "complete"
    incomplete = "incomplete"
    missing = "missing"


class FallbackMode(str, Enum):
    user_no_birth_time = "user_no_birth_time"
    other_no_birth_time = "other_no_birth_time"
    relation_user_only = "relation_user_only"
    timing_degraded = "timing_degraded"
    blocking_missing_data = "blocking_missing_data"
    safeguard_reframed = "safeguard_reframed"
    safeguard_refused = "safeguard_refused"


class SafeguardIssue(str, Enum):
    health = "health"
    emotional_distress = "emotional_distress"
    obsessive_relation = "obsessive_relation"
    pregnancy = "pregnancy"
    death = "death"
    legal_finance = "legal_finance"
    third_party_manipulation = "third_party_manipulation"


class OtherPersonData(BaseModel):
    birth_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    birth_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    birth_time_known: bool = True
    birth_place: str
    birth_city: Optional[str] = None
    birth_country: Optional[str] = None
    place_resolved_id: Optional[int] = Field(default=None, gt=0)
    birth_lat: Optional[float] = None
    birth_lon: Optional[float] = None


class ConsultationPrecheckRequest(BaseModel):
    consultation_type: str
    question: Optional[str] = Field(None, max_length=1000)
    horizon: Optional[str] = None
    other_person: Optional[OtherPersonData] = None


class ConsultationPrecheckData(BaseModel):
    consultation_type: str
    user_profile_quality: UserProfileQuality
    precision_level: PrecisionLevel
    status: ConsultationStatus
    missing_fields: list[str]
    available_modes: list[str]
    fallback_mode: Optional[FallbackMode] = None
    safeguard_issue: Optional[SafeguardIssue] = None
    blocking_reasons: list[str]


class ConsultationPrecheckMeta(BaseModel):
    request_id: str
    contract_version: str = "consultation-precheck.v1"


class ConsultationPrecheckResponse(BaseModel):
    data: ConsultationPrecheckData
    meta: ConsultationPrecheckMeta


class ConsultationGenerateRequest(BaseModel):
    consultation_type: str
    question: str = Field(..., max_length=2000)
    objective: Optional[str] = Field(None, max_length=300)
    horizon: Optional[str] = None
    other_person: Optional[OtherPersonData] = None
    astrologer_id: Optional[str] = "auto"
    save_third_party: bool = False
    third_party_nickname: Optional[str] = Field(None, max_length=100)
    third_party_external_id: Optional[str] = Field(None, max_length=36)


class ConsultationBlockKind(str, Enum):
    paragraph = "paragraph"
    title = "title"
    subtitle = "subtitle"
    bullet_list = "bullet_list"


class ConsultationBlock(BaseModel):
    kind: ConsultationBlockKind
    text: Optional[str] = None
    items: list[str] = Field(default_factory=list)


class ConsultationSection(BaseModel):
    id: str
    title: str
    content: str
    blocks: list[ConsultationBlock] = Field(default_factory=list)


class ConsultationGenerateData(BaseModel):
    consultation_id: str
    contract_version: str = "consultation-generate.v1"
    consultation_type: str
    status: ConsultationStatus
    precision_level: PrecisionLevel
    fallback_mode: Optional[FallbackMode] = None
    safeguard_issue: Optional[SafeguardIssue] = None
    route_key: Optional[str] = None
    summary: str
    sections: list[ConsultationSection]
    chat_prefill: str
    metadata: dict


class ConsultationGenerateResponse(BaseModel):
    data: ConsultationGenerateData
    meta: ConsultationPrecheckMeta


class ConsultationThirdPartyUsage(BaseModel):
    consultation_id: str
    consultation_type: str
    context_summary: str
    created_at: datetime


class ConsultationThirdPartyProfile(BaseModel):
    external_id: str
    nickname: str
    birth_date: date
    birth_time: Optional[str]
    birth_time_known: bool
    birth_place: str
    birth_city: Optional[str]
    birth_country: Optional[str]
    birth_lat: Optional[float]
    birth_lon: Optional[float]
    place_resolved_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    usage_history: list[ConsultationThirdPartyUsage] = Field(default_factory=list)


class ConsultationThirdPartyProfileCreate(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=100)
    birth_date: date
    birth_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    birth_time_known: bool = True
    birth_place: str = Field(..., min_length=1, max_length=255)
    birth_city: Optional[str] = None
    birth_country: Optional[str] = None
    birth_lat: Optional[float] = None
    birth_lon: Optional[float] = None
    place_resolved_id: Optional[int] = None
    birth_timezone: Optional[str] = Field(None, max_length=64)


class ConsultationThirdPartyListMeta(BaseModel):
    request_id: str


class ConsultationThirdPartyListResponse(BaseModel):
    items: list[ConsultationThirdPartyProfile]
    meta: ConsultationThirdPartyListMeta
