import logging
from app.core.config import Settings

logger = logging.getLogger(__name__)


def _portal_billing_is_enabled(settings: Settings) -> bool:
    return bool(
        getattr(
            settings,
            "stripe_portal_endpoints_enabled",
            bool(getattr(settings, "stripe_secret_key", None)),
        )
    )


def run_stripe_portal_startup_validation(settings: Settings) -> None:
    """
    Vérifie que STRIPE_PORTAL_CONFIGURATION_ID est renseigné si le billing Stripe est actif.
    Story 61.64: Configuration explicite du Stripe Customer Portal pour les upgrades SaaS.
    """
    if not _portal_billing_is_enabled(settings):
        logger.info("stripe_portal_startup_validation_disabled")
        return

    if not settings.stripe_portal_configuration_id:
        # On n'échoue pas en test pour éviter de casser la CI qui n'a pas forcément de config Stripe complète
        if settings.app_env in {"test", "testing"}:
            logger.warning(
                "stripe_portal_startup_validation_skipped env=%s "
                "missing_portal_configuration_id",
                settings.app_env
            )
            return

        error_msg = (
            "STRIPE_PORTAL_CONFIGURATION_ID is required when Stripe Customer Portal "
            "billing endpoints are enabled to ensure explicit portal behavior (Story 61.64). "
            "Please create a dedicated portal configuration in Stripe Dashboard and set the ID."
        )
        logger.error("stripe_portal_startup_validation_failed error=%s", error_msg)
        raise RuntimeError(error_msg)

    logger.info("stripe_portal_startup_validation_ok")
