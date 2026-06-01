# Commentaire global: expose les contrats produit purs du theme natal.
"""Exports publics du domaine produit theme natal."""

from app.domain.theme_natal.product_action_resolver import resolve_theme_natal_reading_action
from app.domain.theme_natal.product_contract import (
    THEME_NATAL_READING_CONTRACT_KEYS,
    ThemeNatalEntitlementTier,
    ThemeNatalOutputVariant,
    ThemeNatalPersonaMode,
    ThemeNatalReadingAction,
    ThemeNatalReadingActionRequest,
    ThemeNatalReadingDecisionStatus,
    ThemeNatalReadingKind,
    ThemeNatalReadingProductContract,
    ThemeNatalReadingProductDecision,
    ThemeNatalReadingProductEntitlement,
)

__all__ = [
    "THEME_NATAL_READING_CONTRACT_KEYS",
    "ThemeNatalEntitlementTier",
    "ThemeNatalOutputVariant",
    "ThemeNatalPersonaMode",
    "ThemeNatalReadingAction",
    "ThemeNatalReadingActionRequest",
    "ThemeNatalReadingDecisionStatus",
    "ThemeNatalReadingKind",
    "ThemeNatalReadingProductContract",
    "ThemeNatalReadingProductDecision",
    "ThemeNatalReadingProductEntitlement",
    "resolve_theme_natal_reading_action",
]
