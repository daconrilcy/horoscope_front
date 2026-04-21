import logging
import re
from typing import Any, Dict, Optional, Set

from app.domain.llm.governance.legacy_residual_registry import (
    build_governance_matrix_projection,
    effective_progressive_blocklist,
)
from app.infra.observability.metrics import increment_counter
from app.llm_orchestration.models import FallbackStatus, FallbackType

logger = logging.getLogger(__name__)


class FallbackGovernanceRegistry:
    """
    Registre central de gouvernance des mécanismes de compatibilité (Story 66.21, 66.40).
    La matrice effective est une projection du fichier ``legacy_residual_registry.json`` (AC2).
    """

    GOVERNANCE_MATRIX: Dict[FallbackType, Dict[str, Any]] = build_governance_matrix_projection()

    @staticmethod
    def _infer_family(feature: Optional[str], call_site: str) -> Optional[str]:
        """Infère la famille à partir du feature ou du call_site (use_case)."""
        if feature:
            return feature

        # Les call_sites de resolve_config et mapping contiennent souvent le use_case
        # ex: "resolve_config:horoscope_daily"
        match = re.search(r":([a-zA-Z0-9_-]+)$", call_site)
        if not match:
            return None

        use_case = match.group(1).lower()
        if use_case.startswith("chat"):
            return "chat"
        if use_case.startswith("guidance") or "guidance" in use_case:
            return "guidance"
        if use_case.startswith("natal") or "natal" in use_case:
            return "natal"
        # Story 66.28: daily_prediction is now absorbed into horoscope_daily
        if use_case.startswith("horoscope_daily") or use_case == "daily_prediction":
            return "horoscope_daily"

        return None

    @classmethod
    def track_fallback(
        cls,
        fallback_type: FallbackType,
        call_site: str,
        feature: Optional[str] = None,
        is_nominal: bool = True,
        *,
        subfeature: Optional[str] = None,
        activation_reason: Optional[str] = None,
    ) -> None:
        """
        Enregistre l'usage d'un fallback, vérifie sa conformité et émet la télémétrie.
        """
        from app.core.config import settings

        is_prod = settings.app_env in {"production", "prod"}

        gov = cls.GOVERNANCE_MATRIX.get(fallback_type)
        if not gov:
            logger.warning(
                "governance_unknown_fallback type=%s call_site=%s", fallback_type, call_site
            )
            return

        stable_id = str(gov.get("stable_id", "unknown"))
        path_kind = str(gov.get("path_kind", "unknown"))

        status = gov["status"]
        forbidden_families: Set[str] = gov.get("forbidden_families", set())

        # AC3 Bypass Fix: Inférence de la famille si absente
        effective_feature = cls._infer_family(feature, call_site)

        # 1. Gestion spécifique du statut conditionnel pour USE_CASE_FIRST (AC3)
        if fallback_type == FallbackType.USE_CASE_FIRST:
            if effective_feature not in forbidden_families:
                status = FallbackStatus.TRANSITORY

        reason = activation_reason or "track_fallback"

        blocked = effective_progressive_blocklist()
        if stable_id in blocked:
            from app.llm_orchestration.models import GatewayError
            from app.llm_orchestration.services.observability_service import (
                log_legacy_residual_blocked_attempt,
            )

            log_legacy_residual_blocked_attempt(
                stable_id=stable_id,
                path_kind=path_kind,
                fallback_type=fallback_type.value,
                feature=effective_feature or feature,
                subfeature=subfeature,
                call_site=call_site,
                activation_reason=reason,
                is_nominal=is_nominal,
                status_value=status.value,
            )
            raise GatewayError(
                f"Chemin legacy '{stable_id}' bloqué par la politique progressive "
                f"(LLM_LEGACY_PROGRESSIVE_BLOCKLIST / registre).",
                details={
                    "stable_id": stable_id,
                    "fallback_type": fallback_type.value,
                    "call_site": call_site,
                },
            )

        # 2. Télémétrie (AC5, AC7, AC9, Story 66.40 AC3)
        labels = {
            "fallback_type": fallback_type.value,
            "status": status.value,
            "call_site": call_site,
            "feature": effective_feature or feature or "unknown",
            "is_nominal": "true" if is_nominal else "false",
            "stable_id": stable_id,
            "path_kind": path_kind,
            "activation_reason": reason[:120],
        }
        increment_counter("llm_gateway_fallback_usage_total", labels=labels)

        from app.llm_orchestration.services.observability_service import (
            log_legacy_residual_activation,
        )

        log_legacy_residual_activation(
            stable_id=stable_id,
            path_kind=path_kind,
            fallback_type=fallback_type.value,
            feature=effective_feature or feature,
            subfeature=subfeature,
            call_site=call_site,
            activation_reason=reason,
            is_nominal=is_nominal,
        )

        # 3. Vérification du périmètre (Forbidden families)
        if effective_feature in forbidden_families and is_nominal:
            logger.error(
                "governance_violation_forbidden_fallback type=%s feature=%s call_site=%s status=%s",
                fallback_type.value,
                effective_feature,
                call_site,
                status.value,
            )
            if status == FallbackStatus.TO_REMOVE:
                from app.llm_orchestration.models import GatewayError

                msg = (
                    f"Usage du fallback '{fallback_type.value}' interdit pour "
                    f"la famille '{effective_feature}' (Gouvernance 66.21)"
                )
                raise GatewayError(
                    msg,
                    details={
                        "fallback_type": fallback_type.value,
                        "feature": effective_feature,
                        "status": status.value,
                    },
                )

        # 4. Vérification environnementale (AC9)
        if is_prod:
            if fallback_type == FallbackType.TEST_LOCAL:
                from app.llm_orchestration.models import GatewayError

                raise GatewayError(
                    f"Usage du fallback '{fallback_type.value}' strictement interdit en production",
                    details={"fallback_type": fallback_type.value, "call_site": call_site},
                )

            # Natal No DB en production: alerte critique si non nominal (erreur DB masquée)
            if fallback_type == FallbackType.NATAL_NO_DB and not is_nominal:
                logger.critical(
                    "governance_critical_prod_database_error_masked type=%s call_site=%s",
                    fallback_type.value,
                    call_site,
                )

        # 5. Restriction TO_REMOVE sur nouveaux parcours (AC6)
        if status == FallbackStatus.TO_REMOVE and is_nominal:
            logger.error(
                "governance_nominal_path_dependency_on_to_remove_fallback type=%s call_site=%s",
                fallback_type.value,
                call_site,
            )
            from app.llm_orchestration.models import GatewayError

            raise GatewayError(
                f"Dépendance nominale au fallback '{fallback_type.value}' interdite "
                "(Statut: À RETIRER)",
                details={"fallback_type": fallback_type.value, "call_site": call_site},
            )

        # Logging structuré pour observabilité (AC5)
        log_level = logging.WARNING if status == FallbackStatus.TO_REMOVE else logging.INFO
        logger.log(
            log_level,
            "governance_fallback_usage type=%s status=%s feature=%s call_site=%s nominal=%s "
            "stable_id=%s",
            fallback_type.value,
            status.value,
            effective_feature,
            call_site,
            is_nominal,
            stable_id,
        )

    @classmethod
    def get_status(cls, fallback_type: FallbackType) -> FallbackStatus:
        return cls.GOVERNANCE_MATRIX.get(fallback_type, {}).get("status", FallbackStatus.TRANSITORY)
