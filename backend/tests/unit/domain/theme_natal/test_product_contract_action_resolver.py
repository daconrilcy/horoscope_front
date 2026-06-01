# Commentaire global: tests de matrice du contrat produit theme natal.
"""Verrouille les decisions produit avant toute selection de generation LLM."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.domain.theme_natal import (
    THEME_NATAL_READING_CONTRACT_KEYS,
    ThemeNatalEntitlementTier,
    ThemeNatalOutputVariant,
    ThemeNatalPersonaMode,
    ThemeNatalReadingAction,
    ThemeNatalReadingActionRequest,
    ThemeNatalReadingDecisionStatus,
    ThemeNatalReadingKind,
    ThemeNatalReadingProductEntitlement,
    resolve_theme_natal_reading_action,
)


def _request(
    *,
    tier: ThemeNatalEntitlementTier,
    action: ThemeNatalReadingAction,
    persona_mode: ThemeNatalPersonaMode = ThemeNatalPersonaMode.NONE,
    existing_reading_id: int | None = None,
    granted: bool = True,
) -> ThemeNatalReadingActionRequest:
    """Construit une requete produit minimale pour les cas de matrice."""
    return ThemeNatalReadingActionRequest(
        user_id=7,
        chart_id=42,
        action=action,
        entitlement=ThemeNatalReadingProductEntitlement(
            tier=tier,
            granted=granted,
            reason_code="granted" if granted else "quota_exhausted",
        ),
        locale="fr-FR",
        persona_mode=persona_mode,
        existing_reading_id=existing_reading_id,
    )


def test_contract_fields_and_enums_are_closed() -> None:
    """Prouve les valeurs fermees du contrat produit."""
    assert {action.value for action in ThemeNatalReadingAction} == {
        "preview",
        "generate_full",
        "regenerate",
        "download",
    }
    assert {kind.value for kind in ThemeNatalReadingKind} == {"natal_reading"}
    assert {variant.value for variant in ThemeNatalOutputVariant} == {
        "free_preview",
        "basic_full_reading",
        "premium_full_reading",
    }
    assert {mode.value for mode in ThemeNatalPersonaMode} == {"none", "single", "multi"}

    decision = resolve_theme_natal_reading_action(
        _request(
            tier=ThemeNatalEntitlementTier.BASIC,
            action=ThemeNatalReadingAction.GENERATE_FULL,
        )
    )

    assert decision.contract is not None
    payload = decision.contract.model_dump(mode="json")
    assert set(payload) == {
        "feature",
        "reading_kind",
        "action",
        "output_variant",
        "persona_mode",
        "locale",
        "entitlement",
        "contract_key",
    }
    assert payload["feature"] == "theme_natal"
    assert payload["reading_kind"] == "natal_reading"


def test_free_preview_resolves_free_preview_without_generation_key() -> None:
    """Verifie que la preview Free reste une variante produit sans generation short implicite."""
    decision = resolve_theme_natal_reading_action(
        _request(tier=ThemeNatalEntitlementTier.FREE, action=ThemeNatalReadingAction.PREVIEW)
    )

    assert decision.status is ThemeNatalReadingDecisionStatus.ALLOWED
    assert decision.contract is not None
    assert decision.contract.output_variant is ThemeNatalOutputVariant.FREE_PREVIEW
    assert decision.contract.contract_key is None


def test_free_full_generation_is_paywalled() -> None:
    """Verifie qu'un entitlement Free ne peut pas produire une lecture complete."""
    decision = resolve_theme_natal_reading_action(
        _request(tier=ThemeNatalEntitlementTier.FREE, action=ThemeNatalReadingAction.GENERATE_FULL)
    )

    assert decision.status is ThemeNatalReadingDecisionStatus.LOCKED_PAYWALL
    assert decision.contract is None
    assert decision.reason_code == "full_reading_requires_paid_entitlement"


def test_basic_preview_does_not_select_generation_contract() -> None:
    """Prouve que Basic preview ne route pas vers une generation legacy courte."""
    decision = resolve_theme_natal_reading_action(
        _request(tier=ThemeNatalEntitlementTier.BASIC, action=ThemeNatalReadingAction.PREVIEW)
    )

    assert decision.status is ThemeNatalReadingDecisionStatus.ALLOWED
    assert decision.contract is not None
    assert decision.contract.output_variant is ThemeNatalOutputVariant.FREE_PREVIEW
    assert decision.contract.contract_key is None


@pytest.mark.parametrize(
    ("tier", "expected_variant"),
    [
        (ThemeNatalEntitlementTier.BASIC, ThemeNatalOutputVariant.BASIC_FULL_READING),
        (ThemeNatalEntitlementTier.PREMIUM, ThemeNatalOutputVariant.PREMIUM_FULL_READING),
    ],
)
def test_paid_full_generation_resolves_target_variant(
    tier: ThemeNatalEntitlementTier,
    expected_variant: ThemeNatalOutputVariant,
) -> None:
    """Verifie la selection explicite Basic et Premium vers des contrats distincts."""
    decision = resolve_theme_natal_reading_action(
        _request(tier=tier, action=ThemeNatalReadingAction.GENERATE_FULL)
    )

    assert decision.status is ThemeNatalReadingDecisionStatus.GENERATE_WITH_CONTRACT_KEY
    assert decision.contract is not None
    assert decision.contract.output_variant is expected_variant
    assert decision.contract.contract_key == THEME_NATAL_READING_CONTRACT_KEYS[expected_variant]


def test_persona_mode_is_separate_from_output_variant() -> None:
    """Verifie que le mode persona ne change pas la variante de sortie Basic."""
    decision = resolve_theme_natal_reading_action(
        _request(
            tier=ThemeNatalEntitlementTier.BASIC,
            action=ThemeNatalReadingAction.GENERATE_FULL,
            persona_mode=ThemeNatalPersonaMode.SINGLE,
        )
    )

    assert decision.contract is not None
    assert decision.contract.output_variant is ThemeNatalOutputVariant.BASIC_FULL_READING
    assert decision.contract.persona_mode is ThemeNatalPersonaMode.SINGLE


def test_existing_reading_is_returned_without_generation_key() -> None:
    """Verifie qu'une lecture existante court-circuite la generation nominale."""
    decision = resolve_theme_natal_reading_action(
        _request(
            tier=ThemeNatalEntitlementTier.PREMIUM,
            action=ThemeNatalReadingAction.GENERATE_FULL,
            existing_reading_id=123,
        )
    )

    assert decision.status is ThemeNatalReadingDecisionStatus.EXISTING_READING
    assert decision.existing_reading_id == 123
    assert decision.contract is not None
    assert decision.contract.output_variant is ThemeNatalOutputVariant.PREMIUM_FULL_READING
    assert decision.contract.contract_key is None


def test_regenerate_ignores_existing_reading_and_selects_contract() -> None:
    """Verifie que la regeneration explicite produit une nouvelle cle contractuelle."""
    decision = resolve_theme_natal_reading_action(
        _request(
            tier=ThemeNatalEntitlementTier.BASIC,
            action=ThemeNatalReadingAction.REGENERATE,
            existing_reading_id=123,
        )
    )

    assert decision.status is ThemeNatalReadingDecisionStatus.GENERATE_WITH_CONTRACT_KEY
    assert decision.contract is not None
    assert decision.contract.output_variant is ThemeNatalOutputVariant.BASIC_FULL_READING


def test_download_requires_existing_reading() -> None:
    """Verifie qu'un download sans lecture existante reste une requete invalide."""
    decision = resolve_theme_natal_reading_action(
        _request(tier=ThemeNatalEntitlementTier.PREMIUM, action=ThemeNatalReadingAction.DOWNLOAD)
    )

    assert decision.status is ThemeNatalReadingDecisionStatus.INVALID_REQUEST
    assert decision.reason_code == "download_requires_existing_reading"


def test_decision_status_values_are_closed() -> None:
    """Verifie le vocabulaire ferme des decisions du resolver."""
    assert {status.value for status in ThemeNatalReadingDecisionStatus} == {
        "allowed",
        "locked_paywall",
        "existing_reading",
        "generate_with_contract_key",
        "invalid_request",
    }


@pytest.mark.parametrize(
    "legacy_key",
    [
        "use" + "_case",
        "use" + "_case" + "_level",
        "variant" + "_code",
        "plan",
        "force" + "Refresh",
    ],
)
def test_product_action_request_rejects_technical_frontend_inputs(legacy_key: str) -> None:
    """Verifie que les anciennes entrees techniques ne sont pas acceptees par le DTO."""
    payload = _request(
        tier=ThemeNatalEntitlementTier.BASIC,
        action=ThemeNatalReadingAction.GENERATE_FULL,
    ).model_dump(mode="json")
    payload[legacy_key] = "legacy"

    with pytest.raises(ValidationError):
        ThemeNatalReadingActionRequest(**payload)
