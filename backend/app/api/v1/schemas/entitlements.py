from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class UsageStateResponse(BaseModel):
    quota_key: str
    quota_limit: int
    used: int
    remaining: int
    exhausted: bool
    period_unit: str
    period_value: int
    reset_mode: str
    # window_start est UNIX_EPOCH (1970-01-01T00:00:00Z) pour lifetime en prod,
    # mais certains tests unitaires passent None — déclarer Optional par robustesse
    window_start: datetime | None = None
    window_end: datetime | None = None  # None pour reset_mode="lifetime"


class FeatureEntitlementResponse(BaseModel):
    feature_code: str
    plan_code: str  # code du plan de l'utilisateur ("none", "trial", "basic", "premium")
    billing_status: str  # "active" | "trialing" | "past_due" | "none"
    access_mode: str  # "quota" | "unlimited" | "disabled" | "unknown"
    final_access: bool
    reason: str
    variant_code: str | None = None
    usage_states: list[UsageStateResponse] = Field(default_factory=list)


class EntitlementsMeData(BaseModel):
    features: list[FeatureEntitlementResponse] = Field(default_factory=list)


class ResponseMeta(BaseModel):
    request_id: str


class EntitlementsMeResponse(BaseModel):
    data: EntitlementsMeData
    meta: ResponseMeta
