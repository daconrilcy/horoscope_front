from __future__ import annotations

import stripe

from app.core.config import settings

# Cache par api_key : évite d'instancier un nouveau StripeClient à chaque appel.
# Invalidé automatiquement si la clé change (ex. rotation de secrets ou tests).
_client_cache: dict[str, stripe.StripeClient] = {}


def get_stripe_client() -> stripe.StripeClient | None:
    """Retourne un StripeClient configuré, ou None si la clé secrète est absente."""
    if not settings.stripe_secret_key:
        return None
    api_key = settings.stripe_secret_key
    if api_key not in _client_cache:
        _client_cache[api_key] = stripe.StripeClient(
            api_key=api_key,
            stripe_version=settings.stripe_api_version,
        )
    return _client_cache[api_key]
