from __future__ import annotations

import stripe

from app.core.config import settings


def get_stripe_client() -> stripe.StripeClient | None:
    """Retourne un StripeClient configuré, ou None si la clé secrète est absente."""
    if not settings.stripe_secret_key:
        return None
    return stripe.StripeClient(
        api_key=settings.stripe_secret_key,
        stripe_version=settings.stripe_api_version,
    )
