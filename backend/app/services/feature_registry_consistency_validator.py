from app.services.b2b_api_entitlement_gate import B2BApiEntitlementGate
from app.services.chat_entitlement_gate import ChatEntitlementGate
from app.services.feature_scope_registry import FEATURE_SCOPE_REGISTRY, FeatureScope
from app.services.natal_chart_long_entitlement_gate import NatalChartLongEntitlementGate
from app.services.thematic_consultation_entitlement_gate import (
    ThematicConsultationEntitlementGate,
)


class FeatureRegistryConsistencyError(ValueError):
    """Exception levée sur toute incohérence du registre de features."""
    pass

class FeatureRegistryConsistencyValidator:
    """Validateur central de la cohérence du registre de features."""

    # Liste canonique attendue : (feature_code, expected_scope)
    EXPECTED_GATE_SCOPES: list[tuple[str, FeatureScope]] = [
        (ChatEntitlementGate.FEATURE_CODE, FeatureScope.B2C),
        (ThematicConsultationEntitlementGate.FEATURE_CODE, FeatureScope.B2C),
        (NatalChartLongEntitlementGate.FEATURE_CODE, FeatureScope.B2C),
        (B2BApiEntitlementGate.FEATURE_CODE, FeatureScope.B2B),
    ]

    # Features metered B2C du seed canonique (static, pas de DB)
    CANONICAL_B2C_METERED_FEATURES: frozenset[str] = frozenset({
        "natal_chart_long",
        "astrologer_chat",
        "thematic_consultation",
    })

    @staticmethod
    def validate() -> None:
        """
        Vérifie la cohérence entre le registre, les gates et le seed canonique.
        Lève FeatureRegistryConsistencyError si une incohérence est détectée.
        """
        errors: list[str] = []

        # Vérif 1 & 2 : Exhaustivité registre <-> gates et Scopes canoniques imposés
        for (
            feature_code,
            expected_scope,
        ) in FeatureRegistryConsistencyValidator.EXPECTED_GATE_SCOPES:
            if feature_code not in FEATURE_SCOPE_REGISTRY:
                errors.append(
                    f"Feature code '{feature_code}' manquant dans "
                    "FEATURE_SCOPE_REGISTRY (requis par sa gate quota)."
                )
            elif FEATURE_SCOPE_REGISTRY[feature_code] != expected_scope:
                actual = FEATURE_SCOPE_REGISTRY[feature_code].value
                errors.append(
                    f"Scope invalide pour '{feature_code}' dans le registre : "
                    f"attendu {expected_scope.value}, trouvé {actual}."
                )

        # Vérif 3 : Cohérence seed B2C
        for (
            feature_code
        ) in FeatureRegistryConsistencyValidator.CANONICAL_B2C_METERED_FEATURES:
            if feature_code not in FEATURE_SCOPE_REGISTRY:
                errors.append(
                    f"Feature metered B2C '{feature_code}' (seed canonique) "
                    "manquante dans le registre."
                )
            elif FEATURE_SCOPE_REGISTRY[feature_code] != FeatureScope.B2C:
                errors.append(
                    f"Feature metered B2C '{feature_code}' doit avoir le scope "
                    "B2C dans le registre."
                )

        # Vérif 4 : Validité du registre (enum membership check)
        # On vérifie que chaque valeur dans le registre est bien une instance de FeatureScope
        for feature_code, scope in FEATURE_SCOPE_REGISTRY.items():
            if not isinstance(scope, FeatureScope):
                errors.append(
                    f"Scope invalide '{scope}' (type {type(scope).__name__}) "
                    f"pour la feature '{feature_code}' dans le registre. "
                    "Doit être une instance de FeatureScope."
                )

        if errors:
            raise FeatureRegistryConsistencyError(
                "Feature registry inconsistencies detected:\n"
                + "\n".join(f"  {i+1}. {e}" for i, e in enumerate(errors))
            )
