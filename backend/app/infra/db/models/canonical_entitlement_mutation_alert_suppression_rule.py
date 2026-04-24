# Shim legacy pour l'ancien chemin d'import des règles de suppression.
"""Réexporte le modèle canonique de règle de suppression pour préserver la compatibilité locale."""

from app.infra.db.models.entitlement_mutation.suppression.suppression_rule import (
    CanonicalEntitlementMutationAlertSuppressionRuleModel,
)

__all__ = ["CanonicalEntitlementMutationAlertSuppressionRuleModel"]
