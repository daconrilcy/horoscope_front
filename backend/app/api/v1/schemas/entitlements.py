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
    granted: bool  # remplace final_access
    reason_code: str  # remplace reason (normalisé)
    access_mode: str | None = None
    quota_remaining: int | None = None
    quota_limit: int | None = None
    variant_code: str | None = None
    usage_states: list[UsageStateResponse] = Field(default_factory=list)


class EntitlementsMeData(BaseModel):
    """
    Contrat frontend unique décrivant le plan commercial et les droits effectifs.

    Suffisance frontend (AC4) :
    - Désactiver un CTA si granted == false
    - Afficher le quota restant via quota_remaining et quota_limit
    - Afficher le motif de blocage via reason_code
    - Afficher un CTA d'upgrade si reason_code appartient aux motifs
      "feature_not_in_plan", "billing_inactive" ou "quota_exhausted"
    """

    plan_code: str  # top-level (ex-dupliqué par feature)
    billing_status: str  # top-level
    features: list[FeatureEntitlementResponse] = Field(default_factory=list)


class ResponseMeta(BaseModel):
    request_id: str


class EntitlementsMeResponse(BaseModel):
    """Réponse suffisante pour piloter l'UX d'accès, de quota et d'upgrade côté frontend."""

    data: EntitlementsMeData
    meta: ResponseMeta


# --- Schémas pour le catalogue de plans (AC2) ---


class PlanFeatureQuotaData(BaseModel):
    quota_key: str
    quota_limit: int
    period_unit: str
    period_value: int
    reset_mode: str


class PlanFeatureData(BaseModel):
    feature_code: str
    feature_name: str
    is_enabled: bool
    access_mode: str
    quotas: list[PlanFeatureQuotaData] = Field(default_factory=list)


class PlanCatalogData(BaseModel):
    plan_code: str
    plan_name: str
    monthly_price_cents: int
    currency: str
    is_active: bool
    features: list[PlanFeatureData] = Field(default_factory=list)


class PlansCatalogResponse(BaseModel):
    data: list[PlanCatalogData]
    meta: ResponseMeta
