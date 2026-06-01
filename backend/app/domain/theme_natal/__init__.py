# Commentaire global: expose les contrats produit purs du theme natal.
"""Exports publics du domaine produit theme natal."""

from app.domain.theme_natal.generation_contracts import (
    THEME_NATAL_GENERATION_CONTRACTS,
    THEME_NATAL_GENERATION_CONTRACTS_BY_KEY,
    ThemeNatalGenerationContract,
    ThemeNatalResolvedGenerationContractSnapshot,
    resolve_theme_natal_generation_contract,
)
from app.domain.theme_natal.generation_schemas import (
    THEME_NATAL_PUBLIC_PROJECTED_SCHEMAS,
    THEME_NATAL_RAW_PROVIDER_SCHEMAS,
)
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
    "THEME_NATAL_GENERATION_CONTRACTS",
    "THEME_NATAL_GENERATION_CONTRACTS_BY_KEY",
    "THEME_NATAL_PUBLIC_PROJECTED_SCHEMAS",
    "THEME_NATAL_RAW_PROVIDER_SCHEMAS",
    "THEME_NATAL_READING_CONTRACT_KEYS",
    "ThemeNatalGenerationContract",
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
    "ThemeNatalResolvedGenerationContractSnapshot",
    "resolve_theme_natal_generation_contract",
    "resolve_theme_natal_reading_action",
]
