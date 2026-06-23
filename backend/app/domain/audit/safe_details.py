"""Définit les structures bornées autorisées dans les détails d’audit applicatifs."""

from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


class BaseSafeAuditDetails(BaseModel):
    """Classe de base des DTO d’audit bornés."""

    model_config = ConfigDict(extra="forbid")  # AC8: Force bounded structure


class AdminActionAuditDetails(BaseSafeAuditDetails):
    """Structure sûre pour les actions d’administration génériques."""

    action_type: str
    target_id: Optional[str] = None
    change_summary: Optional[str] = None


def _normalize_safe_value(value: Any) -> Any:
    """Normalise une valeur arbitraire vers une structure JSON bornée."""
    if isinstance(value, BaseSafeAuditDetails):
        return value.model_dump(exclude_none=True)

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, dict):
        return {str(key): _normalize_safe_value(inner) for key, inner in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_normalize_safe_value(item) for item in value]

    return str(value)


def to_safe_details(details: Any) -> Dict[str, Any]:
    """Convertit les détails d’audit en dictionnaire sûr et borné."""
    if isinstance(details, BaseSafeAuditDetails):
        return details.model_dump(exclude_none=True)

    if isinstance(details, dict):
        return {str(key): _normalize_safe_value(value) for key, value in details.items()}

    return {"value": _normalize_safe_value(details)}
