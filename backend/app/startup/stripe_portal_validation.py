import logging

import stripe

from app.core.config import Settings
from app.infra.stripe.client import get_stripe_client

logger = logging.getLogger(__name__)


def _portal_billing_is_enabled(settings: Settings) -> bool:
    return bool(
        getattr(
            settings,
            "stripe_portal_endpoints_enabled",
            bool(getattr(settings, "stripe_secret_key", None)),
        )
    )


def _is_non_prod_env(settings: Settings) -> bool:
    return getattr(settings, "app_env", "development") in {
        "development",
        "dev",
        "local",
        "test",
        "testing",
    }


def _emit_validation_message(settings: Settings, mode: str, error_msg: str) -> None:
    if mode != "warn":
        logger.error("stripe_portal_startup_validation_failed error=%s", error_msg)
        raise RuntimeError(error_msg)

    if _is_non_prod_env(settings):
        logger.info("stripe_portal_startup_validation_advisory error=%s", error_msg)
        return

    logger.warning("stripe_portal_startup_validation_warn error=%s", error_msg)


def run_stripe_portal_startup_validation(settings: Settings) -> None:
    """
    Vérifie que STRIPE_PORTAL_CONFIGURATION_ID est renseigné si le billing Stripe est actif.
    Story 61.64: Configuration explicite du Stripe Customer Portal pour les upgrades SaaS.
    """
    validation_mode = getattr(settings, "stripe_portal_validation_mode", "strict")
    if validation_mode == "off":
        logger.info("stripe_portal_startup_validation_disabled")
        return

    if not _portal_billing_is_enabled(settings):
        logger.info("stripe_portal_startup_validation_disabled")
        return

    if not settings.stripe_portal_configuration_id:
        # On n'échoue pas en test pour éviter de casser la CI qui n'a pas forcément de config
        # Stripe complète.
        if settings.app_env in {"test", "testing"}:
            logger.warning(
                "stripe_portal_startup_validation_skipped env=%s missing_portal_configuration_id",
                settings.app_env,
            )
            return

        error_msg = (
            "STRIPE_PORTAL_CONFIGURATION_ID is required when Stripe Customer Portal "
            "billing endpoints are enabled to ensure explicit portal behavior (Story 61.64). "
            "Please create a dedicated portal configuration in Stripe Dashboard and set the ID."
        )
        _emit_validation_message(settings, validation_mode, error_msg)
        return

    client = get_stripe_client()
    if client is None:
        error_msg = (
            "Stripe Customer Portal validation requires a configured Stripe client when "
            "portal billing endpoints are enabled."
        )
        _emit_validation_message(settings, validation_mode, error_msg)
        return

    try:
        configuration = client.billing_portal.configurations.retrieve(
            settings.stripe_portal_configuration_id
        )
    except stripe.StripeError as error:
        error_msg = (
            "Unable to retrieve Stripe Customer Portal configuration "
            f"{settings.stripe_portal_configuration_id}: {error}"
        )
        try:
            _emit_validation_message(settings, validation_mode, error_msg)
        except RuntimeError:
            raise RuntimeError(error_msg) from error
        return

    subscription_update = getattr(configuration, "features", None)
    subscription_update = getattr(subscription_update, "subscription_update", None)
    enabled = getattr(subscription_update, "enabled", False)
    if not enabled:
        error_msg = (
            "Stripe Customer Portal configuration must enable subscription updates for "
            "self-service plan changes."
        )
        _emit_validation_message(settings, validation_mode, error_msg)
        return

    products = getattr(subscription_update, "products", None) or []
    allowed_price_ids: set[str] = set()
    for product in products:
        prices = getattr(product, "prices", None)
        if prices is None and isinstance(product, dict):
            prices = product.get("prices", [])
        if isinstance(prices, list):
            allowed_price_ids.update(str(price_id) for price_id in prices if price_id)

    expected_price_ids = {
        price_id
        for price_id in [settings.stripe_price_basic, settings.stripe_price_premium]
        if price_id
    }
    missing_price_ids = sorted(expected_price_ids - allowed_price_ids)
    if missing_price_ids:
        error_msg = (
            "Stripe Customer Portal configuration is missing subscription_update prices "
            f"for configured plans: {', '.join(missing_price_ids)}"
        )
        _emit_validation_message(settings, validation_mode, error_msg)
        return

    logger.info("stripe_portal_startup_validation_ok")
