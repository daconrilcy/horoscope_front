# Commentaire global: orchestration backend des commandes produit publiques theme natal.
"""Execute les actions produit publiques sans exposer de controles techniques client."""

from __future__ import annotations

import hashlib
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import ApplicationError
from app.domain.theme_natal.product_action_resolver import resolve_theme_natal_reading_action
from app.domain.theme_natal.product_contract import (
    ThemeNatalEntitlementTier,
    ThemeNatalReadingAction,
    ThemeNatalReadingActionRequest,
    ThemeNatalReadingProductDecision,
    ThemeNatalReadingProductEntitlement,
)
from app.services.api_contracts.public.theme_natal_readings import (
    ThemeNatalReadingCommandRequest,
    ThemeNatalReadingCommandResponse,
)
from app.services.entitlement.natal_chart_long_entitlement_gate import (
    NatalChartLongAccessDeniedError,
    NatalChartLongEntitlementGate,
    NatalChartLongEntitlementResult,
    NatalChartLongQuotaExceededError,
)
from app.services.llm_generation.natal.theme_natal_basic_full_runtime import (
    ThemeNatalBasicFullReadingRuntime,
    ThemeNatalBasicFullReadingRuntimeRequest,
)
from app.services.user_profile.natal_chart_service import (
    UserNatalChartReadData,
    UserNatalChartService,
    UserNatalChartServiceError,
)


def execute_theme_natal_reading_product_action(
    db: Session,
    *,
    user_id: int,
    command: ThemeNatalReadingCommandRequest,
) -> ThemeNatalReadingCommandResponse:
    """Execute une commande publique via les owners produit, slot et runtime canoniques."""
    chart = _load_requested_chart(db, user_id=user_id, chart_id=command.chart_id)
    if command.action is ThemeNatalReadingAction.PREVIEW:
        decision = _resolve_product_decision(
            user_id=user_id,
            command=command,
            tier=ThemeNatalEntitlementTier.BASIC,
        )
        return _controlled_response(state="readonly", decision=decision)

    if command.action not in {
        ThemeNatalReadingAction.GENERATE_FULL,
        ThemeNatalReadingAction.REGENERATE,
    }:
        decision = _resolve_product_decision(
            user_id=user_id,
            command=command,
            tier=ThemeNatalEntitlementTier.BASIC,
        )
        return _controlled_response(state="rejected", decision=decision)

    if not command.client_request_id:
        return ThemeNatalReadingCommandResponse(
            state="rejected",
            details={"reason_code": "client_request_id_required"},
        )

    entitlement = _check_basic_generation_access(db, user_id=user_id)
    if entitlement is None:
        return ThemeNatalReadingCommandResponse(
            state="locked",
            details={"reason_code": "full_reading_requires_paid_entitlement"},
        )

    result = ThemeNatalBasicFullReadingRuntime().generate(
        db,
        natal_result=chart.result,
        request=ThemeNatalBasicFullReadingRuntimeRequest(
            user_id=user_id,
            chart_id=chart.chart_id,
            chart_numeric_id=_stable_product_chart_id(chart.chart_id),
            locale=command.locale,
            client_request_id=command.client_request_id,
            access_result=entitlement,
        ),
    )
    if result.accepted and result.public_payload is not None:
        return ThemeNatalReadingCommandResponse(
            state="accepted",
            data=dict(result.public_payload),
            details=_public_decision_details(result.decision),
        )
    return ThemeNatalReadingCommandResponse(
        state="rejected",
        details=_rejection_details(result.rejection_reason, result.decision),
    )


def _load_requested_chart(db: Session, *, user_id: int, chart_id: str) -> UserNatalChartReadData:
    """Charge le theme natal public attendu sans accepter un identifiant voisin."""
    try:
        chart = UserNatalChartService.get_latest_for_user(db, user_id)
    except UserNatalChartServiceError as error:
        raise ApplicationError(
            code=error.code,
            message=error.message,
            details=error.details,
        ) from error
    if chart.chart_id != chart_id:
        raise ApplicationError(
            code="natal_chart_not_found",
            message="natal chart not found",
            details={"chart_id": chart_id},
        )
    return chart


def _resolve_product_decision(
    *,
    user_id: int,
    command: ThemeNatalReadingCommandRequest,
    tier: ThemeNatalEntitlementTier,
) -> ThemeNatalReadingProductDecision:
    """Construit l'entree produit backend sans reprendre les anciens champs techniques."""
    return resolve_theme_natal_reading_action(
        ThemeNatalReadingActionRequest(
            user_id=user_id,
            chart_id=_stable_product_chart_id(command.chart_id),
            action=command.action,
            entitlement=ThemeNatalReadingProductEntitlement(tier=tier, granted=True),
            locale=command.locale,
        )
    )


def _check_basic_generation_access(
    db: Session,
    *,
    user_id: int,
) -> NatalChartLongEntitlementResult | None:
    """Reserve l'acces Basic complet sans debiter avant publication acceptee."""
    try:
        return NatalChartLongEntitlementGate.check_access_for_complete_generation(
            db, user_id=user_id
        )
    except (NatalChartLongAccessDeniedError, NatalChartLongQuotaExceededError):
        db.rollback()
        return None


def _controlled_response(
    *,
    state: str,
    decision: ThemeNatalReadingProductDecision,
) -> ThemeNatalReadingCommandResponse:
    """Projette une decision produit non generative en etat public controle."""
    return ThemeNatalReadingCommandResponse(state=state, details=_public_decision_details(decision))


def _public_decision_details(decision: ThemeNatalReadingProductDecision) -> dict[str, Any]:
    """Expose seulement les attributs produit utiles au client."""
    details: dict[str, Any] = {"status": decision.status.value}
    if decision.reason_code is not None:
        details["reason_code"] = decision.reason_code
    if decision.contract is not None:
        details["action"] = decision.contract.action.value
        details["output_variant"] = decision.contract.output_variant.value
    return details


def _rejection_details(
    rejection_reason: dict[str, object] | None,
    decision: ThemeNatalReadingProductDecision,
) -> dict[str, Any]:
    """Evite toute fuite provider dans les rejets publics."""
    details = _public_decision_details(decision)
    if rejection_reason:
        reason_code = rejection_reason.get("code")
        if isinstance(reason_code, str) and reason_code:
            details["reason_code"] = reason_code
    return details


def _stable_product_chart_id(chart_id: str) -> int:
    """Convertit l'identifiant public de theme en entier stable requis par le resolver pur."""
    digest = hashlib.sha256(chart_id.encode("utf-8")).hexdigest()
    return int(digest[:12], 16) + 1
