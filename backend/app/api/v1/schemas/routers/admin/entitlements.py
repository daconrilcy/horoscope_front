"""Schemas Pydantic des endpoints admin de droits."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class AdminEntitlementPlan(BaseModel):
    id: int
    code: str
    name: str
    audience: str


class AdminEntitlementFeature(BaseModel):
    id: int
    code: str
    name: str
    is_metered: bool


class AdminEntitlementCell(BaseModel):
    access_mode: str
    is_enabled: bool
    variant_code: str | None
    quota_limit: int | None
    period: str | None
    is_incoherent: bool = False

    model_config = ConfigDict(from_attributes=True)


class AdminEntitlementMatrixResponse(BaseModel):
    plans: list[AdminEntitlementPlan]
    features: list[AdminEntitlementFeature]
    cells: dict[str, AdminEntitlementCell]  # Key: "plan_id:feature_id"


class AdminEntitlementUpdate(BaseModel):
    access_mode: str | None = None
    quota_limit: int | None = None
    is_enabled: bool | None = None
