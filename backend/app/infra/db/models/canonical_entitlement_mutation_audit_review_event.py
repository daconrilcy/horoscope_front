# Shim legacy pour l'ancien chemin d'import de l'historique de review.
"""Réexporte le modèle canonique d'historique de review pour préserver la compatibilité locale."""

from app.infra.db.models.entitlement_mutation.audit.review_event import (
    CanonicalEntitlementMutationAuditReviewEventModel,
)

__all__ = ["CanonicalEntitlementMutationAuditReviewEventModel"]
