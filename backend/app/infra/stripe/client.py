"""Client Stripe centralise pour les appels techniques vers l'API externe."""

from __future__ import annotations

import stripe

from app.core.config import settings

# Cache par politique effective : evite d'instancier un nouveau StripeClient a chaque appel
# tout en invalidant automatiquement les rotations de secret ou de configuration reseau.
_client_cache: dict[tuple[str, str, int, int], stripe.StripeClient] = {}


def get_stripe_client() -> stripe.StripeClient | None:
    """Retourne un StripeClient configure, ou None si la cle secrete est absente."""
    if not settings.stripe_secret_key:
        return None
    api_key = settings.stripe_secret_key
    cache_key = (
        api_key,
        settings.stripe_api_version,
        settings.stripe_timeout_seconds,
        settings.stripe_max_network_retries,
    )
    if cache_key not in _client_cache:
        http_client = stripe.RequestsClient(timeout=settings.stripe_timeout_seconds)
        _client_cache[cache_key] = stripe.StripeClient(
            api_key=api_key,
            stripe_version=settings.stripe_api_version,
            max_network_retries=settings.stripe_max_network_retries,
            http_client=http_client,
        )
    return _client_cache[cache_key]
