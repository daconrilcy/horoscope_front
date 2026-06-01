# Commentaire global: resout les actions produit theme natal sans acces framework, DB ou LLM.
"""Resolver pur des actions produit de lecture natale theme natal."""

from __future__ import annotations

from app.domain.theme_natal.product_contract import (
    THEME_NATAL_READING_CONTRACT_KEYS,
    ThemeNatalEntitlementTier,
    ThemeNatalOutputVariant,
    ThemeNatalReadingAction,
    ThemeNatalReadingActionRequest,
    ThemeNatalReadingDecisionStatus,
    ThemeNatalReadingProductContract,
    ThemeNatalReadingProductDecision,
)

_FULL_READING_VARIANTS: dict[ThemeNatalEntitlementTier, ThemeNatalOutputVariant] = {
    ThemeNatalEntitlementTier.BASIC: ThemeNatalOutputVariant.BASIC_FULL_READING,
    ThemeNatalEntitlementTier.PREMIUM: ThemeNatalOutputVariant.PREMIUM_FULL_READING,
}


def resolve_theme_natal_reading_action(
    request: ThemeNatalReadingActionRequest,
) -> ThemeNatalReadingProductDecision:
    """Retourne la decision produit fermee pour une action de lecture natale."""
    if request.existing_reading_id and request.action is not ThemeNatalReadingAction.REGENERATE:
        return ThemeNatalReadingProductDecision(
            status=ThemeNatalReadingDecisionStatus.EXISTING_READING,
            contract=_contract_without_generation_key(
                request=request,
                output_variant=_output_variant_for_existing_or_preview(request),
            ),
            existing_reading_id=request.existing_reading_id,
            reason_code="reading_already_available",
        )

    if request.action is ThemeNatalReadingAction.PREVIEW:
        return ThemeNatalReadingProductDecision(
            status=ThemeNatalReadingDecisionStatus.ALLOWED,
            contract=_contract_without_generation_key(
                request=request,
                output_variant=ThemeNatalOutputVariant.FREE_PREVIEW,
            ),
            reason_code="preview_available",
        )

    if request.action is ThemeNatalReadingAction.DOWNLOAD:
        return ThemeNatalReadingProductDecision(
            status=ThemeNatalReadingDecisionStatus.INVALID_REQUEST,
            reason_code="download_requires_existing_reading",
        )

    if request.action in {
        ThemeNatalReadingAction.GENERATE_FULL,
        ThemeNatalReadingAction.REGENERATE,
    }:
        return _resolve_full_generation(request)

    return ThemeNatalReadingProductDecision(
        status=ThemeNatalReadingDecisionStatus.INVALID_REQUEST,
        reason_code="unsupported_action",
    )


def _resolve_full_generation(
    request: ThemeNatalReadingActionRequest,
) -> ThemeNatalReadingProductDecision:
    """Resout les generations completes en fonction du tier d'entitlement backend."""
    if (
        not request.entitlement.granted
        or request.entitlement.tier is ThemeNatalEntitlementTier.FREE
    ):
        return ThemeNatalReadingProductDecision(
            status=ThemeNatalReadingDecisionStatus.LOCKED_PAYWALL,
            reason_code="full_reading_requires_paid_entitlement",
        )

    output_variant = _FULL_READING_VARIANTS.get(request.entitlement.tier)
    if output_variant is None:
        return ThemeNatalReadingProductDecision(
            status=ThemeNatalReadingDecisionStatus.INVALID_REQUEST,
            reason_code="unsupported_entitlement_tier",
        )

    return ThemeNatalReadingProductDecision(
        status=ThemeNatalReadingDecisionStatus.GENERATE_WITH_CONTRACT_KEY,
        contract=ThemeNatalReadingProductContract(
            action=request.action,
            output_variant=output_variant,
            persona_mode=request.persona_mode,
            locale=request.locale,
            entitlement=request.entitlement,
            contract_key=THEME_NATAL_READING_CONTRACT_KEYS[output_variant],
        ),
        reason_code="generation_contract_selected",
    )


def _contract_without_generation_key(
    *,
    request: ThemeNatalReadingActionRequest,
    output_variant: ThemeNatalOutputVariant,
) -> ThemeNatalReadingProductContract:
    """Construit un contrat sans cle de generation pour lecture existante ou preview disponible."""
    return ThemeNatalReadingProductContract(
        action=request.action,
        output_variant=output_variant,
        persona_mode=request.persona_mode,
        locale=request.locale,
        entitlement=request.entitlement,
    )


def _output_variant_for_existing_or_preview(
    request: ThemeNatalReadingActionRequest,
) -> ThemeNatalOutputVariant:
    """Deduit la variante attendue quand une lecture existe deja."""
    if request.action is ThemeNatalReadingAction.PREVIEW:
        return ThemeNatalOutputVariant.FREE_PREVIEW
    return _FULL_READING_VARIANTS.get(
        request.entitlement.tier,
        ThemeNatalOutputVariant.FREE_PREVIEW,
    )
