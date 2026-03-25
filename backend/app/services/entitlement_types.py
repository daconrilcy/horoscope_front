from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class QuotaDefinition:
    """Définition d'un quota pour une feature."""

    quota_key: str
    quota_limit: int
    period_unit: str  # "day" | "week" | "month" | "year" | "lifetime"
    period_value: int
    reset_mode: str  # "calendar" | "lifetime"


@dataclass(frozen=True)
class UsageState:
    """État réel de consommation d'un quota."""

    feature_code: str
    quota_key: str
    quota_limit: int
    used: int
    remaining: int
    exhausted: bool  # used >= quota_limit
    period_unit: str
    period_value: int
    reset_mode: str
    window_start: datetime  # timezone-aware UTC
    window_end: datetime | None  # None uniquement si reset_mode="lifetime"


@dataclass
class FeatureEntitlement:
    """Droit d'accès calculé pour une feature."""

    plan_code: str
    billing_status: str
    is_enabled_by_plan: bool
    access_mode: str
    variant_code: str | None
    quotas: list[QuotaDefinition]  # quotas théoriques du plan
    final_access: bool
    reason: str
    usage_states: list[UsageState] = field(default_factory=list)  # état réel de consommation
    quota_exhausted: bool = False  # True si au moins un quota est épuisé
