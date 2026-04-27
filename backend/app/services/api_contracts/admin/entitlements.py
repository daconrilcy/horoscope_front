"""Schemas Pydantic des endpoints admin de droits."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class AdminEntitlementPlan(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    id: int
    code: str
    name: str
    audience: str


class AdminEntitlementFeature(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    id: int
    code: str
    name: str
    is_metered: bool


class AdminEntitlementCell(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    access_mode: str
    is_enabled: bool
    variant_code: str | None
    quota_limit: int | None
    period: str | None
    is_incoherent: bool = False

    model_config = ConfigDict(from_attributes=True)


class AdminEntitlementMatrixResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    plans: list[AdminEntitlementPlan]
    features: list[AdminEntitlementFeature]
    cells: dict[str, AdminEntitlementCell]  # Key: "plan_id:feature_id"


class AdminEntitlementUpdate(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    access_mode: str | None = None
    quota_limit: int | None = None
    is_enabled: bool | None = None
